import requests
import responses

from restream_io.api import RestreamClient
from restream_io.schemas import EventList, StreamEvent


@responses.activate
def test_list_events_simple_array():
    """Test list events endpoint with simple array response."""
    token = "fake-token"
    # Example payload based on typical streaming platform event structure
    events_data = [
        {
            "id": "evt_live_stream_abc123",
            "title": "Morning Gaming Session",
            "status": "live",
            "type": "stream",
            "start_time": "2024-01-20T09:00:00Z",
            "duration": 7200,  # 2 hours in seconds
            "viewer_count": 145,
            "peak_viewers": 203,
            "created_at": "2024-01-20T08:45:00Z",
            "updated_at": "2024-01-20T11:15:00Z"
        },
        {
            "id": "evt_scheduled_abc456",
            "title": "Weekend Variety Stream",
            "status": "scheduled",
            "type": "stream",
            "start_time": "2024-01-27T20:00:00Z",
            "created_at": "2024-01-15T14:30:00Z",
            "updated_at": "2024-01-15T14:30:00Z"
        },
        {
            "id": "evt_ended_xyz789",
            "title": "Tutorial: Setting up OBS",
            "status": "ended",
            "type": "tutorial",
            "start_time": "2024-01-18T15:00:00Z",
            "end_time": "2024-01-18T16:30:00Z",
            "duration": 5400,  # 1.5 hours
            "viewer_count": 0,
            "peak_viewers": 89,
            "created_at": "2024-01-18T14:45:00Z",
            "updated_at": "2024-01-18T16:35:00Z"
        }
    ]
    
    responses.add(
        "GET", "https://api.restream.io/v1/events", json=events_data, status=200
    )
    
    session = requests.Session()
    client = RestreamClient(session, token)
    result = client.list_events()
    
    # Should return list of StreamEvent objects for backward compatibility
    assert isinstance(result, list)
    assert len(result) == 3
    assert all(isinstance(event, StreamEvent) for event in result)
    
    # Verify live event
    live_event = result[0]
    assert live_event.id == "evt_live_stream_abc123"
    assert live_event.title == "Morning Gaming Session"
    assert live_event.status == "live"
    assert live_event.type == "stream"
    assert live_event.viewer_count == 145
    assert live_event.peak_viewers == 203
    assert live_event.duration == 7200
    
    # Verify scheduled event
    scheduled_event = result[1]
    assert scheduled_event.status == "scheduled"
    assert scheduled_event.end_time is None  # Not ended yet
    assert scheduled_event.viewer_count is None  # Not started
    
    # Verify ended event  
    ended_event = result[2]
    assert ended_event.status == "ended"
    assert ended_event.end_time is not None
    assert ended_event.viewer_count == 0  # Stream ended


@responses.activate
def test_list_events_paginated_response():
    """Test list events endpoint with paginated response structure."""
    token = "fake-token"
    events_data = {
        "events": [
            {
                "id": "evt_live_stream_abc123",
                "title": "Morning Gaming Session",
                "status": "live",
                "type": "stream",
                "start_time": "2024-01-20T09:00:00Z",
                "viewer_count": 145,
                "peak_viewers": 203
            }
        ],
        "total": 25,
        "page": 1,
        "per_page": 20
    }
    
    responses.add(
        "GET", "https://api.restream.io/v1/events", json=events_data, status=200
    )
    
    session = requests.Session()
    client = RestreamClient(session, token)
    result = client.list_events()
    
    # Should return EventList object
    assert isinstance(result, EventList)
    assert result.total == 25
    assert result.page == 1
    assert result.per_page == 20
    assert len(result.events) == 1
    assert isinstance(result.events[0], StreamEvent)


@responses.activate
def test_list_events_minimal():
    """Test list events with minimal required fields."""
    token = "fake-token"
    events_data = [
        {
            "id": "evt_minimal",
            "title": "",
            "status": "",
            "type": ""
        }
    ]
    
    responses.add(
        "GET", "https://api.restream.io/v1/events", json=events_data, status=200
    )
    
    session = requests.Session()
    client = RestreamClient(session, token)
    result = client.list_events()
    
    # Should return list with StreamEvent object with defaults
    assert isinstance(result, list)
    assert len(result) == 1
    event = result[0]
    assert isinstance(event, StreamEvent)
    assert event.id == "evt_minimal"
    assert event.title == ""
    assert event.viewer_count is None  # Default value
