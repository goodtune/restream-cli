"""Channel metadata schema."""

import attrs


@attrs.define
class ChannelMeta:
    """Channel metadata from /user/channel-meta/{id} endpoint."""

    title: str
    description: str

    def __str__(self) -> str:
        """Format channel metadata for human-readable output."""
        return (
            f"Channel Metadata:\n"
            f"  Title: {self.title}\n"
            f"  Description: {self.description}"
        )
