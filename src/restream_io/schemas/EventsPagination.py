"""Events pagination schema."""

import attrs


@attrs.define
class EventsPagination:
    """Pagination information for events history."""

    pages_total: int
    page: int
    limit: int

    def __str__(self) -> str:
        """Format pagination for human-readable output."""
        return (
            f"Page {self.page} of {self.pages_total} "
            f"(showing up to {self.limit} items per page)"
        )
