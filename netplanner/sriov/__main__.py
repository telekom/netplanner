#!/usr/bin/env python3
#
# Copyright 2019 Canonical Ltd
# Copyright 2022 Deutsche Telekom AG
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# source: https://github.com/openstack-charmers/sriov-netplan-shim/blob/master/sriov_netplan_shim/cmd.py

import logging

from ..config import NetplannerConfig
from . import pci


def main(configuration: NetplannerConfig):
    """Configure SR-IOV VF's with configuration from interfaces.yaml"""

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
