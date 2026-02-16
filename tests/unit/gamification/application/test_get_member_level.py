"""Tests for GetMemberLevelHandler."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.gamification.application.queries.get_member_level import (
    GetMemberLevelHandler,
    GetMemberLevelQuery,
)
from src.gamification.domain.entities.level_configuration import LevelConfiguration
from src.gamification.domain.entities.member_points import MemberPoints


class TestGetMemberLevelHandler:
    @pytest.fixture
    def member_points_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def level_config_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def handler(
        self, member_points_repo: AsyncMock, level_config_repo: AsyncMock
    ) -> GetMemberLevelHandler:
        return GetMemberLevelHandler(
            member_points_repo=member_points_repo,
            level_config_repo=level_config_repo,
        )

    async def test_returns_member_level_for_existing_member(
        self,
        handler: GetMemberLevelHandler,
        member_points_repo: AsyncMock,
        level_config_repo: AsyncMock,
    ) -> None:
        community_id = uuid4()
        user_id = uuid4()
        config = LevelConfiguration.create_default(community_id=community_id)
        mp = MemberPoints.create(community_id=community_id, user_id=user_id)
        mp.total_points = 15
        mp.current_level = 2

        member_points_repo.get_by_community_and_user.return_value = mp
        level_config_repo.get_by_community.return_value = config

        query = GetMemberLevelQuery(
            community_id=community_id,
            user_id=user_id,
            requesting_user_id=user_id,  # viewing own profile
        )
        result = await handler.handle(query)

        assert result.level == 2
        assert result.level_name == "Practitioner"
        assert result.total_points == 15
        assert result.points_to_next_level == 15  # 30 - 15

    async def test_new_member_returns_level_1(
        self,
        handler: GetMemberLevelHandler,
        member_points_repo: AsyncMock,
        level_config_repo: AsyncMock,
    ) -> None:
        community_id = uuid4()
        config = LevelConfiguration.create_default(community_id=community_id)
        member_points_repo.get_by_community_and_user.return_value = None
        level_config_repo.get_by_community.return_value = config

        query = GetMemberLevelQuery(
            community_id=community_id,
            user_id=uuid4(),
            requesting_user_id=uuid4(),
        )
        result = await handler.handle(query)

        assert result.level == 1
        assert result.level_name == "Student"
        assert result.total_points == 0

    async def test_points_to_next_level_null_for_other_member(
        self,
        handler: GetMemberLevelHandler,
        member_points_repo: AsyncMock,
        level_config_repo: AsyncMock,
    ) -> None:
        community_id = uuid4()
        user_id = uuid4()
        other_user_id = uuid4()
        config = LevelConfiguration.create_default(community_id=community_id)
        mp = MemberPoints.create(community_id=community_id, user_id=user_id)

        member_points_repo.get_by_community_and_user.return_value = mp
        level_config_repo.get_by_community.return_value = config

        query = GetMemberLevelQuery(
            community_id=community_id,
            user_id=user_id,
            requesting_user_id=other_user_id,  # different user
        )
        result = await handler.handle(query)

        assert result.points_to_next_level is None  # private to own profile

    async def test_level_9_has_no_points_to_next(
        self,
        handler: GetMemberLevelHandler,
        member_points_repo: AsyncMock,
        level_config_repo: AsyncMock,
    ) -> None:
        community_id = uuid4()
        user_id = uuid4()
        config = LevelConfiguration.create_default(community_id=community_id)
        mp = MemberPoints.create(community_id=community_id, user_id=user_id)
        mp.total_points = 400
        mp.current_level = 9

        member_points_repo.get_by_community_and_user.return_value = mp
        level_config_repo.get_by_community.return_value = config

        query = GetMemberLevelQuery(
            community_id=community_id,
            user_id=user_id,
            requesting_user_id=user_id,
        )
        result = await handler.handle(query)

        assert result.is_max_level is True
        assert result.points_to_next_level is None
