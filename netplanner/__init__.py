import importlib.metadata

try:
    # This will read version from pyproject.toml
    __version__ = importlib.metadata.version(__name__)
except Exception:
    __version__ = "develop"
