"""Unit tests for pin/unpin post handlers."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from src.community.application.commands import PinPostCommand, UnpinPostCommand
from src.community.application.handlers.pin_post_handler import PinPostHandler
from src.community.application.handlers.unpin_post_handler import UnpinPostHandler
from src.community.domain.entities import CommunityMember, Post
from src.community.domain.exceptions import (
    CannotPinPostError,
    NotCommunityMemberError,
    PostNotFoundError,
)
from src.community.domain.value_objects import (
    CategoryId,
    CommunityId,
    MemberRole,
    PostContent,
    PostTitle,
)
from src.identity.domain.value_objects import UserId


@pytest.fixture
def community_id() -> CommunityId:
    return CommunityId(uuid4())


@pytest.fixture
def author_id() -> UserId:
    return UserId(uuid4())


@pytest.fixture
def post(community_id: CommunityId, author_id: UserId) -> Post:
    return Post.create(
        community_id=community_id,
        author_id=author_id,
        category_id=CategoryId(uuid4()),
        title=PostTitle("Test Post"),
        content=PostContent("Test content."),
    )


@pytest.fixture
def admin_member(community_id: CommunityId) -> CommunityMember:
    return CommunityMember.create(
        user_id=UserId(uuid4()),
        community_id=community_id,
        role=MemberRole.ADMIN,
    )


@pytest.fixture
def member(author_id: UserId, community_id: CommunityId) -> CommunityMember:
    return CommunityMember.create(
        user_id=author_id,
        community_id=community_id,
        role=MemberRole.MEMBER,
    )


class TestPinPostHandler:
    """Tests for PinPostHandler."""

    @pytest.mark.asyncio
    @patch("src.community.application.handlers.pin_post_handler.event_bus")
    async def test_pin_post_success(
        self, mock_event_bus: AsyncMock, post: Post, admin_member: CommunityMember
    ) -> None:
        """PinPostHandler should pin a post when user is admin."""
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = admin_member
        mock_event_bus.publish_all = AsyncMock()

        handler = PinPostHandler(post_repository=mock_post_repo, member_repository=mock_member_repo)
        command = PinPostCommand(post_id=post.id.value, pinner_id=admin_member.user_id.value)
        await handler.handle(command)

        mock_post_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_pin_post_not_found(self) -> None:
        """PinPostHandler should raise PostNotFoundError when post doesn't exist."""
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = None

        handler = PinPostHandler(post_repository=mock_post_repo, member_repository=mock_member_repo)
        command = PinPostCommand(post_id=uuid4(), pinner_id=uuid4())

        with pytest.raises(PostNotFoundError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_pin_post_not_member(self, post: Post) -> None:
        """PinPostHandler should raise NotCommunityMemberError when user is not a member."""
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = None

        handler = PinPostHandler(post_repository=mock_post_repo, member_repository=mock_member_repo)
        command = PinPostCommand(post_id=post.id.value, pinner_id=uuid4())

        with pytest.raises(NotCommunityMemberError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_pin_post_permission_denied(self, post: Post, member: CommunityMember) -> None:
        """PinPostHandler should raise CannotPinPostError when user is regular member."""
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = member

        handler = PinPostHandler(post_repository=mock_post_repo, member_repository=mock_member_repo)
        command = PinPostCommand(post_id=post.id.value, pinner_id=member.user_id.value)

        with pytest.raises(CannotPinPostError):
            await handler.handle(command)


class TestUnpinPostHandler:
    """Tests for UnpinPostHandler."""

    @pytest.mark.asyncio
    @patch("src.community.application.handlers.unpin_post_handler.event_bus")
    async def test_unpin_post_success(
        self, mock_event_bus: AsyncMock, post: Post, admin_member: CommunityMember
    ) -> None:
        """UnpinPostHandler should unpin a pinned post when user is admin."""
        post.pin(admin_member.user_id, admin_member.role)
        post.clear_events()

        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = admin_member
        mock_event_bus.publish_all = AsyncMock()

        handler = UnpinPostHandler(
            post_repository=mock_post_repo, member_repository=mock_member_repo
        )
        command = UnpinPostCommand(post_id=post.id.value, unpinner_id=admin_member.user_id.value)
        await handler.handle(command)

        mock_post_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_unpin_post_not_found(self) -> None:
        """UnpinPostHandler should raise PostNotFoundError when post doesn't exist."""
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = None

        handler = UnpinPostHandler(
            post_repository=mock_post_repo, member_repository=mock_member_repo
        )
        command = UnpinPostCommand(post_id=uuid4(), unpinner_id=uuid4())

        with pytest.raises(PostNotFoundError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_unpin_post_not_member(self, post: Post) -> None:
        """UnpinPostHandler should raise NotCommunityMemberError when user is not a member."""
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = None

        handler = UnpinPostHandler(
            post_repository=mock_post_repo, member_repository=mock_member_repo
        )
        command = UnpinPostCommand(post_id=post.id.value, unpinner_id=uuid4())

        with pytest.raises(NotCommunityMemberError):
            await handler.handle(command)
