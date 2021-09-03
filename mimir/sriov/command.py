#!/usr/bin/env python3
#
# Copyright 2019 Canonical Ltd
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

import argparse
import logging
from mimir.sriov.config import SRIOVConfig
import yaml
from pathlib import Path
from . import pci


DEFAULT_CONF_FILE = "/etc/mimir/mimir.yaml"


def configure(configuration: SRIOVConfig):
    """Configure SR-IOV VF's with configuration from interfaces.yaml"""

    for interface_name in configuration.interfaces:
        interface_config = configuration.interfaces[interface_name]
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
            if interface_config.num_vfs > device.sriov_totalvfs:
                logging.warn(
                    "Requested value for sriov_numfs ({}) too "
                    "high for interface {}. Falling back to "
                    "interface totalvfs "
                    "value: {}".format(
                        interface_config.num_vfs,
                        device.interface_name,
                        device.sriov_totalvfs,
                    )
                )
                interface_config.num_vfs = device.sriov_totalvfs

            logging.info(
                "Configuring SR-IOV device {} with {} "
                "VF's".format(
                    device.interface_name,
                    interface_config.num_vfs,
                )
            )
            device.set_sriov_numvfs(interface_config.num_vfs)


def main():
    """Main entry point for mimir-sriov"""
    parser = argparse.ArgumentParser("mimir-sriov")
    parser.set_defaults(prog=parser.prog)
    subparsers = parser.add_subparsers(
        title="subcommands",
        description="valid subcommands",
        help="sub-command help",
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONF_FILE,
    )
    show_subparser = subparsers.add_parser(
        "configure", help="Configure SR-IOV adapters with VF functions"
    )
    show_subparser.set_defaults(func=configure)

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    try:
        configuration = None
        path = Path(args.config)
        if path.exists():
            with open(path, "r") as conf:
                configuration = SRIOVConfig.from_dict(yaml.safe_load(conf))
        else:
            logging.warn("No configuration file found, skipping configuration")
            return
        args.func(configuration)
    except Exception as e:
        parser.print_help()
        raise SystemExit("{prog}: {msg}".format(prog=args.prog, msg=e))
