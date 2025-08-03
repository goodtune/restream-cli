"""Test CLI event command output formatting."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import responses
from click.testing import CliRunner

from restream_io import config
from restream_io.cli import cli
from restream_io.schemas import (
    EventDestination,
    EventsHistoryResponse,
    EventsPagination,
    StreamEvent,
)


def test_stream_event_str_method():
    """Test StreamEvent.__str__ method for human-readable output."""
    # Test with all fields populated
    destination1 = EventDestination(
        channelId=123,
        externalUrl="https://twitch.tv/testchannel",
        streamingPlatformId=1,
    )
    destination2 = EventDestination(
        channelId=456, externalUrl=None, streamingPlatformId=2
    )

    event_full = StreamEvent(
        id="event123",
        showId="show456",
        status="scheduled",
        title="Test Stream Event",
        description="This is a test event",
        isInstant=False,
        isRecordOnly=True,
        coverUrl="https://example.com/cover.jpg",
        scheduledFor=1672531200,  # 2023-01-01 00:00:00 UTC
        startedAt=1672531300,  # 2023-01-01 00:01:40 UTC
        finishedAt=1672534800,  # 2023-01-01 01:00:00 UTC
        destinations=[destination1, destination2],
    )

    output = str(event_full)

    assert "Event: Test Stream Event" in output
    assert "ID: event123" in output
    assert "Status: scheduled" in output
    assert "Description: This is a test event" in output
    assert "Instant: No" in output
    assert "Record Only: Yes" in output
    assert "Show ID: show456" in output
    assert "Scheduled: 2023-01-01 00:00:00" in output
    assert "Started: 2023-01-01 00:01:40" in output
    assert "Finished: 2023-01-01 01:00:00" in output
    assert "Cover URL: https://example.com/cover.jpg" in output
    assert "Destinations (2):" in output
    assert "Channel ID: 123" in output
    assert "External URL: https://twitch.tv/testchannel" in output

    # Test with minimal fields
    event_minimal = StreamEvent(
        id="event789",
        showId=None,
        status="live",
        title="Minimal Event",
        description="Minimal description",
        isInstant=True,
        isRecordOnly=False,
        coverUrl=None,
        scheduledFor=None,
        startedAt=None,
        finishedAt=None,
        destinations=[],
    )

    output_minimal = str(event_minimal)

    assert "Event: Minimal Event" in output_minimal
    assert "Status: live" in output_minimal
    assert "Instant: Yes" in output_minimal
    assert "Record Only: No" in output_minimal
    assert "Show ID:" not in output_minimal
    assert "Scheduled:" not in output_minimal
    assert "Cover URL:" not in output_minimal
    assert "Destinations (0):" in output_minimal


def test_event_destination_str_method():
    """Test EventDestination.__str__ method for human-readable output."""
    # Test with external URL
    dest_with_url = EventDestination(
        channelId=123,
        externalUrl="https://youtube.com/channel/test",
        streamingPlatformId=3,
    )

    output = str(dest_with_url)
    assert "Destination:" in output
    assert "Channel ID: 123" in output
    assert "Platform ID: 3" in output
    assert "External URL: https://youtube.com/channel/test" in output

    # Test without external URL
    dest_no_url = EventDestination(
        channelId=456, externalUrl=None, streamingPlatformId=1
    )

    output_no_url = str(dest_no_url)
    assert "Channel ID: 456" in output_no_url
    assert "Platform ID: 1" in output_no_url
    assert "External URL:" not in output_no_url


def test_events_pagination_str_method():
    """Test EventsPagination.__str__ method for human-readable output."""
    pagination = EventsPagination(pages_total=5, page=2, limit=10)

    output = str(pagination)
    assert "Page 2 of 5 (showing up to 10 items per page)" == output


def test_events_history_response_str_method():
    """Test EventsHistoryResponse.__str__ method for human-readable output."""
    pagination = EventsPagination(pages_total=3, page=1, limit=2)

    event1 = StreamEvent(
        id="event1",
        showId=None,
        status="completed",
        title="Event One",
        description="First event",
        isInstant=False,
        isRecordOnly=False,
        coverUrl=None,
        scheduledFor=None,
        startedAt=None,
        finishedAt=None,
        destinations=[],
    )

    event2 = StreamEvent(
        id="event2",
        showId=None,
        status="live",
        title="Event Two",
        description="Second event",
        isInstant=True,
        isRecordOnly=True,
        coverUrl=None,
        scheduledFor=None,
        startedAt=None,
        finishedAt=None,
        destinations=[],
    )

    response = EventsHistoryResponse(items=[event1, event2], pagination=pagination)

    output = str(response)

    assert "Events History (2 events):" in output
    assert "Page 1 of 3 (showing up to 2 items per page)" in output
    assert "1. Event: Event One" in output
    assert "2. Event: Event Two" in output


@responses.activate
def test_event_list_command_human_readable_output():
    """Test event list command displays human-readable output by default."""
    # Mock event API responses
    history_data = {
        "items": [
            {
                "id": "event123",
                "showId": None,
                "status": "completed",
                "title": "Past Event",
                "description": "A completed event",
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
    }

    in_progress_data = [
        {
            "id": "event456",
            "showId": "show123",
            "status": "live",
            "title": "Live Event",
            "description": "Currently streaming",
            "isInstant": True,
            "isRecordOnly": False,
            "coverUrl": "https://example.com/cover.jpg",
            "scheduledFor": 1672531000,
            "startedAt": 1672531200,
            "finishedAt": None,
            "destinations": [
                {
                    "channelId": 123,
                    "externalUrl": "https://twitch.tv/test",
                    "streamingPlatformId": 1,
                }
            ],
        }
    ]

    upcoming_data = []

    responses.add(
        "GET",
        "https://api.restream.io/v2/user/events/history?page=1&limit=10",
        json=history_data,
        status=200,
    )

    responses.add(
        "GET",
        "https://api.restream.io/v2/user/events/in-progress",
        json=in_progress_data,
        status=200,
    )

    responses.add(
        "GET",
        "https://api.restream.io/v2/user/events/upcoming",
        json=upcoming_data,
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
            result = runner.invoke(cli, ["event", "list"])

    assert result.exit_code == 0
    assert "1. Event: Past Event" in result.output
    assert "2. Event: Live Event" in result.output
    assert "Status: completed" in result.output
    assert "Status: live" in result.output
    # Should not contain JSON format
    assert "{\n" not in result.output


@responses.activate
def test_event_list_command_json_output():
    """Test event list command outputs JSON when --json flag is used."""
    # Mock empty responses for simplicity
    history_data = {
        "items": [],
        "pagination": {"pages_total": 0, "page": 1, "limit": 10},
    }
    in_progress_data = []
    upcoming_data = []

    responses.add(
        "GET",
        "https://api.restream.io/v2/user/events/history?page=1&limit=10",
        json=history_data,
        status=200,
    )

    responses.add(
        "GET",
        "https://api.restream.io/v2/user/events/in-progress",
        json=in_progress_data,
        status=200,
    )

    responses.add(
        "GET",
        "https://api.restream.io/v2/user/events/upcoming",
        json=upcoming_data,
        status=200,
    )

    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir)
        tokens_file = config_path / "tokens.json"
        tokens_file.parent.mkdir(parents=True, exist_ok=True)
        tokens_file.write_text('{"access_token": "fake-token"}')

        with patch.object(config, "CONFIG_PATH", config_path):
            result = runner.invoke(cli, ["event", "list", "--json"])

    assert result.exit_code == 0
    # Should be valid JSON (empty list in this case)
    output_data = json.loads(result.output.strip())
    assert output_data == []


@responses.activate
def test_event_list_command_api_error():
    """Test event list command handles API errors gracefully."""
    responses.add(
        "GET",
        "https://api.restream.io/v2/user/events/history?page=1&limit=10",
        json={"message": "Internal server error"},
        status=500,
    )

    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir)
        tokens_file = config_path / "tokens.json"
        tokens_file.parent.mkdir(parents=True, exist_ok=True)
        tokens_file.write_text('{"access_token": "fake-token"}')

        with patch.object(config, "CONFIG_PATH", config_path):
            result = runner.invoke(cli, ["event", "list"])

    assert result.exit_code == 1
    assert "API error:" in result.output
