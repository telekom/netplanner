import logging
from pathlib import Path
from subprocess import PIPE, run

from jinja2 import Environment, PackageLoader
from netplanner.config import NetplannerConfig
from netplanner.interfaces.base import Base
from netplanner.interfaces.l2.bond import Bond
from netplanner.interfaces.l2.bridge import Bridge
from netplanner.interfaces.l2.dummy import Dummy
from netplanner.interfaces.l2.ethernet import Ethernet
from netplanner.interfaces.l2.vlan import VLAN
from netplanner.interfaces.l2.vrf import VRF
from netplanner.interfaces.l2.vxlan import VXLAN


class NetworkdProvider:
    env: Environment = Environment(
        loader=PackageLoader("netplanner.providers.networkd")
    )
    priority: int = 10
    DEFAULT_PATH = "etc/systemd/network"

    @staticmethod
    def run_command(command: list[str]) -> None:
        process = run(
            command,
            check=True,
            stdout=PIPE,
            stderr=PIPE,
            universal_newlines=True,
            encoding="utf-8",
        )
        if process.stdout:
            logging.info(process.stdout)
        if process.stderr:
            logging.error(process.stderr)

    @staticmethod
    def networkd(restart: bool = True, status: bool = True):
        command = ["/usr/bin/env", "systemctl"]
        if restart:
            command.append("restart")
        elif status:
            command.append("status")
        else:
            command.append("show")
        command.append("systemd-networkd")
        NetworkdProvider.run_command(command)

    @staticmethod
    def networkctl(reload: bool = True, status: bool = False, all: bool = True):
        command = ["/usr/bin/env", "networkctl"]
        if reload:
            command.append("reload")
        elif status:
            command.append("status")
        else:
            raise NotImplementedError(
                f"(reload:={reload} and status:={status}) == False is not implemented"
            )
        if all:
            command.append("--all")
        NetworkdProvider.run_command(command)

    @staticmethod
    def to_systemd_bool(value: bool) -> str:
        return "yes" if bool(value) else "no"

    @staticmethod
    def to_systemd_link_local(value: set) -> str:
        if not value:
            return "no"
        if "ipv4" in value and "ipv6" in value:
            return "yes"
        elif "ipv4" not in value or "ipv6" not in value:
            return list(value)[0]
        return "no"

    @staticmethod
    def get_file_ending(data: list):
        for item in data:
            for key in item.keys():
                if key.lower() in ["netdev", "network", "link"]:
                    return key.lower()
        raise ValueError(f"Cannot determine file_ending for {data}")

    @staticmethod
    def get_priority(interface_type: Base) -> int:
        if isinstance(interface_type, Ethernet):
            return 10
        elif isinstance(interface_type, Bond):
            return 11
        elif isinstance(interface_type, Dummy):
            return 11
        elif isinstance(interface_type, VRF):
            return 12
        elif isinstance(interface_type, Bridge):
            return 13
        elif isinstance(interface_type, VXLAN):
            return 14
        elif isinstance(interface_type, VLAN):
            return 15
        return 16

    def __init__(self, config: NetplannerConfig, local=True, path: str = DEFAULT_PATH):
        self.config: NetplannerConfig = config
        # Ensures that user provided strings are normalized.
        self.env.filters["to_systemd_bool"] = NetworkdProvider.to_systemd_bool
        self.env.filters[
            "to_systemd_link_local"
        ] = NetworkdProvider.to_systemd_link_local
        path = path.removeprefix("/")
        path = path.removeprefix("./")
        prefix = "/"
        if local:
            prefix = "./"
        self.path = Path(f"{prefix}{path}")
        self.path.mkdir(parents=True, exist_ok=True)

    def render_networks(self):
        template = self.env.get_template("systemd.network.j2")
        for interface_name, interface_config in (
            self.config.network.vxlans
            | self.config.network.vrfs
            | self.config.network.bridges
            | self.config.network.vlans
            | self.config.network.bonds
            | self.config.network.dummies
            | self.config.network.ethernets
        ).items():
            child_interfaces = {}
            parent_interface = None
            if isinstance(interface_config, Bond):
                child_interfaces = {
                    vlan_name: vlan_config
                    for vlan_name, vlan_config in self.config.network.vlans.items()
                    if interface_name == vlan_config.link
                }
            elif isinstance(interface_config, Dummy):
                child_interfaces = {
                    vxlan_name: vxlan_config
                    for vxlan_name, vxlan_config in self.config.network.vxlans.items()
                    if interface_name == vxlan_config.link
                }
            elif (
                isinstance(interface_config, VLAN) and interface_config.link is not None
            ):
                parent_interface = self.config.network.lookup(interface_config.link)
            elif isinstance(interface_config, Ethernet):
                parent_interface = {
                    name: config
                    for name, config in self.config.network.bonds.items()
                    if interface_name in config.interfaces
                }
            elif isinstance(interface_config, VXLAN):
                parent_interface = {
                    name: config
                    for name, config in self.config.network.bridges.items()
                    if interface_name in config.interfaces
                }

            if parent_interface is not None and len(parent_interface) > 1:
                raise ValueError(f"Cannot have more than one parent interface for {interface_name}")

            file_name = f"{NetworkdProvider.get_priority(interface_config)}-{interface_name}.network"
            with open(self.path / file_name, "w") as file:
                logging.info(f"Write: {self.path / file_name}")
                file.write(
                    template.render(
                        interface_name=interface_name,
                        interface=interface_config,
                        child_interfaces=child_interfaces,
                        parent_interface=parent_interface,
                    )
                )

    def render_links(self):
        template = self.env.get_template("systemd.link.j2")
        for interface_name, interface_config in self.config.network.ethernets.items():
            file_name = f"{NetworkdProvider.get_priority(interface_config)}-{interface_name}.link"
            with open(self.path / file_name, "w") as file:
                logging.info(f"Write: {self.path / file_name}")
                file.write(
                    template.render(
                        interface_name=interface_name, interface=interface_config
                    )
                )

    def render_netdevs(self):
        template = self.env.get_template("systemd.netdev.j2")
        for interface_name, interface_config in (
            self.config.network.vxlans
            | self.config.network.vrfs
            | self.config.network.bridges
            | self.config.network.vlans
            | self.config.network.bonds
            | self.config.network.dummies
        ).items():
            file_name = f"{NetworkdProvider.get_priority(interface_config)}-{interface_name}.netdev"
            with open(self.path / file_name, "w") as file:
                logging.info(f"Write: {self.path / file_name}")
                file.write(
                    template.render(
                        interface_name=interface_name, interface=interface_config
                    )
                )

    def render(self):
        self.render_netdevs()
        self.render_links()
        self.render_networks()
        template = self.env.get_template("additionals.j2")
        for file_name, data in self.config.network.additionals.items():
            assert file_name.endswith(
                ("link", "network", "netdev")
            ), "only networkd endings are allowed."
            with open(self.path / file_name, "w") as file:
                logging.info(f"Write: {self.path / file_name}")
                file.write(template.render(data=data))


if __name__ == "__main__":
    import yaml

    with open("examples/worker-config.yaml") as file:
        worker_config = yaml.safe_load(file)
    config = NetplannerConfig.from_dict(worker_config)
    NetworkdProvider(config=config).render()
