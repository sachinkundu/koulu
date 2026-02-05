"""Avatar generator interface."""

from abc import ABC, abstractmethod


class IAvatarGenerator(ABC):
    """
    Interface for generating default avatars.

    Implementations should generate avatars based on user initials
    or other identifying information.
    """

    @abstractmethod
    def generate_from_initials(self, initials: str) -> str:
        """
        Generate an avatar URL from initials.

        Args:
            initials: 1-2 character initials (e.g., "JD" for John Doe)

        Returns:
            URL to the generated avatar image
        """
        ...
