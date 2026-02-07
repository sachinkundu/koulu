"""Pydantic schemas for Classroom API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ============================================================================
# Request Schemas
# ============================================================================


class CreateCourseRequest(BaseModel):
    """Request body for creating a course."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    cover_image_url: str | None = None
    estimated_duration: str | None = None


class UpdateCourseRequest(BaseModel):
    """Request body for updating a course."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    cover_image_url: str | None = None
    estimated_duration: str | None = None


# ============================================================================
# Response Schemas
# ============================================================================


class CreateCourseResponse(BaseModel):
    """Response for successful course creation."""

    id: UUID


class CourseResponse(BaseModel):
    """Course response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    instructor_id: UUID
    title: str
    description: str | None
    cover_image_url: str | None
    estimated_duration: str | None
    module_count: int = 0
    lesson_count: int = 0
    created_at: datetime
    updated_at: datetime


class CourseDetailResponse(BaseModel):
    """Course detail response (Phase 1: no modules yet)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    instructor_id: UUID
    title: str
    description: str | None
    cover_image_url: str | None
    estimated_duration: str | None
    module_count: int = 0
    lesson_count: int = 0
    created_at: datetime
    updated_at: datetime


class CourseListResponse(BaseModel):
    """Response for course list."""

    courses: list[CourseResponse]
    total: int


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


class ErrorResponse(BaseModel):
    """Error response."""

    detail: str
