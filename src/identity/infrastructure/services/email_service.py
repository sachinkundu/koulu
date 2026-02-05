"""Email service implementation."""

import structlog
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from src.config import settings

logger = structlog.get_logger()


class EmailService:
    """
    Email service for sending transactional emails.

    Uses FastAPI-Mail for async email sending.
    """

    def __init__(self) -> None:
        """Initialize email service with configuration."""
        self._config = ConnectionConfig(
            MAIL_USERNAME=settings.mail_username,
            MAIL_PASSWORD=settings.mail_password,
            MAIL_FROM=settings.mail_from,
            MAIL_FROM_NAME=settings.mail_from_name,
            MAIL_PORT=settings.mail_port,
            MAIL_SERVER=settings.mail_server,
            MAIL_STARTTLS=settings.mail_tls,
            MAIL_SSL_TLS=settings.mail_ssl,
            USE_CREDENTIALS=bool(settings.mail_username),
        )
        self._mailer = FastMail(self._config)
        self._frontend_url = settings.frontend_url

    async def send_verification_email(
        self,
        email: str,
        token: str,
    ) -> None:
        """
        Send email verification email.

        Args:
            email: Recipient email address
            token: Verification token
        """
        verification_url = f"{self._frontend_url}/verify?token={token}"

        message = MessageSchema(
            subject="Verify your Koulu account",
            recipients=[email],
            body=f"""
            <h1>Welcome to Koulu!</h1>
            <p>Please verify your email address by clicking the link below:</p>
            <p><a href="{verification_url}">Verify Email</a></p>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't create an account, you can ignore this email.</p>
            """,
            subtype=MessageType.html,
        )

        try:
            await self._mailer.send_message(message)
            logger.info("verification_email_sent", email=email)
        except Exception as e:
            logger.error("verification_email_failed", email=email, error=str(e))
            raise

    async def send_password_reset_email(
        self,
        email: str,
        token: str,
    ) -> None:
        """
        Send password reset email.

        Args:
            email: Recipient email address
            token: Reset token
        """
        reset_url = f"{self._frontend_url}/reset-password?token={token}"

        message = MessageSchema(
            subject="Reset your Koulu password",
            recipients=[email],
            body=f"""
            <h1>Password Reset Request</h1>
            <p>Click the link below to reset your password:</p>
            <p><a href="{reset_url}">Reset Password</a></p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request a password reset, you can ignore this email.</p>
            """,
            subtype=MessageType.html,
        )

        try:
            await self._mailer.send_message(message)
            logger.info("password_reset_email_sent", email=email)
        except Exception as e:
            logger.error("password_reset_email_failed", email=email, error=str(e))
            raise

    async def send_password_changed_email(
        self,
        email: str,
    ) -> None:
        """
        Send password changed confirmation email.

        Args:
            email: Recipient email address
        """
        message = MessageSchema(
            subject="Your Koulu password was changed",
            recipients=[email],
            body="""
            <h1>Password Changed</h1>
            <p>Your password was successfully changed.</p>
            <p>If you didn't make this change, please contact support immediately.</p>
            """,
            subtype=MessageType.html,
        )

        try:
            await self._mailer.send_message(message)
            logger.info("password_changed_email_sent", email=email)
        except Exception as e:
            logger.error("password_changed_email_failed", email=email, error=str(e))
            raise

    async def send_welcome_email(
        self,
        email: str,
        display_name: str,
    ) -> None:
        """
        Send welcome email after profile completion.

        Args:
            email: Recipient email address
            display_name: User's display name
        """
        message = MessageSchema(
            subject="Welcome to Koulu!",
            recipients=[email],
            body=f"""
            <h1>Welcome, {display_name}!</h1>
            <p>Your account is all set up and ready to go.</p>
            <p>Start exploring communities and connecting with others!</p>
            <p><a href="{self._frontend_url}">Go to Koulu</a></p>
            """,
            subtype=MessageType.html,
        )

        try:
            await self._mailer.send_message(message)
            logger.info("welcome_email_sent", email=email)
        except Exception as e:
            logger.error("welcome_email_failed", email=email, error=str(e))
            raise
