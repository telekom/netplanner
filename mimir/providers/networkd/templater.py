from jinja2 import Environment, PackageLoader
from mimir.netplanner import NetplannerConfig, worker_config
import yaml


class Templater:
    env: Environment = Environment(loader=PackageLoader("mimir.providers.networkd"))
    priority: int = 10

    def __init__(self, config: NetplannerConfig):
        self.config: NetplannerConfig = config

    def render(self):
        template = self.env.get_template("systemd.netdev.j2")
        for interface_name, interface_config in self.config.network.vxlans.items():
            print(
                template.render(
                    interface_name=interface_name, interface=interface_config
                )
            )


if __name__ == "__main__":
    config = NetplannerConfig.from_dict(yaml.safe_load(worker_config))
    Templater(config=config).render()
