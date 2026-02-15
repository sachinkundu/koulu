"""Unit tests for comment-related handlers (Add, Edit, Delete, GetPostComments)."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from src.community.application.commands import (
    AddCommentCommand,
    DeleteCommentCommand,
    EditCommentCommand,
)
from src.community.application.handlers.add_comment_handler import AddCommentHandler
from src.community.application.handlers.delete_comment_handler import DeleteCommentHandler
from src.community.application.handlers.edit_comment_handler import EditCommentHandler
from src.community.application.handlers.get_post_comments_handler import GetPostCommentsHandler
from src.community.application.queries import GetPostCommentsQuery
from src.community.domain.entities import Comment, CommunityMember, Post
from src.community.domain.exceptions import (
    CommentNotFoundError,
    MaxReplyDepthExceededError,
    NotCommunityMemberError,
    PostLockedError,
    PostNotFoundError,
)
from src.community.domain.value_objects import (
    CategoryId,
    CommentContent,
    CommunityId,
    MemberRole,
    PostContent,
    PostId,
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
def locked_post(community_id: CommunityId, author_id: UserId) -> Post:
    p = Post.create(
        community_id=community_id,
        author_id=author_id,
        category_id=CategoryId(uuid4()),
        title=PostTitle("Locked Post"),
        content=PostContent("This post is locked."),
    )
    p.lock(author_id, MemberRole.ADMIN)
    p.clear_events()
    return p


@pytest.fixture
def member(author_id: UserId, community_id: CommunityId) -> CommunityMember:
    return CommunityMember.create(
        user_id=author_id,
        community_id=community_id,
        role=MemberRole.MEMBER,
    )


@pytest.fixture
def comment(author_id: UserId, community_id: CommunityId) -> Comment:
    return Comment.create(
        post_id=PostId(uuid4()),
        author_id=author_id,
        content=CommentContent("Test comment content here."),
        community_id=community_id,
    )


@pytest.fixture
def reply(author_id: UserId, comment: Comment, community_id: CommunityId) -> Comment:
    return Comment.create(
        post_id=comment.post_id,
        author_id=author_id,
        content=CommentContent("This is a reply."),
        community_id=community_id,
        parent_comment_id=comment.id,
    )


# ============================================================================
# AddCommentHandler Tests
# ============================================================================


class TestAddCommentHandler:
    @pytest.mark.asyncio
    @patch("src.community.application.handlers.add_comment_handler.event_bus")
    async def test_add_comment_success(
        self,
        mock_event_bus: AsyncMock,
        post: Post,
        member: CommunityMember,
    ) -> None:
        mock_comment_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = member
        mock_event_bus.publish_all = AsyncMock()

        handler = AddCommentHandler(
            comment_repository=mock_comment_repo,
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        command = AddCommentCommand(
            post_id=post.id.value,
            author_id=member.user_id.value,
            content="A new comment.",
        )
        result = await handler.handle(command)

        assert result is not None
        mock_comment_repo.save.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.community.application.handlers.add_comment_handler.event_bus")
    async def test_add_reply_to_comment_success(
        self,
        mock_event_bus: AsyncMock,
        post: Post,
        member: CommunityMember,
        comment: Comment,
    ) -> None:
        mock_comment_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = member
        mock_comment_repo.get_by_id.return_value = comment
        mock_event_bus.publish_all = AsyncMock()

        handler = AddCommentHandler(
            comment_repository=mock_comment_repo,
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        command = AddCommentCommand(
            post_id=post.id.value,
            author_id=member.user_id.value,
            content="A reply.",
            parent_comment_id=comment.id.value,
        )
        result = await handler.handle(command)

        assert result is not None

    @pytest.mark.asyncio
    async def test_add_comment_post_not_found(self) -> None:
        mock_comment_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = None

        handler = AddCommentHandler(
            comment_repository=mock_comment_repo,
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        command = AddCommentCommand(
            post_id=uuid4(),
            author_id=uuid4(),
            content="A comment.",
        )
        with pytest.raises(PostNotFoundError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_add_comment_post_locked(self, locked_post: Post) -> None:
        mock_comment_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = locked_post

        handler = AddCommentHandler(
            comment_repository=mock_comment_repo,
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        command = AddCommentCommand(
            post_id=locked_post.id.value,
            author_id=uuid4(),
            content="A comment.",
        )
        with pytest.raises(PostLockedError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_add_comment_not_member(self, post: Post) -> None:
        mock_comment_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = None

        handler = AddCommentHandler(
            comment_repository=mock_comment_repo,
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        command = AddCommentCommand(
            post_id=post.id.value,
            author_id=uuid4(),
            content="A comment.",
        )
        with pytest.raises(NotCommunityMemberError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_add_comment_parent_not_found(
        self,
        post: Post,
        member: CommunityMember,
    ) -> None:
        mock_comment_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = member
        mock_comment_repo.get_by_id.return_value = None

        handler = AddCommentHandler(
            comment_repository=mock_comment_repo,
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        command = AddCommentCommand(
            post_id=post.id.value,
            author_id=member.user_id.value,
            content="A reply.",
            parent_comment_id=uuid4(),
        )
        with pytest.raises(CommentNotFoundError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_add_reply_max_depth_exceeded(
        self,
        post: Post,
        member: CommunityMember,
        reply: Comment,
    ) -> None:
        mock_comment_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = member
        # reply already has a parent, so replying to it exceeds max depth
        mock_comment_repo.get_by_id.return_value = reply

        handler = AddCommentHandler(
            comment_repository=mock_comment_repo,
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        command = AddCommentCommand(
            post_id=post.id.value,
            author_id=member.user_id.value,
            content="A nested reply.",
            parent_comment_id=reply.id.value,
        )
        with pytest.raises(MaxReplyDepthExceededError):
            await handler.handle(command)


# ============================================================================
# EditCommentHandler Tests
# ============================================================================


class TestEditCommentHandler:
    @pytest.mark.asyncio
    @patch("src.community.application.handlers.edit_comment_handler.event_bus")
    async def test_edit_comment_success(
        self,
        mock_event_bus: AsyncMock,
        comment: Comment,
        post: Post,
        member: CommunityMember,
    ) -> None:
        mock_comment_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_comment_repo.get_by_id.return_value = comment
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = member
        mock_event_bus.publish_all = AsyncMock()

        handler = EditCommentHandler(
            comment_repository=mock_comment_repo,
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        command = EditCommentCommand(
            comment_id=comment.id.value,
            editor_id=member.user_id.value,
            content="Updated comment.",
        )
        await handler.handle(command)

        mock_comment_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_edit_comment_not_found(self) -> None:
        mock_comment_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_comment_repo.get_by_id.return_value = None

        handler = EditCommentHandler(
            comment_repository=mock_comment_repo,
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        command = EditCommentCommand(
            comment_id=uuid4(),
            editor_id=uuid4(),
            content="Updated.",
        )
        with pytest.raises(CommentNotFoundError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_edit_comment_post_not_found(self, comment: Comment) -> None:
        mock_comment_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_comment_repo.get_by_id.return_value = comment
        mock_post_repo.get_by_id.return_value = None

        handler = EditCommentHandler(
            comment_repository=mock_comment_repo,
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        command = EditCommentCommand(
            comment_id=comment.id.value,
            editor_id=uuid4(),
            content="Updated.",
        )
        with pytest.raises(CommentNotFoundError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_edit_comment_not_member(self, comment: Comment, post: Post) -> None:
        mock_comment_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_comment_repo.get_by_id.return_value = comment
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = None

        handler = EditCommentHandler(
            comment_repository=mock_comment_repo,
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        command = EditCommentCommand(
            comment_id=comment.id.value,
            editor_id=uuid4(),
            content="Updated.",
        )
        with pytest.raises(NotCommunityMemberError):
            await handler.handle(command)


# ============================================================================
# DeleteCommentHandler Tests
# ============================================================================


class TestDeleteCommentHandler:
    @pytest.mark.asyncio
    @patch("src.community.application.handlers.delete_comment_handler.event_bus")
    async def test_delete_comment_hard_delete(
        self,
        mock_event_bus: AsyncMock,
        comment: Comment,
        post: Post,
        member: CommunityMember,
    ) -> None:
        mock_comment_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_comment_repo.get_by_id.return_value = comment
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = member
        mock_comment_repo.has_replies.return_value = False
        mock_event_bus.publish_all = AsyncMock()

        handler = DeleteCommentHandler(
            comment_repository=mock_comment_repo,
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        command = DeleteCommentCommand(
            comment_id=comment.id.value,
            deleter_id=member.user_id.value,
        )
        await handler.handle(command)

        mock_comment_repo.delete.assert_called_once_with(comment.id)
        mock_comment_repo.save.assert_not_called()

    @pytest.mark.asyncio
    @patch("src.community.application.handlers.delete_comment_handler.event_bus")
    async def test_delete_comment_soft_delete_with_replies(
        self,
        mock_event_bus: AsyncMock,
        comment: Comment,
        post: Post,
        member: CommunityMember,
    ) -> None:
        mock_comment_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_comment_repo.get_by_id.return_value = comment
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = member
        mock_comment_repo.has_replies.return_value = True
        mock_event_bus.publish_all = AsyncMock()

        handler = DeleteCommentHandler(
            comment_repository=mock_comment_repo,
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        command = DeleteCommentCommand(
            comment_id=comment.id.value,
            deleter_id=member.user_id.value,
        )
        await handler.handle(command)

        mock_comment_repo.save.assert_called_once()
        mock_comment_repo.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_comment_not_found(self) -> None:
        mock_comment_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_comment_repo.get_by_id.return_value = None

        handler = DeleteCommentHandler(
            comment_repository=mock_comment_repo,
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        command = DeleteCommentCommand(comment_id=uuid4(), deleter_id=uuid4())
        with pytest.raises(CommentNotFoundError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_delete_comment_post_not_found(self, comment: Comment) -> None:
        mock_comment_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_comment_repo.get_by_id.return_value = comment
        mock_post_repo.get_by_id.return_value = None

        handler = DeleteCommentHandler(
            comment_repository=mock_comment_repo,
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        command = DeleteCommentCommand(
            comment_id=comment.id.value,
            deleter_id=uuid4(),
        )
        with pytest.raises(CommentNotFoundError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_delete_comment_not_member(self, comment: Comment, post: Post) -> None:
        mock_comment_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_comment_repo.get_by_id.return_value = comment
        mock_post_repo.get_by_id.return_value = post
        mock_member_repo.get_by_user_and_community.return_value = None

        handler = DeleteCommentHandler(
            comment_repository=mock_comment_repo,
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )

        command = DeleteCommentCommand(
            comment_id=comment.id.value,
            deleter_id=uuid4(),
        )
        with pytest.raises(NotCommunityMemberError):
            await handler.handle(command)


# ============================================================================
# GetPostCommentsHandler Tests
# ============================================================================


class TestGetPostCommentsHandler:
    @pytest.mark.asyncio
    async def test_get_comments_success(self, comment: Comment) -> None:
        mock_comment_repo = AsyncMock()
        mock_reaction_repo = AsyncMock()
        mock_comment_repo.list_by_post.return_value = [comment]
        mock_reaction_repo.count_by_target.return_value = 5

        handler = GetPostCommentsHandler(
            comment_repository=mock_comment_repo,
            reaction_repository=mock_reaction_repo,
        )

        query = GetPostCommentsQuery(post_id=comment.post_id.value)
        result = await handler.handle(query)

        assert len(result) == 1
        assert result[0].comment == comment
        assert result[0].like_count == 5

    @pytest.mark.asyncio
    async def test_get_comments_empty(self) -> None:
        mock_comment_repo = AsyncMock()
        mock_reaction_repo = AsyncMock()
        mock_comment_repo.list_by_post.return_value = []

        handler = GetPostCommentsHandler(
            comment_repository=mock_comment_repo,
            reaction_repository=mock_reaction_repo,
        )

        query = GetPostCommentsQuery(post_id=uuid4())
        result = await handler.handle(query)

        assert result == []
