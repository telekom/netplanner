from pathlib import Path

import yaml
from mimir.sriov.config import SRIOVConfig


class MIMIRTemplater:
    DEFAULT_PATH = "etc/mimir"

    def __init__(self, config: SRIOVConfig, local=True, path: str = DEFAULT_PATH):
        self.config: SRIOVConfig = config
        # Ensures that user provided strings are normalized.
        path = path.removeprefix("/")
        path = path.removeprefix("./")
        prefix = "/"
        if local:
            prefix = "./"
        self.path = Path(f"{prefix}{path}")
        self.path.mkdir(parents=True, exist_ok=True)

    def render_init(self):
        pass

    def render_vfs(self):
        with open(self.path / "mimir.yaml", "w") as file:
            file.write(yaml.safe_dump(self.config.as_dict()))

    def render(self):
        self.render_vfs()
        self.render_init()


if __name__ == "__main__":
    config_raw = """
interfaces:
    enp2s0f0:
        num_vfs: 64
    enp3s0f1:
        num_vfs: 64
    enp4s0f0:
        match:
          pciaddress: 0000:81:00.0
        num_vfs: 64
    enp4s0f1:
        match:
          macaddress: 00:53:00:00:00:42
        num_vfs: 64
    """
    config = SRIOVConfig.from_dict(yaml.safe_load(config_raw))
    MIMIRTemplater(config=config).render()
