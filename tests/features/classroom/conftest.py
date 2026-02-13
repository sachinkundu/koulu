"""Pytest fixtures for Classroom BDD tests."""

from collections.abc import Callable, Coroutine
from typing import Any
from uuid import UUID, uuid4

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.classroom.infrastructure.persistence.models import (
    CourseModel,
    LessonCompletionModel,
    LessonModel,
    ModuleModel,
    ProgressModel,
)
from src.community.infrastructure.persistence.models import (
    CommunityMemberModel,
    CommunityModel,
)
from src.identity.infrastructure.persistence.models import ProfileModel, UserModel
from src.identity.infrastructure.services import Argon2PasswordHasher

# Type aliases
CreateCourseFactory = Callable[..., Coroutine[Any, Any, CourseModel]]
CreateModuleFactory = Callable[..., Coroutine[Any, Any, ModuleModel]]
CreateLessonFactory = Callable[..., Coroutine[Any, Any, LessonModel]]
CreateProgressFactory = Callable[..., Coroutine[Any, Any, ProgressModel]]


@pytest_asyncio.fixture
async def default_community(db_session: AsyncSession) -> CommunityModel:
    """Create a default community for role-based access checks."""
    community = CommunityModel(
        id=uuid4(),
        name="Test Community",
        slug="test-community",
    )
    db_session.add(community)
    await db_session.commit()
    await db_session.refresh(community)
    return community


@pytest_asyncio.fixture
async def create_member(
    db_session: AsyncSession,
    default_community: CommunityModel,
) -> Callable[..., Coroutine[Any, Any, CommunityMemberModel]]:
    """Factory fixture to create community memberships."""

    async def _create_member(
        user_id: UUID,
        role: str = "MEMBER",
    ) -> CommunityMemberModel:
        member = CommunityMemberModel(
            id=uuid4(),
            community_id=default_community.id,
            user_id=user_id,
            role=role,
        )
        db_session.add(member)
        await db_session.commit()
        await db_session.refresh(member)
        return member

    return _create_member


@pytest_asyncio.fixture
async def create_user(
    db_session: AsyncSession,
    password_hasher: Argon2PasswordHasher,
) -> Callable[..., Coroutine[Any, Any, UserModel]]:
    """Factory fixture to create test users."""

    async def _create_user(
        email: str,
        password: str = "testpassword123",
        is_verified: bool = True,
        display_name: str = "Test User",
    ) -> UserModel:
        hashed = password_hasher.hash(password)
        user_id = uuid4()
        user = UserModel(
            id=user_id,
            email=email.lower(),
            hashed_password=hashed.value,
            is_verified=is_verified,
            is_active=True,
        )
        db_session.add(user)

        profile = ProfileModel(
            user_id=user_id,
            display_name=display_name,
            is_complete=True,
        )
        db_session.add(profile)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    return _create_user


@pytest_asyncio.fixture
async def create_course_in_db(db_session: AsyncSession) -> CreateCourseFactory:
    """Factory fixture to create courses directly in the database."""

    async def _create_course(
        instructor_id: Any,
        title: str = "Test Course",
        description: str | None = None,
        cover_image_url: str | None = None,
        estimated_duration: str | None = None,
        is_deleted: bool = False,
    ) -> CourseModel:
        course_id = uuid4()
        course = CourseModel(
            id=course_id,
            instructor_id=instructor_id,
            title=title,
            description=description,
            cover_image_url=cover_image_url,
            estimated_duration=estimated_duration,
            is_deleted=is_deleted,
        )
        db_session.add(course)
        await db_session.commit()
        await db_session.refresh(course)
        return course

    return _create_course


@pytest_asyncio.fixture
async def create_module_in_db(db_session: AsyncSession) -> CreateModuleFactory:
    """Factory fixture to create modules directly in the database."""

    async def _create_module(
        course_id: Any,
        title: str = "Test Module",
        description: str | None = None,
        position: int = 1,
    ) -> ModuleModel:
        module_id = uuid4()
        module = ModuleModel(
            id=module_id,
            course_id=course_id,
            title=title,
            description=description,
            position=position,
        )
        db_session.add(module)
        await db_session.commit()
        await db_session.refresh(module)
        return module

    return _create_module


@pytest_asyncio.fixture
async def create_lesson_in_db(db_session: AsyncSession) -> CreateLessonFactory:
    """Factory fixture to create lessons directly in the database."""

    async def _create_lesson(
        module_id: Any,
        title: str = "Test Lesson",
        content_type: str = "text",
        content: str = "Default lesson content.",
        position: int = 1,
    ) -> LessonModel:
        lesson_id = uuid4()
        lesson = LessonModel(
            id=lesson_id,
            module_id=module_id,
            title=title,
            content_type=content_type,
            content=content,
            position=position,
        )
        db_session.add(lesson)
        await db_session.commit()
        await db_session.refresh(lesson)
        return lesson

    return _create_lesson


@pytest_asyncio.fixture
async def create_progress_in_db(db_session: AsyncSession) -> CreateProgressFactory:
    """Factory fixture to create progress records directly in the database."""

    async def _create_progress(
        user_id: Any,
        course_id: Any,
        completed_lesson_ids: list[Any] | None = None,
    ) -> ProgressModel:
        progress_id = uuid4()
        progress = ProgressModel(
            id=progress_id,
            user_id=user_id,
            course_id=course_id,
        )
        db_session.add(progress)
        await db_session.flush()

        if completed_lesson_ids:
            for lesson_id in completed_lesson_ids:
                completion = LessonCompletionModel(
                    id=uuid4(),
                    progress_id=progress_id,
                    lesson_id=lesson_id,
                )
                db_session.add(completion)

        await db_session.commit()
        await db_session.refresh(progress)
        return progress

    return _create_progress
