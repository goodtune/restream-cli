import requests
import responses

from restream_io.api import RestreamClient
from restream_io.schemas import Channel, ChannelList


@responses.activate
def test_list_channels_simple_array():
    """Test list channels endpoint with simple array response."""
    token = "fake-token"
    # Example payload based on typical streaming platform channel structure
    channels_data = [
        {
            "id": "ch_youtube_abc123",
            "name": "My Gaming Channel",
            "platform": "youtube",
            "enabled": True,
            "url": "https://youtube.com/channel/UCabc123",
            "thumbnail_url": "https://yt3.ggpht.com/a/default-user=s88-c-k-c0x00ffffff-no-rj",
            "description": "Gaming content and live streams",
            "followers_count": 15420,
            "created_at": "2023-01-15T10:30:00Z",
            "updated_at": "2024-01-20T14:25:00Z"
        },
        {
            "id": "ch_twitch_xyz789",
            "name": "StreamerPro",
            "platform": "twitch",
            "enabled": True,
            "url": "https://twitch.tv/streamerpro",
            "thumbnail_url": "https://static-cdn.jtvnw.net/jtv_user_pictures/xyz789.jpg",
            "description": "Just chatting and variety gaming",
            "followers_count": 8750,
            "created_at": "2023-03-20T16:45:00Z",
            "updated_at": "2024-01-18T09:12:00Z"
        },
        {
            "id": "ch_facebook_def456",
            "name": "Creative Streams",
            "platform": "facebook",
            "enabled": False,
            "url": "https://facebook.com/creativestreams",
            "followers_count": 2340,
            "created_at": "2023-06-10T12:00:00Z"
        }
    ]
    
    responses.add(
        "GET", "https://api.restream.io/v1/channels", json=channels_data, status=200
    )
    
    session = requests.Session()
    client = RestreamClient(session, token)
    result = client.list_channels()
    
    # Should return list of Channel objects for backward compatibility
    assert isinstance(result, list)
    assert len(result) == 3
    assert all(isinstance(channel, Channel) for channel in result)
    
    # Verify first channel
    youtube_channel = result[0]
    assert youtube_channel.id == "ch_youtube_abc123"
    assert youtube_channel.name == "My Gaming Channel"
    assert youtube_channel.platform == "youtube"
    assert youtube_channel.enabled is True
    assert youtube_channel.followers_count == 15420
    
    # Verify disabled channel
    facebook_channel = result[2]
    assert facebook_channel.enabled is False
    assert facebook_channel.thumbnail_url is None  # Not provided in payload


@responses.activate
def test_list_channels_paginated_response():
    """Test list channels endpoint with paginated response structure."""
    token = "fake-token"
    channels_data = {
        "channels": [
            {
                "id": "ch_youtube_abc123",
                "name": "My Gaming Channel", 
                "platform": "youtube",
                "enabled": True,
                "url": "https://youtube.com/channel/UCabc123",
                "followers_count": 15420
            }
        ],
        "total": 1,
        "page": 1,
        "per_page": 20
    }
    
    responses.add(
        "GET", "https://api.restream.io/v1/channels", json=channels_data, status=200
    )
    
    session = requests.Session()
    client = RestreamClient(session, token)
    result = client.list_channels()
    
    # Should return ChannelList object
    assert isinstance(result, ChannelList)
    assert result.total == 1
    assert len(result.channels) == 1
    assert isinstance(result.channels[0], Channel)


@responses.activate
def test_get_channel():
    """Test get single channel endpoint."""
    token = "fake-token"
    channel_data = {
        "id": "ch_twitch_xyz789",
        "name": "StreamerPro",
        "platform": "twitch",
        "enabled": True,
        "url": "https://twitch.tv/streamerpro",
        "thumbnail_url": "https://static-cdn.jtvnw.net/jtv_user_pictures/xyz789.jpg",
        "description": "Just chatting and variety gaming",
        "followers_count": 8750,
        "created_at": "2023-03-20T16:45:00Z",
        "updated_at": "2024-01-18T09:12:00Z"
    }
    
    responses.add(
        "GET", "https://api.restream.io/v1/channels/ch_twitch_xyz789", json=channel_data, status=200
    )
    
    session = requests.Session()
    client = RestreamClient(session, token)
    result = client.get_channel("ch_twitch_xyz789")
    
    # Should return Channel object
    assert isinstance(result, Channel)
    assert result.id == "ch_twitch_xyz789"
    assert result.name == "StreamerPro"
    assert result.platform == "twitch"
    assert result.enabled is True
    assert result.followers_count == 8750
    assert result.description == "Just chatting and variety gaming"


@responses.activate
def test_get_channel_minimal():
    """Test get channel with minimal required fields."""
    token = "fake-token"
    channel_data = {
        "id": "ch_minimal",
        "name": "Minimal Channel",
        "platform": "unknown",
        "enabled": True
    }
    
    responses.add(
        "GET", "https://api.restream.io/v1/channels/ch_minimal", json=channel_data, status=200
    )
    
    session = requests.Session()
    client = RestreamClient(session, token)
    result = client.get_channel("ch_minimal")
    
    # Should return Channel object with defaults
    assert isinstance(result, Channel)
    assert result.id == "ch_minimal"
    assert result.name == "Minimal Channel"
    assert result.platform == "unknown"
    assert result.enabled is True
    assert result.followers_count is None  # Default value
