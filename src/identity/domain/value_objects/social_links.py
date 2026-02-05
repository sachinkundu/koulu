"""SocialLinks value object."""

from dataclasses import dataclass

from pydantic import HttpUrl, ValidationError

from src.identity.domain.exceptions import InvalidSocialLinkError


@dataclass(frozen=True)
class SocialLinks:
    """
    User social links value object.

    Collection of external profile URLs.
    All fields are optional, but when provided must be valid URLs.

    Validates:
    - URL format (http:// or https:// only)
    - No javascript:, data:, or other dangerous schemes
    """

    twitter_url: str | None = None
    linkedin_url: str | None = None
    instagram_url: str | None = None
    website_url: str | None = None

    def __post_init__(self) -> None:
        """Validate URL formats using Pydantic."""
        field_mapping = {
            "twitter_url": self.twitter_url,
            "linkedin_url": self.linkedin_url,
            "instagram_url": self.instagram_url,
            "website_url": self.website_url,
        }

        for field_name, value in field_mapping.items():
            if value is not None:
                try:
                    # Validate URL format
                    HttpUrl(value)
                except ValidationError as e:
                    raise InvalidSocialLinkError(
                        f"Invalid URL format for {field_name}: {value}"
                    ) from e

    def has_any(self) -> bool:
        """Check if any social link is set."""
        return any(
            [
                self.twitter_url,
                self.linkedin_url,
                self.instagram_url,
                self.website_url,
            ]
        )

    def __str__(self) -> str:
        """Return string representation of social links."""
        links = []
        if self.twitter_url:
            links.append(f"Twitter: {self.twitter_url}")
        if self.linkedin_url:
            links.append(f"LinkedIn: {self.linkedin_url}")
        if self.instagram_url:
            links.append(f"Instagram: {self.instagram_url}")
        if self.website_url:
            links.append(f"Website: {self.website_url}")
        return ", ".join(links) if links else "No social links"
