import random
import time


def exponential_backoff(retries: int, base: float = 0.5, cap: float = 10.0):
    """Return sleep time for given retry number."""
    delay = min(cap, base * (2**retries)) + random.uniform(0, 0.1 * base)
    time.sleep(delay)
