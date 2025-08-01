"""Tests for utils module retry functionality."""

from unittest.mock import Mock, patch

import pytest

from restream_io.errors import APIError
from restream_io.utils import exponential_backoff, retry_on_transient_error


class TestExponentialBackoff:
    """Test exponential backoff functionality."""

    @patch("time.sleep")
    @patch("random.uniform")
    def test_exponential_backoff_calculation(self, mock_uniform, mock_sleep):
        """Test exponential backoff delay calculation."""
        mock_uniform.return_value = 0.05  # Fixed jitter

        # Test first retry (attempt 0)
        exponential_backoff(0, base=1.0, cap=10.0)
        expected_delay = 1.0 + 0.05  # base * 2^0 + jitter
        mock_sleep.assert_called_with(expected_delay)

        # Test second retry (attempt 1)
        exponential_backoff(1, base=1.0, cap=10.0)
        expected_delay = 2.0 + 0.05  # base * 2^1 + jitter
        mock_sleep.assert_called_with(expected_delay)

        # Test third retry (attempt 2)
        exponential_backoff(2, base=1.0, cap=10.0)
        expected_delay = 4.0 + 0.05  # base * 2^2 + jitter
        mock_sleep.assert_called_with(expected_delay)

    @patch("time.sleep")
    @patch("random.uniform")
    def test_exponential_backoff_cap(self, mock_uniform, mock_sleep):
        """Test that delay is capped at max value."""
        mock_uniform.return_value = 0.0  # No jitter for simplicity

        # Large retry number should be capped
        exponential_backoff(10, base=1.0, cap=5.0)
        mock_sleep.assert_called_with(5.0)  # Should be capped at 5.0

    @patch("time.sleep")
    @patch("random.uniform")
    def test_exponential_backoff_jitter(self, mock_uniform, mock_sleep):
        """Test that jitter is added correctly."""
        mock_uniform.return_value = 0.1

        exponential_backoff(0, base=2.0, cap=10.0)
        # base * 2^0 + jitter = 2.0 + 0.1 = 2.1
        mock_sleep.assert_called_with(2.1)


class TestRetryDecorator:
    """Test retry decorator functionality."""

    def test_retry_decorator_success_no_retry(self):
        """Test function that succeeds on first try."""
        mock_func = Mock(return_value="success")
        decorated_func = retry_on_transient_error(max_retries=3)(mock_func)

        result = decorated_func("arg1", key="value")

        assert result == "success"
        mock_func.assert_called_once_with("arg1", key="value")

    @patch("restream_io.utils.exponential_backoff")
    def test_retry_decorator_transient_error_then_success(self, mock_backoff):
        """Test function that fails with transient error then succeeds."""
        transient_error = APIError("Server error", status_code=500)
        mock_func = Mock(side_effect=[transient_error, "success"])
        decorated_func = retry_on_transient_error(max_retries=3)(mock_func)

        result = decorated_func("arg1")

        assert result == "success"
        assert mock_func.call_count == 2
        mock_backoff.assert_called_once_with(0, 0.5, 10.0)  # First retry

    @patch("restream_io.utils.exponential_backoff")
    def test_retry_decorator_non_transient_error_no_retry(self, mock_backoff):
        """Test function that fails with non-transient error."""
        non_transient_error = APIError("Not found", status_code=404)
        mock_func = Mock(side_effect=non_transient_error)
        decorated_func = retry_on_transient_error(max_retries=3)(mock_func)

        with pytest.raises(APIError) as exc_info:
            decorated_func("arg1")

        assert exc_info.value.status_code == 404
        mock_func.assert_called_once()
        mock_backoff.assert_not_called()  # No retry

    @patch("restream_io.utils.exponential_backoff")
    def test_retry_decorator_exhausted_retries(self, mock_backoff):
        """Test function that exhausts all retries."""
        transient_error = APIError("Server error", status_code=500)
        mock_func = Mock(side_effect=transient_error)
        decorated_func = retry_on_transient_error(max_retries=2)(mock_func)

        with pytest.raises(APIError) as exc_info:
            decorated_func("arg1")

        assert exc_info.value.status_code == 500
        assert mock_func.call_count == 3  # 1 original + 2 retries
        assert mock_backoff.call_count == 2  # 2 retries

    def test_retry_decorator_non_api_error_no_retry(self):
        """Test function that raises non-API error."""
        non_api_error = ValueError("Invalid value")
        mock_func = Mock(side_effect=non_api_error)
        decorated_func = retry_on_transient_error(max_retries=3)(mock_func)

        with pytest.raises(ValueError) as exc_info:
            decorated_func("arg1")

        assert str(exc_info.value) == "Invalid value"
        mock_func.assert_called_once()  # No retry

    @patch("restream_io.utils.exponential_backoff")
    def test_retry_decorator_custom_parameters(self, mock_backoff):
        """Test retry decorator with custom parameters."""
        transient_error = APIError("Rate limited", status_code=429)
        mock_func = Mock(side_effect=[transient_error, "success"])
        decorated_func = retry_on_transient_error(
            max_retries=5, base_delay=1.0, max_delay=30.0
        )(mock_func)

        result = decorated_func("arg1")

        assert result == "success"
        assert mock_func.call_count == 2
        mock_backoff.assert_called_once_with(0, 1.0, 30.0)  # Custom parameters

    @patch("restream_io.utils.exponential_backoff")
    def test_retry_decorator_multiple_transient_errors(self, mock_backoff):
        """Test function with multiple transient errors before success."""
        error1 = APIError("Server error", status_code=500)
        error2 = APIError("Bad gateway", status_code=502)
        error3 = APIError("Rate limited", status_code=429)

        mock_func = Mock(side_effect=[error1, error2, error3, "success"])
        decorated_func = retry_on_transient_error(max_retries=3)(mock_func)

        result = decorated_func("arg1")

        assert result == "success"
        assert mock_func.call_count == 4  # 1 original + 3 retries
        assert mock_backoff.call_count == 3  # 3 retries

        # Check backoff was called with correct attempt numbers
        from unittest.mock import call

        expected_calls = [
            call(0, 0.5, 10.0),  # First retry
            call(1, 0.5, 10.0),  # Second retry
            call(2, 0.5, 10.0),  # Third retry
        ]
        mock_backoff.assert_has_calls(expected_calls)

    def test_retry_decorator_preserves_function_metadata(self):
        """Test that decorator preserves original function metadata."""

        def original_function(x, y=None):
            """Original docstring."""
            return x + (y or 0)

        decorated_func = retry_on_transient_error()(original_function)

        assert decorated_func.__name__ == "original_function"
        assert decorated_func.__doc__ == "Original docstring."

        # Test function still works correctly
        result = decorated_func(5, y=3)
        assert result == 8
