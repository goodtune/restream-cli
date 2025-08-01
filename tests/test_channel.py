import requests
import responses

from restream_io.api import RestreamClient
from restream_io.schemas import Channel, ChannelSummary


@responses.activate
def test_list_channels():
    """Test list channels endpoint with actual API response format."""
    token = "fake-token"
    # Response from /user/channel/all endpoint - returns ChannelSummary objects
    channels_data = [
        {
            "id": 000,
            "streamingPlatformId": 000,
            "embedUrl": "https://beam.pro/embed/player/xxx",
            "url": "https://beam.pro/xxx",
            "identifier": "xxx",
            "displayName": "xxx",
            "enabled": True,
        },
        {
            "id": 111,
            "streamingPlatformId": 111,
            "embedUrl": "http://www.twitch.tv/xxx/embed",
            "url": "http://twitch.tv/xxx",
            "identifier": "xxx",
            "displayName": "xxx",
            "enabled": False,
        },
    ]

    responses.add(
        "GET",
        "https://api.restream.io/v2/user/channel/all",
        json=channels_data,
        status=200,
    )

    session = requests.Session()
    client = RestreamClient(session, token)
    result = client.list_channels()

    # Should return list of ChannelSummary objects
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(channel, ChannelSummary) for channel in result)

    # Verify first channel (active)
    channel_0 = result[0]
    assert channel_0.id == 000
    assert channel_0.streamingPlatformId == 000
    assert channel_0.embedUrl == "https://beam.pro/embed/player/xxx"
    assert channel_0.url == "https://beam.pro/xxx"
    assert channel_0.identifier == "xxx"
    assert channel_0.displayName == "xxx"
    assert channel_0.enabled is True

    # Verify second channel (inactive)
    channel_1 = result[1]
    assert channel_1.id == 111
    assert channel_1.streamingPlatformId == 111
    assert channel_1.embedUrl == "http://www.twitch.tv/xxx/embed"
    assert channel_1.url == "http://twitch.tv/xxx"
    assert channel_1.identifier == "xxx"
    assert channel_1.displayName == "xxx"
    assert channel_1.enabled is False


@responses.activate
def test_get_channel():
    """Test get single channel endpoint with actual API response format."""
    token = "fake-token"
    # Response from /user/channel/{id} endpoint - returns full Channel object
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

    session = requests.Session()
    client = RestreamClient(session, token)
    result = client.get_channel("123456")

    # Should return full Channel object
    assert isinstance(result, Channel)
    assert result.id == 123456
    assert result.user_id == 674443
    assert result.service_id == 5
    assert result.channel_identifier == "test_channel_id"
    assert result.channel_url == "https://beam.pro/xxx"
    assert result.event_identifier is None
    assert result.event_url is None
    assert result.embed == "https://beam.pro/embed/player/xxx"
    assert result.active is True
    assert result.display_name == "Test Channel"


@responses.activate
def test_list_channels_with_realistic_data():
    """Test list channels with more realistic data."""
    token = "fake-token"
    channels_data = [
        {
            "id": 1001,
            "streamingPlatformId": 1,
            "embedUrl": (
                "https://www.youtube.com/embed/live_stream" "?channel=UCabc123"
            ),
            "url": "https://youtube.com/channel/UCabc123",
            "identifier": "UCabc123",
            "displayName": "My Gaming Channel",
            "enabled": True,
        },
        {
            "id": 1002,
            "streamingPlatformId": 2,
            "embedUrl": "https://player.twitch.tv/?channel=streamerpro",
            "url": "https://twitch.tv/streamerpro",
            "identifier": "streamerpro",
            "displayName": "StreamerPro",
            "enabled": False,
        },
    ]

    responses.add(
        "GET",
        "https://api.restream.io/v2/user/channel/all",
        json=channels_data,
        status=200,
    )

    session = requests.Session()
    client = RestreamClient(session, token)
    result = client.list_channels()

    # Should return list of ChannelSummary objects
    assert isinstance(result, list)
    assert len(result) == 2

    # Verify YouTube channel
    youtube_channel = result[0]
    assert youtube_channel.id == 1001
    assert youtube_channel.displayName == "My Gaming Channel"
    assert youtube_channel.enabled is True

    # Verify Twitch channel
    twitch_channel = result[1]
    assert twitch_channel.id == 1002
    assert twitch_channel.displayName == "StreamerPro"
    assert twitch_channel.enabled is False
