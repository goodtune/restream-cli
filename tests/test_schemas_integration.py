"""Integration tests for schemas with comprehensive API response examples."""
import json
from datetime import datetime, timezone

import pytest
import requests
import responses

from restream_io.api import RestreamClient
from restream_io.schemas import Channel, ChannelList, EventList, Profile, StreamEvent, User


class TestSchemaIntegration:
    """Test schemas against realistic API response payloads."""

    @responses.activate
    def test_comprehensive_profile_response(self):
        """Test profile endpoint with comprehensive response data."""
        # Example response payload mimicking real streaming platform APIs
        comprehensive_profile = {
            "id": "usr_5f9a8b1234567890abcdef12", 
            "username": "prstreamer2024",
            "display_name": "Pro Streamer",
            "email": "streamer@example.com",
            "avatar_url": "https://cdn.restream.io/avatars/usr_5f9a8b1234567890abcdef12.webp",
            "created_at": "2023-01-15T10:30:00.000Z",
            "verified": True,
            "subscription_plan": "professional",
            "streaming_quota": {
                "hours_used": 45.5,
                "hours_limit": 100,
                "reset_date": "2024-02-01T00:00:00Z",
                "overage_allowed": True
            },
            "features": [
                "multi_platform_streaming",
                "custom_overlays", 
                "advanced_analytics",
                "chat_integration",
                "stream_recording",
                "custom_rtmp"
            ]
        }
        
        responses.add(
            "GET", "https://api.restream.io/v1/profile", 
            json=comprehensive_profile, status=200
        )
        
        client = RestreamClient(requests.Session(), "test-token")
        result = client.get_profile()
        
        # Validate Profile object structure
        assert isinstance(result, Profile)
        assert isinstance(result.user, User)
        
        # Validate user fields
        assert result.user.id == "usr_5f9a8b1234567890abcdef12"
        assert result.user.username == "prstreamer2024"
        assert result.user.display_name == "Pro Streamer"
        assert result.user.email == "streamer@example.com"
        assert result.user.verified is True
        assert result.user.created_at == datetime(2023, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        
        # Validate profile-level fields
        assert result.subscription_plan == "professional"
        assert result.streaming_quota["hours_used"] == 45.5
        assert result.features == [
            "multi_platform_streaming", "custom_overlays", "advanced_analytics",
            "chat_integration", "stream_recording", "custom_rtmp"
        ]

    @responses.activate
    def test_comprehensive_channels_response(self):
        """Test channels endpoint with comprehensive channel data."""
        comprehensive_channels = [
            {
                "id": "ch_yt_UCabc123def456789012345",
                "name": "Gaming Adventures",
                "platform": "youtube",
                "enabled": True,
                "url": "https://youtube.com/channel/UCabc123def456789012345",
                "thumbnail_url": "https://yt3.ggpht.com/ytc/channel_avatar.jpg",
                "description": "Daily gaming content, tutorials, and live streams covering the latest games and gaming news.",
                "followers_count": 125840,
                "created_at": "2023-01-15T10:30:00Z",
                "updated_at": "2024-01-20T14:25:30Z"
            },
            {
                "id": "ch_tw_streamerpro2024",
                "name": "StreamerPro Live",
                "platform": "twitch",
                "enabled": True,
                "url": "https://twitch.tv/streamerpro2024",
                "thumbnail_url": "https://static-cdn.jtvnw.net/jtv_user_pictures/abc123.png",
                "description": "Variety streamer focusing on indie games, Just Chatting, and community events.",
                "followers_count": 34750,
                "created_at": "2023-03-20T16:45:00Z",
                "updated_at": "2024-01-18T09:12:45Z"
            },
            {
                "id": "ch_fb_creativestudios",
                "name": "Creative Studios Live",
                "platform": "facebook",
                "enabled": False,
                "url": "https://facebook.com/creativestudios",
                "thumbnail_url": "https://scontent.xx.fbcdn.net/v/profile_pic.jpg",
                "description": "Art, music production, and creative content streaming.",
                "followers_count": 8420,
                "created_at": "2023-06-10T12:00:00Z",
                "updated_at": "2023-12-15T18:30:00Z"
            }
        ]
        
        responses.add(
            "GET", "https://api.restream.io/v1/channels",
            json=comprehensive_channels, status=200
        )
        
        client = RestreamClient(requests.Session(), "test-token")
        result = client.list_channels()
        
        # Should return list of Channel objects
        assert isinstance(result, list)
        assert len(result) == 3
        assert all(isinstance(ch, Channel) for ch in result)
        
        # Validate YouTube channel
        yt_channel = result[0]
        assert yt_channel.id == "ch_yt_UCabc123def456789012345"
        assert yt_channel.name == "Gaming Adventures"
        assert yt_channel.platform == "youtube"
        assert yt_channel.enabled is True
        assert yt_channel.followers_count == 125840
        assert yt_channel.created_at == datetime(2023, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        
        # Validate disabled Facebook channel
        fb_channel = result[2]
        assert fb_channel.platform == "facebook"
        assert fb_channel.enabled is False

    @responses.activate
    def test_comprehensive_events_response(self):
        """Test events endpoint with comprehensive event data."""
        comprehensive_events = [
            {
                "id": "evt_live_20240120_gaming",
                "title": "Weekend Gaming Marathon - Part 2",
                "status": "live",
                "type": "gaming",
                "start_time": "2024-01-20T09:00:00.000Z",
                "duration": 14400,  # 4 hours
                "viewer_count": 342,
                "peak_viewers": 489,
                "created_at": "2024-01-20T08:45:00Z",
                "updated_at": "2024-01-20T13:15:30Z"
            },
            {
                "id": "evt_scheduled_20240127_tutorial",
                "title": "OBS Studio Advanced Setup Tutorial",
                "status": "scheduled",
                "type": "educational", 
                "start_time": "2024-01-27T20:00:00Z",
                "created_at": "2024-01-15T14:30:00Z",
                "updated_at": "2024-01-15T14:30:00Z"
            },
            {
                "id": "evt_ended_20240118_variety",
                "title": "Indie Game Showcase: Hidden Gems",
                "status": "ended",
                "type": "variety",
                "start_time": "2024-01-18T15:00:00Z",
                "end_time": "2024-01-18T18:30:00Z",
                "duration": 12600,  # 3.5 hours
                "viewer_count": 0,
                "peak_viewers": 156,
                "created_at": "2024-01-18T14:45:00Z",
                "updated_at": "2024-01-18T18:35:00Z"
            }
        ]
        
        responses.add(
            "GET", "https://api.restream.io/v1/events",
            json=comprehensive_events, status=200
        )
        
        client = RestreamClient(requests.Session(), "test-token")
        result = client.list_events()
        
        # Should return list of StreamEvent objects
        assert isinstance(result, list)
        assert len(result) == 3
        assert all(isinstance(event, StreamEvent) for event in result)
        
        # Validate live event
        live_event = result[0]
        assert live_event.id == "evt_live_20240120_gaming"
        assert live_event.title == "Weekend Gaming Marathon - Part 2"
        assert live_event.status == "live"
        assert live_event.type == "gaming"
        assert live_event.viewer_count == 342
        assert live_event.peak_viewers == 489
        assert live_event.duration == 14400
        assert live_event.start_time == datetime(2024, 1, 20, 9, 0, 0, tzinfo=timezone.utc)
        
        # Validate scheduled event (future)
        scheduled_event = result[1]
        assert scheduled_event.status == "scheduled"
        assert scheduled_event.end_time is None
        assert scheduled_event.viewer_count is None
        
        # Validate ended event
        ended_event = result[2]
        assert ended_event.status == "ended"
        assert ended_event.end_time == datetime(2024, 1, 18, 18, 30, 0, tzinfo=timezone.utc)
        assert ended_event.viewer_count == 0  # Stream ended

    @responses.activate
    def test_paginated_channels_response(self):
        """Test channels endpoint with paginated response structure."""
        paginated_response = {
            "channels": [
                {
                    "id": "ch_yt_sample123",
                    "name": "Sample Channel",
                    "platform": "youtube", 
                    "enabled": True,
                    "followers_count": 1500
                }
            ],
            "total": 15,
            "page": 1,
            "per_page": 10,
            "has_more": True
        }
        
        responses.add(
            "GET", "https://api.restream.io/v1/channels",
            json=paginated_response, status=200
        )
        
        client = RestreamClient(requests.Session(), "test-token")
        result = client.list_channels()
        
        # Should return ChannelList object
        assert isinstance(result, ChannelList)
        assert result.total == 15
        assert len(result.channels) == 1
        assert isinstance(result.channels[0], Channel)
        assert result.channels[0].platform == "youtube"

    @responses.activate
    def test_paginated_events_response(self):
        """Test events endpoint with paginated response structure."""
        paginated_response = {
            "events": [
                {
                    "id": "evt_sample_123",
                    "title": "Sample Event",
                    "status": "ended",
                    "type": "entertainment",
                    "peak_viewers": 89
                }
            ],
            "total": 47,
            "page": 2,
            "per_page": 20
        }
        
        responses.add(
            "GET", "https://api.restream.io/v1/events",
            json=paginated_response, status=200
        )
        
        client = RestreamClient(requests.Session(), "test-token")
        result = client.list_events()
        
        # Should return EventList object
        assert isinstance(result, EventList)
        assert result.total == 47
        assert result.page == 2
        assert result.per_page == 20
        assert len(result.events) == 1
        assert isinstance(result.events[0], StreamEvent)

    def test_datetime_parsing_edge_cases(self):
        """Test datetime parsing with various ISO format variations."""
        client = RestreamClient(requests.Session(), "test-token")
        
        # Test various datetime formats
        test_cases = [
            ("2024-01-20T09:00:00Z", datetime(2024, 1, 20, 9, 0, 0, tzinfo=timezone.utc)),
            ("2024-01-20T09:00:00.000Z", datetime(2024, 1, 20, 9, 0, 0, tzinfo=timezone.utc)),
            ("2024-01-20T09:00:00+00:00", datetime(2024, 1, 20, 9, 0, 0, tzinfo=timezone.utc)),
            (None, None),
            ("", None),
            ("invalid", None)
        ]
        
        for dt_str, expected in test_cases:
            result = client._parse_datetime(dt_str)
            if expected is None:
                assert result is None
            else:
                assert result == expected