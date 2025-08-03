"""Tests for additional event CLI commands."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import responses
from click.testing import CliRunner

from restream_io import config
from restream_io.cli import cli


@responses.activate
def test_event_in_progress_command():
    """Test event in-progress command."""
    responses.add(
        responses.GET,
        "https://api.restream.io/v2/user/events/in-progress",
        json=[
            {
                "id": "in-progress-event-id",
                "showId": None,
                "status": "in-progress",
                "title": "Live Event",
                "description": "Currently streaming",
                "isInstant": True,
                "isRecordOnly": False,
                "coverUrl": None,
                "scheduledFor": None,
                "startedAt": 1672531200,
                "finishedAt": None,
                "destinations": [],
            }
        ],
        status=200,
    )

    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir)
        tokens_file = config_path / "tokens.json"
        tokens_file.parent.mkdir(parents=True, exist_ok=True)
        tokens_file.write_text('{"access_token": "fake-token"}')

        with patch.object(config, "CONFIG_PATH", config_path):
            result = runner.invoke(cli, ["event", "in-progress"])

        assert result.exit_code == 0
        assert "Live Event" in result.output
        assert "in-progress" in result.output


@responses.activate
def test_event_upcoming_command():
    """Test event upcoming command."""
    responses.add(
        responses.GET,
        "https://api.restream.io/v2/user/events/upcoming",
        json=[
            {
                "id": "upcoming-event-id",
                "showId": None,
                "status": "upcoming",
                "title": "Future Event",
                "description": "Scheduled for later",
                "isInstant": False,
                "isRecordOnly": False,
                "coverUrl": None,
                "scheduledFor": 1672617600,
                "startedAt": None,
                "finishedAt": None,
                "destinations": [],
            }
        ],
        status=200,
    )

    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir)
        tokens_file = config_path / "tokens.json"
        tokens_file.parent.mkdir(parents=True, exist_ok=True)
        tokens_file.write_text('{"access_token": "fake-token"}')

        with patch.object(config, "CONFIG_PATH", config_path):
            result = runner.invoke(cli, ["event", "upcoming"])

        assert result.exit_code == 0
        assert "Future Event" in result.output
        assert "upcoming" in result.output


@responses.activate
def test_event_upcoming_command_with_filters():
    """Test event upcoming command with source and scheduled filters."""
    responses.add(
        responses.GET,
        "https://api.restream.io/v2/user/events/upcoming?source=1&scheduled=true",
        json=[],
        status=200,
    )

    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir)
        tokens_file = config_path / "tokens.json"
        tokens_file.parent.mkdir(parents=True, exist_ok=True)
        tokens_file.write_text('{"access_token": "fake-token"}')

        with patch.object(config, "CONFIG_PATH", config_path):
            result = runner.invoke(
                cli, ["event", "upcoming", "--source", "1", "--scheduled"]
            )

        assert result.exit_code == 0


@responses.activate
def test_event_history_command():
    """Test event history command."""
    responses.add(
        responses.GET,
        "https://api.restream.io/v2/user/events/history?page=1&limit=10",
        json={
            "items": [
                {
                    "id": "history-event-id",
                    "showId": None,
                    "status": "finished",
                    "title": "Past Event",
                    "description": "Completed event",
                    "isInstant": False,
                    "isRecordOnly": False,
                    "coverUrl": None,
                    "scheduledFor": None,
                    "startedAt": 1672531200,
                    "finishedAt": 1672534800,
                    "destinations": [],
                }
            ],
            "pagination": {"pages_total": 1, "page": 1, "limit": 10},
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
            result = runner.invoke(cli, ["event", "history"])

        assert result.exit_code == 0
        assert "Past Event" in result.output
        assert "finished" in result.output


@responses.activate
def test_event_history_command_with_pagination():
    """Test event history command with custom pagination."""
    responses.add(
        responses.GET,
        "https://api.restream.io/v2/user/events/history?page=2&limit=5",
        json={
            "items": [],
            "pagination": {"pages_total": 2, "page": 2, "limit": 5},
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
            result = runner.invoke(
                cli, ["event", "history", "--page", "2", "--limit", "5"]
            )

        assert result.exit_code == 0


@responses.activate
def test_event_in_progress_command_json_output():
    """Test event in-progress command with JSON output."""
    responses.add(
        responses.GET,
        "https://api.restream.io/v2/user/events/in-progress",
        json=[],
        status=200,
    )

    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir)
        tokens_file = config_path / "tokens.json"
        tokens_file.parent.mkdir(parents=True, exist_ok=True)
        tokens_file.write_text('{"access_token": "fake-token"}')

        with patch.object(config, "CONFIG_PATH", config_path):
            result = runner.invoke(cli, ["event", "in-progress", "--json"])

        assert result.exit_code == 0

        # Parse the JSON output
        output_data = json.loads(result.output)
        assert output_data == []
