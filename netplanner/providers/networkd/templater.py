import logging
from pathlib import Path

import yaml
from jinja2 import Environment, PackageLoader
from netplanner.config import NetplannerConfig
from netplanner.interfaces.l2.bond import Bond
from netplanner.interfaces.l2.bridge import Bridge
from netplanner.interfaces.l2.ethernet import Ethernet
from netplanner.interfaces.l2.vlan import VLAN


class NetworkdTemplater:
    env: Environment = Environment(loader=PackageLoader("netplanner.providers.networkd"))
    priority: int = 10
    DEFAULT_PATH = "etc/systemd/network"

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
        raise ValueError("Cannot determine file_ending for {item}")

    def __init__(self, config: NetplannerConfig, local=True, path: str = DEFAULT_PATH):
        self.config: NetplannerConfig = config
        # Ensures that user provided strings are normalized.
        self.env.filters["to_systemd_bool"] = NetworkdTemplater.to_systemd_bool
        self.env.filters[
            "to_systemd_link_local"
        ] = NetworkdTemplater.to_systemd_link_local
        path = path.removeprefix("/")
        path = path.removeprefix("./")
        prefix = "/"
        if local:
            prefix = "./"
        self.path = Path(f"{prefix}{path}")
        self.path.mkdir(parents=True, exist_ok=True)

    def render_networks(self):
        template = self.env.get_template("systemd.network.j2")
        priority: int = 10
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
            if isinstance(interface_config, (Bond, Bridge)):
                child_interfaces = {
                    child_interface_name: child_interface_config
                    for interface_name in interface_config.interfaces
                    for child_interface_name, child_interface_config in self.config.network.lookup(
                        interface_name
                    ).items()
                } | {
                    vlan_name: vlan_config
                    for vlan_name, vlan_config in self.config.network.vlans.items()
                    if interface_name == vlan_config.link
                }
            elif (
                isinstance(interface_config, VLAN) and interface_config.link is not None
            ):
                parent_interface = self.config.network.lookup(interface_config.link)
            elif isinstance(interface_config, Ethernet):
                parent_interface = {
                    bond_name: bond_config
                    for bond_name, bond_config in self.config.network.bonds.items()
                    if interface_name in bond_config.interfaces
                }
            file_name = f"{priority}-{interface_name}.network"
            with open(self.path / file_name, "w") as file:
                file.write(
                    template.render(
                        interface_name=interface_name,
                        interface=interface_config,
                        child_interfaces=child_interfaces,
                        parent_interface=parent_interface,
                    )
                )

    def render_links(self):
        priority: int = 10
        template = self.env.get_template("systemd.link.j2")

        for interface_name, interface_config in self.config.network.ethernets.items():
            file_name = f"{priority}-{interface_name}.link"
            with open(self.path / file_name, "w") as file:
                file.write(
                    template.render(
                        interface_name=interface_name, interface=interface_config
                    )
                )

    def render_netdevs(self):
        priority: int = 10
        template = self.env.get_template("systemd.netdev.j2")
        for interface_name, interface_config in (
            self.config.network.vxlans
            | self.config.network.vrfs
            | self.config.network.bridges
            | self.config.network.vlans
            | self.config.network.bonds
            | self.config.network.dummies
        ).items():
            file_name = f"{priority}-{interface_name}.netdev"
            with open(self.path / file_name, "w") as file:
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
        for filename, data in self.config.network.additionals.items():
            logging.info(f"Write: {filename}")
            assert filename.endswith(
                ("link", "network", "netdev")
            ), "only networkd endings are allowed."
            with open(self.path / filename, "w") as file:
                file.write(template.render(data=data))


if __name__ == "__main__":
    with open("examples/worker-config.yaml") as file:
        worker_config = yaml.safe_load(file)
    config = NetplannerConfig.from_dict(worker_config)
    NetworkdTemplater(config=config).render()
