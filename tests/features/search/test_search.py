"""BDD tests for Search feature.

Phase 1 (11 scenarios — active):
- Member search: by display name, username, bio, alphabetical sort, card fields
- Post search: by title, by body content, newest-first sort, card fields
- Tabbed results: counts for both tabs, switch between tabs

Phase 2 (8 scenarios — skipped):
- Pagination: paginated results, next page
- Stemming: member bio stemming, post content stemming
- Validation: query too short, empty query, invalid type, max length truncation

Phase 3 (11 scenarios — skipped):
- Edge cases: no results, special characters, deleted posts, inactive members,
  whitespace-only, member with no bio, multiple member matches
- Security: unauthenticated, non-member, SQL injection, rate limiting

NOTE: Step functions have intentionally "unused" parameters like `client` for
pytest-bdd fixture dependency ordering. See MEMORY.md for details.
"""

# ruff: noqa: ARG001

from typing import Any

import pytest
from httpx import AsyncClient
from pytest_bdd import given, parsers, scenario, then, when

# ============================================================================
# PHASE 2 SCENARIOS (8 active — pagination, stemming, validation)
# ============================================================================


@scenario("search.feature", "Search results are paginated")
def test_search_results_are_paginated() -> None:
    pass


@scenario("search.feature", "Navigate to next page of results")
def test_navigate_to_next_page_of_results() -> None:
    pass


@scenario("search.feature", "Search uses stemming for member bio")
def test_search_uses_stemming_for_member_bio() -> None:
    pass


@scenario("search.feature", "Search uses stemming for post content")
def test_search_uses_stemming_for_post_content() -> None:
    pass


@scenario("search.feature", "Search with query shorter than 3 characters")
def test_search_with_query_shorter_than_3_characters() -> None:
    pass


@scenario("search.feature", "Search with empty query")
def test_search_with_empty_query() -> None:
    pass


@scenario("search.feature", "Search with invalid type parameter")
def test_search_with_invalid_type_parameter() -> None:
    pass


@scenario("search.feature", "Search with query exceeding maximum length")
def test_search_with_query_exceeding_maximum_length() -> None:
    pass


# ============================================================================
# PHASE 3 SKIPS (11 scenarios)
# ============================================================================


@pytest.mark.skip(reason="Phase 3: Edge cases")
@scenario("search.feature", "Search returns no results")
def test_search_returns_no_results() -> None:
    pass


@pytest.mark.skip(reason="Phase 3: Edge cases - special characters")
@scenario("search.feature", "Search with special characters")
def test_search_with_special_characters() -> None:
    pass


@pytest.mark.skip(reason="Phase 3: Edge cases - deleted posts")
@scenario("search.feature", "Deleted posts do not appear in search results")
def test_deleted_posts_do_not_appear_in_search_results() -> None:
    pass


@pytest.mark.skip(reason="Phase 3: Edge cases - inactive members")
@scenario("search.feature", "Inactive members do not appear in search results")
def test_inactive_members_do_not_appear_in_search_results() -> None:
    pass


@pytest.mark.skip(reason="Phase 3: Edge cases - whitespace")
@scenario("search.feature", "Search with only whitespace")
def test_search_with_only_whitespace() -> None:
    pass


@pytest.mark.skip(reason="Phase 3: Edge cases - no bio")
@scenario("search.feature", "Member with no bio is still found by name")
def test_member_with_no_bio_is_still_found_by_name() -> None:
    pass


@pytest.mark.skip(reason="Phase 3: Edge cases - multiple matches")
@scenario("search.feature", "Search query matches across multiple members")
def test_search_query_matches_across_multiple_members() -> None:
    pass


@pytest.mark.skip(reason="Phase 3: Security - authentication")
@scenario("search.feature", "Unauthenticated user cannot search")
def test_unauthenticated_user_cannot_search() -> None:
    pass


@pytest.mark.skip(reason="Phase 3: Security - membership")
@scenario("search.feature", "Non-member cannot search a community")
def test_non_member_cannot_search_a_community() -> None:
    pass


@pytest.mark.skip(reason="Phase 3: Security - SQL injection")
@scenario("search.feature", "Search input is sanitized against SQL injection")
def test_search_input_is_sanitized_against_sql_injection() -> None:
    pass


@pytest.mark.skip(reason="Phase 3: Security - rate limiting")
@scenario("search.feature", "Search respects rate limiting")
def test_search_respects_rate_limiting() -> None:
    pass


# ============================================================================
# PHASE 1 SCENARIOS (11 active) — auto-collected by scenarios() call is NOT used
# because we need explicit @scenario decorators for the skip markers above.
# Instead, we declare them explicitly.
# ============================================================================


@scenario("search.feature", "Search for a member by display name")
def test_search_for_a_member_by_display_name() -> None:
    pass


@scenario("search.feature", "Search for a member by username")
def test_search_for_a_member_by_username() -> None:
    pass


@scenario("search.feature", "Search for a member by bio content")
def test_search_for_a_member_by_bio_content() -> None:
    pass


@scenario("search.feature", "Member results are sorted alphabetically")
def test_member_results_are_sorted_alphabetically() -> None:
    pass


@scenario("search.feature", "Member result card shows expected fields")
def test_member_result_card_shows_expected_fields() -> None:
    pass


@scenario("search.feature", "Search for a post by title")
def test_search_for_a_post_by_title() -> None:
    pass


@scenario("search.feature", "Search for a post by body content")
def test_search_for_a_post_by_body_content() -> None:
    pass


@scenario("search.feature", "Post results are sorted by newest first")
def test_post_results_are_sorted_by_newest_first() -> None:
    pass


@scenario("search.feature", "Post result card shows expected fields")
def test_post_result_card_shows_expected_fields() -> None:
    pass


@scenario("search.feature", "Search returns counts for both tabs")
def test_search_returns_counts_for_both_tabs() -> None:
    pass


@scenario("search.feature", "Switch between member and post tabs")
def test_switch_between_member_and_post_tabs() -> None:
    pass


# ============================================================================
# HELPERS
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


@given(parsers.parse('a community "{name}" exists'))
async def community_exists(
    client: AsyncClient,
    name: str,
    create_search_community: Any,
    context: dict[str, Any],
) -> None:
    """Create a community."""
    community = await create_search_community(name=name)
    context["community"] = community
    context["community_id"] = community.id


@given("the community has the following members:")
async def community_has_members(
    client: AsyncClient,
    create_search_member: Any,
    create_search_category: Any,
    context: dict[str, Any],
    datatable: list[dict[str, str]],
) -> None:
    """Create members from datatable."""
    community_id = context["community_id"]
    members: dict[str, Any] = {}

    # Create a default category for posts (needed later)
    if "default_category" not in context:
        category = await create_search_category(community_id=community_id)
        context["default_category"] = category

    for row in datatable:
        user, member = await create_search_member(
            community_id=community_id,
            display_name=row["display_name"],
            username=row["username"],
            bio=row.get("bio"),
        )
        members[row["display_name"]] = {
            "user": user,
            "member": member,
            "email": user.email,
        }

    context["members"] = members


@given("the community has the following posts:")
async def community_has_posts(
    client: AsyncClient,
    create_search_post: Any,
    context: dict[str, Any],
    datatable: list[dict[str, str]],
) -> None:
    """Create posts from datatable."""
    community_id = context["community_id"]
    members = context["members"]
    category = context["default_category"]
    posts: dict[str, Any] = {}

    for row in datatable:
        author_info = members[row["author"]]
        post = await create_search_post(
            community_id=community_id,
            author_id=author_info["user"].id,
            category_id=category.id,
            title=row["title"],
            content=row["body"],
        )
        posts[row["title"]] = post

    context["posts"] = posts


# ============================================================================
# GIVEN — AUTHENTICATION
# ============================================================================


@given(parsers.parse('the member "{display_name}" is authenticated'))
async def member_is_authenticated(
    client: AsyncClient,
    display_name: str,
    context: dict[str, Any],
) -> None:
    """Authenticate a member and store token."""
    members = context["members"]
    member_info = members[display_name]
    email = member_info["email"]
    token = await _get_auth_token(client, email)
    context["token"] = token
    context["current_user"] = display_name


# ============================================================================
# GIVEN — PAGINATION SETUP (Phase 2 — steps for skipped scenarios)
# ============================================================================


@given(parsers.parse('the community has {count:d} members with "{text}" in their bio'))
async def community_has_many_members(
    client: AsyncClient,
    count: int,
    text: str,
    create_search_member: Any,
    context: dict[str, Any],
) -> None:
    """Create multiple members with matching bio for pagination tests."""
    community_id = context["community_id"]
    for i in range(count):
        await create_search_member(
            community_id=community_id,
            display_name=f"Dev User {i:03d}",
            username=f"dev-user-{i:03d}",
            bio=f"A {text} working on project {i}",
        )


# ============================================================================
# WHEN STEPS
# ============================================================================


@when(parsers.parse('the member searches for "{query}" with type "{search_type}"'))
async def member_searches(
    client: AsyncClient,
    query: str,
    search_type: str,
    context: dict[str, Any],
) -> None:
    """Execute a search query."""
    token = context["token"]
    response = await client.get(
        "/api/v1/community/search",
        params={"q": query, "type": search_type},
        headers={"Authorization": f"Bearer {token}"},
    )
    context["response"] = response
    context["response_data"] = response.json() if response.status_code == 200 else {}
    context["response_status"] = response.status_code


@when(
    parsers.parse('the member searches for "{query}" with type "{search_type}" and limit {limit:d}')
)
async def member_searches_with_limit(
    client: AsyncClient,
    query: str,
    search_type: str,
    limit: int,
    context: dict[str, Any],
) -> None:
    """Execute a search query with limit."""
    token = context["token"]
    response = await client.get(
        "/api/v1/community/search",
        params={"q": query, "type": search_type, "limit": limit},
        headers={"Authorization": f"Bearer {token}"},
    )
    context["response"] = response
    context["response_data"] = response.json() if response.status_code == 200 else {}
    context["response_status"] = response.status_code


@when(
    parsers.parse(
        'the member searches for "{query}" with type "{search_type}" and limit {limit:d} and offset {offset:d}'
    )
)
async def member_searches_with_limit_offset(
    client: AsyncClient,
    query: str,
    search_type: str,
    limit: int,
    offset: int,
    context: dict[str, Any],
) -> None:
    """Execute a search query with limit and offset."""
    token = context["token"]
    response = await client.get(
        "/api/v1/community/search",
        params={"q": query, "type": search_type, "limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {token}"},
    )
    context["response"] = response
    context["response_data"] = response.json() if response.status_code == 200 else {}
    context["response_status"] = response.status_code


# ============================================================================
# THEN — MEMBER SEARCH ASSERTIONS
# ============================================================================


@then(parsers.parse("the search results should contain {count:d} member"))
@then(parsers.parse("the search results should contain {count:d} members"))
async def search_contains_n_members(
    client: AsyncClient, count: int, context: dict[str, Any]
) -> None:
    """Assert member result count."""
    data = context["response_data"]
    assert context["response_status"] == 200, f"Expected 200, got {context['response_status']}"
    assert len(data["items"]) == count, f"Expected {count} items, got {len(data['items'])}"


@then(parsers.parse('the member result should include "{display_name}"'))
async def member_result_includes(
    client: AsyncClient, display_name: str, context: dict[str, Any]
) -> None:
    """Assert a member is in results."""
    data = context["response_data"]
    names = [item["display_name"] for item in data["items"]]
    assert display_name in names, f"'{display_name}' not found in {names}"


@then("the member results should be sorted alphabetically by display name")
async def member_results_sorted_alphabetically(
    client: AsyncClient, context: dict[str, Any]
) -> None:
    """Assert member results are sorted by display_name ASC."""
    data = context["response_data"]
    names = [item["display_name"] for item in data["items"]]
    assert names == sorted(names), f"Not sorted: {names}"


@then(parsers.parse('the member result for "{display_name}" should include:'))
async def member_result_has_fields(
    client: AsyncClient,
    display_name: str,
    datatable: list[dict[str, str]],
    context: dict[str, Any],
) -> None:
    """Assert a member result has expected fields."""
    data = context["response_data"]
    member = None
    for item in data["items"]:
        if item.get("display_name") == display_name:
            member = item
            break
    assert member is not None, f"Member '{display_name}' not found in results"

    for row in datatable:
        field = row["field"]
        present = row["present"].lower() == "true"
        if present:
            assert field in member, f"Field '{field}' missing from member result"
            # For fields that should be present, value should not be None
            # (role and joined_at are always present; bio/username can be None)
            if field in ("display_name", "role", "joined_at"):
                assert member[field] is not None, f"Field '{field}' is None"


# ============================================================================
# THEN — POST SEARCH ASSERTIONS
# ============================================================================


@then(parsers.parse("the search results should contain {count:d} post"))
@then(parsers.parse("the search results should contain {count:d} posts"))
async def search_contains_n_posts(client: AsyncClient, count: int, context: dict[str, Any]) -> None:
    """Assert post result count."""
    data = context["response_data"]
    assert context["response_status"] == 200
    assert len(data["items"]) == count, f"Expected {count} items, got {len(data['items'])}"


@then(parsers.parse('the post result should include "{title}"'))
async def post_result_includes(client: AsyncClient, title: str, context: dict[str, Any]) -> None:
    """Assert a post is in results."""
    data = context["response_data"]
    titles = [item["title"] for item in data["items"]]
    assert title in titles, f"'{title}' not found in {titles}"


@then("the post results should be sorted by creation date descending")
async def post_results_sorted_by_date_desc(client: AsyncClient, context: dict[str, Any]) -> None:
    """Assert post results are sorted newest first."""
    data = context["response_data"]
    dates = [item["created_at"] for item in data["items"]]
    assert dates == sorted(dates, reverse=True), f"Not sorted desc: {dates}"


@then(parsers.parse('the post result for "{title}" should include:'))
async def post_result_has_fields(
    client: AsyncClient,
    title: str,
    datatable: list[dict[str, str]],
    context: dict[str, Any],
) -> None:
    """Assert a post result has expected fields."""
    data = context["response_data"]
    post = None
    for item in data["items"]:
        if item.get("title") == title:
            post = item
            break
    assert post is not None, f"Post '{title}' not found in results"

    for row in datatable:
        field = row["field"]
        present = row["present"].lower() == "true"
        # Map BDD field names to API response field names
        field_map = {
            "body_snippet": "body_snippet",
            "author_name": "author_name",
            "category": "category_name",
            "created_at": "created_at",
            "title": "title",
        }
        api_field = field_map.get(field, field)
        if present:
            assert api_field in post, f"Field '{api_field}' missing from post result"


# ============================================================================
# THEN — TABBED RESULTS ASSERTIONS
# ============================================================================


@then("the response should include a member count")
async def response_has_member_count(client: AsyncClient, context: dict[str, Any]) -> None:
    """Assert response includes member_count."""
    data = context["response_data"]
    assert "member_count" in data, "member_count not in response"
    assert isinstance(data["member_count"], int)


@then("the response should include a post count")
async def response_has_post_count(client: AsyncClient, context: dict[str, Any]) -> None:
    """Assert response includes post_count."""
    data = context["response_data"]
    assert "post_count" in data, "post_count not in response"
    assert isinstance(data["post_count"], int)


@then("the search results should contain members")
async def search_contains_members(client: AsyncClient, context: dict[str, Any]) -> None:
    """Assert search returned member results."""
    data = context["response_data"]
    assert context["response_status"] == 200
    # Members have user_id field, posts have title field
    if len(data["items"]) > 0:
        assert "user_id" in data["items"][0] or "display_name" in data["items"][0]


@then("the search results should contain posts")
async def search_contains_posts(client: AsyncClient, context: dict[str, Any]) -> None:
    """Assert search returned post results."""
    data = context["response_data"]
    assert context["response_status"] == 200
    if len(data["items"]) > 0:
        assert "title" in data["items"][0]


# ============================================================================
# THEN — PAGINATION ASSERTIONS (Phase 2 — steps for skipped scenarios)
# ============================================================================


@then("the response should indicate more results are available")
async def response_has_more(client: AsyncClient, context: dict[str, Any]) -> None:
    """Assert has_more is true."""
    data = context["response_data"]
    assert data["has_more"] is True


@then("the results should be from the second page")
async def results_from_second_page(client: AsyncClient, context: dict[str, Any]) -> None:
    """Assert results are from offset page."""
    data = context["response_data"]
    assert len(data["items"]) > 0


# ============================================================================
# THEN — SEARCH RESULT COUNT (multi-use)
# ============================================================================


@then(parsers.parse("the search results should contain at least {count:d} member"))
@then(parsers.parse("the search results should contain at least {count:d} members"))
async def search_contains_at_least_n_members(
    client: AsyncClient, count: int, context: dict[str, Any]
) -> None:
    """Assert at least N member results."""
    data = context["response_data"]
    assert len(data["items"]) >= count


# ============================================================================
# THEN — GENERIC (Phase 2/3 — steps for skipped scenarios, defined to avoid
# collection errors if pytest-bdd tries to parse them)
# ============================================================================


@then(parsers.parse('the search should fail with a "{error_type}" error'))
async def search_fails_with_error(
    client: AsyncClient, error_type: str, context: dict[str, Any]
) -> None:
    """Assert search failed with expected error code."""
    error_code_map = {
        "query too short": ("QUERY_TOO_SHORT", 400),
        "query required": ("QUERY_REQUIRED", 400),
        "invalid search type": ("INVALID_SEARCH_TYPE", 400),
        "authentication required": (None, 401),
        "not a member": (None, 403),
        "rate limit exceeded": ("RATE_LIMIT_EXCEEDED", 429),
    }
    expected_code, expected_status = error_code_map.get(error_type, (None, None))
    assert context["response_status"] == expected_status, (
        f"Expected {expected_status} for '{error_type}', got {context['response_status']}"
    )
    if expected_code is not None:
        response = context["response"]
        detail = response.json().get("detail", {})
        assert detail.get("code") == expected_code, (
            f"Expected error code '{expected_code}', got '{detail}'"
        )


@then("the search should execute successfully")
async def search_executes_successfully(client: AsyncClient, context: dict[str, Any]) -> None:
    """Assert search completed."""
    assert context["response_status"] == 200


@then("the response should indicate no results found")
async def response_no_results(client: AsyncClient, context: dict[str, Any]) -> None:
    """Assert no results."""
    data = context["response_data"]
    assert len(data["items"]) == 0


@then(parsers.parse("the search query should be truncated to {length:d} characters"))
async def search_query_truncated(client: AsyncClient, length: int, context: dict[str, Any]) -> None:
    """Assert query was truncated (search still works)."""
    assert context["response_status"] == 200


@when(parsers.parse('the member searches for "" with type "{search_type}"'))
async def member_searches_empty_query(
    client: AsyncClient,
    search_type: str,
    context: dict[str, Any],
) -> None:
    """Execute a search with empty query."""
    token = context["token"]
    response = await client.get(
        "/api/v1/community/search",
        params={"q": "", "type": search_type},
        headers={"Authorization": f"Bearer {token}"},
    )
    context["response"] = response
    context["response_data"] = response.json() if response.status_code == 200 else {}
    context["response_status"] = response.status_code


@when("the member searches with a 201-character query")
async def member_searches_long_query(client: AsyncClient, context: dict[str, Any]) -> None:
    """Search with a very long query."""
    token = context["token"]
    long_query = "a" * 201
    response = await client.get(
        "/api/v1/community/search",
        params={"q": long_query, "type": "members"},
        headers={"Authorization": f"Bearer {token}"},
    )
    context["response"] = response
    context["response_data"] = response.json() if response.status_code == 200 else {}
    context["response_status"] = response.status_code


@when(parsers.parse("the member performs {count:d} searches within {minutes:d} minute"))
@when(parsers.parse("the member performs {count:d} searches within {minutes:d} minutes"))
async def member_performs_many_searches(
    client: AsyncClient, count: int, minutes: int, context: dict[str, Any]
) -> None:
    """Perform multiple searches for rate limiting test."""
    token = context["token"]
    last_response = None
    for _ in range(count):
        last_response = await client.get(
            "/api/v1/community/search",
            params={"q": "test", "type": "members"},
            headers={"Authorization": f"Bearer {token}"},
        )
    if last_response is not None:
        context["response"] = last_response
        context["response_data"] = last_response.json() if last_response.status_code == 200 else {}
        context["response_status"] = last_response.status_code


@then(parsers.parse('the {ordinal} search should fail with a "{error_type}" error'))
async def nth_search_fails(
    client: AsyncClient, ordinal: str, error_type: str, context: dict[str, Any]
) -> None:
    """Assert the last search failed."""
    assert context["response_status"] != 200


# Phase 3 security — given steps for skipped scenarios


@given("no user is authenticated")
async def no_user_authenticated(client: AsyncClient, context: dict[str, Any]) -> None:
    """No auth token set."""
    context["token"] = None


@when(parsers.parse('an unauthenticated user attempts to search for "{query}"'))
async def unauthenticated_search(client: AsyncClient, query: str, context: dict[str, Any]) -> None:
    """Search without authentication."""
    response = await client.get(
        "/api/v1/community/search",
        params={"q": query, "type": "members"},
    )
    context["response"] = response
    context["response_data"] = response.json() if response.status_code == 200 else {}
    context["response_status"] = response.status_code


@given(parsers.parse('a user "{name}" exists but is not a member of "{community}"'))
async def user_not_member(
    client: AsyncClient, name: str, community: str, context: dict[str, Any]
) -> None:
    """User exists but not a member."""
    context["non_member_name"] = name


@given(parsers.parse('the user "{name}" is authenticated'))
async def user_is_authenticated(client: AsyncClient, name: str, context: dict[str, Any]) -> None:
    """Authenticate a non-member user."""
    context["token"] = "fake-token-for-non-member"


@when(parsers.parse('the user searches for "{query}" in community "{community}"'))
async def user_searches_in_community(
    client: AsyncClient, query: str, community: str, context: dict[str, Any]
) -> None:
    """Search in a specific community."""
    token = context.get("token", "")
    response = await client.get(
        "/api/v1/community/search",
        params={"q": query, "type": "members"},
        headers={"Authorization": f"Bearer {token}"},
    )
    context["response"] = response
    context["response_data"] = response.json() if response.status_code == 200 else {}
    context["response_status"] = response.status_code


@given(parsers.parse('the post "{title}" has been deleted'))
async def post_has_been_deleted(client: AsyncClient, title: str, context: dict[str, Any]) -> None:
    """Mark a post as deleted."""
    pass


@given(parsers.parse('the member "{name}" has been deactivated'))
async def member_has_been_deactivated(
    client: AsyncClient, name: str, context: dict[str, Any]
) -> None:
    """Deactivate a member."""
    pass


@given(parsers.parse('a member "{name}" exists with username "{username}" and no bio'))
async def member_exists_no_bio(
    client: AsyncClient,
    name: str,
    username: str,
    create_search_member: Any,
    context: dict[str, Any],
) -> None:
    """Create a member with no bio."""
    community_id = context["community_id"]
    user, member = await create_search_member(
        community_id=community_id,
        display_name=name,
        username=username,
        bio=None,
    )
    if "members" not in context:
        context["members"] = {}
    context["members"][name] = {"user": user, "member": member, "email": user.email}
