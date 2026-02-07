"""Community domain exceptions."""


class CommunityDomainError(Exception):
    """Base exception for all community domain errors."""

    pass


# Post validation errors
class PostTitleRequiredError(CommunityDomainError):
    """Raised when post title is empty."""

    def __init__(self) -> None:
        super().__init__("Title is required")


class PostTitleTooLongError(CommunityDomainError):
    """Raised when post title exceeds maximum length."""

    def __init__(self, max_length: int) -> None:
        super().__init__(f"Title must be {max_length} characters or less")


class PostContentRequiredError(CommunityDomainError):
    """Raised when post content is empty."""

    def __init__(self) -> None:
        super().__init__("Content is required")


class PostContentTooLongError(CommunityDomainError):
    """Raised when post content exceeds maximum length."""

    def __init__(self, max_length: int) -> None:
        super().__init__(f"Content must be {max_length} characters or less")


class InvalidImageUrlError(CommunityDomainError):
    """Raised when image URL is not HTTPS."""

    def __init__(self) -> None:
        super().__init__("Image URL must use HTTPS")


# Post state errors
class PostNotFoundError(CommunityDomainError):
    """Raised when a post cannot be found."""

    def __init__(self, post_id: str) -> None:
        super().__init__(f"Post not found: {post_id}")
        self.post_id = post_id


class PostAlreadyDeletedError(CommunityDomainError):
    """Raised when attempting to modify a deleted post."""

    def __init__(self) -> None:
        super().__init__("Post has been deleted")


# Authorization errors
class NotPostAuthorError(CommunityDomainError):
    """Raised when user is not the post author and doesn't have permission."""

    def __init__(self) -> None:
        super().__init__("You don't have permission to edit this post")


class CannotDeletePostError(CommunityDomainError):
    """Raised when user cannot delete a post."""

    def __init__(self) -> None:
        super().__init__("You don't have permission to delete this post")


class CannotPinPostError(CommunityDomainError):
    """Raised when user cannot pin a post."""

    def __init__(self) -> None:
        super().__init__("You don't have permission to pin posts")


class CannotLockPostError(CommunityDomainError):
    """Raised when user cannot lock a post."""

    def __init__(self) -> None:
        super().__init__("You don't have permission to lock posts")


# Category errors
class CategoryNotFoundError(CommunityDomainError):
    """Raised when a category cannot be found."""

    def __init__(self, category_name: str | None = None) -> None:
        message = f"Category not found: {category_name}" if category_name else "Category not found"
        super().__init__(message)


class CategoryHasPostsError(CommunityDomainError):
    """Raised when attempting to delete a category that has posts."""

    def __init__(self) -> None:
        super().__init__("Cannot delete category with posts. Reassign posts first.")


class CategoryNameExistsError(CommunityDomainError):
    """Raised when category name already exists."""

    def __init__(self) -> None:
        super().__init__("Category name already exists")


class CannotManageCategoriesError(CommunityDomainError):
    """Raised when user cannot manage categories."""

    def __init__(self) -> None:
        super().__init__("You don't have permission to create categories")


# Comment errors
class CommentContentRequiredError(CommunityDomainError):
    """Raised when comment content is empty."""

    def __init__(self) -> None:
        super().__init__("Comment content is required")


class CommentContentTooLongError(CommunityDomainError):
    """Raised when comment content exceeds maximum length."""

    def __init__(self, max_length: int) -> None:
        super().__init__(f"Comment must be {max_length} characters or less")


class PostLockedError(CommunityDomainError):
    """Raised when attempting to comment on a locked post."""

    def __init__(self) -> None:
        super().__init__("Post is locked. Comments are disabled.")


class MaxReplyDepthExceededError(CommunityDomainError):
    """Raised when attempting to reply beyond maximum depth."""

    def __init__(self) -> None:
        super().__init__("Maximum reply depth exceeded")


class CannotEditCommentError(CommunityDomainError):
    """Raised when user cannot edit a comment."""

    def __init__(self) -> None:
        super().__init__("You don't have permission to edit this comment")


class CannotDeleteCommentError(CommunityDomainError):
    """Raised when user cannot delete a comment."""

    def __init__(self) -> None:
        super().__init__("You don't have permission to delete this comment")


class CommentNotFoundError(CommunityDomainError):
    """Raised when a comment cannot be found."""

    def __init__(self, comment_id: str) -> None:
        super().__init__(f"Comment not found: {comment_id}")
        self.comment_id = comment_id


# Community membership errors
class NotCommunityMemberError(CommunityDomainError):
    """Raised when user is not a member of the community."""

    def __init__(self) -> None:
        super().__init__("You are not a member of this community")


class MemberNotFoundError(CommunityDomainError):
    """Raised when a community member cannot be found."""

    def __init__(self) -> None:
        super().__init__("Community member not found")


# Rate limiting errors
class RateLimitExceededError(CommunityDomainError):
    """Raised when rate limit is exceeded."""

    def __init__(self) -> None:
        super().__init__("Rate limit exceeded. Try again later.")


# Authentication errors
class AuthenticationRequiredError(CommunityDomainError):
    """Raised when authentication is required but not provided."""

    def __init__(self) -> None:
        super().__init__("Authentication required")
