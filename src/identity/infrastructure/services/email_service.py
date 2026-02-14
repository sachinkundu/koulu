"""Email service implementation using Resend HTTP API."""

import resend
import structlog

from src.config import settings
from src.identity.domain.services import IEmailService

logger = structlog.get_logger()


class EmailService(IEmailService):
    """
    Email service for sending transactional emails.

    Uses Resend HTTP API instead of SMTP to avoid port-blocking on cloud platforms.
    """

    def __init__(self) -> None:
        """Initialize email service with Resend API key."""
        resend.api_key = settings.resend_api_key
        self._from_email = f"{settings.mail_from_name} <{settings.mail_from}>"
        self._frontend_url = settings.frontend_url

    async def send_verification_email(
        self,
        email: str,
        token: str,
    ) -> None:
        """Send email verification email."""
        verification_url = f"{self._frontend_url}/verify?token={token}"

        try:
            resend.Emails.send(
                {
                    "from": self._from_email,
                    "to": [email],
                    "subject": "Verify your Koulu account",
                    "html": f"""
                <h1>Welcome to Koulu!</h1>
                <p>Please verify your email address by clicking the link below:</p>
                <p><a href="{verification_url}">Verify Email</a></p>
                <p>This link will expire in 24 hours.</p>
                <p>If you didn't create an account, you can ignore this email.</p>
                """,
                }
            )
            logger.info("verification_email_sent", email=email)
        except Exception as e:
            logger.error("verification_email_failed", email=email, error=str(e))
            raise

    async def send_password_reset_email(
        self,
        email: str,
        token: str,
    ) -> None:
        """Send password reset email."""
        reset_url = f"{self._frontend_url}/reset-password?token={token}"

        try:
            resend.Emails.send(
                {
                    "from": self._from_email,
                    "to": [email],
                    "subject": "Reset your Koulu password",
                    "html": f"""
                <h1>Password Reset Request</h1>
                <p>Click the link below to reset your password:</p>
                <p><a href="{reset_url}">Reset Password</a></p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request a password reset, you can ignore this email.</p>
                """,
                }
            )
            logger.info("password_reset_email_sent", email=email)
        except Exception as e:
            logger.error("password_reset_email_failed", email=email, error=str(e))
            raise

    async def send_password_changed_email(
        self,
        email: str,
    ) -> None:
        """Send password changed confirmation email."""
        try:
            resend.Emails.send(
                {
                    "from": self._from_email,
                    "to": [email],
                    "subject": "Your Koulu password was changed",
                    "html": """
                <h1>Password Changed</h1>
                <p>Your password was successfully changed.</p>
                <p>If you didn't make this change, please contact support immediately.</p>
                """,
                }
            )
            logger.info("password_changed_email_sent", email=email)
        except Exception as e:
            logger.error("password_changed_email_failed", email=email, error=str(e))
            raise

    async def send_welcome_email(
        self,
        email: str,
        display_name: str,
    ) -> None:
        """Send welcome email after profile completion."""
        try:
            resend.Emails.send(
                {
                    "from": self._from_email,
                    "to": [email],
                    "subject": "Welcome to Koulu!",
                    "html": f"""
                <h1>Welcome, {display_name}!</h1>
                <p>Your account is all set up and ready to go.</p>
                <p>Start exploring communities and connecting with others!</p>
                <p><a href="{self._frontend_url}">Go to Koulu</a></p>
                """,
                }
            )
            logger.info("welcome_email_sent", email=email)
        except Exception as e:
            logger.error("welcome_email_failed", email=email, error=str(e))
            raise
