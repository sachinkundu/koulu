"""Update module command."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UpdateModuleCommand:
    """Command to update a module."""

    module_id: UUID
    title: str | None = None
    description: str | None = None
