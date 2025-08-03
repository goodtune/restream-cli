"""Schema for streaming event data from WebSocket API."""

from typing import Any, Dict, Optional

import attrs


@attrs.define
class StreamingMetrics:
    """Streaming metrics data."""

    bitrate: Optional[int] = None
    fps: Optional[float] = None
    resolution: Optional[str] = None
    dropped_frames: Optional[int] = None
    encoding_time: Optional[float] = None

    def __str__(self) -> str:
        """Human-readable representation."""
        parts = []
        if self.bitrate is not None:
            parts.append(f"Bitrate: {self.bitrate} kbps")
        if self.fps is not None:
            parts.append(f"FPS: {self.fps}")
        if self.resolution:
            parts.append(f"Resolution: {self.resolution}")
        if self.dropped_frames is not None:
            parts.append(f"Dropped frames: {self.dropped_frames}")
        if self.encoding_time is not None:
            parts.append(f"Encoding time: {self.encoding_time}ms")
        return " | ".join(parts) if parts else "No metrics available"


@attrs.define
class StreamingEvent:
    """Real-time streaming event from WebSocket."""

    event_type: str
    timestamp: str
    channel_id: Optional[str] = None
    event_id: Optional[str] = None
    metrics: Optional[StreamingMetrics] = None
    status: Optional[str] = None
    platform: Optional[str] = None
    message: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_websocket_message(cls, data: Dict[str, Any]) -> "StreamingEvent":
        """Create StreamingEvent from WebSocket message data.

        Args:
            data: Raw message data from WebSocket

        Returns:
            StreamingEvent instance
        """
        # Extract metrics if present - different structure based on action type
        metrics = None
        if "streaming" in data:
            streaming_data = data["streaming"]

            # Handle different streaming data structures based on action
            if data.get("action") == "updateIncoming":
                # For incoming streams, we have detailed streaming metrics
                bitrate_data = streaming_data.get("bitrate", {})
                total_bitrate = (
                    bitrate_data.get("total", 0)
                    if isinstance(bitrate_data, dict)
                    else streaming_data.get("bitrate", 0)
                )

                metrics = StreamingMetrics(
                    bitrate=total_bitrate,
                    fps=streaming_data.get("fps"),
                    resolution=f"{streaming_data.get('width', 0)}x{streaming_data.get('height', 0)}",
                    dropped_frames=None,  # Not provided in this format
                    encoding_time=None,  # Not provided in this format
                )
            else:
                # For outgoing streams, simpler metrics
                metrics = StreamingMetrics(
                    bitrate=streaming_data.get("bitrate", 0),
                    fps=None,
                    resolution=None,
                    dropped_frames=None,
                    encoding_time=None,
                )

        return cls(
            event_type=data.get("action", "unknown"),
            timestamp=str(data.get("createdAt", "")),
            channel_id=str(data.get("channelId")) if data.get("channelId") else None,
            event_id=data.get("eventIdentifier"),
            metrics=metrics,
            status=(
                data.get("streaming", {}).get("status") if "streaming" in data else None
            ),
            platform=str(data.get("platformId")) if data.get("platformId") else None,
            message=None,  # Not in the official schema
            raw_data=data,
        )

    def __str__(self) -> str:
        """Human-readable representation."""
        parts = [f"[{self.timestamp}] {self.event_type.upper()}"]

        if self.channel_id:
            parts.append(f"Channel: {self.channel_id}")
        if self.event_id:
            parts.append(f"Event: {self.event_id}")
        if self.platform:
            parts.append(f"Platform: {self.platform}")
        if self.status:
            parts.append(f"Status: {self.status}")
        if self.message:
            parts.append(f"Message: {self.message}")

        result = " | ".join(parts)

        if self.metrics:
            result += f"\n  Metrics: {self.metrics}"

        return result
