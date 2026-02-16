"""Unit tests for Comment entity."""

from uuid import uuid4

import pytest

from src.community.domain.entities.comment import Comment
from src.community.domain.events import CommentAdded, CommentDeleted, CommentEdited
from src.community.domain.exceptions import (
    CannotDeleteCommentError,
    CannotEditCommentError,
)
from src.community.domain.value_objects import (
    CommentContent,
    CommentId,
    CommunityId,
    MemberRole,
    PostId,
)
from src.identity.domain.value_objects import UserId


@pytest.fixture
def post_id() -> PostId:
    """Create a test post ID."""
    return PostId(value=uuid4())


@pytest.fixture
def author_id() -> UserId:
    """Create a test author ID."""
    return UserId(value=uuid4())


@pytest.fixture
def content() -> CommentContent:
    """Create a test comment content."""
    return CommentContent("This is a test comment.")


@pytest.fixture
def community_id() -> CommunityId:
    """Create a test community ID."""
    return CommunityId(value=uuid4())


@pytest.fixture
def comment(
    post_id: PostId, author_id: UserId, content: CommentContent, community_id: CommunityId
) -> Comment:
    """Create a test comment."""
    return Comment.create(
        post_id=post_id,
        author_id=author_id,
        content=content,
        community_id=community_id,
    )


class TestCommentCreate:
    """Tests for Comment.create() factory method."""

    def test_create_comment_with_required_fields(
        self, post_id: PostId, author_id: UserId, content: CommentContent, community_id: CommunityId
    ) -> None:
        """Comment.create() should create a comment with all required fields."""
        comment = Comment.create(
            post_id=post_id,
            author_id=author_id,
            content=content,
            community_id=community_id,
        )

        assert isinstance(comment.id, CommentId)
        assert comment.post_id == post_id
        assert comment.author_id == author_id
        assert comment.content == content
        assert comment.parent_comment_id is None
        assert comment.is_deleted is False
        assert comment.created_at is not None
        assert comment.updated_at is not None
        assert comment.edited_at is None

    def test_create_reply_comment(
        self, post_id: PostId, author_id: UserId, content: CommentContent, community_id: CommunityId
    ) -> None:
        """Comment.create() with parent_comment_id should create a reply."""
        parent_id = CommentId(value=uuid4())

        reply = Comment.create(
            post_id=post_id,
            author_id=author_id,
            content=content,
            community_id=community_id,
            parent_comment_id=parent_id,
        )

        assert reply.parent_comment_id == parent_id

    def test_create_comment_publishes_comment_added_event(
        self, post_id: PostId, author_id: UserId, content: CommentContent, community_id: CommunityId
    ) -> None:
        """Comment.create() should publish CommentAdded event."""
        comment = Comment.create(
            post_id=post_id,
            author_id=author_id,
            content=content,
            community_id=community_id,
        )

        events = comment.events
        assert len(events) == 1
        assert isinstance(events[0], CommentAdded)
        assert events[0].comment_id == comment.id
        assert events[0].post_id == post_id
        assert events[0].author_id == author_id
        assert events[0].content == str(content)
        assert events[0].parent_comment_id is None

    def test_create_reply_event_includes_parent_id(
        self, post_id: PostId, author_id: UserId, content: CommentContent, community_id: CommunityId
    ) -> None:
        """CommentAdded event for a reply should include parent_comment_id."""
        parent_id = CommentId(value=uuid4())

        reply = Comment.create(
            post_id=post_id,
            author_id=author_id,
            content=content,
            community_id=community_id,
            parent_comment_id=parent_id,
        )

        events = reply.events
        event = events[0]
        assert isinstance(event, CommentAdded)
        assert event.parent_comment_id == parent_id


class TestCommentEdit:
    """Tests for Comment.edit() method."""

    def test_edit_comment_by_author_updates_content(
        self, comment: Comment, author_id: UserId
    ) -> None:
        """Comment.edit() by author should update content."""
        new_content = CommentContent("Updated comment content.")

        comment.edit(
            editor_id=author_id,
            editor_role=MemberRole.MEMBER,
            content=new_content,
        )

        assert comment.content == new_content
        assert comment.edited_at is not None

    def test_edit_comment_publishes_comment_edited_event(
        self, comment: Comment, author_id: UserId
    ) -> None:
        """Comment.edit() should publish CommentEdited event."""
        comment.clear_events()
        new_content = CommentContent("Edited content.")

        comment.edit(
            editor_id=author_id,
            editor_role=MemberRole.MEMBER,
            content=new_content,
        )

        events = comment.events
        assert len(events) == 1
        assert isinstance(events[0], CommentEdited)
        assert events[0].comment_id == comment.id
        assert events[0].editor_id == author_id

    def test_edit_comment_with_same_content_does_not_publish_event(
        self, comment: Comment, author_id: UserId, content: CommentContent
    ) -> None:
        """Comment.edit() with same content should not publish event."""
        comment.clear_events()

        comment.edit(
            editor_id=author_id,
            editor_role=MemberRole.MEMBER,
            content=content,
        )

        assert len(comment.events) == 0
        assert comment.edited_at is None

    def test_edit_comment_by_non_author_member_raises_error(self, comment: Comment) -> None:
        """Comment.edit() by non-author MEMBER should raise CannotEditCommentError."""
        other_user = UserId(value=uuid4())

        with pytest.raises(CannotEditCommentError):
            comment.edit(
                editor_id=other_user,
                editor_role=MemberRole.MEMBER,
                content=CommentContent("Trying to edit."),
            )

    def test_edit_comment_by_moderator_succeeds(self, comment: Comment) -> None:
        """Comment.edit() by moderator should succeed even if not author."""
        moderator_id = UserId(value=uuid4())
        new_content = CommentContent("Moderator edit.")

        comment.edit(
            editor_id=moderator_id,
            editor_role=MemberRole.MODERATOR,
            content=new_content,
        )

        assert comment.content == new_content

    def test_edit_comment_by_admin_succeeds(self, comment: Comment) -> None:
        """Comment.edit() by admin should succeed even if not author."""
        admin_id = UserId(value=uuid4())
        new_content = CommentContent("Admin edit.")

        comment.edit(
            editor_id=admin_id,
            editor_role=MemberRole.ADMIN,
            content=new_content,
        )

        assert comment.content == new_content


class TestCommentDelete:
    """Tests for Comment.delete() method."""

    def test_delete_comment_without_replies_marks_for_hard_delete(
        self, comment: Comment, author_id: UserId
    ) -> None:
        """Comment.delete() without replies should mark is_deleted=True."""
        comment.delete(
            deleter_id=author_id,
            deleter_role=MemberRole.MEMBER,
            has_replies=False,
        )

        assert comment.is_deleted is True

    def test_delete_comment_with_replies_soft_deletes(
        self, comment: Comment, author_id: UserId
    ) -> None:
        """Comment.delete() with replies should soft delete (content becomes '[deleted]')."""
        comment.delete(
            deleter_id=author_id,
            deleter_role=MemberRole.MEMBER,
            has_replies=True,
        )

        assert comment.is_deleted is True
        assert str(comment.content) == "[deleted]"

    def test_delete_comment_publishes_comment_deleted_event(
        self, comment: Comment, author_id: UserId
    ) -> None:
        """Comment.delete() should publish CommentDeleted event."""
        comment.clear_events()

        comment.delete(
            deleter_id=author_id,
            deleter_role=MemberRole.MEMBER,
            has_replies=False,
        )

        events = comment.events
        assert len(events) == 1
        assert isinstance(events[0], CommentDeleted)
        assert events[0].comment_id == comment.id
        assert events[0].deleted_by == author_id

    def test_delete_comment_by_non_author_member_raises_error(self, comment: Comment) -> None:
        """Comment.delete() by non-author MEMBER should raise CannotDeleteCommentError."""
        other_user = UserId(value=uuid4())

        with pytest.raises(CannotDeleteCommentError):
            comment.delete(
                deleter_id=other_user,
                deleter_role=MemberRole.MEMBER,
                has_replies=False,
            )

    def test_delete_comment_by_moderator_succeeds(self, comment: Comment) -> None:
        """Comment.delete() by moderator should succeed even if not author."""
        moderator_id = UserId(value=uuid4())

        comment.delete(
            deleter_id=moderator_id,
            deleter_role=MemberRole.MODERATOR,
            has_replies=False,
        )

        assert comment.is_deleted is True

    def test_delete_comment_by_admin_succeeds(self, comment: Comment) -> None:
        """Comment.delete() by admin should succeed even if not author."""
        admin_id = UserId(value=uuid4())

        comment.delete(
            deleter_id=admin_id,
            deleter_role=MemberRole.ADMIN,
            has_replies=False,
        )

        assert comment.is_deleted is True


class TestCommentIsEdited:
    """Tests for Comment.is_edited property."""

    def test_is_edited_returns_false_initially(self, comment: Comment) -> None:
        """Comment.is_edited should return False for newly created comment."""
        assert comment.is_edited is False

    def test_is_edited_returns_true_after_edit(self, comment: Comment, author_id: UserId) -> None:
        """Comment.is_edited should return True after comment has been edited."""
        comment.edit(
            editor_id=author_id,
            editor_role=MemberRole.MEMBER,
            content=CommentContent("Edited content."),
        )

        assert comment.is_edited is True


class TestCommentEventManagement:
    """Tests for comment event management methods."""

    def test_clear_events_returns_and_clears_events(self, comment: Comment) -> None:
        """clear_events() should return events and empty the list."""
        assert len(comment.events) == 1

        cleared = comment.clear_events()

        assert len(cleared) == 1
        assert isinstance(cleared[0], CommentAdded)
        assert len(comment.events) == 0

    def test_events_property_returns_copy(self, comment: Comment) -> None:
        """events property should return a copy, not the original list."""
        events = comment.events
        events.clear()
        assert len(comment.events) == 1


class TestCommentEquality:
    """Tests for Comment equality and hashing."""

    def test_comments_with_same_id_are_equal(self, post_id: PostId, author_id: UserId) -> None:
        """Two comments with the same ID should be equal."""
        comment_id = CommentId(value=uuid4())

        comment1 = Comment(
            id=comment_id,
            post_id=post_id,
            author_id=author_id,
            content=CommentContent("Content 1"),
        )

        comment2 = Comment(
            id=comment_id,
            post_id=post_id,
            author_id=author_id,
            content=CommentContent("Content 2"),
        )

        assert comment1 == comment2

    def test_comments_with_different_ids_are_not_equal(
        self, comment: Comment, post_id: PostId, author_id: UserId, content: CommentContent
    ) -> None:
        """Two comments with different IDs should not be equal."""
        other = Comment.create(
            post_id=post_id, author_id=author_id, content=content, community_id=CommunityId(uuid4())
        )
        assert comment != other

    def test_comment_can_be_used_in_set(self, comment: Comment) -> None:
        """Comments should be hashable and usable in sets."""
        comment_set = {comment}
        assert comment in comment_set

    def test_comment_hash_is_consistent(self, comment: Comment) -> None:
        """Comment hash should be consistent across calls."""
        assert hash(comment) == hash(comment)
