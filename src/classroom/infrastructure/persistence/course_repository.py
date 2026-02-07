"""SQLAlchemy implementation of course repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.classroom.domain.entities import Course
from src.classroom.domain.repositories import ICourseRepository
from src.classroom.domain.value_objects import (
    CourseDescription,
    CourseId,
    CourseTitle,
    CoverImageUrl,
    EstimatedDuration,
)
from src.classroom.infrastructure.persistence.models import CourseModel
from src.identity.domain.value_objects import UserId


class SqlAlchemyCourseRepository(ICourseRepository):
    """SQLAlchemy implementation of ICourseRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with database session."""
        self._session = session

    async def save(self, course: Course) -> None:
        """Save a course (create or update)."""
        existing = await self._session.get(CourseModel, course.id.value)

        if existing is None:
            # Create new course
            course_model = CourseModel(
                id=course.id.value,
                instructor_id=course.instructor_id.value,
                title=course.title.value,
                description=course.description.value if course.description else None,
                cover_image_url=course.cover_image_url.value if course.cover_image_url else None,
                estimated_duration=(
                    course.estimated_duration.value if course.estimated_duration else None
                ),
                is_deleted=course.is_deleted,
                deleted_at=course.deleted_at,
                created_at=course.created_at,
                updated_at=course.updated_at,
            )
            self._session.add(course_model)
        else:
            # Update existing course
            existing.instructor_id = course.instructor_id.value
            existing.title = course.title.value
            existing.description = course.description.value if course.description else None
            existing.cover_image_url = (
                course.cover_image_url.value if course.cover_image_url else None
            )
            existing.estimated_duration = (
                course.estimated_duration.value if course.estimated_duration else None
            )
            existing.is_deleted = course.is_deleted
            existing.deleted_at = course.deleted_at
            existing.updated_at = course.updated_at

        await self._session.flush()

    async def get_by_id(self, course_id: CourseId) -> Course | None:
        """Get a course by ID (excluding deleted)."""
        result = await self._session.execute(
            select(CourseModel).where(
                CourseModel.id == course_id.value,
                CourseModel.is_deleted == False,  # noqa: E712
            )
        )
        course_model = result.scalar_one_or_none()

        if course_model is None:
            return None

        return self._to_entity(course_model)

    async def get_by_id_include_deleted(self, course_id: CourseId) -> Course | None:
        """Get a course by ID including deleted courses."""
        result = await self._session.execute(
            select(CourseModel).where(CourseModel.id == course_id.value)
        )
        course_model = result.scalar_one_or_none()

        if course_model is None:
            return None

        return self._to_entity(course_model)

    async def list_all(
        self,
        include_deleted: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Course]:
        """List all courses."""
        query = select(CourseModel)

        if not include_deleted:
            query = query.where(CourseModel.is_deleted == False)  # noqa: E712

        query = query.order_by(CourseModel.created_at.desc()).limit(limit).offset(offset)

        result = await self._session.execute(query)
        course_models = result.scalars().all()

        return [self._to_entity(model) for model in course_models]

    def _to_entity(self, model: CourseModel) -> Course:
        """Convert SQLAlchemy model to domain entity."""
        return Course(
            id=CourseId(value=model.id),
            instructor_id=UserId(value=model.instructor_id),
            title=CourseTitle(model.title),
            description=CourseDescription(model.description) if model.description else None,
            cover_image_url=CoverImageUrl(model.cover_image_url) if model.cover_image_url else None,
            estimated_duration=(
                EstimatedDuration(model.estimated_duration) if model.estimated_duration else None
            ),
            is_deleted=model.is_deleted,
            deleted_at=model.deleted_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
