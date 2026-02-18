"""Pydantic schemas for Gamification API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MemberLevelResponse(BaseModel):
    """Response for GET /communities/{id}/members/{user_id}/level."""

    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    level: int
    level_name: str
    total_points: int
    points_to_next_level: int | None
    is_max_level: bool


class LevelDefinitionSchema(BaseModel):
    """A single level definition."""

    level: int
    name: str
    threshold: int
    member_percentage: float


class LevelDefinitionsResponse(BaseModel):
    """Response for GET /communities/{id}/levels."""

    levels: list[LevelDefinitionSchema]
    current_user_level: int


class LevelUpdateSchema(BaseModel):
    """A single level update in a request."""

    level: int
    name: str
    threshold: int


class UpdateLevelConfigRequest(BaseModel):
    """Request body for PUT /communities/{id}/levels."""

    levels: list[LevelUpdateSchema]


class CourseAccessResponse(BaseModel):
    """Response for GET /communities/{id}/courses/{course_id}/access."""

    course_id: UUID
    has_access: bool
    minimum_level: int | None
    minimum_level_name: str | None
    current_level: int


class SetCourseLevelRequirementRequest(BaseModel):
    """Request body for PUT /communities/{id}/courses/{course_id}/level-requirement."""

    minimum_level: int


class LeaderboardEntrySchema(BaseModel):
    """A single ranked member in a leaderboard."""

    rank: int
    user_id: UUID
    display_name: str
    avatar_url: str | None
    level: int
    points: int


class LeaderboardPeriodSchema(BaseModel):
    """One leaderboard period with entries and optional your-rank."""

    entries: list[LeaderboardEntrySchema]
    your_rank: LeaderboardEntrySchema | None


class LeaderboardsResponse(BaseModel):
    """Response for GET /community/leaderboards."""

    seven_day: LeaderboardPeriodSchema
    thirty_day: LeaderboardPeriodSchema
    all_time: LeaderboardPeriodSchema
    last_updated: datetime


class LeaderboardWidgetResponse(BaseModel):
    """Response for GET /community/leaderboards/widget."""

    entries: list[LeaderboardEntrySchema]
    last_updated: datetime
