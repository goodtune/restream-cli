import requests
import responses

from restream_io.api import RestreamClient
from restream_io.schemas import StreamEvent, EventDestination


@responses.activate
def test_list_events():
    """Test list events endpoint with actual API response format."""
    token = "fake-token"
    # Exact payload from API documentation
    events_data = [
        {
            "id": "2527849f-f961-4b1d-8ae0-8eae4f068327",
            "status": "upcoming",
            "title": "Event title",
            "description": "Event description",
            "coverUrl": "URL or null",
            "scheduledFor": 1599983310,
            "startedAt": None,
            "finishedAt": None,
            "destinations": [
                {
                    "channelId": 1,
                    "externalUrl": "URL or null",
                    "streamingPlatformId": 5
                }
            ]
        }
    ]
    
    responses.add(
        "GET", "https://api.restream.io/v1/events", json=events_data, status=200
    )
    
    session = requests.Session()
    client = RestreamClient(session, token)
    result = client.list_events()
    
    # Should return list of StreamEvent objects
    assert isinstance(result, list)
    assert len(result) == 1
    assert all(isinstance(event, StreamEvent) for event in result)
    
    # Verify event
    event = result[0]
    assert event.id == "2527849f-f961-4b1d-8ae0-8eae4f068327"
    assert event.status == "upcoming"
    assert event.title == "Event title"
    assert event.description == "Event description"
    assert event.coverUrl == "URL or null"
    assert event.scheduledFor == 1599983310
    assert event.startedAt is None
    assert event.finishedAt is None
    
    # Verify destinations
    assert len(event.destinations) == 1
    destination = event.destinations[0]
    assert isinstance(destination, EventDestination)
    assert destination.channelId == 1
    assert destination.externalUrl == "URL or null"
    assert destination.streamingPlatformId == 5


@responses.activate
def test_list_events_with_realistic_data():
    """Test list events with more realistic data."""
    token = "fake-token"
    events_data = [
        {
            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "status": "live",
            "title": "Gaming Stream - Elden Ring",
            "description": "Playing through Elden Ring boss battles",
            "coverUrl": "https://cdn.restream.io/covers/event123.jpg",
            "scheduledFor": 1640995200,  # 2022-01-01 00:00:00 UTC
            "startedAt": 1640995320,     # Started 2 minutes later
            "finishedAt": None,          # Still live
            "destinations": [
                {
                    "channelId": 1001,
                    "externalUrl": "https://youtube.com/watch?v=xyz123",
                    "streamingPlatformId": 1
                },
                {
                    "channelId": 1002,
                    "externalUrl": "https://twitch.tv/streamerpro",
                    "streamingPlatformId": 2
                }
            ]
        },
        {
            "id": "7b68c3e2-1234-4567-89ab-cdef01234567",
            "status": "ended",
            "title": "Tutorial: Setting up OBS",
            "description": "Complete guide to OBS configuration",
            "coverUrl": None,
            "scheduledFor": 1640908800,  # Earlier timestamp
            "startedAt": 1640908900,
            "finishedAt": 1640912500,    # 1 hour stream
            "destinations": [
                {
                    "channelId": 1001,
                    "externalUrl": None,
                    "streamingPlatformId": 1
                }
            ]
        }
    ]
    
    responses.add(
        "GET", "https://api.restream.io/v1/events", json=events_data, status=200
    )
    
    session = requests.Session()
    client = RestreamClient(session, token)
    result = client.list_events()
    
    # Should return list of StreamEvent objects
    assert isinstance(result, list)
    assert len(result) == 2
    
    # Verify live event
    live_event = result[0]
    assert live_event.status == "live"
    assert live_event.title == "Gaming Stream - Elden Ring"
    assert live_event.startedAt == 1640995320
    assert live_event.finishedAt is None
    assert len(live_event.destinations) == 2
    
    # Verify ended event
    ended_event = result[1]
    assert ended_event.status == "ended"
    assert ended_event.title == "Tutorial: Setting up OBS"
    assert ended_event.coverUrl is None
    assert ended_event.finishedAt == 1640912500
    assert len(ended_event.destinations) == 1


@responses.activate
def test_list_events_empty():
    """Test list events with empty response."""
    token = "fake-token"
    events_data = []
    
    responses.add(
        "GET", "https://api.restream.io/v1/events", json=events_data, status=200
    )
    
    session = requests.Session()
    client = RestreamClient(session, token)
    result = client.list_events()
    
    # Should return empty list
    assert isinstance(result, list)
    assert len(result) == 0
