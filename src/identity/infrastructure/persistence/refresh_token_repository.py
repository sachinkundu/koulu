"""Redis implementation of refresh token blacklist repository."""

from redis.asyncio import Redis

from src.identity.domain.repositories import IRefreshTokenRepository
from src.identity.domain.value_objects import UserId


class RedisRefreshTokenRepository(IRefreshTokenRepository):
    """Redis implementation of IRefreshTokenRepository for token blacklist."""

    TOKEN_PREFIX = "token_blacklist:"
    USER_PREFIX = "user_blacklist:"

    def __init__(self, redis: Redis) -> None:  # type: ignore[type-arg]
        """Initialize with Redis client."""
        self._redis = redis

    async def blacklist(self, token: str, expires_in_seconds: int) -> None:
        """Add a refresh token to the blacklist."""
        key = f"{self.TOKEN_PREFIX}{token}"
        await self._redis.setex(key, expires_in_seconds, "1")

    async def is_blacklisted(self, token: str) -> bool:
        """Check if a token is blacklisted."""
        key = f"{self.TOKEN_PREFIX}{token}"
        return await self._redis.exists(key) > 0

    async def blacklist_all_for_user(
        self,
        user_id: UserId,
        expires_in_seconds: int,
    ) -> None:
        """Blacklist all refresh tokens for a user."""
        key = f"{self.USER_PREFIX}{user_id.value}"
        await self._redis.setex(key, expires_in_seconds, "1")

    async def is_user_blacklisted(self, user_id: UserId) -> bool:
        """Check if all tokens for a user are blacklisted."""
        key = f"{self.USER_PREFIX}{user_id.value}"
        return await self._redis.exists(key) > 0
