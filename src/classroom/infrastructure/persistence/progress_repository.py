"""SQLAlchemy implementation of progress repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.classroom.domain.entities.lesson_completion import LessonCompletion
from src.classroom.domain.entities.progress import Progress
from src.classroom.domain.repositories.progress_repository import IProgressRepository
from src.classroom.domain.value_objects.course_id import CourseId
from src.classroom.domain.value_objects.lesson_id import LessonId
from src.classroom.domain.value_objects.progress_id import ProgressId
from src.classroom.infrastructure.persistence.models import (
    LessonCompletionModel,
    ProgressModel,
)
from src.identity.domain.value_objects import UserId


class SqlAlchemyProgressRepository(IProgressRepository):
    """SQLAlchemy implementation of IProgressRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, progress: Progress) -> None:
        """Save a progress record (create or update)."""
        existing = await self._session.get(
            ProgressModel,
            progress.id.value,
            options=[selectinload(ProgressModel.completions)],
        )

        if existing is None:
            model = self._to_model(progress)
            self._session.add(model)
        else:
            existing.last_accessed_lesson_id = (
                progress.last_accessed_lesson_id.value if progress.last_accessed_lesson_id else None
            )
            existing.last_accessed_at = progress.last_accessed_at
            existing.updated_at = progress.updated_at
            self._sync_completions(existing, progress)

        await self._session.flush()

    def _sync_completions(self, model: ProgressModel, progress: Progress) -> None:
        """Synchronize completion models with domain entity."""
        existing_by_lesson = {c.lesson_id: c for c in model.completions}
        domain_lesson_ids = {c.lesson_id.value for c in progress.completions}

        # Add new completions
        for completion in progress.completions:
            if completion.lesson_id.value not in existing_by_lesson:
                model.completions.append(
                    LessonCompletionModel(
                        id=completion.id.value,
                        progress_id=progress.id.value,
                        lesson_id=completion.lesson_id.value,
                        completed_at=completion.completed_at,
                    )
                )

        # Remove completions no longer in domain
        to_remove = [c for c in model.completions if c.lesson_id not in domain_lesson_ids]
        for c in to_remove:
            model.completions.remove(c)

    async def get_by_id(self, progress_id: ProgressId) -> Progress | None:
        result = await self._session.execute(
            select(ProgressModel)
            .options(selectinload(ProgressModel.completions))
            .where(ProgressModel.id == progress_id.value)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_user_and_course(self, user_id: UserId, course_id: CourseId) -> Progress | None:
        result = await self._session.execute(
            select(ProgressModel)
            .options(selectinload(ProgressModel.completions))
            .where(
                ProgressModel.user_id == user_id.value,
                ProgressModel.course_id == course_id.value,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_user(self, user_id: UserId) -> list[Progress]:
        result = await self._session.execute(
            select(ProgressModel)
            .options(selectinload(ProgressModel.completions))
            .where(ProgressModel.user_id == user_id.value)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    def _to_entity(self, model: ProgressModel) -> Progress:
        completions = [
            LessonCompletion(
                id=LessonId(value=c.id),
                lesson_id=LessonId(value=c.lesson_id),
                completed_at=c.completed_at,
            )
            for c in model.completions
        ]

        return Progress(
            id=ProgressId(value=model.id),
            user_id=UserId(value=model.user_id),
            course_id=CourseId(value=model.course_id),
            started_at=model.started_at,
            last_accessed_lesson_id=(
                LessonId(value=model.last_accessed_lesson_id)
                if model.last_accessed_lesson_id
                else None
            ),
            last_accessed_at=model.last_accessed_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
            _completions=completions,
        )

    def _to_model(self, progress: Progress) -> ProgressModel:
        model = ProgressModel(
            id=progress.id.value,
            user_id=progress.user_id.value,
            course_id=progress.course_id.value,
            started_at=progress.started_at,
            last_accessed_lesson_id=(
                progress.last_accessed_lesson_id.value if progress.last_accessed_lesson_id else None
            ),
            last_accessed_at=progress.last_accessed_at,
            created_at=progress.created_at,
            updated_at=progress.updated_at,
        )

        for completion in progress.completions:
            model.completions.append(
                LessonCompletionModel(
                    id=completion.id.value,
                    progress_id=progress.id.value,
                    lesson_id=completion.lesson_id.value,
                    completed_at=completion.completed_at,
                )
            )

        return model
