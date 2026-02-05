"""Unit tests for JWTService."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest

from src.identity.domain.value_objects import UserId
from src.identity.infrastructure.services.jwt_service import JWTService


@pytest.fixture
def jwt_service() -> JWTService:
    """Create a JWT service instance."""
    return JWTService(
        secret_key="test-secret-key-at-least-32-characters-long",
        algorithm="HS256",
        access_token_expire_minutes=30,
        refresh_token_expire_days=7,
        refresh_token_remember_me_days=30,
    )


@pytest.fixture
def user_id() -> UserId:
    """Create a test user ID."""
    return UserId(uuid4())


class TestGenerateAuthTokens:
    """Tests for generate_auth_tokens()."""

    def test_returns_auth_tokens_with_all_fields(
        self, jwt_service: JWTService, user_id: UserId
    ) -> None:
        """Should return AuthTokens with access_token, refresh_token, etc."""
        result = jwt_service.generate_auth_tokens(user_id)

        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.token_type == "bearer"
        assert result.expires_at is not None

    def test_access_token_contains_user_id(self, jwt_service: JWTService, user_id: UserId) -> None:
        """Access token should contain the user ID in 'sub' claim."""
        result = jwt_service.generate_auth_tokens(user_id)

        payload = jwt.decode(
            result.access_token,
            "test-secret-key-at-least-32-characters-long",
            algorithms=["HS256"],
        )
        assert payload["sub"] == str(user_id.value)
        assert payload["type"] == "access"

    def test_refresh_token_contains_user_id(self, jwt_service: JWTService, user_id: UserId) -> None:
        """Refresh token should contain the user ID in 'sub' claim."""
        result = jwt_service.generate_auth_tokens(user_id)

        payload = jwt.decode(
            result.refresh_token,
            "test-secret-key-at-least-32-characters-long",
            algorithms=["HS256"],
        )
        assert payload["sub"] == str(user_id.value)
        assert payload["type"] == "refresh"

    def test_refresh_token_has_unique_jti(self, jwt_service: JWTService, user_id: UserId) -> None:
        """Each refresh token should have a unique JTI for rotation tracking."""
        result1 = jwt_service.generate_auth_tokens(user_id)
        result2 = jwt_service.generate_auth_tokens(user_id)

        payload1 = jwt.decode(
            result1.refresh_token,
            "test-secret-key-at-least-32-characters-long",
            algorithms=["HS256"],
        )
        payload2 = jwt.decode(
            result2.refresh_token,
            "test-secret-key-at-least-32-characters-long",
            algorithms=["HS256"],
        )

        assert payload1["jti"] != payload2["jti"]

    def test_remember_me_extends_refresh_token_expiry(
        self, jwt_service: JWTService, user_id: UserId
    ) -> None:
        """remember_me=True should extend refresh token to 30 days."""
        normal = jwt_service.generate_auth_tokens(user_id, remember_me=False)
        extended = jwt_service.generate_auth_tokens(user_id, remember_me=True)

        normal_payload = jwt.decode(
            normal.refresh_token,
            "test-secret-key-at-least-32-characters-long",
            algorithms=["HS256"],
        )
        extended_payload = jwt.decode(
            extended.refresh_token,
            "test-secret-key-at-least-32-characters-long",
            algorithms=["HS256"],
        )

        # Extended should expire later than normal
        assert extended_payload["exp"] > normal_payload["exp"]


class TestValidateAccessToken:
    """Tests for validate_access_token()."""

    def test_valid_access_token_returns_user_id(
        self, jwt_service: JWTService, user_id: UserId
    ) -> None:
        """Valid access token should return the user ID."""
        tokens = jwt_service.generate_auth_tokens(user_id)

        result = jwt_service.validate_access_token(tokens.access_token)

        assert result is not None
        assert result.value == user_id.value

    def test_invalid_token_returns_none(self, jwt_service: JWTService) -> None:
        """Invalid token should return None."""
        result = jwt_service.validate_access_token("invalid-token")

        assert result is None

    def test_refresh_token_rejected_as_access_token(
        self, jwt_service: JWTService, user_id: UserId
    ) -> None:
        """Refresh token should not be accepted as access token."""
        tokens = jwt_service.generate_auth_tokens(user_id)

        result = jwt_service.validate_access_token(tokens.refresh_token)

        assert result is None

    def test_expired_access_token_returns_none(
        self, jwt_service: JWTService, user_id: UserId
    ) -> None:
        """Expired access token should return None."""
        # Create a service with very short expiry
        short_service = JWTService(
            secret_key="test-secret-key-at-least-32-characters-long",
            access_token_expire_minutes=-1,  # Already expired
        )
        tokens = short_service.generate_auth_tokens(user_id)

        result = jwt_service.validate_access_token(tokens.access_token)

        assert result is None

    def test_token_with_wrong_signature_returns_none(
        self, jwt_service: JWTService, user_id: UserId
    ) -> None:
        """Token signed with different key should return None."""
        other_service = JWTService(
            secret_key="different-secret-key-at-least-32-characters",
        )
        tokens = other_service.generate_auth_tokens(user_id)

        result = jwt_service.validate_access_token(tokens.access_token)

        assert result is None


class TestValidateRefreshToken:
    """Tests for validate_refresh_token()."""

    def test_valid_refresh_token_returns_user_id(
        self, jwt_service: JWTService, user_id: UserId
    ) -> None:
        """Valid refresh token should return the user ID."""
        tokens = jwt_service.generate_auth_tokens(user_id)

        result = jwt_service.validate_refresh_token(tokens.refresh_token)

        assert result is not None
        assert result.value == user_id.value

    def test_invalid_token_returns_none(self, jwt_service: JWTService) -> None:
        """Invalid token should return None."""
        result = jwt_service.validate_refresh_token("invalid-token")

        assert result is None

    def test_access_token_rejected_as_refresh_token(
        self, jwt_service: JWTService, user_id: UserId
    ) -> None:
        """Access token should not be accepted as refresh token."""
        tokens = jwt_service.generate_auth_tokens(user_id)

        result = jwt_service.validate_refresh_token(tokens.access_token)

        assert result is None


class TestGenerateVerificationToken:
    """Tests for generate_verification_token()."""

    def test_returns_non_empty_string(self, jwt_service: JWTService) -> None:
        """Should return a non-empty token string."""
        result = jwt_service.generate_verification_token()

        assert result is not None
        assert len(result) > 0

    def test_generates_unique_tokens(self, jwt_service: JWTService) -> None:
        """Each call should generate a unique token."""
        token1 = jwt_service.generate_verification_token()
        token2 = jwt_service.generate_verification_token()

        assert token1 != token2


class TestGenerateResetToken:
    """Tests for generate_reset_token()."""

    def test_returns_non_empty_string(self, jwt_service: JWTService) -> None:
        """Should return a non-empty token string."""
        result = jwt_service.generate_reset_token()

        assert result is not None
        assert len(result) > 0

    def test_generates_unique_tokens(self, jwt_service: JWTService) -> None:
        """Each call should generate a unique token."""
        token1 = jwt_service.generate_reset_token()
        token2 = jwt_service.generate_reset_token()

        assert token1 != token2


class TestTokenExpiry:
    """Tests for token expiry methods."""

    def test_verification_token_expires_in_24_hours(self, jwt_service: JWTService) -> None:
        """Verification token expiry should be ~24 hours from now."""
        before = datetime.now(UTC)
        expiry = jwt_service.get_verification_token_expiry()
        after = datetime.now(UTC)

        # Should be between 23:59 and 24:01 hours from now
        min_expected = before + timedelta(hours=23, minutes=59)
        max_expected = after + timedelta(hours=24, minutes=1)

        assert min_expected <= expiry <= max_expected

    def test_reset_token_expires_in_1_hour(self, jwt_service: JWTService) -> None:
        """Reset token expiry should be ~1 hour from now."""
        before = datetime.now(UTC)
        expiry = jwt_service.get_reset_token_expiry()
        after = datetime.now(UTC)

        # Should be between 59 and 61 minutes from now
        min_expected = before + timedelta(minutes=59)
        max_expected = after + timedelta(minutes=61)

        assert min_expected <= expiry <= max_expected
