import argparse
import logging
from pathlib import Path

import yaml

from mimir.config import NetplannerConfig
from mimir.providers.networkd.templater import NetworkdTemplater
from mimir.sriov.command import sriov

DEFAULT_CONF_FILE = "/etc/mimir/mimir.yaml"
DEFAULT_OUTPUT_PATH = "/etc/systemd/network"


def configure(configuration: NetplannerConfig, output: str, local: bool):
    sriov(configuration)
    NetworkdTemplater(config=configuration, local=local, path=output).render()


def main():
    """Main entry point for mimir"""
    parser = argparse.ArgumentParser("mimir")
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
        "--output",
        help="The output directory to which the files will be written.",
        default=DEFAULT_OUTPUT_PATH,
    )
    show_subparser = subparsers.add_parser(
        "configure", help="Configure Network Adapters flawlessly"
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
        args.func(configuration, args.output, bool(args.local))
    except Exception as e:
        parser.print_help()
        raise SystemExit("{prog}: {msg}".format(prog=args.prog, msg=e))


if __name__ == "__main__":
    main()
