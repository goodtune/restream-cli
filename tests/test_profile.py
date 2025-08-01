import requests
import responses

from restream_io.api import RestreamClient
from restream_io.schemas import Profile


@responses.activate
def test_get_profile():
    """Test profile endpoint with actual API response format."""
    token = "fake-token"
    # Exact payload from API documentation
    profile_data = {"id": 000, "username": "xxx", "email": "xxx"}

    responses.add(
        "GET", "https://api.restream.io/v2/user/profile", json=profile_data, status=200
    )

    session = requests.Session()
    client = RestreamClient(session, token)
    result = client.get_profile()

    # Verify we get a Profile object
    assert isinstance(result, Profile)

    # Verify profile data matches API documentation format
    assert result.id == 000
    assert result.username == "xxx"
    assert result.email == "xxx"


@responses.activate
def test_get_profile_with_actual_values():
    """Test profile endpoint with realistic values."""
    token = "fake-token"
    profile_data = {
        "id": 123456,
        "username": "streamer_user",
        "email": "user@example.com",
    }

    responses.add(
        "GET", "https://api.restream.io/v2/user/profile", json=profile_data, status=200
    )

    session = requests.Session()
    client = RestreamClient(session, token)
    result = client.get_profile()

    # Verify we get a Profile object with correct data
    assert isinstance(result, Profile)
    assert result.id == 123456
    assert result.username == "streamer_user"
    assert result.email == "user@example.com"
