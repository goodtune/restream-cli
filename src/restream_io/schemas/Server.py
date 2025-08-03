"""Server schema."""

import attrs


@attrs.define
class Server:
    """Ingest server information from /server/all endpoint."""

    id: int
    name: str
    url: str
    rtmpUrl: str
    latitude: str
    longitude: str

    def __str__(self) -> str:
        """Format server for human-readable output."""
        return (
            f"Server: {self.name}\n"
            f"  ID: {self.id}\n"
            f"  URL: {self.url}\n"
            f"  RTMP URL: {self.rtmpUrl}\n"
            f"  Location: {self.latitude}, {self.longitude}"
        )
