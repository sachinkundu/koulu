"""Pydantic schemas for Community API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ============================================================================
# Request Schemas
# ============================================================================


class CreatePostRequest(BaseModel):
    """Request body for creating a post."""

    title: str = Field(..., min_length=1, max_length=300)
    content: str = Field(..., min_length=1)
    category_id: UUID | None = None
    category_name: str | None = None
    image_url: str | None = None


class UpdatePostRequest(BaseModel):
    """Request body for updating a post."""

    title: str | None = Field(None, min_length=1, max_length=300)
    content: str | None = Field(None, min_length=1)
    image_url: str | None = None
    category_id: UUID | None = None


class AddCommentRequest(BaseModel):
    """Request body for adding a comment."""

    content: str = Field(..., min_length=1, max_length=2000)
    parent_comment_id: UUID | None = None


class EditCommentRequest(BaseModel):
    """Request body for editing a comment."""

    content: str = Field(..., min_length=1, max_length=2000)


class CreateCategoryRequest(BaseModel):
    """Request body for creating a category."""

    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    emoji: str = Field(..., min_length=1, max_length=10)
    description: str | None = None


class UpdateCategoryRequest(BaseModel):
    """Request body for updating a category."""

    name: str | None = Field(None, min_length=1, max_length=100)
    emoji: str | None = Field(None, min_length=1, max_length=10)
    description: str | None = None


# ============================================================================
# Response Schemas
# ============================================================================


class CategoryResponse(BaseModel):
    """Category response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    community_id: UUID
    name: str
    slug: str
    emoji: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class CreateCategoryResponse(BaseModel):
    """Response for successful category creation."""

    id: UUID


class CreatePostResponse(BaseModel):
    """Response for successful post creation."""

    id: UUID


class AuthorResponse(BaseModel):
    """Author information for posts."""

    id: UUID
    display_name: str
    avatar_url: str | None


class PostResponse(BaseModel):
    """Post response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    community_id: UUID
    created_by: UUID  # Frontend expects created_by, not author_id
    category_id: UUID
    title: str
    content: str
    image_url: str | None
    is_pinned: bool
    is_locked: bool
    is_edited: bool
    comment_count: int = 0
    like_count: int = 0
    created_at: datetime
    updated_at: datetime
    edited_at: datetime | None
    author: AuthorResponse | None = None  # Optional author information
    liked_by_current_user: bool = False


class CommentResponse(BaseModel):
    """Comment response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    post_id: UUID
    author_id: UUID | None
    content: str
    parent_comment_id: UUID | None
    is_deleted: bool
    like_count: int = 0
    is_edited: bool
    created_at: datetime
    updated_at: datetime
    edited_at: datetime | None
    author: AuthorResponse | None = None


class CreateCommentResponse(BaseModel):
    """Response for successful comment creation."""

    comment_id: UUID
    message: str = "Comment added successfully"


class LikeResponse(BaseModel):
    """Response for like/unlike operations."""

    message: str


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


class FeedResponse(BaseModel):
    """Feed response with list of posts."""

    items: list[PostResponse]  # Frontend expects 'items', not 'posts'
    cursor: str | None  # Frontend uses cursor-based pagination
    has_more: bool  # Indicates if there are more items


# ============================================================================
# Member Directory Schemas
# ============================================================================


class MemberDirectoryItemResponse(BaseModel):
    """Single member entry in the directory."""

    user_id: UUID
    display_name: str | None
    avatar_url: str | None
    role: str
    bio: str | None
    joined_at: datetime


class MemberDirectoryResponse(BaseModel):
    """Paginated member directory response."""

    items: list[MemberDirectoryItemResponse]
    total_count: int
    cursor: str | None
    has_more: bool


class ErrorResponse(BaseModel):
    """Error response."""

    code: str
    message: str


# ============================================================================
# Search Schemas
# ============================================================================


class MemberSearchItemResponse(BaseModel):
    """Member search result item."""

    user_id: UUID
    display_name: str | None
    username: str | None
    avatar_url: str | None
    role: str
    bio: str | None
    joined_at: datetime


class PostSearchItemResponse(BaseModel):
    """Post search result item."""

    id: UUID
    title: str
    body_snippet: str
    author_name: str | None
    author_avatar_url: str | None
    category_name: str | None
    category_emoji: str | None
    created_at: datetime
    like_count: int
    comment_count: int


class SearchResponse(BaseModel):
    """Search results response with tab counts."""

    items: list[MemberSearchItemResponse] | list[PostSearchItemResponse]
    total_count: int
    member_count: int
    post_count: int
    has_more: bool
