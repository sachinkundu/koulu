"""Delete module command."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DeleteModuleCommand:
    """Command to soft delete a module."""

    module_id: UUID
