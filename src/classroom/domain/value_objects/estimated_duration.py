"""EstimatedDuration value object."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EstimatedDuration:
    """
    Estimated duration value object.

    Free-form string (e.g., "8 hours", "2 weeks").
    """

    value: str

    def __post_init__(self) -> None:
        """Normalize whitespace."""
        stripped = self.value.strip()
        object.__setattr__(self, "value", stripped)

    def __str__(self) -> str:
        """Return the duration string."""
        return self.value
