"""Tiny retry helper with exponential backoff (no external deps)."""

from __future__ import annotations

import logging
import time
from functools import wraps
from typing import Any, Callable

from email_profile.core.errors import QuotaExceeded, RateLimited

logger = logging.getLogger(__name__)


_PERMANENT = (QuotaExceeded,)


def with_retry(
    *,
    attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator: retry a callable with exponential backoff.

    Honors ``RateLimited`` by waiting longer. Re-raises ``QuotaExceeded``
    immediately (it won't fix itself).
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            last_error: Exception | None = None

            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except _PERMANENT:
                    raise
                except RateLimited as error:
                    last_error = error
                    wait = min(delay * 4, max_delay)
                    logger.warning(
                        "Rate limited (attempt %d/%d). Waiting %.1fs.",
                        attempt,
                        attempts,
                        wait,
                    )
                    if attempt == attempts:
                        raise
                    time.sleep(wait)
                except Exception as error:
                    last_error = error
                    logger.warning(
                        "Transient error %s (attempt %d/%d). Waiting %.1fs.",
                        type(error).__name__,
                        attempt,
                        attempts,
                        delay,
                    )
                    if attempt == attempts:
                        raise
                    time.sleep(delay)
                    delay = min(delay * 2, max_delay)

            assert last_error is not None
            raise last_error

        return wrapper

    return decorator
