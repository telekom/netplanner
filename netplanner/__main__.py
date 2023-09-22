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

import argparse
import logging
from time import gmtime

from . import __version__
from .config import NetplannerConfig
from .loader.config import ConfigLoader
from .providers.networkd.provider import NetworkdProvider
from .sriov.__main__ import config as sriov
from .sriov.__main__ import rebind

DEFAULT_OUTPUT_PATH = "/etc/systemd/network"
NETPLAN_DEFAULT_OUTPUT_PATH = "/run/systemd/network"

# https://stackoverflow.com/a/7517430/49489
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03dZ level=%(levelname)s module=%(name)s message="%(message)s"',
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logging.addLevelName(logging.DEBUG, "debug")
logging.addLevelName(logging.INFO, "info")
logging.addLevelName(logging.WARNING, "warning")
logging.addLevelName(logging.ERROR, "error")
logging.addLevelName(logging.CRITICAL, "critical")
logging.Formatter.converter = gmtime


def configure(
    configuration: NetplannerConfig,
    output: str,
    local: bool,
    reload: bool,
    only_sriov: bool,
    only_networkd: bool,
):
    provider = NetworkdProvider(config=configuration, local=local, path=output)
    if not only_sriov and not only_networkd:
        sriov(configuration)
        provider.render()
        if reload:
            provider.networkd(restart=True)
            provider.networkctl(reload=True)
    elif only_sriov:
        sriov(configuration)
    elif only_networkd:
        provider.render()
        if reload:
            provider.networkd(restart=True)
            provider.networkctl(reload=True)


def main():
    """Main entry point for netplanner"""
    parser = argparse.ArgumentParser("netplanner")
    parser.set_defaults(prog=parser.prog)
    subparsers = parser.add_subparsers(
        title="subcommands",
        description="valid subcommands",
        help="sub-command help",
        dest="command",
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--config",
        help="Defines the path to the configuration file or directory.",
        default=None,
    )
    parser.add_argument(
        "--debug",
        help="Enables debug logging.",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--local",
        help="This templates the configuration into a local directory",
        action="store_true",
    )
    parser.add_argument(
        "--only-sriov",
        help="This only runs sriov configuration on supported interfaces.",
        action="store_true",
        dest="only_sriov",
    )
    parser.add_argument(
        "--reload",
        help="This reloads networkd and networkctl via systemd.",
        action="store_true",
        dest="reload",
    )
    parser.add_argument(
        "--only-networkd",
        help="This templates only networkd configuration files.",
        action="store_true",
        dest="only_networkd",
    )
    parser.add_argument(
        "--output",
        help="The output directory to which the files will be written.",
        default=None,
    )
    subparsers.add_parser(
        "configure",
        help="Configure Network Adapters flawlessly with the knowledge of the netplanner.",
    )
    subparsers.add_parser(
        "apply",
        help="Configure Network Adapters flawlessly with the knowledge of the netplanner.",
    )
    subparsers.add_parser(
        "generate",
        help="Configure Network Adapters flawlessly with the knowledge of the netplanner.",
    )
    rebind_parser = subparsers.add_parser("rebind", help="Rebind SR-IOV interfaces")
    rebind_parser.add_argument(
        "pci_addresses",
        metavar="address",
        nargs="+",
        help="PCI addresses of PFs to rebind VFs of",
    )

    args = parser.parse_args()

    try:
        if args.debug:
            logging.getLogger().level = logging.DEBUG
            logging.debug(
                f"logger is now in LogLevel {logging.getLevelName(logging.getLogger().level)}"
            )

        loader = ConfigLoader(args.config)
        if loader.load_config():
            logging.debug(loader.config)
            configuration = NetplannerConfig.from_dict(loader.config)
        else:
            raise Exception("Configuration cannot be loaded.")
        output_path = args.output
        if output_path is None:
            if loader.is_netplan:
                output_path = NETPLAN_DEFAULT_OUTPUT_PATH
            else:
                output_path = DEFAULT_OUTPUT_PATH
        ## Python 3.10
        # match args.command:
        #     case ("configure" | "apply" | "generate"):
        #         configure(
        #             configuration,
        #             output_path,
        #             local=bool(args.local),
        #             reload=bool(args.reload),
        #             only_sriov=bool(args.only_sriov),
        #             only_networkd=bool(args.only_networkd),
        #         )
        #     case _:
        #         raise Exception(f"Unknown subcommand: {'<empty>' if args.command is None else args.command}")
        if args.command in ("configure", "apply", "generate"):
            configure(
                configuration,
                output_path,
                local=bool(args.local),
                reload=bool(args.reload),
                only_sriov=bool(args.only_sriov),
                only_networkd=bool(args.only_networkd),
            )
        elif args.command == "rebind":
            rebind(args.pci_addresses)
        else:
            raise Exception(
                f"Unknown subcommand: {'<empty>' if args.command is None else args.command}"
            )
    except Exception as e:
        parser.print_help()
        if args.debug:
            raise e
        else:
            raise SystemExit("{prog}: {msg}".format(prog=args.prog, msg=e))


if __name__ == "__main__":
    main()
