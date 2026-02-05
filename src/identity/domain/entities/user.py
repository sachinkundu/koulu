"""User aggregate root entity."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from src.identity.domain.entities.profile import Profile
from src.identity.domain.events import (
    PasswordReset,
    PasswordResetRequested,
    ProfileCompleted,
    UserLoggedIn,
    UserRegistered,
    UserVerified,
)
from src.identity.domain.exceptions import (
    PasswordTooLongError,
    PasswordTooShortError,
    UserAlreadyVerifiedError,
    UserDisabledError,
    UserNotVerifiedError,
)
from src.identity.domain.value_objects import (
    DisplayName,
    EmailAddress,
    HashedPassword,
    UserId,
)
from src.shared.domain import DomainEvent

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128


@dataclass
class User:
    """
    User aggregate root.

    This is the main entity for user identity. It enforces all
    business rules related to user registration, authentication,
    and password management.
    """

    id: UserId
    email: EmailAddress
    hashed_password: HashedPassword
    is_verified: bool = False
    is_active: bool = True
    profile: Profile | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _events: list[DomainEvent] = field(default_factory=list, repr=False, compare=False)

    @classmethod
    def register(
        cls,
        email: EmailAddress,
        hashed_password: HashedPassword,
    ) -> "User":
        """
        Factory method to register a new user.

        Creates a new unverified user and publishes UserRegistered event.

        Args:
            email: The user's email address (already validated)
            hashed_password: The user's password (already hashed)

        Returns:
            A new User instance
        """
        user_id = UserId(value=uuid4())
        user = cls(
            id=user_id,
            email=email,
            hashed_password=hashed_password,
            is_verified=False,
            is_active=True,
            profile=Profile(user_id=user_id),
        )
        user._add_event(
            UserRegistered(
                user_id=user_id,
                email=email,
            )
        )
        return user

    @staticmethod
    def validate_password_strength(password: str) -> None:
        """
        Validate password meets requirements.

        Args:
            password: The plaintext password to validate

        Raises:
            PasswordTooShortError: If password is less than 8 characters
            PasswordTooLongError: If password is more than 128 characters
        """
        if len(password) < MIN_PASSWORD_LENGTH:
            raise PasswordTooShortError(MIN_PASSWORD_LENGTH)
        if len(password) > MAX_PASSWORD_LENGTH:
            raise PasswordTooLongError(MAX_PASSWORD_LENGTH)

    def verify_email(self) -> None:
        """
        Mark the user's email as verified.

        Raises:
            UserAlreadyVerifiedError: If already verified
        """
        if self.is_verified:
            raise UserAlreadyVerifiedError()

        self.is_verified = True
        self._update_timestamp()
        self._add_event(UserVerified(user_id=self.id))

    def record_login(self) -> None:
        """
        Record a successful login.

        Raises:
            UserNotVerifiedError: If email not verified
            UserDisabledError: If account is disabled
        """
        if not self.is_verified:
            raise UserNotVerifiedError()
        if not self.is_active:
            raise UserDisabledError()

        self._update_timestamp()
        self._add_event(UserLoggedIn(user_id=self.id))

    def request_password_reset(self) -> None:
        """
        Request a password reset.

        Publishes PasswordResetRequested event for email sending.
        Only works for verified, active users.
        """
        if not self.is_verified or not self.is_active:
            # Silently ignore - security measure to prevent enumeration
            return

        self._add_event(PasswordResetRequested(user_id=self.id, email=self.email))

    def reset_password(self, new_hashed_password: HashedPassword) -> None:
        """
        Reset the user's password.

        Args:
            new_hashed_password: The new password (already hashed)
        """
        self.hashed_password = new_hashed_password
        self._update_timestamp()
        self._add_event(PasswordReset(user_id=self.id, email=self.email))

    def complete_profile(
        self,
        display_name: DisplayName,
        avatar_url: str | None = None,
    ) -> None:
        """
        Complete the user's profile.

        Args:
            display_name: The user's chosen display name
            avatar_url: Optional URL to the user's avatar
        """
        if self.profile is None:
            self.profile = Profile(user_id=self.id)

        self.profile.complete(display_name, avatar_url)
        self._update_timestamp()
        self._add_event(
            ProfileCompleted(
                user_id=self.id,
                display_name=display_name,
            )
        )

    def disable(self) -> None:
        """Disable the user account."""
        self.is_active = False
        self._update_timestamp()

    def enable(self) -> None:
        """Enable the user account."""
        self.is_active = True
        self._update_timestamp()

    def _add_event(self, event: DomainEvent) -> None:
        """Add a domain event to be published after persistence."""
        self._events.append(event)

    def clear_events(self) -> list[DomainEvent]:
        """Clear and return all pending domain events."""
        events = self._events.copy()
        self._events.clear()
        return events

    @property
    def events(self) -> list[DomainEvent]:
        """Get pending domain events (read-only view)."""
        return self._events.copy()

    @property
    def has_complete_profile(self) -> bool:
        """Check if the user has completed their profile."""
        return self.profile is not None and self.profile.is_complete

    def _update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(UTC)

    def __eq__(self, other: object) -> bool:
        """Users are equal if they have the same ID."""
        if not isinstance(other, User):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on user ID."""
        return hash(self.id)
