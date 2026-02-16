"""Tests for UpdateLevelConfigHandler."""

# ruff: noqa: ARG002

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from src.gamification.application.commands.update_level_config import (
    LevelUpdate,
    UpdateLevelConfigCommand,
    UpdateLevelConfigHandler,
)
from src.gamification.domain.entities.level_configuration import (
    LevelConfiguration,
)
from src.gamification.domain.entities.member_points import MemberPoints
from src.gamification.domain.exceptions import InvalidThresholdError


def _make_valid_level_updates() -> list[LevelUpdate]:
    """Create a valid set of 9 LevelUpdate items."""
    return [
        LevelUpdate(level=1, name="Newbie", threshold=0),
        LevelUpdate(level=2, name="Beginner", threshold=10),
        LevelUpdate(level=3, name="Intermediate", threshold=25),
        LevelUpdate(level=4, name="Advanced", threshold=50),
        LevelUpdate(level=5, name="Expert", threshold=80),
        LevelUpdate(level=6, name="Master", threshold=120),
        LevelUpdate(level=7, name="Grandmaster", threshold=170),
        LevelUpdate(level=8, name="Champion", threshold=230),
        LevelUpdate(level=9, name="Legend", threshold=300),
    ]


class TestUpdateLevelConfigHandler:
    @pytest.fixture
    def member_points_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def level_config_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def handler(
        self, member_points_repo: AsyncMock, level_config_repo: AsyncMock
    ) -> UpdateLevelConfigHandler:
        return UpdateLevelConfigHandler(
            member_points_repo=member_points_repo,
            level_config_repo=level_config_repo,
        )

    @patch(
        "src.gamification.application.commands.update_level_config.event_bus",
        new_callable=AsyncMock,
    )
    async def test_updates_config_successfully(
        self,
        mock_event_bus: AsyncMock,
        handler: UpdateLevelConfigHandler,
        member_points_repo: AsyncMock,
        level_config_repo: AsyncMock,
    ) -> None:
        community_id = uuid4()
        config = LevelConfiguration.create_default(community_id=community_id)

        level_config_repo.get_by_community.return_value = config
        member_points_repo.list_by_community.return_value = []

        command = UpdateLevelConfigCommand(
            community_id=community_id,
            admin_user_id=uuid4(),
            levels=_make_valid_level_updates(),
        )
        await handler.handle(command)

        level_config_repo.save.assert_called()
        assert config.levels[0].name == "Newbie"

    @patch(
        "src.gamification.application.commands.update_level_config.event_bus",
        new_callable=AsyncMock,
    )
    async def test_recalculates_member_levels_when_thresholds_change(
        self,
        mock_event_bus: AsyncMock,
        handler: UpdateLevelConfigHandler,
        member_points_repo: AsyncMock,
        level_config_repo: AsyncMock,
    ) -> None:
        community_id = uuid4()
        config = LevelConfiguration.create_default(community_id=community_id)

        # Member at level 2 with 15 points; new thresholds lower level 3 to 12
        mp = MemberPoints.create(community_id=community_id, user_id=uuid4())
        mp.total_points = 15
        mp.current_level = 2

        level_config_repo.get_by_community.return_value = config
        member_points_repo.list_by_community.return_value = [mp]

        # New config lowers level 3 threshold from 30 to 12
        updates = _make_valid_level_updates()
        updates[2] = LevelUpdate(level=3, name="Intermediate", threshold=12)

        command = UpdateLevelConfigCommand(
            community_id=community_id,
            admin_user_id=uuid4(),
            levels=updates,
        )
        await handler.handle(command)

        # Member should have been saved (recalculated)
        member_points_repo.save.assert_called()
        # Member should now be level 3 (15 points >= 12 threshold)
        assert mp.current_level == 3

    @patch(
        "src.gamification.application.commands.update_level_config.event_bus",
        new_callable=AsyncMock,
    )
    async def test_ratchet_preserved_when_thresholds_increase(
        self,
        mock_event_bus: AsyncMock,
        handler: UpdateLevelConfigHandler,
        member_points_repo: AsyncMock,
        level_config_repo: AsyncMock,
    ) -> None:
        community_id = uuid4()
        config = LevelConfiguration.create_default(community_id=community_id)

        # Member at level 3 with 35 points
        mp = MemberPoints.create(community_id=community_id, user_id=uuid4())
        mp.total_points = 35
        mp.current_level = 3

        level_config_repo.get_by_community.return_value = config
        member_points_repo.list_by_community.return_value = [mp]

        # New config raises level 3 threshold from 30 to 40
        # Member's 35 points < 40, but ratchet means level stays at 3
        updates = _make_valid_level_updates()
        updates[2] = LevelUpdate(level=3, name="Intermediate", threshold=40)
        # Adjust level 4+ to keep strictly increasing
        updates[3] = LevelUpdate(level=4, name="Advanced", threshold=60)

        command = UpdateLevelConfigCommand(
            community_id=community_id,
            admin_user_id=uuid4(),
            levels=updates,
        )
        await handler.handle(command)

        # Level should NOT decrease due to ratchet
        assert mp.current_level == 3

    @patch(
        "src.gamification.application.commands.update_level_config.event_bus",
        new_callable=AsyncMock,
    )
    async def test_publishes_level_up_events(
        self,
        mock_event_bus: AsyncMock,
        handler: UpdateLevelConfigHandler,
        member_points_repo: AsyncMock,
        level_config_repo: AsyncMock,
    ) -> None:
        community_id = uuid4()
        config = LevelConfiguration.create_default(community_id=community_id)

        # Member at level 1 with 50 points; new thresholds lower level 2 to 5
        mp = MemberPoints.create(community_id=community_id, user_id=uuid4())
        mp.total_points = 50
        mp.current_level = 1

        level_config_repo.get_by_community.return_value = config
        member_points_repo.list_by_community.return_value = [mp]

        updates = _make_valid_level_updates()

        command = UpdateLevelConfigCommand(
            community_id=community_id,
            admin_user_id=uuid4(),
            levels=updates,
        )
        await handler.handle(command)

        # Events should be published for level-up
        mock_event_bus.publish_all.assert_called()

    @patch(
        "src.gamification.application.commands.update_level_config.event_bus",
        new_callable=AsyncMock,
    )
    async def test_no_recalculation_when_only_names_change(
        self,
        mock_event_bus: AsyncMock,
        handler: UpdateLevelConfigHandler,
        member_points_repo: AsyncMock,
        level_config_repo: AsyncMock,
    ) -> None:
        community_id = uuid4()
        config = LevelConfiguration.create_default(community_id=community_id)

        level_config_repo.get_by_community.return_value = config
        member_points_repo.list_by_community.return_value = []

        # Same thresholds as default, just different names
        updates = [
            LevelUpdate(level=1, name="Novice", threshold=0),
            LevelUpdate(level=2, name="Apprentice", threshold=10),
            LevelUpdate(level=3, name="Journeyman", threshold=30),
            LevelUpdate(level=4, name="Adept", threshold=60),
            LevelUpdate(level=5, name="Veteran", threshold=100),
            LevelUpdate(level=6, name="Elite", threshold=150),
            LevelUpdate(level=7, name="Overlord", threshold=210),
            LevelUpdate(level=8, name="Mythic", threshold=280),
            LevelUpdate(level=9, name="Eternal", threshold=360),
        ]

        command = UpdateLevelConfigCommand(
            community_id=community_id,
            admin_user_id=uuid4(),
            levels=updates,
        )
        await handler.handle(command)

        # list_by_community should not be called since thresholds didn't change
        member_points_repo.list_by_community.assert_not_called()

    async def test_creates_default_config_when_none_exists(
        self,
        handler: UpdateLevelConfigHandler,
        member_points_repo: AsyncMock,
        level_config_repo: AsyncMock,
    ) -> None:
        community_id = uuid4()

        level_config_repo.get_by_community.return_value = None
        member_points_repo.list_by_community.return_value = []

        command = UpdateLevelConfigCommand(
            community_id=community_id,
            admin_user_id=uuid4(),
            levels=_make_valid_level_updates(),
        )

        with patch(
            "src.gamification.application.commands.update_level_config.event_bus",
            new_callable=AsyncMock,
        ):
            await handler.handle(command)

        # Should have saved twice: once for initial default, once after update
        assert level_config_repo.save.call_count == 2

    async def test_invalid_config_raises_domain_exception(
        self,
        handler: UpdateLevelConfigHandler,
        member_points_repo: AsyncMock,
        level_config_repo: AsyncMock,
    ) -> None:
        community_id = uuid4()
        config = LevelConfiguration.create_default(community_id=community_id)

        level_config_repo.get_by_community.return_value = config

        # Invalid: level 1 threshold not 0
        updates = _make_valid_level_updates()
        updates[0] = LevelUpdate(level=1, name="Newbie", threshold=5)

        command = UpdateLevelConfigCommand(
            community_id=community_id,
            admin_user_id=uuid4(),
            levels=updates,
        )

        with pytest.raises(InvalidThresholdError):
            await handler.handle(command)
