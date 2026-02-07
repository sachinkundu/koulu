"""Unit tests for Reaction entity."""

from uuid import uuid4

import pytest

from src.community.domain.entities.reaction import Reaction
from src.community.domain.value_objects import CommentId, PostId, ReactionId
from src.identity.domain.value_objects import UserId


@pytest.fixture
def user_id() -> UserId:
    """Create a test user ID."""
    return UserId(value=uuid4())


@pytest.fixture
def post_id() -> PostId:
    """Create a test post ID."""
    return PostId(value=uuid4())


@pytest.fixture
def comment_id() -> CommentId:
    """Create a test comment ID."""
    return CommentId(value=uuid4())


class TestReactionCreate:
    """Tests for Reaction.create() factory method."""

    def test_create_post_reaction(self, user_id: UserId, post_id: PostId) -> None:
        """Reaction.create() should create a post reaction."""
        reaction = Reaction.create(
            user_id=user_id,
            target_type="post",
            target_id=post_id,
        )

        assert isinstance(reaction.id, ReactionId)
        assert reaction.user_id == user_id
        assert reaction.target_type == "post"
        assert reaction.target_id == post_id.value
        assert reaction.created_at is not None

    def test_create_comment_reaction(self, user_id: UserId, comment_id: CommentId) -> None:
        """Reaction.create() should create a comment reaction."""
        reaction = Reaction.create(
            user_id=user_id,
            target_type="comment",
            target_id=comment_id,
        )

        assert reaction.target_type == "comment"
        assert reaction.target_id == comment_id.value

    def test_reaction_is_immutable(self, user_id: UserId, post_id: PostId) -> None:
        """Reaction should be immutable (frozen=True)."""
        reaction = Reaction.create(
            user_id=user_id,
            target_type="post",
            target_id=post_id,
        )

        with pytest.raises(AttributeError):
            reaction.target_type = "comment"  # type: ignore[misc]


class TestReactionEquality:
    """Tests for Reaction equality and hashing."""

    def test_reactions_with_same_id_are_equal(self, user_id: UserId, post_id: PostId) -> None:
        """Two reactions with the same ID should be equal."""
        reaction_id = ReactionId(value=uuid4())
        from datetime import UTC, datetime

        r1 = Reaction(
            id=reaction_id,
            user_id=user_id,
            target_type="post",
            target_id=post_id.value,
            created_at=datetime.now(UTC),
        )
        r2 = Reaction(
            id=reaction_id,
            user_id=user_id,
            target_type="post",
            target_id=post_id.value,
            created_at=datetime.now(UTC),
        )

        assert r1 == r2

    def test_reactions_with_different_ids_are_not_equal(
        self, user_id: UserId, post_id: PostId
    ) -> None:
        """Two reactions with different IDs should not be equal."""
        r1 = Reaction.create(user_id=user_id, target_type="post", target_id=post_id)
        r2 = Reaction.create(user_id=user_id, target_type="post", target_id=post_id)

        assert r1 != r2

    def test_reaction_can_be_used_in_set(self, user_id: UserId, post_id: PostId) -> None:
        """Reactions should be hashable and usable in sets."""
        reaction = Reaction.create(user_id=user_id, target_type="post", target_id=post_id)
        reaction_set = {reaction}
        assert reaction in reaction_set

    def test_reaction_hash_is_consistent(self, user_id: UserId, post_id: PostId) -> None:
        """Reaction hash should be consistent across calls."""
        reaction = Reaction.create(user_id=user_id, target_type="post", target_id=post_id)
        assert hash(reaction) == hash(reaction)
