"""Pydantic schemas for Community API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ============================================================================
# Request Schemas
# ============================================================================


class CreatePostRequest(BaseModel):
    """Request body for creating a post."""

    title: str = Field(..., min_length=1, max_length=300)
    content: str = Field(..., min_length=1)
    category_id: UUID | None = None
    category_name: str | None = None
    image_url: str | None = None


class UpdatePostRequest(BaseModel):
    """Request body for updating a post."""

    title: str | None = Field(None, min_length=1, max_length=300)
    content: str | None = Field(None, min_length=1)
    image_url: str | None = None
    category_id: UUID | None = None


# ============================================================================
# Response Schemas
# ============================================================================


class CreatePostResponse(BaseModel):
    """Response for successful post creation."""

    id: UUID


class PostResponse(BaseModel):
    """Post response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    community_id: UUID
    author_id: UUID
    category_id: UUID
    title: str
    content: str
    image_url: str | None
    is_pinned: bool
    is_locked: bool
    is_edited: bool
    created_at: datetime
    updated_at: datetime
    edited_at: datetime | None


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


class ErrorResponse(BaseModel):
    """Error response."""

    code: str
    message: str
