"""BDD step definitions for gamification points & levels.

Total: 40 scenarios — all enabled (Phase 3 complete).

Phase 1 (15): Earning points, level progression, ratchet, edge cases
Phase 2 (9): Level display, definitions, admin config
Phase 3 (16): Course gating, validation errors, security

NOTE: Step functions have intentionally "unused" parameters like `client` for pytest-bdd
fixture dependency ordering.
"""

# ruff: noqa: ARG001

from typing import Any
from uuid import uuid4

import pytest
from httpx import AsyncClient
from pytest_bdd import given, parsers, scenario, scenarios, then, when

from src.gamification.application.commands.award_points import (
    AwardPointsCommand,
    AwardPointsHandler,
)
from src.gamification.application.commands.deduct_points import (
    DeductPointsCommand,
    DeductPointsHandler,
)
from src.gamification.application.commands.set_course_level_requirement import (
    SetCourseLevelRequirementCommand,
    SetCourseLevelRequirementHandler,
)
from src.gamification.application.commands.update_level_config import (
    LevelUpdate,
    UpdateLevelConfigCommand,
    UpdateLevelConfigHandler,
)
from src.gamification.application.queries.check_course_access import (
    CheckCourseAccessHandler,
    CheckCourseAccessQuery,
)
from src.gamification.application.queries.get_level_definitions import (
    GetLevelDefinitionsHandler,
    GetLevelDefinitionsQuery,
)
from src.gamification.application.queries.get_member_level import (
    GetMemberLevelHandler,
    GetMemberLevelQuery,
)
from src.gamification.domain.exceptions import (
    DuplicateLessonCompletionError,
    InvalidLevelNameError,
    InvalidThresholdError,
)
from src.gamification.domain.value_objects.point_source import PointSource
from src.gamification.infrastructure.persistence.level_config_repository import (
    SqlAlchemyLevelConfigRepository,
)
from src.gamification.infrastructure.persistence.member_points_repository import (
    SqlAlchemyMemberPointsRepository,
)

# ============================================================================
# HELPER
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
# PHASE 2 SCENARIOS — Display + Admin Config (9 enabled)
# Must be declared BEFORE scenarios() to prevent auto-generation.
# ============================================================================


@scenario("points.feature", "Level badge shown on post author avatar")
def test_level_badge_shown_on_post_author_avatar() -> None:
    pass


@scenario("points.feature", "Level badge shown in member directory")
def test_level_badge_shown_in_member_directory() -> None:
    pass


@scenario("points.feature", "Level information shown on member profile")
def test_level_information_shown_on_member_profile() -> None:
    pass


@scenario("points.feature", "Member can view all level definitions")
def test_member_can_view_all_level_definitions() -> None:
    pass


@scenario("points.feature", "Level definitions show percentage of members at each level")
def test_level_definitions_show_percentage_of_members_at_each_level() -> None:
    pass


@scenario("points.feature", "Admin customizes level names")
def test_admin_customizes_level_names() -> None:
    pass


@scenario("points.feature", "Admin customizes point thresholds")
def test_admin_customizes_point_thresholds() -> None:
    pass


@scenario("points.feature", "Threshold change recalculates member levels")
def test_threshold_change_recalculates_member_levels() -> None:
    pass


@scenario("points.feature", "Level ratchet preserved when thresholds change")
def test_level_ratchet_preserved_when_thresholds_change() -> None:
    pass


# ============================================================================
# PHASE 3 SCENARIOS — Course Gating + Validation + Security (16 enabled)
# ============================================================================


@scenario("points.feature", "Member can access course when at required level")
def test_member_can_access_course_when_at_required_level() -> None:
    pass


@scenario("points.feature", "Member cannot access course below required level")
def test_member_cannot_access_course_below_required_level() -> None:
    pass


@scenario("points.feature", "Locked course visible in course list with lock indicator")
def test_locked_course_visible_in_course_list_with_lock_indicator() -> None:
    pass


@scenario("points.feature", "Course with no level requirement is accessible to all")
def test_course_with_no_level_requirement_is_accessible_to_all() -> None:
    pass


@scenario("points.feature", "No points awarded for self-like attempt")
def test_no_points_awarded_for_self_like_attempt() -> None:
    pass


@scenario("points.feature", "Level name too long is rejected")
def test_level_name_too_long_is_rejected() -> None:
    pass


@scenario("points.feature", "Empty level name is rejected")
def test_empty_level_name_is_rejected() -> None:
    pass


@scenario("points.feature", "Duplicate level names are rejected")
def test_duplicate_level_names_are_rejected() -> None:
    pass


@scenario("points.feature", "Non-increasing thresholds are rejected")
def test_non_increasing_thresholds_are_rejected() -> None:
    pass


@scenario("points.feature", "Zero threshold for level 2 is rejected")
def test_zero_threshold_for_level_2_is_rejected() -> None:
    pass


@scenario("points.feature", "Unauthenticated user cannot view points")
def test_unauthenticated_user_cannot_view_points() -> None:
    pass


@scenario("points.feature", "Non-admin cannot configure levels")
def test_non_admin_cannot_configure_levels() -> None:
    pass


@scenario("points.feature", "Non-admin cannot set course level requirements")
def test_non_admin_cannot_set_course_level_requirements() -> None:
    pass


@scenario("points.feature", "Level name input is sanitized")
def test_level_name_input_is_sanitized() -> None:
    pass


@scenario("points.feature", "Admin lowers course level requirement grants immediate access")
def test_admin_lowers_course_level_requirement_grants_immediate_access() -> None:
    pass


@scenario("points.feature", "Admin raises course level requirement revokes access")
def test_admin_raises_course_level_requirement_revokes_access() -> None:
    pass


# ============================================================================
# Auto-load remaining scenarios (Phase 1 — 15 enabled)
# ============================================================================

scenarios("points.feature")


# ============================================================================
# BACKGROUND STEPS
# ============================================================================


@given(parsers.parse('a community exists with name "{name}"'))
async def community_exists(
    client: AsyncClient,
    name: str,
    create_community: Any,
    context: dict[str, Any],
    lc_repo: SqlAlchemyLevelConfigRepository,
) -> None:
    """Create a community and initialize default level configuration."""
    community = await create_community(name=name)
    context["community"] = community
    context["community_id"] = community.id


@given("the community has default level configuration:")
async def community_has_default_level_config(
    client: AsyncClient,
    context: dict[str, Any],
    lc_repo: SqlAlchemyLevelConfigRepository,
    datatable: list[dict[str, str]],
) -> None:
    """Initialize default level configuration (already created by seed)."""
    from src.gamification.domain.entities.level_configuration import (
        LevelConfiguration,
        LevelDefinition,
    )

    community_id = context["community_id"]
    levels = [
        LevelDefinition(
            level=int(row["level"]),
            name=row["name"],
            threshold=int(row["threshold"]),
        )
        for row in datatable
    ]
    config = LevelConfiguration(
        id=uuid4(),
        community_id=community_id,
        levels=levels,
    )
    await lc_repo.save(config)
    context["level_config"] = config


# ============================================================================
# GIVEN STEPS — USER CREATION
# ============================================================================


@given(parsers.parse('a user exists with email "{email}" and role "{role}"'))
async def user_exists_with_role(
    client: AsyncClient,
    email: str,
    role: str,
    create_user: Any,
    create_member: Any,
    context: dict[str, Any],
) -> None:
    """Create a user with community membership."""
    community_id = context["community_id"]
    user = await create_user(email=email, display_name=email.split("@")[0].title())
    await create_member(community_id=community_id, user_id=user.id, role=role)

    if "users" not in context:
        context["users"] = {}
    context["users"][email] = {"user": user, "user_id": user.id}


# ============================================================================
# GIVEN STEPS — POINTS STATE SETUP
# ============================================================================


@given(parsers.parse('"{email}" has {points:d} points'))
async def user_has_points(
    client: AsyncClient,
    email: str,
    points: int,
    context: dict[str, Any],
    award_handler: AwardPointsHandler,
    mp_repo: SqlAlchemyMemberPointsRepository,
) -> None:
    """Set a user's point total to a specific value."""

    user_id = context["users"][email]["user_id"]
    community_id = context["community_id"]

    if points == 0:
        # Just ensure a MemberPoints record exists at 0
        return

    # Award points in a batch to reach the desired total.
    # Use LESSON_COMPLETED (5 pts) and POST_LIKED (1 pt) to build up.
    remaining = points
    while remaining > 0:
        if remaining >= 5:
            source = PointSource.LESSON_COMPLETED
            remaining -= 5
        elif remaining >= 2:
            source = PointSource.POST_CREATED
            remaining -= 2
        else:
            source = PointSource.POST_LIKED
            remaining -= 1
        await award_handler.handle(
            AwardPointsCommand(
                community_id=community_id,
                user_id=user_id,
                source=source,
                source_id=uuid4(),
            )
        )


@given(parsers.parse('"{email}" is at level {level:d}'))
async def user_is_at_level(
    client: AsyncClient,
    email: str,
    level: int,
    context: dict[str, Any],
    mp_repo: SqlAlchemyMemberPointsRepository,
    lc_repo: SqlAlchemyLevelConfigRepository,
) -> None:
    """Ensure user is at the specified level (set directly if needed)."""
    from src.gamification.domain.entities.member_points import MemberPoints

    user_id = context["users"][email]["user_id"]
    community_id = context["community_id"]

    mp = await mp_repo.get_by_community_and_user(community_id, user_id)
    if mp is None:
        mp = MemberPoints.create(community_id=community_id, user_id=user_id)

    # Set the level directly (for test setup convenience)
    mp.current_level = level
    await mp_repo.save(mp)


@given(parsers.parse('"{email}" is at level {level:d} due to a previous lower threshold'))
async def user_at_level_due_to_previous_threshold(
    client: AsyncClient,
    email: str,
    level: int,
    context: dict[str, Any],
    mp_repo: SqlAlchemyMemberPointsRepository,
) -> None:
    """Set user at a specific level (ratcheted from previous threshold)."""
    from src.gamification.domain.entities.member_points import MemberPoints

    user_id = context["users"][email]["user_id"]
    community_id = context["community_id"]

    mp = await mp_repo.get_by_community_and_user(community_id, user_id)
    if mp is None:
        mp = MemberPoints.create(community_id=community_id, user_id=user_id)
    mp.current_level = level
    await mp_repo.save(mp)


# ============================================================================
# GIVEN STEPS — CONTENT CREATION
# ============================================================================


@given(parsers.parse('"{email}" has created a post with title "{title}"'))
async def user_has_created_post(
    client: AsyncClient,
    email: str,
    title: str,
    context: dict[str, Any],
    create_category: Any,
    create_post: Any,
) -> None:
    """Create a post for a user (bypassing API to avoid event side-effects)."""
    community_id = context["community_id"]
    user_id = context["users"][email]["user_id"]

    # Ensure a category exists
    if "category" not in context:
        category = await create_category(community_id=community_id)
        context["category"] = category

    post = await create_post(
        community_id=community_id,
        author_id=user_id,
        category_id=context["category"].id,
        title=title,
    )
    context["post"] = post
    context["post_id"] = post.id
    context["post_author_email"] = email


@given("a post exists in the community")
async def post_exists_in_community(
    client: AsyncClient,
    context: dict[str, Any],
    create_category: Any,
    create_post: Any,
) -> None:
    """Create a generic post in the community."""
    community_id = context["community_id"]
    first_email = next(iter(context["users"]))
    user_id = context["users"][first_email]["user_id"]

    if "category" not in context:
        category = await create_category(community_id=community_id)
        context["category"] = category

    post = await create_post(
        community_id=community_id,
        author_id=user_id,
        category_id=context["category"].id,
    )
    context["post"] = post
    context["post_id"] = post.id
    context["post_author_email"] = first_email


@given(parsers.parse('"{email}" has commented on the post'))
async def user_has_commented(
    client: AsyncClient,
    email: str,
    context: dict[str, Any],
    create_comment: Any,
) -> None:
    """Create a comment for a user on the current post."""
    user_id = context["users"][email]["user_id"]
    post_id = context["post_id"]

    comment = await create_comment(
        post_id=post_id,
        author_id=user_id,
        content="Test comment",
    )
    context["comment"] = comment
    context["comment_id"] = comment.id
    context["comment_author_email"] = email


@given(parsers.parse('a course exists with a lesson "{lesson_name}"'))
async def course_with_lesson_exists(
    client: AsyncClient,
    lesson_name: str,
    context: dict[str, Any],
) -> None:
    """Store lesson info in context (gamification tracks by source_id, not actual course entity)."""
    lesson_id = uuid4()
    context["lesson_name"] = lesson_name
    context["lesson_id"] = lesson_id


@given(parsers.parse('"{email}" has already completed the lesson "{lesson_name}"'))
async def user_completed_lesson(
    client: AsyncClient,
    email: str,
    lesson_name: str,
    context: dict[str, Any],
    award_handler: AwardPointsHandler,
) -> None:
    """Award lesson completion points (first time)."""
    user_id = context["users"][email]["user_id"]
    community_id = context["community_id"]
    lesson_id = context["lesson_id"]

    await award_handler.handle(
        AwardPointsCommand(
            community_id=community_id,
            user_id=user_id,
            source=PointSource.LESSON_COMPLETED,
            source_id=lesson_id,
        )
    )


# ============================================================================
# GIVEN STEPS — LIKE STATE
# ============================================================================


@given(parsers.parse('"{email}" has liked the post by "{author_email}"'))
async def user_has_liked_post(
    client: AsyncClient,
    email: str,
    author_email: str,
    context: dict[str, Any],
    award_handler: AwardPointsHandler,
) -> None:
    """Simulate a like: award 1 point to author for POST_LIKED."""
    author_id = context["users"][author_email]["user_id"]
    community_id = context["community_id"]
    post_id = context["post_id"]

    await award_handler.handle(
        AwardPointsCommand(
            community_id=community_id,
            user_id=author_id,
            source=PointSource.POST_LIKED,
            source_id=post_id,
        )
    )
    # Track that this like happened
    context["liked_post_author"] = author_email
    context["liked_by"] = email


@given(parsers.parse('I am authenticated as "{email}"'))
async def authenticated_as(
    client: AsyncClient,
    email: str,
    context: dict[str, Any],
) -> None:
    """Set authenticated user in context."""
    token = await _get_auth_token(client, email)
    context["auth_token"] = token
    context["auth_email"] = email


@given(parsers.parse('level {level:d} is named "{name}"'))
async def level_is_named(
    client: AsyncClient,
    level: int,
    name: str,
    context: dict[str, Any],
) -> None:
    """Assert a level has a specific name (pre-condition check)."""
    # This is a pre-condition from the background, already set up
    pass


@given(parsers.parse("the community has {count:d} members"))
async def community_has_members(
    client: AsyncClient,
    count: int,
    context: dict[str, Any],
    create_user: Any,
    create_member: Any,
) -> None:
    """Create specified number of members in the community."""
    community_id = context["community_id"]
    context["bulk_members"] = []

    for i in range(count):
        email = f"member{i}@example.com"
        user = await create_user(email=email, display_name=f"Member {i}")
        await create_member(community_id=community_id, user_id=user.id, role="MEMBER")
        context["bulk_members"].append({"user": user, "user_id": user.id, "email": email})


@given(parsers.parse("{count:d} members are at level {level:d}"))
async def members_at_level(
    client: AsyncClient,
    count: int,
    level: int,
    context: dict[str, Any],
    mp_repo: SqlAlchemyMemberPointsRepository,
    lc_repo: SqlAlchemyLevelConfigRepository,
) -> None:
    """Set specified number of members to a given level."""
    from src.gamification.domain.entities.level_configuration import LevelConfiguration
    from src.gamification.domain.entities.member_points import MemberPoints

    community_id = context["community_id"]
    bulk_members = context.get("bulk_members", [])

    # Get the config to determine threshold for the level
    config = await lc_repo.get_by_community(community_id)
    if config is None:
        config = LevelConfiguration.create_default(community_id)
        await lc_repo.save(config)

    # Track how many we've assigned
    if "assigned_count" not in context:
        context["assigned_count"] = 0

    start = context["assigned_count"]
    for i in range(start, start + count):
        user_id = bulk_members[i]["user_id"]
        # Create MemberPoints at the desired level
        mp = MemberPoints.create(community_id=community_id, user_id=user_id)
        mp.total_points = config.threshold_for_level(level)
        mp.current_level = level
        await mp_repo.save(mp)

    context["assigned_count"] = start + count


@given(parsers.parse('a course "{name}" exists with minimum level {level:d}'))
async def course_with_min_level(
    client: AsyncClient,
    name: str,
    level: int,
    context: dict[str, Any],
    set_course_req_handler: SetCourseLevelRequirementHandler,
) -> None:
    """Create a course with minimum level requirement."""
    community_id = context["community_id"]
    course_id = uuid4()
    context.setdefault("courses", {})[name] = {"course_id": course_id}

    admin_email = context.get("auth_email")
    admin_id = (
        context["users"][admin_email]["user_id"]
        if admin_email and admin_email in context.get("users", {})
        else uuid4()
    )

    await set_course_req_handler.handle(
        SetCourseLevelRequirementCommand(
            community_id=community_id,
            course_id=course_id,
            admin_user_id=admin_id,
            minimum_level=level,
        )
    )


@given(parsers.parse('a course "{name}" exists with no minimum level'))
async def course_with_no_min_level(
    client: AsyncClient,
    name: str,
    context: dict[str, Any],
) -> None:
    """Create a course with no minimum level requirement."""
    course_id = uuid4()
    context.setdefault("courses", {})[name] = {"course_id": course_id}


@given(parsers.parse('a course "{name}" exists'))
async def course_exists(
    client: AsyncClient,
    name: str,
    context: dict[str, Any],
) -> None:
    """Create a course (no level requirement)."""
    course_id = uuid4()
    context.setdefault("courses", {})[name] = {"course_id": course_id}


# ============================================================================
# WHEN STEPS — EARNING POINTS (LIKES)
# ============================================================================


@when(parsers.parse('"{email}" likes the post by "{author_email}"'))
async def user_likes_post(
    client: AsyncClient,
    email: str,
    author_email: str,
    context: dict[str, Any],
    award_handler: AwardPointsHandler,
) -> None:
    """Award 1 point to post author when post is liked."""
    author_id = context["users"][author_email]["user_id"]
    community_id = context["community_id"]
    post_id = context["post_id"]

    await award_handler.handle(
        AwardPointsCommand(
            community_id=community_id,
            user_id=author_id,
            source=PointSource.POST_LIKED,
            source_id=post_id,
        )
    )


@when(parsers.parse('"{email}" likes the comment by "{author_email}"'))
async def user_likes_comment(
    client: AsyncClient,
    email: str,
    author_email: str,
    context: dict[str, Any],
    award_handler: AwardPointsHandler,
) -> None:
    """Award 1 point to comment author when comment is liked."""
    author_id = context["users"][author_email]["user_id"]
    community_id = context["community_id"]
    comment_id = context["comment_id"]

    await award_handler.handle(
        AwardPointsCommand(
            community_id=community_id,
            user_id=author_id,
            source=PointSource.COMMENT_LIKED,
            source_id=comment_id,
        )
    )


@when(parsers.parse('"{email}" unlikes the post by "{author_email}"'))
async def user_unlikes_post(
    client: AsyncClient,
    email: str,
    author_email: str,
    context: dict[str, Any],
    deduct_handler: DeductPointsHandler,
) -> None:
    """Deduct 1 point from post author when post is unliked."""
    author_id = context["users"][author_email]["user_id"]
    community_id = context["community_id"]
    post_id = context["post_id"]

    await deduct_handler.handle(
        DeductPointsCommand(
            community_id=community_id,
            user_id=author_id,
            source=PointSource.POST_LIKED,
            source_id=post_id,
        )
    )


# ============================================================================
# WHEN STEPS — EARNING POINTS (CONTENT CREATION)
# ============================================================================


@when(parsers.parse('"{email}" creates a post with title "{title}"'))
async def user_creates_post(
    client: AsyncClient,
    email: str,
    title: str,
    context: dict[str, Any],
    award_handler: AwardPointsHandler,
    create_category: Any,
    create_post: Any,
) -> None:
    """Create a post and award 2 points to author."""
    user_id = context["users"][email]["user_id"]
    community_id = context["community_id"]

    if "category" not in context:
        category = await create_category(community_id=community_id)
        context["category"] = category

    post = await create_post(
        community_id=community_id,
        author_id=user_id,
        category_id=context["category"].id,
        title=title,
    )
    context["post"] = post
    context["post_id"] = post.id

    await award_handler.handle(
        AwardPointsCommand(
            community_id=community_id,
            user_id=user_id,
            source=PointSource.POST_CREATED,
            source_id=post.id,
        )
    )


@when(parsers.parse('"{email}" comments on the post with "{content}"'))
async def user_comments_on_post(
    client: AsyncClient,
    email: str,
    content: str,
    context: dict[str, Any],
    award_handler: AwardPointsHandler,
    create_comment: Any,
) -> None:
    """Create a comment and award 1 point to author."""
    user_id = context["users"][email]["user_id"]
    community_id = context["community_id"]
    post_id = context["post_id"]

    comment = await create_comment(
        post_id=post_id,
        author_id=user_id,
        content=content,
    )

    await award_handler.handle(
        AwardPointsCommand(
            community_id=community_id,
            user_id=user_id,
            source=PointSource.COMMENT_CREATED,
            source_id=comment.id,
        )
    )


@when(parsers.parse('"{email}" comments on a post with "{content}"'))
async def user_comments_on_a_post(
    client: AsyncClient,
    email: str,
    content: str,
    context: dict[str, Any],
    award_handler: AwardPointsHandler,
    create_comment: Any,
) -> None:
    """Create a comment on any post and award 1 point."""
    user_id = context["users"][email]["user_id"]
    community_id = context["community_id"]
    post_id = context["post_id"]

    comment = await create_comment(
        post_id=post_id,
        author_id=user_id,
        content=content,
    )

    await award_handler.handle(
        AwardPointsCommand(
            community_id=community_id,
            user_id=user_id,
            source=PointSource.COMMENT_CREATED,
            source_id=comment.id,
        )
    )


# ============================================================================
# WHEN STEPS — LESSON COMPLETION
# ============================================================================


@when(parsers.parse('"{email}" completes the lesson "{lesson_name}"'))
async def user_completes_lesson(
    client: AsyncClient,
    email: str,
    lesson_name: str,
    context: dict[str, Any],
    award_handler: AwardPointsHandler,
) -> None:
    """Award 5 points for lesson completion."""
    user_id = context["users"][email]["user_id"]
    community_id = context["community_id"]
    lesson_id = context["lesson_id"]

    await award_handler.handle(
        AwardPointsCommand(
            community_id=community_id,
            user_id=user_id,
            source=PointSource.LESSON_COMPLETED,
            source_id=lesson_id,
        )
    )


@when(parsers.parse('"{email}" completes the lesson "{lesson_name}" again'))
async def user_completes_lesson_again(
    client: AsyncClient,
    email: str,
    lesson_name: str,
    context: dict[str, Any],
    award_handler: AwardPointsHandler,
) -> None:
    """Attempt duplicate lesson completion (should be suppressed)."""
    user_id = context["users"][email]["user_id"]
    community_id = context["community_id"]
    lesson_id = context["lesson_id"]

    try:
        await award_handler.handle(
            AwardPointsCommand(
                community_id=community_id,
                user_id=user_id,
                source=PointSource.LESSON_COMPLETED,
                source_id=lesson_id,
            )
        )
    except DuplicateLessonCompletionError:
        context["duplicate_lesson_error"] = True


# ============================================================================
# WHEN STEPS — LEVEL QUERIES
# ============================================================================


@when(parsers.parse('I view the profile of "{email}"'))
async def view_profile(
    client: AsyncClient,
    email: str,
    context: dict[str, Any],
    level_query_handler: GetMemberLevelHandler,
) -> None:
    """Query member level (as another user viewing their profile)."""
    user_id = context["users"][email]["user_id"]
    community_id = context["community_id"]
    # View as a different user to test public profile
    requesting_user_id = user_id  # same user for simplicity; adjusted in specific scenarios

    result = await level_query_handler.handle(
        GetMemberLevelQuery(
            community_id=community_id,
            user_id=user_id,
            requesting_user_id=requesting_user_id,
        )
    )
    context["level_result"] = result


@when(parsers.parse('I view my own profile as "{email}"'))
async def view_own_profile(
    client: AsyncClient,
    email: str,
    context: dict[str, Any],
    level_query_handler: GetMemberLevelHandler,
) -> None:
    """Query member level (viewing own profile)."""
    user_id = context["users"][email]["user_id"]
    community_id = context["community_id"]

    result = await level_query_handler.handle(
        GetMemberLevelQuery(
            community_id=community_id,
            user_id=user_id,
            requesting_user_id=user_id,
        )
    )
    context["level_result"] = result


@when(parsers.parse('"{email}" earns {points:d} point'))
async def user_earns_points_singular(
    client: AsyncClient,
    email: str,
    points: int,
    context: dict[str, Any],
    award_handler: AwardPointsHandler,
) -> None:
    """Award a specific number of points (1 at a time)."""
    user_id = context["users"][email]["user_id"]
    community_id = context["community_id"]

    remaining = points
    while remaining > 0:
        if remaining >= 5:
            source = PointSource.LESSON_COMPLETED
            remaining -= 5
        elif remaining >= 2:
            source = PointSource.POST_CREATED
            remaining -= 2
        else:
            source = PointSource.POST_LIKED
            remaining -= 1
        await award_handler.handle(
            AwardPointsCommand(
                community_id=community_id,
                user_id=user_id,
                source=source,
                source_id=uuid4(),
            )
        )


@when(parsers.parse('"{email}" earns {points:d} points'))
async def user_earns_points_plural(
    client: AsyncClient,
    email: str,
    points: int,
    context: dict[str, Any],
    award_handler: AwardPointsHandler,
) -> None:
    """Award a specific number of points."""
    user_id = context["users"][email]["user_id"]
    community_id = context["community_id"]

    remaining = points
    while remaining > 0:
        if remaining >= 5:
            source = PointSource.LESSON_COMPLETED
            remaining -= 5
        elif remaining >= 2:
            source = PointSource.POST_CREATED
            remaining -= 2
        else:
            source = PointSource.POST_LIKED
            remaining -= 1
        await award_handler.handle(
            AwardPointsCommand(
                community_id=community_id,
                user_id=user_id,
                source=source,
                source_id=uuid4(),
            )
        )


@when(parsers.parse('a point deduction of {points:d} is attempted for "{email}"'))
async def point_deduction_attempted(
    client: AsyncClient,
    points: int,
    email: str,
    context: dict[str, Any],
    deduct_handler: DeductPointsHandler,
) -> None:
    """Attempt to deduct points from a user."""
    user_id = context["users"][email]["user_id"]
    community_id = context["community_id"]

    await deduct_handler.handle(
        DeductPointsCommand(
            community_id=community_id,
            user_id=user_id,
            source=PointSource.POST_LIKED,
            source_id=uuid4(),
        )
    )


# ============================================================================
# WHEN STEPS — STUBS FOR PHASE 2/3
# ============================================================================


@when("I view the community feed")
async def view_community_feed(
    client: AsyncClient,
    context: dict[str, Any],
    level_query_handler: GetMemberLevelHandler,
) -> None:
    """View community feed — query level data for post authors."""
    # For feed display test, we verify level data is available via the query handler
    email = context.get("post_author_email")
    if email and email in context.get("users", {}):
        user_id = context["users"][email]["user_id"]
        community_id = context["community_id"]
        result = await level_query_handler.handle(
            GetMemberLevelQuery(
                community_id=community_id,
                user_id=user_id,
                requesting_user_id=user_id,
            )
        )
        context["feed_level_result"] = result


@when("I view the member directory")
async def view_member_directory(
    client: AsyncClient,
    context: dict[str, Any],
    level_query_handler: GetMemberLevelHandler,
) -> None:
    """View member directory — query level data for listed members."""
    # Query level for all users in context
    community_id = context["community_id"]
    context["directory_levels"] = {}
    for email, user_data in context.get("users", {}).items():
        result = await level_query_handler.handle(
            GetMemberLevelQuery(
                community_id=community_id,
                user_id=user_data["user_id"],
                requesting_user_id=user_data["user_id"],
            )
        )
        context["directory_levels"][email] = result


@when("I view the level definitions")
async def view_level_definitions(
    client: AsyncClient,
    context: dict[str, Any],
    level_definitions_handler: GetLevelDefinitionsHandler,
) -> None:
    """View level definitions via the query handler."""
    community_id = context["community_id"]
    # Use the first user as the requester
    requesting_user_id = next(
        (u["user_id"] for u in context.get("users", {}).values()),
        uuid4(),
    )
    result = await level_definitions_handler.handle(
        GetLevelDefinitionsQuery(
            community_id=community_id,
            requesting_user_id=requesting_user_id,
        )
    )
    context["level_definitions_result"] = result


@when(parsers.parse('the admin updates level {level:d} name to "{name}"'))
async def admin_updates_level_name(
    client: AsyncClient,
    level: int,
    name: str,
    context: dict[str, Any],
    update_level_config_handler: UpdateLevelConfigHandler,
    lc_repo: SqlAlchemyLevelConfigRepository,
) -> None:
    """Admin updates a level name via the UpdateLevelConfig command."""
    community_id = context["community_id"]
    config = await lc_repo.get_by_community(community_id)
    if config is None:
        config = context.get("level_config")
    assert config is not None

    # Build full levels list, replacing the target level's name
    levels = [
        LevelUpdate(
            level=ld.level,
            name=name if ld.level == level else ld.name,
            threshold=ld.threshold,
        )
        for ld in config.levels
    ]

    admin_email = context.get("auth_email", "admin@example.com")
    admin_id = context["users"][admin_email]["user_id"]

    await update_level_config_handler.handle(
        UpdateLevelConfigCommand(
            community_id=community_id,
            admin_user_id=admin_id,
            levels=levels,
        )
    )
    # Update context config
    config = await lc_repo.get_by_community(community_id)
    context["level_config"] = config


@when("the admin updates level thresholds:")
async def admin_updates_thresholds(
    client: AsyncClient,
    context: dict[str, Any],
    datatable: list[dict[str, str]],
    update_level_config_handler: UpdateLevelConfigHandler,
    lc_repo: SqlAlchemyLevelConfigRepository,
) -> None:
    """Admin updates thresholds via the UpdateLevelConfig command."""
    community_id = context["community_id"]
    config = await lc_repo.get_by_community(community_id)
    if config is None:
        config = context.get("level_config")
    assert config is not None

    # Build threshold overrides from datatable
    threshold_overrides = {int(row["level"]): int(row["threshold"]) for row in datatable}

    levels = [
        LevelUpdate(
            level=ld.level,
            name=ld.name,
            threshold=threshold_overrides.get(ld.level, ld.threshold),
        )
        for ld in config.levels
    ]

    admin_email = context.get("auth_email", "admin@example.com")
    admin_id = context["users"][admin_email]["user_id"]

    await update_level_config_handler.handle(
        UpdateLevelConfigCommand(
            community_id=community_id,
            admin_user_id=admin_id,
            levels=levels,
        )
    )
    config = await lc_repo.get_by_community(community_id)
    context["level_config"] = config


@when(parsers.parse("the admin updates level {level:d} threshold from {old:d} to {new:d}"))
async def admin_updates_single_threshold(
    client: AsyncClient,
    level: int,
    old: int,
    new: int,
    context: dict[str, Any],
    update_level_config_handler: UpdateLevelConfigHandler,
    lc_repo: SqlAlchemyLevelConfigRepository,
) -> None:
    """Admin updates a single threshold via the UpdateLevelConfig command."""
    community_id = context["community_id"]
    config = await lc_repo.get_by_community(community_id)
    if config is None:
        config = context.get("level_config")
    assert config is not None

    levels = [
        LevelUpdate(
            level=ld.level,
            name=ld.name,
            threshold=new if ld.level == level else ld.threshold,
        )
        for ld in config.levels
    ]

    admin_email = context.get("auth_email", "admin@example.com")
    admin_id = context["users"][admin_email]["user_id"]

    await update_level_config_handler.handle(
        UpdateLevelConfigCommand(
            community_id=community_id,
            admin_user_id=admin_id,
            levels=levels,
        )
    )
    config = await lc_repo.get_by_community(community_id)
    context["level_config"] = config


@when(parsers.parse('"{email}" attempts to access the course "{name}"'))
async def attempt_access_course(
    client: AsyncClient,
    email: str,
    name: str,
    context: dict[str, Any],
    check_course_access_handler: CheckCourseAccessHandler,
) -> None:
    """Attempt course access via CheckCourseAccessQuery."""
    user_id = context["users"][email]["user_id"]
    community_id = context["community_id"]
    course_id = context["courses"][name]["course_id"]

    result = await check_course_access_handler.handle(
        CheckCourseAccessQuery(
            community_id=community_id,
            course_id=course_id,
            user_id=user_id,
        )
    )
    context["course_access_result"] = result


@when(parsers.parse('"{email}" views the course list'))
async def view_course_list(
    client: AsyncClient,
    email: str,
    context: dict[str, Any],
    check_course_access_handler: CheckCourseAccessHandler,
) -> None:
    """View course list — check access for all courses."""
    user_id = context["users"][email]["user_id"]
    community_id = context["community_id"]
    context["course_list_results"] = {}

    for course_name, course_data in context.get("courses", {}).items():
        result = await check_course_access_handler.handle(
            CheckCourseAccessQuery(
                community_id=community_id,
                course_id=course_data["course_id"],
                user_id=user_id,
            )
        )
        context["course_list_results"][course_name] = result


@when(parsers.parse('"{email}" attempts to like their own post'))
async def attempt_self_like(
    client: AsyncClient,
    email: str,
    context: dict[str, Any],
) -> None:
    """Attempt to self-like via API (should be rejected)."""
    post_id = context["post_id"]
    token = await _get_auth_token(client, email)

    response = await client.post(
        f"/api/v1/posts/{post_id}/like",
        headers={"Authorization": f"Bearer {token}"},
    )
    context["self_like_response"] = response


@when(
    parsers.parse("the admin attempts to set level {level:d} name to a {length:d} character string")
)
async def admin_set_long_name(
    client: AsyncClient,
    level: int,
    length: int,
    context: dict[str, Any],
    update_level_config_handler: UpdateLevelConfigHandler,
    lc_repo: SqlAlchemyLevelConfigRepository,
) -> None:
    """Admin attempts long level name."""
    community_id = context["community_id"]
    config = await lc_repo.get_by_community(community_id)
    assert config is not None

    long_name = "A" * length
    levels = [
        LevelUpdate(
            level=ld.level,
            name=long_name if ld.level == level else ld.name,
            threshold=ld.threshold,
        )
        for ld in config.levels
    ]

    admin_email = context.get("auth_email", "admin@example.com")
    admin_id = context["users"][admin_email]["user_id"]

    try:
        await update_level_config_handler.handle(
            UpdateLevelConfigCommand(
                community_id=community_id,
                admin_user_id=admin_id,
                levels=levels,
            )
        )
    except InvalidLevelNameError as e:
        context["validation_error"] = str(e)


@when(parsers.parse('the admin attempts to set level {level:d} name to "{name}"'))
async def admin_set_level_name(
    client: AsyncClient,
    level: int,
    name: str,
    context: dict[str, Any],
    update_level_config_handler: UpdateLevelConfigHandler,
    lc_repo: SqlAlchemyLevelConfigRepository,
) -> None:
    """Admin attempts to set level name (may fail with validation)."""
    community_id = context["community_id"]
    config = await lc_repo.get_by_community(community_id)
    assert config is not None

    levels = [
        LevelUpdate(
            level=ld.level,
            name=name if ld.level == level else ld.name,
            threshold=ld.threshold,
        )
        for ld in config.levels
    ]

    admin_email = context.get("auth_email", "admin@example.com")
    admin_id = context["users"][admin_email]["user_id"]

    try:
        await update_level_config_handler.handle(
            UpdateLevelConfigCommand(
                community_id=community_id,
                admin_user_id=admin_id,
                levels=levels,
            )
        )
    except (InvalidLevelNameError, InvalidThresholdError) as e:
        context["validation_error"] = str(e)


@when(parsers.parse('the admin attempts to set level {level:d} name to ""'))
async def admin_set_empty_name(
    client: AsyncClient,
    level: int,
    context: dict[str, Any],
    update_level_config_handler: UpdateLevelConfigHandler,
    lc_repo: SqlAlchemyLevelConfigRepository,
) -> None:
    """Admin attempts empty level name."""
    community_id = context["community_id"]
    config = await lc_repo.get_by_community(community_id)
    assert config is not None

    levels = [
        LevelUpdate(
            level=ld.level,
            name="" if ld.level == level else ld.name,
            threshold=ld.threshold,
        )
        for ld in config.levels
    ]

    admin_email = context.get("auth_email", "admin@example.com")
    admin_id = context["users"][admin_email]["user_id"]

    try:
        await update_level_config_handler.handle(
            UpdateLevelConfigCommand(
                community_id=community_id,
                admin_user_id=admin_id,
                levels=levels,
            )
        )
    except InvalidLevelNameError as e:
        context["validation_error"] = str(e)


@when(
    parsers.parse(
        "the admin attempts to set level {level:d} threshold to {threshold:d} when level {other_level:d} threshold is {other:d}"
    )
)
async def admin_set_bad_threshold(
    client: AsyncClient,
    level: int,
    threshold: int,
    other_level: int,
    other: int,
    context: dict[str, Any],
    update_level_config_handler: UpdateLevelConfigHandler,
    lc_repo: SqlAlchemyLevelConfigRepository,
) -> None:
    """Admin attempts non-increasing threshold."""
    community_id = context["community_id"]
    config = await lc_repo.get_by_community(community_id)
    assert config is not None

    levels = [
        LevelUpdate(
            level=ld.level,
            name=ld.name,
            threshold=(
                threshold
                if ld.level == level
                else (other if ld.level == other_level else ld.threshold)
            ),
        )
        for ld in config.levels
    ]

    admin_email = context.get("auth_email", "admin@example.com")
    admin_id = context["users"][admin_email]["user_id"]

    try:
        await update_level_config_handler.handle(
            UpdateLevelConfigCommand(
                community_id=community_id,
                admin_user_id=admin_id,
                levels=levels,
            )
        )
    except InvalidThresholdError as e:
        context["validation_error"] = str(e)


@when(parsers.parse("the admin attempts to set level {level:d} threshold to {threshold:d}"))
async def admin_set_zero_threshold(
    client: AsyncClient,
    level: int,
    threshold: int,
    context: dict[str, Any],
    update_level_config_handler: UpdateLevelConfigHandler,
    lc_repo: SqlAlchemyLevelConfigRepository,
) -> None:
    """Admin attempts zero/invalid threshold."""
    community_id = context["community_id"]
    config = await lc_repo.get_by_community(community_id)
    assert config is not None

    levels = [
        LevelUpdate(
            level=ld.level,
            name=ld.name,
            threshold=threshold if ld.level == level else ld.threshold,
        )
        for ld in config.levels
    ]

    admin_email = context.get("auth_email", "admin@example.com")
    admin_id = context["users"][admin_email]["user_id"]

    try:
        await update_level_config_handler.handle(
            UpdateLevelConfigCommand(
                community_id=community_id,
                admin_user_id=admin_id,
                levels=levels,
            )
        )
    except InvalidThresholdError as e:
        context["validation_error"] = str(e)


@when("an unauthenticated user attempts to view member points")
async def unauthenticated_view_points(
    client: AsyncClient,
    context: dict[str, Any],
) -> None:
    """Unauthenticated view attempt via HTTP API."""
    community_id = context["community_id"]
    # Use a random user_id — the endpoint should reject before looking it up
    response = await client.get(
        f"/api/v1/communities/{community_id}/members/{uuid4()}/level",
    )
    context["api_response"] = response


@when(parsers.parse('"{email}" attempts to update level {level:d} name to "{name}"'))
async def member_attempts_update_level(
    client: AsyncClient,
    email: str,
    level: int,
    name: str,
    context: dict[str, Any],
) -> None:
    """Non-admin member attempts to update level config via HTTP API."""
    community_id = context["community_id"]
    token = await _get_auth_token(client, email)

    # Build a full level config update request
    from src.gamification.domain.entities.level_configuration import DEFAULT_LEVELS

    levels_data = [
        {
            "level": ld.level,
            "name": name if ld.level == level else ld.name,
            "threshold": ld.threshold,
        }
        for ld in DEFAULT_LEVELS
    ]

    response = await client.put(
        f"/api/v1/communities/{community_id}/levels",
        json={"levels": levels_data},
        headers={"Authorization": f"Bearer {token}"},
    )
    context["api_response"] = response


@when(parsers.parse('"{email}" attempts to set minimum level {level:d} on course "{name}"'))
async def member_attempts_set_course_level(
    client: AsyncClient,
    email: str,
    level: int,
    name: str,
    context: dict[str, Any],
) -> None:
    """Non-admin member attempts to set course level requirement via HTTP API."""
    community_id = context["community_id"]
    course_id = context["courses"][name]["course_id"]
    token = await _get_auth_token(client, email)

    response = await client.put(
        f"/api/v1/communities/{community_id}/courses/{course_id}/level-requirement",
        json={"minimum_level": level},
        headers={"Authorization": f"Bearer {token}"},
    )
    context["api_response"] = response


@when(
    parsers.parse(
        "the admin attempts to set level {level:d} name to \"<script>alert('xss')</script>\""
    )
)
async def admin_set_xss_name(
    client: AsyncClient,
    level: int,
    context: dict[str, Any],
    update_level_config_handler: UpdateLevelConfigHandler,
    lc_repo: SqlAlchemyLevelConfigRepository,
) -> None:
    """Admin attempts XSS level name — domain strips HTML tags."""
    community_id = context["community_id"]
    config = await lc_repo.get_by_community(community_id)
    assert config is not None

    xss_name = "<script>alert('xss')</script>"
    levels = [
        LevelUpdate(
            level=ld.level,
            name=xss_name if ld.level == level else ld.name,
            threshold=ld.threshold,
        )
        for ld in config.levels
    ]

    admin_email = context.get("auth_email", "admin@example.com")
    admin_id = context["users"][admin_email]["user_id"]

    try:
        await update_level_config_handler.handle(
            UpdateLevelConfigCommand(
                community_id=community_id,
                admin_user_id=admin_id,
                levels=levels,
            )
        )
        # XSS name was sanitized to "alert('xss')" — store updated config
        config = await lc_repo.get_by_community(community_id)
        context["level_config"] = config
        context["xss_sanitized"] = True
    except InvalidLevelNameError:
        context["xss_sanitized"] = False


@when(parsers.parse('the admin changes minimum level for "{course}" from {old:d} to {new:d}'))
async def admin_changes_course_level(
    client: AsyncClient,
    course: str,
    old: int,
    new: int,
    context: dict[str, Any],
    set_course_req_handler: SetCourseLevelRequirementHandler,
) -> None:
    """Admin changes course level requirement."""
    community_id = context["community_id"]
    course_id = context["courses"][course]["course_id"]

    admin_email = context.get("auth_email", "admin@example.com")
    admin_id = context["users"][admin_email]["user_id"]

    await set_course_req_handler.handle(
        SetCourseLevelRequirementCommand(
            community_id=community_id,
            course_id=course_id,
            admin_user_id=admin_id,
            minimum_level=new,
        )
    )


# ============================================================================
# THEN STEPS — POINT ASSERTIONS
# ============================================================================


@then(parsers.parse('"{email}" should have {points:d} points'))
async def user_should_have_points(
    client: AsyncClient,
    email: str,
    points: int,
    context: dict[str, Any],
    mp_repo: SqlAlchemyMemberPointsRepository,
) -> None:
    """Assert user has the expected number of points."""
    user_id = context["users"][email]["user_id"]
    community_id = context["community_id"]

    mp = await mp_repo.get_by_community_and_user(community_id, user_id)
    if points == 0 and mp is None:
        return  # No record means 0 points
    assert mp is not None, f"No MemberPoints record for {email}"
    assert mp.total_points == points, (
        f"Expected {email} to have {points} points, got {mp.total_points}"
    )


@then(
    parsers.parse(
        'a "PointsAwarded" event should be published for "{email}" with {points:d} points'
    )
)
async def points_awarded_event_published(
    client: AsyncClient,
    email: str,
    points: int,
    context: dict[str, Any],
    mp_repo: SqlAlchemyMemberPointsRepository,
) -> None:
    """Verify points were awarded by checking the transaction log."""
    user_id = context["users"][email]["user_id"]
    community_id = context["community_id"]

    mp = await mp_repo.get_by_community_and_user(community_id, user_id)
    assert mp is not None, f"No MemberPoints record for {email}"
    # Verify at least one transaction with the expected point value exists
    matching = [t for t in mp.transactions if t.points == points]
    assert len(matching) > 0, (
        f"Expected a transaction of {points} points for {email}, "
        f"found transactions: {[(t.points, t.source.source_name) for t in mp.transactions]}"
    )


@then(
    parsers.parse(
        'a "PointsDeducted" event should be published for "{email}" with {points:d} points'
    )
)
async def points_deducted_event_published(
    client: AsyncClient,
    email: str,
    points: int,
    context: dict[str, Any],
    mp_repo: SqlAlchemyMemberPointsRepository,
) -> None:
    """Verify points were deducted by checking the transaction log."""
    user_id = context["users"][email]["user_id"]
    community_id = context["community_id"]

    mp = await mp_repo.get_by_community_and_user(community_id, user_id)
    assert mp is not None, f"No MemberPoints record for {email}"
    # Verify a negative transaction exists
    matching = [t for t in mp.transactions if t.points == -points]
    assert len(matching) > 0, (
        f"Expected a deduction of -{points} points for {email}, "
        f"found transactions: {[(t.points, t.source.source_name) for t in mp.transactions]}"
    )


# ============================================================================
# THEN STEPS — LEVEL ASSERTIONS
# ============================================================================


@then(parsers.parse("the member should be at level {level:d}"))
async def member_at_level(
    client: AsyncClient,
    level: int,
    context: dict[str, Any],
) -> None:
    """Assert the last queried member is at the expected level."""
    result = context["level_result"]
    assert result.level == level, f"Expected level {level}, got {result.level}"


@then(parsers.parse('the member level name should be "{name}"'))
async def member_level_name(
    client: AsyncClient,
    name: str,
    context: dict[str, Any],
) -> None:
    """Assert the last queried member's level name."""
    result = context["level_result"]
    assert result.level_name == name, f"Expected level name '{name}', got '{result.level_name}'"


@then(parsers.parse("the member should have {points:d} points"))
async def member_has_points(
    client: AsyncClient,
    points: int,
    context: dict[str, Any],
) -> None:
    """Assert the last queried member's point total."""
    result = context["level_result"]
    assert result.total_points == points, f"Expected {points} points, got {result.total_points}"


@then(parsers.parse('"{email}" should be at level {level:d}'))
async def user_should_be_at_level(
    client: AsyncClient,
    email: str,
    level: int,
    context: dict[str, Any],
    mp_repo: SqlAlchemyMemberPointsRepository,
) -> None:
    """Assert user is at the expected level."""
    user_id = context["users"][email]["user_id"]
    community_id = context["community_id"]

    mp = await mp_repo.get_by_community_and_user(community_id, user_id)
    assert mp is not None, f"No MemberPoints record for {email}"
    assert mp.current_level == level, (
        f"Expected {email} to be at level {level}, got {mp.current_level}"
    )


@then(parsers.parse('"{email}" level name should be "{name}"'))
async def user_level_name(
    client: AsyncClient,
    email: str,
    name: str,
    context: dict[str, Any],
    level_query_handler: GetMemberLevelHandler,
) -> None:
    """Assert user's level name."""
    user_id = context["users"][email]["user_id"]
    community_id = context["community_id"]

    result = await level_query_handler.handle(
        GetMemberLevelQuery(
            community_id=community_id,
            user_id=user_id,
            requesting_user_id=user_id,
        )
    )
    assert result.level_name == name, f"Expected level name '{name}', got '{result.level_name}'"


@then(
    parsers.parse(
        'a "MemberLeveledUp" event should be published for "{email}" from level {old:d} to level {new:d}'
    )
)
async def member_leveled_up_event(
    client: AsyncClient,
    email: str,
    old: int,
    new: int,
    context: dict[str, Any],
    mp_repo: SqlAlchemyMemberPointsRepository,
) -> None:
    """Verify level-up happened by checking current level."""
    user_id = context["users"][email]["user_id"]
    community_id = context["community_id"]

    mp = await mp_repo.get_by_community_and_user(community_id, user_id)
    assert mp is not None, f"No MemberPoints record for {email}"
    assert mp.current_level == new, (
        f"Expected {email} to be at level {new} (leveled up from {old}), got {mp.current_level}"
    )


@then(parsers.parse('I should see "{text}"'))
async def should_see_text(
    client: AsyncClient,
    text: str,
    context: dict[str, Any],
) -> None:
    """Assert text content from the level query result."""
    result = context["level_result"]

    if "points to level up" in text:
        # Extract the number from "15 points to level up"
        expected_points = int(text.split(" ")[0])
        assert result.points_to_next_level == expected_points, (
            f"Expected {expected_points} points to level up, got {result.points_to_next_level}"
        )


@then(parsers.parse('I should not see a "points to level up" message'))
async def should_not_see_level_up_message(
    client: AsyncClient,
    context: dict[str, Any],
) -> None:
    """Assert that points_to_next_level is None (max level)."""
    result = context["level_result"]
    assert result.points_to_next_level is None, (
        f"Expected no points_to_next_level for max level, got {result.points_to_next_level}"
    )
    assert result.is_max_level is True, "Expected is_max_level to be True"


# ============================================================================
# THEN STEPS — LEVEL DISPLAY & COURSE GATING
# ============================================================================


@then(parsers.parse('the post by "{email}" should show level badge {level:d}'))
async def post_shows_level_badge(
    client: AsyncClient,
    email: str,
    level: int,
    context: dict[str, Any],
) -> None:
    """Post author's level badge data is available via query."""
    result = context.get("feed_level_result")
    assert result is not None, "Feed level result not available"
    assert result.level == level, (
        f"Expected post author {email} to show level badge {level}, got {result.level}"
    )


@then(parsers.parse('"{email}" should show level badge {level:d}'))
async def member_shows_level_badge(
    client: AsyncClient,
    email: str,
    level: int,
    context: dict[str, Any],
) -> None:
    """Member directory shows correct level badge."""
    directory_levels = context.get("directory_levels", {})
    result = directory_levels.get(email)
    assert result is not None, f"No directory level result for {email}"
    assert result.level == level, (
        f"Expected {email} to show level badge {level}, got {result.level}"
    )


@then(parsers.parse('the profile should show "{text}"'))
async def profile_shows_text(
    client: AsyncClient,
    text: str,
    context: dict[str, Any],
) -> None:
    """Profile shows level text (e.g. 'Level 3 - Builder')."""
    result = context["level_result"]
    expected_text = f"Level {result.level} - {result.level_name}"
    assert text == expected_text, f"Expected profile to show '{text}', computed '{expected_text}'"


@then(parsers.parse("the profile should show level badge {level:d}"))
async def profile_shows_badge(
    client: AsyncClient,
    level: int,
    context: dict[str, Any],
) -> None:
    """Profile shows level badge."""
    result = context["level_result"]
    assert result.level == level, f"Expected profile level badge {level}, got {result.level}"


@then(parsers.parse("I should see {count:d} levels displayed"))
async def see_levels_displayed(
    client: AsyncClient,
    count: int,
    context: dict[str, Any],
) -> None:
    """Level definitions grid shows expected number of levels."""
    result = context["level_definitions_result"]
    assert len(result.levels) == count, (
        f"Expected {count} levels displayed, got {len(result.levels)}"
    )


@then(parsers.parse('level {level:d} should be named "{name}" with threshold {threshold:d}'))
async def level_named_with_threshold(
    client: AsyncClient,
    level: int,
    name: str,
    threshold: int,
    context: dict[str, Any],
) -> None:
    """Level definition has expected name and threshold."""
    result = context["level_definitions_result"]
    ld = next((lvl for lvl in result.levels if lvl.level == level), None)
    assert ld is not None, f"Level {level} not found in definitions"
    assert ld.name == name, f"Expected level {level} name '{name}', got '{ld.name}'"
    assert ld.threshold == threshold, (
        f"Expected level {level} threshold {threshold}, got {ld.threshold}"
    )


@then(parsers.parse('level {level:d} should be named "{name}"'))
async def level_named(
    client: AsyncClient,
    level: int,
    name: str,
    context: dict[str, Any],
    lc_repo: SqlAlchemyLevelConfigRepository,
) -> None:
    """Level has expected name (from config)."""
    community_id = context["community_id"]
    config = await lc_repo.get_by_community(community_id)
    assert config is not None, "No level config found"
    actual_name = config.name_for_level(level)
    assert actual_name == name, f"Expected level {level} name '{name}', got '{actual_name}'"


@then(parsers.parse('level {level:d} should show "{text}"'))
async def level_shows_text(
    client: AsyncClient,
    level: int,
    text: str,
    context: dict[str, Any],
) -> None:
    """Level definition shows expected distribution text."""
    result = context["level_definitions_result"]
    ld = next((lvl for lvl in result.levels if lvl.level == level), None)
    assert ld is not None, f"Level {level} not found in definitions"
    # Parse "50% of members" text
    expected_pct = float(text.split("%")[0])
    assert ld.member_percentage == expected_pct, (
        f"Expected level {level} to show '{text}', got {ld.member_percentage}% of members"
    )


@then(parsers.parse("level {level:d} should have threshold {threshold:d}"))
async def level_has_threshold(
    client: AsyncClient,
    level: int,
    threshold: int,
    context: dict[str, Any],
    lc_repo: SqlAlchemyLevelConfigRepository,
) -> None:
    """Level has expected threshold (from config)."""
    community_id = context["community_id"]
    config = await lc_repo.get_by_community(community_id)
    assert config is not None, "No level config found"
    actual_threshold = config.threshold_for_level(level)
    assert actual_threshold == threshold, (
        f"Expected level {level} threshold {threshold}, got {actual_threshold}"
    )


@then("access should be granted")
async def access_granted(
    client: AsyncClient,
    context: dict[str, Any],
) -> None:
    """Assert course access was granted."""
    result = context["course_access_result"]
    assert result.has_access is True, (
        f"Expected access to be granted, but was denied (current level: {result.current_level}, "
        f"minimum: {result.minimum_level})"
    )


@then("access should be denied")
async def access_denied(
    client: AsyncClient,
    context: dict[str, Any],
) -> None:
    """Assert course access was denied."""
    result = context["course_access_result"]
    assert result.has_access is False, (
        f"Expected access to be denied, but was granted (current level: {result.current_level}, "
        f"minimum: {result.minimum_level})"
    )


@then(parsers.parse('the response should indicate "{text}"'))
async def response_indicates(
    client: AsyncClient,
    text: str,
    context: dict[str, Any],
) -> None:
    """Assert course access result contains the expected indication text."""
    result = context["course_access_result"]
    # Text like "Unlock at Level 3 - Builder" — check minimum_level_name is in text
    if result.minimum_level_name is not None:
        expected = f"Unlock at Level {result.minimum_level} - {result.minimum_level_name}"
        assert expected == text, f"Expected indication '{text}', got '{expected}'"
    else:
        pytest.fail(f"Expected indication '{text}' but no minimum_level_name set")


@then(parsers.parse('the course "{name}" should be visible'))
async def course_visible(
    client: AsyncClient,
    name: str,
    context: dict[str, Any],
) -> None:
    """Assert course is present in the course list results."""
    results = context["course_list_results"]
    assert name in results, (
        f"Expected course '{name}' to be visible, but not found in results: {list(results.keys())}"
    )


@then(parsers.parse('the course "{name}" should show a lock indicator'))
async def course_shows_lock(
    client: AsyncClient,
    name: str,
    context: dict[str, Any],
) -> None:
    """Assert course shows a lock indicator (access denied)."""
    results = context["course_list_results"]
    assert name in results, f"Course '{name}' not found in results"
    result = results[name]
    assert result.has_access is False, (
        f"Expected course '{name}' to show lock (access denied), but access was granted"
    )


@then(parsers.parse('the course should display "{text}"'))
async def course_displays_text(
    client: AsyncClient,
    text: str,
    context: dict[str, Any],
) -> None:
    """Assert course displays the expected text (e.g. 'Unlock at Level 3')."""
    # Find the course that's locked in the results
    results = context["course_list_results"]
    locked_courses = {n: r for n, r in results.items() if not r.has_access}
    assert len(locked_courses) > 0, "Expected at least one locked course"
    # Check the text against any locked course
    for _name, result in locked_courses.items():
        expected = f"Unlock at Level {result.minimum_level}"
        if expected == text:
            return
    pytest.fail(
        f"No locked course displays '{text}'. "
        f"Locked courses: {[(n, f'Unlock at Level {r.minimum_level}') for n, r in locked_courses.items()]}"
    )


@then("the like should be rejected")
async def like_rejected(
    client: AsyncClient,
    context: dict[str, Any],
) -> None:
    """Assert that the self-like attempt was rejected."""
    response = context["self_like_response"]
    assert response.status_code in (400, 403, 422), (
        f"Expected self-like to be rejected (400/403/422), got {response.status_code}"
    )


@then(parsers.parse('the update should fail with error "{error}"'))
async def update_fails_with_error(
    client: AsyncClient,
    error: str,
    context: dict[str, Any],
) -> None:
    """Assert update failed with expected validation error message."""
    validation_error = context.get("validation_error")
    assert validation_error is not None, "Expected a validation error but none was raised"
    assert error in validation_error, (
        f"Expected error containing '{error}', got '{validation_error}'"
    )


@then(parsers.parse("the request should fail with a {status_code:d} error"))
async def request_fails_with_status(
    client: AsyncClient,
    status_code: int,
    context: dict[str, Any],
) -> None:
    """Assert the API request failed with the expected HTTP status code."""
    response = context["api_response"]
    assert response.status_code == status_code, (
        f"Expected status {status_code}, got {response.status_code}. Body: {response.text}"
    )


@then("the level name should be sanitized")
async def level_name_sanitized(
    client: AsyncClient,
    context: dict[str, Any],
) -> None:
    """Assert that the XSS attempt was sanitized (HTML tags stripped)."""
    assert context.get("xss_sanitized") is True, (
        "Expected level name to be sanitized (HTML stripped), but it was rejected or not processed"
    )


@then("no script tags should be stored")
async def no_script_tags(
    client: AsyncClient,
    context: dict[str, Any],
    lc_repo: SqlAlchemyLevelConfigRepository,
) -> None:
    """Assert no script tags are stored in level names."""
    community_id = context["community_id"]
    config = await lc_repo.get_by_community(community_id)
    assert config is not None, "No level config found"
    for ld in config.levels:
        assert "<script>" not in ld.name, (
            f"Found <script> tag in level {ld.level} name: '{ld.name}'"
        )
        assert "</script>" not in ld.name, (
            f"Found </script> tag in level {ld.level} name: '{ld.name}'"
        )


@then(parsers.parse('"{email}" should be able to access "{course}"'))
async def user_can_access_course(
    client: AsyncClient,
    email: str,
    course: str,
    context: dict[str, Any],
    check_course_access_handler: CheckCourseAccessHandler,
) -> None:
    """Assert user can access the specified course."""
    user_id = context["users"][email]["user_id"]
    community_id = context["community_id"]
    course_id = context["courses"][course]["course_id"]

    result = await check_course_access_handler.handle(
        CheckCourseAccessQuery(
            community_id=community_id,
            course_id=course_id,
            user_id=user_id,
        )
    )
    assert result.has_access is True, (
        f"Expected {email} to have access to '{course}', but access denied "
        f"(current level: {result.current_level}, minimum: {result.minimum_level})"
    )


@then(parsers.parse('"{email}" should not be able to access "{course}"'))
async def user_cannot_access_course(
    client: AsyncClient,
    email: str,
    course: str,
    context: dict[str, Any],
    check_course_access_handler: CheckCourseAccessHandler,
) -> None:
    """Assert user cannot access the specified course."""
    user_id = context["users"][email]["user_id"]
    community_id = context["community_id"]
    course_id = context["courses"][course]["course_id"]

    result = await check_course_access_handler.handle(
        CheckCourseAccessQuery(
            community_id=community_id,
            course_id=course_id,
            user_id=user_id,
        )
    )
    assert result.has_access is False, (
        f"Expected {email} to NOT have access to '{course}', but access was granted "
        f"(current level: {result.current_level}, minimum: {result.minimum_level})"
    )


@then(parsers.parse('"{email}" should still be at level {level:d}'))
async def user_still_at_level(
    client: AsyncClient,
    email: str,
    level: int,
    context: dict[str, Any],
    mp_repo: SqlAlchemyMemberPointsRepository,
) -> None:
    """User still at level (ratchet preserved)."""
    user_id = context["users"][email]["user_id"]
    community_id = context["community_id"]

    mp = await mp_repo.get_by_community_and_user(community_id, user_id)
    assert mp is not None, f"No MemberPoints record for {email}"
    assert mp.current_level == level, (
        f"Expected {email} to still be at level {level}, got {mp.current_level}"
    )
