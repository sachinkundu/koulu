"""User repository interface."""

from abc import ABC, abstractmethod

from src.identity.domain.entities import User
from src.identity.domain.value_objects import EmailAddress, UserId


class IUserRepository(ABC):
    """
    Interface for User persistence operations.

    Implementations handle database operations for User aggregate.
    """

    @abstractmethod
    async def save(self, user: User) -> None:
        """
        Save a user (create or update).

        Args:
            user: The user entity to save
        """
        ...

    @abstractmethod
    async def get_by_id(self, user_id: UserId) -> User | None:
        """
        Get a user by ID.

        Args:
            user_id: The user's ID

        Returns:
            User if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_by_email(self, email: EmailAddress) -> User | None:
        """
        Get a user by email address.

        Args:
            email: The user's email address

        Returns:
            User if found, None otherwise
        """
        ...

    @abstractmethod
    async def exists_by_email(self, email: EmailAddress) -> bool:
        """
        Check if a user exists with the given email.

        Args:
            email: The email address to check

        Returns:
            True if user exists, False otherwise
        """
        ...

    @abstractmethod
    async def delete(self, user_id: UserId) -> None:
        """
        Delete a user by ID.

        Args:
            user_id: The ID of the user to delete
        """
        ...
