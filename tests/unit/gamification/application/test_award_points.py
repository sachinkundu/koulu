"""Tests for AwardPointsHandler."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.gamification.application.commands.award_points import (
    AwardPointsCommand,
    AwardPointsHandler,
)
from src.gamification.domain.entities.level_configuration import LevelConfiguration
from src.gamification.domain.entities.member_points import MemberPoints
from src.gamification.domain.value_objects.point_source import PointSource


class TestAwardPointsHandler:
    @pytest.fixture
    def member_points_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def level_config_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def handler(
        self, member_points_repo: AsyncMock, level_config_repo: AsyncMock
    ) -> AwardPointsHandler:
        return AwardPointsHandler(
            member_points_repo=member_points_repo,
            level_config_repo=level_config_repo,
        )

    async def test_creates_member_points_if_not_exists(
        self,
        handler: AwardPointsHandler,
        member_points_repo: AsyncMock,
        level_config_repo: AsyncMock,
    ) -> None:
        community_id = uuid4()
        user_id = uuid4()
        config = LevelConfiguration.create_default(community_id=community_id)

        member_points_repo.get_by_community_and_user.return_value = None
        level_config_repo.get_by_community.return_value = config

        command = AwardPointsCommand(
            community_id=community_id,
            user_id=user_id,
            source=PointSource.POST_CREATED,
            source_id=uuid4(),
        )
        await handler.handle(command)

        member_points_repo.save.assert_called_once()
        saved = member_points_repo.save.call_args[0][0]
        assert saved.total_points == 2
        assert saved.user_id == user_id

    async def test_awards_to_existing_member(
        self,
        handler: AwardPointsHandler,
        member_points_repo: AsyncMock,
        level_config_repo: AsyncMock,
    ) -> None:
        community_id = uuid4()
        user_id = uuid4()
        config = LevelConfiguration.create_default(community_id=community_id)
        existing = MemberPoints.create(community_id=community_id, user_id=user_id)

        member_points_repo.get_by_community_and_user.return_value = existing
        level_config_repo.get_by_community.return_value = config

        command = AwardPointsCommand(
            community_id=community_id,
            user_id=user_id,
            source=PointSource.POST_LIKED,
            source_id=uuid4(),
        )
        await handler.handle(command)

        member_points_repo.save.assert_called_once()
        saved = member_points_repo.save.call_args[0][0]
        assert saved.total_points == 1

    async def test_creates_default_config_if_not_exists(
        self,
        handler: AwardPointsHandler,
        member_points_repo: AsyncMock,
        level_config_repo: AsyncMock,
    ) -> None:
        community_id = uuid4()
        member_points_repo.get_by_community_and_user.return_value = None
        level_config_repo.get_by_community.return_value = None  # No config yet

        command = AwardPointsCommand(
            community_id=community_id,
            user_id=uuid4(),
            source=PointSource.POST_CREATED,
            source_id=uuid4(),
        )
        await handler.handle(command)

        # Should have saved a default config
        level_config_repo.save.assert_called_once()
