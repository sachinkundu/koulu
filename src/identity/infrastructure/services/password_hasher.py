"""Argon2id password hasher implementation."""

from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from src.identity.domain.services import IPasswordHasher
from src.identity.domain.value_objects import HashedPassword


class Argon2PasswordHasher(IPasswordHasher):
    """
    Password hasher using Argon2id algorithm.

    Argon2id is the recommended algorithm for password hashing:
    - Memory-hard (resistant to GPU attacks)
    - Time-hard (resistant to brute force)
    - OWASP recommended
    """

    def __init__(self) -> None:
        """Initialize the password hasher."""
        self._hasher = PasswordHash((Argon2Hasher(),))

    def hash(self, password: str) -> HashedPassword:
        """Hash a plaintext password using Argon2id."""
        hashed = self._hasher.hash(password)
        return HashedPassword(value=hashed)

    def verify(self, password: str, hashed: HashedPassword) -> bool:
        """
        Verify a password against a hash.

        Uses constant-time comparison to prevent timing attacks.
        """
        try:
            return self._hasher.verify(password, hashed.value)
        except Exception:
            # Any error means invalid password
            return False
