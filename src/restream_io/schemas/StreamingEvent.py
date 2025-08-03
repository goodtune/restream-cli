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
        # Extract metrics if present
        metrics = None
        if "metrics" in data:
            metrics_data = data["metrics"]
            metrics = StreamingMetrics(
                bitrate=metrics_data.get("bitrate"),
                fps=metrics_data.get("fps"),
                resolution=metrics_data.get("resolution"),
                dropped_frames=metrics_data.get("dropped_frames"),
                encoding_time=metrics_data.get("encoding_time"),
            )
        
        return cls(
            event_type=data.get("type", "unknown"),
            timestamp=data.get("timestamp", ""),
            channel_id=data.get("channel_id"),
            event_id=data.get("event_id"),
            metrics=metrics,
            status=data.get("status"),
            platform=data.get("platform"),
            message=data.get("message"),
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