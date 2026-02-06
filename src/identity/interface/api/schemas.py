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


class UpdateProfileRequest(BaseModel):
    """Request body for updating user profile."""

    display_name: str | None = Field(None, min_length=2, max_length=50)
    avatar_url: str | None = None
    bio: str | None = Field(None, max_length=500)
    city: str | None = Field(None, min_length=2, max_length=100)
    country: str | None = Field(None, min_length=2, max_length=100)
    twitter_url: str | None = None
    linkedin_url: str | None = None
    instagram_url: str | None = None
    website_url: str | None = None


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


class ProfileDetailResponse(BaseModel):
    """Detailed profile response with all fields."""

    model_config = ConfigDict(from_attributes=True)

    display_name: str | None
    avatar_url: str | None
    bio: str | None
    location_city: str | None
    location_country: str | None
    twitter_url: str | None
    linkedin_url: str | None
    instagram_url: str | None
    website_url: str | None
    is_complete: bool
    is_own_profile: bool  # Whether the requesting user owns this profile
    created_at: datetime
    updated_at: datetime


class StatsResponse(BaseModel):
    """Profile statistics response."""

    contribution_count: int
    joined_at: datetime


class ActivityItemResponse(BaseModel):
    """Single activity item response."""

    id: str
    type: str
    content: str
    created_at: datetime


class ActivityResponse(BaseModel):
    """Profile activity feed response."""

    items: list[ActivityItemResponse]
    total_count: int


class ActivityChartResponse(BaseModel):
    """30-day activity chart data response."""

    days: list[datetime]
    counts: list[int]


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
