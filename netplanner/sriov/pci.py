#!/usr/bin/env python3
# netplanner
# Copyright (C) 2020-2022 Canonical, Ltd.
# Copyright (C) 2021-2023 Deutsche Telekom AG
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# inspired by https://github.com/canonical/netplan/blob/main/netplan_cli/cli/sriov.py

import json
import glob
import os
import shlex
import subprocess
import re
from pathlib import Path
from typing import Optional
import typing


# PCIDevice class originates from mlnx_switchdev_mode/sriovify.py
# Copyright 2019 Canonical Ltd, Apache License, Version 2.0
# https://github.com/openstack-charmers/mlnx-switchdev-mode
class PCIDevice(object):
    """Helper class for interaction with a PCI device"""

    def __init__(self, pci_addr: str):
        """Initialise a new PCI device handler

        :param pci_addr: PCI address of device
        :type: str
        """
        self.pci_addr = pci_addr

    @property
    def path(self) -> str:
        """/sys path for PCI device

        :return: full path to PCI device in /sys filesystem
        :rtype: str
        """
        return "/sys/bus/pci/devices/{}".format(self.pci_addr)

    def subpath(self, subpath: str) -> str:
        """/sys subpath helper for PCI device

        :param subpath: subpath to construct path for
        :type: str
        :return: self.path + subpath
        :rtype: str
        """
        return os.path.join(self.path, subpath)

    @property
    def driver(self) -> str:
        """Kernel driver for PCI device

        :return: kernel driver in use for device
        :rtype: str
        """
        driver = ""
        if os.path.exists(self.subpath("driver")):
            driver = os.path.basename(os.readlink(self.subpath("driver")))
        return driver

    @property
    def bound(self) -> bool:
        """Determine if device is bound to a kernel driver

        :return: whether device is bound to a kernel driver
        :rtype: bool
        """
        return os.path.exists(self.subpath("driver"))

    @property
    def is_pf(self) -> bool:
        """Determine if device is a SR-IOV Physical Function

        :return: whether device is a PF
        :rtype: bool
        """
        return os.path.exists(self.subpath("sriov_numvfs"))

    @property
    def is_vf(self) -> bool:
        """Determine if device is a SR-IOV Virtual Function

        :return: whether device is a VF
        :rtype: bool
        """
        return os.path.exists(self.subpath("physfn"))

    @property
    def vf_addrs(self) -> list:
        """List Virtual Function addresses associated with a Physical Function

        :return: List of PCI addresses of Virtual Functions
        :rtype: list[str]
        """
        vf_addrs = []
        i = 0
        while True:
            try:
                vf_addrs.append(
                    os.path.basename(os.readlink(self.subpath("virtfn{}".format(i))))
                )
            except FileNotFoundError:
                break
            i += 1
        return vf_addrs

    @property
    def vfs(self) -> list:
        """List Virtual Function associated with a Physical Function

        :return: List of PCI devices of Virtual Functions
        :rtype: list[PCIDevice]
        """
        return [PCIDevice(addr) for addr in self.vf_addrs]

    def devlink_get(self, obj_name: str):
        """Query devlink for information about the PCI device

        :param obj_name: devlink object to query
        :type: str
        :return: Dictionary of information about the device
        :rtype: dict
        """
        out = subprocess.check_output(
            [
                "/sbin/devlink",
                "dev",
                obj_name,
                "show",
                "pci/{}".format(self.pci_addr),
                "--json",
            ]
        )
        return json.loads(out)["dev"]["pci/{}".format(self.pci_addr)]

    def devlink_set(self, obj_name: str, prop: str, value: str):
        """Set devlink options for the PCI device

        :param obj_name: devlink object to set options on
        :type: str
        :param prop: property to set
        :type: str
        :param value: value to set for property
        :type: str
        """
        subprocess.check_call(
            [
                "/sbin/devlink",
                "dev",
                obj_name,
                "set",
                "pci/{}".format(self.pci_addr),
                prop,
                value,
            ]
        )

    def __str__(self) -> str:
        """String represenation of object

        :return: PCI address of string
        :rtype: str
        """
        return self.pci_addr


def bind_vfs(vfs: typing.Iterable[PCIDevice]):
    """Bind unbound VFs to mlx5_core driver."""
    bound_vfs = []
    for vf in vfs:
        if not vf.bound:
            with open("/sys/bus/pci/drivers/mlx5_core/bind", "wt") as f:
                f.write(vf.pci_addr)
                bound_vfs.append(vf)
    return bound_vfs


def unbind_vfs(vfs: typing.Iterable[PCIDevice]) -> typing.Iterable[PCIDevice]:
    """Unbind bound VFs from mlx5_core driver."""
    unbound_vfs = []
    for vf in vfs:
        if vf.bound:
            with open(
                "/sys/bus/pci/drivers/mlx5_core/unbind",
                "wt",
            ) as f:
                f.write(vf.pci_addr)
                unbound_vfs.append(vf)
    return unbound_vfs


def format_pci_addr(pci_addr: str) -> str:
    """Format a PCI address with 0 fill for parts

    :param: pci_addr: unformatted PCI address
    :type: str
    :returns: formatted PCI address
    :rtype: str
    """
    domain, bus, slot_func = pci_addr.split(":")
    slot, func = slot_func.split(".")
    return "{}:{}:{}.{}".format(domain.zfill(4), bus.zfill(2), slot.zfill(2), func)


def get_sysnet_interfaces_and_macs() -> list:
    """Catalog interface information from local system

    each device dict contains:

        interface: logical name
        mac_address: MAC address
        pci_address: PCI address
        state: Current interface state (up/down)
        sriov: Boolean indicating whether interface is an SR-IOV
               capable device.
        sriov_totalvfs: Total VF capacity of device
        sriov_numvfs: Configured VF capacity of device

    :returns: array of dict objects containing details of each interface
    :rtype: list
    """
    net_devs = []
    for sdir in glob.glob("/sys/class/net/*"):
        sym_link = Path(sdir) / "device"
        # Ignore representor interfaces
        phys_port_name = Path(sdir) / "phys_port_name"
        try:
            if phys_port_name.exists() and not re.search(
                r"^p\d+$", phys_port_name.read_text()
            ):
                continue
        except:
            pass
        if sym_link.is_symlink():
            fq_path = sym_link.resolve()
            path = fq_path.parts
            if "virtio" in path[-1]:
                pci_address = path[-2]
            else:
                pci_address = path[-1]
            device = {
                "interface": get_sysnet_interface(sdir),
                "mac_address": get_sysnet_mac(sdir),
                "pci_address": pci_address,
                "state": get_sysnet_device_state(sdir),
                "sriov": is_sriov(sdir),
            }
            if device["sriov"]:
                device["sriov_totalvfs"] = get_sriov_totalvfs(sdir)
                device["sriov_numvfs"] = get_sriov_numvfs(sdir)
            net_devs.append(device)

    return net_devs


def get_sysnet_mac(sysdir: str) -> str:
    """Determine MAC address for a device

    :param: sysdir: path to device /sys directory
    :type: str
    :returns: MAC address of device
    :rtype: str
    """
    mac_addr_file = Path(sysdir) / "address"
    with open(mac_addr_file, "r") as f:
        read_data = f.read()
    return read_data.strip()


def get_sysnet_device_state(sysdir: str) -> str:
    """Read operational state of a device

    :param: sysdir: path to device /sys directory
    :type: str
    :returns: current device state
    :rtype: str
    """
    state_file = Path(sysdir) / "operstate"
    with open(state_file, "r") as f:
        read_data = f.read()
    return read_data.strip()


def is_sriov(sysdir: str) -> bool:
    """Determine whether a device is SR-IOV capable

    :param: sysdir: path to device /sys directory
    :type: str
    :returns: whether device is SR-IOV capable or not
    :rtype: bool
    """
    return Path(Path(sysdir) / "device" / "sriov_totalvfs").exists()


def get_sriov_totalvfs(sysdir: str) -> int:
    """Read total VF capacity for a device

    :param: sysdir: path to device /sys directory
    :type: str
    :returns: number of VF's the device supports
    :rtype: int
    """
    sriov_totalvfs_file = Path(sysdir) / "device" / "sriov_totalvfs"
    with open(sriov_totalvfs_file, "r") as f:
        read_data = f.read()
    return int(read_data.strip())


def get_sriov_numvfs(sysdir: str) -> int:
    """Read configured VF capacity for a device

    :param: sysdir: path to device /sys directory
    :type: str
    :returns: number of VF's the device is configured with
    :rtype: int
    """
    sriov_numvfs_file = Path(sysdir) / "device" / "sriov_numvfs"
    with open(sriov_numvfs_file, "r") as f:
        read_data = f.read()
    return int(read_data.strip())


def get_sysnet_interface(sysdir):
    return Path(sysdir).parts[-1]


def get_pci_ethernet_addresses() -> list:
    """Generate list of PCI addresses for all network adapters

    :returns: list of PCI addresses
    :rtype: list
    """
    cmd = ["lspci", "-m", "-D"]
    lspci_output = subprocess.check_output(cmd).decode("UTF-8")
    pci_addresses = []
    for line in lspci_output.split("\n"):
        columns = shlex.split(line)
        if len(columns) > 1 and columns[1] == "Ethernet controller":
            pci_address = columns[0]
            pci_addresses.append(format_pci_addr(pci_address))
    return pci_addresses


# PCINetDevice class originates from sriov_netplan_shim/pci.py
# Copyright 2019 Canonical Ltd, Apache License, Version 2.0
# https://github.com/openstack-charmers/sriov-netplan-shim
class PCINetDevice(object):
    def __init__(self, pci_address):
        self.pci_address = pci_address
        self.interface_name = None
        self.mac_address = None
        self.state = None
        self.sriov = False
        self.sriov_totalvfs = None
        self.sriov_numvfs = None
        self.pci_device = PCIDevice(self.pci_address)
        self.update_attributes()

    def update_attributes(self):
        self.update_interface_info()

    def update_interface_info(self):
        net_devices = get_sysnet_interfaces_and_macs()
        for interface in net_devices:
            if self.pci_address == interface["pci_address"]:
                self.interface_name = interface["interface"]
                self.mac_address = interface["mac_address"]
                self.state = interface["state"]
                self.sriov = interface["sriov"]
                if self.sriov:
                    self.sriov_totalvfs = interface["sriov_totalvfs"]
                    self.sriov_numvfs = interface["sriov_numvfs"]

    def _set_sriov_numvfs(self, numvfs: int):
        sdevice = (
            Path("/sys/class/net") / self.interface_name / "device" / "sriov_numvfs"
        )
        with open(sdevice, "w") as sh:
            sh.write(str(numvfs))
        self.update_attributes()

    def set_sriov_numvfs(self, numvfs: int) -> bool:
        """Set the number of VF devices for a SR-IOV PF

        Assuming the device is an SR-IOV device, this function will attempt
        to change the number of VF's created by the PF.

        @param numvfs: integer to set the current number of VF's to
        @returns boolean indicating whether any changes where made
        """
        if self.sriov and numvfs != self.sriov_numvfs:
            # NOTE(fnordahl): run-time change of numvfs is disallowed
            # without resetting to 0 first.
            self._set_sriov_numvfs(0)
            self._set_sriov_numvfs(numvfs)
            return True
        return False

    def set_eswitch_mode(self, switch_mode: str, delay_rebind: bool) -> bool:
        if self.pci_device.is_pf:
            unbind_vfs(self.pci_device.vfs)
            self.pci_device.devlink_set("eswitch", "mode", switch_mode)
            if not delay_rebind:
                bind_vfs(self.pci_device.vfs)
            self.update_attributes()
            return self.pci_device.devlink_get("eswitch")["mode"] == switch_mode
        return False


class PCINetDevices(object):
    def __init__(self):
        self.pci_devices = [PCINetDevice(dev) for dev in get_pci_ethernet_addresses()]

    def update_devices(self):
        for pcidev in self.pci_devices:
            pcidev.update_attributes()

    def get_macs(self) -> list:
        macs = []
        for pcidev in self.pci_devices:
            if pcidev.mac_address:
                macs.append(pcidev.mac_address)
        return macs

    def get_device_from_mac(self, mac: str) -> Optional[PCINetDevice]:
        for pcidev in self.pci_devices:
            if pcidev.mac_address == mac:
                return pcidev
        return None

    def get_device_from_pci_address(self, pci_addr: str) -> Optional[PCINetDevice]:
        for pcidev in self.pci_devices:
            if pcidev.pci_address == pci_addr:
                return pcidev
        return None

    def get_device_from_interface_name(
        self, interface_name: str
    ) -> Optional[PCINetDevice]:
        for pcidev in self.pci_devices:
            if pcidev.interface_name == interface_name:
                return pcidev
        return None
