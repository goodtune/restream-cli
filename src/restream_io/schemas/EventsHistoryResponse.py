"""Events history response schema."""

from typing import List

import attrs

from .EventsPagination import EventsPagination
from .StreamEvent import StreamEvent


@attrs.define
class EventsHistoryResponse:
    """Response from events history endpoint."""

    items: List[StreamEvent]
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
