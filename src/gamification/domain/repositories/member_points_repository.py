"""MemberPoints repository interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from src.gamification.domain.entities.member_points import MemberPoints
from src.gamification.domain.value_objects.leaderboard_period import LeaderboardPeriod


@dataclass(frozen=True)
class LeaderboardEntry:
    """A single ranked member in a leaderboard."""

    rank: int
    user_id: UUID
    display_name: str
    avatar_url: str | None
    level: int
    points: int


@dataclass(frozen=True)
class LeaderboardResult:
    """Result of a leaderboard query — top N entries + optional 'your rank'."""

    entries: list[LeaderboardEntry]
    your_rank: LeaderboardEntry | None


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

    @abstractmethod
    async def get_leaderboard(
        self,
        community_id: UUID,
        period: LeaderboardPeriod,
        limit: int,
        current_user_id: UUID,
    ) -> LeaderboardResult: ...

    @abstractmethod
    async def get_leaderboard_widget(
        self,
        community_id: UUID,
        limit: int,
    ) -> list[LeaderboardEntry]: ...
