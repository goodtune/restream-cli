"""Strongly typed schemas for Restream.io API responses."""

from typing import List, Optional

import attrs


@attrs.define
class Profile:
    """User profile information from /profile endpoint."""

    id: int
    username: str
    email: str


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
