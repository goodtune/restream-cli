class APIError(Exception):
    """Exception raised when API requests fail."""

    def __init__(
        self,
        message: str,
        status_code: int = None,
        response_text: str = None,
        url: str = None,
    ):
        self.message = message
        self.status_code = status_code
        self.response_text = response_text
        self.url = url
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format a comprehensive error message."""
        parts = [self.message]

        if self.status_code:
            parts.append(f"Status: {self.status_code}")

        if self.url:
            parts.append(f"URL: {self.url}")

        if self.response_text:
            # Truncate long responses
            response = (
                self.response_text[:200] + "..."
                if len(self.response_text) > 200
                else self.response_text
            )
            parts.append(f"Response: {response}")

        return " | ".join(parts)

    def is_transient(self) -> bool:
        """Check if this error might be transient and worth retrying."""
        if not self.status_code:
            return False

        # 5xx server errors and some 4xx client errors are considered transient
        return (
            self.status_code >= 500  # Server errors
            or self.status_code == 429  # Rate limiting
            or self.status_code == 408  # Request timeout
        )


class AuthenticationError(Exception):
    """Raised when OAuth authentication fails."""

    pass
