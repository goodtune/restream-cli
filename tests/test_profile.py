import responses
import pytest
from restream_io.api import RestreamClient
import requests

@responses.activate
def test_get_profile(monkeypatch):
    token = "fake-token"
    profile_data = {"id": "user123", "name": "Test User"}
    responses.add("GET", "https://api.restream.io/v1/profile", json=profile_data, status=200)
    session = requests.Session()
    client = RestreamClient(session, token)
    result = client.get_profile()
    assert result == profile_data
