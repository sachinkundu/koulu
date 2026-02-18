Feature: Leaderboards
  As a community member
  I want to see ranked leaderboards of the most active members
  So that I can track my standing and discover top contributors

  Background:
    Given a community exists
    And the community has default level configuration
    And the following members exist in the community:
      | name          | role   |
      | Alice Admin   | admin  |
      | Bob Builder   | member |
      | Carol Creator | member |
      | Dave Doer     | member |
      | Eve Earner    | member |
      | Frank Finder  | member |
      | Grace Giver   | member |
      | Hank Helper   | member |
      | Iris Igniter  | member |
      | Jack Joiner   | member |
      | Karl Keeper   | member |

  # === HAPPY PATH — 7-DAY LEADERBOARD ===

  @happy_path
  Scenario: Member views the 7-day leaderboard with ranked members
    Given the following point transactions occurred in the last 7 days:
      | member        | points |
      | Bob Builder   | 15     |
      | Carol Creator | 12     |
      | Dave Doer     | 9      |
      | Eve Earner    | 7      |
      | Frank Finder  | 6      |
      | Grace Giver   | 5      |
      | Hank Helper   | 4      |
      | Iris Igniter  | 3      |
      | Jack Joiner   | 2      |
      | Karl Keeper   | 1      |
    When "Alice Admin" requests the 7-day leaderboard
    Then the response contains 10 ranked members
    And rank 1 is "Bob Builder" with 15 points
    And rank 2 is "Carol Creator" with 12 points
    And rank 3 is "Dave Doer" with 9 points
    And rank 10 is "Karl Keeper" with 1 point
    And ranks 1, 2, 3 have medal indicators (gold, silver, bronze)
    And each entry includes the member's level badge

  @happy_path
  Scenario: Member views the 30-day leaderboard with rolled-up period points
    Given "Bob Builder" earned 20 points between 8 and 30 days ago
    And "Bob Builder" earned 10 points in the last 7 days
    And "Carol Creator" earned 25 points in the last 7 days
    When "Alice Admin" requests the 30-day leaderboard
    Then "Bob Builder" appears at rank 1 with 30 points in the 30-day leaderboard
    And "Carol Creator" appears at rank 2 with 25 points in the 30-day leaderboard

  @happy_path
  Scenario: Member views the all-time leaderboard using total accumulated points
    Given "Bob Builder" has a total of 200 accumulated points
    And "Bob Builder" earned only 2 points in the last 7 days
    And "Carol Creator" has a total of 50 accumulated points
    And "Carol Creator" earned 40 points in the last 7 days
    When "Alice Admin" requests the all-time leaderboard
    Then "Bob Builder" appears at rank 1 with 200 points in the all-time leaderboard
    And "Carol Creator" appears at rank 2 with 50 points in the all-time leaderboard

  @happy_path
  Scenario: Points earned in period shown with plus prefix for timed boards
    Given "Bob Builder" earned 15 points in the last 7 days
    When "Alice Admin" requests the 7-day leaderboard
    Then rank 1 displays "+15" as the point value
    And the all-time leaderboard displays total points without a plus prefix

  # === HAPPY PATH — YOUR RANK ===

  @happy_path
  Scenario: Member outside top 10 sees their own rank below the list
    Given the following members earned points in the last 7 days, ranking them 1–10:
      | member        | points |
      | Bob Builder   | 15     |
      | Carol Creator | 12     |
      | Dave Doer     | 9      |
      | Eve Earner    | 7      |
      | Frank Finder  | 6      |
      | Grace Giver   | 5      |
      | Hank Helper   | 4      |
      | Iris Igniter  | 3      |
      | Jack Joiner   | 2      |
      | Karl Keeper   | 1      |
    And "Alice Admin" earned 0 points in the last 7 days
    When "Alice Admin" requests the 7-day leaderboard
    Then the response includes a "your_rank" entry for "Alice Admin"
    And "Alice Admin"'s rank is 11

  @happy_path
  Scenario: Member inside top 10 does not receive a separate your-rank entry
    Given "Alice Admin" earned 20 points in the last 7 days (most in community)
    When "Alice Admin" requests the 7-day leaderboard
    Then "Alice Admin" appears at rank 1 in the main list
    And the response does not include a separate "your_rank" entry

  @happy_path
  Scenario: Member with zero points in period still receives a your-rank entry
    Given 10 members each earned between 1 and 10 points in the last 7 days
    And "Alice Admin" earned 0 points in the last 7 days
    When "Alice Admin" requests the 7-day leaderboard
    Then the response includes a "your_rank" entry for "Alice Admin"
    And "Alice Admin"'s rank is 11
    And "Alice Admin"'s points for the period are 0

  # === HAPPY PATH — SIDEBAR WIDGET ===

  @happy_path
  Scenario: Community feed sidebar widget shows the 30-day top-5 leaderboard
    Given the following members earned points in the last 30 days:
      | member        | points |
      | Bob Builder   | 60     |
      | Carol Creator | 45     |
      | Dave Doer     | 30     |
      | Eve Earner    | 20     |
      | Frank Finder  | 10     |
      | Grace Giver   | 5      |
    When "Alice Admin" requests the sidebar leaderboard widget
    Then the widget contains exactly 5 entries
    And rank 1 in the widget is "Bob Builder" with 60 points
    And rank 5 in the widget is "Frank Finder" with 10 points
    And the widget does not include a "your_rank" row
    And the widget includes a link to the leaderboards page

  # === EDGE CASES ===

  @edge_case
  Scenario: Fewer than 10 members in community shows all available members
    Given the community has only 3 members with points in the last 7 days:
      | member        | points |
      | Bob Builder   | 10     |
      | Carol Creator | 7      |
      | Dave Doer     | 3      |
    When "Bob Builder" requests the 7-day leaderboard
    Then the response contains 10 ranked members
    And the response does not include a "your_rank" entry (Bob is in the visible list)

  @edge_case
  Scenario: Ties in points are broken alphabetically by display name
    Given "Carol Creator" earned 10 points in the last 7 days
    And "Bob Builder" earned 10 points in the last 7 days
    When "Alice Admin" requests the 7-day leaderboard
    Then rank 1 is "Bob Builder" (alphabetically before "Carol Creator")
    And rank 2 is "Carol Creator"

  @edge_case
  Scenario: Negative net period points are displayed as zero
    Given "Bob Builder" earned 3 points from likes in the last 7 days
    And "Bob Builder" had 5 points deducted (from unlikes) in the last 7 days
    When "Alice Admin" requests the 7-day leaderboard
    Then "Bob Builder" appears in the leaderboard with 0 points for the period

  @edge_case
  Scenario: Points earned outside the rolling window are excluded
    Given "Bob Builder" earned 50 points 8 days ago
    And "Bob Builder" earned 5 points 6 days ago
    When "Alice Admin" requests the 7-day leaderboard
    Then "Bob Builder"'s 7-day points are 5 (only the in-window transactions count)

  @edge_case
  Scenario: All-time leaderboard includes total accumulated points regardless of when earned
    Given "Bob Builder" earned 30 points 60 days ago
    And "Bob Builder" earned 10 points 3 days ago
    When "Alice Admin" requests the all-time leaderboard
    Then "Bob Builder"'s all-time points are 40

  @edge_case
  Scenario: Member with 0 points in all periods has a rank in each leaderboard
    Given 5 members each earned 10 points in the last 30 days
    And "Karl Keeper" has never earned any points
    When "Karl Keeper" requests the 7-day leaderboard
    Then the response includes a "your_rank" entry for "Karl Keeper"
    And "Karl Keeper"'s rank is 11 (behind the 10 members who earned points)
    And "Karl Keeper"'s points for the period are 0

  @edge_case
  Scenario: Last updated timestamp is included in the leaderboard response
    When "Alice Admin" requests the 7-day leaderboard
    Then the response includes a "last_updated" timestamp

  # === SECURITY ===

  @security
  Scenario: Unauthenticated user cannot view leaderboards
    When an unauthenticated request is made to the leaderboard endpoint
    Then the response status is 401

  @security
  Scenario: Unauthenticated user cannot view the sidebar widget
    When an unauthenticated request is made to the sidebar widget endpoint
    Then the response status is 401

  @security
  Scenario: Member cannot view leaderboard for a community they do not belong to
    Given a second community exists with its own members
    When "Alice Admin" requests the leaderboard for the second community
    Then the response status is 403
