"""Base value object class for domain value objects."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BaseValueObject:
    """
    Base class for all domain value objects.

    Value objects are:
    - Immutable (frozen=True ensures this)
    - Compared by value (all fields), not identity
    - Self-validating (validation in __post_init__)

    Subclasses should:
    1. Use @dataclass(frozen=True) decorator
    2. Override __post_init__ to add validation
    3. Raise domain-specific exceptions on invalid input
    """

    def __post_init__(self) -> None:
        """
        Override this method to add validation logic.
        Raise a domain exception if validation fails.

        Base implementation does nothing - subclasses add their validation.
        """
        self._validate()

    def _validate(self) -> None:
        """Override in subclasses to add validation logic."""
