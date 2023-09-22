#!/usr/bin/env python3
# netplanner
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
# delayed-rebind inspired by netplan (https://github.com/canonical/netplan/blob/main/src/sriov.c)
# Copyright (C) 2020-2022 Canonical, Ltd., GNU General Public License, Version 3

import logging
from pathlib import Path

from jinja2 import Environment

from netplanner.loader.templates import ImportLibLoader
from netplanner.sriov import templates

from ..config import NetplannerConfig
from . import pci


SERVICE_PATH = Path("/run/systemd/system/netplanner-delayed-rebind.service")
LINK_PATH = Path(
    "/run/systemd/system/multi-user.target.wants/netplanner-delayed-rebind.service"
)


template_env = Environment(loader=ImportLibLoader(templates))


def config(configuration: NetplannerConfig):
    """Configure SR-IOV VF's with configuration from interfaces.yaml"""

    delayed_bindings = []

    for interface_name in configuration.network.ethernets:
        interface_config = configuration.network.ethernets[interface_name]
        if interface_config.virtual_function_count is None:
            continue
        devices = pci.PCINetDevices()
        for device in devices.pci_devices:
            device.update_attributes()
        logging.info([device.interface_name for device in devices.pci_devices])
        device = None
        if match := interface_config.match:
            if match.macaddress:
                device = devices.get_device_from_mac(match.macaddress)
            elif match.pciaddress:
                device = devices.get_device_from_pci_address(match.pciaddress)
        else:
            device = devices.get_device_from_interface_name(interface_name)
        if device and device.sriov:
            if interface_config.delay_virtual_functions_rebind:
                delayed_bindings.append(device)

            if interface_config.virtual_function_count > device.sriov_totalvfs:
                logging.warning(
                    "Requested value for sriov_numfs ({}) too "
                    "high for interface {}. Falling back to "
                    "interface totalvfs "
                    "value: {}".format(
                        interface_config.virtual_function_count,
                        device.interface_name,
                        device.sriov_totalvfs,
                    )
                )
                interface_config.virtual_function_count = device.sriov_totalvfs

            logging.info(
                "Configuring SR-IOV device {} with {} "
                "VF's".format(
                    device.interface_name,
                    interface_config.virtual_function_count,
                )
            )
            device.set_sriov_numvfs(interface_config.virtual_function_count)
            if interface_config.embedded_switch_mode is not None:
                device.set_eswitch_mode(
                    interface_config.embedded_switch_mode.value,
                    interface_config.delay_virtual_functions_rebind,
                )

    if len(delayed_bindings) > 0:
        with SERVICE_PATH.open("w") as file:
            file.write(
                template_env.get_template("netplanner-delayed-rebind.j2").render(
                    devices=delayed_bindings
                )
            )
        LINK_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not LINK_PATH.exists():
            LINK_PATH.symlink_to(SERVICE_PATH)


def rebind(pci_addresses: list[str]):
    for pci_address in pci_addresses:
        device = pci.PCIDevice(pci_address)
        pci.bind_vfs(device.vfs)
