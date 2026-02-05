"""JWT token service implementation."""

import secrets
from datetime import UTC, datetime, timedelta

import jwt

from src.identity.domain.services import ITokenGenerator
from src.identity.domain.value_objects import AuthTokens, UserId


class JWTService(ITokenGenerator):
    """
    JWT-based token generator.

    - Access tokens: Short-lived (30 min), stateless
    - Refresh tokens: Long-lived (7-30 days), tracked for rotation
    - Verification/reset tokens: Secure random strings
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
        refresh_token_remember_me_days: int = 30,
    ) -> None:
        """
        Initialize JWT service.

        Args:
            secret_key: Secret key for signing tokens (min 32 chars)
            algorithm: JWT algorithm (HS256 recommended)
            access_token_expire_minutes: Access token lifetime
            refresh_token_expire_days: Refresh token lifetime (standard)
            refresh_token_remember_me_days: Refresh token lifetime (remember me)
        """
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_token_expire_minutes = access_token_expire_minutes
        self._refresh_token_expire_days = refresh_token_expire_days
        self._refresh_token_remember_me_days = refresh_token_remember_me_days

    def generate_auth_tokens(
        self,
        user_id: UserId,
        remember_me: bool = False,
    ) -> AuthTokens:
        """Generate access and refresh tokens for a user."""
        now = datetime.now(UTC)

        # Access token
        access_expires = now + timedelta(minutes=self._access_token_expire_minutes)
        access_payload = {
            "sub": str(user_id.value),
            "type": "access",
            "exp": access_expires,
            "iat": now,
        }
        access_token = jwt.encode(
            access_payload,
            self._secret_key,
            algorithm=self._algorithm,
        )

        # Refresh token
        refresh_days = (
            self._refresh_token_remember_me_days if remember_me else self._refresh_token_expire_days
        )
        refresh_expires = now + timedelta(days=refresh_days)
        refresh_payload = {
            "sub": str(user_id.value),
            "type": "refresh",
            "exp": refresh_expires,
            "iat": now,
            "jti": secrets.token_urlsafe(16),  # Unique ID for rotation
        }
        refresh_token = jwt.encode(
            refresh_payload,
            self._secret_key,
            algorithm=self._algorithm,
        )

        return AuthTokens(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_at=access_expires,
        )

    def generate_verification_token(self) -> str:
        """Generate a secure random verification token."""
        return secrets.token_urlsafe(32)

    def generate_reset_token(self) -> str:
        """Generate a secure random password reset token."""
        return secrets.token_urlsafe(32)

    def validate_access_token(self, token: str) -> UserId | None:
        """Validate an access token and extract user ID."""
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
            )
            if payload.get("type") != "access":
                return None
            user_id_str = payload.get("sub")
            if user_id_str is None:
                return None
            return UserId.from_string(user_id_str)
        except jwt.PyJWTError:
            return None

    def validate_refresh_token(self, token: str) -> UserId | None:
        """Validate a refresh token and extract user ID."""
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
            )
            if payload.get("type") != "refresh":
                return None
            user_id_str = payload.get("sub")
            if user_id_str is None:
                return None
            return UserId.from_string(user_id_str)
        except jwt.PyJWTError:
            return None

    def get_verification_token_expiry(self) -> datetime:
        """Get expiry for verification token (24 hours from now)."""
        return datetime.now(UTC) + timedelta(hours=24)

    def get_reset_token_expiry(self) -> datetime:
        """Get expiry for reset token (1 hour from now)."""
        return datetime.now(UTC) + timedelta(hours=1)
