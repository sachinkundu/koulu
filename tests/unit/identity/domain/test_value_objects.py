"""Unit tests for Identity domain value objects."""

import pytest

from src.identity.domain.exceptions import (
    InvalidBioError,
    InvalidDisplayNameError,
    InvalidEmailError,
    InvalidLocationError,
    InvalidSocialLinkError,
)
from src.identity.domain.value_objects import (
    Bio,
    DisplayName,
    EmailAddress,
    HashedPassword,
    Location,
    SocialLinks,
)


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


class TestBio:
    """Tests for Bio value object."""

    def test_valid_bio_creates_instance(self) -> None:
        """Valid bio should create a Bio instance."""
        bio = Bio("Software developer passionate about clean code")
        assert bio.value == "Software developer passionate about clean code"

    def test_bio_sanitizes_html_tags(self) -> None:
        """Bio should strip HTML tags for XSS prevention."""
        bio = Bio("<script>alert('xss')</script>Hello")
        assert bio.value == "Hello"
        assert "<script>" not in bio.value

    def test_bio_sanitizes_nested_html(self) -> None:
        """Bio should strip nested HTML tags."""
        bio = Bio("I love <b>coding</b> and <i>design</i>")
        assert bio.value == "I love coding and design"

    def test_bio_too_long_raises_error(self) -> None:
        """Bio over 500 chars should raise InvalidBioError."""
        long_bio = "a" * 501
        with pytest.raises(InvalidBioError) as exc_info:
            Bio(long_bio)
        assert "500" in str(exc_info.value)

    def test_bio_at_max_length_is_valid(self) -> None:
        """Bio at exactly 500 chars should be valid."""
        bio = Bio("a" * 500)
        assert len(bio.value) == 500

    def test_str_returns_value(self) -> None:
        """str() should return the bio value."""
        bio = Bio("Hello world")
        assert str(bio) == "Hello world"

    def test_bio_with_special_characters_is_valid(self) -> None:
        """Bio with special characters should be valid."""
        bio = Bio("Developer @ Company! 🚀 #coding")
        assert "Developer @ Company!" in bio.value


class TestLocation:
    """Tests for Location value object."""

    def test_valid_location_creates_instance(self) -> None:
        """Valid location should create a Location instance."""
        location = Location(city="San Francisco", country="USA")
        assert location.city == "San Francisco"
        assert location.country == "USA"

    def test_location_fields_are_trimmed(self) -> None:
        """Location fields should have whitespace trimmed."""
        location = Location(city="  Paris  ", country="  France  ")
        assert location.city == "Paris"
        assert location.country == "France"

    def test_city_too_short_raises_error(self) -> None:
        """City under 2 chars should raise InvalidLocationError."""
        with pytest.raises(InvalidLocationError) as exc_info:
            Location(city="X", country="USA")
        assert "City" in str(exc_info.value)
        assert "2" in str(exc_info.value)

    def test_city_too_long_raises_error(self) -> None:
        """City over 100 chars should raise InvalidLocationError."""
        long_city = "a" * 101
        with pytest.raises(InvalidLocationError) as exc_info:
            Location(city=long_city, country="USA")
        assert "City" in str(exc_info.value)
        assert "100" in str(exc_info.value)

    def test_country_too_short_raises_error(self) -> None:
        """Country under 2 chars should raise InvalidLocationError."""
        with pytest.raises(InvalidLocationError) as exc_info:
            Location(city="Paris", country="F")
        assert "Country" in str(exc_info.value)
        assert "2" in str(exc_info.value)

    def test_country_too_long_raises_error(self) -> None:
        """Country over 100 chars should raise InvalidLocationError."""
        long_country = "a" * 101
        with pytest.raises(InvalidLocationError) as exc_info:
            Location(city="Paris", country=long_country)
        assert "Country" in str(exc_info.value)
        assert "100" in str(exc_info.value)

    def test_city_with_html_tags_raises_error(self) -> None:
        """City with HTML tags should raise InvalidLocationError."""
        with pytest.raises(InvalidLocationError) as exc_info:
            Location(city="<script>Paris</script>", country="France")
        assert "HTML" in str(exc_info.value)

    def test_country_with_html_tags_raises_error(self) -> None:
        """Country with HTML tags should raise InvalidLocationError."""
        with pytest.raises(InvalidLocationError) as exc_info:
            Location(city="Paris", country="<b>France</b>")
        assert "HTML" in str(exc_info.value)

    def test_format_returns_city_comma_country(self) -> None:
        """format() should return 'city, country'."""
        location = Location(city="Tokyo", country="Japan")
        assert location.format() == "Tokyo, Japan"

    def test_location_at_minimum_length_is_valid(self) -> None:
        """Location with minimum length fields should be valid."""
        location = Location(city="LA", country="US")
        assert location.city == "LA"
        assert location.country == "US"

    def test_location_at_maximum_length_is_valid(self) -> None:
        """Location with maximum length fields should be valid."""
        location = Location(city="a" * 100, country="b" * 100)
        assert len(location.city) == 100
        assert len(location.country) == 100


class TestSocialLinks:
    """Tests for SocialLinks value object."""

    def test_valid_social_links_create_instance(self) -> None:
        """Valid social links should create a SocialLinks instance."""
        links = SocialLinks(
            twitter_url="https://twitter.com/user",
            linkedin_url="https://linkedin.com/in/user",
        )
        assert links.twitter_url == "https://twitter.com/user"
        assert links.linkedin_url == "https://linkedin.com/in/user"

    def test_all_fields_optional(self) -> None:
        """All social link fields should be optional."""
        links = SocialLinks()
        assert links.twitter_url is None
        assert links.linkedin_url is None
        assert links.instagram_url is None
        assert links.website_url is None

    def test_invalid_url_raises_error(self) -> None:
        """Invalid URL should raise InvalidSocialLinkError."""
        with pytest.raises(InvalidSocialLinkError):
            SocialLinks(twitter_url="not-a-url")

    def test_javascript_scheme_blocked(self) -> None:
        """javascript: URL scheme should be blocked."""
        with pytest.raises(InvalidSocialLinkError):
            SocialLinks(twitter_url="javascript:alert('xss')")

    def test_data_scheme_blocked(self) -> None:
        """data: URL scheme should be blocked."""
        with pytest.raises(InvalidSocialLinkError):
            SocialLinks(website_url="data:text/html,<script>alert('xss')</script>")

    def test_has_any_returns_true_when_any_link_set(self) -> None:
        """has_any() should return True when any link is set."""
        links = SocialLinks(twitter_url="https://twitter.com/user")
        assert links.has_any() is True

    def test_has_any_returns_false_when_all_none(self) -> None:
        """has_any() should return False when all links are None."""
        links = SocialLinks()
        assert links.has_any() is False

    def test_multiple_links_can_be_set(self) -> None:
        """Multiple links can be set at once."""
        links = SocialLinks(
            twitter_url="https://twitter.com/user",
            linkedin_url="https://linkedin.com/in/user",
            instagram_url="https://instagram.com/user",
            website_url="https://example.com",
        )
        assert links.twitter_url == "https://twitter.com/user"
        assert links.linkedin_url == "https://linkedin.com/in/user"
        assert links.instagram_url == "https://instagram.com/user"
        assert links.website_url == "https://example.com"

    def test_partial_links_are_valid(self) -> None:
        """Setting only some links should be valid."""
        links = SocialLinks(
            linkedin_url="https://linkedin.com/in/user",
            website_url="https://example.com",
        )
        assert links.twitter_url is None
        assert links.linkedin_url == "https://linkedin.com/in/user"
        assert links.instagram_url is None
        assert links.website_url == "https://example.com"
