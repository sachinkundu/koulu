"""Email service interface."""

from abc import ABC, abstractmethod


class IEmailService(ABC):
    """
    Interface for email sending service.

    This is a domain service interface - implementations live in infrastructure.
    """

    @abstractmethod
    async def send_verification_email(self, email: str, token: str) -> None:
        """
        Send verification email to user.

        Args:
            email: Recipient email address
            token: Verification token
        """
        ...

    @abstractmethod
    async def send_password_reset_email(self, email: str, token: str) -> None:
        """
        Send password reset email to user.

        Args:
            email: Recipient email address
            token: Reset token
        """
        ...

    @abstractmethod
    async def send_password_changed_email(self, email: str) -> None:
        """
        Send password changed confirmation email.

        Args:
            email: Recipient email address
        """
        ...
