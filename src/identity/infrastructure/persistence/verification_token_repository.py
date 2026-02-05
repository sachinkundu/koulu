"""SQLAlchemy implementation of verification token repository."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.identity.domain.repositories import IVerificationTokenRepository
from src.identity.domain.value_objects import UserId
from src.identity.infrastructure.persistence.models import VerificationTokenModel


class SqlAlchemyVerificationTokenRepository(IVerificationTokenRepository):
    """SQLAlchemy implementation of IVerificationTokenRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with database session."""
        self._session = session

    async def save(
        self,
        user_id: UserId,
        token: str,
        expires_at: datetime,
    ) -> None:
        """Save a verification token (replaces existing)."""
        # Delete existing tokens for user
        await self._session.execute(
            delete(VerificationTokenModel).where(VerificationTokenModel.user_id == user_id.value)
        )

        # Create new token
        token_model = VerificationTokenModel(
            id=uuid4(),
            user_id=user_id.value,
            token=token,
            expires_at=expires_at,
        )
        self._session.add(token_model)
        await self._session.flush()

    async def get_user_id_by_token(self, token: str) -> UserId | None:
        """Get the user ID associated with a valid, non-expired token."""
        now = datetime.now(UTC)
        result = await self._session.execute(
            select(VerificationTokenModel.user_id).where(
                VerificationTokenModel.token == token,
                VerificationTokenModel.expires_at > now,
            )
        )
        user_id = result.scalar_one_or_none()

        if user_id is None:
            return None

        return UserId(value=user_id)

    async def delete_by_user_id(self, user_id: UserId) -> None:
        """Delete all tokens for a user."""
        await self._session.execute(
            delete(VerificationTokenModel).where(VerificationTokenModel.user_id == user_id.value)
        )
        await self._session.flush()

    async def delete_by_token(self, token: str) -> None:
        """Delete a specific token."""
        await self._session.execute(
            delete(VerificationTokenModel).where(VerificationTokenModel.token == token)
        )
        await self._session.flush()

    async def delete_expired(self) -> int:
        """Delete all expired tokens."""
        now = datetime.now(UTC)
        result = await self._session.execute(
            delete(VerificationTokenModel)
            .where(VerificationTokenModel.expires_at <= now)
            .returning(VerificationTokenModel.id)
        )
        deleted = result.fetchall()
        await self._session.flush()
        return len(deleted)
