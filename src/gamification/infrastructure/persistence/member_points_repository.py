"""SQLAlchemy implementation of IMemberPointsRepository."""

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.gamification.domain.entities.member_points import MemberPoints
from src.gamification.domain.repositories.member_points_repository import (
    IMemberPointsRepository,
    LeaderboardEntry,
    LeaderboardResult,
)
from src.gamification.domain.value_objects.leaderboard_period import LeaderboardPeriod
from src.gamification.domain.value_objects.point_source import PointSource
from src.gamification.domain.value_objects.point_transaction import PointTransaction
from src.gamification.infrastructure.persistence.models import (
    MemberPointsModel,
    PointTransactionModel,
)


class SqlAlchemyMemberPointsRepository(IMemberPointsRepository):
    """SQLAlchemy implementation of IMemberPointsRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, member_points: MemberPoints) -> None:
        existing = await self._session.get(MemberPointsModel, member_points.id)

        if existing is None:
            model = MemberPointsModel(
                id=member_points.id,
                community_id=member_points.community_id,
                user_id=member_points.user_id,
                total_points=member_points.total_points,
                current_level=member_points.current_level,
            )
            # Add transactions
            for txn in member_points.transactions:
                model.transactions.append(
                    PointTransactionModel(
                        points=txn.points,
                        source=txn.source.source_name,
                        source_id=txn.source_id,
                        created_at=txn.created_at,
                    )
                )
            self._session.add(model)
        else:
            existing.total_points = member_points.total_points
            existing.current_level = member_points.current_level
            # Add only NEW transactions (those not yet persisted)
            existing_txn_count = len(existing.transactions)
            for txn in member_points.transactions[existing_txn_count:]:
                existing.transactions.append(
                    PointTransactionModel(
                        points=txn.points,
                        source=txn.source.source_name,
                        source_id=txn.source_id,
                        created_at=txn.created_at,
                    )
                )

        await self._session.flush()

    async def get_by_community_and_user(
        self, community_id: UUID, user_id: UUID
    ) -> MemberPoints | None:
        stmt = (
            select(MemberPointsModel)
            .where(
                MemberPointsModel.community_id == community_id,
                MemberPointsModel.user_id == user_id,
            )
            .options(selectinload(MemberPointsModel.transactions))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def list_by_community(self, community_id: UUID) -> list[MemberPoints]:
        stmt = (
            select(MemberPointsModel)
            .where(MemberPointsModel.community_id == community_id)
            .options(selectinload(MemberPointsModel.transactions))
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    def _to_entity(self, model: MemberPointsModel) -> MemberPoints:
        transactions = [
            PointTransaction(
                points=t.points,
                source=self._source_name_to_enum(t.source),
                source_id=t.source_id,
                created_at=t.created_at,
            )
            for t in model.transactions
        ]
        return MemberPoints(
            id=model.id,
            community_id=model.community_id,
            user_id=model.user_id,
            total_points=model.total_points,
            current_level=model.current_level,
            created_at=model.created_at,
            updated_at=model.updated_at,
            transactions=transactions,
        )

    async def get_leaderboard(
        self,
        community_id: UUID,
        period: LeaderboardPeriod,
        limit: int,
        current_user_id: UUID,
    ) -> LeaderboardResult:
        if period == LeaderboardPeriod.ALL_TIME:
            return await self._get_alltime_leaderboard(community_id, limit, current_user_id)
        return await self._get_period_leaderboard(community_id, period, limit, current_user_id)

    async def _get_period_leaderboard(
        self,
        community_id: UUID,
        period: LeaderboardPeriod,
        limit: int,
        current_user_id: UUID,
    ) -> LeaderboardResult:
        assert period.interval_hours is not None
        cutoff = datetime.now(UTC) - timedelta(hours=period.interval_hours)

        sql = text("""
            WITH period_points AS (
                SELECT
                    mp.id AS mp_id,
                    mp.user_id,
                    mp.current_level,
                    GREATEST(0, COALESCE(SUM(pt.points), 0)) AS net_points
                FROM member_points mp
                LEFT JOIN point_transactions pt
                    ON pt.member_points_id = mp.id
                    AND pt.created_at >= :cutoff
                WHERE mp.community_id = :community_id
                GROUP BY mp.id, mp.user_id, mp.current_level
            ),
            ranked AS (
                SELECT
                    pp.user_id,
                    pp.current_level,
                    pp.net_points,
                    COALESCE(p.display_name, 'Member') AS display_name,
                    p.avatar_url,
                    ROW_NUMBER() OVER (
                        ORDER BY pp.net_points DESC, COALESCE(p.display_name, 'Member') ASC
                    ) AS rank
                FROM period_points pp
                LEFT JOIN profiles p ON p.user_id = pp.user_id
            )
            SELECT user_id, display_name, avatar_url, current_level, net_points, rank
            FROM ranked
            WHERE rank <= :limit OR user_id = :current_user_id
            ORDER BY rank
        """)

        result = await self._session.execute(
            sql,
            {
                "community_id": community_id,
                "cutoff": cutoff,
                "limit": limit,
                "current_user_id": current_user_id,
            },
        )
        rows = result.fetchall()
        return self._build_leaderboard_result(rows, limit, current_user_id)

    async def _get_alltime_leaderboard(
        self,
        community_id: UUID,
        limit: int,
        current_user_id: UUID,
    ) -> LeaderboardResult:
        sql = text("""
            WITH ranked AS (
                SELECT
                    mp.user_id,
                    mp.current_level,
                    mp.total_points AS net_points,
                    COALESCE(p.display_name, 'Member') AS display_name,
                    p.avatar_url,
                    ROW_NUMBER() OVER (
                        ORDER BY mp.total_points DESC, COALESCE(p.display_name, 'Member') ASC
                    ) AS rank
                FROM member_points mp
                LEFT JOIN profiles p ON p.user_id = mp.user_id
                WHERE mp.community_id = :community_id
            )
            SELECT user_id, display_name, avatar_url, current_level, net_points, rank
            FROM ranked
            WHERE rank <= :limit OR user_id = :current_user_id
            ORDER BY rank
        """)

        result = await self._session.execute(
            sql,
            {
                "community_id": community_id,
                "limit": limit,
                "current_user_id": current_user_id,
            },
        )
        rows = result.fetchall()
        return self._build_leaderboard_result(rows, limit, current_user_id)

    @staticmethod
    def _build_leaderboard_result(
        rows: Sequence[Row[Any]],
        limit: int,
        current_user_id: UUID,
    ) -> LeaderboardResult:
        entries: list[LeaderboardEntry] = []
        your_rank: LeaderboardEntry | None = None
        user_in_top = False

        for row in rows:
            entry = LeaderboardEntry(
                rank=row.rank,
                user_id=row.user_id,
                display_name=row.display_name,
                avatar_url=row.avatar_url,
                level=row.current_level,
                points=row.net_points,
            )
            if row.rank <= limit:
                entries.append(entry)
                if row.user_id == current_user_id:
                    user_in_top = True
            else:
                your_rank = entry

        if not user_in_top and your_rank is None:
            # Current user has no member_points row at all
            pass

        return LeaderboardResult(entries=entries, your_rank=your_rank)

    @staticmethod
    def _source_name_to_enum(source_name: str) -> PointSource:
        """Map source_name string to PointSource enum."""
        for ps in PointSource:
            if ps.source_name == source_name:
                return ps
        raise ValueError(f"Unknown point source: {source_name}")
