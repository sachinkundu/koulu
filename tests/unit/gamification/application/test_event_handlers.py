"""Tests for gamification event handlers."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from src.community.domain.events import CommentAdded, CommentLiked, CommentUnliked, PostCreated, PostLiked, PostUnliked
from src.community.domain.value_objects import CategoryId, CommentId, CommunityId, PostId, ReactionId
from src.gamification.application.event_handlers.community_event_handlers import (
    handle_comment_added,
    handle_comment_liked,
    handle_comment_unliked,
    handle_post_created,
    handle_post_liked,
    handle_post_unliked,
)
from src.gamification.domain.value_objects.point_source import PointSource
from src.identity.domain.value_objects import UserId


class TestPostCreatedHandler:
    @pytest.mark.asyncio
    @patch("src.gamification.application.event_handlers.community_event_handlers._get_award_handler")
    async def test_awards_2_points_to_author(self, mock_get_handler: AsyncMock) -> None:
        mock_handler = AsyncMock()
        mock_get_handler.return_value = mock_handler

        event = PostCreated(
            post_id=PostId(uuid4()),
            community_id=CommunityId(uuid4()),
            author_id=UserId(uuid4()),
            category_id=CategoryId(uuid4()),
            title="Test",
            content="Test content",
            image_url=None,
        )
        await handle_post_created(event)

        mock_handler.handle.assert_called_once()
        cmd = mock_handler.handle.call_args[0][0]
        assert cmd.source == PointSource.POST_CREATED
        assert cmd.user_id == event.author_id.value
        assert cmd.community_id == event.community_id.value
        assert cmd.source_id == event.post_id.value


class TestPostLikedHandler:
    @pytest.mark.asyncio
    @patch("src.gamification.application.event_handlers.community_event_handlers._get_award_handler")
    async def test_awards_1_point_to_author(self, mock_get_handler: AsyncMock) -> None:
        mock_handler = AsyncMock()
        mock_get_handler.return_value = mock_handler

        event = PostLiked(
            reaction_id=ReactionId(uuid4()),
            post_id=PostId(uuid4()),
            community_id=CommunityId(uuid4()),
            user_id=UserId(uuid4()),
            author_id=UserId(uuid4()),
        )
        await handle_post_liked(event)

        mock_handler.handle.assert_called_once()
        cmd = mock_handler.handle.call_args[0][0]
        assert cmd.source == PointSource.POST_LIKED
        assert cmd.user_id == event.author_id.value


class TestPostUnlikedHandler:
    @pytest.mark.asyncio
    @patch("src.gamification.application.event_handlers.community_event_handlers._get_deduct_handler")
    async def test_deducts_1_point_from_author(self, mock_get_handler: AsyncMock) -> None:
        mock_handler = AsyncMock()
        mock_get_handler.return_value = mock_handler

        event = PostUnliked(
            post_id=PostId(uuid4()),
            community_id=CommunityId(uuid4()),
            user_id=UserId(uuid4()),
            author_id=UserId(uuid4()),
        )
        await handle_post_unliked(event)

        mock_handler.handle.assert_called_once()
        cmd = mock_handler.handle.call_args[0][0]
        assert cmd.user_id == event.author_id.value
        assert cmd.source == PointSource.POST_LIKED


class TestCommentAddedHandler:
    @pytest.mark.asyncio
    @patch("src.gamification.application.event_handlers.community_event_handlers._get_award_handler")
    async def test_awards_1_point_to_author(self, mock_get_handler: AsyncMock) -> None:
        mock_handler = AsyncMock()
        mock_get_handler.return_value = mock_handler

        event = CommentAdded(
            comment_id=CommentId(uuid4()),
            post_id=PostId(uuid4()),
            community_id=CommunityId(uuid4()),
            author_id=UserId(uuid4()),
            content="Test comment",
            parent_comment_id=None,
        )
        await handle_comment_added(event)

        mock_handler.handle.assert_called_once()
        cmd = mock_handler.handle.call_args[0][0]
        assert cmd.source == PointSource.COMMENT_CREATED
        assert cmd.user_id == event.author_id.value


class TestCommentLikedHandler:
    @pytest.mark.asyncio
    @patch("src.gamification.application.event_handlers.community_event_handlers._get_award_handler")
    async def test_awards_1_point_to_comment_author(self, mock_get_handler: AsyncMock) -> None:
        mock_handler = AsyncMock()
        mock_get_handler.return_value = mock_handler

        event = CommentLiked(
            reaction_id=ReactionId(uuid4()),
            comment_id=CommentId(uuid4()),
            community_id=CommunityId(uuid4()),
            user_id=UserId(uuid4()),
            author_id=UserId(uuid4()),
        )
        await handle_comment_liked(event)

        mock_handler.handle.assert_called_once()
        cmd = mock_handler.handle.call_args[0][0]
        assert cmd.source == PointSource.COMMENT_LIKED
        assert cmd.user_id == event.author_id.value


class TestCommentUnlikedHandler:
    @pytest.mark.asyncio
    @patch("src.gamification.application.event_handlers.community_event_handlers._get_deduct_handler")
    async def test_deducts_1_point_from_comment_author(self, mock_get_handler: AsyncMock) -> None:
        mock_handler = AsyncMock()
        mock_get_handler.return_value = mock_handler

        event = CommentUnliked(
            comment_id=CommentId(uuid4()),
            community_id=CommunityId(uuid4()),
            user_id=UserId(uuid4()),
            author_id=UserId(uuid4()),
        )
        await handle_comment_unliked(event)

        mock_handler.handle.assert_called_once()
        cmd = mock_handler.handle.call_args[0][0]
        assert cmd.source == PointSource.COMMENT_LIKED
        assert cmd.user_id == event.author_id.value
