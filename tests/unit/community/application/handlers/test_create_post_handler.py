"""Unit tests for CreatePostHandler."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from src.community.application.commands import CreatePostCommand
from src.community.application.handlers.create_post_handler import CreatePostHandler
from src.community.domain.entities import CommunityMember
from src.community.domain.entities.category import Category
from src.community.domain.exceptions import (
    CategoryNotFoundError,
    NotCommunityMemberError,
    RateLimitExceededError,
)
from src.community.domain.value_objects import CategoryId, CommunityId, MemberRole
from src.community.infrastructure.services import InMemoryRateLimiter
from src.identity.domain.value_objects import UserId


@pytest.fixture
def mock_post_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_category_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_member_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_rate_limiter() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def handler(
    mock_post_repo: AsyncMock,
    mock_category_repo: AsyncMock,
    mock_member_repo: AsyncMock,
    mock_rate_limiter: AsyncMock,
) -> CreatePostHandler:
    return CreatePostHandler(
        post_repository=mock_post_repo,
        category_repository=mock_category_repo,
        member_repository=mock_member_repo,
        rate_limiter=mock_rate_limiter,
    )


@pytest.fixture
def community_id() -> CommunityId:
    return CommunityId(uuid4())


@pytest.fixture
def author_id() -> UserId:
    return UserId(uuid4())


@pytest.fixture
def category(community_id: CommunityId) -> Category:
    return Category(
        id=CategoryId(uuid4()),
        community_id=community_id,
        name="General",
        slug="general",
        emoji="💬",
    )


@pytest.fixture
def member(author_id: UserId, community_id: CommunityId) -> CommunityMember:
    return CommunityMember.create(
        user_id=author_id,
        community_id=community_id,
        role=MemberRole.MEMBER,
    )


class TestCreatePostHandler:
    @pytest.mark.asyncio
    @patch("src.community.application.handlers.create_post_handler.event_bus")
    async def test_create_post_success_with_category_id(
        self,
        mock_event_bus: AsyncMock,
        handler: CreatePostHandler,
        mock_member_repo: AsyncMock,
        mock_category_repo: AsyncMock,
        mock_post_repo: AsyncMock,
        member: CommunityMember,
        category: Category,
    ) -> None:
        mock_member_repo.get_by_user_and_community.return_value = member
        mock_category_repo.get_by_id.return_value = category
        mock_event_bus.publish_all = AsyncMock()

        command = CreatePostCommand(
            community_id=member.community_id.value,
            author_id=member.user_id.value,
            category_id=category.id.value,
            category_name=None,
            title="Test Post",
            content="Test content for the post.",
        )

        result = await handler.handle(command)

        assert result is not None
        mock_post_repo.save.assert_called_once()
        mock_event_bus.publish_all.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.community.application.handlers.create_post_handler.event_bus")
    async def test_create_post_success_with_category_name(
        self,
        mock_event_bus: AsyncMock,
        handler: CreatePostHandler,
        mock_member_repo: AsyncMock,
        mock_category_repo: AsyncMock,
        member: CommunityMember,
        category: Category,
    ) -> None:
        mock_member_repo.get_by_user_and_community.return_value = member
        mock_category_repo.get_by_name.return_value = category
        mock_event_bus.publish_all = AsyncMock()

        command = CreatePostCommand(
            community_id=member.community_id.value,
            author_id=member.user_id.value,
            category_id=None,
            category_name="General",
            title="Test Post",
            content="Test content for the post.",
        )

        result = await handler.handle(command)

        assert result is not None
        mock_category_repo.get_by_name.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.community.application.handlers.create_post_handler.event_bus")
    async def test_create_post_default_category(
        self,
        mock_event_bus: AsyncMock,
        handler: CreatePostHandler,
        mock_member_repo: AsyncMock,
        mock_category_repo: AsyncMock,
        member: CommunityMember,
        category: Category,
    ) -> None:
        mock_member_repo.get_by_user_and_community.return_value = member
        mock_category_repo.list_by_community.return_value = [category]
        mock_event_bus.publish_all = AsyncMock()

        command = CreatePostCommand(
            community_id=member.community_id.value,
            author_id=member.user_id.value,
            category_id=None,
            category_name=None,
            title="Test Post",
            content="Test content for the post.",
        )

        result = await handler.handle(command)

        assert result is not None
        mock_category_repo.list_by_community.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_post_not_member_raises_error(
        self,
        handler: CreatePostHandler,
        mock_member_repo: AsyncMock,
    ) -> None:
        mock_member_repo.get_by_user_and_community.return_value = None

        command = CreatePostCommand(
            community_id=uuid4(),
            author_id=uuid4(),
            category_id=uuid4(),
            category_name=None,
            title="Test Post",
            content="Test content.",
        )

        with pytest.raises(NotCommunityMemberError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_create_post_category_not_found_raises_error(
        self,
        handler: CreatePostHandler,
        mock_member_repo: AsyncMock,
        mock_category_repo: AsyncMock,
        member: CommunityMember,
    ) -> None:
        mock_member_repo.get_by_user_and_community.return_value = member
        mock_category_repo.get_by_id.return_value = None

        command = CreatePostCommand(
            community_id=member.community_id.value,
            author_id=member.user_id.value,
            category_id=uuid4(),
            category_name=None,
            title="Test Post",
            content="Test content.",
        )

        with pytest.raises(CategoryNotFoundError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_create_post_rate_limited_raises_error(
        self,
        mock_post_repo: AsyncMock,
        mock_category_repo: AsyncMock,
        mock_member_repo: AsyncMock,
    ) -> None:
        rate_limiter = InMemoryRateLimiter()
        rate_limiter.reset()

        handler = CreatePostHandler(
            post_repository=mock_post_repo,
            category_repository=mock_category_repo,
            member_repository=mock_member_repo,
            rate_limiter=rate_limiter,
        )

        author_id = uuid4()
        community_id = uuid4()

        command = CreatePostCommand(
            community_id=community_id,
            author_id=author_id,
            category_id=uuid4(),
            category_name=None,
            title="Test Post",
            content="Test content.",
        )

        # Exhaust rate limit (10 calls)
        mock_member_repo.get_by_user_and_community.return_value = CommunityMember.create(
            user_id=UserId(author_id),
            community_id=CommunityId(community_id),
            role=MemberRole.MEMBER,
        )
        mock_category_repo.get_by_id.return_value = Category(
            id=CategoryId(uuid4()),
            community_id=CommunityId(community_id),
            name="General",
            slug="general",
            emoji="💬",
        )

        for _ in range(10):
            with patch(
                "src.community.application.handlers.create_post_handler.event_bus"
            ) as mock_eb:
                mock_eb.publish_all = AsyncMock()
                await handler.handle(command)

        # 11th should fail
        with pytest.raises(RateLimitExceededError):
            await handler.handle(command)

        rate_limiter.reset()
