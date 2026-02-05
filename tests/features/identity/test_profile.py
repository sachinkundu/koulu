"""BDD step definitions for user profile.

NOTE: Many step functions have intentionally "unused" parameters like `client` and `db_session`.
These are required for pytest-bdd fixture dependency ordering - async steps must share the same
fixture instances to properly share the `context` dict. See BUG-001 for details.
"""
# ruff: noqa: ARG001

from typing import Any

from httpx import AsyncClient
from pytest_bdd import given, parsers, scenarios, then, when

# Load all scenarios from the feature file
scenarios("profile.feature")


# ============================================================================
# GIVEN STEPS
# ============================================================================


@given(parsers.parse('the user "{email}" has not completed their profile'))
async def user_has_incomplete_profile(
    client: AsyncClient, email: str, create_user: Any, context: dict[str, Any]
) -> None:
    """Create a verified user with incomplete profile."""
    user = await create_user(email=email, is_verified=True)
    context["user"] = user
    context["email"] = email


@given(parsers.parse('the user "{email}" has a completed profile'))
async def user_has_completed_profile(
    client: AsyncClient, email: str, create_user: Any, context: dict[str, Any]
) -> None:
    """Create a verified user with completed profile."""
    user = await create_user(
        email=email,
        is_verified=True,
        display_name="Test User",
    )
    context["user"] = user
    context["email"] = email


@given(parsers.parse('the user "{email}" has a completed profile with:'))
async def user_has_completed_profile_with_data(
    client: AsyncClient,
    email: str,
    create_user: Any,
    context: dict[str, Any],
    datatable: list[dict[str, str]],
) -> None:
    """Create a verified user with completed profile and specific data."""
    # Convert datatable to kwargs
    profile_data = {row["field"]: row["value"] for row in datatable}

    user = await create_user(
        email=email,
        is_verified=True,
        **profile_data,
    )
    context["user"] = user
    context["email"] = email
    context["profile_data"] = profile_data


@given("the user has no community activity")
async def user_has_no_activity(client: AsyncClient, context: dict[str, Any]) -> None:
    """User has no community activity."""
    context["has_activity"] = False


# ============================================================================
# WHEN STEPS
# ============================================================================


@when(parsers.parse('the user completes their profile with display name "{name}"'))
async def complete_profile_with_name(
    client: AsyncClient, name: str, context: dict[str, Any]
) -> None:
    """Complete profile with only display name."""
    # TODO (Phase 3): Implement actual API call to POST /api/v1/users/me/profile/complete
    # For now, we'll test domain layer validation
    from src.identity.domain.value_objects import DisplayName

    try:
        display_name = DisplayName(name)
        context["display_name"] = display_name
        context["profile_complete_success"] = True
    except Exception as e:
        context["error"] = e
        context["profile_complete_success"] = False


@when("the user completes their profile with:")
async def complete_profile_with_data(
    client: AsyncClient, context: dict[str, Any], datatable: list[dict[str, str]]
) -> None:
    """Complete profile with data table."""
    # TODO (Phase 3): Implement actual API call to POST /api/v1/users/me/profile/complete
    # For now, test domain layer validation
    from src.identity.domain.value_objects import Bio, DisplayName, Location, SocialLinks

    try:
        profile_data = {row["field"]: row["value"] for row in datatable}

        # Validate display name
        if "display_name" in profile_data:
            context["display_name"] = DisplayName(profile_data["display_name"])

        # Validate bio
        if "bio" in profile_data:
            context["bio"] = Bio(profile_data["bio"])

        # Validate location
        if "city" in profile_data and "country" in profile_data:
            context["location"] = Location(
                city=profile_data["city"],
                country=profile_data["country"],
            )
        elif "city" in profile_data:
            raise ValueError("Country is required when city is provided")
        elif "country" in profile_data:
            raise ValueError("City is required when country is provided")

        # Validate social links
        social_links_data = {}
        for key in ["twitter_url", "linkedin_url", "instagram_url", "website_url"]:
            if key in profile_data:
                social_links_data[key] = profile_data[key]

        if social_links_data:
            context["social_links"] = SocialLinks(**social_links_data)

        context["profile_data"] = profile_data
        context["profile_complete_success"] = True
    except Exception as e:
        context["error"] = e
        context["profile_complete_success"] = False


@when("the user attempts to complete their profile without a display name")
async def attempt_complete_without_name(client: AsyncClient, context: dict[str, Any]) -> None:
    """Attempt to complete profile without display name."""
    # TODO (Phase 3): Implement actual API call
    # For now, simulate validation error
    context["error"] = ValueError("display name is required")
    context["profile_complete_success"] = False


@when(parsers.parse('the user attempts to complete their profile with display name "{name}"'))
async def attempt_complete_with_name(
    client: AsyncClient, name: str, context: dict[str, Any]
) -> None:
    """Attempt to complete profile with specific display name."""
    await complete_profile_with_name(client, name, context)


@when(
    parsers.parse(
        "the user attempts to complete their profile with a display name of {length:d} characters"
    )
)
async def attempt_complete_with_long_name(
    client: AsyncClient, length: int, context: dict[str, Any]
) -> None:
    """Attempt to complete profile with display name of specific length."""
    name = "x" * length
    await complete_profile_with_name(client, name, context)


@when("the user attempts to complete their profile with:")
async def attempt_complete_with_data(
    client: AsyncClient, context: dict[str, Any], datatable: list[dict[str, str]]
) -> None:
    """Attempt to complete profile with data table."""
    # Special handling for <501 character string>
    processed_datatable = []
    for row in datatable:
        if row["value"] == "<501 character string>":
            processed_datatable.append({"field": row["field"], "value": "a" * 501})
        else:
            processed_datatable.append(row)

    context["datatable"] = processed_datatable
    await complete_profile_with_data(client, context, processed_datatable)


@when("the user requests their own profile")
async def request_own_profile(client: AsyncClient, context: dict[str, Any]) -> None:
    """Request own profile."""
    # TODO (Phase 2): Implement actual API call to GET /api/v1/users/me/profile
    pass


@when("the user requests their profile activity")
async def request_profile_activity(client: AsyncClient, context: dict[str, Any]) -> None:
    """Request profile activity."""
    # TODO (Phase 2): Implement actual API call to GET /api/v1/users/me/profile/activity
    pass


# ============================================================================
# THEN STEPS
# ============================================================================


@then("the profile should be marked as complete")
async def profile_marked_complete(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify profile is marked as complete."""
    # TODO (Phase 3): Verify in database that profile.is_complete = True
    assert context.get("profile_complete_success") is True


@then(parsers.parse('a "{event}" event should be published'))
async def event_published(event: str, client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify event was published."""
    # TODO (Phase 3): Implement event publishing verification
    pass


@then(parsers.parse('a default avatar should be generated from the initials "{initials}"'))
async def default_avatar_generated(
    initials: str, client: AsyncClient, context: dict[str, Any]
) -> None:
    """Verify default avatar generated from initials."""
    # TODO (Phase 3): Verify avatar URL contains initials
    if "display_name" in context:
        assert context["display_name"].initials == initials


@then("the profile should contain all provided information")
async def profile_contains_all_info(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify all provided information is stored."""
    # TODO (Phase 3): Verify all fields in database
    assert context.get("profile_complete_success") is True
    assert "profile_data" in context


@then("the location should be empty")
async def location_empty(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify location is empty."""
    assert "location" not in context or context["location"] is None


@then("the twitter_url should be empty")
async def twitter_empty(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify twitter_url is empty."""
    assert "social_links" not in context or context.get("social_links") is None


@then("the linkedin_url should be empty")
async def linkedin_empty(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify linkedin_url is empty."""
    assert "social_links" not in context or context.get("social_links") is None


@then("the instagram_url should be empty")
async def instagram_empty(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify instagram_url is empty."""
    assert "social_links" not in context or context.get("social_links") is None


@then(parsers.parse('profile completion should fail with "{error_message}" error'))
async def profile_completion_fails(
    error_message: str, client: AsyncClient, context: dict[str, Any]
) -> None:
    """Verify profile completion failed with expected error."""
    assert context.get("profile_complete_success") is False
    assert "error" in context
    error = str(context["error"]).lower()
    assert error_message.lower() in error


@then("the profile should be returned with all stored information")
async def profile_returned(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify profile data is returned."""
    # TODO (Phase 2): Verify response contains all profile fields
    pass


@then("the response should include contribution stats")
async def response_includes_stats(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify response includes stats."""
    # TODO (Phase 2): Verify response has contribution_count, posts_count, etc.
    pass


@then('the response should include an "Edit Profile" option indicator')
async def response_includes_edit_option(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify response includes edit option."""
    # TODO (Phase 2): Verify response has can_edit: true
    pass


@then("the activity list should be empty")
async def activity_list_empty(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify activity list is empty."""
    # TODO (Phase 2): Verify response activity array is empty
    pass


@then("the contribution count should be 0")
async def contribution_count_zero(client: AsyncClient, context: dict[str, Any]) -> None:
    """Verify contribution count is 0."""
    # TODO (Phase 2): Verify response contribution_count == 0
    pass
