import random
import time
from functools import wraps
from typing import Callable, TypeVar

from .errors import APIError

T = TypeVar("T")


def exponential_backoff(retries: int, base: float = 0.5, cap: float = 10.0):
    """Return sleep time for given retry number."""
    delay = min(cap, base * (2**retries)) + random.uniform(0, 0.1 * base)
    time.sleep(delay)


def retry_on_transient_error(
    max_retries: int = 3, base_delay: float = 0.5, max_delay: float = 10.0
):
    """Decorator to retry function calls on transient errors.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay for exponential backoff
        max_delay: Maximum delay between retries
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except APIError as e:
                    # Only retry transient errors and not on the last attempt
                    if e.is_transient() and attempt < max_retries:
                        exponential_backoff(attempt, base_delay, max_delay)
                        continue
                    raise
                except Exception:
                    # Don't retry non-API errors
                    raise

            # This should never be reached, but just in case
            return func(*args, **kwargs)

        return wrapper

    return decorator
