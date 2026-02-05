"""HashedPassword value object."""

from dataclasses import dataclass


@dataclass(frozen=True)
class HashedPassword:
    """
    Hashed password value object.

    This value object stores only hashed passwords (never plaintext).
    The actual hashing is done by the PasswordHasher service.

    The hash format is determined by the hashing algorithm (Argon2id).
    """

    value: str

    def __post_init__(self) -> None:
        """Validate the hashed password is not empty."""
        if not self.value:
            raise ValueError("Hashed password cannot be empty")

    def __str__(self) -> str:
        """Return masked representation for safety."""
        return "[HASHED]"

    def __repr__(self) -> str:
        """Return masked representation for safety."""
        return "HashedPassword([HASHED])"
