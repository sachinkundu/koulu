"""Unit tests for reaction-related handlers (Like/Unlike Post, Like/Unlike Comment)."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from src.community.application.commands import (
    LikeCommentCommand,
    LikePostCommand,
    UnlikeCommentCommand,
    UnlikePostCommand,
)
from src.community.application.handlers.like_comment_handler import LikeCommentHandler
from src.community.application.handlers.like_post_handler import LikePostHandler
from src.community.application.handlers.unlike_comment_handler import UnlikeCommentHandler
from src.community.application.handlers.unlike_post_handler import UnlikePostHandler
from src.community.domain.entities import Comment, Post, Reaction
from src.community.domain.exceptions import CommentNotFoundError, PostNotFoundError
from src.community.domain.value_objects import (
    CategoryId,
    CommentContent,
    CommentId,
    CommunityId,
    PostContent,
    PostId,
    PostTitle,
)
from src.identity.domain.value_objects import UserId


@pytest.fixture
def user_id() -> UserId:
    return UserId(uuid4())


@pytest.fixture
def post() -> Post:
    return Post.create(
        community_id=CommunityId(uuid4()),
        author_id=UserId(uuid4()),
        category_id=CategoryId(uuid4()),
        title=PostTitle("Test Post"),
        content=PostContent("Test content for the post body."),
    )


@pytest.fixture
def comment() -> Comment:
    return Comment.create(
        post_id=PostId(uuid4()),
        author_id=UserId(uuid4()),
        content=CommentContent("A test comment content here."),
        community_id=CommunityId(uuid4()),
    )


@pytest.fixture
def reaction(user_id: UserId, post: Post) -> Reaction:
    return Reaction.create(
        user_id=user_id,
        target_type="post",
        target_id=post.id,
    )


# ============================================================================
# LikePostHandler Tests
# ============================================================================


class TestLikePostHandler:
    @pytest.mark.asyncio
    @patch("src.community.application.handlers.like_post_handler.event_bus")
    async def test_like_post_success(
        self,
        mock_event_bus: AsyncMock,
        post: Post,
        user_id: UserId,
    ) -> None:
        mock_reaction_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post
        mock_reaction_repo.find_by_user_and_target.return_value = None
        mock_event_bus.publish_all = AsyncMock()

        handler = LikePostHandler(
            reaction_repository=mock_reaction_repo,
            post_repository=mock_post_repo,
        )

        command = LikePostCommand(post_id=post.id.value, user_id=user_id.value)
        await handler.handle(command)

        mock_reaction_repo.save.assert_called_once()
        mock_event_bus.publish_all.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.community.application.handlers.like_post_handler.event_bus")
    async def test_like_post_already_liked_idempotent(
        self,
        _mock_event_bus: AsyncMock,
        post: Post,
        user_id: UserId,
        reaction: Reaction,
    ) -> None:
        mock_reaction_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = post
        mock_reaction_repo.find_by_user_and_target.return_value = reaction

        handler = LikePostHandler(
            reaction_repository=mock_reaction_repo,
            post_repository=mock_post_repo,
        )

        command = LikePostCommand(post_id=post.id.value, user_id=user_id.value)
        await handler.handle(command)

        mock_reaction_repo.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_like_post_not_found(self, user_id: UserId) -> None:
        mock_reaction_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_post_repo.get_by_id.return_value = None

        handler = LikePostHandler(
            reaction_repository=mock_reaction_repo,
            post_repository=mock_post_repo,
        )

        command = LikePostCommand(post_id=uuid4(), user_id=user_id.value)
        with pytest.raises(PostNotFoundError):
            await handler.handle(command)


# ============================================================================
# UnlikePostHandler Tests
# ============================================================================


class TestUnlikePostHandler:
    @pytest.mark.asyncio
    @patch("src.community.application.handlers.unlike_post_handler.event_bus")
    async def test_unlike_post_success(
        self,
        mock_event_bus: AsyncMock,
        post: Post,
        user_id: UserId,
        reaction: Reaction,
    ) -> None:
        mock_reaction_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_reaction_repo.find_by_user_and_target.return_value = reaction
        mock_post_repo.get_by_id.return_value = post
        mock_event_bus.publish_all = AsyncMock()

        handler = UnlikePostHandler(
            reaction_repository=mock_reaction_repo,
            post_repository=mock_post_repo,
        )

        command = UnlikePostCommand(post_id=post.id.value, user_id=user_id.value)
        await handler.handle(command)

        mock_reaction_repo.delete.assert_called_once_with(reaction.id)
        mock_event_bus.publish_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_unlike_post_not_liked_idempotent(self, user_id: UserId) -> None:
        mock_reaction_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_reaction_repo.find_by_user_and_target.return_value = None

        handler = UnlikePostHandler(
            reaction_repository=mock_reaction_repo,
            post_repository=mock_post_repo,
        )

        command = UnlikePostCommand(post_id=uuid4(), user_id=user_id.value)
        await handler.handle(command)

        mock_reaction_repo.delete.assert_not_called()


# ============================================================================
# LikeCommentHandler Tests
# ============================================================================


class TestLikeCommentHandler:
    @pytest.mark.asyncio
    @patch("src.community.application.handlers.like_comment_handler.event_bus")
    async def test_like_comment_success(
        self,
        mock_event_bus: AsyncMock,
        comment: Comment,
        post: Post,
        user_id: UserId,
    ) -> None:
        mock_reaction_repo = AsyncMock()
        mock_comment_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_comment_repo.get_by_id.return_value = comment
        mock_reaction_repo.find_by_user_and_target.return_value = None
        mock_post_repo.get_by_id.return_value = post
        mock_event_bus.publish_all = AsyncMock()

        handler = LikeCommentHandler(
            reaction_repository=mock_reaction_repo,
            comment_repository=mock_comment_repo,
            post_repository=mock_post_repo,
        )

        command = LikeCommentCommand(comment_id=comment.id.value, user_id=user_id.value)
        await handler.handle(command)

        mock_reaction_repo.save.assert_called_once()
        mock_event_bus.publish_all.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.community.application.handlers.like_comment_handler.event_bus")
    async def test_like_comment_already_liked_idempotent(
        self,
        _mock_event_bus: AsyncMock,
        comment: Comment,
        user_id: UserId,
    ) -> None:
        existing_reaction = Reaction.create(
            user_id=user_id,
            target_type="comment",
            target_id=comment.id,
        )
        mock_reaction_repo = AsyncMock()
        mock_comment_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_comment_repo.get_by_id.return_value = comment
        mock_reaction_repo.find_by_user_and_target.return_value = existing_reaction

        handler = LikeCommentHandler(
            reaction_repository=mock_reaction_repo,
            comment_repository=mock_comment_repo,
            post_repository=mock_post_repo,
        )

        command = LikeCommentCommand(comment_id=comment.id.value, user_id=user_id.value)
        await handler.handle(command)

        mock_reaction_repo.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_like_comment_not_found(self, user_id: UserId) -> None:
        mock_reaction_repo = AsyncMock()
        mock_comment_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_comment_repo.get_by_id.return_value = None

        handler = LikeCommentHandler(
            reaction_repository=mock_reaction_repo,
            comment_repository=mock_comment_repo,
            post_repository=mock_post_repo,
        )

        command = LikeCommentCommand(comment_id=uuid4(), user_id=user_id.value)
        with pytest.raises(CommentNotFoundError):
            await handler.handle(command)


# ============================================================================
# UnlikeCommentHandler Tests
# ============================================================================


class TestUnlikeCommentHandler:
    @pytest.mark.asyncio
    @patch("src.community.application.handlers.unlike_comment_handler.event_bus")
    async def test_unlike_comment_success(
        self,
        mock_event_bus: AsyncMock,
        comment: Comment,
        post: Post,
        user_id: UserId,
    ) -> None:
        existing_reaction = Reaction.create(
            user_id=user_id,
            target_type="comment",
            target_id=comment.id,
        )
        mock_reaction_repo = AsyncMock()
        mock_comment_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_reaction_repo.find_by_user_and_target.return_value = existing_reaction
        mock_comment_repo.get_by_id.return_value = comment
        mock_post_repo.get_by_id.return_value = post
        mock_event_bus.publish_all = AsyncMock()

        handler = UnlikeCommentHandler(
            reaction_repository=mock_reaction_repo,
            comment_repository=mock_comment_repo,
            post_repository=mock_post_repo,
        )

        command = UnlikeCommentCommand(comment_id=comment.id.value, user_id=user_id.value)
        await handler.handle(command)

        mock_reaction_repo.delete.assert_called_once_with(existing_reaction.id)

    @pytest.mark.asyncio
    async def test_unlike_comment_not_liked_idempotent(self, user_id: UserId) -> None:
        mock_reaction_repo = AsyncMock()
        mock_comment_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_reaction_repo.find_by_user_and_target.return_value = None

        handler = UnlikeCommentHandler(
            reaction_repository=mock_reaction_repo,
            comment_repository=mock_comment_repo,
            post_repository=mock_post_repo,
        )

        command = UnlikeCommentCommand(comment_id=uuid4(), user_id=user_id.value)
        await handler.handle(command)

        mock_reaction_repo.delete.assert_not_called()
