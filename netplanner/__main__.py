import argparse
import logging
from pathlib import Path

import yaml

from netplanner.config import NetplannerConfig
from netplanner.providers.networkd.templater import NetworkdTemplater
from netplanner.sriov.command import sriov

DEFAULT_CONF_FILE = "/etc/netplanner/netplanner.yaml"
DEFAULT_OUTPUT_PATH = "/etc/systemd/network"


def configure(
    configuration: NetplannerConfig,
    output: str,
    local: bool,
    only_sriov: bool,
    only_networkd: bool,
):
    if not only_sriov and not only_networkd:
        sriov(configuration)
        NetworkdTemplater(config=configuration, local=local, path=output).render()
    elif only_sriov:
        sriov(configuration)
    elif only_networkd:
        NetworkdTemplater(config=configuration, local=local, path=output).render()


def main():
    """Main entry point for netplanner"""
    parser = argparse.ArgumentParser("netplanner")
    parser.set_defaults(prog=parser.prog)
    subparsers = parser.add_subparsers(
        title="subcommands",
        description="valid subcommands",
        help="sub-command help",
    )
    parser.add_argument(
        "--config",
        help="Defines the path to the configuration file",
        default=DEFAULT_CONF_FILE,
    )
    parser.add_argument(
        "--local",
        help="This templates the configuration into a local directory",
        action="store_true",
    )
    parser.add_argument(
        "--only-sriov",
        help="This only runs sriov configuration",
        action="store_true",
        dest="only_sriov",
    )
    parser.add_argument(
        "--only-networkd",
        help="This templates only networkd",
        action="store_true",
        dest="only_networkd",
    )
    parser.add_argument(
        "--output",
        help="The output directory to which the files will be written.",
        default=DEFAULT_OUTPUT_PATH,
    )
    show_subparser = subparsers.add_parser(
        "configure", help="Configure Network Adapters flawlessly with the knowledge of mimir the netplanner."
    )
    show_subparser.set_defaults(func=configure)

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    try:
        configuration = None
        path = Path(args.config)
        if path.exists():
            with open(path, "r") as conf:
                configuration = NetplannerConfig.from_dict(yaml.safe_load(conf))
        else:
            logging.warn("No configuration file found, skipping configuration")
            return
        args.func(
            configuration,
            args.output,
            bool(args.local),
            only_sriov=bool(args.only_sriov),
            only_networkd=bool(args.only_networkd),
        )
    except Exception as e:
        parser.print_help()
        raise SystemExit("{prog}: {msg}".format(prog=args.prog, msg=e))


if __name__ == "__main__":
    main()
