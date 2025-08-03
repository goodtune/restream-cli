"""Channel detailed information schema."""

from typing import Optional

import attrs


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
