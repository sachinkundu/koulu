"""SQLAlchemy implementation of post repository."""

import base64
import json

from sqlalchemy import Float, cast, func, literal, select
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
from src.community.infrastructure.persistence.models import (
    CommentModel,
    PostModel,
    ReactionModel,
)
from src.identity.domain.value_objects import UserId


class SqlAlchemyPostRepository(IPostRepository):
    """SQLAlchemy implementation of IPostRepository."""

    MAX_PINNED_DISPLAY = 5

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
            select(PostModel).where(PostModel.id == post_id.value, PostModel.is_deleted.is_(False))
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
        category_id: CategoryId | None = None,
        limit: int = 20,
        offset: int = 0,
        sort: str = "new",
        cursor: str | None = None,
    ) -> list[Post]:
        """List posts in a community (excluding deleted)."""
        # Decode cursor if provided
        effective_offset = offset
        if cursor is not None:
            try:
                cursor_data = json.loads(base64.b64decode(cursor).decode())
                effective_offset = cursor_data.get("offset", 0)
            except (json.JSONDecodeError, ValueError, KeyError):
                pass

        stmt = select(PostModel).where(
            PostModel.community_id == community_id.value,
            PostModel.is_deleted.is_(False),
        )

        if category_id is not None:
            stmt = stmt.where(PostModel.category_id == category_id.value)

        # Build sort order - pinned posts always first
        if sort == "top":
            # Sort by like_count (reaction count) descending
            like_count_subq = (
                select(func.count())
                .select_from(ReactionModel)
                .where(
                    ReactionModel.target_type == "post",
                    ReactionModel.target_id == PostModel.id,
                )
                .correlate(PostModel)
                .scalar_subquery()
            )
            stmt = stmt.order_by(
                PostModel.is_pinned.desc(),
                like_count_subq.desc(),
                PostModel.created_at.desc(),
            )
        elif sort == "hot":
            # Wilson-style hot ranking:
            # (like_count + comment_count * 2) / (hours_since_creation + 2)^1.5
            like_count_subq = (
                select(func.count())
                .select_from(ReactionModel)
                .where(
                    ReactionModel.target_type == "post",
                    ReactionModel.target_id == PostModel.id,
                )
                .correlate(PostModel)
                .scalar_subquery()
            )
            comment_count_subq = (
                select(func.count())
                .select_from(CommentModel)
                .where(
                    CommentModel.post_id == PostModel.id,
                    CommentModel.is_deleted.is_(False),
                )
                .correlate(PostModel)
                .scalar_subquery()
            )
            hours_since = func.extract(
                "epoch",
                func.now() - PostModel.created_at,
            ) / literal(3600)
            hot_score = cast(
                (like_count_subq + comment_count_subq * literal(2)),
                Float,
            ) / func.power(hours_since + literal(2), literal(1.5))
            stmt = stmt.order_by(
                PostModel.is_pinned.desc(),
                hot_score.desc(),
                PostModel.created_at.desc(),
            )
        else:
            # Default "new" sort - by creation date
            stmt = stmt.order_by(
                PostModel.is_pinned.desc(),
                PostModel.created_at.desc(),
            )

        stmt = stmt.limit(limit).offset(effective_offset)

        result = await self._session.execute(stmt)
        post_models = list(result.scalars().all())

        entities = [self._to_entity(model) for model in post_models]

        # Limit pinned posts displayed at top to MAX_PINNED_DISPLAY (5).
        # Excess pinned posts appear in the non-pinned portion in their sort order.
        pinned = [p for p in entities if p.is_pinned]
        if len(pinned) > self.MAX_PINNED_DISPLAY:
            unpinned = [p for p in entities if not p.is_pinned]
            top_pinned = sorted(pinned, key=lambda p: p.pinned_at or p.created_at, reverse=True)[
                : self.MAX_PINNED_DISPLAY
            ]
            overflow = [p for p in pinned if p not in top_pinned]
            entities = top_pinned + overflow + unpinned

        return entities

    async def count_by_category(self, category_id: CategoryId) -> int:
        """Count non-deleted posts in a category."""
        result = await self._session.execute(
            select(func.count())
            .select_from(PostModel)
            .where(
                PostModel.category_id == category_id.value,
                PostModel.is_deleted.is_(False),
            )
        )
        return result.scalar_one()

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
