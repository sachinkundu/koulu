"""Email service implementation using SMTP (for local dev and E2E tests with MailHog)."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import structlog

from src.config import settings
from src.identity.domain.services import IEmailService

logger = structlog.get_logger()


class SmtpEmailService(IEmailService):
    """
    Email service that sends via SMTP.

    Used for local development and E2E tests with MailHog.
    """

    def __init__(self) -> None:
        """Initialize SMTP email service."""
        self._host = settings.smtp_host
        self._port = settings.smtp_port
        self._from_email = f"{settings.mail_from_name} <{settings.mail_from}>"
        self._frontend_url = settings.frontend_url

    def _send(self, to: str, subject: str, html: str) -> None:
        """Send an email via SMTP."""
        msg = MIMEMultipart("alternative")
        msg["From"] = self._from_email
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(self._host, self._port) as server:
            server.sendmail(self._from_email, [to], msg.as_string())

    async def send_verification_email(self, email: str, token: str) -> None:
        """Send email verification email."""
        verification_url = f"{self._frontend_url}/verify?token={token}"
        try:
            self._send(
                email,
                "Verify your Koulu account",
                f"""
                <h1>Welcome to Koulu!</h1>
                <p>Please verify your email address by clicking the link below:</p>
                <p><a href="{verification_url}">Verify Email</a></p>
                <p>This link will expire in 24 hours.</p>
                <p>If you didn't create an account, you can ignore this email.</p>
                """,
            )
            logger.info("verification_email_sent", email=email)
        except Exception as e:
            logger.error("verification_email_failed", email=email, error=str(e))
            raise

    async def send_password_reset_email(self, email: str, token: str) -> None:
        """Send password reset email."""
        reset_url = f"{self._frontend_url}/reset-password?token={token}"
        try:
            self._send(
                email,
                "Reset your Koulu password",
                f"""
                <h1>Password Reset Request</h1>
                <p>Click the link below to reset your password:</p>
                <p><a href="{reset_url}">Reset Password</a></p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request a password reset, you can ignore this email.</p>
                """,
            )
            logger.info("password_reset_email_sent", email=email)
        except Exception as e:
            logger.error("password_reset_email_failed", email=email, error=str(e))
            raise

    async def send_password_changed_email(self, email: str) -> None:
        """Send password changed confirmation email."""
        try:
            self._send(
                email,
                "Your Koulu password was changed",
                """
                <h1>Password Changed</h1>
                <p>Your password was successfully changed.</p>
                <p>If you didn't make this change, please contact support immediately.</p>
                """,
            )
            logger.info("password_changed_email_sent", email=email)
        except Exception as e:
            logger.error("password_changed_email_failed", email=email, error=str(e))
            raise

    async def send_welcome_email(self, email: str, display_name: str) -> None:
        """Send welcome email after profile completion."""
        try:
            self._send(
                email,
                "Welcome to Koulu!",
                f"""
                <h1>Welcome, {display_name}!</h1>
                <p>Your account is all set up and ready to go.</p>
                <p>Start exploring communities and connecting with others!</p>
                <p><a href="{self._frontend_url}">Go to Koulu</a></p>
                """,
            )
            logger.info("welcome_email_sent", email=email)
        except Exception as e:
            logger.error("welcome_email_failed", email=email, error=str(e))
            raise
