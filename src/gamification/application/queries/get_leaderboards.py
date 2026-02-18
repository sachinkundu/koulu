"""GetLeaderboards query and handler."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from src.gamification.domain.repositories.member_points_repository import (
    IMemberPointsRepository,
    LeaderboardEntry,
)
from src.gamification.domain.value_objects.leaderboard_period import LeaderboardPeriod


@dataclass(frozen=True)
class GetLeaderboardsQuery:
    community_id: UUID
    current_user_id: UUID


@dataclass(frozen=True)
class LeaderboardPeriodResult:
    entries: list[LeaderboardEntry]
    your_rank: LeaderboardEntry | None


@dataclass(frozen=True)
class LeaderboardsResult:
    seven_day: LeaderboardPeriodResult
    thirty_day: LeaderboardPeriodResult
    all_time: LeaderboardPeriodResult
    last_updated: datetime


class GetLeaderboardsHandler:
    def __init__(self, member_points_repo: IMemberPointsRepository) -> None:
        self._repo = member_points_repo

    async def handle(self, query: GetLeaderboardsQuery) -> LeaderboardsResult:
        limit = 10

        seven_day = await self._repo.get_leaderboard(
            query.community_id, LeaderboardPeriod.SEVEN_DAY, limit, query.current_user_id
        )
        thirty_day = await self._repo.get_leaderboard(
            query.community_id, LeaderboardPeriod.THIRTY_DAY, limit, query.current_user_id
        )
        all_time = await self._repo.get_leaderboard(
            query.community_id, LeaderboardPeriod.ALL_TIME, limit, query.current_user_id
        )

        return LeaderboardsResult(
            seven_day=LeaderboardPeriodResult(
                entries=seven_day.entries, your_rank=seven_day.your_rank
            ),
            thirty_day=LeaderboardPeriodResult(
                entries=thirty_day.entries, your_rank=thirty_day.your_rank
            ),
            all_time=LeaderboardPeriodResult(
                entries=all_time.entries, your_rank=all_time.your_rank
            ),
            last_updated=datetime.now(UTC),
        )
