"""Schema for chat event data from WebSocket API."""

from typing import Any, Dict, Optional

import attrs


@attrs.define
class ChatUser:
    """Chat user information."""

    id: Optional[str] = None
    username: Optional[str] = None
    display_name: Optional[str] = None
    platform: Optional[str] = None
    is_moderator: Optional[bool] = None
    is_subscriber: Optional[bool] = None
    badges: Optional[list] = None

    def __str__(self) -> str:
        """Human-readable representation."""
        name = self.display_name or self.username or self.id or "Unknown"
        badges_str = ""
        if self.badges:
            badges_str = f" [{', '.join(self.badges)}]"
        platform_str = f" ({self.platform})" if self.platform else ""
        return f"{name}{badges_str}{platform_str}"


@attrs.define
class ChatMessage:
    """Chat message content."""

    text: Optional[str] = None
    emotes: Optional[list] = None
    mentions: Optional[list] = None

    def __str__(self) -> str:
        """Human-readable representation."""
        return self.text or ""


@attrs.define
class ChatEvent:
    """Real-time chat event from WebSocket."""

    event_type: str
    timestamp: str
    channel_id: Optional[str] = None
    user: Optional[ChatUser] = None
    message: Optional[ChatMessage] = None
    platform: Optional[str] = None
    event_id: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None

    @classmethod
    def from_websocket_message(cls, data: Dict[str, Any]) -> "ChatEvent":
        """Create ChatEvent from WebSocket message data.

        Args:
            data: Raw message data from WebSocket

        Returns:
            ChatEvent instance
        """
        # Extract user information if present
        user = None
        if "user" in data:
            user_data = data["user"]
            user = ChatUser(
                id=user_data.get("id"),
                username=user_data.get("username"),
                display_name=user_data.get("display_name"),
                platform=user_data.get("platform"),
                is_moderator=user_data.get("is_moderator"),
                is_subscriber=user_data.get("is_subscriber"),
                badges=user_data.get("badges", []),
            )

        # Extract message content if present
        message = None
        if "message" in data:
            message_data = data["message"]
            if isinstance(message_data, str):
                message = ChatMessage(text=message_data)
            elif isinstance(message_data, dict):
                message = ChatMessage(
                    text=message_data.get("text"),
                    emotes=message_data.get("emotes", []),
                    mentions=message_data.get("mentions", []),
                )

        return cls(
            event_type=data.get("type", "unknown"),
            timestamp=data.get("timestamp", ""),
            channel_id=data.get("channel_id"),
            user=user,
            message=message,
            platform=data.get("platform"),
            event_id=data.get("event_id"),
            raw_data=data,
        )

    def __str__(self) -> str:
        """Human-readable representation."""
        timestamp_part = f"[{self.timestamp}]"
        event_part = f"{self.event_type.upper()}"

        if self.event_type == "message" and self.user and self.message:
            # Format as chat message
            return f"{timestamp_part} {self.user}: {self.message}"
        elif self.event_type == "join" and self.user:
            # Format as user join
            return f"{timestamp_part} {event_part}: {self.user} joined"
        elif self.event_type == "leave" and self.user:
            # Format as user leave
            return f"{timestamp_part} {event_part}: {self.user} left"
        else:
            # Generic format
            parts = [timestamp_part, event_part]
            if self.channel_id:
                parts.append(f"Channel: {self.channel_id}")
            if self.platform:
                parts.append(f"Platform: {self.platform}")
            if self.user:
                parts.append(f"User: {self.user}")
            if self.message:
                parts.append(f"Message: {self.message}")
            return " | ".join(parts)
