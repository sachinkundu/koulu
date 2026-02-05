"""Domain exceptions for the Identity context."""


class IdentityDomainError(Exception):
    """Base exception for Identity domain errors."""

    def __init__(self, message: str, code: str) -> None:
        """Initialize with message and error code."""
        super().__init__(message)
        self.message = message
        self.code = code


class InvalidEmailError(IdentityDomainError):
    """Raised when an email address is invalid."""

    def __init__(self, email: str) -> None:
        """Initialize with the invalid email."""
        super().__init__(
            message=f"Invalid email address: {email}",
            code="invalid_email",
        )
        self.email = email


class PasswordTooShortError(IdentityDomainError):
    """Raised when a password is too short."""

    def __init__(self, min_length: int = 8) -> None:
        """Initialize with the minimum length."""
        super().__init__(
            message=f"Password must be at least {min_length} characters",
            code="password_too_short",
        )
        self.min_length = min_length


class PasswordTooLongError(IdentityDomainError):
    """Raised when a password is too long."""

    def __init__(self, max_length: int = 128) -> None:
        """Initialize with the maximum length."""
        super().__init__(
            message=f"Password must be at most {max_length} characters",
            code="password_too_long",
        )
        self.max_length = max_length


class InvalidDisplayNameError(IdentityDomainError):
    """Raised when a display name is invalid."""

    def __init__(self, reason: str) -> None:
        """Initialize with the reason for invalidity."""
        super().__init__(
            message=f"Invalid display name: {reason}",
            code="invalid_display_name",
        )
        self.reason = reason


class UserNotFoundError(IdentityDomainError):
    """Raised when a user is not found."""

    def __init__(self, identifier: str) -> None:
        """Initialize with the identifier used to search."""
        super().__init__(
            message=f"User not found: {identifier}",
            code="user_not_found",
        )
        self.identifier = identifier


class UserAlreadyExistsError(IdentityDomainError):
    """Raised when attempting to create a user that already exists."""

    def __init__(self, email: str) -> None:
        """Initialize with the email that already exists."""
        super().__init__(
            message=f"User already exists with email: {email}",
            code="user_already_exists",
        )
        self.email = email


class UserAlreadyVerifiedError(IdentityDomainError):
    """Raised when attempting to verify an already verified user."""

    def __init__(self) -> None:
        """Initialize the exception."""
        super().__init__(
            message="User is already verified",
            code="already_verified",
        )


class UserNotVerifiedError(IdentityDomainError):
    """Raised when a user is not verified but verification is required."""

    def __init__(self) -> None:
        """Initialize the exception."""
        super().__init__(
            message="Email not verified",
            code="email_not_verified",
        )


class UserDisabledError(IdentityDomainError):
    """Raised when a user account is disabled."""

    def __init__(self) -> None:
        """Initialize the exception."""
        super().__init__(
            message="Account is disabled",
            code="account_disabled",
        )


class InvalidCredentialsError(IdentityDomainError):
    """Raised when login credentials are invalid."""

    def __init__(self) -> None:
        """Initialize the exception."""
        super().__init__(
            message="Invalid email or password",
            code="invalid_credentials",
        )


class InvalidTokenError(IdentityDomainError):
    """Raised when a token is invalid or expired."""

    def __init__(self, reason: str = "Token is invalid or expired") -> None:
        """Initialize with optional reason."""
        super().__init__(
            message=reason,
            code="invalid_token",
        )
        self.reason = reason


class RateLimitExceededError(IdentityDomainError):
    """Raised when rate limit is exceeded."""

    def __init__(self, retry_after: int | None = None) -> None:
        """Initialize with optional retry-after seconds."""
        super().__init__(
            message="Rate limit exceeded. Please try again later.",
            code="rate_limited",
        )
        self.retry_after = retry_after


class InvalidLocationError(IdentityDomainError):
    """Raised when a location value is invalid."""

    def __init__(self, reason: str) -> None:
        """Initialize with the reason for invalidity."""
        super().__init__(
            message=f"Invalid location: {reason}",
            code="invalid_location",
        )
        self.reason = reason


class InvalidSocialLinkError(IdentityDomainError):
    """Raised when a social link URL is invalid."""

    def __init__(self, reason: str) -> None:
        """Initialize with the reason for invalidity."""
        super().__init__(
            message=f"Invalid social link: {reason}",
            code="invalid_social_link",
        )
        self.reason = reason


class InvalidBioError(IdentityDomainError):
    """Raised when a bio value is invalid."""

    def __init__(self, reason: str) -> None:
        """Initialize with the reason for invalidity."""
        super().__init__(
            message=f"Invalid bio: {reason}",
            code="invalid_bio",
        )
        self.reason = reason


class ProfileNotFoundError(IdentityDomainError):
    """Raised when a profile is not found."""

    def __init__(self, user_id: str) -> None:
        """Initialize with the user ID."""
        super().__init__(
            message=f"Profile not found for user: {user_id}",
            code="profile_not_found",
        )
        self.user_id = user_id
