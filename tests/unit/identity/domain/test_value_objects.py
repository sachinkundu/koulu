"""Unit tests for Identity domain value objects."""

import pytest

from src.identity.domain.exceptions import InvalidDisplayNameError, InvalidEmailError
from src.identity.domain.value_objects import DisplayName, EmailAddress, HashedPassword


class TestEmailAddress:
    """Tests for EmailAddress value object."""

    def test_valid_email_creates_instance(self) -> None:
        """Valid email should create an EmailAddress instance."""
        email = EmailAddress("user@example.com")
        assert email.value == "user@example.com"

    def test_email_is_normalized_to_lowercase(self) -> None:
        """Email should be normalized to lowercase."""
        email = EmailAddress("User@EXAMPLE.COM")
        assert email.value == "user@example.com"

    def test_email_is_trimmed(self) -> None:
        """Email should have whitespace trimmed."""
        email = EmailAddress("  user@example.com  ")
        assert email.value == "user@example.com"

    def test_empty_email_raises_error(self) -> None:
        """Empty email should raise InvalidEmailError."""
        with pytest.raises(InvalidEmailError):
            EmailAddress("")

    def test_whitespace_only_email_raises_error(self) -> None:
        """Whitespace-only email should raise InvalidEmailError."""
        with pytest.raises(InvalidEmailError):
            EmailAddress("   ")

    def test_email_without_at_symbol_raises_error(self) -> None:
        """Email without @ should raise InvalidEmailError."""
        with pytest.raises(InvalidEmailError):
            EmailAddress("userexample.com")

    def test_email_without_domain_raises_error(self) -> None:
        """Email without domain should raise InvalidEmailError."""
        with pytest.raises(InvalidEmailError):
            EmailAddress("user@")

    def test_email_without_local_part_raises_error(self) -> None:
        """Email without local part should raise InvalidEmailError."""
        with pytest.raises(InvalidEmailError):
            EmailAddress("@example.com")

    def test_email_exceeding_max_length_raises_error(self) -> None:
        """Email over 254 characters should raise InvalidEmailError."""
        long_local = "a" * 245
        long_email = f"{long_local}@example.com"  # > 254 chars
        with pytest.raises(InvalidEmailError):
            EmailAddress(long_email)

    def test_email_at_max_length_is_valid(self) -> None:
        """Email at exactly 254 characters should be valid."""
        # Create email at exactly 254 chars: local@domain.com
        local = "a" * 242
        email = EmailAddress(f"{local}@example.com")  # 242 + 12 = 254
        assert len(email.value) == 254

    def test_local_part_property(self) -> None:
        """local_part should return the part before @."""
        email = EmailAddress("user@example.com")
        assert email.local_part == "user"

    def test_domain_property(self) -> None:
        """domain should return the part after @."""
        email = EmailAddress("user@example.com")
        assert email.domain == "example.com"

    def test_str_returns_value(self) -> None:
        """str() should return the email value."""
        email = EmailAddress("user@example.com")
        assert str(email) == "user@example.com"

    def test_email_with_plus_sign_is_valid(self) -> None:
        """Email with + in local part should be valid."""
        email = EmailAddress("user+tag@example.com")
        assert email.value == "user+tag@example.com"

    def test_email_with_dots_in_local_part_is_valid(self) -> None:
        """Email with dots in local part should be valid."""
        email = EmailAddress("first.last@example.com")
        assert email.value == "first.last@example.com"

    def test_email_with_subdomain_is_valid(self) -> None:
        """Email with subdomain should be valid."""
        email = EmailAddress("user@mail.example.com")
        assert email.value == "user@mail.example.com"


class TestDisplayName:
    """Tests for DisplayName value object."""

    def test_valid_display_name_creates_instance(self) -> None:
        """Valid display name should create a DisplayName instance."""
        name = DisplayName("John Doe")
        assert name.value == "John Doe"

    def test_display_name_is_trimmed(self) -> None:
        """Display name should have whitespace trimmed."""
        name = DisplayName("  John Doe  ")
        assert name.value == "John Doe"

    def test_display_name_too_short_raises_error(self) -> None:
        """Display name under 2 chars should raise InvalidDisplayNameError."""
        with pytest.raises(InvalidDisplayNameError) as exc_info:
            DisplayName("J")
        assert "at least 2" in str(exc_info.value)

    def test_display_name_too_long_raises_error(self) -> None:
        """Display name over 50 chars should raise InvalidDisplayNameError."""
        long_name = "a" * 51
        with pytest.raises(InvalidDisplayNameError) as exc_info:
            DisplayName(long_name)
        assert "at most 50" in str(exc_info.value)

    def test_display_name_at_minimum_length_is_valid(self) -> None:
        """Display name at exactly 2 chars should be valid."""
        name = DisplayName("Jo")
        assert name.value == "Jo"

    def test_display_name_at_maximum_length_is_valid(self) -> None:
        """Display name at exactly 50 chars should be valid."""
        name = DisplayName("a" * 50)
        assert len(name.value) == 50

    def test_display_name_with_html_tags_raises_error(self) -> None:
        """Display name with HTML tags should raise InvalidDisplayNameError."""
        with pytest.raises(InvalidDisplayNameError) as exc_info:
            DisplayName("<script>alert('xss')</script>")
        assert "HTML tags" in str(exc_info.value)

    def test_display_name_with_html_tag_in_middle_raises_error(self) -> None:
        """Display name with HTML tag in middle should raise error."""
        with pytest.raises(InvalidDisplayNameError):
            DisplayName("John<b>Doe</b>")

    def test_str_returns_value(self) -> None:
        """str() should return the display name value."""
        name = DisplayName("John Doe")
        assert str(name) == "John Doe"

    def test_initials_for_two_word_name(self) -> None:
        """Initials for two-word name should be first letters of each word."""
        name = DisplayName("John Doe")
        assert name.initials == "JD"

    def test_initials_for_single_word_name(self) -> None:
        """Initials for single-word name should be first letter."""
        name = DisplayName("Alice")
        assert name.initials == "A"

    def test_initials_for_multi_word_name(self) -> None:
        """Initials for multi-word name should be first two words only."""
        name = DisplayName("John Jacob Jingleheimer")
        assert name.initials == "JJ"

    def test_initials_are_uppercase(self) -> None:
        """Initials should be uppercase."""
        name = DisplayName("john doe")
        assert name.initials == "JD"


class TestHashedPassword:
    """Tests for HashedPassword value object."""

    def test_valid_hashed_password_creates_instance(self) -> None:
        """Valid hash should create a HashedPassword instance."""
        hashed = HashedPassword("$argon2id$v=19$m=65536,t=3,p=4$somehash")
        assert hashed.value == "$argon2id$v=19$m=65536,t=3,p=4$somehash"

    def test_empty_hash_raises_error(self) -> None:
        """Empty hash should raise ValueError."""
        with pytest.raises(ValueError):
            HashedPassword("")

    def test_str_returns_masked_value(self) -> None:
        """str() should return masked value for security (not actual hash)."""
        hashed = HashedPassword("$argon2id$v=19$m=65536,t=3,p=4$somehash")
        # Hash should not be revealed in string representation
        assert str(hashed) == "[HASHED]"
        assert "argon2" not in str(hashed)
