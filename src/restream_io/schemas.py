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
class Channel:
    """Restream channel information."""
    id: int
    streamingPlatformId: int
    embedUrl: str
    url: str
    identifier: str
    displayName: str
    active: bool


@attrs.define
class EventDestination:
    """Event destination information."""
    channelId: int
    externalUrl: Optional[str]
    streamingPlatformId: int


@attrs.define
class StreamEvent:
    """Stream event information."""
    id: str
    status: str
    title: str
    description: str
    coverUrl: Optional[str]
    scheduledFor: Optional[int]  # timestamp in seconds or NULL
    startedAt: Optional[int]     # timestamp in seconds or NULL
    finishedAt: Optional[int]    # timestamp in seconds or NULL
    destinations: List[EventDestination]