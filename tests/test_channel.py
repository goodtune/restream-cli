import requests
import responses

from restream_io.api import RestreamClient


@responses.activate
def test_list_channels():
    token = "fake-token"
    channels = [{"id": "c1", "name": "Channel One"}]
    responses.add(
        "GET", "https://api.restream.io/v1/channels", json=channels, status=200
    )
    session = requests.Session()
    client = RestreamClient(session, token)
    result = client.list_channels()
    assert result == channels


@responses.activate
def test_get_channel():
    token = "fake-token"
    channel = {"id": "c1", "name": "Channel One"}
    responses.add(
        "GET", "https://api.restream.io/v1/channels/c1", json=channel, status=200
    )
    session = requests.Session()
    client = RestreamClient(session, token)
    result = client.get_channel("c1")
    assert result == channel
