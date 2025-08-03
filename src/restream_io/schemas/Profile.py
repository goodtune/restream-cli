"""User profile schema."""

import attrs


@attrs.define
class Profile:
    """User profile information from /profile endpoint."""

    id: int
    username: str
    email: str

    def __str__(self) -> str:
        """Format profile for human-readable output."""
        return (
            f"Profile Information:\n"
            f"  ID: {self.id}\n"
            f"  Username: {self.username}\n"
            f"  Email: {self.email}"
        )
