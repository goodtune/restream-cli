"""Stream key schema."""

from typing import Optional

import attrs


@attrs.define
class StreamKey:
    """Stream key information."""

    streamKey: str
    srtUrl: Optional[str]

    def __str__(self) -> str:
        """Format stream key for human-readable output."""
        result = f"Stream Key: {self.streamKey}"

        if self.srtUrl:
            result += f"\nSRT URL: {self.srtUrl}"

        return result
