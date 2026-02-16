"""SQLAlchemy implementation of ICourseLevelRequirementRepository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.gamification.domain.entities.course_level_requirement import CourseLevelRequirement
from src.gamification.domain.repositories.course_level_requirement_repository import (
    ICourseLevelRequirementRepository,
)
from src.gamification.infrastructure.persistence.models import CourseLevelRequirementModel


class SqlAlchemyCourseLevelRequirementRepository(ICourseLevelRequirementRepository):
    """SQLAlchemy implementation of ICourseLevelRequirementRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, requirement: CourseLevelRequirement) -> None:
        existing = await self._session.get(CourseLevelRequirementModel, requirement.id)

        if existing is None:
            model = CourseLevelRequirementModel(
                id=requirement.id,
                community_id=requirement.community_id,
                course_id=requirement.course_id,
                minimum_level=requirement.minimum_level,
            )
            self._session.add(model)
        else:
            existing.minimum_level = requirement.minimum_level

        await self._session.flush()

    async def get_by_community_and_course(
        self, community_id: UUID, course_id: UUID
    ) -> CourseLevelRequirement | None:
        stmt = select(CourseLevelRequirementModel).where(
            CourseLevelRequirementModel.community_id == community_id,
            CourseLevelRequirementModel.course_id == course_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def delete(self, community_id: UUID, course_id: UUID) -> None:
        stmt = select(CourseLevelRequirementModel).where(
            CourseLevelRequirementModel.community_id == community_id,
            CourseLevelRequirementModel.course_id == course_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is not None:
            await self._session.delete(model)
            await self._session.flush()

    def _to_entity(self, model: CourseLevelRequirementModel) -> CourseLevelRequirement:
        return CourseLevelRequirement(
            id=model.id,
            community_id=model.community_id,
            course_id=model.course_id,
            minimum_level=model.minimum_level,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
