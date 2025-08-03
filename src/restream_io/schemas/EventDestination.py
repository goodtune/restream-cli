"""Event destination schema."""

from typing import Optional

import attrs


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
