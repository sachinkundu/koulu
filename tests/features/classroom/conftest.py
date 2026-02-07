"""Pytest fixtures for Classroom BDD tests."""

from collections.abc import Callable, Coroutine
from typing import Any
from uuid import uuid4

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.classroom.infrastructure.persistence.models import CourseModel
from src.identity.infrastructure.persistence.models import ProfileModel, UserModel
from src.identity.infrastructure.services import Argon2PasswordHasher

# Type aliases
CreateCourseFactory = Callable[..., Coroutine[Any, Any, CourseModel]]


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
