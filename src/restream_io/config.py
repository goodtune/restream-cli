import json
import os
import time
from pathlib import Path

CONFIG_PATH = Path(
    os.getenv("RESTREAM_CONFIG_PATH", Path.home() / ".config" / "restream.io")
)


def ensure_config_dir():
    """Create config directory with secure permissions if it doesn't exist."""
    CONFIG_PATH.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.chmod(0o700)


def save_tokens(data: dict):
    """Save tokens to config file with secure permissions."""
    ensure_config_dir()
    path = CONFIG_PATH / "tokens.json"

    # Calculate expires_at if expires_in is provided
    token_data = data.copy()
    if "expires_in" in token_data and "expires_at" not in token_data:
        token_data["expires_at"] = time.time() + token_data["expires_in"]

    try:
        with open(path, "w") as f:
            json.dump(token_data, f, indent=2)
        path.chmod(0o600)
    except (OSError, IOError) as e:
        raise RuntimeError(f"Failed to save tokens: {e}")


def load_tokens():
    """Load tokens from config file, return None if file doesn't exist."""
    path = CONFIG_PATH / "tokens.json"
    if not path.exists():
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, IOError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Failed to load tokens: {e}")


def get_client_id():
    """Get client ID from environment variable."""
    return os.getenv("RESTREAM_CLIENT_ID")


def get_client_secret():
    """Get client secret from environment variable."""
    return os.getenv("RESTREAM_CLIENT_SECRET")
