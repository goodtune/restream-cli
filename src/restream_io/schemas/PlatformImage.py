"""Platform image schema."""

import attrs


@attrs.define
class PlatformImage:
    """Platform image URLs."""

    png: str
    svg: str

    def __str__(self) -> str:
        """Format platform image for human-readable output."""
        return f"PNG: {self.png}, SVG: {self.svg}"
