"""SQLAlchemy implementation of reset token repository."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.identity.domain.repositories import IResetTokenRepository
from src.identity.domain.value_objects import UserId
from src.identity.infrastructure.persistence.models import ResetTokenModel


class SqlAlchemyResetTokenRepository(IResetTokenRepository):
    """SQLAlchemy implementation of IResetTokenRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with database session."""
        self._session = session

    async def save(
        self,
        user_id: UserId,
        token: str,
        expires_at: datetime,
    ) -> None:
        """Save a reset token (replaces existing)."""
        # Delete existing tokens for user
        await self._session.execute(
            delete(ResetTokenModel).where(ResetTokenModel.user_id == user_id.value)
        )

        # Create new token
        token_model = ResetTokenModel(
            id=uuid4(),
            user_id=user_id.value,
            token=token,
            expires_at=expires_at,
        )
        self._session.add(token_model)
        await self._session.flush()

    async def get_user_id_by_token(self, token: str) -> UserId | None:
        """Get user ID for valid, non-expired, unused token."""
        now = datetime.now(UTC)
        result = await self._session.execute(
            select(ResetTokenModel.user_id).where(
                ResetTokenModel.token == token,
                ResetTokenModel.expires_at > now,
                ResetTokenModel.used_at.is_(None),
            )
        )
        user_id = result.scalar_one_or_none()

        if user_id is None:
            return None

        return UserId(value=user_id)

    async def mark_as_used(self, token: str) -> None:
        """Mark a token as used."""
        now = datetime.now(UTC)
        await self._session.execute(
            update(ResetTokenModel).where(ResetTokenModel.token == token).values(used_at=now)
        )
        await self._session.flush()

    async def delete_by_user_id(self, user_id: UserId) -> None:
        """Delete all reset tokens for a user."""
        await self._session.execute(
            delete(ResetTokenModel).where(ResetTokenModel.user_id == user_id.value)
        )
        await self._session.flush()

    async def delete_expired(self) -> int:
        """Delete all expired tokens."""
        now = datetime.now(UTC)
        result = await self._session.execute(
            delete(ResetTokenModel)
            .where(ResetTokenModel.expires_at <= now)
            .returning(ResetTokenModel.id)
        )
        deleted = result.fetchall()
        await self._session.flush()
        return len(deleted)
