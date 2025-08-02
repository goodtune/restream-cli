"""Strongly typed schemas for Restream.io API responses."""

from typing import List, Optional

import attrs


@attrs.define
class Profile:
    """User profile information from /profile endpoint."""

    id: int
    username: str
    email: str

    def __str__(self) -> str:
        """Format profile for human-readable output."""
        return (
            f"Profile Information:\n"
            f"  ID: {self.id}\n"
            f"  Username: {self.username}\n"
            f"  Email: {self.email}"
        )


@attrs.define
class ChannelSummary:
    """
    Channel summary information from /user/channel/all endpoint.

    This represents the simplified channel data returned when listing all
    channels.
    """

    id: int
    streamingPlatformId: int
    embedUrl: str
    url: str
    identifier: str
    displayName: str
    enabled: bool


@attrs.define
class Channel:
    """
    Detailed channel information from /user/channel/{id} endpoint.

    This represents the full channel data returned when requesting a specific
    channel. The response structure differs significantly from the list endpoint.
    """

    id: int
    user_id: int
    service_id: int
    channel_identifier: str
    channel_url: str
    event_identifier: Optional[str]
    event_url: Optional[str]
    embed: str
    active: bool
    display_name: str

    def __str__(self) -> str:
        """Format channel for human-readable output."""
        status = "Active" if self.active else "Inactive"
        result = (
            f"Channel Information:\n"
            f"  ID: {self.id}\n"
            f"  Display Name: {self.display_name}\n"
            f"  Status: {status}\n"
            f"  Channel URL: {self.channel_url}\n"
            f"  Channel Identifier: {self.channel_identifier}\n"
            f"  Service ID: {self.service_id}\n"
            f"  User ID: {self.user_id}"
        )
        
        if self.event_identifier:
            result += f"\n  Event Identifier: {self.event_identifier}"
        
        if self.event_url:
            result += f"\n  Event URL: {self.event_url}"
            
        return result


@attrs.define
class EventDestination:
    """Event destination information."""

    channelId: int
    externalUrl: Optional[str]
    streamingPlatformId: int


@attrs.define
class EventsPagination:
    """Pagination information for events history."""

    pages_total: int
    page: int
    limit: int


@attrs.define
class EventsHistoryResponse:
    """Response from events history endpoint."""

    items: List["StreamEvent"]
    pagination: EventsPagination


@attrs.define
class StreamEvent:
    """Stream event information."""

    id: str
    showId: Optional[str]
    status: str
    title: str
    description: str
    isInstant: bool
    isRecordOnly: bool
    coverUrl: Optional[str]
    scheduledFor: Optional[int]  # timestamp in seconds or NULL
    startedAt: Optional[int]  # timestamp in seconds or NULL
    finishedAt: Optional[int]  # timestamp in seconds or NULL
    destinations: List[EventDestination]
