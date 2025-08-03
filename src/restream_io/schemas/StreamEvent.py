"""Stream event schema."""

from typing import List, Optional

import attrs

from .EventDestination import EventDestination


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
