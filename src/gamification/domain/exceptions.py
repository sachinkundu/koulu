"""Gamification domain exceptions."""


class GamificationDomainError(Exception):
    """Base exception for all gamification domain errors."""


class InvalidLevelNumberError(GamificationDomainError):
    """Raised when level number is not 1-9."""

    def __init__(self, value: int) -> None:
        super().__init__(f"Level number must be between 1 and 9, got {value}")
        self.value = value


class InvalidLevelNameError(GamificationDomainError):
    """Raised when level name is invalid."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)


class InvalidThresholdError(GamificationDomainError):
    """Raised when point thresholds are invalid."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)


class DuplicateLessonCompletionError(GamificationDomainError):
    """Raised when lesson completion points already awarded."""

    def __init__(self, lesson_id: str) -> None:
        super().__init__(f"Points already awarded for lesson: {lesson_id}")
        self.lesson_id = lesson_id
