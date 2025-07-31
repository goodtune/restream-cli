import requests
import responses

from restream_io.api import RestreamClient


@responses.activate
def test_list_events():
    token = "fake-token"
    events = [{"id": "e1", "type": "test"}]
    responses.add("GET", "https://api.restream.io/v1/events", json=events, status=200)
    session = requests.Session()
    client = RestreamClient(session, token)
    result = client.list_events()
    assert result == events
