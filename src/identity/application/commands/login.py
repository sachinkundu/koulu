"""Login command."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LoginCommand:
    """Command to log in a user."""

    email: str
    password: str
    remember_me: bool = False
