"""LevelConfiguration repository interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.gamification.domain.entities.level_configuration import LevelConfiguration


class ILevelConfigRepository(ABC):
    """Interface for LevelConfiguration persistence."""

    @abstractmethod
    async def get_by_community(self, community_id: UUID) -> LevelConfiguration | None: ...

    @abstractmethod
    async def save(self, config: LevelConfiguration) -> None: ...
