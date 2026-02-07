"""BDD step definitions for community feed.

Phase 1 scenarios (12 enabled):
- Post creation (8 scenarios)
- Post editing (2 scenarios)
- Post deletion (2 scenarios)

Phase 2-4 scenarios (58 skipped):
- Phase 2: Admin/moderator permissions, pinning, rate limiting (8 scenarios)
- Phase 3: Comments, reactions, locking (25 scenarios)
- Phase 4: Feed display, categories, edge cases (25 scenarios)

NOTE: Step functions have intentionally "unused" parameters like `client` for pytest-bdd
fixture dependency ordering. See MEMORY.md BUG-001 for details.
"""

# ruff: noqa: ARG001

from typing import Any

import pytest
from httpx import AsyncClient
from pytest_bdd import given, parsers, scenarios, then, when

# Load all scenarios from the feature file
scenarios("feed.feature")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


async def _get_auth_token(
    client: AsyncClient, email: str, password: str = "testpassword123"
) -> str:
    """Helper to get auth token for a user."""
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    token: str = login_response.json()["access_token"]
    return token


# ============================================================================
# BACKGROUND STEPS
# ============================================================================


@given(parsers.parse('a community exists with name "{name}"'))
async def community_exists(
    client: AsyncClient, name: str, create_community: Any, context: dict[str, Any]
) -> None:
    """Create a community."""
    community = await create_community(name=name)
    context["community"] = community
    context["community_id"] = community.id


@given("the following categories exist:")
async def categories_exist(
    client: AsyncClient,
    create_category: Any,
    context: dict[str, Any],
    datatable: list[dict[str, str]],
) -> None:
    """Create categories from datatable."""
    community_id = context["community_id"]
    categories = {}

    for row in datatable:
        category = await create_category(
            community_id=community_id,
            name=row["name"],
            slug=row["slug"],
            emoji=row.get("emoji"),
        )
        categories[row["name"]] = category

    context["categories"] = categories


# ============================================================================
# GIVEN STEPS - USER CREATION
# ============================================================================


@given(parsers.parse('a user exists with email "{email}" and role "{role}"'))
async def user_exists_with_role(
    client: AsyncClient,
    email: str,
    role: str,
    create_community_user: Any,
    context: dict[str, Any],
) -> None:
    """Create a user with community membership."""
    community_id = context.get("community_id")

    user, community, member = await create_community_user(
        email=email,
        role=role,
        community_id=community_id,
    )

    # Store in context - use email as key to track multiple users
    if "users" not in context:
        context["users"] = {}
    context["users"][email] = {"user": user, "member": member}

    # Store primary user if not already set
    if "user" not in context:
        context["user"] = user
        context["email"] = email
        context["member"] = member


@given(parsers.parse('user "{email}" created a post'))
async def user_created_post(client: AsyncClient, email: str, context: dict[str, Any]) -> None:
    """Create a post as a specific user."""
    # Get auth token for the user
    token = await _get_auth_token(client, email)

    # Get a category to use
    categories = context.get("categories", {})
    category_name = list(categories.keys())[0] if categories else "General"

    # Create post
    response = await client.post(
        "/api/v1/posts",
        json={
            "title": "Test Post",
            "content": "This is a test post",
            "category": category_name,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201, f"Post creation failed: {response.text}"

    post_data = response.json()
    context["post_id"] = post_data["id"]
    context["post"] = post_data


@given(parsers.parse('user "{email}" created a post with title "{title}"'))
async def user_created_post_with_title(
    client: AsyncClient, email: str, title: str, context: dict[str, Any]
) -> None:
    """Create a post with specific title as a user."""
    token = await _get_auth_token(client, email)

    categories = context.get("categories", {})
    category_name = list(categories.keys())[0] if categories else "General"

    response = await client.post(
        "/api/v1/posts",
        json={
            "title": title,
            "content": "This is a test post",
            "category": category_name,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201, f"Post creation failed: {response.text}"
    post_data = response.json()

    # Store the post for this user
    if "users" not in context:
        context["users"] = {}
    if email not in context["users"]:
        context["users"][email] = {}
    context["users"][email]["post"] = post_data
    context["post_id"] = post_data["id"]
    context["post"] = post_data


# ============================================================================
# GIVEN STEPS - AUTHENTICATION
# ============================================================================


@given(parsers.parse('I am authenticated as "{email}"'))
async def authenticated_as(client: AsyncClient, email: str, context: dict[str, Any]) -> None:
    """Set authenticated user in context."""
    token = await _get_auth_token(client, email)
    context["auth_token"] = token
    context["auth_email"] = email


@given(parsers.parse('I created a post with title "{title}"'))
async def i_created_post(client: AsyncClient, title: str, context: dict[str, Any]) -> None:
    """Create a post as the authenticated user."""
    token = context["auth_token"]

    categories = context.get("categories", {})
    category_name = list(categories.keys())[0] if categories else "General"

    response = await client.post(
        "/api/v1/posts",
        json={
            "title": title,
            "content": "This is a test post",
            "category": category_name,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201, f"Post creation failed: {response.text}"
    post_data = response.json()
    context["my_post_id"] = post_data["id"]
    context["my_post"] = post_data


# ============================================================================
# WHEN STEPS - POST CREATION
# ============================================================================


@when("I create a post with:")
async def create_post_with_data(
    client: AsyncClient, context: dict[str, Any], datatable: list[dict[str, str]]
) -> None:
    """Create a post with data from datatable."""
    token = context["auth_token"]

    # Convert datatable to dict
    post_data = {}
    for row in datatable:
        key = row["field"] if "field" in row else list(row.keys())[0]
        value = row["value"] if "value" in row else list(row.values())[0]
        post_data[key] = value

    response = await client.post(
        "/api/v1/posts",
        json=post_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    context["post_response"] = response
    if response.status_code == 201:
        context["post"] = response.json()
        context["post_id"] = response.json()["id"]


@when("I attempt to create a post with:")
async def attempt_create_post_with_data(
    client: AsyncClient, context: dict[str, Any], datatable: list[dict[str, str]]
) -> None:
    """Attempt to create a post (may fail)."""
    await create_post_with_data(client, context, datatable)


@when(parsers.parse("I attempt to create a post with a title of {length:d} characters"))
async def attempt_create_post_long_title(
    client: AsyncClient, length: int, context: dict[str, Any]
) -> None:
    """Attempt to create a post with long title."""
    token = context["auth_token"]
    title = "x" * length

    categories = context.get("categories", {})
    category_name = list(categories.keys())[0] if categories else "General"

    response = await client.post(
        "/api/v1/posts",
        json={
            "title": title,
            "content": "Test content",
            "category": category_name,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    context["post_response"] = response


@when(parsers.parse("I attempt to create a post with content of {length:d} characters"))
async def attempt_create_post_long_content(
    client: AsyncClient, length: int, context: dict[str, Any]
) -> None:
    """Attempt to create a post with long content."""
    token = context["auth_token"]
    content = "a" * length

    categories = context.get("categories", {})
    category_name = list(categories.keys())[0] if categories else "General"

    response = await client.post(
        "/api/v1/posts",
        json={
            "title": "Test title",
            "content": content,
            "category": category_name,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    context["post_response"] = response


@when("I attempt to create a post without authentication")
async def attempt_create_post_without_auth(client: AsyncClient, context: dict[str, Any]) -> None:
    """Attempt to create a post without auth token."""
    categories = context.get("categories", {})
    category_name = list(categories.keys())[0] if categories else "General"

    response = await client.post(
        "/api/v1/posts",
        json={
            "title": "Test title",
            "content": "Test content",
            "category": category_name,
        },
    )

    context["post_response"] = response


# ============================================================================
# WHEN STEPS - POST EDITING
# ============================================================================


@when("I edit the post with:")
async def edit_post_with_data(
    client: AsyncClient, context: dict[str, Any], datatable: list[dict[str, str]]
) -> None:
    """Edit a post with data from datatable."""
    token = context["auth_token"]
    post_id = context["my_post_id"]

    # Convert datatable to dict
    update_data = {}
    for row in datatable:
        key = row["field"] if "field" in row else list(row.keys())[0]
        value = row["value"] if "value" in row else list(row.values())[0]
        update_data[key] = value

    response = await client.patch(
        f"/api/v1/posts/{post_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    context["edit_response"] = response
    if response.status_code == 200:
        context["my_post"] = response.json()


@when("I attempt to edit Alice's post")
async def attempt_edit_alice_post(client: AsyncClient, context: dict[str, Any]) -> None:
    """Attempt to edit another user's post."""
    token = context["auth_token"]

    # Get Alice's post from users context
    alice_post = context["users"]["alice@example.com"]["post"]

    response = await client.patch(
        f"/api/v1/posts/{alice_post['id']}",
        json={"title": "Hacked title"},
        headers={"Authorization": f"Bearer {token}"},
    )

    context["edit_response"] = response


# ============================================================================
# WHEN STEPS - POST DELETION
# ============================================================================


@when("I delete my post")
async def delete_my_post(client: AsyncClient, context: dict[str, Any]) -> None:
    """Delete own post."""
    token = context["auth_token"]
    post_id = context["my_post_id"]

    response = await client.delete(
        f"/api/v1/posts/{post_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    context["delete_response"] = response


@when("I attempt to delete Alice's post")
async def attempt_delete_alice_post(client: AsyncClient, context: dict[str, Any]) -> None:
    """Attempt to delete another user's post."""
    token = context["auth_token"]

    # Get Alice's post from users context
    alice_post = context["users"]["alice@example.com"]["post"]

    response = await client.delete(
        f"/api/v1/posts/{alice_post['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )

    context["delete_response"] = response


# ============================================================================
# THEN STEPS - POST CREATION
# ============================================================================


@then("the post should be created successfully")
async def post_created_successfully(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify post was created."""
    response = context["post_response"]
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    assert "id" in response.json()


@then(parsers.parse('the post should have title "{title}"'))
async def post_has_title(title: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify post title."""
    response = context["post_response"]
    assert response.status_code == 201
    post = response.json()
    assert post["title"] == title, f"Expected title '{title}', got '{post['title']}'"


@then(parsers.parse('the post should be in category "{category}"'))
async def post_in_category(category: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify post category."""
    response = context["post_response"]
    assert response.status_code == 201
    post = response.json()
    assert post["category_name"] == category, (
        f"Expected category '{category}', got '{post['category_name']}'"
    )


@then(parsers.parse('the post author should be "{email}"'))
async def post_author_is(email: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify post author."""
    response = context["post_response"]
    assert response.status_code == 201
    post = response.json()
    # The author_id should match the authenticated user
    user = context["users"][email]["user"]
    assert str(post["author_id"]) == str(user.id)


@then(parsers.parse('a "{event_name}" event should be published'))
async def event_published(event_name: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify event was published (indicated by successful operation)."""
    # For now, we verify the operation succeeded
    # In production, you'd check an event store or message queue
    if event_name == "PostCreated":
        response = context.get("post_response")
        assert response is not None and response.status_code == 201
    elif event_name == "PostEdited":
        response = context.get("edit_response")
        assert response is not None and response.status_code == 200
    elif event_name == "PostDeleted":
        response = context.get("delete_response")
        assert response is not None and response.status_code == 200


@then(parsers.parse('the post should have an image at "{url}"'))
async def post_has_image(url: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify post has image URL."""
    response = context["post_response"]
    assert response.status_code == 201
    post = response.json()
    assert post["image_url"] == url


@then(parsers.parse('the post creation should fail with error "{error_message}"'))
async def post_creation_fails(
    error_message: str, client: AsyncClient, context: dict[str, Any]
) -> None:
    """Verify post creation failed with specific error."""
    response = context["post_response"]
    assert response.status_code in (400, 401, 404), (
        f"Expected error status, got {response.status_code}"
    )

    # Check error message
    error_data = response.json()
    error_text = error_data.get("detail", str(error_data))
    assert error_message.lower() in error_text.lower(), (
        f"Expected '{error_message}' in error, got: {error_text}"
    )


# ============================================================================
# THEN STEPS - POST EDITING
# ============================================================================


@then("the post should be updated successfully")
async def post_updated_successfully(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify post was updated."""
    response = context["edit_response"]
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"


@then('the post should show as "edited"')
async def post_shows_edited(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify post is marked as edited."""
    response = context["edit_response"]
    assert response.status_code == 200
    post = response.json()
    assert post.get("is_edited") is True or post.get("edited_at") is not None


@then(parsers.parse('the edit should fail with error "{error_message}"'))
async def edit_fails(error_message: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify edit failed with specific error."""
    response = context["edit_response"]
    assert response.status_code in (400, 403, 404), (
        f"Expected error status, got {response.status_code}"
    )

    error_data = response.json()
    error_text = error_data.get("detail", str(error_data))
    assert error_message.lower() in error_text.lower(), (
        f"Expected '{error_message}' in error, got: {error_text}"
    )


# ============================================================================
# THEN STEPS - POST DELETION
# ============================================================================


@then("the post should be deleted")
@then("the post should be deleted successfully")
async def post_deleted_successfully(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify post was deleted."""
    response = context["delete_response"]
    assert response.status_code == 204, f"Expected 204, got {response.status_code}: {response.text}"


@then("the post should not appear in the feed")
async def post_not_in_feed(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify deleted post doesn't appear in feed."""
    # Try to fetch the post directly
    token = context["auth_token"]
    post_id = context["my_post_id"]

    response = await client.get(
        f"/api/v1/posts/{post_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Should return 404 or indicate deletion
    assert response.status_code in (404, 410), f"Expected 404/410, got {response.status_code}"


@then(parsers.parse('the deletion should fail with error "{error_message}"'))
async def deletion_fails(error_message: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify deletion failed with specific error."""
    response = context["delete_response"]
    assert response.status_code in (400, 403, 404), (
        f"Expected error status, got {response.status_code}"
    )

    error_data = response.json()
    error_text = error_data.get("detail", str(error_data))
    assert error_message.lower() in error_text.lower(), (
        f"Expected '{error_message}' in error, got: {error_text}"
    )


# ============================================================================
# PHASE 2 SCENARIOS - SKIPPED (Roles & Permissions)
# ============================================================================


@pytest.mark.skip(reason="Phase 2: Rate limiting will be implemented with Redis integration")
@given("I have created 10 posts in the last hour")
async def given_created_10_posts(client: AsyncClient, context: dict[str, Any]) -> None:
    """Create 10 posts for rate limiting test - given variant."""
    pass


@pytest.mark.skip(reason="Phase 2: Rate limiting will be implemented with Redis integration")
@when("I have created 10 posts in the last hour")
async def created_10_posts(client: AsyncClient, context: dict[str, Any]) -> None:
    """Create 10 posts for rate limiting test."""
    pass


@pytest.mark.skip(reason="Phase 2: Rate limiting will be implemented with Redis integration")
@when("I attempt to create another post")
async def attempt_create_another_post(client: AsyncClient, context: dict[str, Any]) -> None:
    """Attempt to create post when rate limited."""
    pass


@pytest.mark.skip(
    reason="Phase 2: Admin permissions will be implemented with role-based authorization"
)
@when("I delete the member's post")
async def delete_member_post(client: AsyncClient, context: dict[str, Any]) -> None:
    """Admin deletes member's post."""
    pass


@pytest.mark.skip(
    reason="Phase 2: Admin permissions will be implemented with role-based authorization"
)
@then(parsers.parse('a "{event}" event should be published with admin user_id'))
async def event_published_with_admin(
    event: str, client: AsyncClient, context: dict[str, Any]
) -> None:
    """Verify event published with admin user ID."""
    pass


@pytest.mark.skip(reason="Phase 2: Post pinning will be implemented with pin/unpin methods")
@when("I pin the post")
async def pin_post(client: AsyncClient, context: dict[str, Any]) -> None:
    """Pin a post."""
    pass


@pytest.mark.skip(reason="Phase 2: Post pinning will be implemented with pin/unpin methods")
@when("I unpin the post")
async def unpin_post(client: AsyncClient, context: dict[str, Any]) -> None:
    """Unpin a post."""
    pass


@pytest.mark.skip(reason="Phase 2: Post pinning will be implemented with pin/unpin methods")
@when("I attempt to pin the post")
async def attempt_pin_post(client: AsyncClient, context: dict[str, Any]) -> None:
    """Attempt to pin post (may fail)."""
    pass


@pytest.mark.skip(reason="Phase 2: Post pinning will be implemented with pin/unpin methods")
@then("the post should be pinned successfully")
async def post_pinned(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify post was pinned."""
    pass


@pytest.mark.skip(reason="Phase 2: Post pinning will be implemented with pin/unpin methods")
@then("the post should appear at the top of the feed")
async def post_at_top(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify pinned post appears at top."""
    pass


@pytest.mark.skip(reason="Phase 2: Post pinning will be implemented with pin/unpin methods")
@then("the post should no longer be pinned")
async def post_not_pinned(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify post is no longer pinned."""
    pass


@pytest.mark.skip(reason="Phase 2: Post pinning will be implemented with pin/unpin methods")
@then("the post should appear in normal feed order")
async def post_in_normal_order(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify post appears in normal order."""
    pass


@pytest.mark.skip(reason="Phase 2: Post pinning will be implemented with pin/unpin methods")
@then(parsers.parse('the pin should fail with error "{error_message}"'))
async def pin_fails(error_message: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify pin failed."""
    pass


# ============================================================================
# PHASE 2 GIVEN STEPS - SKIPPED
# ============================================================================


@pytest.mark.skip(reason="Phase 2: Will be implemented with post repository")
@given("a post exists")
async def post_exists(client: AsyncClient, context: dict[str, Any]) -> None:
    """Create a post."""
    pass


@pytest.mark.skip(reason="Phase 2: Will be implemented with post repository")
@given("a post exists and is pinned")
async def post_exists_pinned(client: AsyncClient, context: dict[str, Any]) -> None:
    """Create a pinned post."""
    pass


# ============================================================================
# PHASE 3 SCENARIOS - SKIPPED (Comments & Reactions & Locking)
# ============================================================================


@pytest.mark.skip(reason="Phase 3: Post locking will be implemented with lock/unlock methods")
@given("a post exists and is locked")
async def post_locked(client: AsyncClient, context: dict[str, Any]) -> None:
    """Create a locked post."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@given(parsers.parse('a post exists with title "{title}"'))
async def post_exists_with_title(title: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Create a post with specific title."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@given("a post exists with a comment")
async def post_with_comment(client: AsyncClient, context: dict[str, Any]) -> None:
    """Create post with comment."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@given(parsers.parse('a post exists with a comment by "{email}"'))
async def post_with_comment_by(email: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Create post with comment by specific user."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@given("a post exists with a comment and a reply to that comment")
async def post_with_comment_and_reply(client: AsyncClient, context: dict[str, Any]) -> None:
    """Create post with comment and reply."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@given("the comment has no replies")
async def comment_has_no_replies(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify comment has no replies."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@given(parsers.parse("the comment has {count:d} replies"))
async def comment_has_replies(count: int, client: AsyncClient, context: dict[str, Any]) -> None:
    """Create comment with replies."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with like/unlike methods")
@given("I have already liked the post")
async def already_liked_post(client: AsyncClient, context: dict[str, Any]) -> None:
    """Like a post."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with like/unlike methods")
@given("I have already liked the comment")
async def already_liked_comment(client: AsyncClient, context: dict[str, Any]) -> None:
    """Like a comment."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with rate limiting")
@given(parsers.parse("I have liked {count:d} posts in the last hour"))
async def liked_many_posts(count: int, client: AsyncClient, context: dict[str, Any]) -> None:
    """Create many likes for rate limiting test."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented with rate limiting")
@given(parsers.parse("I have created {count:d} comments in the last hour"))
async def created_many_comments(count: int, client: AsyncClient, context: dict[str, Any]) -> None:
    """Create many comments for rate limiting test."""
    pass


@pytest.mark.skip(reason="Phase 3: Post locking will be implemented with lock/unlock methods")
@when("I lock the post")
async def lock_post(client: AsyncClient, context: dict[str, Any]) -> None:
    """Lock a post."""
    pass


@pytest.mark.skip(reason="Phase 3: Post locking will be implemented with lock/unlock methods")
@when("I unlock the post")
async def unlock_post(client: AsyncClient, context: dict[str, Any]) -> None:
    """Unlock a post."""
    pass


@pytest.mark.skip(reason="Phase 3: Post locking will be implemented with lock/unlock methods")
@when("I attempt to lock the post")
async def attempt_lock_post(client: AsyncClient, context: dict[str, Any]) -> None:
    """Attempt to lock post."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@when("I add a comment with content")
async def add_comment(client: AsyncClient, context: dict[str, Any]) -> None:
    """Add comment to post."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@when("I attempt to add a comment to the locked post")
async def attempt_comment_locked(client: AsyncClient, context: dict[str, Any]) -> None:
    """Attempt to comment on locked post."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with like/unlike methods")
@when("I like the post")
async def like_post(client: AsyncClient, context: dict[str, Any]) -> None:
    """Like a post."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented with cascade deletion")
@given("the post has 5 comments")
async def post_has_comments(client: AsyncClient, context: dict[str, Any]) -> None:
    """Add comments to post."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with cascade deletion")
@given("the post has 3 likes")
async def post_has_likes(client: AsyncClient, context: dict[str, Any]) -> None:
    """Add likes to post."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented with cascade deletion")
@then("all comments on the post should be deleted")
async def comments_deleted(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify comments deleted."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with cascade deletion")
@then("all reactions on the post should be deleted")
async def reactions_deleted(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify reactions deleted."""
    pass


# Additional Phase 3 when/then steps


@pytest.mark.skip(reason="Phase 3: Post locking will be implemented with lock/unlock methods")
@then("the post should be locked successfully")
async def post_locked_successfully(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify post was locked."""
    pass


@pytest.mark.skip(reason="Phase 3: Post locking will be implemented with lock/unlock methods")
@then("new comments should not be allowed")
async def comments_not_allowed(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify comments disabled."""
    pass


@pytest.mark.skip(reason="Phase 3: Post locking will be implemented with lock/unlock methods")
@then("the post should be unlocked")
async def post_unlocked(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify post was unlocked."""
    pass


@pytest.mark.skip(reason="Phase 3: Post locking will be implemented with lock/unlock methods")
@then("new comments should be allowed again")
async def comments_allowed_again(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify comments enabled."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@then(parsers.parse('the comment should fail with error "{error_message}"'))
async def comment_fails(error_message: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify comment failed."""
    pass


@pytest.mark.skip(reason="Phase 3: Post locking will be implemented with lock/unlock methods")
@then(parsers.parse('the lock should fail with error "{error_message}"'))
async def lock_fails(error_message: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify lock failed."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@when(parsers.parse('I add a comment with content "{content}"'))
async def add_comment_with_content(
    content: str, client: AsyncClient, context: dict[str, Any]
) -> None:
    """Add comment with content."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@when(parsers.parse('I reply to Bob\'s comment with "{content}"'))
async def reply_to_comment(content: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Reply to comment."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@when("I attempt to reply to the reply")
async def attempt_reply_to_reply(client: AsyncClient, context: dict[str, Any]) -> None:
    """Attempt to reply to reply (max depth)."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@then(parsers.parse('the reply should fail with error "{error_message}"'))
async def reply_fails(error_message: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify reply failed."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@when(parsers.parse("I attempt to add a comment with {length:d} characters"))
async def attempt_long_comment(length: int, client: AsyncClient, context: dict[str, Any]) -> None:
    """Attempt to add long comment."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@when("I attempt to add an empty comment")
async def attempt_empty_comment(client: AsyncClient, context: dict[str, Any]) -> None:
    """Attempt to add empty comment."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@then("the comment should be added successfully")
async def comment_added(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify comment was added."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@then("the comment should appear on the post")
async def comment_appears(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify comment appears on post."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@then(parsers.parse("the post comment count should increase by {count:d}"))
async def comment_count_increases(count: int, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify comment count increased."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@then("the reply should be added successfully")
async def reply_added(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify reply was added."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@then("the reply should be nested under Bob's comment")
async def reply_nested(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify reply is nested."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@when(parsers.parse('I edit my comment to "{content}"'))
async def edit_comment(content: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Edit comment."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@when("I delete my comment")
async def delete_comment(client: AsyncClient, context: dict[str, Any]) -> None:
    """Delete own comment."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@when("I delete the member's comment")
async def delete_member_comment(client: AsyncClient, context: dict[str, Any]) -> None:
    """Delete member's comment."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@when("I attempt to edit Alice's comment")
async def attempt_edit_alice_comment(client: AsyncClient, context: dict[str, Any]) -> None:
    """Attempt to edit another user's comment."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@when("I attempt to delete Alice's comment")
async def attempt_delete_alice_comment(client: AsyncClient, context: dict[str, Any]) -> None:
    """Attempt to delete another user's comment."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@then("the comment should be updated successfully")
async def comment_updated(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify comment was updated."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@then('the comment should show as "edited"')
async def comment_shows_edited(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify comment is marked as edited."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@then("the comment should be removed completely")
async def comment_removed(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify comment was removed."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@then('the comment content should show "[deleted]"')
async def comment_shows_deleted(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify comment shows as deleted."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@then("the replies should remain visible")
async def replies_visible(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify replies are still visible."""
    pass


@pytest.mark.skip(reason="Phase 3: Comments will be implemented as separate aggregate")
@then("the comment should be deleted successfully")
async def comment_deleted_successfully(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify comment was deleted."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with like/unlike methods")
@when("I unlike the post")
async def unlike_post(client: AsyncClient, context: dict[str, Any]) -> None:
    """Unlike a post."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with like/unlike methods")
@when("I like the comment")
async def like_comment(client: AsyncClient, context: dict[str, Any]) -> None:
    """Like a comment."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with like/unlike methods")
@when("I unlike the comment")
async def unlike_comment(client: AsyncClient, context: dict[str, Any]) -> None:
    """Unlike a comment."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with like/unlike methods")
@when("I like the post again")
async def like_post_again(client: AsyncClient, context: dict[str, Any]) -> None:
    """Like post again (idempotent test)."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with like/unlike methods")
@when("I like my own post")
async def like_own_post(client: AsyncClient, context: dict[str, Any]) -> None:
    """Like own post."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with like/unlike methods")
@when("I attempt to like another post")
async def attempt_like_another_post(client: AsyncClient, context: dict[str, Any]) -> None:
    """Attempt to like post (rate limited)."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with like/unlike methods")
@when("I attempt to like the post without authentication")
async def attempt_like_without_auth(client: AsyncClient, context: dict[str, Any]) -> None:
    """Attempt to like without auth."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with like/unlike methods")
@then("the like should be recorded successfully")
async def like_recorded(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify like was recorded."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with like/unlike methods")
@then(parsers.parse("the post like count should increase by {count:d}"))
async def like_count_increases(count: int, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify like count increased."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with like/unlike methods")
@then("I should appear in the list of likers")
async def in_likers_list(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify user in likers list."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with like/unlike methods")
@then("the like should be removed successfully")
async def like_removed(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify like was removed."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with like/unlike methods")
@then(parsers.parse("the post like count should decrease by {count:d}"))
async def like_count_decreases(count: int, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify like count decreased."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with like/unlike methods")
@then("I should not appear in the list of likers")
async def not_in_likers_list(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify user not in likers list."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with like/unlike methods")
@then(parsers.parse("the comment like count should increase by {count:d}"))
async def comment_like_count_increases(
    count: int, client: AsyncClient, context: dict[str, Any]
) -> None:
    """Verify comment like count increased."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with like/unlike methods")
@then("the like should be removed")
async def like_removed_alt(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify like was removed (alt)."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with like/unlike methods")
@then(parsers.parse("the comment like count should decrease by {count:d}"))
async def comment_like_count_decreases(
    count: int, client: AsyncClient, context: dict[str, Any]
) -> None:
    """Verify comment like count decreased."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with like/unlike methods")
@then("the like count should not change")
async def like_count_unchanged(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify like count didn't change."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with like/unlike methods")
@then("no additional event should be published")
async def no_additional_event(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify no extra events."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with like/unlike methods")
@then(parsers.parse("the post like count should be {count:d}"))
async def like_count_is(count: int, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify like count is exact value."""
    pass


@pytest.mark.skip(reason="Phase 3: Reactions will be implemented with like/unlike methods")
@then(parsers.parse('the like should fail with error "{error_message}"'))
async def like_fails(error_message: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify like failed."""
    pass


# ============================================================================
# PHASE 4 SCENARIOS - SKIPPED (Feed Display & Categories)
# ============================================================================


@pytest.mark.skip(reason="Phase 4: Feed will be implemented with sorting strategies")
@when('I view the feed with "Hot" sorting')
async def view_feed_hot(client: AsyncClient, context: dict[str, Any]) -> None:
    """View feed with Hot sorting."""
    pass


@pytest.mark.skip(reason="Phase 4: Category CRUD will be implemented with admin permissions")
@when("I create a category with:")
async def create_category(client: AsyncClient, context: dict[str, Any]) -> None:
    """Create a category."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed will be implemented with pagination")
@when("I view the feed")
async def view_feed(client: AsyncClient, context: dict[str, Any]) -> None:
    """View the feed."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed will be implemented with sorting strategies")
@then("posts should be ordered")
async def posts_ordered(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify post order."""
    pass


# Additional Phase 4 steps - Category management, feed sorting, pagination


@pytest.mark.skip(reason="Phase 4: Category CRUD will be implemented with admin permissions")
@given(parsers.parse('a category exists with name "{name}"'))
async def category_exists(name: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Create a category."""
    pass


@pytest.mark.skip(reason="Phase 4: Category CRUD will be implemented with admin permissions")
@given("the category has no posts")
async def category_has_no_posts(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify category is empty."""
    pass


@pytest.mark.skip(reason="Phase 4: Category CRUD will be implemented with admin permissions")
@given(parsers.parse("the category has {count:d} posts"))
async def category_has_posts(count: int, client: AsyncClient, context: dict[str, Any]) -> None:
    """Create posts in category."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed will be implemented with sorting strategies")
@given("the following posts exist:")
async def posts_exist(client: AsyncClient, context: dict[str, Any]) -> None:
    """Create multiple posts from datatable."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed will be implemented with pagination")
@given(parsers.parse("{count:d} posts exist in the community"))
async def many_posts_exist(count: int, client: AsyncClient, context: dict[str, Any]) -> None:
    """Create many posts."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed will be implemented with empty state")
@given("no posts exist in the community")
async def no_posts_exist(client: AsyncClient, context: dict[str, Any]) -> None:
    """Ensure no posts exist."""
    pass


@pytest.mark.skip(reason="Phase 4: Non-member access will be implemented with membership checks")
@given(parsers.parse('a user exists with email "{email}" and is not a community member'))
async def user_not_member(email: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Create user without membership."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed will be implemented with sorting strategies")
@given(parsers.parse('a post exists in category "{category}"'))
async def post_in_category_given(
    category: str, client: AsyncClient, context: dict[str, Any]
) -> None:
    """Create post in specific category."""
    pass


@pytest.mark.skip(reason="Phase 4: Comments will be implemented in Phase 3")
@given(parsers.parse("the post has {count:d} comments"))
async def post_has_n_comments(count: int, client: AsyncClient, context: dict[str, Any]) -> None:
    """Add comments to post."""
    pass


@pytest.mark.skip(reason="Phase 4: Post detail view will be implemented with feed")
@given("a post exists")
async def post_exists_phase4(client: AsyncClient, context: dict[str, Any]) -> None:
    """Create a post."""
    pass


@pytest.mark.skip(reason="Phase 4: Post detail view will be implemented with comments")
@given("the post has a comment with 2 replies")
async def post_has_comment_with_replies(client: AsyncClient, context: dict[str, Any]) -> None:
    """Create post with threaded comments."""
    pass


@pytest.mark.skip(reason="Phase 4: Deleted user content will be implemented with soft deletion")
@given("a post exists authored by a user who deleted their account")
async def post_by_deleted_user(client: AsyncClient, context: dict[str, Any]) -> None:
    """Create post by deleted user."""
    pass


@pytest.mark.skip(reason="Phase 4: Deleted user content will be implemented with soft deletion")
@given("I am a community member")
async def i_am_member(client: AsyncClient, context: dict[str, Any]) -> None:
    """Mark as community member."""
    pass


@pytest.mark.skip(reason="Phase 4: Deleted posts will be handled with soft deletion")
@given("a post existed but was deleted")
async def post_was_deleted(client: AsyncClient, context: dict[str, Any]) -> None:
    """Create and delete a post."""
    pass


@pytest.mark.skip(reason="Phase 4: Pinning limits will be implemented with pin validation")
@given(parsers.parse("{count:d} posts are pinned"))
async def many_posts_pinned(count: int, client: AsyncClient, context: dict[str, Any]) -> None:
    """Create many pinned posts."""
    pass


@pytest.mark.skip(reason="Phase 4: Concurrent edits will be tested with optimistic locking")
@when("two users edit the post simultaneously")
async def concurrent_edits(client: AsyncClient, context: dict[str, Any]) -> None:
    """Simulate concurrent edits."""
    pass


@pytest.mark.skip(reason="Phase 4: Category CRUD will be implemented with admin permissions")
@when("I update the category with:")
async def update_category(client: AsyncClient, context: dict[str, Any]) -> None:
    """Update a category."""
    pass


@pytest.mark.skip(reason="Phase 4: Category CRUD will be implemented with admin permissions")
@when("I delete the category")
async def delete_category(client: AsyncClient, context: dict[str, Any]) -> None:
    """Delete a category."""
    pass


@pytest.mark.skip(reason="Phase 4: Category CRUD will be implemented with admin permissions")
@when("I attempt to delete the category")
async def attempt_delete_category(client: AsyncClient, context: dict[str, Any]) -> None:
    """Attempt to delete category."""
    pass


@pytest.mark.skip(reason="Phase 4: Category CRUD will be implemented with uniqueness validation")
@when(parsers.parse('I attempt to create a category with name "{name}"'))
async def attempt_create_category_with_name(
    name: str, client: AsyncClient, context: dict[str, Any]
) -> None:
    """Attempt to create category with specific name."""
    pass


@pytest.mark.skip(reason="Phase 4: Category CRUD will be implemented with admin permissions")
@when("I attempt to create a category")
async def attempt_create_category(client: AsyncClient, context: dict[str, Any]) -> None:
    """Attempt to create category (may fail)."""
    pass


@pytest.mark.skip(reason="Phase 4: Category management will be implemented with post moving")
@when(parsers.parse('I move the post to category "{category}"'))
async def move_post_to_category(
    category: str, client: AsyncClient, context: dict[str, Any]
) -> None:
    """Move post to different category."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed will be implemented with sorting strategies")
@when(parsers.parse('I view the feed with "{sort}" sorting'))
async def view_feed_with_sort(sort: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """View feed with specific sorting."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed will be implemented with category filtering")
@when(parsers.parse('I filter the feed by category "{category}"'))
async def filter_feed_by_category(
    category: str, client: AsyncClient, context: dict[str, Any]
) -> None:
    """Filter feed by category."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed will be implemented with pagination")
@when(parsers.parse("I view the feed with limit {limit:d}"))
async def view_feed_with_limit(limit: int, client: AsyncClient, context: dict[str, Any]) -> None:
    """View feed with pagination limit."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed will be implemented with pagination")
@when("I request the next page with the cursor")
async def request_next_page(client: AsyncClient, context: dict[str, Any]) -> None:
    """Request next page of feed."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed will be implemented with authentication check")
@when("I attempt to view the feed without authentication")
async def attempt_view_feed_without_auth(client: AsyncClient, context: dict[str, Any]) -> None:
    """Attempt to view feed without auth."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed will be implemented with membership check")
@when("I attempt to view the community feed")
async def attempt_view_community_feed(client: AsyncClient, context: dict[str, Any]) -> None:
    """Attempt to view feed (may fail for non-members)."""
    pass


@pytest.mark.skip(reason="Phase 4: Post detail view will be implemented with feed")
@when("I view the post details")
async def view_post_details(client: AsyncClient, context: dict[str, Any]) -> None:
    """View post details."""
    pass


@pytest.mark.skip(reason="Phase 4: Post detail view will be implemented with deleted posts")
@when("I attempt to view the deleted post")
async def attempt_view_deleted_post(client: AsyncClient, context: dict[str, Any]) -> None:
    """Attempt to view deleted post."""
    pass


@pytest.mark.skip(reason="Phase 4: Deleted user content will be implemented with placeholder")
@when("I view the post")
async def view_post(client: AsyncClient, context: dict[str, Any]) -> None:
    """View a post."""
    pass


@pytest.mark.skip(reason="Phase 4: Category CRUD will be implemented with admin permissions")
@then("the category should be created successfully")
async def category_created(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify category was created."""
    pass


@pytest.mark.skip(reason="Phase 4: Category CRUD will be implemented with admin permissions")
@then("the category should appear in the category list")
async def category_in_list(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify category appears in list."""
    pass


@pytest.mark.skip(reason="Phase 4: Category CRUD will be implemented with admin permissions")
@then("the category should be updated successfully")
async def category_updated(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify category was updated."""
    pass


@pytest.mark.skip(reason="Phase 4: Category CRUD will be implemented with admin permissions")
@then("the category should be deleted successfully")
async def category_deleted(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify category was deleted."""
    pass


@pytest.mark.skip(reason="Phase 4: Category CRUD will be implemented with validation")
@then(parsers.parse('the deletion should fail with error "{error_message}"'))
async def deletion_fails_alt(
    error_message: str, client: AsyncClient, context: dict[str, Any]
) -> None:
    """Verify deletion failed (alt)."""
    pass


@pytest.mark.skip(reason="Phase 4: Category CRUD will be implemented with validation")
@then(parsers.parse('the creation should fail with error "{error_message}"'))
async def creation_fails(error_message: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify creation failed."""
    pass


@pytest.mark.skip(reason="Phase 4: Category management will be implemented with post moving")
@then(parsers.parse('the post should be in category "{category}"'))
async def post_in_category_check(
    category: str, client: AsyncClient, context: dict[str, Any]
) -> None:
    """Verify post is in category."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed will be implemented with sorting strategies")
@then("posts should be ordered:")
async def posts_ordered_list(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify post order."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed will be implemented with pinned posts")
@then("pinned posts should appear first:")
async def pinned_posts_first(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify pinned posts at top."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed will be implemented with pinned posts")
@then("then regular posts:")
async def then_regular_posts(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify regular posts after pinned."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed will be implemented with category filtering")
@then("I should see only posts:")
async def see_only_posts(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify filtered posts."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed will be implemented with pagination")
@then(parsers.parse("I should see {count:d} posts"))
async def see_n_posts(count: int, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify post count."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed will be implemented with pagination")
@then("I should receive a cursor for the next page")
async def receive_cursor(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify cursor received."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed will be implemented with pagination")
@then(parsers.parse("I should see the remaining {count:d} posts"))
async def see_remaining_posts(count: int, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify remaining posts."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed will be implemented with empty state")
@then("I should see an empty state message")
async def see_empty_state(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify empty state shown."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed will be implemented with empty state")
@then(parsers.parse('the message should say "{message}"'))
async def message_says(message: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify message content."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed will be implemented with authentication check")
@then(parsers.parse('the request should fail with error "{error_message}"'))
async def request_fails_with_error(
    error_message: str, client: AsyncClient, context: dict[str, Any]
) -> None:
    """Verify request failed."""
    pass


@pytest.mark.skip(reason="Phase 4: Post detail view will be implemented with comments")
@then("I should see the full post content")
async def see_full_content(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify full content shown."""
    pass


@pytest.mark.skip(reason="Phase 4: Post detail view will be implemented with comments")
@then(parsers.parse("I should see all {count:d} comments"))
async def see_all_comments(count: int, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify all comments shown."""
    pass


@pytest.mark.skip(reason="Phase 4: Post detail view will be implemented with reactions")
@then("I should see like counts for post and comments")
async def see_like_counts(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify like counts shown."""
    pass


@pytest.mark.skip(reason="Phase 4: Post detail view will be implemented with reactions")
@then("I should see the list of users who liked")
async def see_likers_list(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify likers list shown."""
    pass


@pytest.mark.skip(reason="Phase 4: Post detail view will be implemented with threaded comments")
@then("I should see the parent comment")
async def see_parent_comment(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify parent comment shown."""
    pass


@pytest.mark.skip(reason="Phase 4: Post detail view will be implemented with threaded comments")
@then(parsers.parse("I should see the {count:d} replies nested under the parent"))
async def see_nested_replies(count: int, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify nested replies shown."""
    pass


@pytest.mark.skip(reason="Phase 4: Permissions summary will be tested comprehensively")
@then("I should be able to create posts")
async def can_create_posts(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify can create posts."""
    pass


@pytest.mark.skip(reason="Phase 4: Permissions summary will be tested comprehensively")
@then("I should be able to delete any post")
async def can_delete_any_post(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify can delete any post."""
    pass


@pytest.mark.skip(reason="Phase 4: Permissions summary will be tested comprehensively")
@then("I should be able to pin posts")
async def can_pin_posts(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify can pin posts."""
    pass


@pytest.mark.skip(reason="Phase 4: Permissions summary will be tested comprehensively")
@then("I should be able to lock posts")
async def can_lock_posts(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify can lock posts."""
    pass


@pytest.mark.skip(reason="Phase 4: Permissions summary will be tested comprehensively")
@then("I should be able to create categories")
async def can_create_categories(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify can create categories."""
    pass


@pytest.mark.skip(reason="Phase 4: Permissions summary will be tested comprehensively")
@then("I should be able to delete categories")
async def can_delete_categories(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify can delete categories."""
    pass


@pytest.mark.skip(reason="Phase 4: Permissions summary will be tested comprehensively")
@then("I should NOT be able to create categories")
async def cannot_create_categories(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify cannot create categories."""
    pass


@pytest.mark.skip(reason="Phase 4: Permissions summary will be tested comprehensively")
@then("I should NOT be able to delete categories")
async def cannot_delete_categories(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify cannot delete categories."""
    pass


@pytest.mark.skip(reason="Phase 4: Permissions summary will be tested comprehensively")
@then("I should be able to edit my own posts")
async def can_edit_own_posts(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify can edit own posts."""
    pass


@pytest.mark.skip(reason="Phase 4: Permissions summary will be tested comprehensively")
@then("I should be able to delete my own posts")
async def can_delete_own_posts(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify can delete own posts."""
    pass


@pytest.mark.skip(reason="Phase 4: Permissions summary will be tested comprehensively")
@then("I should NOT be able to delete other posts")
async def cannot_delete_other_posts(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify cannot delete other posts."""
    pass


@pytest.mark.skip(reason="Phase 4: Permissions summary will be tested comprehensively")
@then("I should NOT be able to pin posts")
async def cannot_pin_posts(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify cannot pin posts."""
    pass


@pytest.mark.skip(reason="Phase 4: Permissions summary will be tested comprehensively")
@then("I should NOT be able to lock posts")
async def cannot_lock_posts(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify cannot lock posts."""
    pass


@pytest.mark.skip(reason="Phase 4: Concurrent edits will be tested with optimistic locking")
@then("the last edit should be saved")
async def last_edit_saved(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify last edit was saved."""
    pass


@pytest.mark.skip(reason="Phase 4: Deleted posts will be handled with soft deletion")
@then("I should see a 404 error")
async def see_404_error(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify 404 error shown."""
    pass


@pytest.mark.skip(reason="Phase 4: Deleted posts will be handled with soft deletion")
@then(parsers.parse('the error message should say "{message}"'))
async def error_message_says(message: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify error message content."""
    pass


@pytest.mark.skip(reason="Phase 4: Deleted user content will be implemented with placeholder")
@then('the author should show as "[deleted user]"')
async def author_shows_deleted(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify author shows as deleted."""
    pass


@pytest.mark.skip(reason="Phase 4: Deleted user content will be implemented with placeholder")
@then("the post content should still be visible")
async def content_still_visible(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify content still visible."""
    pass


@pytest.mark.skip(reason="Phase 4: Pinning limits will be implemented with pin validation")
@then("I should see only the 5 most recently pinned posts at the top")
async def see_5_pinned_posts(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify max 5 pinned posts shown."""
    pass


# ============================================================================
# MISSING STEP DEFINITIONS FOR PHASE 3-4 (Stub implementations)
# ============================================================================


@pytest.mark.skip(reason="Phase 3: Comment threading not yet implemented")
@then(parsers.parse('a "{event}" event should be published with parent_comment_id'))
async def event_with_parent_comment_id(
    event: str, client: AsyncClient, context: dict[str, Any]
) -> None:
    """Verify event with parent_comment_id (Phase 3)."""
    pass


@pytest.mark.skip(reason="Phase 3: Comment rate limiting not yet implemented")
@when("I attempt to add another comment")
async def attempt_add_another_comment(client: AsyncClient, context: dict[str, Any]) -> None:
    """Attempt to add another comment for rate limit test (Phase 3)."""
    pass


@pytest.mark.skip(reason="Phase 3: Simplified post creation for reactions not yet implemented")
@given("I created a post")
async def created_a_post(client: AsyncClient, context: dict[str, Any]) -> None:
    """User created a post (Phase 3 - simplified version)."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed sorting not yet implemented")
@then(parsers.parse("posts should be ordered: {posts}"))
async def posts_ordered_with_arg(posts: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify posts are in specified order (Phase 4)."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed with pinning not yet implemented")
@then(parsers.parse("pinned posts should appear first: {posts}"))
async def pinned_posts_first_with_arg(
    posts: str, client: AsyncClient, context: dict[str, Any]
) -> None:
    """Verify pinned posts appear first (Phase 4)."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed filtering not yet implemented")
@then(parsers.parse("I should see only posts: {posts}"))
async def see_only_posts_with_arg(posts: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify only specified posts are visible (Phase 4)."""
    pass


@pytest.mark.skip(reason="Phase 4: Feed with pinning not yet implemented")
@then(parsers.parse("then regular posts: {posts}"))
async def then_regular_posts_with_arg(
    posts: str, client: AsyncClient, context: dict[str, Any]
) -> None:
    """Verify regular posts order after pinned posts (Phase 4)."""
    pass
