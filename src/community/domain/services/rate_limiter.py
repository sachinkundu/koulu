"""Rate limiter interface."""

from abc import ABC, abstractmethod

from src.identity.domain.value_objects import UserId


class IRateLimiter(ABC):
    """Interface for rate limiting operations."""

    @abstractmethod
    async def check_rate_limit(self, user_id: UserId, action: str) -> None:
        """
        Check if user has exceeded the rate limit for an action.

        Args:
            user_id: The user performing the action
            action: The action being rate limited (e.g., "create_post")

        Raises:
            RateLimitExceededError: If rate limit is exceeded
        """
        ...
