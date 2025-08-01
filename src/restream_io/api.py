import time
from typing import List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import get_client_id, get_client_secret, load_tokens, save_tokens
from .errors import APIError, AuthenticationError
from .schemas import (
    Channel,
    ChannelSummary,
    EventDestination,
    EventsHistoryResponse,
    EventsPagination,
    Profile,
    StreamEvent,
)

DEFAULT_BASE_URL = "https://api.restream.io/v2"


class RestreamClient:
    def __init__(
        self, session: requests.Session, token: str, base_url: str = DEFAULT_BASE_URL
    ):
        self.session = session
        self.token = token
        self.base_url = base_url
        self.session.headers.update({"Authorization": f"Bearer {token}"})

        # Configure retry strategy using urllib3.util.Retry
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[408, 429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"],
            raise_on_status=False,  # Let us handle status codes
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    @classmethod
    def from_config(
        cls,
        session: Optional[requests.Session] = None,
        base_url: str = DEFAULT_BASE_URL,
    ) -> "RestreamClient":
        """Create a RestreamClient instance using tokens from config.

        Args:
            session: Optional requests session. If not provided, creates a new one.
            base_url: Base URL for API requests. Defaults to production API.

        Returns:
            RestreamClient instance

        Raises:
            AuthenticationError: If no valid tokens are available
        """
        if session is None:
            session = requests.Session()

        tokens = load_tokens()
        if not tokens:
            raise AuthenticationError(
                "No stored tokens found. Please run 'restream.io login' first."
            )

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
                raise AuthenticationError(
                    "Access token expired and no refresh token available. Please re-login."
                )

        return cls(session, access_token, base_url)

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
                raise AuthenticationError(
                    f"Token refresh failed: {response.status_code}"
                )

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
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = self.session.request(method, url, **kwargs)

            if not response.ok:
                # Try to get error details from response
                try:
                    error_data = response.json()
                    error_message = error_data.get(
                        "message", error_data.get("error", "API request failed")
                    )
                    # Ensure error_message is a string
                    if not isinstance(error_message, str):
                        error_message = str(error_message)
                except (ValueError, KeyError):
                    error_message = "API request failed"

                raise APIError(
                    message=error_message,
                    status_code=response.status_code,
                    response_text=response.text,
                    url=url,
                )

            return response.json()

        except requests.RequestException as e:
            raise APIError(f"Network error: {e}", url=url)

    def get_profile(self) -> Profile:
        """Get user profile information.

        Returns:
            Profile object with user information
        """
        data = self._make_request("GET", "/user/profile")
        return Profile(**data)

    def list_channels(self) -> List[ChannelSummary]:
        """List all channels for the authenticated user.

        Returns:
            List of ChannelSummary objects
        """
        data = self._make_request("GET", "/user/channel/all")

        # API returns a simple array of channel summary objects
        return [ChannelSummary(**item) for item in data]

    def get_channel(self, channel_id: str) -> Channel:
        """Get details for a specific channel.

        Args:
            channel_id: The channel ID to retrieve

        Returns:
            Channel object with full channel details
        """
        data = self._make_request("GET", f"/user/channel/{channel_id}")
        return Channel(**data)

    def _convert_events_data(self, events_data: List[dict]) -> List[StreamEvent]:
        """Convert raw events data to StreamEvent objects.

        Args:
            events_data: List of raw event data from API

        Returns:
            List of StreamEvent objects
        """
        events = []
        for item in events_data:
            # Convert destinations separately since they need nested object conversion
            destinations = [EventDestination(**dest) for dest in item["destinations"]]
            # Create a copy of item data and replace destinations with converted objects
            event_data = {**item, "destinations": destinations}
            events.append(StreamEvent(**event_data))
        return events

    def list_events_history(
        self, page: int = 1, limit: int = 10
    ) -> EventsHistoryResponse:
        """List historical events for the authenticated user.

        Args:
            page: Page number (default: 1)
            limit: Number of events per page (default: 10)

        Returns:
            EventsHistoryResponse with items and pagination
        """
        data = self._make_request(
            "GET", f"/user/events/history?page={page}&limit={limit}"
        )

        # Convert events data
        events = self._convert_events_data(data["items"])

        # Create pagination object
        pagination = EventsPagination(**data["pagination"])

        return EventsHistoryResponse(items=events, pagination=pagination)

    def list_events_in_progress(self) -> List[StreamEvent]:
        """List currently running events for the authenticated user.

        Returns:
            List of StreamEvent objects
        """
        data = self._make_request("GET", "/user/events/in-progress")
        return self._convert_events_data(data)

    def list_events_upcoming(
        self, source: Optional[int] = None, scheduled: Optional[bool] = None
    ) -> List[StreamEvent]:
        """List upcoming events for the authenticated user.

        Args:
            source: Filter by source type (1=Studio, 2=Encoder, 3=Video)
            scheduled: When True, returns only scheduled events

        Returns:
            List of StreamEvent objects
        """
        params = []
        if source is not None:
            params.append(f"source={source}")
        if scheduled is not None:
            params.append(f"scheduled={'true' if scheduled else 'false'}")

        query_string = "&".join(params)
        endpoint = "/user/events/upcoming"
        if query_string:
            endpoint += f"?{query_string}"

        data = self._make_request("GET", endpoint)
        return self._convert_events_data(data)

    def list_events(self) -> List[StreamEvent]:
        """List all events for the authenticated user.

        This method combines events from history, in-progress, and upcoming endpoints.

        Returns:
            List of StreamEvent objects
        """
        # Get events from all three endpoints
        history_response = self.list_events_history(page=1, limit=10)
        in_progress = self.list_events_in_progress()
        upcoming = self.list_events_upcoming()

        # Combine all events
        all_events = history_response.items + in_progress + upcoming

        return all_events
