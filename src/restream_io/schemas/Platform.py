"""Platform schema."""

import attrs

from .PlatformImage import PlatformImage


@attrs.define
class Platform:
    """Streaming platform information from /platform/all endpoint."""

    id: int
    name: str
    url: str
    image: PlatformImage
    altImage: PlatformImage

    def __str__(self) -> str:
        """Format platform for human-readable output."""
        return (
            f"Platform: {self.name}\n"
            f"  ID: {self.id}\n"
            f"  URL: {self.url}\n"
            f"  Image: {self.image}\n"
            f"  Alt Image: {self.altImage}"
        )
