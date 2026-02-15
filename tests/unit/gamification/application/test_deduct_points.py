"""Tests for DeductPointsHandler."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.gamification.application.commands.deduct_points import (
    DeductPointsCommand,
    DeductPointsHandler,
)
from src.gamification.domain.entities.level_configuration import LevelConfiguration
from src.gamification.domain.entities.member_points import MemberPoints
from src.gamification.domain.value_objects.point_source import PointSource


class TestDeductPointsHandler:
    @pytest.fixture
    def member_points_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def level_config_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def handler(
        self, member_points_repo: AsyncMock, level_config_repo: AsyncMock
    ) -> DeductPointsHandler:
        return DeductPointsHandler(
            member_points_repo=member_points_repo,
            level_config_repo=level_config_repo,
        )

    async def test_deducts_from_existing_member(
        self,
        handler: DeductPointsHandler,
        member_points_repo: AsyncMock,
        level_config_repo: AsyncMock,
    ) -> None:
        community_id = uuid4()
        user_id = uuid4()
        config = LevelConfiguration.create_default(community_id=community_id)
        existing = MemberPoints.create(community_id=community_id, user_id=user_id)
        existing.total_points = 5

        member_points_repo.get_by_community_and_user.return_value = existing
        level_config_repo.get_by_community.return_value = config

        command = DeductPointsCommand(
            community_id=community_id,
            user_id=user_id,
            source=PointSource.POST_LIKED,
            source_id=uuid4(),
        )
        await handler.handle(command)

        member_points_repo.save.assert_called_once()
        saved = member_points_repo.save.call_args[0][0]
        assert saved.total_points == 4

    async def test_noop_if_member_not_found(
        self,
        handler: DeductPointsHandler,
        member_points_repo: AsyncMock,
        level_config_repo: AsyncMock,
    ) -> None:
        community_id = uuid4()
        config = LevelConfiguration.create_default(community_id=community_id)
        member_points_repo.get_by_community_and_user.return_value = None
        level_config_repo.get_by_community.return_value = config

        command = DeductPointsCommand(
            community_id=community_id,
            user_id=uuid4(),
            source=PointSource.POST_LIKED,
            source_id=uuid4(),
        )
        await handler.handle(command)

        member_points_repo.save.assert_not_called()
