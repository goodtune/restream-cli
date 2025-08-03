"""Tests for event get CLI command."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import responses
from click.testing import CliRunner

from restream_io import config
from restream_io.cli import cli


@responses.activate
def test_event_get_command_human_readable_output():
    """Test event get command with human-readable output."""
    responses.add(
        responses.GET,
        "https://api.restream.io/v2/user/events/test-event-id",
        json={
            "id": "test-event-id",
            "showId": "show-123",
            "status": "upcoming",
            "title": "Test Event",
            "description": "A test event description",
            "isInstant": False,
            "isRecordOnly": False,
            "coverUrl": "https://example.com/cover.jpg",
            "scheduledFor": 1599983310,
            "startedAt": None,
            "finishedAt": None,
            "destinations": [
                {
                    "channelId": 1,
                    "externalUrl": "https://youtube.com/watch?v=123",
                    "streamingPlatformId": 5,
                }
            ],
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
            result = runner.invoke(cli, ["event", "get", "test-event-id"])

        assert result.exit_code == 0
        assert "Test Event" in result.output
        assert "test-event-id" in result.output
        assert "upcoming" in result.output


@responses.activate
def test_event_get_command_json_output():
    """Test event get command with JSON output."""
    responses.add(
        responses.GET,
        "https://api.restream.io/v2/user/events/test-event-id",
        json={
            "id": "test-event-id",
            "showId": None,
            "status": "upcoming",
            "title": "Test Event",
            "description": "A test event description",
            "isInstant": False,
            "isRecordOnly": False,
            "coverUrl": None,
            "scheduledFor": None,
            "startedAt": None,
            "finishedAt": None,
            "destinations": [],
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
            result = runner.invoke(cli, ["event", "get", "test-event-id", "--json"])

        assert result.exit_code == 0

        # Parse the JSON output
        output_data = json.loads(result.output)
        assert output_data["id"] == "test-event-id"
        assert output_data["title"] == "Test Event"
        assert output_data["status"] == "upcoming"


@responses.activate
def test_event_get_command_not_found():
    """Test event get command when event is not found."""
    responses.add(
        responses.GET,
        "https://api.restream.io/v2/user/events/nonexistent-id",
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
            result = runner.invoke(cli, ["event", "get", "nonexistent-id"])

        assert result.exit_code == 1
        assert "Event not found: nonexistent-id" in result.output


@responses.activate
def test_event_get_command_api_error():
    """Test event get command when API returns an error."""
    responses.add(
        responses.GET,
        "https://api.restream.io/v2/user/events/test-event-id",
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
            result = runner.invoke(cli, ["event", "get", "test-event-id"])

        assert result.exit_code == 1
        assert "API error" in result.output
