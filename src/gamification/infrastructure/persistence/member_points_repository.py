"""SQLAlchemy implementation of IMemberPointsRepository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.gamification.domain.entities.member_points import MemberPoints
from src.gamification.domain.repositories.member_points_repository import IMemberPointsRepository
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

    @staticmethod
    def _source_name_to_enum(source_name: str) -> PointSource:
        """Map source_name string to PointSource enum."""
        for ps in PointSource:
            if ps.source_name == source_name:
                return ps
        raise ValueError(f"Unknown point source: {source_name}")
