"""SQLAlchemy implementation of comment repository."""

from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.community.domain.entities import Comment
from src.community.domain.repositories import ICommentRepository
from src.community.domain.value_objects import CommentContent, CommentId, PostId
from src.community.infrastructure.persistence.models import CommentModel
from src.identity.domain.value_objects import UserId


class SqlAlchemyCommentRepository(ICommentRepository):
    """SQLAlchemy implementation of ICommentRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with database session."""
        self._session = session

    async def save(self, comment: Comment) -> None:
        """Save a comment (create or update)."""
        existing = await self._session.get(CommentModel, comment.id.value)

        if existing is None:
            # Create new comment
            model = CommentModel(
                id=comment.id.value,
                post_id=comment.post_id.value,
                author_id=comment.author_id.value,
                parent_comment_id=comment.parent_comment_id.value
                if comment.parent_comment_id
                else None,
                content=str(comment.content),
                is_deleted=comment.is_deleted,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
                edited_at=comment.edited_at,
            )
            self._session.add(model)
        else:
            # Update existing comment
            existing.content = str(comment.content)
            existing.is_deleted = comment.is_deleted
            existing.updated_at = comment.updated_at
            existing.edited_at = comment.edited_at

        await self._session.flush()

    async def get_by_id(self, comment_id: CommentId) -> Comment | None:
        """Get a comment by ID (excluding deleted)."""
        result = await self._session.execute(
            select(CommentModel).where(
                CommentModel.id == comment_id.value,
                CommentModel.is_deleted == False,  # noqa: E712
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_post(
        self,
        post_id: PostId,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Comment]:
        """List comments for a post (excluding deleted, ordered by created_at)."""
        result = await self._session.execute(
            select(CommentModel)
            .where(
                CommentModel.post_id == post_id.value,
                CommentModel.is_deleted == False,  # noqa: E712
            )
            .order_by(CommentModel.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def count_by_post(self, post_id: PostId) -> int:
        """Count comments for a post (excluding deleted)."""
        result = await self._session.execute(
            select(func.count(CommentModel.id)).where(
                CommentModel.post_id == post_id.value,
                CommentModel.is_deleted == False,  # noqa: E712
            )
        )
        return result.scalar_one()

    async def has_replies(self, comment_id: CommentId) -> bool:
        """Check if a comment has any non-deleted replies."""
        result = await self._session.execute(
            select(func.count(CommentModel.id)).where(
                CommentModel.parent_comment_id == comment_id.value,
                CommentModel.is_deleted == False,  # noqa: E712
            )
        )
        count = result.scalar_one()
        return count > 0

    async def delete(self, comment_id: CommentId) -> None:
        """Delete a comment by ID (hard delete)."""
        stmt = delete(CommentModel).where(CommentModel.id == comment_id.value)
        await self._session.execute(stmt)
        await self._session.flush()

    async def delete_by_post(self, post_id: PostId) -> None:
        """Delete all comments for a post (cascade delete)."""
        stmt = delete(CommentModel).where(CommentModel.post_id == post_id.value)
        await self._session.execute(stmt)
        await self._session.flush()

    def _to_entity(self, model: CommentModel) -> Comment:
        """Convert SQLAlchemy model to domain entity."""
        return Comment(
            id=CommentId(model.id),
            post_id=PostId(model.post_id),
            author_id=UserId(model.author_id)
            if model.author_id
            else UserId(UUID("00000000-0000-0000-0000-000000000000")),
            content=CommentContent(model.content),
            parent_comment_id=CommentId(model.parent_comment_id)
            if model.parent_comment_id
            else None,
            is_deleted=model.is_deleted,
            created_at=model.created_at,
            updated_at=model.updated_at,
            edited_at=model.edited_at,
        )
