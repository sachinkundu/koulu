"""SQLAlchemy implementation of ILevelConfigRepository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.gamification.domain.entities.level_configuration import (
    LevelConfiguration,
    LevelDefinition,
)
from src.gamification.domain.repositories.level_config_repository import ILevelConfigRepository
from src.gamification.infrastructure.persistence.models import LevelConfigurationModel


class SqlAlchemyLevelConfigRepository(ILevelConfigRepository):
    """SQLAlchemy implementation of ILevelConfigRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_community(self, community_id: UUID) -> LevelConfiguration | None:
        stmt = select(LevelConfigurationModel).where(
            LevelConfigurationModel.community_id == community_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def save(self, config: LevelConfiguration) -> None:
        existing = await self._session.get(LevelConfigurationModel, config.id)

        levels_data = [
            {"level": ld.level, "name": ld.name, "threshold": ld.threshold}
            for ld in config.levels
        ]

        if existing is None:
            model = LevelConfigurationModel(
                id=config.id,
                community_id=config.community_id,
                levels=levels_data,
            )
            self._session.add(model)
        else:
            existing.levels = levels_data

        await self._session.flush()

    def _to_entity(self, model: LevelConfigurationModel) -> LevelConfiguration:
        levels = [
            LevelDefinition(
                level=ld["level"],
                name=ld["name"],
                threshold=ld["threshold"],
            )
            for ld in model.levels
        ]
        return LevelConfiguration(
            id=model.id,
            community_id=model.community_id,
            levels=levels,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
