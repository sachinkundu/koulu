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


class AddModuleRequest(BaseModel):
    """Request body for adding a module to a course."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)


class UpdateModuleRequest(BaseModel):
    """Request body for updating a module."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)


class ReorderRequest(BaseModel):
    """Request body for reordering modules or lessons."""

    ordered_ids: list[UUID]


class AddLessonRequest(BaseModel):
    """Request body for adding a lesson to a module."""

    title: str = Field(..., min_length=1, max_length=200)
    content_type: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)


class UpdateLessonRequest(BaseModel):
    """Request body for updating a lesson."""

    title: str | None = Field(None, min_length=1, max_length=200)
    content_type: str | None = None
    content: str | None = None


# ============================================================================
# Response Schemas
# ============================================================================


class CreateCourseResponse(BaseModel):
    """Response for successful course creation."""

    id: UUID


class CreateModuleResponse(BaseModel):
    """Response for successful module creation."""

    id: UUID


class CreateLessonResponse(BaseModel):
    """Response for successful lesson creation."""

    id: UUID


class LessonResponse(BaseModel):
    """Lesson response within a module."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    content_type: str
    position: int
    created_at: datetime
    updated_at: datetime


class LessonDetailResponse(BaseModel):
    """Lesson detail response including content."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    content_type: str
    content: str
    position: int
    created_at: datetime
    updated_at: datetime


class ModuleResponse(BaseModel):
    """Module response within a course."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    position: int
    lesson_count: int = 0
    created_at: datetime
    updated_at: datetime


class ModuleDetailResponse(BaseModel):
    """Module detail response including lessons."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    position: int
    lesson_count: int = 0
    lessons: list[LessonDetailResponse] = []
    created_at: datetime
    updated_at: datetime


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
    """Course detail response with modules and lessons."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    instructor_id: UUID
    title: str
    description: str | None
    cover_image_url: str | None
    estimated_duration: str | None
    module_count: int = 0
    lesson_count: int = 0
    modules: list[ModuleDetailResponse] = []
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
