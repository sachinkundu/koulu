"""Tests for GetLevelDefinitionsHandler."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.gamification.application.queries.get_level_definitions import (
    GetLevelDefinitionsHandler,
    GetLevelDefinitionsQuery,
)
from src.gamification.domain.entities.level_configuration import LevelConfiguration
from src.gamification.domain.entities.member_points import MemberPoints


class TestGetLevelDefinitionsHandler:
    @pytest.fixture
    def member_points_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def level_config_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def handler(
        self, member_points_repo: AsyncMock, level_config_repo: AsyncMock
    ) -> GetLevelDefinitionsHandler:
        return GetLevelDefinitionsHandler(
            member_points_repo=member_points_repo,
            level_config_repo=level_config_repo,
        )

    async def test_returns_all_9_levels(
        self,
        handler: GetLevelDefinitionsHandler,
        member_points_repo: AsyncMock,
        level_config_repo: AsyncMock,
    ) -> None:
        community_id = uuid4()
        user_id = uuid4()
        config = LevelConfiguration.create_default(community_id=community_id)

        level_config_repo.get_by_community.return_value = config
        member_points_repo.list_by_community.return_value = []
        member_points_repo.get_by_community_and_user.return_value = None

        query = GetLevelDefinitionsQuery(
            community_id=community_id,
            requesting_user_id=user_id,
        )
        result = await handler.handle(query)

        assert len(result.levels) == 9
        assert result.levels[0].name == "Student"
        assert result.levels[0].threshold == 0
        assert result.levels[8].name == "Icon"

    async def test_distribution_calculation_with_members(
        self,
        handler: GetLevelDefinitionsHandler,
        member_points_repo: AsyncMock,
        level_config_repo: AsyncMock,
    ) -> None:
        community_id = uuid4()
        user_id = uuid4()
        config = LevelConfiguration.create_default(community_id=community_id)

        # Create 4 members: 2 at level 1, 1 at level 2, 1 at level 3
        members = []
        for level, count in [(1, 2), (2, 1), (3, 1)]:
            for _ in range(count):
                mp = MemberPoints.create(community_id=community_id, user_id=uuid4())
                mp.current_level = level
                members.append(mp)

        level_config_repo.get_by_community.return_value = config
        member_points_repo.list_by_community.return_value = members
        member_points_repo.get_by_community_and_user.return_value = None

        query = GetLevelDefinitionsQuery(
            community_id=community_id,
            requesting_user_id=user_id,
        )
        result = await handler.handle(query)

        # 2/4 = 50%, 1/4 = 25%, 1/4 = 25%
        assert result.levels[0].member_percentage == 50.0
        assert result.levels[1].member_percentage == 25.0
        assert result.levels[2].member_percentage == 25.0
        # Remaining levels should be 0%
        for level_def in result.levels[3:]:
            assert level_def.member_percentage == 0.0

    async def test_distribution_zero_members(
        self,
        handler: GetLevelDefinitionsHandler,
        member_points_repo: AsyncMock,
        level_config_repo: AsyncMock,
    ) -> None:
        community_id = uuid4()
        config = LevelConfiguration.create_default(community_id=community_id)

        level_config_repo.get_by_community.return_value = config
        member_points_repo.list_by_community.return_value = []
        member_points_repo.get_by_community_and_user.return_value = None

        query = GetLevelDefinitionsQuery(
            community_id=community_id,
            requesting_user_id=uuid4(),
        )
        result = await handler.handle(query)

        for level_def in result.levels:
            assert level_def.member_percentage == 0.0

    async def test_current_user_level_returned(
        self,
        handler: GetLevelDefinitionsHandler,
        member_points_repo: AsyncMock,
        level_config_repo: AsyncMock,
    ) -> None:
        community_id = uuid4()
        user_id = uuid4()
        config = LevelConfiguration.create_default(community_id=community_id)

        mp = MemberPoints.create(community_id=community_id, user_id=user_id)
        mp.current_level = 5

        level_config_repo.get_by_community.return_value = config
        member_points_repo.list_by_community.return_value = [mp]
        member_points_repo.get_by_community_and_user.return_value = mp

        query = GetLevelDefinitionsQuery(
            community_id=community_id,
            requesting_user_id=user_id,
        )
        result = await handler.handle(query)

        assert result.current_user_level == 5

    async def test_new_user_defaults_to_level_1(
        self,
        handler: GetLevelDefinitionsHandler,
        member_points_repo: AsyncMock,
        level_config_repo: AsyncMock,
    ) -> None:
        community_id = uuid4()
        config = LevelConfiguration.create_default(community_id=community_id)

        level_config_repo.get_by_community.return_value = config
        member_points_repo.list_by_community.return_value = []
        member_points_repo.get_by_community_and_user.return_value = None

        query = GetLevelDefinitionsQuery(
            community_id=community_id,
            requesting_user_id=uuid4(),
        )
        result = await handler.handle(query)

        assert result.current_user_level == 1

    async def test_creates_default_config_when_none_exists(
        self,
        handler: GetLevelDefinitionsHandler,
        member_points_repo: AsyncMock,
        level_config_repo: AsyncMock,
    ) -> None:
        community_id = uuid4()

        level_config_repo.get_by_community.return_value = None
        member_points_repo.list_by_community.return_value = []
        member_points_repo.get_by_community_and_user.return_value = None

        query = GetLevelDefinitionsQuery(
            community_id=community_id,
            requesting_user_id=uuid4(),
        )
        result = await handler.handle(query)

        # Should use default config
        assert len(result.levels) == 9
        assert result.levels[0].name == "Student"
