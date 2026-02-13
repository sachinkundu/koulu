"""BDD step definitions for member directory.

Total: 23 scenarios
Phase 1 (6 active): Browse, count, sort, pagination
Phase 2 (11 skipped): Search, filter, sort options, combinations
Phase 3 (6 skipped): Edge cases, security
"""

# ruff: noqa: ARG001

from typing import Any

import pytest
from httpx import AsyncClient
from pytest_bdd import given, parsers, scenario, then, when

# ============================================================================
# PHASE 1 SCENARIOS (6 active)
# ============================================================================


@scenario("directory.feature", "View member directory as a community member")
def test_view_member_directory() -> None:
    pass


@scenario("directory.feature", "Member directory shows correct member count")
def test_member_directory_shows_count() -> None:
    pass


@scenario("directory.feature", "Sort members by most recent")
def test_sort_by_most_recent() -> None:
    pass


@scenario("directory.feature", "Paginated member loading")
def test_paginated_member_loading() -> None:
    pass


@scenario("directory.feature", "Load second page of members")
def test_load_second_page() -> None:
    pass


@scenario("directory.feature", "Load final page of members")
def test_load_final_page() -> None:
    pass


# ============================================================================
# PHASE 2 SCENARIOS (11 skipped — search, filter, sort options)
# ============================================================================


@pytest.mark.skip(reason="Phase 2: Requires search query param")
@scenario("directory.feature", "Search members by name")
def test_search_members_by_name() -> None:
    pass


@pytest.mark.skip(reason="Phase 2: Requires search query param")
@scenario("directory.feature", "Search is case-insensitive")
def test_search_is_case_insensitive() -> None:
    pass


@pytest.mark.skip(reason="Phase 2: Requires search query param")
@scenario("directory.feature", "Search with partial name match")
def test_search_with_partial_name_match() -> None:
    pass


@pytest.mark.skip(reason="Phase 2: Requires role filter param")
@scenario("directory.feature", "Filter members by admin role")
def test_filter_by_admin_role() -> None:
    pass


@pytest.mark.skip(reason="Phase 2: Requires role filter param")
@scenario("directory.feature", "Filter members by moderator role")
def test_filter_by_moderator_role() -> None:
    pass


@pytest.mark.skip(reason="Phase 2: Requires role filter param")
@scenario("directory.feature", "Filter members by member role")
def test_filter_by_member_role() -> None:
    pass


@pytest.mark.skip(reason="Phase 2: Requires alphabetical sort option")
@scenario("directory.feature", "Sort members alphabetically")
def test_sort_alphabetically() -> None:
    pass


@pytest.mark.skip(reason="Phase 2: Requires search + filter combination")
@scenario("directory.feature", "Combine search with role filter")
def test_combine_search_with_role_filter() -> None:
    pass


@pytest.mark.skip(reason="Phase 2: Requires search query param")
@scenario("directory.feature", "Search returns no results")
def test_search_returns_no_results() -> None:
    pass


@pytest.mark.skip(reason="Phase 2: Requires role filter param")
@scenario("directory.feature", "Filter returns no results")
def test_filter_returns_no_results() -> None:
    pass


@pytest.mark.skip(reason="Phase 2: Requires search query param")
@scenario("directory.feature", "Empty search query returns all members")
def test_empty_search_returns_all() -> None:
    pass


# ============================================================================
# PHASE 3 SCENARIOS (6 skipped — edge cases, security)
# ============================================================================


@pytest.mark.skip(reason="Phase 3: Edge case — deactivated members")
@scenario("directory.feature", "Deactivated members are excluded from directory")
def test_deactivated_members_excluded() -> None:
    pass


@pytest.mark.skip(reason="Phase 3: Edge case — incomplete profiles")
@scenario("directory.feature", "Members without completed profiles appear with defaults")
def test_incomplete_profiles_with_defaults() -> None:
    pass


@pytest.mark.skip(reason="Phase 3: Edge case — single member community")
@scenario("directory.feature", "Member directory for community with single member")
def test_single_member_community() -> None:
    pass


@pytest.mark.skip(reason="Phase 3: Security — authentication required")
@scenario("directory.feature", "Unauthenticated user cannot access member directory")
def test_unauthenticated_access() -> None:
    pass


@pytest.mark.skip(reason="Phase 3: Security — membership required")
@scenario("directory.feature", "Non-member cannot access community directory")
def test_non_member_access() -> None:
    pass


@pytest.mark.skip(reason="Phase 3: Security — no private data exposure")
@scenario("directory.feature", "Member directory does not expose private information")
def test_no_private_info_exposed() -> None:
    pass


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


@given("the system is initialized")
async def system_initialized(client: AsyncClient) -> None:
    """System is initialized (no-op, handled by fixtures)."""
    pass


@given(parsers.parse('a community "{name}" exists'))
async def community_exists(
    client: AsyncClient,
    name: str,
    create_community: Any,
    context: dict[str, Any],
) -> None:
    """Create a community."""
    community = await create_community(name=name)
    context["community"] = community
    context["community_id"] = community.id


@given("the following members exist in the community:")
async def members_exist(
    client: AsyncClient,
    create_member_with_profile: Any,
    context: dict[str, Any],
    datatable: list[dict[str, str]],
) -> None:
    """Create members from the BDD datatable."""
    community_id = context["community_id"]
    members: dict[str, Any] = {}

    for row in datatable:
        user, member = await create_member_with_profile(
            community_id=community_id,
            display_name=row["display_name"],
            role=row["role"].upper(),
            bio=row.get("bio"),
            joined_days_ago=int(row["joined_days_ago"]),
        )
        members[row["display_name"]] = {
            "user": user,
            "member": member,
        }

    context["members"] = members


# ============================================================================
# GIVEN STEPS
# ============================================================================


@given("the user is an authenticated member of the community")
async def user_is_authenticated_member(
    client: AsyncClient,
    context: dict[str, Any],
) -> None:
    """Authenticate as one of the existing members."""
    # Use the first member (Alice Admin) for authentication
    members = context["members"]
    first_member_name = next(iter(members))
    user = members[first_member_name]["user"]
    token = await _get_auth_token(client, user.email)
    context["auth_token"] = token


@given(parsers.parse("the community has {count:d} active members"))
async def community_has_n_members(
    client: AsyncClient,
    count: int,
    create_member_with_profile: Any,
    context: dict[str, Any],
) -> None:
    """Create additional members to reach the target count."""
    community_id = context["community_id"]
    existing_count = len(context.get("members", {}))
    additional_needed = count - existing_count

    for i in range(additional_needed):
        await create_member_with_profile(
            community_id=community_id,
            display_name=f"Member {i + 1}",
            role="MEMBER",
            bio=f"Bio of member {i + 1}",
            joined_days_ago=i,
        )


# ============================================================================
# GIVEN STEPS — Phase 2 (search/filter placeholders)
# ============================================================================


@given(parsers.parse('2 additional admin members exist with names containing "Test"'))
async def additional_admin_members_with_test(
    client: AsyncClient,
    create_member_with_profile: Any,
    context: dict[str, Any],
) -> None:
    """Create 2 additional admin members with 'Test' in their name."""
    community_id = context["community_id"]
    for i in range(2):
        await create_member_with_profile(
            community_id=community_id,
            display_name=f"Test Admin {i + 1}",
            role="ADMIN",
            joined_days_ago=i,
        )


@given("no moderators exist in the community")
async def no_moderators(
    client: AsyncClient,
    context: dict[str, Any],
) -> None:
    """Placeholder — in Phase 2, this step will deactivate moderators."""
    pass


# ============================================================================
# GIVEN STEPS — Phase 3 (edge case/security placeholders)
# ============================================================================


@given(parsers.parse('"{name}" has been deactivated'))
async def member_deactivated(
    client: AsyncClient,
    name: str,
    context: dict[str, Any],
) -> None:
    """Placeholder — Phase 3 will implement deactivation."""
    pass


@given(parsers.parse('"{name}" has not completed their profile'))
async def member_incomplete_profile(
    client: AsyncClient,
    name: str,
    context: dict[str, Any],
) -> None:
    """Placeholder — Phase 3 will handle incomplete profiles."""
    pass


@given("the user is the only member of a new community")
async def single_member_community(
    client: AsyncClient,
    context: dict[str, Any],
) -> None:
    """Placeholder — Phase 3 will create a single-member community."""
    pass


@given("the user is not authenticated")
async def user_not_authenticated(client: AsyncClient, context: dict[str, Any]) -> None:
    """Ensure no auth token in context."""
    context.pop("auth_token", None)


@given("the user is authenticated but not a member of the community")
async def user_authenticated_non_member(
    client: AsyncClient,
    context: dict[str, Any],
) -> None:
    """Placeholder — Phase 3 will create a non-member user."""
    pass


# ============================================================================
# WHEN STEPS
# ============================================================================


@when("the user requests the member directory")
async def request_member_directory(
    client: AsyncClient,
    context: dict[str, Any],
) -> None:
    """GET /api/v1/community/members."""
    token = context["auth_token"]
    response = await client.get(
        "/api/v1/community/members",
        headers={"Authorization": f"Bearer {token}"},
    )
    context["response"] = response
    context["response_json"] = response.json()


@when(parsers.parse('the user requests the member directory sorted by "{sort}"'))
async def request_directory_sorted(
    client: AsyncClient,
    sort: str,
    context: dict[str, Any],
) -> None:
    """GET /api/v1/community/members?sort=..."""
    token = context["auth_token"]
    response = await client.get(
        f"/api/v1/community/members?sort={sort}",
        headers={"Authorization": f"Bearer {token}"},
    )
    context["response"] = response
    context["response_json"] = response.json()


@when(parsers.parse("the user requests the first page of the member directory with a limit of {limit:d}"))
async def request_first_page(
    client: AsyncClient,
    limit: int,
    context: dict[str, Any],
) -> None:
    """GET /api/v1/community/members?limit=..."""
    token = context["auth_token"]
    response = await client.get(
        f"/api/v1/community/members?limit={limit}",
        headers={"Authorization": f"Bearer {token}"},
    )
    context["response"] = response
    context["response_json"] = response.json()


@when(parsers.parse("the user requests the second page of the member directory with a limit of {limit:d}"))
async def request_second_page(
    client: AsyncClient,
    limit: int,
    context: dict[str, Any],
) -> None:
    """Request first page, then use cursor for second page."""
    token = context["auth_token"]
    # First page
    first_response = await client.get(
        f"/api/v1/community/members?limit={limit}",
        headers={"Authorization": f"Bearer {token}"},
    )
    first_json = first_response.json()
    cursor = first_json["cursor"]

    # Second page
    response = await client.get(
        f"/api/v1/community/members?limit={limit}&cursor={cursor}",
        headers={"Authorization": f"Bearer {token}"},
    )
    context["response"] = response
    context["response_json"] = response.json()


@when(parsers.parse("the user requests the third page of the member directory with a limit of {limit:d}"))
async def request_third_page(
    client: AsyncClient,
    limit: int,
    context: dict[str, Any],
) -> None:
    """Request first two pages, then use cursor for third page."""
    token = context["auth_token"]

    # First page
    first_response = await client.get(
        f"/api/v1/community/members?limit={limit}",
        headers={"Authorization": f"Bearer {token}"},
    )
    cursor = first_response.json()["cursor"]

    # Second page
    second_response = await client.get(
        f"/api/v1/community/members?limit={limit}&cursor={cursor}",
        headers={"Authorization": f"Bearer {token}"},
    )
    cursor = second_response.json()["cursor"]

    # Third page
    response = await client.get(
        f"/api/v1/community/members?limit={limit}&cursor={cursor}",
        headers={"Authorization": f"Bearer {token}"},
    )
    context["response"] = response
    context["response_json"] = response.json()


# ============================================================================
# WHEN STEPS — Phase 2 (search/filter placeholders)
# ============================================================================


@when(parsers.parse('the user searches the directory for "{search}"'))
async def search_directory(
    client: AsyncClient,
    search: str,
    context: dict[str, Any],
) -> None:
    """Placeholder — Phase 2."""
    context["response_json"] = {"items": [], "total_count": 0}


@when(parsers.parse('the user filters the directory by role "{role}"'))
async def filter_by_role(
    client: AsyncClient,
    role: str,
    context: dict[str, Any],
) -> None:
    """Placeholder — Phase 2."""
    context["response_json"] = {"items": [], "total_count": 0}


@when(parsers.parse('the user searches the directory for "{search}" and filters by role "{role}"'))
async def search_and_filter(
    client: AsyncClient,
    search: str,
    role: str,
    context: dict[str, Any],
) -> None:
    """Placeholder — Phase 2."""
    context["response_json"] = {"items": [], "total_count": 0}


@when("the user requests the member directory for that community")
async def request_directory_for_community(
    client: AsyncClient,
    context: dict[str, Any],
) -> None:
    """Placeholder — Phase 3."""
    context["response"] = None
    context["response_json"] = {}


# ============================================================================
# THEN STEPS
# ============================================================================


@then("the directory should return a list of active members")
async def directory_returns_active_members(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify response contains member items."""
    data = context["response_json"]
    assert context["response"].status_code == 200
    assert len(data["items"]) > 0


@then("each member entry should include display name, avatar URL, role, bio, and join date")
async def member_entry_has_required_fields(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify each member entry has all required fields."""
    items = context["response_json"]["items"]
    for item in items:
        assert "user_id" in item
        assert "display_name" in item
        assert "avatar_url" in item
        assert "role" in item
        assert "bio" in item
        assert "joined_at" in item


@then("the members should be ordered by join date descending by default")
async def members_ordered_by_join_date_desc(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify members are in descending join date order."""
    items = context["response_json"]["items"]
    dates = [item["joined_at"] for item in items]
    assert dates == sorted(dates, reverse=True)


@then(parsers.parse("the total member count should be {count:d}"))
async def total_member_count(count: int, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify total_count field."""
    data = context["response_json"]
    assert data["total_count"] == count


@then(parsers.parse("the directory should return {count:d} members"))
async def directory_returns_count(count: int, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify number of items returned."""
    items = context["response_json"]["items"]
    assert len(items) == count


@then(parsers.parse("the directory should return {count:d} member"))
async def directory_returns_count_singular(count: int, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify number of items returned (singular form)."""
    items = context["response_json"]["items"]
    assert len(items) == count


@then(parsers.parse('the first member in the list should be "{name}"'))
async def first_member_is(name: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify the first member's display name."""
    items = context["response_json"]["items"]
    assert items[0]["display_name"] == name


@then(parsers.parse('the last member in the list should be "{name}"'))
async def last_member_is(name: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify the last member's display name."""
    items = context["response_json"]["items"]
    assert items[-1]["display_name"] == name


@then("the response should indicate there are more members to load")
async def has_more_members(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify has_more is true and cursor is present."""
    data = context["response_json"]
    assert data["has_more"] is True
    assert data["cursor"] is not None


@then("the response should indicate there are no more members to load")
async def no_more_members(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify has_more is false."""
    data = context["response_json"]
    assert data["has_more"] is False


# ============================================================================
# THEN STEPS — Phase 2 (search/filter placeholders)
# ============================================================================


@then(parsers.parse('the result should include "{name}"'))
async def result_includes_member(name: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify a specific member is in results."""
    items = context["response_json"]["items"]
    names = [item["display_name"] for item in items]
    assert name in names


@then(parsers.parse('the results should include "{name1}", "{name2}", and "{name3}"'))
async def results_include_three_members(
    name1: str, name2: str, name3: str, client: AsyncClient, context: dict[str, Any]
) -> None:
    """Verify three specific members are in results."""
    items = context["response_json"]["items"]
    names = [item["display_name"] for item in items]
    assert name1 in names
    assert name2 in names
    assert name3 in names


@then(parsers.parse('all returned members should have the role "{role}"'))
async def all_members_have_role(role: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify all members have the specified role."""
    items = context["response_json"]["items"]
    for item in items:
        assert item["role"] == role


@then("the response should indicate no members were found")
async def no_members_found(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify empty result."""
    data = context["response_json"]
    assert data["total_count"] == 0


@then("the directory should return all active members")
async def returns_all_active_members(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify all members are returned."""
    data = context["response_json"]
    assert len(data["items"]) > 0


# ============================================================================
# THEN STEPS — Phase 3 (edge case/security placeholders)
# ============================================================================


@then(parsers.parse('the results should not include "{name}"'))
async def results_not_include(name: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify a specific member is not in results."""
    items = context["response_json"].get("items", [])
    names = [item["display_name"] for item in items]
    assert name not in names


@then(parsers.parse('the member entry for "{name}" should have a null avatar URL'))
async def member_has_null_avatar(name: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify member has null avatar_url."""
    items = context["response_json"].get("items", [])
    member = next((m for m in items if m["display_name"] == name), None)
    assert member is not None
    assert member["avatar_url"] is None


@then(parsers.parse('the member entry for "{name}" should have an empty bio'))
async def member_has_empty_bio(name: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify member has null/empty bio."""
    items = context["response_json"].get("items", [])
    member = next((m for m in items if m["display_name"] == name), None)
    assert member is not None
    assert member["bio"] is None or member["bio"] == ""


@then("the request should be rejected with an authentication error")
async def rejected_with_auth_error(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify 401 response."""
    response = context.get("response")
    assert response is not None
    assert response.status_code == 401


@then("the request should be rejected with an authorization error")
async def rejected_with_authz_error(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify 403 response."""
    response = context.get("response")
    assert response is not None
    assert response.status_code == 403


@then("no member entry should contain an email address")
async def no_email_in_response(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify no email fields in response."""
    items = context["response_json"].get("items", [])
    for item in items:
        assert "email" not in item


@then("no member entry should contain private settings")
async def no_private_settings_in_response(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify no private settings in response."""
    items = context["response_json"].get("items", [])
    for item in items:
        assert "settings" not in item
        assert "hashed_password" not in item
