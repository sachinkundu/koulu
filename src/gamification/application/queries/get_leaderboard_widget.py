"""GetLeaderboardWidget query and handler."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from src.gamification.domain.repositories.member_points_repository import (
    IMemberPointsRepository,
    LeaderboardEntry,
)


@dataclass(frozen=True)
class GetLeaderboardWidgetQuery:
    community_id: UUID
    current_user_id: UUID


@dataclass(frozen=True)
class LeaderboardWidgetResult:
    entries: list[LeaderboardEntry]
    last_updated: datetime


class GetLeaderboardWidgetHandler:
    def __init__(self, member_points_repo: IMemberPointsRepository) -> None:
        self._repo = member_points_repo

    async def handle(self, query: GetLeaderboardWidgetQuery) -> LeaderboardWidgetResult:
        limit = 5
        entries = await self._repo.get_leaderboard_widget(query.community_id, limit)
        return LeaderboardWidgetResult(
            entries=entries,
            last_updated=datetime.now(UTC),
        )
