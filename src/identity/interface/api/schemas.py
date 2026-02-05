"""Pydantic schemas for Identity API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# ============================================================================
# Request Schemas
# ============================================================================


class RegisterRequest(BaseModel):
    """Request body for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """Request body for user login."""

    email: EmailStr
    password: str
    remember_me: bool = False


class VerifyEmailRequest(BaseModel):
    """Request body for email verification."""

    token: str


class ResendVerificationRequest(BaseModel):
    """Request body for resending verification email."""

    email: EmailStr


class RefreshTokenRequest(BaseModel):
    """Request body for token refresh."""

    refresh_token: str


class LogoutRequest(BaseModel):
    """Request body for logout."""

    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    """Request body for password reset request."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Request body for password reset."""

    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class CompleteProfileRequest(BaseModel):
    """Request body for completing user profile."""

    display_name: str = Field(..., min_length=2, max_length=50)
    avatar_url: str | None = None


# ============================================================================
# Response Schemas
# ============================================================================


class TokenResponse(BaseModel):
    """Response containing auth tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_at: datetime


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


class ErrorResponse(BaseModel):
    """Error response."""

    code: str
    message: str


class ProfileResponse(BaseModel):
    """User profile response."""

    model_config = ConfigDict(from_attributes=True)

    display_name: str | None
    avatar_url: str | None
    bio: str | None
    is_complete: bool


class UserResponse(BaseModel):
    """User response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    is_verified: bool
    is_active: bool
    profile: ProfileResponse | None
    created_at: datetime
    updated_at: datetime


class RegisterResponse(BaseModel):
    """Response for successful registration."""

    message: str = "Please check your email to verify your account"
