"""Gamification repository interfaces."""

from src.gamification.domain.repositories.course_level_requirement_repository import (
    ICourseLevelRequirementRepository,
)
from src.gamification.domain.repositories.level_config_repository import ILevelConfigRepository
from src.gamification.domain.repositories.member_points_repository import IMemberPointsRepository

__all__ = [
    "ICourseLevelRequirementRepository",
    "ILevelConfigRepository",
    "IMemberPointsRepository",
]
