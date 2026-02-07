"""Unit tests for Post entity."""

from uuid import uuid4

import pytest

from src.community.domain.entities.post import Post
from src.community.domain.events import PostCreated, PostDeleted, PostEdited
from src.community.domain.exceptions import (
    InvalidImageUrlError,
    NotPostAuthorError,
    PostAlreadyDeletedError,
)
from src.community.domain.value_objects import (
    CategoryId,
    CommunityId,
    MemberRole,
    PostContent,
    PostId,
    PostTitle,
)
from src.identity.domain.value_objects import UserId


@pytest.fixture
def community_id() -> CommunityId:
    """Create a test community ID."""
    return CommunityId(value=uuid4())


@pytest.fixture
def author_id() -> UserId:
    """Create a test author ID."""
    return UserId(value=uuid4())


@pytest.fixture
def category_id() -> CategoryId:
    """Create a test category ID."""
    return CategoryId(value=uuid4())


@pytest.fixture
def title() -> PostTitle:
    """Create a test post title."""
    return PostTitle("My First Post")


@pytest.fixture
def content() -> PostContent:
    """Create a test post content."""
    return PostContent("This is the content of my first post.")


@pytest.fixture
def post(
    community_id: CommunityId,
    author_id: UserId,
    category_id: CategoryId,
    title: PostTitle,
    content: PostContent,
) -> Post:
    """Create a test post."""
    return Post.create(
        community_id=community_id,
        author_id=author_id,
        category_id=category_id,
        title=title,
        content=content,
    )


class TestPostCreate:
    """Tests for Post.create() factory method."""

    def test_create_post_with_all_required_fields(
        self,
        community_id: CommunityId,
        author_id: UserId,
        category_id: CategoryId,
        title: PostTitle,
        content: PostContent,
    ) -> None:
        """Post.create() should create a post with all required fields."""
        post = Post.create(
            community_id=community_id,
            author_id=author_id,
            category_id=category_id,
            title=title,
            content=content,
        )

        assert isinstance(post.id, PostId)
        assert post.community_id == community_id
        assert post.author_id == author_id
        assert post.category_id == category_id
        assert post.title == title
        assert post.content == content
        assert post.image_url is None
        assert post.is_pinned is False
        assert post.is_locked is False
        assert post.is_deleted is False
        assert post.created_at is not None
        assert post.updated_at is not None
        assert post.edited_at is None

    def test_create_post_with_valid_https_image_url(
        self,
        community_id: CommunityId,
        author_id: UserId,
        category_id: CategoryId,
        title: PostTitle,
        content: PostContent,
    ) -> None:
        """Post.create() should accept valid HTTPS image URL."""
        image_url = "https://example.com/image.png"

        post = Post.create(
            community_id=community_id,
            author_id=author_id,
            category_id=category_id,
            title=title,
            content=content,
            image_url=image_url,
        )

        assert post.image_url == image_url

    def test_create_post_with_invalid_http_image_url_raises_error(
        self,
        community_id: CommunityId,
        author_id: UserId,
        category_id: CategoryId,
        title: PostTitle,
        content: PostContent,
    ) -> None:
        """Post.create() with HTTP (not HTTPS) image URL should raise InvalidImageUrlError."""
        image_url = "http://example.com/image.png"

        with pytest.raises(InvalidImageUrlError):
            Post.create(
                community_id=community_id,
                author_id=author_id,
                category_id=category_id,
                title=title,
                content=content,
                image_url=image_url,
            )

    def test_create_post_with_invalid_protocol_image_url_raises_error(
        self,
        community_id: CommunityId,
        author_id: UserId,
        category_id: CategoryId,
        title: PostTitle,
        content: PostContent,
    ) -> None:
        """Post.create() with non-HTTPS protocol should raise InvalidImageUrlError."""
        image_url = "ftp://example.com/image.png"

        with pytest.raises(InvalidImageUrlError):
            Post.create(
                community_id=community_id,
                author_id=author_id,
                category_id=category_id,
                title=title,
                content=content,
                image_url=image_url,
            )

    def test_create_post_publishes_post_created_event(
        self,
        community_id: CommunityId,
        author_id: UserId,
        category_id: CategoryId,
        title: PostTitle,
        content: PostContent,
    ) -> None:
        """Post.create() should publish PostCreated event."""
        post = Post.create(
            community_id=community_id,
            author_id=author_id,
            category_id=category_id,
            title=title,
            content=content,
        )

        events = post.events
        assert len(events) == 1
        assert isinstance(events[0], PostCreated)
        assert events[0].post_id == post.id
        assert events[0].community_id == community_id
        assert events[0].author_id == author_id
        assert events[0].category_id == category_id
        assert events[0].title == str(title)
        assert events[0].content == str(content)
        assert events[0].image_url is None

    def test_create_post_with_image_includes_image_in_event(
        self,
        community_id: CommunityId,
        author_id: UserId,
        category_id: CategoryId,
        title: PostTitle,
        content: PostContent,
    ) -> None:
        """Post.create() with image should include image_url in PostCreated event."""
        image_url = "https://example.com/image.png"

        post = Post.create(
            community_id=community_id,
            author_id=author_id,
            category_id=category_id,
            title=title,
            content=content,
            image_url=image_url,
        )

        events = post.events
        assert len(events) == 1
        assert isinstance(events[0], PostCreated)
        assert events[0].image_url == image_url


class TestPostEdit:
    """Tests for Post.edit() method."""

    def test_edit_post_by_author_updates_title(self, post: Post, author_id: UserId) -> None:
        """Post.edit() by author should update title and return changed fields."""
        new_title = PostTitle("Updated Title")

        changed = post.edit(
            editor_id=author_id,
            editor_role=MemberRole.MEMBER,
            title=new_title,
        )

        assert post.title == new_title
        assert changed == ["title"]
        assert post.edited_at is not None

    def test_edit_post_by_author_updates_content(self, post: Post, author_id: UserId) -> None:
        """Post.edit() by author should update content and return changed fields."""
        new_content = PostContent("Updated content goes here.")

        changed = post.edit(
            editor_id=author_id,
            editor_role=MemberRole.MEMBER,
            content=new_content,
        )

        assert post.content == new_content
        assert changed == ["content"]
        assert post.edited_at is not None

    def test_edit_post_by_author_updates_image_url(self, post: Post, author_id: UserId) -> None:
        """Post.edit() by author should update image_url and return changed fields."""
        new_image_url = "https://example.com/new-image.png"

        changed = post.edit(
            editor_id=author_id,
            editor_role=MemberRole.MEMBER,
            image_url=new_image_url,
        )

        assert post.image_url == new_image_url
        assert changed == ["image_url"]
        assert post.edited_at is not None

    def test_edit_post_by_author_updates_category(self, post: Post, author_id: UserId) -> None:
        """Post.edit() by author should update category and return changed fields."""
        new_category_id = CategoryId(value=uuid4())

        changed = post.edit(
            editor_id=author_id,
            editor_role=MemberRole.MEMBER,
            category_id=new_category_id,
        )

        assert post.category_id == new_category_id
        assert changed == ["category_id"]
        assert post.edited_at is not None

    def test_edit_post_updates_multiple_fields(self, post: Post, author_id: UserId) -> None:
        """Post.edit() should update multiple fields and return all changed fields."""
        new_title = PostTitle("New Title")
        new_content = PostContent("New content.")

        changed = post.edit(
            editor_id=author_id,
            editor_role=MemberRole.MEMBER,
            title=new_title,
            content=new_content,
        )

        assert post.title == new_title
        assert post.content == new_content
        assert set(changed) == {"title", "content"}

    def test_edit_post_with_empty_string_image_removes_image(
        self, post: Post, author_id: UserId
    ) -> None:
        """Post.edit() with empty string image_url should remove the image."""
        # First set an image
        post.edit(
            editor_id=author_id,
            editor_role=MemberRole.MEMBER,
            image_url="https://example.com/image.png",
        )
        assert post.image_url is not None

        # Now remove it with empty string
        changed = post.edit(
            editor_id=author_id,
            editor_role=MemberRole.MEMBER,
            image_url="",
        )

        assert post.image_url is None
        assert changed == ["image_url"]

    def test_edit_post_with_same_values_returns_empty_list(
        self, post: Post, author_id: UserId
    ) -> None:
        """Post.edit() with same values should not update and return empty list."""
        original_title = post.title
        original_edited_at = post.edited_at

        changed = post.edit(
            editor_id=author_id,
            editor_role=MemberRole.MEMBER,
            title=original_title,
        )

        assert changed == []
        assert post.edited_at == original_edited_at  # Should not update timestamp

    def test_edit_post_by_non_author_without_permission_raises_error(self, post: Post) -> None:
        """Post.edit() by non-author with MEMBER role should raise NotPostAuthorError."""
        other_user_id = UserId(value=uuid4())

        with pytest.raises(NotPostAuthorError):
            post.edit(
                editor_id=other_user_id,
                editor_role=MemberRole.MEMBER,
                title=PostTitle("Trying to edit"),
            )

    def test_edit_post_by_moderator_succeeds(self, post: Post) -> None:
        """Post.edit() by moderator should succeed even if not author."""
        moderator_id = UserId(value=uuid4())
        new_title = PostTitle("Moderator Edit")

        changed = post.edit(
            editor_id=moderator_id,
            editor_role=MemberRole.MODERATOR,
            title=new_title,
        )

        assert post.title == new_title
        assert changed == ["title"]

    def test_edit_post_by_admin_succeeds(self, post: Post) -> None:
        """Post.edit() by admin should succeed even if not author."""
        admin_id = UserId(value=uuid4())
        new_title = PostTitle("Admin Edit")

        changed = post.edit(
            editor_id=admin_id,
            editor_role=MemberRole.ADMIN,
            title=new_title,
        )

        assert post.title == new_title
        assert changed == ["title"]

    def test_edit_deleted_post_raises_error(self, post: Post, author_id: UserId) -> None:
        """Post.edit() on deleted post should raise PostAlreadyDeletedError."""
        post.delete(deleter_id=author_id)

        with pytest.raises(PostAlreadyDeletedError):
            post.edit(
                editor_id=author_id,
                editor_role=MemberRole.MEMBER,
                title=PostTitle("Cannot edit deleted"),
            )

    def test_edit_post_with_non_https_image_raises_error(
        self, post: Post, author_id: UserId
    ) -> None:
        """Post.edit() with non-HTTPS image URL should raise InvalidImageUrlError."""
        with pytest.raises(InvalidImageUrlError):
            post.edit(
                editor_id=author_id,
                editor_role=MemberRole.MEMBER,
                image_url="http://example.com/image.png",
            )

    def test_edit_post_publishes_post_edited_event(self, post: Post, author_id: UserId) -> None:
        """Post.edit() should publish PostEdited event."""
        post.clear_events()  # Clear creation event

        new_title = PostTitle("Edited Title")
        changed = post.edit(
            editor_id=author_id,
            editor_role=MemberRole.MEMBER,
            title=new_title,
        )

        events = post.events
        assert len(events) == 1
        assert isinstance(events[0], PostEdited)
        assert events[0].post_id == post.id
        assert events[0].editor_id == author_id
        assert events[0].changed_fields == changed

    def test_edit_post_with_no_changes_does_not_publish_event(
        self, post: Post, author_id: UserId
    ) -> None:
        """Post.edit() with no actual changes should not publish event."""
        post.clear_events()

        original_title = post.title
        post.edit(
            editor_id=author_id,
            editor_role=MemberRole.MEMBER,
            title=original_title,  # Same as current
        )

        events = post.events
        assert len(events) == 0  # No event published


class TestPostDelete:
    """Tests for Post.delete() method."""

    def test_delete_post_marks_as_deleted(self, post: Post, author_id: UserId) -> None:
        """Post.delete() should set is_deleted to True."""
        assert post.is_deleted is False

        post.delete(deleter_id=author_id)

        assert post.is_deleted is True

    def test_delete_post_updates_timestamp(self, post: Post, author_id: UserId) -> None:
        """Post.delete() should update the updated_at timestamp."""
        original_updated_at = post.updated_at

        post.delete(deleter_id=author_id)

        assert post.updated_at > original_updated_at

    def test_delete_already_deleted_post_raises_error(self, post: Post, author_id: UserId) -> None:
        """Post.delete() on already deleted post should raise PostAlreadyDeletedError."""
        post.delete(deleter_id=author_id)  # First delete succeeds

        with pytest.raises(PostAlreadyDeletedError):
            post.delete(deleter_id=author_id)  # Second delete fails

    def test_delete_post_publishes_post_deleted_event(self, post: Post, author_id: UserId) -> None:
        """Post.delete() should publish PostDeleted event."""
        post.clear_events()  # Clear creation event

        post.delete(deleter_id=author_id)

        events = post.events
        assert len(events) == 1
        assert isinstance(events[0], PostDeleted)
        assert events[0].post_id == post.id
        assert events[0].deleted_by == author_id


class TestPostIsEdited:
    """Tests for Post.is_edited property."""

    def test_is_edited_returns_false_initially(self, post: Post) -> None:
        """Post.is_edited should return False for newly created post."""
        assert post.is_edited is False

    def test_is_edited_returns_true_after_edit(self, post: Post, author_id: UserId) -> None:
        """Post.is_edited should return True after post has been edited."""
        post.edit(
            editor_id=author_id,
            editor_role=MemberRole.MEMBER,
            title=PostTitle("Edited"),
        )

        assert post.is_edited is True


class TestPostEventManagement:
    """Tests for post event management methods."""

    def test_clear_events_returns_and_clears_events(self, post: Post) -> None:
        """clear_events() should return events and empty the list."""
        assert len(post.events) == 1  # PostCreated from creation

        cleared = post.clear_events()

        assert len(cleared) == 1
        assert isinstance(cleared[0], PostCreated)
        assert len(post.events) == 0

    def test_events_property_returns_copy(self, post: Post) -> None:
        """events property should return a copy, not the original list."""
        events = post.events

        events.clear()  # Modify the returned list

        assert len(post.events) == 1  # Original unchanged


class TestPostEquality:
    """Tests for Post equality and hashing."""

    def test_posts_with_same_id_are_equal(
        self,
        community_id: CommunityId,
        author_id: UserId,
        category_id: CategoryId,
    ) -> None:
        """Two posts with the same ID should be equal."""
        post_id = PostId(value=uuid4())

        post1 = Post(
            id=post_id,
            community_id=community_id,
            author_id=author_id,
            category_id=category_id,
            title=PostTitle("Post 1"),
            content=PostContent("Content 1"),
        )

        post2 = Post(
            id=post_id,
            community_id=community_id,
            author_id=author_id,
            category_id=category_id,
            title=PostTitle("Post 2"),  # Different title
            content=PostContent("Content 2"),  # Different content
        )

        assert post1 == post2

    def test_posts_with_different_ids_are_not_equal(self, post: Post) -> None:
        """Two posts with different IDs should not be equal."""
        other_post = Post.create(
            community_id=post.community_id,
            author_id=post.author_id,
            category_id=post.category_id,
            title=post.title,
            content=post.content,
        )

        assert post != other_post

    def test_post_can_be_used_in_set(self, post: Post) -> None:
        """Posts should be hashable and usable in sets."""
        post_set = {post}

        assert post in post_set
        assert len(post_set) == 1

    def test_post_can_be_used_as_dict_key(self, post: Post) -> None:
        """Posts should be hashable and usable as dict keys."""
        post_dict = {post: "metadata"}

        assert post_dict[post] == "metadata"

    def test_post_hash_is_consistent(self, post: Post) -> None:
        """Post hash should be consistent across calls."""
        hash1 = hash(post)
        hash2 = hash(post)

        assert hash1 == hash2
