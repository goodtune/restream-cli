import base64
import hashlib
import secrets
import socket
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Event, Thread
from typing import Optional, Tuple

import requests

from .config import get_client_id, get_client_secret, load_tokens, save_tokens
from .errors import AuthenticationError


def generate_pkce_pair() -> Tuple[str, str]:
    """Generate PKCE code verifier and challenge pair.

    Returns:
        Tuple of (code_verifier, code_challenge)
    """
    # Generate code verifier (43-128 characters)
    code_verifier = (
        base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8").rstrip("=")
    )

    # Generate code challenge
    challenge_bytes = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = (
        base64.urlsafe_b64encode(challenge_bytes).decode("utf-8").rstrip("=")
    )

    return code_verifier, code_challenge


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth2 callback."""

    def __init__(self, expected_state: str, callback_event: Event, *args, **kwargs):
        self.expected_state = expected_state
        self.callback_event = callback_event
        self.auth_code = None
        self.auth_error = None
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET request from OAuth provider redirect."""
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.query)

        # Check for error parameter
        if "error" in query_params:
            error = query_params["error"][0]
            error_description = query_params.get(
                "error_description", ["Unknown error"]
            )[0]
            self.auth_error = f"OAuth error: {error} - {error_description}"
            self._send_error_response()
            return

        # Validate state parameter
        received_state = query_params.get("state", [None])[0]
        if not received_state or received_state != self.expected_state:
            self.auth_error = "Invalid state parameter - potential CSRF attack"
            self._send_error_response()
            return

        # Extract authorization code
        auth_code = query_params.get("code", [None])[0]
        if not auth_code:
            self.auth_error = "No authorization code received"
            self._send_error_response()
            return

        self.auth_code = auth_code
        self._send_success_response()

        # Signal that callback has been processed
        self.callback_event.set()

    def _send_success_response(self):
        """Send success response to browser."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        html = """
        <html>
        <head><title>Authorization Successful</title></head>
        <body>
            <h1>Authorization Successful!</h1>
            <p>You can now close this window and return to the CLI.</p>
        </body>
        </html>
        """
        self.wfile.write(html.encode())

    def _send_error_response(self):
        """Send error response to browser."""
        self.send_response(400)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        html = f"""
        <html>
        <head><title>Authorization Failed</title></head>
        <body>
            <h1>Authorization Failed</h1>
            <p>Error: {self.auth_error}</p>
            <p>Please try again or contact support.</p>
        </body>
        </html>
        """
        self.wfile.write(html.encode())

        # Signal that callback has been processed (even on error)
        self.callback_event.set()

    def log_message(self, format, *args):
        """Suppress server log messages."""
        pass


def find_free_port() -> int:
    """Find a free port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


def exchange_code_for_tokens(
    auth_code: str, redirect_uri: str, code_verifier: Optional[str] = None
) -> dict:
    """Exchange authorization code for access and refresh tokens.

    Args:
        auth_code: Authorization code from OAuth provider
        redirect_uri: The redirect URI used in the authorization request
        code_verifier: PKCE code verifier (optional)

    Returns:
        Dictionary containing token response

    Raises:
        AuthenticationError: If token exchange fails
    """
    client_id = get_client_id()
    client_secret = get_client_secret()

    if not client_id:
        raise AuthenticationError("RESTREAM_CLIENT_ID environment variable not set")

    # Prepare token request data
    token_data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "code": auth_code,
        "redirect_uri": redirect_uri,
    }

    # Add PKCE code verifier if provided
    if code_verifier:
        token_data["code_verifier"] = code_verifier

    # Add client secret if available (not needed for PKCE)
    if client_secret:
        token_data["client_secret"] = client_secret

    # Make token exchange request
    token_url = "https://api.restream.io/oauth/token"

    try:
        response = requests.post(
            token_url,
            data=token_data,
            headers={"Accept": "application/json"},
            timeout=30,
        )

        if not response.ok:
            error_msg = f"Token exchange failed: {response.status_code}"
            try:
                error_data = response.json()
                if "error_description" in error_data:
                    error_msg += f" - {error_data['error_description']}"
                elif "error" in error_data:
                    error_msg += f" - {error_data['error']}"
            except ValueError:
                error_msg += f" - {response.text}"

            raise AuthenticationError(error_msg)

        return response.json()

    except requests.RequestException as e:
        raise AuthenticationError(f"Network error during token exchange: {e}")


def perform_login(
    client_id: str = None, redirect_port: int = 12000, use_pkce: bool = True
) -> bool:
    """Perform OAuth2 Authorization Code flow with local redirect capture.

    Args:
        client_id: OAuth client ID (uses environment variable if not provided)
        redirect_port: Port for local redirect server (default: 12000)
        use_pkce: Whether to use PKCE (default: True)

    Returns:
        True if login successful, False otherwise

    Raises:
        AuthenticationError: If authentication fails
    """
    # Get client ID from parameter or environment
    if not client_id:
        client_id = get_client_id()

    if not client_id:
        raise AuthenticationError(
            "Client ID not provided and RESTREAM_CLIENT_ID environment variable not set"
        )

    # Use provided port or default to 12000
    if redirect_port is None:
        redirect_port = 12000

    # Generate state for CSRF protection
    state = secrets.token_urlsafe(16)

    # Generate PKCE pair if requested
    code_verifier = None
    code_challenge = None
    if use_pkce:
        code_verifier, code_challenge = generate_pkce_pair()

    # Build authorization URL
    redirect_uri = f"http://localhost:{redirect_port}/callback"

    auth_params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state,
    }

    if code_challenge:
        auth_params["code_challenge"] = code_challenge
        auth_params["code_challenge_method"] = "S256"

    auth_url = "https://api.restream.io/oauth/authorize?" + urllib.parse.urlencode(
        auth_params
    )

    # Set up callback handler and server
    callback_event = Event()
    callback_results = {"auth_code": None, "auth_error": None}

    class CallbackHandlerWithResults(OAuthCallbackHandler):
        def do_GET(self):
            super().do_GET()
            # Store results after processing
            callback_results["auth_code"] = getattr(self, "auth_code", None)
            callback_results["auth_error"] = getattr(self, "auth_error", None)

    def handler_factory(*args, **kwargs):
        return CallbackHandlerWithResults(state, callback_event, *args, **kwargs)

    # Start local server
    try:
        server = HTTPServer(("localhost", redirect_port), handler_factory)
        server_thread = Thread(target=server.serve_forever, daemon=True)
        server_thread.start()

        print("Starting OAuth2 login flow...")
        print(f"Opening browser to: {auth_url}")
        print(f"Listening for callback on http://localhost:{redirect_port}/callback")

        # Open browser
        webbrowser.open(auth_url)

        # Wait for callback with timeout
        callback_received = callback_event.wait(timeout=300)  # 5 minute timeout

        # Stop server
        server.shutdown()
        server.server_close()

        if not callback_received:
            raise AuthenticationError(
                "Login timed out - no response received within 5 minutes"
            )

        # Check for errors from callback
        if callback_results["auth_error"]:
            raise AuthenticationError(callback_results["auth_error"])

        if not callback_results["auth_code"]:
            raise AuthenticationError("No authorization code received")

        # Exchange code for tokens
        print("Authorization code received, exchanging for tokens...")
        token_response = exchange_code_for_tokens(
            callback_results["auth_code"], redirect_uri, code_verifier
        )

        # Save tokens
        save_tokens(token_response)

        print("Login successful! Tokens saved securely.")
        return True

    except AuthenticationError:
        raise
    except Exception as e:
        raise AuthenticationError(f"Unexpected error during login: {e}")


def get_access_token() -> Optional[str]:
    """Get a valid access token, refreshing if necessary.

    Returns:
        Valid access token or None if no tokens available

    Raises:
        AuthenticationError: If token refresh fails
    """
    tokens = load_tokens()
    if not tokens:
        return None

    access_token = tokens.get("access_token")
    if not access_token:
        return None

    # Check if token is expired and refresh if needed
    expires_at = tokens.get("expires_at")
    if expires_at and time.time() >= expires_at:
        refresh_token = tokens.get("refresh_token")
        if refresh_token:
            access_token = _refresh_token(refresh_token)
        else:
            return None

    return access_token


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
            raise AuthenticationError(f"Token refresh failed: {response.status_code}")

        token_response = response.json()

        # Save the new tokens
        save_tokens(token_response)

        return token_response["access_token"]

    except requests.RequestException as e:
        raise AuthenticationError(f"Network error during token refresh: {e}")
