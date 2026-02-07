"""SQLAlchemy implementation of course repository."""

from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.classroom.domain.entities import Course
from src.classroom.domain.entities.lesson import Lesson
from src.classroom.domain.entities.module import Module
from src.classroom.domain.repositories import ICourseRepository
from src.classroom.domain.value_objects import (
    CourseDescription,
    CourseId,
    CourseTitle,
    CoverImageUrl,
    EstimatedDuration,
    LessonId,
    LessonTitle,
    ModuleDescription,
    ModuleId,
    ModuleTitle,
)
from src.classroom.domain.value_objects.content_type import ContentType
from src.classroom.infrastructure.persistence.models import (
    CourseModel,
    LessonModel,
    ModuleModel,
)
from src.identity.domain.value_objects import UserId


class SqlAlchemyCourseRepository(ICourseRepository):
    """SQLAlchemy implementation of ICourseRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with database session."""
        self._session = session

    async def save(self, course: Course) -> None:
        """Save a course (create or update) with full aggregate persistence."""
        existing = await self._session.get(
            CourseModel,
            course.id.value,
            options=[
                selectinload(CourseModel.modules).selectinload(ModuleModel.lessons),
            ],
        )

        if existing is None:
            # Create new course with modules and lessons
            course_model = self._to_model(course)
            self._session.add(course_model)
        else:
            # Update existing course fields
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

            # Sync modules
            self._sync_modules(existing, course)

        await self._session.flush()

    def _sync_modules(self, course_model: CourseModel, course: Course) -> None:
        """Synchronize module models with domain entity modules."""
        existing_modules = {m.id: m for m in course_model.modules}

        for module in course.all_modules:
            module_model = existing_modules.get(module.id.value)
            if module_model is None:
                # New module
                module_model = self._module_to_model(module, course.id.value)
                course_model.modules.append(module_model)
            else:
                # Update existing module
                module_model.title = module.title.value
                module_model.description = module.description.value if module.description else None
                module_model.position = module.position
                module_model.is_deleted = module.is_deleted
                module_model.deleted_at = module.deleted_at
                module_model.updated_at = module.updated_at

                # Sync lessons
                self._sync_lessons(module_model, module)

    def _sync_lessons(self, module_model: ModuleModel, module: Module) -> None:
        """Synchronize lesson models with domain entity lessons."""
        existing_lessons = {ls.id: ls for ls in module_model.lessons}

        for lesson in module.all_lessons:
            lesson_model = existing_lessons.get(lesson.id.value)
            if lesson_model is None:
                # New lesson
                lesson_model = self._lesson_to_model(lesson, module.id.value)
                module_model.lessons.append(lesson_model)
            else:
                # Update existing lesson
                lesson_model.title = lesson.title.value
                lesson_model.content_type = lesson.content_type.value
                lesson_model.content = lesson.content
                lesson_model.position = lesson.position
                lesson_model.is_deleted = lesson.is_deleted
                lesson_model.deleted_at = lesson.deleted_at
                lesson_model.updated_at = lesson.updated_at

    def _build_query(self) -> Select[Any]:
        """Build base query with eager loading for modules and lessons."""
        return select(CourseModel).options(
            selectinload(CourseModel.modules).selectinload(ModuleModel.lessons),
        )

    async def get_by_id(self, course_id: CourseId) -> Course | None:
        """Get a course by ID (excluding deleted)."""
        result = await self._session.execute(
            self._build_query().where(
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
            self._build_query().where(CourseModel.id == course_id.value)
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
        query = self._build_query()

        if not include_deleted:
            query = query.where(CourseModel.is_deleted == False)  # noqa: E712

        query = query.order_by(CourseModel.created_at.desc()).limit(limit).offset(offset)

        result = await self._session.execute(query)
        course_models = result.scalars().unique().all()

        return [self._to_entity(model) for model in course_models]

    async def get_course_by_module_id(self, module_id: ModuleId) -> Course | None:
        """Get the course that contains a specific module."""
        result = await self._session.execute(
            self._build_query()
            .join(CourseModel.modules)
            .where(
                ModuleModel.id == module_id.value,
                CourseModel.is_deleted == False,  # noqa: E712
            )
        )
        course_model = result.scalar_one_or_none()

        if course_model is None:
            return None

        return self._to_entity(course_model)

    async def get_course_by_lesson_id(self, lesson_id: LessonId) -> Course | None:
        """Get the course that contains a specific lesson."""
        result = await self._session.execute(
            self._build_query()
            .join(CourseModel.modules)
            .join(ModuleModel.lessons)
            .where(
                LessonModel.id == lesson_id.value,
                CourseModel.is_deleted == False,  # noqa: E712
            )
        )
        course_model = result.scalar_one_or_none()

        if course_model is None:
            return None

        return self._to_entity(course_model)

    def _to_entity(self, model: CourseModel) -> Course:
        """Convert SQLAlchemy model to domain entity."""
        modules = [self._module_to_entity(m) for m in model.modules]

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
            _modules=modules,
        )

    def _module_to_entity(self, model: ModuleModel) -> Module:
        """Convert module model to domain entity."""
        lessons = [self._lesson_to_entity(ls) for ls in model.lessons]

        return Module(
            id=ModuleId(value=model.id),
            title=ModuleTitle(model.title),
            description=ModuleDescription(model.description) if model.description else None,
            position=model.position,
            is_deleted=model.is_deleted,
            deleted_at=model.deleted_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
            _lessons=lessons,
        )

    def _lesson_to_entity(self, model: LessonModel) -> Lesson:
        """Convert lesson model to domain entity."""
        return Lesson(
            id=LessonId(value=model.id),
            title=LessonTitle(model.title),
            content_type=ContentType(model.content_type),
            content=model.content,
            position=model.position,
            is_deleted=model.is_deleted,
            deleted_at=model.deleted_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, course: Course) -> CourseModel:
        """Convert domain entity to SQLAlchemy model (for new courses)."""
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

        for module in course.all_modules:
            module_model = self._module_to_model(module, course.id.value)
            course_model.modules.append(module_model)

        return course_model

    def _module_to_model(self, module: Module, course_id: object) -> ModuleModel:
        """Convert module domain entity to SQLAlchemy model."""
        module_model = ModuleModel(
            id=module.id.value,
            course_id=course_id,
            title=module.title.value,
            description=module.description.value if module.description else None,
            position=module.position,
            is_deleted=module.is_deleted,
            deleted_at=module.deleted_at,
            created_at=module.created_at,
            updated_at=module.updated_at,
        )

        for lesson in module.all_lessons:
            lesson_model = self._lesson_to_model(lesson, module.id.value)
            module_model.lessons.append(lesson_model)

        return module_model

    def _lesson_to_model(self, lesson: Lesson, module_id: object) -> LessonModel:
        """Convert lesson domain entity to SQLAlchemy model."""
        return LessonModel(
            id=lesson.id.value,
            module_id=module_id,
            title=lesson.title.value,
            content_type=lesson.content_type.value,
            content=lesson.content,
            position=lesson.position,
            is_deleted=lesson.is_deleted,
            deleted_at=lesson.deleted_at,
            created_at=lesson.created_at,
            updated_at=lesson.updated_at,
        )
