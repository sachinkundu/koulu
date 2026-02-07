"""SQLAlchemy implementation of category repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.community.domain.entities import Category
from src.community.domain.repositories import ICategoryRepository
from src.community.domain.value_objects import CategoryId, CommunityId
from src.community.infrastructure.persistence.models import CategoryModel


class SqlAlchemyCategoryRepository(ICategoryRepository):
    """SQLAlchemy implementation of ICategoryRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with database session."""
        self._session = session

    async def save(self, category: Category) -> None:
        """Save a category (create or update)."""
        # Check if category exists
        existing = await self._session.get(CategoryModel, category.id.value)

        if existing is None:
            # Create new category
            category_model = CategoryModel(
                id=category.id.value,
                community_id=category.community_id.value,
                name=category.name,
                slug=category.slug,
                emoji=category.emoji,
                description=category.description,
                created_at=category.created_at,
                updated_at=category.updated_at,
            )
            self._session.add(category_model)
        else:
            # Update existing category
            existing.community_id = category.community_id.value
            existing.name = category.name
            existing.slug = category.slug
            existing.emoji = category.emoji
            existing.description = category.description
            existing.updated_at = category.updated_at

        await self._session.flush()

    async def get_by_id(self, category_id: CategoryId) -> Category | None:
        """Get a category by ID."""
        result = await self._session.execute(
            select(CategoryModel).where(CategoryModel.id == category_id.value)
        )
        category_model = result.scalar_one_or_none()

        if category_model is None:
            return None

        return self._to_entity(category_model)

    async def get_by_name(self, community_id: CommunityId, name: str) -> Category | None:
        """Get a category by name within a community."""
        result = await self._session.execute(
            select(CategoryModel).where(
                CategoryModel.community_id == community_id.value, CategoryModel.name == name
            )
        )
        category_model = result.scalar_one_or_none()

        if category_model is None:
            return None

        return self._to_entity(category_model)

    async def get_by_slug(self, community_id: CommunityId, slug: str) -> Category | None:
        """Get a category by slug within a community."""
        result = await self._session.execute(
            select(CategoryModel).where(
                CategoryModel.community_id == community_id.value, CategoryModel.slug == slug
            )
        )
        category_model = result.scalar_one_or_none()

        if category_model is None:
            return None

        return self._to_entity(category_model)

    async def list_by_community(self, community_id: CommunityId) -> list[Category]:
        """List all categories in a community."""
        result = await self._session.execute(
            select(CategoryModel)
            .where(CategoryModel.community_id == community_id.value)
            .order_by(CategoryModel.name)
        )
        category_models = result.scalars().all()

        return [self._to_entity(model) for model in category_models]

    async def exists_by_name(self, community_id: CommunityId, name: str) -> bool:
        """Check if a category with the given name exists."""
        result = await self._session.execute(
            select(CategoryModel.id).where(
                CategoryModel.community_id == community_id.value, CategoryModel.name == name
            )
        )
        return result.scalar_one_or_none() is not None

    async def delete(self, category_id: CategoryId) -> None:
        """Delete a category by ID."""
        category_model = await self._session.get(CategoryModel, category_id.value)
        if category_model is not None:
            await self._session.delete(category_model)
            await self._session.flush()

    def _to_entity(self, model: CategoryModel) -> Category:
        """Convert SQLAlchemy model to domain entity."""
        return Category(
            id=CategoryId(value=model.id),
            community_id=CommunityId(value=model.community_id),
            name=model.name,
            slug=model.slug,
            emoji=model.emoji,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
