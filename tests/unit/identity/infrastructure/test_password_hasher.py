"""Unit tests for Argon2PasswordHasher."""

import pytest

from src.identity.infrastructure.services.password_hasher import Argon2PasswordHasher


@pytest.fixture
def hasher() -> Argon2PasswordHasher:
    """Create a password hasher instance."""
    return Argon2PasswordHasher()


class TestArgon2PasswordHasher:
    """Tests for Argon2PasswordHasher."""

    def test_hash_returns_hashed_password_value_object(self, hasher: Argon2PasswordHasher) -> None:
        """hash() should return a HashedPassword value object."""
        result = hasher.hash("testpassword123")

        assert result.value is not None
        assert result.value != "testpassword123"  # Not plaintext

    def test_hash_produces_argon2id_format(self, hasher: Argon2PasswordHasher) -> None:
        """Hash should be in Argon2id format."""
        result = hasher.hash("testpassword123")

        assert result.value.startswith("$argon2")

    def test_hash_produces_different_hashes_for_same_password(
        self, hasher: Argon2PasswordHasher
    ) -> None:
        """Same password should produce different hashes (due to salt)."""
        hash1 = hasher.hash("testpassword123")
        hash2 = hasher.hash("testpassword123")

        assert hash1.value != hash2.value

    def test_verify_returns_true_for_correct_password(self, hasher: Argon2PasswordHasher) -> None:
        """verify() should return True for correct password."""
        hashed = hasher.hash("correctpassword")

        result = hasher.verify("correctpassword", hashed)

        assert result is True

    def test_verify_returns_false_for_wrong_password(self, hasher: Argon2PasswordHasher) -> None:
        """verify() should return False for wrong password."""
        hashed = hasher.hash("correctpassword")

        result = hasher.verify("wrongpassword", hashed)

        assert result is False

    def test_verify_returns_false_for_invalid_hash_format(
        self, hasher: Argon2PasswordHasher
    ) -> None:
        """verify() should return False for invalid hash format (not crash)."""
        from src.identity.domain.value_objects import HashedPassword

        invalid_hash = HashedPassword("not-a-valid-hash")

        result = hasher.verify("anypassword", invalid_hash)

        assert result is False

    def test_verify_returns_false_for_empty_password(self, hasher: Argon2PasswordHasher) -> None:
        """verify() should return False for empty password."""
        hashed = hasher.hash("correctpassword")

        result = hasher.verify("", hashed)

        assert result is False
