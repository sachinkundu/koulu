"""SQLAlchemy implementation of reaction repository."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.community.domain.entities import Reaction
from src.community.domain.repositories import IReactionRepository
from src.community.domain.value_objects import PostId, ReactionId
from src.community.infrastructure.persistence.models import CommentModel, ReactionModel
from src.identity.domain.value_objects import UserId


class SqlAlchemyReactionRepository(IReactionRepository):
    """SQLAlchemy implementation of IReactionRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with database session."""
        self._session = session

    async def save(self, reaction: Reaction) -> None:
        """Save a reaction (create)."""
        model = ReactionModel(
            id=reaction.id.value,
            user_id=reaction.user_id.value,
            target_type=reaction.target_type,
            target_id=reaction.target_id,
            created_at=reaction.created_at,
        )
        self._session.add(model)
        await self._session.flush()

    async def find_by_user_and_target(
        self,
        user_id: UserId,
        target_type: str,
        target_id: UUID,
    ) -> Reaction | None:
        """Find a reaction by user and target."""
        result = await self._session.execute(
            select(ReactionModel).where(
                ReactionModel.user_id == user_id.value,
                ReactionModel.target_type == target_type,
                ReactionModel.target_id == target_id,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def delete(self, reaction_id: ReactionId) -> None:
        """Delete a reaction by ID."""
        stmt = delete(ReactionModel).where(ReactionModel.id == reaction_id.value)
        await self._session.execute(stmt)
        await self._session.flush()

    async def delete_by_target(self, target_type: str, target_id: UUID) -> None:
        """Delete all reactions for a target."""
        stmt = delete(ReactionModel).where(
            ReactionModel.target_type == target_type,
            ReactionModel.target_id == target_id,
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def count_by_target(self, target_type: str, target_id: UUID) -> int:
        """Count reactions for a target."""
        result = await self._session.execute(
            select(func.count(ReactionModel.id)).where(
                ReactionModel.target_type == target_type,
                ReactionModel.target_id == target_id,
            )
        )
        return result.scalar_one()

    async def list_users_by_target(
        self,
        target_type: str,
        target_id: UUID,
        limit: int = 100,
    ) -> list[UserId]:
        """List users who reacted to a target."""
        result = await self._session.execute(
            select(ReactionModel.user_id)
            .where(
                ReactionModel.target_type == target_type,
                ReactionModel.target_id == target_id,
            )
            .limit(limit)
        )
        user_ids = result.scalars().all()
        return [UserId(uid) for uid in user_ids]

    async def count_by_user_since(self, user_id: UserId, since: datetime) -> int:
        """Count reactions created by a user since a given time."""
        result = await self._session.execute(
            select(func.count(ReactionModel.id)).where(
                ReactionModel.user_id == user_id.value,
                ReactionModel.created_at >= since,
            )
        )
        return result.scalar_one()

    async def delete_by_post_cascade(self, post_id: PostId) -> None:
        """Delete all reactions for a post and its comments."""
        # Delete reactions on the post itself
        stmt1 = delete(ReactionModel).where(
            ReactionModel.target_type == "post",
            ReactionModel.target_id == post_id.value,
        )
        await self._session.execute(stmt1)

        # Delete reactions on comments of the post
        comment_ids_stmt = select(CommentModel.id).where(CommentModel.post_id == post_id.value)
        comment_ids_result = await self._session.execute(comment_ids_stmt)
        comment_ids = comment_ids_result.scalars().all()

        if comment_ids:
            stmt2 = delete(ReactionModel).where(
                ReactionModel.target_type == "comment",
                ReactionModel.target_id.in_(comment_ids),
            )
            await self._session.execute(stmt2)

        await self._session.flush()

    def _to_entity(self, model: ReactionModel) -> Reaction:
        """Convert SQLAlchemy model to domain entity."""
        return Reaction(
            id=ReactionId(model.id),
            user_id=UserId(model.user_id),
            target_type=model.target_type,
            target_id=model.target_id,
            created_at=model.created_at,
        )
