"""Test CLI channel command output formatting."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import responses
from click.testing import CliRunner

from restream_io import config
from restream_io.cli import cli
from restream_io.schemas import Channel


def test_channel_str_method():
    """Test Channel.__str__ method for human-readable output."""
    # Test with all fields populated
    channel_full = Channel(
        id=123456,
        user_id=674443,
        service_id=5,
        channel_identifier="test_channel_id",
        channel_url="https://beam.pro/xxx",
        event_identifier="event123",
        event_url="https://example.com/event",
        embed="https://beam.pro/embed/player/xxx",
        active=True,
        display_name="Test Channel",
    )

    output = str(channel_full)

    assert "Channel Information:" in output
    assert "ID: 123456" in output
    assert "Display Name: Test Channel" in output
    assert "Status: Active" in output
    assert "Channel URL: https://beam.pro/xxx" in output
    assert "Channel Identifier: test_channel_id" in output
    assert "Service ID: 5" in output
    assert "User ID: 674443" in output
    assert "Event Identifier: event123" in output
    assert "Event URL: https://example.com/event" in output

    # Test with inactive channel and no event info
    channel_minimal = Channel(
        id=999,
        user_id=111,
        service_id=2,
        channel_identifier="minimal",
        channel_url="https://twitch.tv/minimal",
        event_identifier=None,
        event_url=None,
        embed="https://player.twitch.tv/?channel=minimal",
        active=False,
        display_name="Minimal Channel",
    )

    output_minimal = str(channel_minimal)

    assert "Status: Inactive" in output_minimal
    assert "Event Identifier:" not in output_minimal
    assert "Event URL:" not in output_minimal


@responses.activate
def test_channel_get_command_human_readable_output():
    """Test channel get command displays human-readable output by default."""
    # Mock channel API response
    channel_data = {
        "id": 123456,
        "user_id": 674443,
        "service_id": 5,
        "channel_identifier": "test_channel_id",
        "channel_url": "https://beam.pro/xxx",
        "event_identifier": None,
        "event_url": None,
        "embed": "https://beam.pro/embed/player/xxx",
        "active": True,
        "display_name": "Test Channel",
    }

    responses.add(
        "GET",
        "https://api.restream.io/v2/user/channel/123456",
        json=channel_data,
        status=200,
    )

    runner = CliRunner()

    # Mock config with valid token
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir)
        tokens_file = config_path / "tokens.json"
        tokens_file.parent.mkdir(parents=True, exist_ok=True)
        tokens_file.write_text('{"access_token": "fake-token"}')

        with patch.object(config, "CONFIG_PATH", config_path):
            result = runner.invoke(cli, ["channel", "get", "123456"])

    assert result.exit_code == 0
    assert "Channel Information:" in result.output
    assert "ID: 123456" in result.output
    assert "Display Name: Test Channel" in result.output
    assert "Status: Active" in result.output
    assert "Channel URL: https://beam.pro/xxx" in result.output
    # Should not contain JSON format
    assert "{\n" not in result.output


@responses.activate
def test_channel_get_command_json_output():
    """Test channel get command outputs JSON when --json flag is used."""
    channel_data = {
        "id": 123456,
        "user_id": 674443,
        "service_id": 5,
        "channel_identifier": "test_channel_id",
        "channel_url": "https://beam.pro/xxx",
        "event_identifier": None,
        "event_url": None,
        "embed": "https://beam.pro/embed/player/xxx",
        "active": True,
        "display_name": "Test Channel",
    }

    responses.add(
        "GET",
        "https://api.restream.io/v2/user/channel/123456",
        json=channel_data,
        status=200,
    )

    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir)
        tokens_file = config_path / "tokens.json"
        tokens_file.parent.mkdir(parents=True, exist_ok=True)
        tokens_file.write_text('{"access_token": "fake-token"}')

        with patch.object(config, "CONFIG_PATH", config_path):
            result = runner.invoke(cli, ["channel", "get", "123456", "--json"])

    assert result.exit_code == 0
    # Should be valid JSON
    output_data = json.loads(result.output.strip())
    assert output_data["id"] == 123456
    assert output_data["display_name"] == "Test Channel"
    assert output_data["active"] is True


@responses.activate
def test_channel_get_command_not_found():
    """Test channel get command handles 404 error with human-readable message."""
    responses.add(
        "GET",
        "https://api.restream.io/v2/user/channel/999999",
        json={"message": "Channel not found"},
        status=404,
    )

    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir)
        tokens_file = config_path / "tokens.json"
        tokens_file.parent.mkdir(parents=True, exist_ok=True)
        tokens_file.write_text('{"access_token": "fake-token"}')

        with patch.object(config, "CONFIG_PATH", config_path):
            result = runner.invoke(cli, ["channel", "get", "999999"])

    assert result.exit_code == 1
    assert "Channel not found: 999999" in result.output
