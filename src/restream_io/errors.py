class APIError(Exception):
    pass


class AuthenticationError(Exception):
    """Raised when OAuth authentication fails."""
    pass
