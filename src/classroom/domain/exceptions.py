"""Classroom domain exceptions."""


class ClassroomDomainError(Exception):
    """Base exception for all classroom domain errors."""

    pass


# Course validation errors
class CourseTitleRequiredError(ClassroomDomainError):
    """Raised when course title is empty."""

    def __init__(self) -> None:
        super().__init__("Title is required")


class CourseTitleTooShortError(ClassroomDomainError):
    """Raised when course title is too short."""

    def __init__(self, min_length: int) -> None:
        super().__init__(f"Title must be at least {min_length} characters")


class CourseTitleTooLongError(ClassroomDomainError):
    """Raised when course title exceeds maximum length."""

    def __init__(self, max_length: int) -> None:
        super().__init__(f"Title must be {max_length} characters or less")


class CourseDescriptionTooLongError(ClassroomDomainError):
    """Raised when course description exceeds maximum length."""

    def __init__(self, max_length: int) -> None:
        super().__init__(f"Description must be {max_length} characters or less")


class InvalidCoverImageUrlError(ClassroomDomainError):
    """Raised when cover image URL is not a valid HTTPS URL."""

    def __init__(self) -> None:
        super().__init__("Cover image URL must be a valid HTTPS URL")


# Course state errors
class CourseNotFoundError(ClassroomDomainError):
    """Raised when a course cannot be found."""

    def __init__(self, course_id: str) -> None:
        super().__init__(f"Course not found: {course_id}")
        self.course_id = course_id


class CourseAlreadyDeletedError(ClassroomDomainError):
    """Raised when attempting to modify a deleted course."""

    def __init__(self) -> None:
        super().__init__("Course has been deleted")


# Module validation errors
class ModuleTitleRequiredError(ClassroomDomainError):
    """Raised when module title is empty."""

    def __init__(self) -> None:
        super().__init__("Title is required")


class ModuleTitleTooShortError(ClassroomDomainError):
    """Raised when module title is too short."""

    def __init__(self, min_length: int) -> None:
        super().__init__(f"Title must be at least {min_length} characters")


class ModuleTitleTooLongError(ClassroomDomainError):
    """Raised when module title exceeds maximum length."""

    def __init__(self, max_length: int) -> None:
        super().__init__(f"Title must be {max_length} characters or less")


class ModuleDescriptionTooLongError(ClassroomDomainError):
    """Raised when module description exceeds maximum length."""

    def __init__(self, max_length: int) -> None:
        super().__init__(f"Description must be {max_length} characters or less")


# Module state errors
class ModuleNotFoundError(ClassroomDomainError):
    """Raised when a module cannot be found."""

    def __init__(self, module_id: str) -> None:
        super().__init__(f"Module not found: {module_id}")
        self.module_id = module_id


class ModuleLimitExceededError(ClassroomDomainError):
    """Raised when module limit is exceeded."""

    def __init__(self, max_modules: int) -> None:
        super().__init__(f"Maximum {max_modules} modules allowed per course")


class ModuleHasLessonsError(ClassroomDomainError):
    """Raised when attempting to hard delete a module that has lessons."""

    def __init__(self) -> None:
        super().__init__("Module has lessons and cannot be hard deleted")


# Lesson validation errors
class LessonTitleRequiredError(ClassroomDomainError):
    """Raised when lesson title is empty."""

    def __init__(self) -> None:
        super().__init__("Title is required")


class LessonTitleTooShortError(ClassroomDomainError):
    """Raised when lesson title is too short."""

    def __init__(self, min_length: int) -> None:
        super().__init__(f"Title must be at least {min_length} characters")


class LessonTitleTooLongError(ClassroomDomainError):
    """Raised when lesson title exceeds maximum length."""

    def __init__(self, max_length: int) -> None:
        super().__init__(f"Title must be {max_length} characters or less")


# Lesson state errors
class LessonNotFoundError(ClassroomDomainError):
    """Raised when a lesson cannot be found."""

    def __init__(self, lesson_id: str) -> None:
        super().__init__(f"Lesson not found: {lesson_id}")
        self.lesson_id = lesson_id


class LessonLimitExceededError(ClassroomDomainError):
    """Raised when lesson limit is exceeded."""

    def __init__(self, max_lessons: int) -> None:
        super().__init__(f"Maximum {max_lessons} lessons allowed per module")


# Content validation errors
class InvalidContentTypeError(ClassroomDomainError):
    """Raised when content type is not valid."""

    def __init__(self, content_type: str) -> None:
        super().__init__(f"Invalid content type: {content_type}")


class TextContentRequiredError(ClassroomDomainError):
    """Raised when text content is empty."""

    def __init__(self) -> None:
        super().__init__("Content is required")


class TextContentTooLongError(ClassroomDomainError):
    """Raised when text content exceeds maximum length."""

    def __init__(self, max_length: int) -> None:
        super().__init__(f"Content must be {max_length} characters or less")


class VideoUrlRequiredError(ClassroomDomainError):
    """Raised when video URL is empty."""

    def __init__(self) -> None:
        super().__init__("Video URL is required")


class InvalidVideoUrlError(ClassroomDomainError):
    """Raised when video URL is not a valid YouTube, Vimeo, or Loom URL."""

    def __init__(self) -> None:
        super().__init__("Invalid video URL. Supported: YouTube, Vimeo, Loom")


# Position errors
class InvalidPositionError(ClassroomDomainError):
    """Raised when position values are invalid."""

    def __init__(self, reason: str = "Invalid position") -> None:
        super().__init__(reason)


# Progress errors
class ProgressNotFoundError(ClassroomDomainError):
    """Raised when progress cannot be found for a user and course."""

    def __init__(self, user_id: str, course_id: str) -> None:
        super().__init__(f"Progress not found for user {user_id} on course {course_id}")
        self.user_id = user_id
        self.course_id = course_id


class ProgressAlreadyExistsError(ClassroomDomainError):
    """Raised when progress already exists for a user and course."""

    def __init__(self, user_id: str, course_id: str) -> None:
        super().__init__(f"Progress already exists for user {user_id} on course {course_id}")


class LessonAlreadyCompletedError(ClassroomDomainError):
    """Raised when a lesson is already marked as complete."""

    def __init__(self, lesson_id: str) -> None:
        super().__init__(f"Lesson already completed: {lesson_id}")
        self.lesson_id = lesson_id


class LessonNotCompletedError(ClassroomDomainError):
    """Raised when trying to unmark a lesson that isn't completed."""

    def __init__(self, lesson_id: str) -> None:
        super().__init__(f"Lesson not completed: {lesson_id}")
        self.lesson_id = lesson_id
