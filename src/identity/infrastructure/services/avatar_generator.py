"""Avatar generator implementation."""

from src.identity.domain.services import IAvatarGenerator


class InitialsAvatarGenerator(IAvatarGenerator):
    """
    Generate avatar URLs based on initials.

    Uses UI Avatars service for generating SVG avatars.
    In production, could be replaced with a self-hosted solution.
    """

    def __init__(
        self,
        base_url: str = "https://ui-avatars.com/api/",
        size: int = 128,
        background: str = "0ea5e9",  # Primary-500 color
        color: str = "ffffff",
    ) -> None:
        """
        Initialize avatar generator.

        Args:
            base_url: Base URL for avatar service
            size: Avatar size in pixels
            background: Background color (hex without #)
            color: Text color (hex without #)
        """
        self._base_url = base_url
        self._size = size
        self._background = background
        self._color = color

    def generate_from_initials(self, initials: str) -> str:
        """Generate an avatar URL from initials."""
        # Ensure initials are uppercase and max 2 characters
        clean_initials = initials.upper()[:2]

        return (
            f"{self._base_url}"
            f"?name={clean_initials}"
            f"&size={self._size}"
            f"&background={self._background}"
            f"&color={self._color}"
            f"&bold=true"
            f"&format=svg"
        )
