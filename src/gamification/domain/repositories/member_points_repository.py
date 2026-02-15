"""MemberPoints repository interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.gamification.domain.entities.member_points import MemberPoints


class IMemberPointsRepository(ABC):
    """Interface for MemberPoints persistence."""

    @abstractmethod
    async def save(self, member_points: MemberPoints) -> None: ...

    @abstractmethod
    async def get_by_community_and_user(
        self, community_id: UUID, user_id: UUID
    ) -> MemberPoints | None: ...

    @abstractmethod
    async def list_by_community(self, community_id: UUID) -> list[MemberPoints]: ...
