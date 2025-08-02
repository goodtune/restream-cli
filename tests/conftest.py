import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import requests
import responses

from restream_io import config
from restream_io.api import RestreamClient


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    # Prevent real HTTP requests by default; tests should enable responses
    pass


@pytest.fixture
def mock_session():
    """Create a mock requests session for testing."""
    session = requests.Session()
    return session


@pytest.fixture
def test_token():
    """Provide a test token for API authentication."""
    return "test-token-12345"


@pytest.fixture
def mock_client(mock_session, test_token):
    """Create a RestreamClient with mocked token for testing."""
    return RestreamClient(mock_session, test_token)


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for config tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(config, "CONFIG_PATH", Path(tmpdir) / "test-config"):
            yield Path(tmpdir) / "test-config"


@pytest.fixture
def mock_tokens_file(temp_config_dir):
    """Create a temporary tokens file with test data."""
    tokens_data = {
        "access_token": "test-access-token",
        "refresh_token": "test-refresh-token",
        "expires_at": 1999999999,  # Far future timestamp
    }
    tokens_file = temp_config_dir / "tokens.json"
    tokens_file.parent.mkdir(parents=True, exist_ok=True)
    with open(tokens_file, "w") as f:
        import json

        json.dump(tokens_data, f)
    return tokens_file


@pytest.fixture
def responses_mock():
    """Activate responses for HTTP mocking."""
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def common_api_responses():
    """Common API response payloads for testing."""
    return {
        "profile": {"id": 123456, "username": "test_user", "email": "test@example.com"},
        "channel_summary": {
            "id": 123,
            "displayName": "Test Channel",
            "enabled": True,
            "streamingPlatformId": 1,
            "identifier": "test_channel",
            "url": "https://twitch.tv/test_channel",
        },
        "channel_detail": {
            "id": 123,
            "display_name": "Test Channel",
            "active": True,
            "channel_url": "https://twitch.tv/test_channel",
            "channel_identifier": "test_channel",
            "service_id": 1,
            "user_id": 456,
        },
        "stream_event": {
            "id": "event123",
            "showId": "show456",
            "status": "scheduled",
            "title": "Test Stream Event",
            "description": "Test event description",
            "isInstant": False,
            "isRecordOnly": True,
            "coverUrl": "https://example.com/cover.jpg",
            "scheduledFor": 1672531200,
            "startedAt": None,
            "finishedAt": None,
            "destinations": [],
        },
    }
