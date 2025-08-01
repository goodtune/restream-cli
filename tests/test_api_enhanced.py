"""Tests for enhanced RestreamClient functionality."""

import time
from unittest.mock import Mock, patch

import pytest
import requests
import responses

from restream_io.api import RestreamClient
from restream_io.errors import APIError, AuthenticationError


class TestAPIError:
    """Test the enhanced APIError class."""

    def test_api_error_basic(self):
        """Test basic APIError creation."""
        error = APIError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.status_code is None
        assert error.response_text is None
        assert error.url is None

    def test_api_error_with_all_details(self):
        """Test APIError with all details."""
        error = APIError(
            message="Request failed",
            status_code=500,
            response_text="Internal server error",
            url="https://api.restream.io/v2/user/profile",
        )

        expected = "Request failed | Status: 500 | URL: https://api.restream.io/v2/user/profile | Response: Internal server error"
        assert str(error) == expected
        assert error.status_code == 500
        assert error.response_text == "Internal server error"
        assert error.url == "https://api.restream.io/v2/user/profile"

    def test_api_error_long_response_truncated(self):
        """Test that long responses are truncated."""
        long_response = "x" * 250
        error = APIError("Failed", response_text=long_response)

        # Should be truncated to 200 chars + "..."
        assert "..." in str(error)
        assert len(str(error).split("Response: ")[1]) == 203  # 200 + "..."

    def test_is_transient_server_errors(self):
        """Test is_transient for server errors."""
        error_500 = APIError("Server error", status_code=500)
        error_502 = APIError("Bad gateway", status_code=502)
        error_503 = APIError("Service unavailable", status_code=503)

        assert error_500.is_transient()
        assert error_502.is_transient()
        assert error_503.is_transient()

    def test_is_transient_rate_limit(self):
        """Test is_transient for rate limiting."""
        error = APIError("Rate limited", status_code=429)
        assert error.is_transient()

    def test_is_transient_timeout(self):
        """Test is_transient for timeout."""
        error = APIError("Timeout", status_code=408)
        assert error.is_transient()

    def test_not_transient_client_errors(self):
        """Test is_transient for non-transient client errors."""
        error_400 = APIError("Bad request", status_code=400)
        error_401 = APIError("Unauthorized", status_code=401)
        error_404 = APIError("Not found", status_code=404)

        assert not error_400.is_transient()
        assert not error_401.is_transient()
        assert not error_404.is_transient()

    def test_not_transient_no_status_code(self):
        """Test is_transient when no status code is provided."""
        error = APIError("Network error")
        assert not error.is_transient()


class TestRestreamClientEnhanced:
    """Test enhanced RestreamClient functionality."""

    def test_client_initialization(self):
        """Test basic client initialization."""
        session = requests.Session()
        token = "test-token"
        client = RestreamClient(session, token)

        assert client.session is session
        assert client.token == token
        assert session.headers["Authorization"] == "Bearer test-token"

    @responses.activate
    def test_make_request_success(self):
        """Test successful API request."""
        responses.add(
            "GET",
            "https://api.restream.io/v2/test",
            json={"result": "success"},
            status=200,
        )

        session = requests.Session()
        client = RestreamClient(session, "test-token")

        result = client._make_request("GET", "/test")
        assert result == {"result": "success"}

    @responses.activate
    def test_make_request_error_with_json_response(self):
        """Test API request that returns structured error."""
        error_response = {
            "error": "invalid_request",
            "message": "Missing required parameter",
        }
        responses.add(
            "GET", "https://api.restream.io/v2/test", json=error_response, status=400
        )

        session = requests.Session()
        client = RestreamClient(session, "test-token")

        with pytest.raises(APIError) as exc_info:
            client._make_request("GET", "/test")

        error = exc_info.value
        assert error.status_code == 400
        assert (
            "Missing required parameter" in error.message
        )  # Using message field directly
        assert error.url == "https://api.restream.io/v2/test"

    @responses.activate
    def test_make_request_error_with_text_response(self):
        """Test API request that returns plain text error."""
        responses.add(
            "GET",
            "https://api.restream.io/v2/test",
            body="Internal Server Error",
            status=500,
        )

        session = requests.Session()
        client = RestreamClient(session, "test-token")

        with pytest.raises(APIError) as exc_info:
            client._make_request("GET", "/test")

        error = exc_info.value
        assert error.status_code == 500
        assert error.message == "API request failed"
        assert "Internal Server Error" in error.response_text

    def test_make_request_network_error(self):
        """Test network error handling."""
        session = Mock()
        session.request.side_effect = requests.RequestException("Connection failed")

        client = RestreamClient(session, "test-token")

        with pytest.raises(APIError) as exc_info:
            client._make_request("GET", "/test")

        error = exc_info.value
        assert "Network error" in error.message
        assert "Connection failed" in error.message

    @patch("restream_io.api.load_tokens")
    def test_from_config_no_tokens(self, mock_load_tokens):
        """Test from_config when no tokens are stored."""
        mock_load_tokens.return_value = None

        with pytest.raises(AuthenticationError) as exc_info:
            RestreamClient.from_config()

        assert "No stored tokens found" in str(exc_info.value)

    @patch("restream_io.api.load_tokens")
    def test_from_config_no_access_token(self, mock_load_tokens):
        """Test from_config when tokens don't contain access_token."""
        mock_load_tokens.return_value = {"refresh_token": "refresh-token"}

        with pytest.raises(AuthenticationError) as exc_info:
            RestreamClient.from_config()

        assert "No access token found" in str(exc_info.value)

    @patch("restream_io.api.load_tokens")
    def test_from_config_valid_token(self, mock_load_tokens):
        """Test from_config with valid non-expired token."""
        future_time = time.time() + 3600  # 1 hour from now
        mock_load_tokens.return_value = {
            "access_token": "access-token",
            "refresh_token": "refresh-token",
            "expires_at": future_time,
        }

        client = RestreamClient.from_config()
        assert client.token == "access-token"
        assert client.session.headers["Authorization"] == "Bearer access-token"

    @patch("restream_io.api.load_tokens")
    @patch("restream_io.api.RestreamClient._refresh_token")
    def test_from_config_expired_token_with_refresh(
        self, mock_refresh, mock_load_tokens
    ):
        """Test from_config with expired token that gets refreshed."""
        past_time = time.time() - 3600  # 1 hour ago
        mock_load_tokens.return_value = {
            "access_token": "old-access-token",
            "refresh_token": "refresh-token",
            "expires_at": past_time,
        }
        mock_refresh.return_value = "new-access-token"

        client = RestreamClient.from_config()
        assert client.token == "new-access-token"
        mock_refresh.assert_called_once_with("refresh-token")

    @patch("restream_io.api.load_tokens")
    def test_from_config_expired_token_no_refresh(self, mock_load_tokens):
        """Test from_config with expired token and no refresh token."""
        past_time = time.time() - 3600  # 1 hour ago
        mock_load_tokens.return_value = {
            "access_token": "old-access-token",
            "expires_at": past_time,
        }

        with pytest.raises(AuthenticationError) as exc_info:
            RestreamClient.from_config()

        assert "expired and no refresh token" in str(exc_info.value)


class TestRetryLogic:
    """Test retry logic integration."""

    @responses.activate
    def test_retry_on_transient_error(self):
        """Test that transient errors are retried."""
        # First call returns 500 (transient), second call succeeds
        responses.add("GET", "https://api.restream.io/v2/user/profile", status=500)
        responses.add(
            "GET",
            "https://api.restream.io/v2/user/profile",
            json={"id": 123, "username": "test", "email": "test@example.com"},
            status=200,
        )

        session = requests.Session()
        client = RestreamClient(session, "test-token")

        # This should succeed after retry
        result = client.get_profile()
        assert result.id == 123
        assert result.username == "test"
        assert len(responses.calls) == 2

    @responses.activate
    def test_no_retry_on_non_transient_error(self):
        """Test that non-transient errors are not retried."""
        responses.add("GET", "https://api.restream.io/v2/user/profile", status=404)

        session = requests.Session()
        client = RestreamClient(session, "test-token")

        with pytest.raises(APIError) as exc_info:
            client.get_profile()

        assert exc_info.value.status_code == 404
        assert len(responses.calls) == 1  # No retry

    @responses.activate
    def test_retry_exhaustion(self):
        """Test that retries are exhausted and error is raised."""
        # Return 500 for all calls
        for _ in range(5):  # More than max_retries (3) + 1
            responses.add("GET", "https://api.restream.io/v2/user/profile", status=500)

        session = requests.Session()
        client = RestreamClient(session, "test-token")

        with pytest.raises(APIError) as exc_info:
            client.get_profile()

        assert exc_info.value.status_code == 500
        assert len(responses.calls) == 4  # 1 + 3 retries


class TestTokenRefresh:
    """Test token refresh functionality."""

    @responses.activate
    def test_refresh_token_success(self):
        """Test successful token refresh."""
        # Mock environment variables
        with patch.dict(
            "os.environ",
            {
                "RESTREAM_CLIENT_ID": "test-client-id",
                "RESTREAM_CLIENT_SECRET": "test-client-secret",
            },
        ):
            new_token_response = {
                "access_token": "new-access-token",
                "refresh_token": "new-refresh-token",
                "expires_in": 3600,
            }

            responses.add(
                "POST",
                "https://api.restream.io/oauth/token",
                json=new_token_response,
                status=200,
            )

            with patch("restream_io.api.save_tokens") as mock_save_tokens:
                result = RestreamClient._refresh_token("old-refresh-token")

                assert result == "new-access-token"
                mock_save_tokens.assert_called_once_with(new_token_response)

            # Check request was made with correct data
            request = responses.calls[0].request
            assert "grant_type=refresh_token" in request.body
            assert "refresh_token=old-refresh-token" in request.body
            assert "client_id=test-client-id" in request.body
            assert "client_secret=test-client-secret" in request.body

    @responses.activate
    def test_refresh_token_missing_client_id(self):
        """Test token refresh with missing client ID."""
        with patch.dict("os.environ", {}, clear=True):  # Clear environment
            with pytest.raises(AuthenticationError) as exc_info:
                RestreamClient._refresh_token("refresh-token")

            assert "RESTREAM_CLIENT_ID" in str(exc_info.value)

    @responses.activate
    def test_refresh_token_server_error(self):
        """Test token refresh server error."""
        with patch.dict("os.environ", {"RESTREAM_CLIENT_ID": "test-client-id"}):
            responses.add("POST", "https://api.restream.io/oauth/token", status=400)

            with pytest.raises(AuthenticationError) as exc_info:
                RestreamClient._refresh_token("refresh-token")

            assert "Token refresh failed: 400" in str(exc_info.value)
