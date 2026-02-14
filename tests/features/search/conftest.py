"""Pytest fixtures for Search BDD tests."""

from collections.abc import Callable, Coroutine, Generator
from typing import Any
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.community.infrastructure.persistence.models import (
    CategoryModel,
    CommunityMemberModel,
    CommunityModel,
    PostModel,
)
from src.community.infrastructure.services import InMemoryRateLimiter
from src.identity.infrastructure.persistence.models import ProfileModel, UserModel
from src.identity.infrastructure.services import Argon2PasswordHasher

# Type aliases
CreateSearchCommunityFactory = Callable[..., Coroutine[Any, Any, CommunityModel]]
CreateSearchMemberFactory = Callable[
    ..., Coroutine[Any, Any, tuple[UserModel, CommunityMemberModel]]
]
CreateSearchPostFactory = Callable[..., Coroutine[Any, Any, PostModel]]


@pytest.fixture(autouse=True)
def _reset_rate_limiter() -> Generator[None, None, None]:
    """Reset rate limiter state between tests."""
    InMemoryRateLimiter.reset()
    yield
    InMemoryRateLimiter.reset()


@pytest_asyncio.fixture
async def create_search_community(db_session: AsyncSession) -> CreateSearchCommunityFactory:
    """Factory to create a community for search tests."""

    async def _create(
        name: str = "Startup Empire",
        slug: str | None = None,
    ) -> CommunityModel:
        if slug is None:
            slug = name.lower().replace(" ", "-") + f"-{uuid4().hex[:6]}"
        community = CommunityModel(
            id=uuid4(),
            name=name,
            slug=slug,
        )
        db_session.add(community)
        await db_session.commit()
        await db_session.refresh(community)
        return community

    return _create


@pytest_asyncio.fixture
async def create_search_member(
    db_session: AsyncSession,
    password_hasher: Argon2PasswordHasher,
) -> CreateSearchMemberFactory:
    """Factory to create a user + profile + community membership with search_vector populated."""

    async def _create(
        community_id: UUID,
        display_name: str,
        username: str,
        bio: str | None = None,
        role: str = "MEMBER",
        email: str | None = None,
        is_active: bool = True,
    ) -> tuple[UserModel, CommunityMemberModel]:
        user_id = uuid4()
        if email is None:
            email = f"{username}@example.com"

        hashed = password_hasher.hash("testpassword123")
        user = UserModel(
            id=user_id,
            email=email.lower(),
            hashed_password=hashed.value,
            is_verified=True,
            is_active=True,
        )
        db_session.add(user)

        profile = ProfileModel(
            user_id=user_id,
            display_name=display_name,
            username=username,
            bio=bio,
            is_complete=True,
        )
        db_session.add(profile)
        await db_session.flush()

        # Manually populate search_vector since test DB has no triggers
        parts = []
        if display_name:
            parts.append("setweight(to_tsvector('english', :dn), 'A')")
        if username:
            parts.append("setweight(to_tsvector('english', :un), 'B')")
        if bio:
            parts.append("setweight(to_tsvector('english', :bio), 'C')")

        if parts:
            expr = " || ".join(parts)
            params: dict[str, str] = {}
            if display_name:
                params["dn"] = display_name
            if username:
                params["un"] = username
            if bio:
                params["bio"] = bio
            params["uid"] = str(user_id)

            await db_session.execute(
                text(f"UPDATE profiles SET search_vector = {expr} WHERE user_id = :uid"),
                params,
            )

        member = CommunityMemberModel(
            community_id=community_id,
            user_id=user_id,
            role=role,
            is_active=is_active,
        )
        db_session.add(member)
        await db_session.commit()
        await db_session.refresh(user)
        await db_session.refresh(member)

        return user, member

    return _create


@pytest_asyncio.fixture
async def create_search_post(db_session: AsyncSession) -> CreateSearchPostFactory:
    """Factory to create a post with search_vector populated."""

    async def _create(
        community_id: UUID,
        author_id: UUID,
        category_id: UUID,
        title: str,
        content: str,
        is_deleted: bool = False,
    ) -> PostModel:
        post_id = uuid4()
        post = PostModel(
            id=post_id,
            community_id=community_id,
            author_id=author_id,
            category_id=category_id,
            title=title,
            content=content,
            is_deleted=is_deleted,
        )
        db_session.add(post)
        await db_session.flush()

        # Manually populate search_vector since test DB has no triggers
        await db_session.execute(
            text(
                "UPDATE posts SET search_vector = "
                "setweight(to_tsvector('english', :title), 'A') || "
                "setweight(to_tsvector('english', :content), 'B') "
                "WHERE id = :pid"
            ),
            {"title": title, "content": content, "pid": str(post_id)},
        )

        await db_session.commit()
        await db_session.refresh(post)
        return post

    return _create


@pytest_asyncio.fixture
async def create_search_category(
    db_session: AsyncSession,
) -> Callable[..., Coroutine[Any, Any, CategoryModel]]:
    """Factory to create a category for search tests."""

    async def _create(
        community_id: UUID,
        name: str = "General",
        slug: str = "general",
        emoji: str = "💬",
    ) -> CategoryModel:
        category = CategoryModel(
            id=uuid4(),
            community_id=community_id,
            name=name,
            slug=slug,
            emoji=emoji,
        )
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)
        return category

    return _create
