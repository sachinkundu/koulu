"""SQLAlchemy implementation of post repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.community.domain.entities import Post
from src.community.domain.repositories import IPostRepository
from src.community.domain.value_objects import (
    CategoryId,
    CommunityId,
    PostContent,
    PostId,
    PostTitle,
)
from src.community.infrastructure.persistence.models import PostModel
from src.identity.domain.value_objects import UserId


class SqlAlchemyPostRepository(IPostRepository):
    """SQLAlchemy implementation of IPostRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with database session."""
        self._session = session

    async def save(self, post: Post) -> None:
        """Save a post (create or update)."""
        # Check if post exists
        existing = await self._session.get(PostModel, post.id.value)

        if existing is None:
            # Create new post
            post_model = PostModel(
                id=post.id.value,
                community_id=post.community_id.value,
                author_id=post.author_id.value,
                category_id=post.category_id.value,
                title=post.title.value,
                content=post.content.value,
                image_url=post.image_url,
                is_pinned=post.is_pinned,
                pinned_at=post.pinned_at,
                is_locked=post.is_locked,
                is_deleted=post.is_deleted,
                created_at=post.created_at,
                updated_at=post.updated_at,
                edited_at=post.edited_at,
            )
            self._session.add(post_model)
        else:
            # Update existing post
            existing.community_id = post.community_id.value
            existing.author_id = post.author_id.value
            existing.category_id = post.category_id.value
            existing.title = post.title.value
            existing.content = post.content.value
            existing.image_url = post.image_url
            existing.is_pinned = post.is_pinned
            existing.pinned_at = post.pinned_at
            existing.is_locked = post.is_locked
            existing.is_deleted = post.is_deleted
            existing.updated_at = post.updated_at
            existing.edited_at = post.edited_at

        await self._session.flush()

    async def get_by_id(self, post_id: PostId) -> Post | None:
        """Get a post by ID (excluding deleted posts)."""
        result = await self._session.execute(
            select(PostModel).where(PostModel.id == post_id.value, PostModel.is_deleted == False)  # noqa: E712
        )
        post_model = result.scalar_one_or_none()

        if post_model is None:
            return None

        return self._to_entity(post_model)

    async def get_by_id_include_deleted(self, post_id: PostId) -> Post | None:
        """Get a post by ID including deleted posts."""
        result = await self._session.execute(select(PostModel).where(PostModel.id == post_id.value))
        post_model = result.scalar_one_or_none()

        if post_model is None:
            return None

        return self._to_entity(post_model)

    async def list_by_community(
        self,
        community_id: CommunityId,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Post]:
        """List posts in a community (excluding deleted)."""
        result = await self._session.execute(
            select(PostModel)
            .where(PostModel.community_id == community_id.value, PostModel.is_deleted == False)  # noqa: E712
            .order_by(PostModel.is_pinned.desc(), PostModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        post_models = result.scalars().all()

        return [self._to_entity(model) for model in post_models]

    async def delete(self, post_id: PostId) -> None:
        """Delete a post by ID (hard delete)."""
        post_model = await self._session.get(PostModel, post_id.value)
        if post_model is not None:
            await self._session.delete(post_model)
            await self._session.flush()

    def _to_entity(self, model: PostModel) -> Post:
        """Convert SQLAlchemy model to domain entity."""
        return Post(
            id=PostId(value=model.id),
            community_id=CommunityId(value=model.community_id),
            author_id=UserId(value=model.author_id),
            category_id=CategoryId(value=model.category_id),
            title=PostTitle(model.title),
            content=PostContent(model.content),
            image_url=model.image_url,
            is_pinned=model.is_pinned,
            pinned_at=model.pinned_at,
            is_locked=model.is_locked,
            is_deleted=model.is_deleted,
            created_at=model.created_at,
            updated_at=model.updated_at,
            edited_at=model.edited_at,
        )
