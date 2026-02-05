"""Register user command."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterUserCommand:
    """Command to register a new user."""

    email: str
    password: str
