"""Channel summary schema."""

import attrs


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
