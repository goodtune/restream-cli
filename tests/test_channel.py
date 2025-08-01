import requests
import responses

from restream_io.api import RestreamClient
from restream_io.schemas import Channel


@responses.activate
def test_list_channels():
    """Test list channels endpoint with actual API response format."""
    token = "fake-token"
    # Exact payload from API documentation
    channels_data = [
        {
            "id": 000,
            "streamingPlatformId": 000,
            "embedUrl": "https://beam.pro/embed/player/xxx",
            "url": "https://beam.pro/xxx",
            "identifier": "xxx",
            "displayName": "xxx",
            "active": True
        },
        {
            "id": 111,
            "streamingPlatformId": 111,
            "embedUrl": "http://www.twitch.tv/xxx/embed",
            "url": "http://twitch.tv/xxx",
            "identifier": "xxx",
            "displayName": "xxx",
            "active": False
        }
    ]
    
    responses.add(
        "GET", "https://api.restream.io/v1/channels", json=channels_data, status=200
    )
    
    session = requests.Session()
    client = RestreamClient(session, token)
    result = client.list_channels()
    
    # Should return list of Channel objects
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(channel, Channel) for channel in result)
    
    # Verify first channel (active)
    channel_0 = result[0]
    assert channel_0.id == 000
    assert channel_0.streamingPlatformId == 000
    assert channel_0.embedUrl == "https://beam.pro/embed/player/xxx"
    assert channel_0.url == "https://beam.pro/xxx"
    assert channel_0.identifier == "xxx"
    assert channel_0.displayName == "xxx"
    assert channel_0.active is True
    
    # Verify second channel (inactive)
    channel_1 = result[1]
    assert channel_1.id == 111
    assert channel_1.streamingPlatformId == 111
    assert channel_1.embedUrl == "http://www.twitch.tv/xxx/embed"
    assert channel_1.url == "http://twitch.tv/xxx"
    assert channel_1.identifier == "xxx"
    assert channel_1.displayName == "xxx"
    assert channel_1.active is False


@responses.activate
def test_get_channel():
    """Test get single channel endpoint with actual API response format."""
    token = "fake-token"
    # Exact payload from API documentation
    channel_data = {
        "id": 123456,
        "streamingPlatformId": 000,
        "embedUrl": "https://beam.pro/embed/player/xxx",
        "url": "https://beam.pro/xxx",
        "identifier": "xxx",
        "displayName": "xxx",
        "active": True
    }
    
    responses.add(
        "GET", "https://api.restream.io/v1/channels/123456", json=channel_data, status=200
    )
    
    session = requests.Session()
    client = RestreamClient(session, token)
    result = client.get_channel("123456")
    
    # Should return Channel object
    assert isinstance(result, Channel)
    assert result.id == 123456
    assert result.streamingPlatformId == 000
    assert result.embedUrl == "https://beam.pro/embed/player/xxx"
    assert result.url == "https://beam.pro/xxx"
    assert result.identifier == "xxx"
    assert result.displayName == "xxx"
    assert result.active is True


@responses.activate
def test_list_channels_with_realistic_data():
    """Test list channels with more realistic data."""
    token = "fake-token"
    channels_data = [
        {
            "id": 1001,
            "streamingPlatformId": 1,
            "embedUrl": "https://www.youtube.com/embed/live_stream?channel=UCabc123",
            "url": "https://youtube.com/channel/UCabc123",
            "identifier": "UCabc123",
            "displayName": "My Gaming Channel",
            "active": True
        },
        {
            "id": 1002,
            "streamingPlatformId": 2,
            "embedUrl": "https://player.twitch.tv/?channel=streamerpro",
            "url": "https://twitch.tv/streamerpro",
            "identifier": "streamerpro",
            "displayName": "StreamerPro",
            "active": False
        }
    ]
    
    responses.add(
        "GET", "https://api.restream.io/v1/channels", json=channels_data, status=200
    )
    
    session = requests.Session()
    client = RestreamClient(session, token)
    result = client.list_channels()
    
    # Should return list of Channel objects
    assert isinstance(result, list)
    assert len(result) == 2
    
    # Verify YouTube channel
    youtube_channel = result[0]
    assert youtube_channel.id == 1001
    assert youtube_channel.displayName == "My Gaming Channel"
    assert youtube_channel.active is True
    
    # Verify Twitch channel
    twitch_channel = result[1]
    assert twitch_channel.id == 1002
    assert twitch_channel.displayName == "StreamerPro"
    assert twitch_channel.active is False
