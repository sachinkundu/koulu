# Community Feed Phase 2: Implementation Guide

**Status:** In Progress (8/14 tasks complete)
**Date:** 2026-02-08
**Goal:** Implement Comments, Reactions & Post Locking (25 new BDD scenarios)

---

## ✅ Completed Work (Tasks 1-6, 8)

### 1. Documentation ✅
- **File:** `docs/features/community/feed-implementation-phases.md`
- **Changes:** Reordered phases - Phase 2 is now Comments/Reactions/Locking (was Roles & Permissions)
- **Impact:** Updated scenario counts, phase markers, and dependency graph

### 2. Domain Value Objects ✅
Created 3 new value objects:

**`src/community/domain/value_objects/comment_id.py`**
```python
@dataclass(frozen=True)
class CommentId:
    value: UUID
```

**`src/community/domain/value_objects/comment_content.py`**
```python
@dataclass(frozen=True)
class CommentContent:
    value: str
    # Validates: 1-2000 chars, sanitizes HTML with bleach
```

**`src/community/domain/value_objects/reaction_id.py`**
```python
@dataclass(frozen=True)
class ReactionId:
    value: UUID
```

### 3. Domain Events ✅
Added 7 new events to `src/community/domain/events.py`:
- `CommentAdded` - has post_id, author_id, content, parent_comment_id
- `CommentEdited` - has comment_id, editor_id
- `CommentDeleted` - has comment_id, deleted_by
- `PostLiked` - has reaction_id, post_id, user_id
- `PostUnliked` - has post_id, user_id
- `CommentLiked` - has reaction_id, comment_id, user_id
- `CommentUnliked` - has comment_id, user_id

### 4. Domain Exceptions ✅
Added to `src/community/domain/exceptions.py`:
- `CommentNotFoundError(comment_id)` - new
- Other comment exceptions already existed

### 5. Domain Entities ✅

**`src/community/domain/entities/comment.py`** - Comment aggregate
```python
class Comment:
    id: CommentId
    post_id: PostId
    author_id: UserId
    content: CommentContent
    parent_comment_id: CommentId | None
    is_deleted: bool

    @classmethod
    def create(...) -> Comment
    def edit(editor_id, editor_role, content) -> None
    def delete(deleter_id, deleter_role, has_replies) -> None
```

**Key behaviors:**
- Soft delete if `has_replies=True` (content becomes "[deleted]")
- Hard delete if `has_replies=False` (repository deletes)
- Max threading depth: 1 (comment → reply, no nested replies)

**`src/community/domain/entities/reaction.py`** - Reaction entity
```python
@dataclass(frozen=True)
class Reaction:
    id: ReactionId
    user_id: UserId
    target_type: str  # "post" or "comment"
    target_id: UUID

    @classmethod
    def create(...) -> Reaction
```

**Modified:** `src/community/domain/entities/post.py`
```python
def lock(locker_id, locker_role) -> None:
    # Check: locker_role.can_lock_posts()
    # Sets is_locked=True, publishes PostLocked

def unlock(unlocker_id, unlocker_role) -> None:
    # Check: unlocker_role.can_lock_posts()
    # Sets is_locked=False, publishes PostUnlocked
```

### 6. Repository Interfaces ✅

**`src/community/domain/repositories/comment_repository.py`**
```python
class ICommentRepository(ABC):
    async def save(comment: Comment) -> None
    async def get_by_id(comment_id) -> Comment | None
    async def list_by_post(post_id, limit, offset) -> list[Comment]
    async def count_by_post(post_id) -> int
    async def has_replies(comment_id) -> bool
    async def delete(comment_id) -> None
    async def delete_by_post(post_id) -> None  # Cascade
```

**`src/community/domain/repositories/reaction_repository.py`**
```python
class IReactionRepository(ABC):
    async def save(reaction: Reaction) -> None
    async def find_by_user_and_target(user_id, target_type, target_id) -> Reaction | None
    async def delete(reaction_id) -> None
    async def delete_by_target(target_type, target_id) -> None
    async def count_by_target(target_type, target_id) -> int
    async def list_users_by_target(target_type, target_id, limit) -> list[UserId]
    async def count_by_user_since(user_id, since) -> int  # For rate limiting
    async def delete_by_post_cascade(post_id) -> None
```

### 7. Application Commands & Queries ✅

**Added to `src/community/application/commands.py`:**
```python
@dataclass(frozen=True)
class LockPostCommand:
    post_id: UUID
    locker_id: UUID

@dataclass(frozen=True)
class UnlockPostCommand:
    post_id: UUID
    unlocker_id: UUID

@dataclass(frozen=True)
class AddCommentCommand:
    post_id: UUID
    author_id: UUID
    content: str
    parent_comment_id: UUID | None = None

@dataclass(frozen=True)
class EditCommentCommand:
    comment_id: UUID
    editor_id: UUID
    content: str

@dataclass(frozen=True)
class DeleteCommentCommand:
    comment_id: UUID
    deleter_id: UUID

@dataclass(frozen=True)
class LikePostCommand:
    post_id: UUID
    user_id: UUID

@dataclass(frozen=True)
class UnlikePostCommand:
    post_id: UUID
    user_id: UUID

@dataclass(frozen=True)
class LikeCommentCommand:
    comment_id: UUID
    user_id: UUID

@dataclass(frozen=True)
class UnlikeCommentCommand:
    comment_id: UUID
    user_id: UUID
```

**Added to `src/community/application/queries.py`:**
```python
@dataclass(frozen=True)
class GetPostCommentsQuery:
    post_id: UUID
    limit: int = 100
    offset: int = 0
```

### 8. Database Models & Migrations ✅

**Modified:** `src/community/infrastructure/persistence/models.py`

Added `CommentModel`:
```python
class CommentModel(Base):
    __tablename__ = "comments"

    id: Mapped[UUID]
    post_id: Mapped[UUID]  # FK posts.id CASCADE
    author_id: Mapped[UUID | None]  # FK users.id SET NULL
    parent_comment_id: Mapped[UUID | None]  # FK comments.id CASCADE
    content: Mapped[str]
    is_deleted: Mapped[bool]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    edited_at: Mapped[datetime | None]

    # Indexes: (post_id, created_at), (parent_comment_id)
```

Added `ReactionModel`:
```python
class ReactionModel(Base):
    __tablename__ = "reactions"

    id: Mapped[UUID]
    user_id: Mapped[UUID]  # FK users.id CASCADE
    target_type: Mapped[str]  # "post" or "comment"
    target_id: Mapped[UUID]
    created_at: Mapped[datetime]

    # Unique: (user_id, target_type, target_id)
    # Index: (target_type, target_id)
```

**Created migrations:**
- `alembic/versions/20260208_1000_create_comments.py` (revision 008)
- `alembic/versions/20260208_1010_create_reactions.py` (revision 009)

---

## 🚧 Remaining Work (Tasks 7, 9-14)

### Task 7: Application Handlers (10 handlers + 1 modified)

**Pattern to follow:** `src/community/application/handlers/create_post_handler.py`

**Common structure for ALL handlers:**
```python
import structlog
from src.shared.domain import IEventBus

class XxxHandler:
    def __init__(
        self,
        xxx_repository: IXxxRepository,
        yyy_repository: IYyyRepository,
        event_bus: IEventBus,
    ) -> None:
        self._xxx_repo = xxx_repository
        self._yyy_repo = yyy_repository
        self._event_bus = event_bus
        self._logger = structlog.get_logger()

    async def handle(self, command: XxxCommand) -> ResultType:
        self._logger.info("xxx.started", xxx_id=str(command.xxx_id))

        # 1. Load aggregates
        # 2. Execute domain logic
        # 3. Save aggregates
        # 4. Publish events
        # 5. Log success

        self._logger.info("xxx.completed", xxx_id=str(command.xxx_id))
        return result
```

#### Handler 1: `lock_post_handler.py`
```python
class LockPostHandler:
    def __init__(self, post_repo, member_repo, event_bus)

    async def handle(self, cmd: LockPostCommand) -> None:
        # 1. Load post: post_repo.get_by_id(PostId(cmd.post_id))
        # 2. Load member: member_repo.get_by_user_and_community(...)
        # 3. Call: post.lock(UserId(cmd.locker_id), member.role)
        # 4. Save: post_repo.save(post)
        # 5. Publish: event_bus.publish(post.clear_events())
```

**Error cases:**
- PostNotFoundError → 404
- CannotLockPostError → 403

#### Handler 2: `unlock_post_handler.py`
```python
class UnlockPostHandler:
    def __init__(self, post_repo, member_repo, event_bus)

    async def handle(self, cmd: UnlockPostCommand) -> None:
        # Similar to lock, but calls post.unlock(...)
```

#### Handler 3: `add_comment_handler.py`
```python
class AddCommentHandler:
    def __init__(self, comment_repo, post_repo, member_repo, event_bus)

    async def handle(self, cmd: AddCommentCommand) -> CommentId:
        # 1. Load post to check is_locked
        #    if post.is_locked: raise PostLockedError()
        # 2. If parent_comment_id, load parent and check depth
        #    if parent.parent_comment_id is not None: raise MaxReplyDepthExceededError()
        # 3. Create: comment = Comment.create(
        #        post_id=PostId(cmd.post_id),
        #        author_id=UserId(cmd.author_id),
        #        content=CommentContent(cmd.content),
        #        parent_comment_id=CommentId(cmd.parent_comment_id) if cmd.parent_comment_id else None
        #    )
        # 4. Save: comment_repo.save(comment)
        # 5. Publish: event_bus.publish(comment.clear_events())
        # 6. Return: comment.id
```

**Error cases:**
- PostNotFoundError → 404
- PostLockedError → 400
- MaxReplyDepthExceededError → 400
- CommentContentRequiredError → 400
- CommentContentTooLongError → 400

#### Handler 4: `edit_comment_handler.py`
```python
class EditCommentHandler:
    def __init__(self, comment_repo, member_repo, event_bus)

    async def handle(self, cmd: EditCommentCommand) -> None:
        # 1. Load comment: comment_repo.get_by_id(CommentId(cmd.comment_id))
        # 2. Load member: member_repo.get_by_user_and_community(...)
        # 3. Call: comment.edit(
        #        editor_id=UserId(cmd.editor_id),
        #        editor_role=member.role,
        #        content=CommentContent(cmd.content)
        #    )
        # 4. Save: comment_repo.save(comment)
        # 5. Publish: event_bus.publish(comment.clear_events())
```

**Error cases:**
- CommentNotFoundError → 404
- CannotEditCommentError → 403

#### Handler 5: `delete_comment_handler.py`
```python
class DeleteCommentHandler:
    def __init__(self, comment_repo, member_repo, event_bus)

    async def handle(self, cmd: DeleteCommentCommand) -> None:
        # 1. Load comment: comment_repo.get_by_id(CommentId(cmd.comment_id))
        # 2. Load member: member_repo.get_by_user_and_community(...)
        # 3. Check replies: has_replies = await comment_repo.has_replies(comment.id)
        # 4. Call: comment.delete(
        #        deleter_id=UserId(cmd.deleter_id),
        #        deleter_role=member.role,
        #        has_replies=has_replies
        #    )
        # 5. If has_replies: comment_repo.save(comment) (soft delete)
        #    Else: comment_repo.delete(comment.id) (hard delete)
        # 6. Publish: event_bus.publish(comment.clear_events())
```

**Error cases:**
- CommentNotFoundError → 404
- CannotDeleteCommentError → 403

#### Handler 6: `like_post_handler.py`
```python
class LikePostHandler:
    def __init__(self, reaction_repo, post_repo, event_bus)

    async def handle(self, cmd: LikePostCommand) -> None:
        # 1. Check if post exists: post_repo.get_by_id(PostId(cmd.post_id))
        # 2. Check if already liked: existing = await reaction_repo.find_by_user_and_target(
        #        user_id=UserId(cmd.user_id),
        #        target_type="post",
        #        target_id=cmd.post_id
        #    )
        # 3. If existing: return (idempotent - no error)
        # 4. Create: reaction = Reaction.create(
        #        user_id=UserId(cmd.user_id),
        #        target_type="post",
        #        target_id=PostId(cmd.post_id)
        #    )
        # 5. Save: reaction_repo.save(reaction)
        # 6. Publish: PostLiked event manually (Reaction is immutable, no events)
```

**Error cases:**
- PostNotFoundError → 404

#### Handler 7: `unlike_post_handler.py`
```python
class UnlikePostHandler:
    def __init__(self, reaction_repo, event_bus)

    async def handle(self, cmd: UnlikePostCommand) -> None:
        # 1. Find reaction: reaction = await reaction_repo.find_by_user_and_target(...)
        # 2. If not found: return (idempotent - no error)
        # 3. Delete: reaction_repo.delete(reaction.id)
        # 4. Publish: PostUnliked event manually
```

#### Handler 8: `like_comment_handler.py`
```python
class LikeCommentHandler:
    def __init__(self, reaction_repo, comment_repo, event_bus)

    async def handle(self, cmd: LikeCommentCommand) -> None:
        # Similar to like_post_handler, but target_type="comment"
```

**Error cases:**
- CommentNotFoundError → 404

#### Handler 9: `unlike_comment_handler.py`
```python
class UnlikeCommentHandler:
    def __init__(self, reaction_repo, event_bus)

    async def handle(self, cmd: UnlikeCommentCommand) -> None:
        # Similar to unlike_post_handler, but target_type="comment"
```

#### Handler 10: `get_post_comments_handler.py`
```python
class GetPostCommentsHandler:
    def __init__(self, comment_repo, reaction_repo)

    async def handle(self, query: GetPostCommentsQuery) -> list[CommentWithLikes]:
        # 1. Load comments: comments = await comment_repo.list_by_post(
        #        post_id=PostId(query.post_id),
        #        limit=query.limit,
        #        offset=query.offset
        #    )
        # 2. For each comment, get like count: reaction_repo.count_by_target("comment", comment.id.value)
        # 3. Return list of CommentWithLikes(comment, like_count)
```

**Return type:**
```python
@dataclass
class CommentWithLikes:
    comment: Comment
    like_count: int
```

#### Handler 11 (Modified): `delete_post_handler.py`
**Add cascade delete logic:**
```python
class DeletePostHandler:
    def __init__(
        self,
        post_repo,
        comment_repo,  # NEW
        reaction_repo,  # NEW
        member_repo,
        event_bus,
    )

    async def handle(self, cmd: DeletePostCommand) -> None:
        # ... existing logic ...

        # BEFORE post.delete():
        # 1. Delete all comments: await comment_repo.delete_by_post(post.id)
        # 2. Delete all reactions: await reaction_repo.delete_by_post_cascade(post.id)

        # ... rest of existing logic ...
```

**Update `__init__.py`:**
```python
# src/community/application/handlers/__init__.py
from .add_comment_handler import AddCommentHandler
from .delete_comment_handler import DeleteCommentHandler
from .edit_comment_handler import EditCommentHandler
from .get_post_comments_handler import GetPostCommentsHandler
from .like_comment_handler import LikeCommentHandler
from .like_post_handler import LikePostHandler
from .lock_post_handler import LockPostHandler
from .unlike_comment_handler import UnlikeCommentHandler
from .unlike_post_handler import UnlikePostHandler
from .unlock_post_handler import UnlockPostHandler

__all__ = [
    # ... existing handlers ...
    "AddCommentHandler",
    "DeleteCommentHandler",
    "EditCommentHandler",
    "GetPostCommentsHandler",
    "LikeCommentHandler",
    "LikePostHandler",
    "LockPostHandler",
    "UnlikeCommentHandler",
    "UnlikePostHandler",
    "UnlockPostHandler",
]
```

---

### Task 9: Infrastructure Repositories (2 new)

**Pattern to follow:** `src/community/infrastructure/persistence/post_repository.py`

#### Repository 1: `comment_repository.py`
```python
class SqlAlchemyCommentRepository(ICommentRepository):
    def __init__(self, session: AsyncSession):
        self._session = session
        self._logger = structlog.get_logger()

    async def save(self, comment: Comment) -> None:
        # Check if exists
        stmt = select(CommentModel).where(CommentModel.id == comment.id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            # Update
            model.content = str(comment.content)
            model.is_deleted = comment.is_deleted
            model.updated_at = comment.updated_at
            model.edited_at = comment.edited_at
        else:
            # Insert
            model = CommentModel(
                id=comment.id.value,
                post_id=comment.post_id.value,
                author_id=comment.author_id.value,
                parent_comment_id=comment.parent_comment_id.value if comment.parent_comment_id else None,
                content=str(comment.content),
                is_deleted=comment.is_deleted,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
                edited_at=comment.edited_at,
            )
            self._session.add(model)

        await self._session.flush()

    async def get_by_id(self, comment_id: CommentId) -> Comment | None:
        stmt = select(CommentModel).where(
            CommentModel.id == comment_id.value,
            CommentModel.is_deleted == False
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_post(
        self,
        post_id: PostId,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Comment]:
        stmt = (
            select(CommentModel)
            .where(
                CommentModel.post_id == post_id.value,
                CommentModel.is_deleted == False
            )
            .order_by(CommentModel.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def count_by_post(self, post_id: PostId) -> int:
        stmt = select(func.count(CommentModel.id)).where(
            CommentModel.post_id == post_id.value,
            CommentModel.is_deleted == False
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def has_replies(self, comment_id: CommentId) -> bool:
        stmt = select(func.count(CommentModel.id)).where(
            CommentModel.parent_comment_id == comment_id.value,
            CommentModel.is_deleted == False
        )
        result = await self._session.execute(stmt)
        count = result.scalar_one()
        return count > 0

    async def delete(self, comment_id: CommentId) -> None:
        stmt = delete(CommentModel).where(CommentModel.id == comment_id.value)
        await self._session.execute(stmt)
        await self._session.flush()

    async def delete_by_post(self, post_id: PostId) -> None:
        stmt = delete(CommentModel).where(CommentModel.post_id == post_id.value)
        await self._session.execute(stmt)
        await self._session.flush()

    def _to_entity(self, model: CommentModel) -> Comment:
        return Comment(
            id=CommentId(model.id),
            post_id=PostId(model.post_id),
            author_id=UserId(model.author_id) if model.author_id else UserId(UUID("00000000-0000-0000-0000-000000000000")),
            content=CommentContent(model.content),
            parent_comment_id=CommentId(model.parent_comment_id) if model.parent_comment_id else None,
            is_deleted=model.is_deleted,
            created_at=model.created_at,
            updated_at=model.updated_at,
            edited_at=model.edited_at,
        )
```

**Key imports:**
```python
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from uuid import UUID

from src.community.domain.entities import Comment
from src.community.domain.repositories import ICommentRepository
from src.community.domain.value_objects import CommentContent, CommentId, PostId
from src.identity.domain.value_objects import UserId
from src.community.infrastructure.persistence.models import CommentModel
```

#### Repository 2: `reaction_repository.py`
```python
class SqlAlchemyReactionRepository(IReactionRepository):
    def __init__(self, session: AsyncSession):
        self._session = session
        self._logger = structlog.get_logger()

    async def save(self, reaction: Reaction) -> None:
        model = ReactionModel(
            id=reaction.id.value,
            user_id=reaction.user_id.value,
            target_type=reaction.target_type,
            target_id=reaction.target_id,
            created_at=reaction.created_at,
        )
        self._session.add(model)
        await self._session.flush()

    async def find_by_user_and_target(
        self,
        user_id: UserId,
        target_type: str,
        target_id: UUID,
    ) -> Reaction | None:
        stmt = select(ReactionModel).where(
            ReactionModel.user_id == user_id.value,
            ReactionModel.target_type == target_type,
            ReactionModel.target_id == target_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def delete(self, reaction_id: ReactionId) -> None:
        stmt = delete(ReactionModel).where(ReactionModel.id == reaction_id.value)
        await self._session.execute(stmt)
        await self._session.flush()

    async def delete_by_target(self, target_type: str, target_id: UUID) -> None:
        stmt = delete(ReactionModel).where(
            ReactionModel.target_type == target_type,
            ReactionModel.target_id == target_id,
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def count_by_target(self, target_type: str, target_id: UUID) -> int:
        stmt = select(func.count(ReactionModel.id)).where(
            ReactionModel.target_type == target_type,
            ReactionModel.target_id == target_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def list_users_by_target(
        self,
        target_type: str,
        target_id: UUID,
        limit: int = 100,
    ) -> list[UserId]:
        stmt = (
            select(ReactionModel.user_id)
            .where(
                ReactionModel.target_type == target_type,
                ReactionModel.target_id == target_id,
            )
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        user_ids = result.scalars().all()
        return [UserId(uid) for uid in user_ids]

    async def count_by_user_since(self, user_id: UserId, since: datetime) -> int:
        stmt = select(func.count(ReactionModel.id)).where(
            ReactionModel.user_id == user_id.value,
            ReactionModel.created_at >= since,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def delete_by_post_cascade(self, post_id: PostId) -> None:
        # Delete reactions on the post itself
        stmt1 = delete(ReactionModel).where(
            ReactionModel.target_type == "post",
            ReactionModel.target_id == post_id.value,
        )
        await self._session.execute(stmt1)

        # Delete reactions on comments of the post
        # First, get all comment IDs for this post
        from src.community.infrastructure.persistence.models import CommentModel
        comment_ids_stmt = select(CommentModel.id).where(CommentModel.post_id == post_id.value)
        comment_ids_result = await self._session.execute(comment_ids_stmt)
        comment_ids = comment_ids_result.scalars().all()

        if comment_ids:
            stmt2 = delete(ReactionModel).where(
                ReactionModel.target_type == "comment",
                ReactionModel.target_id.in_(comment_ids),
            )
            await self._session.execute(stmt2)

        await self._session.flush()

    def _to_entity(self, model: ReactionModel) -> Reaction:
        return Reaction(
            id=ReactionId(model.id),
            user_id=UserId(model.user_id),
            target_type=model.target_type,
            target_id=model.target_id,
            created_at=model.created_at,
        )
```

**Key imports:**
```python
from datetime import datetime
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from uuid import UUID

from src.community.domain.entities import Reaction
from src.community.domain.repositories import IReactionRepository
from src.community.domain.value_objects import PostId, ReactionId
from src.identity.domain.value_objects import UserId
from src.community.infrastructure.persistence.models import ReactionModel
```

---

### Task 10: API Schemas & Dependencies

#### 10.1 Update `src/community/interface/api/schemas.py`

**Add new request schemas:**
```python
class AddCommentRequest(BaseModel):
    """Request to add a comment."""
    content: str = Field(..., min_length=1, max_length=2000)
    parent_comment_id: UUID | None = None

class EditCommentRequest(BaseModel):
    """Request to edit a comment."""
    content: str = Field(..., min_length=1, max_length=2000)
```

**Add new response schemas:**
```python
class CommentResponse(BaseModel):
    """Response for a comment."""
    id: UUID
    post_id: UUID
    author_id: UUID | None
    content: str
    parent_comment_id: UUID | None
    is_deleted: bool
    like_count: int = 0
    created_at: datetime
    updated_at: datetime
    edited_at: datetime | None
    is_edited: bool

    @staticmethod
    def from_entity(comment: Comment, like_count: int = 0) -> "CommentResponse":
        return CommentResponse(
            id=comment.id.value,
            post_id=comment.post_id.value,
            author_id=comment.author_id.value if comment.author_id else None,
            content=str(comment.content),
            parent_comment_id=comment.parent_comment_id.value if comment.parent_comment_id else None,
            is_deleted=comment.is_deleted,
            like_count=like_count,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            edited_at=comment.edited_at,
            is_edited=comment.is_edited,
        )

class CreateCommentResponse(BaseModel):
    """Response after creating a comment."""
    comment_id: UUID
    message: str = "Comment added successfully"

class LikeResponse(BaseModel):
    """Response for like/unlike operations."""
    message: str
```

**Update `PostResponse`:**
```python
class PostResponse(BaseModel):
    # ... existing fields ...
    comment_count: int = 0  # ADD THIS
    like_count: int = 0     # ADD THIS

    @staticmethod
    def from_entity(post: Post, comment_count: int = 0, like_count: int = 0) -> "PostResponse":
        return PostResponse(
            # ... existing fields ...
            comment_count=comment_count,  # ADD THIS
            like_count=like_count,        # ADD THIS
        )
```

#### 10.2 Update `src/community/interface/api/dependencies.py`

**Add repository factories:**
```python
def get_comment_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> ICommentRepository:
    """Get comment repository dependency."""
    from src.community.infrastructure.persistence.comment_repository import SqlAlchemyCommentRepository
    return SqlAlchemyCommentRepository(session)

def get_reaction_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> IReactionRepository:
    """Get reaction repository dependency."""
    from src.community.infrastructure.persistence.reaction_repository import SqlAlchemyReactionRepository
    return SqlAlchemyReactionRepository(session)
```

**Add handler factories:**
```python
def get_lock_post_handler(
    post_repo: Annotated[IPostRepository, Depends(get_post_repository)],
    member_repo: Annotated[IMemberRepository, Depends(get_member_repository)],
    event_bus: Annotated[IEventBus, Depends(get_event_bus)],
) -> LockPostHandler:
    from src.community.application.handlers import LockPostHandler
    return LockPostHandler(post_repo, member_repo, event_bus)

def get_unlock_post_handler(
    post_repo: Annotated[IPostRepository, Depends(get_post_repository)],
    member_repo: Annotated[IMemberRepository, Depends(get_member_repository)],
    event_bus: Annotated[IEventBus, Depends(get_event_bus)],
) -> UnlockPostHandler:
    from src.community.application.handlers import UnlockPostHandler
    return UnlockPostHandler(post_repo, member_repo, event_bus)

def get_add_comment_handler(
    comment_repo: Annotated[ICommentRepository, Depends(get_comment_repository)],
    post_repo: Annotated[IPostRepository, Depends(get_post_repository)],
    member_repo: Annotated[IMemberRepository, Depends(get_member_repository)],
    event_bus: Annotated[IEventBus, Depends(get_event_bus)],
) -> AddCommentHandler:
    from src.community.application.handlers import AddCommentHandler
    return AddCommentHandler(comment_repo, post_repo, member_repo, event_bus)

def get_edit_comment_handler(
    comment_repo: Annotated[ICommentRepository, Depends(get_comment_repository)],
    member_repo: Annotated[IMemberRepository, Depends(get_member_repository)],
    event_bus: Annotated[IEventBus, Depends(get_event_bus)],
) -> EditCommentHandler:
    from src.community.application.handlers import EditCommentHandler
    return EditCommentHandler(comment_repo, member_repo, event_bus)

def get_delete_comment_handler(
    comment_repo: Annotated[ICommentRepository, Depends(get_comment_repository)],
    member_repo: Annotated[IMemberRepository, Depends(get_member_repository)],
    event_bus: Annotated[IEventBus, Depends(get_event_bus)],
) -> DeleteCommentHandler:
    from src.community.application.handlers import DeleteCommentHandler
    return DeleteCommentHandler(comment_repo, member_repo, event_bus)

def get_like_post_handler(
    reaction_repo: Annotated[IReactionRepository, Depends(get_reaction_repository)],
    post_repo: Annotated[IPostRepository, Depends(get_post_repository)],
    event_bus: Annotated[IEventBus, Depends(get_event_bus)],
) -> LikePostHandler:
    from src.community.application.handlers import LikePostHandler
    return LikePostHandler(reaction_repo, post_repo, event_bus)

def get_unlike_post_handler(
    reaction_repo: Annotated[IReactionRepository, Depends(get_reaction_repository)],
    event_bus: Annotated[IEventBus, Depends(get_event_bus)],
) -> UnlikePostHandler:
    from src.community.application.handlers import UnlikePostHandler
    return UnlikePostHandler(reaction_repo, event_bus)

def get_like_comment_handler(
    reaction_repo: Annotated[IReactionRepository, Depends(get_reaction_repository)],
    comment_repo: Annotated[ICommentRepository, Depends(get_comment_repository)],
    event_bus: Annotated[IEventBus, Depends(get_event_bus)],
) -> LikeCommentHandler:
    from src.community.application.handlers import LikeCommentHandler
    return LikeCommentHandler(reaction_repo, comment_repo, event_bus)

def get_unlike_comment_handler(
    reaction_repo: Annotated[IReactionRepository, Depends(get_reaction_repository)],
    event_bus: Annotated[IEventBus, Depends(get_event_bus)],
) -> UnlikeCommentHandler:
    from src.community.application.handlers import UnlikeCommentHandler
    return UnlikeCommentHandler(reaction_repo, event_bus)

def get_get_post_comments_handler(
    comment_repo: Annotated[ICommentRepository, Depends(get_comment_repository)],
    reaction_repo: Annotated[IReactionRepository, Depends(get_reaction_repository)],
) -> GetPostCommentsHandler:
    from src.community.application.handlers import GetPostCommentsHandler
    return GetPostCommentsHandler(comment_repo, reaction_repo)
```

**Update `get_delete_post_handler`:**
```python
def get_delete_post_handler(
    post_repo: Annotated[IPostRepository, Depends(get_post_repository)],
    comment_repo: Annotated[ICommentRepository, Depends(get_comment_repository)],  # ADD
    reaction_repo: Annotated[IReactionRepository, Depends(get_reaction_repository)],  # ADD
    member_repo: Annotated[IMemberRepository, Depends(get_member_repository)],
    event_bus: Annotated[IEventBus, Depends(get_event_bus)],
) -> DeletePostHandler:
    from src.community.application.handlers import DeletePostHandler
    return DeletePostHandler(post_repo, comment_repo, reaction_repo, member_repo, event_bus)  # UPDATE
```

---

### Task 11: API Controllers

#### 11.1 Update `src/community/interface/api/post_controller.py`

**Add lock/unlock endpoints:**
```python
@router.post("/{post_id}/lock", status_code=status.HTTP_204_NO_CONTENT)
async def lock_post(
    post_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    handler: Annotated[LockPostHandler, Depends(get_lock_post_handler)],
) -> None:
    """Lock a post to prevent new comments."""
    try:
        command = LockPostCommand(post_id=post_id, locker_id=current_user.id.value)
        await handler.handle(command)
    except PostNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    except CannotLockPostError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.delete("/{post_id}/lock", status_code=status.HTTP_204_NO_CONTENT)
async def unlock_post(
    post_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    handler: Annotated[UnlockPostHandler, Depends(get_unlock_post_handler)],
) -> None:
    """Unlock a post to allow comments again."""
    try:
        command = UnlockPostCommand(post_id=post_id, unlocker_id=current_user.id.value)
        await handler.handle(command)
    except PostNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    except CannotLockPostError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
```

**Add like/unlike endpoints:**
```python
@router.post("/{post_id}/like", status_code=status.HTTP_200_OK)
async def like_post(
    post_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    handler: Annotated[LikePostHandler, Depends(get_like_post_handler)],
) -> LikeResponse:
    """Like a post."""
    try:
        command = LikePostCommand(post_id=post_id, user_id=current_user.id.value)
        await handler.handle(command)
        return LikeResponse(message="Post liked successfully")
    except PostNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@router.delete("/{post_id}/like", status_code=status.HTTP_200_OK)
async def unlike_post(
    post_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    handler: Annotated[UnlikePostHandler, Depends(get_unlike_post_handler)],
) -> LikeResponse:
    """Unlike a post."""
    command = UnlikePostCommand(post_id=post_id, user_id=current_user.id.value)
    await handler.handle(command)
    return LikeResponse(message="Post unliked successfully")
```

#### 11.2 Create `src/community/interface/api/comment_controller.py`

```python
"""Comment API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.community.application.commands import (
    AddCommentCommand,
    DeleteCommentCommand,
    EditCommentCommand,
    LikeCommentCommand,
    UnlikeCommentCommand,
)
from src.community.application.handlers import (
    AddCommentHandler,
    DeleteCommentHandler,
    EditCommentHandler,
    GetPostCommentsHandler,
    LikeCommentHandler,
    UnlikeCommentHandler,
)
from src.community.application.queries import GetPostCommentsQuery
from src.community.domain.exceptions import (
    CommentContentRequiredError,
    CommentContentTooLongError,
    CommentNotFoundError,
    CannotEditCommentError,
    CannotDeleteCommentError,
    MaxReplyDepthExceededError,
    PostLockedError,
    PostNotFoundError,
)
from src.community.interface.api.dependencies import (
    get_add_comment_handler,
    get_delete_comment_handler,
    get_edit_comment_handler,
    get_get_post_comments_handler,
    get_like_comment_handler,
    get_unlike_comment_handler,
)
from src.community.interface.api.schemas import (
    AddCommentRequest,
    CommentResponse,
    CreateCommentResponse,
    EditCommentRequest,
    LikeResponse,
)
from src.identity.domain.entities import User
from src.identity.interface.api.dependencies import get_current_user

# Router for /api/v1/posts/{post_id}/comments
post_comments_router = APIRouter()

# Router for /api/v1/comments/{comment_id}
comments_router = APIRouter()


@post_comments_router.post("/{post_id}/comments", status_code=status.HTTP_201_CREATED)
async def add_comment(
    post_id: UUID,
    request: AddCommentRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    handler: Annotated[AddCommentHandler, Depends(get_add_comment_handler)],
) -> CreateCommentResponse:
    """Add a comment to a post."""
    try:
        command = AddCommentCommand(
            post_id=post_id,
            author_id=current_user.id.value,
            content=request.content,
            parent_comment_id=request.parent_comment_id,
        )
        comment_id = await handler.handle(command)
        return CreateCommentResponse(comment_id=comment_id.value)
    except PostNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    except PostLockedError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except MaxReplyDepthExceededError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except (CommentContentRequiredError, CommentContentTooLongError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@post_comments_router.get("/{post_id}/comments", status_code=status.HTTP_200_OK)
async def get_post_comments(
    post_id: UUID,
    limit: int = 100,
    offset: int = 0,
    handler: Annotated[GetPostCommentsHandler, Depends(get_get_post_comments_handler)],
) -> list[CommentResponse]:
    """Get comments for a post."""
    query = GetPostCommentsQuery(post_id=post_id, limit=limit, offset=offset)
    comments_with_likes = await handler.handle(query)
    return [
        CommentResponse.from_entity(cwl.comment, cwl.like_count)
        for cwl in comments_with_likes
    ]


@comments_router.patch("/{comment_id}", status_code=status.HTTP_200_OK)
async def edit_comment(
    comment_id: UUID,
    request: EditCommentRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    handler: Annotated[EditCommentHandler, Depends(get_edit_comment_handler)],
) -> LikeResponse:
    """Edit a comment."""
    try:
        command = EditCommentCommand(
            comment_id=comment_id,
            editor_id=current_user.id.value,
            content=request.content,
        )
        await handler.handle(command)
        return LikeResponse(message="Comment edited successfully")
    except CommentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    except CannotEditCommentError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except (CommentContentRequiredError, CommentContentTooLongError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@comments_router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    handler: Annotated[DeleteCommentHandler, Depends(get_delete_comment_handler)],
) -> None:
    """Delete a comment."""
    try:
        command = DeleteCommentCommand(comment_id=comment_id, deleter_id=current_user.id.value)
        await handler.handle(command)
    except CommentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    except CannotDeleteCommentError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@comments_router.post("/{comment_id}/like", status_code=status.HTTP_200_OK)
async def like_comment(
    comment_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    handler: Annotated[LikeCommentHandler, Depends(get_like_comment_handler)],
) -> LikeResponse:
    """Like a comment."""
    try:
        command = LikeCommentCommand(comment_id=comment_id, user_id=current_user.id.value)
        await handler.handle(command)
        return LikeResponse(message="Comment liked successfully")
    except CommentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")


@comments_router.delete("/{comment_id}/like", status_code=status.HTTP_200_OK)
async def unlike_comment(
    comment_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    handler: Annotated[UnlikeCommentHandler, Depends(get_unlike_comment_handler)],
) -> LikeResponse:
    """Unlike a comment."""
    command = UnlikeCommentCommand(comment_id=comment_id, user_id=current_user.id.value)
    await handler.handle(command)
    return LikeResponse(message="Comment unliked successfully")
```

#### 11.3 Update `src/community/interface/api/__init__.py`

```python
from src.community.interface.api.comment_controller import (
    comments_router,
    post_comments_router,
)
from src.community.interface.api.post_controller import router as post_router

__all__ = [
    "post_router",
    "post_comments_router",
    "comments_router",
]
```

#### 11.4 Update `src/main.py`

```python
from src.community.interface.api import (
    comments_router,
    post_comments_router,
    post_router,
)

# ... in create_app() ...

# Register community routes
app.include_router(post_router, prefix="/api/v1/posts", tags=["posts"])
app.include_router(post_comments_router, prefix="/api/v1/posts", tags=["comments"])  # NEW
app.include_router(comments_router, prefix="/api/v1/comments", tags=["comments"])  # NEW
```

---

### Task 12: Unit Tests for Domain Layer

Create 4 test files with ~36 tests total.

#### Test 1: `tests/unit/community/domain/test_comment.py` (~15 tests)

```python
"""Unit tests for Comment entity."""

import pytest
from uuid import uuid4

from src.community.domain.entities import Comment
from src.community.domain.events import CommentAdded, CommentDeleted, CommentEdited
from src.community.domain.exceptions import (
    CannotDeleteCommentError,
    CannotEditCommentError,
)
from src.community.domain.value_objects import (
    CommentContent,
    CommentId,
    MemberRole,
    PostId,
)
from src.identity.domain.value_objects import UserId


class TestCommentCreate:
    def test_create_comment_success(self):
        # Arrange
        post_id = PostId(uuid4())
        author_id = UserId(uuid4())
        content = CommentContent("This is a comment")

        # Act
        comment = Comment.create(post_id, author_id, content)

        # Assert
        assert comment.post_id == post_id
        assert comment.author_id == author_id
        assert comment.content == content
        assert comment.parent_comment_id is None
        assert not comment.is_deleted
        assert len(comment.events) == 1
        assert isinstance(comment.events[0], CommentAdded)

    def test_create_reply_success(self):
        # Arrange
        post_id = PostId(uuid4())
        author_id = UserId(uuid4())
        content = CommentContent("This is a reply")
        parent_id = CommentId(uuid4())

        # Act
        comment = Comment.create(post_id, author_id, content, parent_id)

        # Assert
        assert comment.parent_comment_id == parent_id
        assert len(comment.events) == 1


class TestCommentEdit:
    def test_edit_own_comment_success(self):
        # Arrange
        comment = Comment.create(
            PostId(uuid4()),
            UserId(uuid4()),
            CommentContent("Original")
        )
        comment.clear_events()
        new_content = CommentContent("Edited")

        # Act
        comment.edit(comment.author_id, MemberRole.MEMBER, new_content)

        # Assert
        assert comment.content == new_content
        assert comment.is_edited
        assert len(comment.events) == 1
        assert isinstance(comment.events[0], CommentEdited)

    def test_edit_as_admin_success(self):
        # Arrange
        comment = Comment.create(
            PostId(uuid4()),
            UserId(uuid4()),
            CommentContent("Original")
        )
        comment.clear_events()
        admin_id = UserId(uuid4())
        new_content = CommentContent("Edited by admin")

        # Act
        comment.edit(admin_id, MemberRole.ADMIN, new_content)

        # Assert
        assert comment.content == new_content

    def test_edit_as_moderator_success(self):
        # Similar to admin test

    def test_edit_others_comment_as_member_fails(self):
        # Arrange
        comment = Comment.create(
            PostId(uuid4()),
            UserId(uuid4()),
            CommentContent("Original")
        )
        other_user_id = UserId(uuid4())
        new_content = CommentContent("Trying to edit")

        # Act & Assert
        with pytest.raises(CannotEditCommentError):
            comment.edit(other_user_id, MemberRole.MEMBER, new_content)

    def test_edit_no_change_no_event(self):
        # Arrange
        comment = Comment.create(
            PostId(uuid4()),
            UserId(uuid4()),
            CommentContent("Content")
        )
        comment.clear_events()

        # Act
        comment.edit(comment.author_id, MemberRole.MEMBER, comment.content)

        # Assert
        assert len(comment.events) == 0


class TestCommentDelete:
    def test_delete_own_comment_no_replies_hard_delete(self):
        # Arrange
        comment = Comment.create(
            PostId(uuid4()),
            UserId(uuid4()),
            CommentContent("To delete")
        )
        comment.clear_events()

        # Act
        comment.delete(comment.author_id, MemberRole.MEMBER, has_replies=False)

        # Assert
        assert comment.is_deleted
        assert len(comment.events) == 1
        assert isinstance(comment.events[0], CommentDeleted)

    def test_delete_own_comment_with_replies_soft_delete(self):
        # Arrange
        comment = Comment.create(
            PostId(uuid4()),
            UserId(uuid4()),
            CommentContent("To delete")
        )
        comment.clear_events()

        # Act
        comment.delete(comment.author_id, MemberRole.MEMBER, has_replies=True)

        # Assert
        assert comment.is_deleted
        assert str(comment.content) == "[deleted]"

    def test_delete_as_admin_success(self):
        # Similar pattern

    def test_delete_others_comment_as_member_fails(self):
        # Arrange
        comment = Comment.create(
            PostId(uuid4()),
            UserId(uuid4()),
            CommentContent("Original")
        )
        other_user_id = UserId(uuid4())

        # Act & Assert
        with pytest.raises(CannotDeleteCommentError):
            comment.delete(other_user_id, MemberRole.MEMBER, has_replies=False)


class TestCommentProperties:
    def test_is_edited_false_initially(self):
        comment = Comment.create(
            PostId(uuid4()),
            UserId(uuid4()),
            CommentContent("Content")
        )
        assert not comment.is_edited

    def test_is_edited_true_after_edit(self):
        comment = Comment.create(
            PostId(uuid4()),
            UserId(uuid4()),
            CommentContent("Content")
        )
        comment.edit(comment.author_id, MemberRole.MEMBER, CommentContent("New"))
        assert comment.is_edited


class TestCommentEquality:
    def test_comments_equal_same_id(self):
        comment_id = CommentId(uuid4())
        comment1 = Comment(
            id=comment_id,
            post_id=PostId(uuid4()),
            author_id=UserId(uuid4()),
            content=CommentContent("Test"),
        )
        comment2 = Comment(
            id=comment_id,
            post_id=PostId(uuid4()),
            author_id=UserId(uuid4()),
            content=CommentContent("Different"),
        )
        assert comment1 == comment2

    def test_comments_not_equal_different_id(self):
        comment1 = Comment.create(PostId(uuid4()), UserId(uuid4()), CommentContent("Test"))
        comment2 = Comment.create(PostId(uuid4()), UserId(uuid4()), CommentContent("Test"))
        assert comment1 != comment2
```

#### Test 2: `tests/unit/community/domain/test_reaction.py` (~4 tests)

```python
"""Unit tests for Reaction entity."""

from uuid import uuid4

from src.community.domain.entities import Reaction
from src.community.domain.value_objects import PostId, CommentId
from src.identity.domain.value_objects import UserId


class TestReactionCreate:
    def test_create_post_reaction_success(self):
        # Arrange
        user_id = UserId(uuid4())
        post_id = PostId(uuid4())

        # Act
        reaction = Reaction.create(user_id, "post", post_id)

        # Assert
        assert reaction.user_id == user_id
        assert reaction.target_type == "post"
        assert reaction.target_id == post_id.value
        assert reaction.id is not None

    def test_create_comment_reaction_success(self):
        # Arrange
        user_id = UserId(uuid4())
        comment_id = CommentId(uuid4())

        # Act
        reaction = Reaction.create(user_id, "comment", comment_id)

        # Assert
        assert reaction.target_type == "comment"
        assert reaction.target_id == comment_id.value


class TestReactionEquality:
    def test_reactions_equal_same_id(self):
        user_id = UserId(uuid4())
        post_id = PostId(uuid4())
        reaction1 = Reaction.create(user_id, "post", post_id)

        # Create another with same ID (hack for testing)
        from src.community.domain.value_objects import ReactionId
        from datetime import datetime, UTC
        reaction2 = Reaction(
            id=reaction1.id,
            user_id=UserId(uuid4()),
            target_type="post",
            target_id=uuid4(),
            created_at=datetime.now(UTC),
        )
        assert reaction1 == reaction2

    def test_reactions_not_equal_different_id(self):
        user_id = UserId(uuid4())
        post_id = PostId(uuid4())
        reaction1 = Reaction.create(user_id, "post", post_id)
        reaction2 = Reaction.create(user_id, "post", post_id)
        assert reaction1 != reaction2
```

#### Test 3: `tests/unit/community/domain/test_comment_content.py` (~10 tests)

```python
"""Unit tests for CommentContent value object."""

import pytest

from src.community.domain.exceptions import (
    CommentContentRequiredError,
    CommentContentTooLongError,
)
from src.community.domain.value_objects import CommentContent


class TestCommentContentValidation:
    def test_valid_content_success(self):
        content = CommentContent("This is a valid comment")
        assert str(content) == "This is a valid comment"

    def test_empty_content_fails(self):
        with pytest.raises(CommentContentRequiredError):
            CommentContent("")

    def test_whitespace_only_fails(self):
        with pytest.raises(CommentContentRequiredError):
            CommentContent("   ")

    def test_max_length_success(self):
        content = CommentContent("a" * 2000)
        assert len(str(content)) == 2000

    def test_exceeds_max_length_fails(self):
        with pytest.raises(CommentContentTooLongError):
            CommentContent("a" * 2001)


class TestCommentContentSanitization:
    def test_strips_html_tags(self):
        content = CommentContent("<script>alert('xss')</script>Hello")
        assert str(content) == "Hello"

    def test_strips_multiple_tags(self):
        content = CommentContent("<b>Bold</b> and <i>italic</i>")
        assert str(content) == "Bold and italic"

    def test_preserves_whitespace_between_words(self):
        content = CommentContent("Hello   world")
        assert "Hello" in str(content)
        assert "world" in str(content)

    def test_trims_leading_trailing_whitespace(self):
        content = CommentContent("  Hello world  ")
        assert str(content) == "Hello world"


class TestCommentContentImmutability:
    def test_content_is_frozen(self):
        content = CommentContent("Test")
        with pytest.raises(Exception):  # FrozenInstanceError
            content.value = "Changed"
```

#### Test 4: Update `tests/unit/community/domain/test_post.py` (~7 new tests)

Add these test classes:

```python
class TestPostLock:
    def test_lock_post_as_admin_success(self):
        # Arrange
        post = Post.create(...)
        post.clear_events()
        admin_id = UserId(uuid4())

        # Act
        post.lock(admin_id, MemberRole.ADMIN)

        # Assert
        assert post.is_locked
        assert len(post.events) == 1
        assert isinstance(post.events[0], PostLocked)

    def test_lock_post_as_moderator_success(self):
        # Similar to admin

    def test_lock_post_as_member_fails(self):
        post = Post.create(...)
        member_id = UserId(uuid4())

        with pytest.raises(CannotLockPostError):
            post.lock(member_id, MemberRole.MEMBER)

    def test_lock_already_locked_post_no_duplicate_event(self):
        post = Post.create(...)
        admin_id = UserId(uuid4())
        post.lock(admin_id, MemberRole.ADMIN)
        post.clear_events()

        post.lock(admin_id, MemberRole.ADMIN)

        assert len(post.events) == 0  # No duplicate event


class TestPostUnlock:
    def test_unlock_post_as_admin_success(self):
        post = Post.create(...)
        admin_id = UserId(uuid4())
        post.lock(admin_id, MemberRole.ADMIN)
        post.clear_events()

        post.unlock(admin_id, MemberRole.ADMIN)

        assert not post.is_locked
        assert len(post.events) == 1
        assert isinstance(post.events[0], PostUnlocked)

    def test_unlock_post_as_member_fails(self):
        post = Post.create(...)
        admin_id = UserId(uuid4())
        post.lock(admin_id, MemberRole.ADMIN)

        member_id = UserId(uuid4())
        with pytest.raises(CannotLockPostError):
            post.unlock(member_id, MemberRole.MEMBER)

    def test_unlock_already_unlocked_post_no_event(self):
        post = Post.create(...)
        admin_id = UserId(uuid4())
        post.clear_events()

        post.unlock(admin_id, MemberRole.ADMIN)

        assert len(post.events) == 0
```

---

### Task 13: BDD Step Definitions

**File:** `tests/features/community/test_feed.py`

**Task:** Remove `@pytest.mark.skip` from 25 Phase 2 scenarios and implement HTTP calls.

**Key patterns:**

```python
# Lock post
@when('I lock the post')
async def lock_post(context):
    post_id = context.response.json()["post_id"]
    response = await context.client.post(
        f"/api/v1/posts/{post_id}/lock",
        headers={"Authorization": f"Bearer {context.access_token}"}
    )
    context.response = response

# Add comment
@when('I add a comment with content "{content}"')
async def add_comment(context, content: str):
    post_id = context.response.json()["post_id"]
    response = await context.client.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"content": content},
        headers={"Authorization": f"Bearer {context.access_token}"}
    )
    context.response = response
    if response.status_code == 201:
        context.comment_id = response.json()["comment_id"]

# Like post
@when('I like the post')
async def like_post(context):
    post_id = context.response.json()["post_id"]
    response = await context.client.post(
        f"/api/v1/posts/{post_id}/like",
        headers={"Authorization": f"Bearer {context.access_token}"}
    )
    context.response = response

# Edit comment
@when('I edit the comment to "{new_content}"')
async def edit_comment(context, new_content: str):
    response = await context.client.patch(
        f"/api/v1/comments/{context.comment_id}",
        json={"content": new_content},
        headers={"Authorization": f"Bearer {context.access_token}"}
    )
    context.response = response

# Delete comment
@when('I delete the comment')
async def delete_comment(context):
    response = await context.client.delete(
        f"/api/v1/comments/{context.comment_id}",
        headers={"Authorization": f"Bearer {context.access_token}"}
    )
    context.response = response

# Assertions
@then('the post should be locked')
async def post_is_locked(context):
    post_id = context.response.json()["post_id"]
    response = await context.client.get(
        f"/api/v1/posts/{post_id}",
        headers={"Authorization": f"Bearer {context.access_token}"}
    )
    assert response.json()["is_locked"] is True

@then('the comment should be visible')
async def comment_visible(context):
    post_id = context.response.json()["post_id"]
    response = await context.client.get(
        f"/api/v1/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {context.access_token}"}
    )
    comments = response.json()
    assert len(comments) > 0
    assert context.comment_id in [c["id"] for c in comments]
```

**Update phase markers:**
- Lines marked "Phase 2" in skip reasons → keep enabled
- Lines marked "Phase 3" or "Phase 4" in skip reasons → update to correct phase number per new doc

---

### Task 14: Verification

**Run in order:**

```bash
# 1. Run migrations
alembic upgrade head

# 2. Test BDD scenarios
pytest tests/features/community/test_feed.py -v --tb=short
# Expected: 45 passed, 25 skipped, 0 failed, 0 warnings

# 3. Test unit tests
pytest tests/unit/community/ -v
# Expected: All passing, 0 failed

# 4. Full verification
./scripts/verify.sh
# Expected: 0 failed, 0 warnings, coverage ≥80%

# 5. Verify skip markers
grep -r "@pytest.mark.skip" tests/features/community/ | grep "Phase [0-9]"
# Expected: All Phase 3+ scenarios, no Phase 2
```

**Definition of Done:**
- ✅ 45 BDD scenarios passing (20 Phase 1 + 25 Phase 2)
- ✅ 25 scenarios skipped with Phase 3+ markers
- ✅ All unit tests passing (~36 new + existing)
- ✅ Coverage ≥ 80%
- ✅ 0 failed, 0 warnings
- ✅ All handlers, repositories, controllers working
- ✅ Migrations applied successfully

---

## Implementation Order

**Recommended sequence:**

1. **Handlers first** (Task 7) - Core business logic
2. **Repositories** (Task 9) - Data access
3. **API layer** (Tasks 10, 11) - Expose functionality
4. **Run migrations** (Part of Task 14) - Setup database
5. **Manual API testing** - Verify endpoints work
6. **Unit tests** (Task 12) - Test domain logic
7. **BDD tests** (Task 13) - Integration tests
8. **Final verification** (Task 14) - All checks green

---

## Rate Limiting Notes

For BDD scenarios requiring rate limiting (comment spam, excessive liking):
- Implement using slowapi decorators
- Follow pattern from `src/identity/infrastructure/services/rate_limiter.py`
- Constants: `COMMENT_LIMIT = "50/hour"`, `LIKE_LIMIT = "200/hour"`
- Apply to endpoints: POST /posts/{id}/comments, POST /posts/{id}/like, POST /comments/{id}/like

---

## Common Pitfalls to Avoid

1. **Don't bypass domain logic** - Always use Comment.create(), not direct model creation
2. **Remember event publishing** - All handlers must publish events via event_bus
3. **Check `has_replies` before delete** - Comment deletion logic depends on this
4. **Idempotent reactions** - Like handlers should no-op if already liked
5. **Cascade deletes** - DeletePostHandler must delete comments + reactions
6. **Update test phase markers** - Old "Phase 2" comments/reactions → now Phase 2, old "Phase 3" feed → now Phase 3
7. **Null author_id handling** - When user deleted, author_id can be None (use placeholder UUID or handle gracefully)

---

## Contact Points with Existing Code

**Modified files:**
- `src/community/domain/entities/post.py` - Added lock/unlock methods
- `src/community/application/handlers/delete_post_handler.py` - Added cascade logic
- `src/community/infrastructure/persistence/models.py` - Added relationships
- `src/community/interface/api/dependencies.py` - Updated delete_post_handler factory
- `src/community/interface/api/schemas.py` - Updated PostResponse
- `src/main.py` - Registered new routers
- `tests/unit/community/domain/test_post.py` - Added lock/unlock tests

**New modules (no conflicts):**
- Everything in Task 7-13 is net new code

---

## Success Metrics

**Phase 2 is complete when:**
- ✅ 45 BDD scenarios pass (breakdown: 4 locking + 12 comments + 8 reactions + 1 cascade = 25 new)
- ✅ Users can: lock posts, add/edit/delete comments, like posts/comments
- ✅ Soft delete works (comments with replies show "[deleted]")
- ✅ Threading works (comment → reply, no nested)
- ✅ Rate limiting prevents spam
- ✅ CI green with 0 warnings

---

**End of Implementation Guide**

Use this document as reference while implementing remaining tasks. Each section provides exact patterns, imports, and logic to follow for consistency with existing codebase.
