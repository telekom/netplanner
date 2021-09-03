import pathlib
from jinja2 import Environment, PackageLoader
from mimir.netplanner import NetplannerConfig, worker_config
import yaml
from pathlib import Path


class Templater:
    env: Environment = Environment(loader=PackageLoader("mimir.providers.networkd"))
    priority: int = 10
    DEFAULT_PATH = "etc/systemd/network"

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
        path = path.removeprefix("/")
        path = path.removeprefix("./")
        prefix = "/"
        if local:
            prefix = "./"
        self.networkd_path = Path(f"{prefix}{path}")
        self.networkd_path.mkdir(parents=True, exist_ok=True)

    def render_networks(self):
        template = self.env.get_template("systemd.network.j2")

    def render_vfs(self):
        
    def render_links(self):
        priority: int = 10
        template = self.env.get_template("systemd.link.j2")

        for interface_name, interface_config in self.config.network.ethernets.items():
            file_name = f"{priority}-{interface_name}.link"
            with open(self.networkd_path / file_name, 'w') as file:
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
            | self.config.network.bonds
        ).items():
            print(
                template.render(
                    interface_name=interface_name, interface=interface_config
                )
            )

    def render(self):
        self.render_netdevs()
        self.render_links()
        self.render_networks()
        template = self.env.get_template("additionals.j2")
        for filename_prefix, data in self.config.network.additionals.items():
            file_name = f"{filename_prefix}.{Templater.get_file_ending(data):}"
            with open(self.networkd_path / file_name, "w") as file:
                file.write(template.render(data=data))


if __name__ == "__main__":
    config = NetplannerConfig.from_dict(yaml.safe_load(worker_config))
    Templater(config=config).render()
