"""Pydantic schemas for Gamification API."""

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
