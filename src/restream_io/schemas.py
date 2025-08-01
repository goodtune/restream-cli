"""Strongly typed schemas for Restream.io API responses."""
from datetime import datetime
from typing import List, Optional

import attrs


@attrs.define
class User:
    """User profile information."""
    id: str
    username: str
    display_name: str
    email: str
    avatar_url: Optional[str] = None
    created_at: Optional[datetime] = None
    verified: bool = False


@attrs.define  
class Channel:
    """Restream channel information."""
    id: str
    name: str
    platform: str
    enabled: bool
    url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    description: Optional[str] = None
    followers_count: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@attrs.define
class ChannelList:
    """List of channels response."""
    channels: List[Channel]
    total: int = 0


@attrs.define
class StreamEvent:
    """Stream event information."""
    id: str
    title: str
    status: str
    type: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    viewer_count: Optional[int] = None
    peak_viewers: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@attrs.define
class EventList:
    """List of events response."""
    events: List[StreamEvent]
    total: int = 0
    page: int = 1
    per_page: int = 20


@attrs.define
class Profile:
    """User profile response."""
    user: User
    subscription_plan: Optional[str] = None
    streaming_quota: Optional[dict] = None
    features: Optional[List[str]] = None