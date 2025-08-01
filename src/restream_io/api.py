import time
from typing import Optional

import requests

from .config import load_tokens, save_tokens
from .errors import APIError, AuthenticationError
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

    @retry_on_transient_error(max_retries=3)
    def get_profile(self):
        """Get user profile information."""
        return self._make_request("GET", "/profile")

    @retry_on_transient_error(max_retries=3)
    def list_channels(self):
        """List all channels for the authenticated user."""
        return self._make_request("GET", "/channels")

    @retry_on_transient_error(max_retries=3)
    def get_channel(self, channel_id: str):
        """Get details for a specific channel.
        
        Args:
            channel_id: The channel ID to retrieve
        """
        return self._make_request("GET", f"/channels/{channel_id}")

    @retry_on_transient_error(max_retries=3)
    def list_events(self):
        """List all events for the authenticated user."""
        return self._make_request("GET", "/events")
