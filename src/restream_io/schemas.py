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

    def __str__(self) -> str:
        """Format channel summary for human-readable output."""
        status = "Enabled" if self.enabled else "Disabled"
        return (
            f"Channel Summary:"
            f"\n  ID: {self.id}"
            f"\n  Display Name: {self.displayName}"
            f"\n  Status: {status}"
            f"\n  Platform ID: {self.streamingPlatformId}"
            f"\n  Identifier: {self.identifier}"
            f"\n  URL: {self.url}"
        )


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

    def __str__(self) -> str:
        """Format event destination for human-readable output."""
        result = (
            f"Destination:"
            f"\n    Channel ID: {self.channelId}"
            f"\n    Platform ID: {self.streamingPlatformId}"
        )
        if self.externalUrl:
            result += f"\n    External URL: {self.externalUrl}"
        return result


@attrs.define
class EventsPagination:
    """Pagination information for events history."""

    pages_total: int
    page: int
    limit: int

    def __str__(self) -> str:
        """Format pagination for human-readable output."""
        return (
            f"Page {self.page} of {self.pages_total} "
            f"(showing up to {self.limit} items per page)"
        )


@attrs.define
class EventsHistoryResponse:
    """Response from events history endpoint."""

    items: List["StreamEvent"]
    pagination: EventsPagination

    def __str__(self) -> str:
        """Format events history response for human-readable output."""
        result = f"Events History ({len(self.items)} events):\n"
        result += f"{self.pagination}\n\n"

        for i, event in enumerate(self.items, 1):
            result += f"{i}. {event}\n"
            if i < len(self.items):
                result += "\n"

        return result.rstrip()


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

    def __str__(self) -> str:
        """Format stream event for human-readable output."""
        from datetime import datetime

        result = (
            f"Event: {self.title}\n"
            f"  ID: {self.id}\n"
            f"  Status: {self.status}\n"
            f"  Description: {self.description}\n"
            f"  Instant: {'Yes' if self.isInstant else 'No'}\n"
            f"  Record Only: {'Yes' if self.isRecordOnly else 'No'}"
        )

        if self.showId:
            result += f"\n  Show ID: {self.showId}"

        if self.scheduledFor:
            scheduled_time = datetime.utcfromtimestamp(self.scheduledFor)
            result += f"\n  Scheduled: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}"

        if self.startedAt:
            started_time = datetime.utcfromtimestamp(self.startedAt)
            result += f"\n  Started: {started_time.strftime('%Y-%m-%d %H:%M:%S')}"

        if self.finishedAt:
            finished_time = datetime.utcfromtimestamp(self.finishedAt)
            result += f"\n  Finished: {finished_time.strftime('%Y-%m-%d %H:%M:%S')}"

        if self.coverUrl:
            result += f"\n  Cover URL: {self.coverUrl}"

        # Always show destinations section, even if empty
        result += f"\n  Destinations ({len(self.destinations)}):"
        for dest in self.destinations:
            dest_str = str(dest).replace("\n", "\n  ")
            result += f"\n  {dest_str}"

        return result
