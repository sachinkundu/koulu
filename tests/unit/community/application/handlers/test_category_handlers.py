"""Unit tests for category CRUD handlers."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.community.application.commands import (
    CreateCategoryCommand,
    DeleteCategoryCommand,
    UpdateCategoryCommand,
)
from src.community.application.handlers.create_category_handler import (
    CreateCategoryHandler,
)
from src.community.application.handlers.delete_category_handler import (
    DeleteCategoryHandler,
)
from src.community.application.handlers.update_category_handler import (
    UpdateCategoryHandler,
)
from src.community.domain.entities import Category, CommunityMember
from src.community.domain.exceptions import (
    CannotManageCategoriesError,
    CategoryHasPostsError,
    CategoryNameExistsError,
    CategoryNotFoundError,
    NotCommunityMemberError,
)
from src.community.domain.value_objects import CommunityId, MemberRole
from src.identity.domain.value_objects import UserId


@pytest.fixture
def community_id() -> CommunityId:
    return CommunityId(uuid4())


@pytest.fixture
def admin_member(community_id: CommunityId) -> CommunityMember:
    return CommunityMember.create(
        user_id=UserId(uuid4()),
        community_id=community_id,
        role=MemberRole.ADMIN,
    )


@pytest.fixture
def regular_member(community_id: CommunityId) -> CommunityMember:
    return CommunityMember.create(
        user_id=UserId(uuid4()),
        community_id=community_id,
        role=MemberRole.MEMBER,
    )


@pytest.fixture
def mod_member(community_id: CommunityId) -> CommunityMember:
    return CommunityMember.create(
        user_id=UserId(uuid4()),
        community_id=community_id,
        role=MemberRole.MODERATOR,
    )


@pytest.fixture
def category(community_id: CommunityId) -> Category:
    return Category.create(
        community_id=community_id,
        name="Test Category",
        slug="test-category",
        emoji="📝",
        description="A test category",
    )


class TestCreateCategoryHandler:
    @pytest.mark.asyncio
    async def test_create_category_success(
        self,
        community_id: CommunityId,
        admin_member: CommunityMember,
    ) -> None:
        mock_category_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_member_repo.get_by_user_and_community.return_value = admin_member
        mock_category_repo.exists_by_name.return_value = False

        handler = CreateCategoryHandler(
            category_repository=mock_category_repo,
            member_repository=mock_member_repo,
        )
        command = CreateCategoryCommand(
            community_id=community_id.value,
            creator_id=admin_member.user_id.value,
            name="Resources",
            slug="resources",
            emoji="📚",
            description="Helpful resources",
        )
        result = await handler.handle(command)
        assert result.name == "Resources"
        mock_category_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_category_not_admin(
        self,
        community_id: CommunityId,
        regular_member: CommunityMember,
    ) -> None:
        mock_category_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_member_repo.get_by_user_and_community.return_value = regular_member

        handler = CreateCategoryHandler(
            category_repository=mock_category_repo,
            member_repository=mock_member_repo,
        )
        command = CreateCategoryCommand(
            community_id=community_id.value,
            creator_id=regular_member.user_id.value,
            name="Resources",
            slug="resources",
            emoji="📚",
        )
        with pytest.raises(CannotManageCategoriesError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_create_category_mod_cannot(
        self,
        community_id: CommunityId,
        mod_member: CommunityMember,
    ) -> None:
        mock_category_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_member_repo.get_by_user_and_community.return_value = mod_member

        handler = CreateCategoryHandler(
            category_repository=mock_category_repo,
            member_repository=mock_member_repo,
        )
        command = CreateCategoryCommand(
            community_id=community_id.value,
            creator_id=mod_member.user_id.value,
            name="Resources",
            slug="resources",
            emoji="📚",
        )
        with pytest.raises(CannotManageCategoriesError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_create_category_name_exists(
        self,
        community_id: CommunityId,
        admin_member: CommunityMember,
    ) -> None:
        mock_category_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_member_repo.get_by_user_and_community.return_value = admin_member
        mock_category_repo.exists_by_name.return_value = True

        handler = CreateCategoryHandler(
            category_repository=mock_category_repo,
            member_repository=mock_member_repo,
        )
        command = CreateCategoryCommand(
            community_id=community_id.value,
            creator_id=admin_member.user_id.value,
            name="Existing",
            slug="existing",
            emoji="📚",
        )
        with pytest.raises(CategoryNameExistsError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_create_category_not_member(self, community_id: CommunityId) -> None:
        mock_category_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_member_repo.get_by_user_and_community.return_value = None

        handler = CreateCategoryHandler(
            category_repository=mock_category_repo,
            member_repository=mock_member_repo,
        )
        command = CreateCategoryCommand(
            community_id=community_id.value,
            creator_id=uuid4(),
            name="Resources",
            slug="resources",
            emoji="📚",
        )
        with pytest.raises(NotCommunityMemberError):
            await handler.handle(command)


class TestUpdateCategoryHandler:
    @pytest.mark.asyncio
    async def test_update_category_success(
        self,
        community_id: CommunityId,
        admin_member: CommunityMember,
        category: Category,
    ) -> None:
        mock_category_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_member_repo.get_by_user_and_community.return_value = admin_member
        mock_category_repo.get_by_id.return_value = category
        mock_category_repo.exists_by_name.return_value = False

        handler = UpdateCategoryHandler(
            category_repository=mock_category_repo,
            member_repository=mock_member_repo,
        )
        command = UpdateCategoryCommand(
            category_id=category.id.value,
            updater_id=admin_member.user_id.value,
            community_id=community_id.value,
            name="Updated Name",
        )
        await handler.handle(command)
        mock_category_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_category_not_admin(
        self,
        community_id: CommunityId,
        regular_member: CommunityMember,
    ) -> None:
        mock_category_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_member_repo.get_by_user_and_community.return_value = regular_member

        handler = UpdateCategoryHandler(
            category_repository=mock_category_repo,
            member_repository=mock_member_repo,
        )
        command = UpdateCategoryCommand(
            category_id=uuid4(),
            updater_id=regular_member.user_id.value,
            community_id=community_id.value,
            name="New Name",
        )
        with pytest.raises(CannotManageCategoriesError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_update_category_not_found(
        self,
        community_id: CommunityId,
        admin_member: CommunityMember,
    ) -> None:
        mock_category_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_member_repo.get_by_user_and_community.return_value = admin_member
        mock_category_repo.get_by_id.return_value = None

        handler = UpdateCategoryHandler(
            category_repository=mock_category_repo,
            member_repository=mock_member_repo,
        )
        command = UpdateCategoryCommand(
            category_id=uuid4(),
            updater_id=admin_member.user_id.value,
            community_id=community_id.value,
            name="New Name",
        )
        with pytest.raises(CategoryNotFoundError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_update_category_name_conflict(
        self,
        community_id: CommunityId,
        admin_member: CommunityMember,
        category: Category,
    ) -> None:
        mock_category_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_member_repo.get_by_user_and_community.return_value = admin_member
        mock_category_repo.get_by_id.return_value = category
        mock_category_repo.exists_by_name.return_value = True

        handler = UpdateCategoryHandler(
            category_repository=mock_category_repo,
            member_repository=mock_member_repo,
        )
        command = UpdateCategoryCommand(
            category_id=category.id.value,
            updater_id=admin_member.user_id.value,
            community_id=community_id.value,
            name="Conflicting Name",
        )
        with pytest.raises(CategoryNameExistsError):
            await handler.handle(command)


class TestDeleteCategoryHandler:
    @pytest.mark.asyncio
    async def test_delete_category_success(
        self,
        community_id: CommunityId,
        admin_member: CommunityMember,
        category: Category,
    ) -> None:
        mock_category_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_member_repo.get_by_user_and_community.return_value = admin_member
        mock_category_repo.get_by_id.return_value = category
        mock_post_repo.count_by_category.return_value = 0

        handler = DeleteCategoryHandler(
            category_repository=mock_category_repo,
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )
        command = DeleteCategoryCommand(
            category_id=category.id.value,
            deleter_id=admin_member.user_id.value,
            community_id=community_id.value,
        )
        await handler.handle(command)
        mock_category_repo.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_category_has_posts(
        self,
        community_id: CommunityId,
        admin_member: CommunityMember,
        category: Category,
    ) -> None:
        mock_category_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_member_repo.get_by_user_and_community.return_value = admin_member
        mock_category_repo.get_by_id.return_value = category
        mock_post_repo.count_by_category.return_value = 5

        handler = DeleteCategoryHandler(
            category_repository=mock_category_repo,
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )
        command = DeleteCategoryCommand(
            category_id=category.id.value,
            deleter_id=admin_member.user_id.value,
            community_id=community_id.value,
        )
        with pytest.raises(CategoryHasPostsError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_delete_category_not_admin(
        self,
        community_id: CommunityId,
        regular_member: CommunityMember,
    ) -> None:
        mock_category_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_member_repo.get_by_user_and_community.return_value = regular_member

        handler = DeleteCategoryHandler(
            category_repository=mock_category_repo,
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )
        command = DeleteCategoryCommand(
            category_id=uuid4(),
            deleter_id=regular_member.user_id.value,
            community_id=community_id.value,
        )
        with pytest.raises(CannotManageCategoriesError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_delete_category_not_found(
        self,
        community_id: CommunityId,
        admin_member: CommunityMember,
    ) -> None:
        mock_category_repo = AsyncMock()
        mock_post_repo = AsyncMock()
        mock_member_repo = AsyncMock()
        mock_member_repo.get_by_user_and_community.return_value = admin_member
        mock_category_repo.get_by_id.return_value = None

        handler = DeleteCategoryHandler(
            category_repository=mock_category_repo,
            post_repository=mock_post_repo,
            member_repository=mock_member_repo,
        )
        command = DeleteCategoryCommand(
            category_id=uuid4(),
            deleter_id=admin_member.user_id.value,
            community_id=community_id.value,
        )
        with pytest.raises(CategoryNotFoundError):
            await handler.handle(command)
