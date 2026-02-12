"""In-memory rate limiter implementation."""

import time
from collections import defaultdict

from src.community.domain.exceptions import RateLimitExceededError
from src.community.domain.services.rate_limiter import IRateLimiter
from src.identity.domain.value_objects import UserId

# Rate limits: action -> (max_count, window_seconds)
RATE_LIMITS: dict[str, tuple[int, int]] = {
    "create_post": (10, 3600),  # 10 posts per hour
}


class InMemoryRateLimiter(IRateLimiter):
    """In-memory rate limiter using class-level storage."""

    _timestamps: dict[str, list[float]] = defaultdict(list)

    async def check_rate_limit(self, user_id: UserId, action: str) -> None:
        """Check if user has exceeded the rate limit for an action."""
        limit_config = RATE_LIMITS.get(action)
        if limit_config is None:
            return

        max_count, window_seconds = limit_config
        key = f"{user_id.value}:{action}"
        now = time.monotonic()

        # Clean expired timestamps
        self._timestamps[key] = [ts for ts in self._timestamps[key] if now - ts < window_seconds]

        if len(self._timestamps[key]) >= max_count:
            raise RateLimitExceededError()

        self._timestamps[key].append(now)

    @classmethod
    def reset(cls) -> None:
        """Reset all rate limit tracking. Used in tests."""
        cls._timestamps.clear()
