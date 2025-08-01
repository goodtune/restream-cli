import json
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from restream_io import config


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for config tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(config, "CONFIG_PATH", Path(tmpdir) / "test-config"):
            yield Path(tmpdir) / "test-config"


def test_ensure_config_dir_creates_directory(temp_config_dir):
    """Test that ensure_config_dir creates directory with correct permissions."""
    # Directory shouldn't exist initially
    assert not temp_config_dir.exists()

    config.ensure_config_dir()

    # Directory should now exist with correct permissions
    assert temp_config_dir.exists()
    assert temp_config_dir.is_dir()
    assert oct(temp_config_dir.stat().st_mode)[-3:] == "700"


def test_ensure_config_dir_idempotent(temp_config_dir):
    """Test that ensure_config_dir can be called multiple times safely."""
    config.ensure_config_dir()

    # Call again
    config.ensure_config_dir()

    # Should still exist with same permissions
    assert temp_config_dir.exists()
    assert oct(temp_config_dir.stat().st_mode)[-3:] == "700"


def test_save_tokens_creates_file_with_permissions(temp_config_dir):
    """Test that save_tokens creates file with correct permissions."""
    token_data = {
        "access_token": "test-access-token",
        "refresh_token": "test-refresh-token",
        "expires_in": 3600,
    }

    config.save_tokens(token_data)

    token_file = temp_config_dir / "tokens.json"
    assert token_file.exists()
    assert token_file.is_file()
    assert oct(token_file.stat().st_mode)[-3:] == "600"

    # Check content - should include expires_at
    with open(token_file) as f:
        saved_data = json.load(f)

    # Original data should be preserved
    for key, value in token_data.items():
        assert saved_data[key] == value

    # expires_at should be added when expires_in is present
    assert "expires_at" in saved_data
    assert saved_data["expires_at"] > time.time()  # Should be in the future


def test_save_tokens_overwrites_existing(temp_config_dir):
    """Test that save_tokens overwrites existing token file."""
    old_data = {"old": "token"}
    new_data = {"new": "token"}

    config.save_tokens(old_data)
    config.save_tokens(new_data)

    token_file = temp_config_dir / "tokens.json"
    with open(token_file) as f:
        saved_data = json.load(f)
    assert saved_data == new_data


def test_load_tokens_returns_none_when_file_missing(temp_config_dir):
    """Test that load_tokens returns None when tokens file doesn't exist."""
    result = config.load_tokens()
    assert result is None


def test_load_tokens_returns_data_when_file_exists(temp_config_dir):
    """Test that load_tokens returns saved token data."""
    token_data = {
        "access_token": "test-access-token",
        "refresh_token": "test-refresh-token",
        "expires_in": 3600,
    }

    config.save_tokens(token_data)
    loaded_data = config.load_tokens()

    # Check that all original data is preserved
    for key, value in token_data.items():
        assert loaded_data[key] == value

    # expires_at should be added when expires_in is present
    assert "expires_at" in loaded_data


def test_load_tokens_handles_corrupted_file(temp_config_dir):
    """Test that load_tokens raises RuntimeError for corrupted JSON."""
    # Create a corrupted JSON file
    config.ensure_config_dir()
    token_file = temp_config_dir / "tokens.json"
    with open(token_file, "w") as f:
        f.write("invalid json content")

    with pytest.raises(RuntimeError, match="Failed to load tokens"):
        config.load_tokens()


def test_save_tokens_handles_permission_error(temp_config_dir):
    """Test that save_tokens raises RuntimeError on permission error."""
    # Mock the open function to simulate a permission error
    with patch("builtins.open", side_effect=PermissionError("Permission denied")):
        with pytest.raises(RuntimeError, match="Failed to save tokens"):
            config.save_tokens({"test": "data"})


def test_get_client_id_from_environment():
    """Test that get_client_id returns value from environment variable."""
    with patch.dict(os.environ, {"RESTREAM_CLIENT_ID": "test-client-id"}):
        assert config.get_client_id() == "test-client-id"


def test_get_client_id_returns_none_when_not_set():
    """Test that get_client_id returns None when environment variable not set."""
    with patch.dict(os.environ, {}, clear=True):
        assert config.get_client_id() is None


def test_get_client_secret_from_environment():
    """Test that get_client_secret returns value from environment variable."""
    with patch.dict(os.environ, {"RESTREAM_CLIENT_SECRET": "test-client-secret"}):
        assert config.get_client_secret() == "test-client-secret"


def test_get_client_secret_returns_none_when_not_set():
    """Test that get_client_secret returns None when environment variable not set."""
    with patch.dict(os.environ, {}, clear=True):
        assert config.get_client_secret() is None


def test_config_path_environment_override():
    """Test that CONFIG_PATH can be overridden via environment variable."""
    with tempfile.TemporaryDirectory() as tmpdir:
        custom_path = Path(tmpdir) / "custom-config"
        with patch.dict(os.environ, {"RESTREAM_CONFIG_PATH": str(custom_path)}):
            # Re-import to get new CONFIG_PATH value
            import importlib

            importlib.reload(config)

            config.ensure_config_dir()
            assert custom_path.exists()
            assert custom_path.is_dir()


def test_save_and_load_roundtrip(temp_config_dir):
    """Test that saving and loading tokens preserves data exactly."""
    original_data = {
        "access_token": "access-token-123",
        "refresh_token": "refresh-token-456",
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "read write",
    }

    config.save_tokens(original_data)
    loaded_data = config.load_tokens()

    # Check that all original data is preserved
    for key, value in original_data.items():
        assert loaded_data[key] == value

    # expires_at should be added when expires_in is present
    assert "expires_at" in loaded_data
    assert isinstance(loaded_data, type(original_data))
    for key in original_data:
        assert loaded_data[key] == original_data[key]
        assert isinstance(loaded_data[key], type(original_data[key]))
