"""Password hasher interface."""

from abc import ABC, abstractmethod

from src.identity.domain.value_objects import HashedPassword


class IPasswordHasher(ABC):
    """
    Interface for password hashing operations.

    Implementations should use Argon2id (memory-hard, GPU-resistant).
    """

    @abstractmethod
    def hash(self, password: str) -> HashedPassword:
        """
        Hash a plaintext password.

        Args:
            password: The plaintext password to hash

        Returns:
            The hashed password value object
        """
        ...

    @abstractmethod
    def verify(self, password: str, hashed: HashedPassword) -> bool:
        """
        Verify a password against a hash.

        Uses constant-time comparison to prevent timing attacks.

        Args:
            password: The plaintext password to verify
            hashed: The hashed password to compare against

        Returns:
            True if the password matches, False otherwise
        """
        ...
