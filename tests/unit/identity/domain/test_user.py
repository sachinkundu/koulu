"""Unit tests for User entity."""

import pytest

from src.identity.domain.entities.user import User
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
from src.identity.domain.value_objects import DisplayName, EmailAddress, HashedPassword


@pytest.fixture
def email() -> EmailAddress:
    """Create a test email address."""
    return EmailAddress("test@example.com")


@pytest.fixture
def hashed_password() -> HashedPassword:
    """Create a test hashed password."""
    return HashedPassword("$argon2id$v=19$m=65536,t=3,p=4$somehash")


@pytest.fixture
def user(email: EmailAddress, hashed_password: HashedPassword) -> User:
    """Create a test user."""
    return User.register(email, hashed_password)


class TestUserRegister:
    """Tests for User.register() factory method."""

    def test_register_creates_unverified_user(
        self, email: EmailAddress, hashed_password: HashedPassword
    ) -> None:
        """New users should be unverified by default."""
        user = User.register(email, hashed_password)

        assert user.email == email
        assert user.hashed_password == hashed_password
        assert user.is_verified is False
        assert user.is_active is True

    def test_register_creates_profile(
        self, email: EmailAddress, hashed_password: HashedPassword
    ) -> None:
        """New users should have an incomplete profile."""
        user = User.register(email, hashed_password)

        assert user.profile is not None
        assert user.profile.is_complete is False

    def test_register_publishes_user_registered_event(
        self, email: EmailAddress, hashed_password: HashedPassword
    ) -> None:
        """Registration should publish UserRegistered event."""
        user = User.register(email, hashed_password)

        events = user.events
        assert len(events) == 1
        assert isinstance(events[0], UserRegistered)
        assert events[0].user_id == user.id
        assert events[0].email == email


class TestValidatePasswordStrength:
    """Tests for User.validate_password_strength() static method."""

    def test_valid_password_passes(self) -> None:
        """Password with 8+ chars should pass."""
        User.validate_password_strength("validpass123")  # Should not raise

    def test_password_too_short_raises_error(self) -> None:
        """Password under 8 chars should raise PasswordTooShortError."""
        with pytest.raises(PasswordTooShortError) as exc_info:
            User.validate_password_strength("short")

        assert exc_info.value.min_length == 8

    def test_password_too_long_raises_error(self) -> None:
        """Password over 128 chars should raise PasswordTooLongError."""
        long_password = "a" * 129

        with pytest.raises(PasswordTooLongError) as exc_info:
            User.validate_password_strength(long_password)

        assert exc_info.value.max_length == 128

    def test_password_at_minimum_length_passes(self) -> None:
        """Password at exactly 8 chars should pass."""
        User.validate_password_strength("12345678")  # Should not raise

    def test_password_at_maximum_length_passes(self) -> None:
        """Password at exactly 128 chars should pass."""
        User.validate_password_strength("a" * 128)  # Should not raise


class TestVerifyEmail:
    """Tests for User.verify_email() method."""

    def test_verify_email_marks_user_as_verified(self, user: User) -> None:
        """Verifying email should set is_verified to True."""
        assert user.is_verified is False

        user.verify_email()

        assert user.is_verified is True

    def test_verify_email_publishes_event(self, user: User) -> None:
        """Verifying email should publish UserVerified event."""
        user.clear_events()  # Clear registration event

        user.verify_email()

        events = user.events
        assert len(events) == 1
        assert isinstance(events[0], UserVerified)
        assert events[0].user_id == user.id

    def test_verify_email_when_already_verified_raises_error(self, user: User) -> None:
        """Verifying an already verified user should raise UserAlreadyVerifiedError."""
        user.verify_email()  # First verification succeeds

        with pytest.raises(UserAlreadyVerifiedError):
            user.verify_email()  # Second verification fails


class TestRecordLogin:
    """Tests for User.record_login() method."""

    def test_record_login_for_verified_active_user_succeeds(self, user: User) -> None:
        """Verified active user should be able to login."""
        user.verify_email()
        user.clear_events()

        user.record_login()

        events = user.events
        assert len(events) == 1
        assert isinstance(events[0], UserLoggedIn)

    def test_record_login_for_unverified_user_raises_error(self, user: User) -> None:
        """Unverified user should not be able to login."""
        assert user.is_verified is False

        with pytest.raises(UserNotVerifiedError):
            user.record_login()

    def test_record_login_for_disabled_user_raises_error(self, user: User) -> None:
        """Disabled user should not be able to login."""
        user.verify_email()
        user.disable()

        with pytest.raises(UserDisabledError):
            user.record_login()


class TestRequestPasswordReset:
    """Tests for User.request_password_reset() method."""

    def test_request_password_reset_for_verified_active_user_publishes_event(
        self, user: User
    ) -> None:
        """Verified active user requesting reset should publish event."""
        user.verify_email()
        user.clear_events()

        user.request_password_reset()

        events = user.events
        assert len(events) == 1
        assert isinstance(events[0], PasswordResetRequested)
        assert events[0].user_id == user.id

    def test_request_password_reset_for_unverified_user_is_silent(self, user: User) -> None:
        """Unverified user requesting reset should be silently ignored (security)."""
        user.clear_events()

        user.request_password_reset()

        assert len(user.events) == 0  # No event published

    def test_request_password_reset_for_disabled_user_is_silent(self, user: User) -> None:
        """Disabled user requesting reset should be silently ignored (security)."""
        user.verify_email()
        user.disable()
        user.clear_events()

        user.request_password_reset()

        assert len(user.events) == 0  # No event published


class TestResetPassword:
    """Tests for User.reset_password() method."""

    def test_reset_password_updates_hashed_password(self, user: User) -> None:
        """Resetting password should update the hashed_password."""
        old_password = user.hashed_password
        new_password = HashedPassword("$argon2id$v=19$m=65536,t=3,p=4$newhash")

        user.reset_password(new_password)

        assert user.hashed_password == new_password
        assert user.hashed_password != old_password

    def test_reset_password_publishes_event(self, user: User) -> None:
        """Resetting password should publish PasswordReset event."""
        user.clear_events()
        new_password = HashedPassword("$argon2id$v=19$m=65536,t=3,p=4$newhash")

        user.reset_password(new_password)

        events = user.events
        assert len(events) == 1
        assert isinstance(events[0], PasswordReset)


class TestCompleteProfile:
    """Tests for User.complete_profile() method."""

    def test_complete_profile_sets_display_name_and_avatar(self, user: User) -> None:
        """Completing profile should set display name and avatar."""
        display_name = DisplayName("John Doe")
        avatar_url = "https://example.com/avatar.png"

        user.complete_profile(display_name, avatar_url)

        assert user.profile is not None
        assert user.profile.display_name == display_name
        assert user.profile.avatar_url == avatar_url
        assert user.profile.is_complete is True

    def test_complete_profile_publishes_event(self, user: User) -> None:
        """Completing profile should publish ProfileCompleted event."""
        user.clear_events()
        display_name = DisplayName("John Doe")

        user.complete_profile(display_name)

        events = user.events
        assert len(events) == 1
        assert isinstance(events[0], ProfileCompleted)
        assert events[0].display_name == display_name

    def test_has_complete_profile_returns_correct_value(self, user: User) -> None:
        """has_complete_profile should reflect profile completion state."""
        assert user.has_complete_profile is False

        user.complete_profile(DisplayName("John Doe"))

        assert user.has_complete_profile is True


class TestDisableEnable:
    """Tests for User.disable() and User.enable() methods."""

    def test_disable_sets_is_active_to_false(self, user: User) -> None:
        """Disabling user should set is_active to False."""
        assert user.is_active is True

        user.disable()

        assert user.is_active is False

    def test_enable_sets_is_active_to_true(self, user: User) -> None:
        """Enabling user should set is_active to True."""
        user.disable()
        assert user.is_active is False

        user.enable()

        assert user.is_active is True


class TestEventManagement:
    """Tests for event management methods."""

    def test_clear_events_returns_and_clears_events(self, user: User) -> None:
        """clear_events() should return events and empty the list."""
        assert len(user.events) == 1  # UserRegistered from creation

        cleared = user.clear_events()

        assert len(cleared) == 1
        assert isinstance(cleared[0], UserRegistered)
        assert len(user.events) == 0

    def test_events_property_returns_copy(self, user: User) -> None:
        """events property should return a copy, not the original list."""
        events = user.events

        events.clear()  # Modify the returned list

        assert len(user.events) == 1  # Original unchanged
