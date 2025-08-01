"""Tests for schema deserialization and validation."""

import pytest

from restream_io.schemas import Channel, ChannelSummary


class TestChannelSchemas:
    """Test Channel and ChannelSummary schema deserialization."""

    def test_channel_summary_deserialization(self):
        """Test ChannelSummary deserialization from /user/channel/all."""
        # Data structure from /user/channel/all endpoint
        channel_data = {
            "id": 12345,
            "streamingPlatformId": 1,
            "embedUrl": "https://youtube.com/embed/xyz",
            "url": "https://youtube.com/channel/xyz",
            "identifier": "channel_identifier",
            "displayName": "My Gaming Channel",
            "enabled": True,
        }

        channel = ChannelSummary(**channel_data)

        assert channel.id == 12345
        assert channel.streamingPlatformId == 1
        assert channel.embedUrl == "https://youtube.com/embed/xyz"
        assert channel.url == "https://youtube.com/channel/xyz"
        assert channel.identifier == "channel_identifier"
        assert channel.displayName == "My Gaming Channel"
        assert channel.enabled is True

    def test_channel_summary_inactive(self):
        """Test ChannelSummary with inactive channel."""
        channel_data = {
            "id": 67890,
            "streamingPlatformId": 2,
            "embedUrl": "https://twitch.tv/embed/xyz",
            "url": "https://twitch.tv/xyz",
            "identifier": "twitch_user",
            "displayName": "Twitch Stream",
            "enabled": False,
        }

        channel = ChannelSummary(**channel_data)

        assert channel.id == 67890
        assert channel.enabled is False

    def test_channel_deserialization(self):
        """Test Channel deserialization from /user/channel/{id} response."""
        # Data structure from /user/channel/{id} endpoint
        channel_data = {
            "id": 12345,
            "user_id": 674443,
            "service_id": 1,
            "channel_identifier": "channel_identifier",
            "channel_url": "https://youtube.com/channel/xyz",
            "event_identifier": None,
            "event_url": None,
            "embed": "https://youtube.com/embed/xyz",
            "active": True,
            "display_name": "My Gaming Channel",
        }

        channel = Channel(**channel_data)

        assert channel.id == 12345
        assert channel.user_id == 674443
        assert channel.service_id == 1
        assert channel.channel_identifier == "channel_identifier"
        assert channel.channel_url == "https://youtube.com/channel/xyz"
        assert channel.event_identifier is None
        assert channel.event_url is None
        assert channel.embed == "https://youtube.com/embed/xyz"
        assert channel.active is True
        assert channel.display_name == "My Gaming Channel"

    def test_channel_disabled(self):
        """Test Channel with disabled channel."""
        channel_data = {
            "id": 67890,
            "user_id": 674443,
            "service_id": 2,
            "channel_identifier": "twitch_user",
            "channel_url": "https://twitch.tv/xyz",
            "event_identifier": None,
            "event_url": None,
            "embed": "https://twitch.tv/embed/xyz",
            "active": False,
            "display_name": "Twitch Stream",
        }

        channel = Channel(**channel_data)

        assert channel.id == 67890
        assert channel.active is False

    def test_schema_differences(self):
        """Test that the schemas have different structures and field names."""
        # ChannelSummary uses 'enabled' and has different fields
        summary_data = {
            "id": 1,
            "streamingPlatformId": 1,
            "embedUrl": "test",
            "url": "test",
            "identifier": "test",
            "displayName": "test",
            "enabled": True,
        }

        # Channel uses 'active' and has completely different fields
        detailed_data = {
            "id": 1,
            "user_id": 674443,
            "service_id": 1,
            "channel_identifier": "test",
            "channel_url": "test",
            "event_identifier": None,
            "event_url": None,
            "embed": "test",
            "active": True,
            "display_name": "test",
        }

        summary = ChannelSummary(**summary_data)
        detailed = Channel(**detailed_data)

        # ChannelSummary uses enabled, Channel uses active
        assert hasattr(summary, "enabled")
        assert not hasattr(summary, "active")
        assert hasattr(detailed, "active")
        assert not hasattr(detailed, "enabled")

        assert summary.enabled is True
        assert detailed.active is True

    def test_channel_summary_missing_enabled_field(self):
        """Test that ChannelSummary requires 'enabled' field."""
        channel_data = {
            "id": 1,
            "streamingPlatformId": 1,
            "embedUrl": "test",
            "url": "test",
            "identifier": "test",
            "displayName": "test",
            # Missing 'enabled' field
        }

        with pytest.raises(TypeError, match="missing.*required.*enabled"):
            ChannelSummary(**channel_data)

    def test_channel_missing_active_field(self):
        """Test that Channel requires 'active' field."""
        channel_data = {
            "id": 1,
            "user_id": 674443,
            "service_id": 1,
            "channel_identifier": "test",
            "channel_url": "test",
            "event_identifier": None,
            "event_url": None,
            "embed": "test",
            "display_name": "test",
            # Missing 'active' field
        }

        with pytest.raises(TypeError, match="missing.*required.*active"):
            Channel(**channel_data)
