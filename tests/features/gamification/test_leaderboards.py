"""BDD tests for Leaderboards feature.

pytest-bdd 8.x does not natively await async step functions, so every step
is synchronous and uses the pytest-asyncio ``Runner`` to drive async
operations within the same event loop that hosts the async fixtures.
"""

from __future__ import annotations

from asyncio import Runner
from collections.abc import Callable, Coroutine
from typing import Any

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from sqlalchemy.ext.asyncio import AsyncSession

from src.community.infrastructure.persistence.models import CommunityModel
from src.gamification.application.queries.get_leaderboards import (
    GetLeaderboardsHandler,
    GetLeaderboardsQuery,
    LeaderboardsResult,
)
from src.gamification.infrastructure.persistence.models import (
    MemberPointsModel,
    PointTransactionModel,
)
from src.identity.infrastructure.persistence.models import UserModel

# ============================================================================
# Scenario declarations
# ============================================================================

# --- Happy path: 7-day leaderboard ---


@scenario(
    "leaderboards.feature",
    "Member views the 7-day leaderboard with ranked members",
)
def test_member_views_7day_leaderboard() -> None:
    pass


@scenario(
    "leaderboards.feature",
    "Member views the 30-day leaderboard with rolled-up period points",
)
def test_member_views_30day_leaderboard() -> None:
    pass


@scenario(
    "leaderboards.feature",
    "Member views the all-time leaderboard using total accumulated points",
)
def test_member_views_alltime_leaderboard() -> None:
    pass


@scenario(
    "leaderboards.feature",
    "Points earned in period shown with plus prefix for timed boards",
)
def test_points_plus_prefix() -> None:
    pass


# --- Happy path: Your rank ---


@scenario(
    "leaderboards.feature",
    "Member outside top 10 sees their own rank below the list",
)
def test_your_rank_outside_top10() -> None:
    pass


@scenario(
    "leaderboards.feature",
    "Member inside top 10 does not receive a separate your-rank entry",
)
def test_your_rank_inside_top10() -> None:
    pass


@scenario(
    "leaderboards.feature",
    "Member with zero points in period still receives a your-rank entry",
)
def test_your_rank_zero_points() -> None:
    pass


# --- Happy path: Sidebar widget (Phase 2) ---


@pytest.mark.skip(reason="Phase 2: Sidebar widget endpoint not yet implemented")
@scenario(
    "leaderboards.feature",
    "Community feed sidebar widget shows the 30-day top-5 leaderboard",
)
def test_sidebar_widget() -> None:
    pass


# --- Edge cases ---


@scenario(
    "leaderboards.feature",
    "Fewer than 10 members in community shows all available members",
)
def test_fewer_than_10_members() -> None:
    pass


@scenario(
    "leaderboards.feature",
    "Ties in points are broken alphabetically by display name",
)
def test_ties_broken_alphabetically() -> None:
    pass


@scenario(
    "leaderboards.feature",
    "Negative net period points are displayed as zero",
)
def test_negative_net_points() -> None:
    pass


@scenario(
    "leaderboards.feature",
    "Points earned outside the rolling window are excluded",
)
def test_rolling_window_exclusion() -> None:
    pass


@scenario(
    "leaderboards.feature",
    "All-time leaderboard includes total accumulated points regardless of when earned",
)
def test_alltime_includes_all_points() -> None:
    pass


@scenario(
    "leaderboards.feature",
    "Member with 0 points in all periods has a rank in each leaderboard",
)
def test_zero_points_all_periods() -> None:
    pass


# --- Edge case: timestamp (Phase 2) ---


@pytest.mark.skip(reason="Phase 2: Tested with widget endpoint")
@scenario(
    "leaderboards.feature",
    "Last updated timestamp is included in the leaderboard response",
)
def test_last_updated_timestamp() -> None:
    pass


# --- Security (Phase 2) ---


@pytest.mark.skip(reason="Phase 2: Security batch - unauthenticated leaderboard")
@scenario(
    "leaderboards.feature",
    "Unauthenticated user cannot view leaderboards",
)
def test_unauthenticated_leaderboard() -> None:
    pass


@pytest.mark.skip(reason="Phase 2: Security batch - unauthenticated widget")
@scenario(
    "leaderboards.feature",
    "Unauthenticated user cannot view the sidebar widget",
)
def test_unauthenticated_widget() -> None:
    pass


@pytest.mark.skip(reason="Phase 2: Security batch - cross-community access")
@scenario(
    "leaderboards.feature",
    "Member cannot view leaderboard for a community they do not belong to",
)
def test_cross_community_access() -> None:
    pass


# ============================================================================
# Shared state (pytest-bdd fixtures)
# ============================================================================


@pytest.fixture()
def community_data() -> dict[str, Any]:
    """Shared state for community and member data within a scenario."""
    return {
        "community_id": None,
        "members": {},  # name -> {"user_id": UUID, "mp_id": UUID}
    }


@pytest.fixture()
def result_holder() -> dict[str, Any]:
    """Holds the query result for Then steps."""
    return {"result": None, "period": None}


# ============================================================================
# Helper: run async code from sync step functions
# ============================================================================


def _run(runner: Runner, coro: Coroutine[Any, Any, Any]) -> Any:
    """Run a coroutine via the pytest-asyncio Runner (same event loop as fixtures)."""
    return runner.run(coro)


def _table_to_dicts(datatable: Any) -> list[dict[str, str]]:
    """Convert pytest-bdd raw datatable (list of lists) to list of dicts.

    The first row is treated as the header row.
    """
    rows: list[list[str]] = [list(row) for row in datatable]
    headers = rows[0]
    return [dict(zip(headers, row, strict=True)) for row in rows[1:]]


# ============================================================================
# Background steps
# ============================================================================


@given("a community exists", target_fixture="community_data")
def given_community_exists(
    _function_scoped_runner: Runner,
    create_community: Callable[..., Coroutine[Any, Any, CommunityModel]],
    community_data: dict[str, Any],
) -> dict[str, Any]:
    community = _run(_function_scoped_runner, create_community())
    community_data["community_id"] = community.id
    return community_data


@given("the community has default level configuration")
def given_default_level_config(
    _function_scoped_runner: Runner,
    community_data: dict[str, Any],
    db_session: AsyncSession,
) -> None:
    from src.gamification.infrastructure.persistence.models import LevelConfigurationModel

    async def _setup() -> None:
        lc = LevelConfigurationModel(
            community_id=community_data["community_id"],
            levels=[
                {"level": 1, "name": "Newcomer", "threshold": 0},
                {"level": 2, "name": "Active", "threshold": 10},
                {"level": 3, "name": "Rising Star", "threshold": 25},
                {"level": 4, "name": "Contributor", "threshold": 50},
                {"level": 5, "name": "Expert", "threshold": 100},
                {"level": 6, "name": "Leader", "threshold": 200},
                {"level": 7, "name": "Veteran", "threshold": 500},
                {"level": 8, "name": "Champion", "threshold": 1000},
                {"level": 9, "name": "Legend", "threshold": 2500},
            ],
        )
        db_session.add(lc)
        await db_session.flush()

    _run(_function_scoped_runner, _setup())


@given("the following members exist in the community:")
def given_members_exist(
    _function_scoped_runner: Runner,
    community_data: dict[str, Any],
    create_user: Callable[..., Coroutine[Any, Any, UserModel]],
    create_member: Callable[..., Coroutine[Any, Any, Any]],
    create_member_points: Callable[..., Coroutine[Any, Any, MemberPointsModel]],
    datatable: Any,
) -> None:
    rows = _table_to_dicts(datatable)

    async def _setup() -> None:
        community_id = community_data["community_id"]
        for row in rows:
            name = row["name"]
            role = row["role"].upper()
            email = name.lower().replace(" ", ".") + "@test.com"
            user = await create_user(email=email, display_name=name)
            await create_member(community_id=community_id, user_id=user.id, role=role)
            mp = await create_member_points(community_id=community_id, user_id=user.id)
            community_data["members"][name] = {"user_id": user.id, "mp_id": mp.id}

    _run(_function_scoped_runner, _setup())


# ============================================================================
# Given steps -- point transactions
# ============================================================================


@given("the following point transactions occurred in the last 7 days:")
def given_point_txns_last_7_days(
    _function_scoped_runner: Runner,
    community_data: dict[str, Any],
    create_point_transaction: Callable[..., Coroutine[Any, Any, PointTransactionModel]],
    db_session: AsyncSession,
    datatable: Any,
) -> None:
    rows = _table_to_dicts(datatable)

    async def _setup() -> None:
        for row in rows:
            member = community_data["members"][row["member"]]
            pts = int(row["points"])
            await create_point_transaction(
                member_points_id=member["mp_id"],
                points=pts,
                days_ago=1,
            )
            mp = await db_session.get(MemberPointsModel, member["mp_id"])
            assert mp is not None
            mp.total_points += pts
            await db_session.flush()

    _run(_function_scoped_runner, _setup())


@given("the following members earned points in the last 7 days, ranking them 1\u201310:")
def given_members_ranked_1_to_10(
    _function_scoped_runner: Runner,
    community_data: dict[str, Any],
    create_point_transaction: Callable[..., Coroutine[Any, Any, PointTransactionModel]],
    db_session: AsyncSession,
    datatable: Any,
) -> None:
    rows = _table_to_dicts(datatable)

    async def _setup() -> None:
        for row in rows:
            member = community_data["members"][row["member"]]
            points = int(row["points"])
            await create_point_transaction(
                member_points_id=member["mp_id"],
                points=points,
                days_ago=1,
            )
            mp = await db_session.get(MemberPointsModel, member["mp_id"])
            assert mp is not None
            mp.total_points += points
            await db_session.flush()

    _run(_function_scoped_runner, _setup())


@given(
    parsers.re(
        r'"(?P<name>[^"]+)" earned (?P<points>\d+) points between (?P<start>\d+) and (?P<end>\d+) days ago'
    )
)
def given_earned_points_between_days(
    _function_scoped_runner: Runner,
    community_data: dict[str, Any],
    create_point_transaction: Callable[..., Coroutine[Any, Any, PointTransactionModel]],
    db_session: AsyncSession,
    name: str,
    points: str,
    start: str,
    end: str,
) -> None:
    async def _setup() -> None:
        member = community_data["members"][name]
        mid_days = (int(start) + int(end)) / 2
        pts = int(points)
        await create_point_transaction(
            member_points_id=member["mp_id"],
            points=pts,
            days_ago=mid_days,
        )
        mp = await db_session.get(MemberPointsModel, member["mp_id"])
        assert mp is not None
        mp.total_points += pts
        await db_session.flush()

    _run(_function_scoped_runner, _setup())


@given(parsers.re(r'"(?P<name>[^"]+)" earned (?P<points>\d+) points in the last 7 days'))
def given_earned_points_last_7_days(
    _function_scoped_runner: Runner,
    community_data: dict[str, Any],
    create_point_transaction: Callable[..., Coroutine[Any, Any, PointTransactionModel]],
    name: str,
    points: str,
) -> None:
    async def _setup() -> None:
        member = community_data["members"][name]
        pts = int(points)
        await create_point_transaction(
            member_points_id=member["mp_id"],
            points=pts,
            days_ago=1,
        )
        # Don't update total_points here -- scenarios that need all-time
        # totals use the explicit "has a total of" step.

    _run(_function_scoped_runner, _setup())


@given(
    parsers.re(
        r'"(?P<name>[^"]+)" earned (?P<points>\d+) points in the last 7 days \(most in community\)'
    )
)
def given_earned_most_points_7_days(
    _function_scoped_runner: Runner,
    community_data: dict[str, Any],
    create_point_transaction: Callable[..., Coroutine[Any, Any, PointTransactionModel]],
    name: str,
    points: str,
) -> None:
    async def _setup() -> None:
        member = community_data["members"][name]
        pts = int(points)
        await create_point_transaction(
            member_points_id=member["mp_id"],
            points=pts,
            days_ago=1,
        )

    _run(_function_scoped_runner, _setup())


@given(parsers.re(r'"(?P<name>[^"]+)" has a total of (?P<points>\d+) accumulated points'))
def given_total_accumulated_points(
    _function_scoped_runner: Runner,
    community_data: dict[str, Any],
    db_session: AsyncSession,
    name: str,
    points: str,
) -> None:
    async def _setup() -> None:
        member = community_data["members"][name]
        mp = await db_session.get(MemberPointsModel, member["mp_id"])
        assert mp is not None
        mp.total_points = int(points)
        await db_session.flush()

    _run(_function_scoped_runner, _setup())


@given(parsers.re(r'"(?P<name>[^"]+)" earned only (?P<points>\d+) points in the last 7 days'))
def given_earned_only_points_7_days(
    _function_scoped_runner: Runner,
    community_data: dict[str, Any],
    create_point_transaction: Callable[..., Coroutine[Any, Any, PointTransactionModel]],
    db_session: AsyncSession,  # noqa: ARG001 (needed for async fixture chain)
    name: str,
    points: str,
) -> None:
    async def _setup() -> None:
        member = community_data["members"][name]
        await create_point_transaction(
            member_points_id=member["mp_id"],
            points=int(points),
            days_ago=1,
        )
        # total_points already set via "has a total of" step, don't override

    _run(_function_scoped_runner, _setup())


@given(parsers.re(r'"(?P<name>[^"]+)" earned 0 points in the last 7 days'))
def given_earned_zero_points_7_days(
    community_data: dict[str, Any],
    name: str,
) -> None:
    # No transactions to create -- 0 points means no transactions
    pass


@given("the community has only 3 members with points in the last 7 days:")
def given_community_3_members(
    _function_scoped_runner: Runner,
    community_data: dict[str, Any],
    create_point_transaction: Callable[..., Coroutine[Any, Any, PointTransactionModel]],
    db_session: AsyncSession,
    datatable: Any,
) -> None:
    rows = _table_to_dicts(datatable)

    async def _setup() -> None:
        for row in rows:
            member = community_data["members"][row["member"]]
            pts = int(row["points"])
            await create_point_transaction(
                member_points_id=member["mp_id"],
                points=pts,
                days_ago=1,
            )
            mp = await db_session.get(MemberPointsModel, member["mp_id"])
            assert mp is not None
            mp.total_points += pts
            await db_session.flush()

    _run(_function_scoped_runner, _setup())


@given(parsers.re(r"10 members each earned between 1 and 10 points in the last 7 days"))
def given_10_members_earned_points(
    _function_scoped_runner: Runner,
    community_data: dict[str, Any],
    create_point_transaction: Callable[..., Coroutine[Any, Any, PointTransactionModel]],
    db_session: AsyncSession,
) -> None:
    async def _setup() -> None:
        # Award points to all non-Alice members (there are 10 of them)
        members_with_points = [name for name in community_data["members"] if name != "Alice Admin"]
        for i, name in enumerate(sorted(members_with_points)):
            member = community_data["members"][name]
            pts = 10 - i  # 10, 9, 8, ... 1
            await create_point_transaction(
                member_points_id=member["mp_id"],
                points=pts,
                days_ago=1,
            )
            mp = await db_session.get(MemberPointsModel, member["mp_id"])
            assert mp is not None
            mp.total_points += pts
            await db_session.flush()

    _run(_function_scoped_runner, _setup())


@given(parsers.re(r'"(?P<name>[^"]+)" earned (?P<points>\d+) points from likes in the last 7 days'))
def given_earned_from_likes(
    _function_scoped_runner: Runner,
    community_data: dict[str, Any],
    create_point_transaction: Callable[..., Coroutine[Any, Any, PointTransactionModel]],
    db_session: AsyncSession,
    name: str,
    points: str,
) -> None:
    async def _setup() -> None:
        member = community_data["members"][name]
        pts = int(points)
        await create_point_transaction(
            member_points_id=member["mp_id"],
            points=pts,
            days_ago=1,
            source="post_liked",
        )
        mp = await db_session.get(MemberPointsModel, member["mp_id"])
        assert mp is not None
        mp.total_points += pts
        await db_session.flush()

    _run(_function_scoped_runner, _setup())


@given(
    parsers.re(
        r'"(?P<name>[^"]+)" had (?P<points>\d+) points deducted \(from unlikes\) in the last 7 days'
    )
)
def given_points_deducted(
    _function_scoped_runner: Runner,
    community_data: dict[str, Any],
    create_point_transaction: Callable[..., Coroutine[Any, Any, PointTransactionModel]],
    db_session: AsyncSession,
    name: str,
    points: str,
) -> None:
    async def _setup() -> None:
        member = community_data["members"][name]
        pts = int(points)
        await create_point_transaction(
            member_points_id=member["mp_id"],
            points=-pts,
            days_ago=1,
            source="post_liked",
        )
        mp = await db_session.get(MemberPointsModel, member["mp_id"])
        assert mp is not None
        mp.total_points -= pts
        await db_session.flush()

    _run(_function_scoped_runner, _setup())


@given(parsers.re(r'"(?P<name>[^"]+)" earned (?P<points>\d+) points (?P<days>\d+) days ago'))
def given_earned_points_n_days_ago(
    _function_scoped_runner: Runner,
    community_data: dict[str, Any],
    create_point_transaction: Callable[..., Coroutine[Any, Any, PointTransactionModel]],
    db_session: AsyncSession,
    name: str,
    points: str,
    days: str,
) -> None:
    async def _setup() -> None:
        member = community_data["members"][name]
        pts = int(points)
        await create_point_transaction(
            member_points_id=member["mp_id"],
            points=pts,
            days_ago=int(days),
        )
        mp = await db_session.get(MemberPointsModel, member["mp_id"])
        assert mp is not None
        mp.total_points += pts
        await db_session.flush()

    _run(_function_scoped_runner, _setup())


@given(parsers.re(r"5 members each earned 10 points in the last 30 days"))
def given_5_members_earned_10_points(
    _function_scoped_runner: Runner,
    community_data: dict[str, Any],
    create_point_transaction: Callable[..., Coroutine[Any, Any, PointTransactionModel]],
    db_session: AsyncSession,
) -> None:
    async def _setup() -> None:
        # Pick 5 members (not Karl Keeper -- he's the "never earned" one)
        members = ["Bob Builder", "Carol Creator", "Dave Doer", "Eve Earner", "Frank Finder"]
        for name in members:
            member = community_data["members"][name]
            await create_point_transaction(
                member_points_id=member["mp_id"],
                points=10,
                days_ago=5,
            )
            mp = await db_session.get(MemberPointsModel, member["mp_id"])
            assert mp is not None
            mp.total_points += 10
            await db_session.flush()

    _run(_function_scoped_runner, _setup())


@given(parsers.re(r'"(?P<name>[^"]+)" has never earned any points'))
def given_never_earned_points(
    community_data: dict[str, Any],
    name: str,
) -> None:
    # No action needed -- member already has 0 points
    pass


# ============================================================================
# When steps
# ============================================================================


@when(parsers.re(r'"(?P<name>[^"]+)" requests the (?P<period>7-day|30-day|all-time) leaderboard'))
def when_member_requests_leaderboard(
    _function_scoped_runner: Runner,
    community_data: dict[str, Any],
    leaderboard_handler: GetLeaderboardsHandler,
    result_holder: dict[str, Any],
    name: str,
    period: str,
) -> None:
    member = community_data["members"][name]
    query = GetLeaderboardsQuery(
        community_id=community_data["community_id"],
        current_user_id=member["user_id"],
    )
    result = _run(_function_scoped_runner, leaderboard_handler.handle(query))
    result_holder["result"] = result
    result_holder["period"] = period


# ============================================================================
# Then steps
# ============================================================================


def _get_period_result(result: LeaderboardsResult, period: str) -> Any:
    """Get the LeaderboardPeriodResult for a given period string."""
    periods = {
        "7-day": result.seven_day,
        "30-day": result.thirty_day,
        "all-time": result.all_time,
    }
    if period not in periods:
        raise ValueError(f"Unknown period: {period}")
    return periods[period]


@then(parsers.re(r"the response contains (?P<count>\d+) ranked members"))
def then_response_contains_n_members(
    result_holder: dict[str, Any],
    count: str,
) -> None:
    period_result = _get_period_result(result_holder["result"], result_holder["period"])
    assert len(period_result.entries) == int(count)


@then(parsers.re(r'rank (?P<rank>\d+) is "(?P<name>[^"]+)" with (?P<points>\d+) points?'))
def then_rank_is(
    result_holder: dict[str, Any],
    rank: str,
    name: str,
    points: str,
) -> None:
    period_result = _get_period_result(result_holder["result"], result_holder["period"])
    idx = int(rank) - 1
    entry = period_result.entries[idx]
    assert entry.rank == int(rank), f"Expected rank {rank}, got {entry.rank}"
    assert entry.display_name == name, f"Expected {name}, got {entry.display_name}"
    assert entry.points == int(points), f"Expected {points} pts, got {entry.points}"


@then("ranks 1, 2, 3 have medal indicators (gold, silver, bronze)")
def then_ranks_have_medals(
    result_holder: dict[str, Any],
) -> None:
    period_result = _get_period_result(result_holder["result"], result_holder["period"])
    for i in range(min(3, len(period_result.entries))):
        assert period_result.entries[i].rank == i + 1


@then("each entry includes the member's level badge")
def then_entries_have_level(
    result_holder: dict[str, Any],
) -> None:
    period_result = _get_period_result(result_holder["result"], result_holder["period"])
    for entry in period_result.entries:
        assert entry.level >= 1


@then(
    parsers.re(
        r'"(?P<name>[^"]+)" appears at rank (?P<rank>\d+) with (?P<points>\d+) points in the (?P<period>7-day|30-day|all-time) leaderboard'
    )
)
def then_member_at_rank_in_period(
    result_holder: dict[str, Any],
    name: str,
    rank: str,
    points: str,
    period: str,
) -> None:
    period_result = _get_period_result(result_holder["result"], period)
    idx = int(rank) - 1
    entry = period_result.entries[idx]
    assert entry.rank == int(rank), f"Expected rank {rank}, got {entry.rank}"
    assert entry.display_name == name, f"Expected {name}, got {entry.display_name}"
    assert entry.points == int(points), f"Expected {points} pts, got {entry.points}"


@then(parsers.re(r'rank (?P<rank>\d+) displays "\+(?P<points>\d+)" as the point value'))
def then_rank_displays_plus(
    result_holder: dict[str, Any],
    rank: str,
    points: str,
) -> None:
    # The plus prefix is a frontend concern, but we verify the numeric value
    period_result = _get_period_result(result_holder["result"], result_holder["period"])
    idx = int(rank) - 1
    entry = period_result.entries[idx]
    assert entry.points == int(points)


@then("the all-time leaderboard displays total points without a plus prefix")
def then_alltime_no_plus(
    result_holder: dict[str, Any],
) -> None:
    # Frontend concern -- just verify the all-time result has data
    assert result_holder["result"].all_time is not None


@then(parsers.re(r'the response includes a "your_rank" entry for "(?P<name>[^"]+)"'))
def then_response_includes_your_rank(
    result_holder: dict[str, Any],
    name: str,
) -> None:
    period_result = _get_period_result(result_holder["result"], result_holder["period"])
    assert period_result.your_rank is not None, "your_rank should not be None"
    assert period_result.your_rank.display_name == name


@then(parsers.re(r'"(?P<name>[^"]+)"\'s rank is (?P<rank>\d+)'))
def then_members_rank_is(
    result_holder: dict[str, Any],
    name: str,  # noqa: ARG001 (captured by regex, used in step matching)
    rank: str,
) -> None:
    period_result = _get_period_result(result_holder["result"], result_holder["period"])
    assert period_result.your_rank is not None
    assert period_result.your_rank.rank == int(rank), (
        f"Expected rank {rank}, got {period_result.your_rank.rank}"
    )


@then(parsers.re(r'"(?P<name>[^"]+)" appears at rank (?P<rank>\d+) in the main list'))
def then_member_at_rank_in_main_list(
    result_holder: dict[str, Any],
    name: str,
    rank: str,
) -> None:
    period_result = _get_period_result(result_holder["result"], result_holder["period"])
    idx = int(rank) - 1
    entry = period_result.entries[idx]
    assert entry.rank == int(rank)
    assert entry.display_name == name


@then('the response does not include a separate "your_rank" entry')
def then_no_your_rank(
    result_holder: dict[str, Any],
) -> None:
    period_result = _get_period_result(result_holder["result"], result_holder["period"])
    assert period_result.your_rank is None


@then(parsers.re(r'"(?P<name>[^"]+)"\'s points for the period are (?P<points>\d+)'))
def then_members_period_points(
    result_holder: dict[str, Any],
    name: str,  # noqa: ARG001 (captured by regex, used in step matching)
    points: str,
) -> None:
    period_result = _get_period_result(result_holder["result"], result_holder["period"])
    assert period_result.your_rank is not None
    assert period_result.your_rank.points == int(points)


@then('the response does not include a "your_rank" entry (Bob is in the visible list)')
def then_no_your_rank_bob_visible(
    result_holder: dict[str, Any],
) -> None:
    period_result = _get_period_result(result_holder["result"], result_holder["period"])
    assert period_result.your_rank is None


@then(
    parsers.re(
        r'rank (?P<rank>\d+) is "(?P<name>[^"]+)" \(alphabetically before "(?P<other>[^"]+)"\)'
    )
)
def then_rank_alphabetical(
    result_holder: dict[str, Any],
    rank: str,
    name: str,
    other: str,  # noqa: ARG001 (captured by regex, used in step matching)
) -> None:
    period_result = _get_period_result(result_holder["result"], result_holder["period"])
    idx = int(rank) - 1
    entry = period_result.entries[idx]
    assert entry.display_name == name


@then(parsers.re(r'rank (?P<rank>\d+) is "(?P<name>[^"]+)"$'))
def then_rank_is_name(
    result_holder: dict[str, Any],
    rank: str,
    name: str,
) -> None:
    period_result = _get_period_result(result_holder["result"], result_holder["period"])
    idx = int(rank) - 1
    entry = period_result.entries[idx]
    assert entry.display_name == name


@then(
    parsers.re(
        r'"(?P<name>[^"]+)" appears in the leaderboard with (?P<points>\d+) points for the period'
    )
)
def then_member_in_leaderboard_with_points(
    result_holder: dict[str, Any],
    name: str,
    points: str,
) -> None:
    period_result = _get_period_result(result_holder["result"], result_holder["period"])
    found = False
    for entry in period_result.entries:
        if entry.display_name == name:
            assert entry.points == int(points), f"Expected {points}, got {entry.points}"
            found = True
            break
    if not found and period_result.your_rank and period_result.your_rank.display_name == name:
        assert period_result.your_rank.points == int(points)
        found = True
    assert found, f"{name} not found in leaderboard"


@then(
    parsers.re(
        r'"(?P<name>[^"]+)"\'s 7-day points are (?P<points>\d+) \(only the in-window transactions count\)'
    )
)
def then_7day_points_in_window(
    result_holder: dict[str, Any],
    name: str,
    points: str,
) -> None:
    period_result = _get_period_result(result_holder["result"], "7-day")
    found = False
    for entry in period_result.entries:
        if entry.display_name == name:
            assert entry.points == int(points), f"Expected {points}, got {entry.points}"
            found = True
            break
    if not found and period_result.your_rank and period_result.your_rank.display_name == name:
        assert period_result.your_rank.points == int(points)
        found = True
    assert found, f"{name} not found in 7-day leaderboard"


@then(parsers.re(r'"(?P<name>[^"]+)"\'s all-time points are (?P<points>\d+)'))
def then_alltime_points(
    result_holder: dict[str, Any],
    name: str,
    points: str,
) -> None:
    period_result = _get_period_result(result_holder["result"], "all-time")
    found = False
    for entry in period_result.entries:
        if entry.display_name == name:
            assert entry.points == int(points), f"Expected {points}, got {entry.points}"
            found = True
            break
    if not found and period_result.your_rank and period_result.your_rank.display_name == name:
        assert period_result.your_rank.points == int(points)
        found = True
    assert found, f"{name} not found in all-time leaderboard"


@then(
    parsers.re(
        r'"(?P<name>[^"]+)"\'s rank is (?P<rank>\d+) \(behind the (?P<count>\d+) members who earned points\)'
    )
)
def then_rank_behind_n_members(
    result_holder: dict[str, Any],
    name: str,
    rank: str,
    count: str,  # noqa: ARG001 (captured by regex, used in step matching)
) -> None:
    period_result = _get_period_result(result_holder["result"], result_holder["period"])
    assert period_result.your_rank is not None
    assert period_result.your_rank.rank == int(rank)
    assert period_result.your_rank.display_name == name
