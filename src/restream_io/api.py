import time
from datetime import datetime
from typing import List, Optional, Union

import requests

from .config import load_tokens, save_tokens
from .errors import APIError, AuthenticationError
from .schemas import Channel, ChannelList, EventList, Profile, StreamEvent, User
from .utils import retry_on_transient_error

BASE_URL = "https://api.restream.io/v1"  # placeholder; confirm from docs


class RestreamClient:
    def __init__(self, session: requests.Session, token: str):
        self.session = session
        self.token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    @classmethod
    def from_config(cls, session: Optional[requests.Session] = None) -> "RestreamClient":
        """Create a RestreamClient instance using tokens from config.
        
        Args:
            session: Optional requests session. If not provided, creates a new one.
            
        Returns:
            RestreamClient instance
            
        Raises:
            AuthenticationError: If no valid tokens are available
        """
        if session is None:
            session = requests.Session()
            
        tokens = load_tokens()
        if not tokens:
            raise AuthenticationError("No stored tokens found. Please run 'restream.io login' first.")
        
        access_token = tokens.get("access_token")
        if not access_token:
            raise AuthenticationError("No access token found in stored tokens.")
        
        # Check if token is expired and refresh if needed
        expires_at = tokens.get("expires_at")
        if expires_at and time.time() >= expires_at:
            refresh_token = tokens.get("refresh_token")
            if refresh_token:
                access_token = cls._refresh_token(refresh_token)
            else:
                raise AuthenticationError("Access token expired and no refresh token available. Please re-login.")
        
        return cls(session, access_token)
    
    @staticmethod
    def _refresh_token(refresh_token: str) -> str:
        """Refresh access token using refresh token.
        
        Args:
            refresh_token: The refresh token
            
        Returns:
            New access token
            
        Raises:
            AuthenticationError: If token refresh fails
        """
        from .config import get_client_id, get_client_secret
        
        client_id = get_client_id()
        client_secret = get_client_secret()
        
        if not client_id:
            raise AuthenticationError("RESTREAM_CLIENT_ID environment variable not set")
        
        token_data = {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "refresh_token": refresh_token,
        }
        
        if client_secret:
            token_data["client_secret"] = client_secret
        
        token_url = "https://api.restream.io/oauth/token"
        
        try:
            response = requests.post(
                token_url,
                data=token_data,
                headers={"Accept": "application/json"},
                timeout=30,
            )
            
            if not response.ok:
                raise AuthenticationError(f"Token refresh failed: {response.status_code}")
            
            token_response = response.json()
            
            # Save the new tokens
            save_tokens(token_response)
            
            return token_response["access_token"]
            
        except requests.RequestException as e:
            raise AuthenticationError(f"Network error during token refresh: {e}")

    def _make_request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make an HTTP request to the API with error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            JSON response data
            
        Raises:
            APIError: If the request fails
        """
        url = f"{BASE_URL}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            if not response.ok:
                # Try to get error details from response
                try:
                    error_data = response.json()
                    error_message = error_data.get("message", error_data.get("error", "API request failed"))
                except (ValueError, KeyError):
                    error_message = f"API request failed"
                
                raise APIError(
                    message=error_message,
                    status_code=response.status_code,
                    response_text=response.text,
                    url=url
                )
            
            return response.json()
            
        except requests.RequestException as e:
            raise APIError(f"Network error: {e}", url=url)

    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string from API response.
        
        Args:
            dt_str: ISO format datetime string
            
        Returns:
            Parsed datetime object or None
        """
        if not dt_str:
            return None
        try:
            # Handle various ISO format variations
            if dt_str.endswith('Z'):
                dt_str = dt_str[:-1] + '+00:00'
            return datetime.fromisoformat(dt_str)
        except (ValueError, TypeError):
            return None

    def _convert_user_data(self, data: dict) -> User:
        """Convert raw user data to User object.
        
        Args:
            data: Raw user data from API
            
        Returns:
            User object
        """
        return User(
            id=data["id"],
            username=data.get("username", ""),
            display_name=data.get("display_name", data.get("name", "")),
            email=data.get("email", ""),
            avatar_url=data.get("avatar_url"),
            created_at=self._parse_datetime(data.get("created_at")),
            verified=data.get("verified", False)
        )

    def _convert_channel_data(self, data: dict) -> Channel:
        """Convert raw channel data to Channel object.
        
        Args:
            data: Raw channel data from API
            
        Returns:
            Channel object
        """
        return Channel(
            id=data["id"],
            name=data["name"],
            platform=data.get("platform", ""),
            enabled=data.get("enabled", True),
            url=data.get("url"),
            thumbnail_url=data.get("thumbnail_url"),
            description=data.get("description"),
            followers_count=data.get("followers_count"),
            created_at=self._parse_datetime(data.get("created_at")),
            updated_at=self._parse_datetime(data.get("updated_at"))
        )

    def _convert_event_data(self, data: dict) -> StreamEvent:
        """Convert raw event data to StreamEvent object.
        
        Args:
            data: Raw event data from API
            
        Returns:
            StreamEvent object
        """
        return StreamEvent(
            id=data["id"],
            title=data.get("title", ""),
            status=data.get("status", ""),
            type=data.get("type", ""),
            start_time=self._parse_datetime(data.get("start_time")),
            end_time=self._parse_datetime(data.get("end_time")),
            duration=data.get("duration"),
            viewer_count=data.get("viewer_count"),
            peak_viewers=data.get("peak_viewers"),
            created_at=self._parse_datetime(data.get("created_at")),
            updated_at=self._parse_datetime(data.get("updated_at"))
        )

    @retry_on_transient_error(max_retries=3)
    def get_profile(self) -> Profile:
        """Get user profile information.
        
        Returns:
            Profile object with user information
        """
        data = self._make_request("GET", "/profile")
        
        # Handle both nested and flat profile responses
        if "user" in data:
            user_data = data["user"]
        else:
            user_data = data
            
        user = self._convert_user_data(user_data)
        
        return Profile(
            user=user,
            subscription_plan=data.get("subscription_plan"),
            streaming_quota=data.get("streaming_quota"),
            features=data.get("features")
        )

    @retry_on_transient_error(max_retries=3)
    def list_channels(self) -> Union[ChannelList, List[Channel]]:
        """List all channels for the authenticated user.
        
        Returns:
            ChannelList object or list of Channel objects for backward compatibility
        """
        data = self._make_request("GET", "/channels")
        
        # Handle both paginated and simple list responses
        if isinstance(data, list):
            # Simple list response - convert to list of Channel objects
            channels = [self._convert_channel_data(item) for item in data]
            return channels
        elif isinstance(data, dict) and "channels" in data:
            # Paginated response
            channels = [self._convert_channel_data(item) for item in data["channels"]]
            return ChannelList(
                channels=channels,
                total=data.get("total", len(channels))
            )
        else:
            # Fallback to empty list
            return []

    @retry_on_transient_error(max_retries=3)
    def get_channel(self, channel_id: str) -> Channel:
        """Get details for a specific channel.
        
        Args:
            channel_id: The channel ID to retrieve
            
        Returns:
            Channel object with channel details
        """
        data = self._make_request("GET", f"/channels/{channel_id}")
        return self._convert_channel_data(data)

    @retry_on_transient_error(max_retries=3)
    def list_events(self) -> Union[EventList, List[StreamEvent]]:
        """List all events for the authenticated user.
        
        Returns:
            EventList object or list of StreamEvent objects for backward compatibility
        """
        data = self._make_request("GET", "/events")
        
        # Handle both paginated and simple list responses
        if isinstance(data, list):
            # Simple list response - convert to list of StreamEvent objects
            events = [self._convert_event_data(item) for item in data]
            return events
        elif isinstance(data, dict) and "events" in data:
            # Paginated response
            events = [self._convert_event_data(item) for item in data["events"]]
            return EventList(
                events=events,
                total=data.get("total", len(events)),
                page=data.get("page", 1),
                per_page=data.get("per_page", 20)
            )
        else:
            # Fallback to empty list
            return []
