import argparse
import logging
from time import gmtime

from netplanner.config import NetplannerConfig
from netplanner.providers.networkd.provider import NetworkdProvider
from netplanner.sriov.command import sriov
from netplanner.loader.config import ConfigLoader

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
            provider.networkd(start=True)
    elif only_sriov:
        sriov(configuration)
    elif only_networkd:
        provider.render()
        if reload:
            provider.networkd(start=True)


generate = apply = configure


def main():
    """Main entry point for netplanner"""
    parser = argparse.ArgumentParser("netplanner")
    parser.set_defaults(prog=parser.prog)
    subparsers = parser.add_subparsers(
        title="subcommands",
        description="valid subcommands",
        help="sub-command help",
    )
    parser.add_argument("--version", action="version", version="0.8.4")
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
    configure_subparser = subparsers.add_parser(
        "configure",
        help="Configure Network Adapters flawlessly with the knowledge of the netplanner.",
    )
    apply_subparser = subparsers.add_parser(
        "apply",
        help="Configure Network Adapters flawlessly with the knowledge of the netplanner.",
    )
    generate_subparser = subparsers.add_parser(
        "generate",
        help="Configure Network Adapters flawlessly with the knowledge of the netplanner.",
    )
    configure_subparser.set_defaults(func=configure)
    apply_subparser.set_defaults(func=apply)
    generate_subparser.set_defaults(func=generate)

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
        reload = args.reload
        if not reload and loader.is_netplan:
            reload = True
        output_path = args.output
        if output_path is None:
            if loader.is_netplan:
                output_path = NETPLAN_DEFAULT_OUTPUT_PATH
            else:
                output_path = DEFAULT_OUTPUT_PATH

        args.func(
            configuration,
            output_path,
            local=bool(args.local),
            reload=bool(reload),
            only_sriov=bool(args.only_sriov),
            only_networkd=bool(args.only_networkd),
        )
    except Exception as e:
        parser.print_help()
        if args.debug:
            raise e
        else:
            raise SystemExit("{prog}: {msg}".format(prog=args.prog, msg=e))


if __name__ == "__main__":
    main()
