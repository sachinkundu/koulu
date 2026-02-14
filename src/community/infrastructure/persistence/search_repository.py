"""SQLAlchemy implementation of search repository using PostgreSQL Full-Text Search."""

from typing import Any

from sqlalchemy import func as sa_func
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.community.application.dtos.search_results import MemberSearchEntry, PostSearchEntry
from src.community.domain.repositories.search_repository import ISearchRepository
from src.community.domain.value_objects import CommunityId
from src.community.infrastructure.persistence.models import (
    CategoryModel,
    CommentModel,
    CommunityMemberModel,
    PostModel,
    ReactionModel,
)
from src.identity.infrastructure.persistence.models import ProfileModel


class SqlAlchemySearchRepository(ISearchRepository):
    """SQLAlchemy implementation of ISearchRepository using PostgreSQL FTS."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with database session."""
        self._session = session

    def _build_member_filters(
        self,
        community_id: CommunityId,
        query: str,
    ) -> list[Any]:
        """Build common WHERE filters for member search queries."""
        tsquery = sa_func.plainto_tsquery("english", query)
        return [
            CommunityMemberModel.community_id == community_id.value,
            CommunityMemberModel.is_active.is_(True),
            or_(
                ProfileModel.search_vector.op("@@")(tsquery),
                ProfileModel.username.ilike(f"%{query}%"),
            ),
        ]

    def _build_member_base_query(
        self,
        community_id: CommunityId,
        query: str,
    ) -> Any:
        """Build the base SELECT FROM with JOINs for member search."""
        filters = self._build_member_filters(community_id, query)
        return (
            select(CommunityMemberModel)
            .outerjoin(
                ProfileModel,
                CommunityMemberModel.user_id == ProfileModel.user_id,
            )
            .where(*filters)
        )

    async def search_members(
        self,
        community_id: CommunityId,
        query: str,
        limit: int = 10,
        offset: int = 0,
    ) -> list[MemberSearchEntry]:
        """Search community members by display name, username, or bio."""
        filters = self._build_member_filters(community_id, query)

        stmt = (
            select(
                CommunityMemberModel.user_id,
                CommunityMemberModel.role,
                CommunityMemberModel.joined_at,
                ProfileModel.display_name,
                ProfileModel.username,
                ProfileModel.avatar_url,
                ProfileModel.bio,
            )
            .outerjoin(
                ProfileModel,
                CommunityMemberModel.user_id == ProfileModel.user_id,
            )
            .where(*filters)
            .order_by(ProfileModel.display_name.asc().nulls_last())
            .offset(offset)
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        rows = result.all()

        return [
            MemberSearchEntry(
                user_id=row.user_id,
                display_name=row.display_name,
                username=row.username,
                avatar_url=row.avatar_url,
                role=row.role.lower() if row.role else "member",
                bio=row.bio,
                joined_at=row.joined_at,
            )
            for row in rows
        ]

    async def count_members(
        self,
        community_id: CommunityId,
        query: str,
    ) -> int:
        """Count matching members."""
        filters = self._build_member_filters(community_id, query)

        stmt = (
            select(sa_func.count())
            .select_from(CommunityMemberModel)
            .outerjoin(
                ProfileModel,
                CommunityMemberModel.user_id == ProfileModel.user_id,
            )
            .where(*filters)
        )

        result = await self._session.execute(stmt)
        return result.scalar_one()

    def _build_post_filters(
        self,
        community_id: CommunityId,
        query: str,
    ) -> list[Any]:
        """Build common WHERE filters for post search queries."""
        tsquery = sa_func.plainto_tsquery("english", query)
        return [
            PostModel.community_id == community_id.value,
            PostModel.is_deleted.is_(False),
            PostModel.search_vector.op("@@")(tsquery),
        ]

    async def search_posts(
        self,
        community_id: CommunityId,
        query: str,
        limit: int = 10,
        offset: int = 0,
    ) -> list[PostSearchEntry]:
        """Search community posts by title or content."""
        filters = self._build_post_filters(community_id, query)

        like_count_subquery = (
            select(sa_func.count())
            .select_from(ReactionModel)
            .where(
                ReactionModel.target_type == "post",
                ReactionModel.target_id == PostModel.id,
            )
            .correlate(PostModel)
            .scalar_subquery()
            .label("like_count")
        )

        comment_count_subquery = (
            select(sa_func.count())
            .select_from(CommentModel)
            .where(
                CommentModel.post_id == PostModel.id,
                CommentModel.is_deleted.is_(False),
            )
            .correlate(PostModel)
            .scalar_subquery()
            .label("comment_count")
        )

        stmt = (
            select(
                PostModel.id,
                PostModel.title,
                sa_func.left(PostModel.content, 200).label("body_snippet"),
                ProfileModel.display_name.label("author_name"),
                ProfileModel.avatar_url.label("author_avatar_url"),
                CategoryModel.name.label("category_name"),
                CategoryModel.emoji.label("category_emoji"),
                PostModel.created_at,
                like_count_subquery,
                comment_count_subquery,
            )
            .outerjoin(
                ProfileModel,
                PostModel.author_id == ProfileModel.user_id,
            )
            .outerjoin(
                CategoryModel,
                PostModel.category_id == CategoryModel.id,
            )
            .where(*filters)
            .order_by(PostModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        rows = result.all()

        return [
            PostSearchEntry(
                id=row.id,
                title=row.title,
                body_snippet=row.body_snippet or "",
                author_name=row.author_name,
                author_avatar_url=row.author_avatar_url,
                category_name=row.category_name,
                category_emoji=row.category_emoji,
                created_at=row.created_at,
                like_count=row.like_count,
                comment_count=row.comment_count,
            )
            for row in rows
        ]

    async def count_posts(
        self,
        community_id: CommunityId,
        query: str,
    ) -> int:
        """Count matching posts."""
        filters = self._build_post_filters(community_id, query)

        stmt = select(sa_func.count()).select_from(PostModel).where(*filters)

        result = await self._session.execute(stmt)
        return result.scalar_one()
