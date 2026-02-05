"""SQLAlchemy implementation of user repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.identity.domain.entities import Profile, User
from src.identity.domain.repositories import IUserRepository
from src.identity.domain.value_objects import (
    DisplayName,
    EmailAddress,
    HashedPassword,
    UserId,
)
from src.identity.infrastructure.persistence.models import ProfileModel, UserModel


class SqlAlchemyUserRepository(IUserRepository):
    """SQLAlchemy implementation of IUserRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with database session."""
        self._session = session

    async def save(self, user: User) -> None:
        """Save a user (create or update)."""
        # Check if user exists
        existing = await self._session.get(
            UserModel,
            user.id.value,
            options=[selectinload(UserModel.profile)],
        )

        if existing is None:
            # Create new user
            user_model = UserModel(
                id=user.id.value,
                email=user.email.value,
                hashed_password=user.hashed_password.value,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            self._session.add(user_model)

            # Create profile if present
            if user.profile is not None:
                profile_model = ProfileModel(
                    user_id=user.id.value,
                    display_name=(
                        user.profile.display_name.value if user.profile.display_name else None
                    ),
                    avatar_url=user.profile.avatar_url,
                    bio=user.profile.bio,
                    is_complete=user.profile.is_complete,
                    created_at=user.profile.created_at,
                    updated_at=user.profile.updated_at,
                )
                self._session.add(profile_model)
        else:
            # Update existing user
            existing.email = user.email.value
            existing.hashed_password = user.hashed_password.value
            existing.is_active = user.is_active
            existing.is_verified = user.is_verified
            existing.updated_at = user.updated_at

            # Update profile
            if user.profile is not None:
                if existing.profile is None:
                    profile_model = ProfileModel(
                        user_id=user.id.value,
                        display_name=(
                            user.profile.display_name.value if user.profile.display_name else None
                        ),
                        avatar_url=user.profile.avatar_url,
                        bio=user.profile.bio,
                        is_complete=user.profile.is_complete,
                    )
                    self._session.add(profile_model)
                else:
                    existing.profile.display_name = (
                        user.profile.display_name.value if user.profile.display_name else None
                    )
                    existing.profile.avatar_url = user.profile.avatar_url
                    existing.profile.bio = user.profile.bio
                    existing.profile.is_complete = user.profile.is_complete
                    existing.profile.updated_at = user.profile.updated_at

        await self._session.flush()

    async def get_by_id(self, user_id: UserId) -> User | None:
        """Get a user by ID."""
        result = await self._session.execute(
            select(UserModel)
            .options(selectinload(UserModel.profile))
            .where(UserModel.id == user_id.value)
        )
        user_model = result.scalar_one_or_none()

        if user_model is None:
            return None

        return self._to_entity(user_model)

    async def get_by_email(self, email: EmailAddress) -> User | None:
        """Get a user by email address."""
        result = await self._session.execute(
            select(UserModel)
            .options(selectinload(UserModel.profile))
            .where(UserModel.email == email.value)
        )
        user_model = result.scalar_one_or_none()

        if user_model is None:
            return None

        return self._to_entity(user_model)

    async def exists_by_email(self, email: EmailAddress) -> bool:
        """Check if a user exists with the given email."""
        result = await self._session.execute(
            select(UserModel.id).where(UserModel.email == email.value)
        )
        return result.scalar_one_or_none() is not None

    async def delete(self, user_id: UserId) -> None:
        """Delete a user by ID."""
        user_model = await self._session.get(UserModel, user_id.value)
        if user_model is not None:
            await self._session.delete(user_model)
            await self._session.flush()

    def _to_entity(self, model: UserModel) -> User:
        """Convert SQLAlchemy model to domain entity."""
        profile = None
        if model.profile is not None:
            display_name = None
            if model.profile.display_name is not None:
                display_name = DisplayName(model.profile.display_name)

            profile = Profile(
                user_id=UserId(value=model.id),
                display_name=display_name,
                avatar_url=model.profile.avatar_url,
                bio=model.profile.bio,
                is_complete=model.profile.is_complete,
                created_at=model.profile.created_at,
                updated_at=model.profile.updated_at,
            )

        return User(
            id=UserId(value=model.id),
            email=EmailAddress(model.email),
            hashed_password=HashedPassword(model.hashed_password),
            is_verified=model.is_verified,
            is_active=model.is_active,
            profile=profile,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
