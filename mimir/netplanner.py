import yaml
from pprint import pprint
from .config import NetplannerConfig
from .config import NetworkRenderer
from .interfaces.typing import InterfaceName

if __name__ == "__main__":
    with open('examples/worker-config.yaml') as file:
        worker_config = yaml.safe_load(file)
    config = NetplannerConfig.from_dict(yaml.safe_load(worker_config))
    pprint(config)
    pprint(config.network.lookup("vx.5000"))
    # print(json.dumps(config.as_dict(), indent=2))
    assert config.network.renderer == NetworkRenderer.NETWORKD
    assert InterfaceName("0123456789abcd") == "0123456789abcd"
    try:
        assert InterfaceName("0123456789abcdefg") == "This should not work"
    except ValueError:
        assert True
