"""Test CLI profile command output formatting."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import responses
from click.testing import CliRunner

from restream_io import config
from restream_io.cli import profile


@responses.activate
def test_profile_command_human_readable_output():
    """Test profile command displays human-readable output by default."""
    # Mock profile API response
    profile_data = {"id": 123456, "username": "test_user", "email": "test@example.com"}

    responses.add(
        "GET", "https://api.restream.io/v2/user/profile", json=profile_data, status=200
    )

    runner = CliRunner()

    # Mock config with valid token
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir)
        tokens_file = config_path / "tokens.json"
        tokens_file.parent.mkdir(parents=True, exist_ok=True)
        tokens_file.write_text('{"access_token": "fake-token"}')

        with patch.object(config, "CONFIG_PATH", config_path):
            result = runner.invoke(profile, [])

    assert result.exit_code == 0
    assert "Profile Information:" in result.output
    assert "ID: 123456" in result.output
    assert "Username: test_user" in result.output
    assert "Email: test@example.com" in result.output
    # Should not contain JSON format
    assert "{\n" not in result.output


@responses.activate
def test_profile_command_json_output():
    """Test profile command outputs JSON when --json flag is used."""
    profile_data = {"id": 123456, "username": "test_user", "email": "test@example.com"}

    responses.add(
        "GET", "https://api.restream.io/v2/user/profile", json=profile_data, status=200
    )

    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir)
        tokens_file = config_path / "tokens.json"
        tokens_file.parent.mkdir(parents=True, exist_ok=True)
        tokens_file.write_text('{"access_token": "fake-token"}')

        with patch.object(config, "CONFIG_PATH", config_path):
            # Use the main CLI with --json flag
            from restream_io.cli import cli

            result = runner.invoke(cli, ["profile", "--json"])

    assert result.exit_code == 0
    # Should be valid JSON
    output_data = json.loads(result.output.strip())
    assert output_data["id"] == 123456
    assert output_data["username"] == "test_user"
    assert output_data["email"] == "test@example.com"


def test_profile_command_missing_token():
    """Test profile command handles missing authentication token."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test-config"
        # No config file (missing token)

        with patch.object(config, "CONFIG_PATH", config_path):
            result = runner.invoke(profile, [])

    assert result.exit_code == 1
    assert "Authentication error" in result.output
    assert "Please run 'restream.io login' first" in result.output


@responses.activate
def test_profile_command_expired_token():
    """Test profile command handles expired token."""
    responses.add(
        "GET",
        "https://api.restream.io/v2/user/profile",
        json={"error": "Unauthorized"},
        status=401,
    )

    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir)
        tokens_file = config_path / "tokens.json"
        tokens_file.parent.mkdir(parents=True, exist_ok=True)
        tokens_file.write_text('{"access_token": "expired-token"}')

        with patch.object(config, "CONFIG_PATH", config_path):
            result = runner.invoke(profile, [])

    assert result.exit_code == 1
    assert "API error" in result.output
