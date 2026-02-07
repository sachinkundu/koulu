"""Unit tests for post-related handlers (Get, Update, Delete, Lock, Unlock)."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from src.community.application.commands import (
    DeletePostCommand,
    LockPostCommand,
    UnlockPostCommand,
    UpdatePostCommand,
)
from src.community.application.handlers.delete_post_handler import DeletePostHandler
from src.community.application.handlers.get_post_handler import GetPostHandler
from src.community.application.handlers.lock_post_handler import LockPostHandler
from src.community.application.handlers.unlock_post_handler import UnlockPostHandler
from src.community.application.handlers.update_post_handler import UpdatePostHandler
from src.community.application.queries import GetPostQuery
from src.community.domain.entities import CommunityMember, Post
from src.community.domain.exceptions import (
    CannotDeletePostError,
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
        content=PostContent("Test content for the post body."),
    )


@pytest.fixture
def member(author_id: UserId, community_id: CommunityId) -> CommunityMember:
    return CommunityMember.create(
        user_id=author_id,
        community_id=community_id,
        role=MemberRole.MEMBER,
    )


@pytest.fixture
def admin_member(community_id: CommunityId) -> CommunityMember:
    return CommunityMember.create(
        user_id=UserId(uuid4()),
        community_id=community_id,
        role=MemberRole.ADMIN,
    )


# ============================================================================
# GetPostHandler Tests
# ============================================================================


class TestGetPostHandler:
    @pytest.mark.asyncio
    async def test_get_post_success(self, post: Post) -> None:
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post

        handler = GetPostHandler(
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        query = GetPostQuery(post_id=post.id.value)
        result = await handler.handle(query)

        assert result.id == post.id

    @pytest.mark.asyncio
    async def test_get_post_not_found(self) -> None:
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = None

        handler = GetPostHandler(
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        query = GetPostQuery(post_id=uuid4())
        with pytest.raises(PostNotFoundError):
            await handler.handle(query)

    @pytest.mark.asyncio
    async def test_get_post_with_requester_not_member(self, post: Post) -> None:
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = None

        handler = GetPostHandler(
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        query = GetPostQuery(post_id=post.id.value, requester_id=uuid4())
        with pytest.raises(NotCommunityMemberError):
            await handler.handle(query)

    @pytest.mark.asyncio
    async def test_get_post_with_valid_requester(self, post: Post, member: CommunityMember) -> None:
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = member

        handler = GetPostHandler(
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        query = GetPostQuery(post_id=post.id.value, requester_id=member.user_id.value)
        result = await handler.handle(query)
        assert result.id == post.id


# ============================================================================
# UpdatePostHandler Tests
# ============================================================================


class TestUpdatePostHandler:
    @pytest.mark.asyncio
    @patch("src.community.application.handlers.update_post_handler.event_bus")
    async def test_update_post_success(
        self,
        mock_event_bus: AsyncMock,
        post: Post,
        member: CommunityMember,
    ) -> None:
        mock_post_repo = AsyncMock()
        mock_category_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = member
        mock_event_bus.publish_all = AsyncMock()

        handler = UpdatePostHandler(
            post_repository=mock_post_repo,
            category_repository=mock_category_repo,
            member_repository=mock_member_repo,
        )

        command = UpdatePostCommand(
            post_id=post.id.value,
            editor_id=member.user_id.value,
            title="Updated Title",
        )
        await handler.handle(command)

        mock_post_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_post_not_found(self) -> None:
        mock_post_repo = AsyncMock()
        mock_category_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = None

        handler = UpdatePostHandler(
            post_repository=mock_post_repo,
            category_repository=mock_category_repo,
            member_repository=mock_member_repo,
        )

        command = UpdatePostCommand(post_id=uuid4(), editor_id=uuid4(), title="New")
        with pytest.raises(PostNotFoundError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_update_post_not_member(self, post: Post) -> None:
        mock_post_repo = AsyncMock()
        mock_category_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = None

        handler = UpdatePostHandler(
            post_repository=mock_post_repo,
            category_repository=mock_category_repo,
            member_repository=mock_member_repo,
        )

        command = UpdatePostCommand(post_id=post.id.value, editor_id=uuid4(), title="New")
        with pytest.raises(NotCommunityMemberError):
            await handler.handle(command)

    @pytest.mark.asyncio
    @patch("src.community.application.handlers.update_post_handler.event_bus")
    async def test_update_post_no_changes(
        self,
        mock_event_bus: AsyncMock,
        post: Post,
        member: CommunityMember,
    ) -> None:
        mock_post_repo = AsyncMock()
        mock_category_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = member
        mock_event_bus.publish_all = AsyncMock()

        handler = UpdatePostHandler(
            post_repository=mock_post_repo,
            category_repository=mock_category_repo,
            member_repository=mock_member_repo,
        )

        # Pass no changes
        command = UpdatePostCommand(post_id=post.id.value, editor_id=member.user_id.value)
        await handler.handle(command)

        mock_post_repo.save.assert_not_called()


# ============================================================================
# DeletePostHandler Tests
# ============================================================================


class TestDeletePostHandler:
    @pytest.mark.asyncio
    @patch("src.community.application.handlers.delete_post_handler.event_bus")
    async def test_delete_post_by_author(
        self,
        mock_event_bus: AsyncMock,
        post: Post,
        member: CommunityMember,
    ) -> None:
        mock_post_repo = AsyncMock()
        mock_comment_repo = AsyncMock()
        mock_reaction_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = member
        mock_event_bus.publish_all = AsyncMock()

        handler = DeletePostHandler(
            post_repository=mock_post_repo,
            comment_repository=mock_comment_repo,
            reaction_repository=mock_reaction_repo,
            member_repository=mock_member_repo,
        )

        command = DeletePostCommand(
            post_id=post.id.value,
            deleter_id=member.user_id.value,
        )
        await handler.handle(command)

        mock_reaction_repo.delete_by_post_cascade.assert_called_once()
        mock_comment_repo.delete_by_post.assert_called_once()
        mock_post_repo.save.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.community.application.handlers.delete_post_handler.event_bus")
    async def test_delete_post_by_admin(
        self,
        mock_event_bus: AsyncMock,
        post: Post,
        admin_member: CommunityMember,
    ) -> None:
        mock_post_repo = AsyncMock()
        mock_comment_repo = AsyncMock()
        mock_reaction_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = admin_member
        mock_event_bus.publish_all = AsyncMock()

        handler = DeletePostHandler(
            post_repository=mock_post_repo,
            comment_repository=mock_comment_repo,
            reaction_repository=mock_reaction_repo,
            member_repository=mock_member_repo,
        )

        command = DeletePostCommand(
            post_id=post.id.value,
            deleter_id=admin_member.user_id.value,
        )
        await handler.handle(command)

        mock_post_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_post_not_found(self) -> None:
        mock_post_repo = AsyncMock()
        mock_comment_repo = AsyncMock()
        mock_reaction_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = None

        handler = DeletePostHandler(
            post_repository=mock_post_repo,
            comment_repository=mock_comment_repo,
            reaction_repository=mock_reaction_repo,
            member_repository=mock_member_repo,
        )

        command = DeletePostCommand(post_id=uuid4(), deleter_id=uuid4())
        with pytest.raises(PostNotFoundError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_delete_post_not_member(self, post: Post) -> None:
        mock_post_repo = AsyncMock()
        mock_comment_repo = AsyncMock()
        mock_reaction_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = None

        handler = DeletePostHandler(
            post_repository=mock_post_repo,
            comment_repository=mock_comment_repo,
            reaction_repository=mock_reaction_repo,
            member_repository=mock_member_repo,
        )

        command = DeletePostCommand(post_id=post.id.value, deleter_id=uuid4())
        with pytest.raises(NotCommunityMemberError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_delete_post_not_author_and_not_admin(
        self,
        post: Post,
        community_id: CommunityId,
    ) -> None:
        other_user = UserId(uuid4())
        regular_member = CommunityMember.create(
            user_id=other_user,
            community_id=community_id,
            role=MemberRole.MEMBER,
        )
        mock_post_repo = AsyncMock()
        mock_comment_repo = AsyncMock()
        mock_reaction_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = regular_member

        handler = DeletePostHandler(
            post_repository=mock_post_repo,
            comment_repository=mock_comment_repo,
            reaction_repository=mock_reaction_repo,
            member_repository=mock_member_repo,
        )

        command = DeletePostCommand(
            post_id=post.id.value,
            deleter_id=other_user.value,
        )
        with pytest.raises(CannotDeletePostError):
            await handler.handle(command)


# ============================================================================
# LockPostHandler Tests
# ============================================================================


class TestLockPostHandler:
    @pytest.mark.asyncio
    @patch("src.community.application.handlers.lock_post_handler.event_bus")
    async def test_lock_post_success(
        self,
        mock_event_bus: AsyncMock,
        post: Post,
        admin_member: CommunityMember,
    ) -> None:
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = admin_member
        mock_event_bus.publish_all = AsyncMock()

        handler = LockPostHandler(
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        command = LockPostCommand(
            post_id=post.id.value,
            locker_id=admin_member.user_id.value,
        )
        await handler.handle(command)

        mock_post_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_lock_post_not_found(self) -> None:
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = None

        handler = LockPostHandler(
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        command = LockPostCommand(post_id=uuid4(), locker_id=uuid4())
        with pytest.raises(PostNotFoundError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_lock_post_not_member(self, post: Post) -> None:
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = None

        handler = LockPostHandler(
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        command = LockPostCommand(post_id=post.id.value, locker_id=uuid4())
        with pytest.raises(NotCommunityMemberError):
            await handler.handle(command)


# ============================================================================
# UnlockPostHandler Tests
# ============================================================================


class TestUnlockPostHandler:
    @pytest.mark.asyncio
    @patch("src.community.application.handlers.unlock_post_handler.event_bus")
    async def test_unlock_post_success(
        self,
        mock_event_bus: AsyncMock,
        post: Post,
        admin_member: CommunityMember,
    ) -> None:
        # Lock the post first
        post.lock(admin_member.user_id, admin_member.role)
        post.clear_events()

        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = admin_member
        mock_event_bus.publish_all = AsyncMock()

        handler = UnlockPostHandler(
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        command = UnlockPostCommand(
            post_id=post.id.value,
            unlocker_id=admin_member.user_id.value,
        )
        await handler.handle(command)

        mock_post_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_unlock_post_not_found(self) -> None:
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = None

        handler = UnlockPostHandler(
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        command = UnlockPostCommand(post_id=uuid4(), unlocker_id=uuid4())
        with pytest.raises(PostNotFoundError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_unlock_post_not_member(self, post: Post) -> None:
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = None

        handler = UnlockPostHandler(
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        command = UnlockPostCommand(post_id=post.id.value, unlocker_id=uuid4())
        with pytest.raises(NotCommunityMemberError):
            await handler.handle(command)
