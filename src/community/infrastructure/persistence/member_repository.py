"""SQLAlchemy implementation of member repository."""

from sqlalchemy import func as sa_func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.community.application.dtos.member_directory_entry import MemberDirectoryEntry
from src.community.domain.entities import CommunityMember
from src.community.domain.repositories import IMemberRepository
from src.community.domain.value_objects import CommunityId, MemberRole
from src.community.infrastructure.persistence.models import CommunityMemberModel
from src.identity.domain.value_objects import UserId
from src.identity.infrastructure.persistence.models import ProfileModel


class SqlAlchemyMemberRepository(IMemberRepository):
    """SQLAlchemy implementation of IMemberRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with database session."""
        self._session = session

    async def save(self, member: CommunityMember) -> None:
        """Save a community member (create or update)."""
        # Check if member exists
        existing = await self._session.get(
            CommunityMemberModel,
            {"user_id": member.user_id.value, "community_id": member.community_id.value},
        )

        if existing is None:
            # Create new member
            member_model = CommunityMemberModel(
                user_id=member.user_id.value,
                community_id=member.community_id.value,
                role=member.role.value,
                joined_at=member.joined_at,
                is_active=member.is_active,
            )
            self._session.add(member_model)
        else:
            # Update existing member
            existing.role = member.role.value
            existing.is_active = member.is_active

        await self._session.flush()

    async def get_by_user_and_community(
        self,
        user_id: UserId,
        community_id: CommunityId,
    ) -> CommunityMember | None:
        """Get a member by user ID and community ID (active only)."""
        result = await self._session.execute(
            select(CommunityMemberModel).where(
                CommunityMemberModel.user_id == user_id.value,
                CommunityMemberModel.community_id == community_id.value,
                CommunityMemberModel.is_active.is_(True),
            )
        )
        member_model = result.scalar_one_or_none()

        if member_model is None:
            return None

        return self._to_entity(member_model)

    async def exists(
        self,
        user_id: UserId,
        community_id: CommunityId,
    ) -> bool:
        """Check if a user is a member of a community (active only)."""
        result = await self._session.execute(
            select(CommunityMemberModel.user_id).where(
                CommunityMemberModel.user_id == user_id.value,
                CommunityMemberModel.community_id == community_id.value,
                CommunityMemberModel.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none() is not None

    async def list_by_community(
        self,
        community_id: CommunityId,
    ) -> list[CommunityMember]:
        """List all members in a community (active only)."""
        result = await self._session.execute(
            select(CommunityMemberModel)
            .where(
                CommunityMemberModel.community_id == community_id.value,
                CommunityMemberModel.is_active.is_(True),
            )
            .order_by(CommunityMemberModel.joined_at)
        )
        member_models = result.scalars().all()

        return [self._to_entity(model) for model in member_models]

    async def delete(
        self,
        user_id: UserId,
        community_id: CommunityId,
    ) -> None:
        """Delete a community member (hard delete)."""
        member_model = await self._session.get(
            CommunityMemberModel,
            {"user_id": user_id.value, "community_id": community_id.value},
        )
        if member_model is not None:
            await self._session.delete(member_model)
            await self._session.flush()

    async def list_directory(
        self,
        community_id: CommunityId,
        sort: str = "most_recent",
        limit: int = 20,
        offset: int = 0,
    ) -> list[MemberDirectoryEntry]:
        """List community members with profile data via JOIN."""
        query = (
            select(
                CommunityMemberModel.user_id,
                CommunityMemberModel.role,
                CommunityMemberModel.joined_at,
                ProfileModel.display_name,
                ProfileModel.avatar_url,
                ProfileModel.bio,
            )
            .outerjoin(
                ProfileModel,
                CommunityMemberModel.user_id == ProfileModel.user_id,
            )
            .where(
                CommunityMemberModel.community_id == community_id.value,
                CommunityMemberModel.is_active.is_(True),
            )
        )

        if sort == "alphabetical":
            query = query.order_by(ProfileModel.display_name.asc().nulls_last())
        else:
            query = query.order_by(CommunityMemberModel.joined_at.desc())

        query = query.offset(offset).limit(limit)

        result = await self._session.execute(query)
        rows = result.all()

        return [
            MemberDirectoryEntry(
                user_id=row.user_id,
                display_name=row.display_name,
                avatar_url=row.avatar_url,
                role=row.role.lower() if row.role else "member",
                bio=row.bio,
                joined_at=row.joined_at,
            )
            for row in rows
        ]

    async def count_directory(
        self,
        community_id: CommunityId,
    ) -> int:
        """Count active members in a community."""
        result = await self._session.execute(
            select(sa_func.count())
            .select_from(CommunityMemberModel)
            .where(
                CommunityMemberModel.community_id == community_id.value,
                CommunityMemberModel.is_active.is_(True),
            )
        )
        return result.scalar_one()

    def _to_entity(self, model: CommunityMemberModel) -> CommunityMember:
        """Convert SQLAlchemy model to domain entity."""
        return CommunityMember(
            id=UserId(value=model.user_id),
            user_id=UserId(value=model.user_id),
            community_id=CommunityId(value=model.community_id),
            role=MemberRole(model.role),
            joined_at=model.joined_at,
            is_active=model.is_active,
        )
