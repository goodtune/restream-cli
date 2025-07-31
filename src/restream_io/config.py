import json
import os
from pathlib import Path

CONFIG_PATH = Path(
    os.getenv("RESTREAM_CONFIG_PATH", Path.home() / ".config" / "restream.io")
)


def ensure_config_dir():
    CONFIG_PATH.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.chmod(0o700)


def save_tokens(data: dict):
    ensure_config_dir()
    path = CONFIG_PATH / "tokens.json"
    with open(path, "w") as f:
        json.dump(data, f)
    path.chmod(0o600)


def load_tokens():
    path = CONFIG_PATH / "tokens.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)
