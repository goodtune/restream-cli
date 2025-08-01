"""Integration tests for schemas with comprehensive API response examples."""
import json

import pytest
import requests
import responses

from restream_io.api import RestreamClient
from restream_io.schemas import Channel, EventDestination, Profile, StreamEvent


class TestSchemaIntegration:
    """Test schemas against realistic API response payloads."""

    @responses.activate
    def test_profile_response_from_docs(self):
        """Test profile endpoint with exact response from API documentation."""
        # Exact response from API documentation
        profile_response = {
            "id": 000,
            "username": "xxx", 
            "email": "xxx"
        }
        
        responses.add(
            "GET", "https://api.restream.io/v1/profile", 
            json=profile_response, status=200
        )
        
        client = RestreamClient(requests.Session(), "test-token")
        result = client.get_profile()
        
        # Validate Profile object structure
        assert isinstance(result, Profile)
        assert result.id == 000
        assert result.username == "xxx"
        assert result.email == "xxx"

    @responses.activate
    def test_realistic_profile_response(self):
        """Test profile endpoint with realistic values."""
        profile_response = {
            "id": 123456,
            "username": "gamer_streamer",
            "email": "streamer@example.com"
        }
        
        responses.add(
            "GET", "https://api.restream.io/v1/profile", 
            json=profile_response, status=200
        )
        
        client = RestreamClient(requests.Session(), "test-token")
        result = client.get_profile()
        
        assert isinstance(result, Profile)
        assert result.id == 123456
        assert result.username == "gamer_streamer"
        assert result.email == "streamer@example.com"

    @responses.activate
    def test_channels_response_from_docs(self):
        """Test channels endpoint with exact response from API documentation."""
        # Exact response from API documentation
        channels_response = [
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
            "GET", "https://api.restream.io/v1/channels",
            json=channels_response, status=200
        )
        
        client = RestreamClient(requests.Session(), "test-token")
        result = client.list_channels()
        
        # Should return list of Channel objects
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(ch, Channel) for ch in result)
        
        # Validate first channel
        channel_0 = result[0]
        assert channel_0.id == 000
        assert channel_0.streamingPlatformId == 000
        assert channel_0.embedUrl == "https://beam.pro/embed/player/xxx"
        assert channel_0.url == "https://beam.pro/xxx"
        assert channel_0.identifier == "xxx"
        assert channel_0.displayName == "xxx"
        assert channel_0.active is True
        
        # Validate second channel
        channel_1 = result[1]
        assert channel_1.id == 111
        assert channel_1.active is False

    @responses.activate
    def test_realistic_channels_response(self):
        """Test channels endpoint with realistic values."""
        channels_response = [
            {
                "id": 1001,
                "streamingPlatformId": 1,
                "embedUrl": "https://www.youtube.com/embed/live_stream?channel=UCabc123",
                "url": "https://youtube.com/channel/UCabc123",
                "identifier": "UCabc123",
                "displayName": "Gaming Adventures",
                "active": True
            },
            {
                "id": 1002,
                "streamingPlatformId": 2,
                "embedUrl": "https://player.twitch.tv/?channel=streamerpro",
                "url": "https://twitch.tv/streamerpro",
                "identifier": "streamerpro", 
                "displayName": "StreamerPro Live",
                "active": True
            }
        ]
        
        responses.add(
            "GET", "https://api.restream.io/v1/channels",
            json=channels_response, status=200
        )
        
        client = RestreamClient(requests.Session(), "test-token")
        result = client.list_channels()
        
        assert isinstance(result, list)
        assert len(result) == 2
        
        # Validate YouTube channel
        yt_channel = result[0]
        assert yt_channel.id == 1001
        assert yt_channel.streamingPlatformId == 1
        assert yt_channel.displayName == "Gaming Adventures"
        assert yt_channel.active is True
        
        # Validate Twitch channel
        twitch_channel = result[1]
        assert twitch_channel.id == 1002
        assert twitch_channel.streamingPlatformId == 2
        assert twitch_channel.displayName == "StreamerPro Live"

    @responses.activate
    def test_events_response_from_docs(self):
        """Test events endpoint with exact response from API documentation."""
        # Exact response from API documentation
        events_response = [
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
            "GET", "https://api.restream.io/v1/events",
            json=events_response, status=200
        )
        
        client = RestreamClient(requests.Session(), "test-token")
        result = client.list_events()
        
        # Should return list of StreamEvent objects
        assert isinstance(result, list)
        assert len(result) == 1
        assert all(isinstance(event, StreamEvent) for event in result)
        
        # Validate event
        event = result[0]
        assert event.id == "2527849f-f961-4b1d-8ae0-8eae4f068327"
        assert event.status == "upcoming"
        assert event.title == "Event title"
        assert event.description == "Event description"
        assert event.coverUrl == "URL or null"
        assert event.scheduledFor == 1599983310
        assert event.startedAt is None
        assert event.finishedAt is None
        
        # Validate destination
        assert len(event.destinations) == 1
        destination = event.destinations[0]
        assert isinstance(destination, EventDestination)
        assert destination.channelId == 1
        assert destination.externalUrl == "URL or null"
        assert destination.streamingPlatformId == 5

    @responses.activate
    def test_realistic_events_response(self):
        """Test events endpoint with realistic values."""
        events_response = [
            {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "status": "live",
                "title": "Gaming Stream - Elden Ring Boss Fight",
                "description": "Taking on the hardest bosses in Elden Ring",
                "coverUrl": "https://cdn.restream.io/covers/event123.jpg",
                "scheduledFor": 1640995200,
                "startedAt": 1640995320,
                "finishedAt": None,
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
                "title": "Tutorial: Setting up OBS for streaming",
                "description": "Complete guide to OBS configuration",
                "coverUrl": None,
                "scheduledFor": 1640908800,
                "startedAt": 1640908900,
                "finishedAt": 1640912500,
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
            "GET", "https://api.restream.io/v1/events",
            json=events_response, status=200
        )
        
        client = RestreamClient(requests.Session(), "test-token")
        result = client.list_events()
        
        assert isinstance(result, list)
        assert len(result) == 2
        
        # Validate live event
        live_event = result[0]
        assert live_event.id == "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        assert live_event.status == "live"
        assert live_event.title == "Gaming Stream - Elden Ring Boss Fight"
        assert live_event.startedAt == 1640995320
        assert live_event.finishedAt is None
        assert len(live_event.destinations) == 2
        
        # Validate ended event
        ended_event = result[1]
        assert ended_event.status == "ended"
        assert ended_event.title == "Tutorial: Setting up OBS for streaming"
        assert ended_event.coverUrl is None
        assert ended_event.finishedAt == 1640912500
        assert len(ended_event.destinations) == 1

    @responses.activate
    def test_get_single_channel_from_docs(self):
        """Test get channel endpoint with exact response from API documentation."""
        # Using the same format as the channels list response
        channel_response = {
            "id": 123456,
            "streamingPlatformId": 000,
            "embedUrl": "https://beam.pro/embed/player/xxx",
            "url": "https://beam.pro/xxx",
            "identifier": "xxx",
            "displayName": "xxx",
            "active": True
        }
        
        responses.add(
            "GET", "https://api.restream.io/v1/channels/123456",
            json=channel_response, status=200
        )
        
        client = RestreamClient(requests.Session(), "test-token")
        result = client.get_channel("123456")
        
        assert isinstance(result, Channel)
        assert result.id == 123456
        assert result.streamingPlatformId == 000
        assert result.embedUrl == "https://beam.pro/embed/player/xxx"
        assert result.url == "https://beam.pro/xxx"
        assert result.identifier == "xxx"
        assert result.displayName == "xxx"
        assert result.active is True