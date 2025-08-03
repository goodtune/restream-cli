"""Tests for stream-key CLI commands."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import responses
from click.testing import CliRunner

from restream_io import config
from restream_io.cli import cli


@responses.activate
def test_stream_key_get_command_human_readable_output():
    """Test stream-key get command with human-readable output."""
    responses.add(
        responses.GET,
        "https://api.restream.io/v2/user/streamKey",
        json={
            "streamKey": "re_123_456",
            "srtUrl": "srt://live.restream.io:2010?streamid=srt_789_abc&passphrase=re_123_456",
        },
        status=200,
    )

    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir)
        tokens_file = config_path / "tokens.json"
        tokens_file.parent.mkdir(parents=True, exist_ok=True)
        tokens_file.write_text('{"access_token": "fake-token"}')

        with patch.object(config, "CONFIG_PATH", config_path):
            result = runner.invoke(cli, ["stream-key", "get"])

        assert result.exit_code == 0
        assert "Stream Key: re_123_456" in result.output
        assert "SRT URL: srt://live.restream.io:2010" in result.output


@responses.activate
def test_stream_key_get_command_json_output():
    """Test stream-key get command with JSON output."""
    responses.add(
        responses.GET,
        "https://api.restream.io/v2/user/streamKey",
        json={
            "streamKey": "re_123_456",
            "srtUrl": None,
        },
        status=200,
    )

    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir)
        tokens_file = config_path / "tokens.json"
        tokens_file.parent.mkdir(parents=True, exist_ok=True)
        tokens_file.write_text('{"access_token": "fake-token"}')

        with patch.object(config, "CONFIG_PATH", config_path):
            result = runner.invoke(cli, ["stream-key", "get", "--json"])

        assert result.exit_code == 0

        # Parse the JSON output
        output_data = json.loads(result.output)
        assert output_data["streamKey"] == "re_123_456"
        assert output_data["srtUrl"] is None


@responses.activate
def test_event_stream_key_command_human_readable_output():
    """Test event stream-key command with human-readable output."""
    responses.add(
        responses.GET,
        "https://api.restream.io/v2/user/events/test-event-id/streamKey",
        json={
            "streamKey": "re_event_789",
            "srtUrl": "srt://live.restream.io:2010?streamid=srt_event_def&passphrase=re_event_789",
        },
        status=200,
    )

    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir)
        tokens_file = config_path / "tokens.json"
        tokens_file.parent.mkdir(parents=True, exist_ok=True)
        tokens_file.write_text('{"access_token": "fake-token"}')

        with patch.object(config, "CONFIG_PATH", config_path):
            result = runner.invoke(cli, ["event", "stream-key", "test-event-id"])

        assert result.exit_code == 0
        assert "Stream Key: re_event_789" in result.output
        assert "SRT URL: srt://live.restream.io:2010" in result.output


@responses.activate
def test_event_stream_key_command_not_found():
    """Test event stream-key command when event is not found."""
    responses.add(
        responses.GET,
        "https://api.restream.io/v2/user/events/nonexistent-id/streamKey",
        json={"error": {"message": "Event not found"}},
        status=404,
    )

    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir)
        tokens_file = config_path / "tokens.json"
        tokens_file.parent.mkdir(parents=True, exist_ok=True)
        tokens_file.write_text('{"access_token": "fake-token"}')

        with patch.object(config, "CONFIG_PATH", config_path):
            result = runner.invoke(cli, ["event", "stream-key", "nonexistent-id"])

        assert result.exit_code == 1
        assert "Event not found: nonexistent-id" in result.output


@responses.activate
def test_stream_key_get_command_api_error():
    """Test stream-key get command when API returns an error."""
    responses.add(
        responses.GET,
        "https://api.restream.io/v2/user/streamKey",
        json={"error": {"message": "Internal server error"}},
        status=500,
    )

    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir)
        tokens_file = config_path / "tokens.json"
        tokens_file.parent.mkdir(parents=True, exist_ok=True)
        tokens_file.write_text('{"access_token": "fake-token"}')

        with patch.object(config, "CONFIG_PATH", config_path):
            result = runner.invoke(cli, ["stream-key", "get"])

        assert result.exit_code == 1
        assert "API error" in result.output
