import requests
import responses

from restream_io.api import RestreamClient
from restream_io.schemas import Profile, User


@responses.activate
def test_get_profile_flat_response(monkeypatch):
    """Test profile endpoint with flat user data response."""
    token = "fake-token"
    # Example payload based on typical REST API user profile structure
    profile_data = {
        "id": "user_5f9a8b1234567890",
        "username": "streamuser123", 
        "display_name": "John Streamer",
        "email": "john@example.com",
        "avatar_url": "https://cdn.restream.io/avatars/user_5f9a8b1234567890.jpg",
        "created_at": "2023-01-15T10:30:00Z",
        "verified": True,
        "subscription_plan": "pro",
        "streaming_quota": {
            "used": 150,
            "limit": 1000,
            "reset_date": "2024-02-01T00:00:00Z"
        },
        "features": ["multi_platform", "custom_overlays", "analytics"]
    }
    
    responses.add(
        "GET", "https://api.restream.io/v1/profile", json=profile_data, status=200
    )
    
    session = requests.Session()
    client = RestreamClient(session, token)
    result = client.get_profile()
    
    # Verify we get a Profile object
    assert isinstance(result, Profile)
    assert isinstance(result.user, User)
    
    # Verify user data
    assert result.user.id == "user_5f9a8b1234567890"
    assert result.user.username == "streamuser123"
    assert result.user.display_name == "John Streamer"
    assert result.user.email == "john@example.com"
    assert result.user.avatar_url == "https://cdn.restream.io/avatars/user_5f9a8b1234567890.jpg"
    assert result.user.verified is True
    
    # Verify profile-level data
    assert result.subscription_plan == "pro"
    assert result.streaming_quota == {
        "used": 150,
        "limit": 1000,
        "reset_date": "2024-02-01T00:00:00Z"
    }
    assert result.features == ["multi_platform", "custom_overlays", "analytics"]


@responses.activate
def test_get_profile_nested_response():
    """Test profile endpoint with nested user data response."""
    token = "fake-token"
    # Example payload with nested user object
    profile_data = {
        "user": {
            "id": "user_5f9a8b1234567890",
            "username": "streamuser123", 
            "display_name": "John Streamer",
            "email": "john@example.com",
            "avatar_url": "https://cdn.restream.io/avatars/user_5f9a8b1234567890.jpg",
            "created_at": "2023-01-15T10:30:00Z",
            "verified": True
        },
        "subscription_plan": "pro",
        "streaming_quota": {
            "used": 150,
            "limit": 1000,
            "reset_date": "2024-02-01T00:00:00Z"
        },
        "features": ["multi_platform", "custom_overlays", "analytics"]
    }
    
    responses.add(
        "GET", "https://api.restream.io/v1/profile", json=profile_data, status=200
    )
    
    session = requests.Session()
    client = RestreamClient(session, token)
    result = client.get_profile()
    
    # Verify we get a Profile object
    assert isinstance(result, Profile)
    assert isinstance(result.user, User)
    
    # Verify user data
    assert result.user.id == "user_5f9a8b1234567890"
    assert result.user.username == "streamuser123"
    assert result.user.display_name == "John Streamer"
    assert result.user.email == "john@example.com"
    assert result.user.verified is True


@responses.activate  
def test_get_profile_minimal_response():
    """Test profile endpoint with minimal required fields."""
    token = "fake-token"
    profile_data = {
        "id": "user123",
        "username": "",
        "display_name": "Test User",
        "email": ""
    }
    
    responses.add(
        "GET", "https://api.restream.io/v1/profile", json=profile_data, status=200
    )
    
    session = requests.Session()
    client = RestreamClient(session, token)
    result = client.get_profile()
    
    # Verify we get a Profile object with defaults
    assert isinstance(result, Profile)
    assert result.user.id == "user123"
    assert result.user.display_name == "Test User"
    assert result.user.verified is False  # Default value
    assert result.subscription_plan is None  # Default value
