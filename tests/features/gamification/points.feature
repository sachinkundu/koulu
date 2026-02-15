Feature: Points & Levels
  As a community member
  I want to earn points and progress through levels
  So that I'm rewarded for my engagement and can unlock exclusive content

  Background:
    Given a community exists with name "Koulu Community"
    And the community has default level configuration:
      | level | name           | threshold |
      | 1     | Student        | 0         |
      | 2     | Practitioner   | 10        |
      | 3     | Builder        | 30        |
      | 4     | Leader         | 60        |
      | 5     | Mentor         | 100       |
      | 6     | Empire Builder | 150       |
      | 7     | Ruler          | 210       |
      | 8     | Legend         | 280       |
      | 9     | Icon           | 360       |

  # ============================================
  # EARNING POINTS — LIKES RECEIVED
  # ============================================

  @happy_path @points
  Scenario: Member earns a point when their post is liked
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And a user exists with email "bob@example.com" and role "MEMBER"
    And "alice@example.com" has 0 points
    And "alice@example.com" has created a post with title "My first post"
    When "bob@example.com" likes the post by "alice@example.com"
    Then "alice@example.com" should have 1 points
    And a "PointsAwarded" event should be published for "alice@example.com" with 1 points

  @happy_path @points
  Scenario: Member earns a point when their comment is liked
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And a user exists with email "bob@example.com" and role "MEMBER"
    And "alice@example.com" has 0 points
    And a post exists in the community
    And "alice@example.com" has commented on the post
    When "bob@example.com" likes the comment by "alice@example.com"
    Then "alice@example.com" should have 1 points
    And a "PointsAwarded" event should be published for "alice@example.com" with 1 points

  @happy_path @points
  Scenario: Point is deducted when a like is removed
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And a user exists with email "bob@example.com" and role "MEMBER"
    And "alice@example.com" has 5 points
    And "alice@example.com" has created a post with title "Popular post"
    And "bob@example.com" has liked the post by "alice@example.com"
    When "bob@example.com" unlikes the post by "alice@example.com"
    Then "alice@example.com" should have 4 points
    And a "PointsDeducted" event should be published for "alice@example.com" with 1 points

  # ============================================
  # EARNING POINTS — CREATING CONTENT
  # ============================================

  @happy_path @points
  Scenario: Member earns points when creating a post
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And "alice@example.com" has 0 points
    When "alice@example.com" creates a post with title "New discussion"
    Then "alice@example.com" should have 2 points
    And a "PointsAwarded" event should be published for "alice@example.com" with 2 points

  @happy_path @points
  Scenario: Member earns a point when commenting on a post
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And "alice@example.com" has 0 points
    And a post exists in the community
    When "alice@example.com" comments on the post with "Great discussion!"
    Then "alice@example.com" should have 1 points
    And a "PointsAwarded" event should be published for "alice@example.com" with 1 points

  # ============================================
  # EARNING POINTS — LESSON COMPLETION
  # ============================================

  @happy_path @points
  Scenario: Member earns points when completing a lesson
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And "alice@example.com" has 0 points
    And a course exists with a lesson "Introduction to Python"
    When "alice@example.com" completes the lesson "Introduction to Python"
    Then "alice@example.com" should have 5 points
    And a "PointsAwarded" event should be published for "alice@example.com" with 5 points

  @edge_case @points
  Scenario: No duplicate points for completing the same lesson twice
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And "alice@example.com" has 5 points
    And a course exists with a lesson "Introduction to Python"
    And "alice@example.com" has already completed the lesson "Introduction to Python"
    When "alice@example.com" completes the lesson "Introduction to Python" again
    Then "alice@example.com" should have 5 points

  # ============================================
  # LEVEL PROGRESSION
  # ============================================

  @happy_path @levels
  Scenario: New member starts at Level 1
    Given a user exists with email "newbie@example.com" and role "MEMBER"
    When I view the profile of "newbie@example.com"
    Then the member should be at level 1
    And the member level name should be "Student"
    And the member should have 0 points

  @happy_path @levels
  Scenario: Member levels up when reaching point threshold
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And "alice@example.com" has 9 points
    And "alice@example.com" is at level 1
    When "alice@example.com" earns 1 point
    Then "alice@example.com" should be at level 2
    And "alice@example.com" level name should be "Practitioner"
    And a "MemberLeveledUp" event should be published for "alice@example.com" from level 1 to level 2

  @happy_path @levels
  Scenario: Member can skip levels with large point gains
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And "alice@example.com" has 8 points
    And "alice@example.com" is at level 1
    When "alice@example.com" earns 25 points
    Then "alice@example.com" should have 33 points
    And "alice@example.com" should be at level 3
    And "alice@example.com" level name should be "Builder"

  @happy_path @levels
  Scenario: Member sees points needed to reach next level
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And "alice@example.com" has 15 points
    And "alice@example.com" is at level 2
    When I view my own profile as "alice@example.com"
    Then I should see "15 points to level up"

  @edge_case @levels
  Scenario: Level 9 member sees no level-up progress
    Given a user exists with email "legend@example.com" and role "MEMBER"
    And "legend@example.com" has 400 points
    And "legend@example.com" is at level 9
    When I view my own profile as "legend@example.com"
    Then I should not see a "points to level up" message
    And the member should be at level 9
    And the member level name should be "Icon"

  # ============================================
  # LEVEL RATCHET (LEVELS NEVER DECREASE)
  # ============================================

  @edge_case @levels
  Scenario: Level does not decrease when points drop below threshold
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And a user exists with email "bob@example.com" and role "MEMBER"
    And "alice@example.com" has 10 points
    And "alice@example.com" is at level 2
    And "alice@example.com" has created a post with title "Test post"
    And "bob@example.com" has liked the post by "alice@example.com"
    When "bob@example.com" unlikes the post by "alice@example.com"
    Then "alice@example.com" should have 9 points
    And "alice@example.com" should be at level 2

  @edge_case @levels
  Scenario: Points cannot go below zero
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And "alice@example.com" has 0 points
    When a point deduction of 1 is attempted for "alice@example.com"
    Then "alice@example.com" should have 0 points
    And "alice@example.com" should be at level 1

  # ============================================
  # LEVEL BADGE DISPLAY
  # ============================================

  @happy_path @display
  Scenario: Level badge shown on post author avatar
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And "alice@example.com" is at level 3
    And "alice@example.com" has created a post with title "Level 3 post"
    When I view the community feed
    Then the post by "alice@example.com" should show level badge 3

  @happy_path @display
  Scenario: Level badge shown in member directory
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And "alice@example.com" is at level 5
    When I view the member directory
    Then "alice@example.com" should show level badge 5

  @happy_path @display
  Scenario: Level information shown on member profile
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And "alice@example.com" has 45 points
    And "alice@example.com" is at level 3
    When I view the profile of "alice@example.com"
    Then the profile should show "Level 3 - Builder"
    And the profile should show level badge 3

  # ============================================
  # LEVEL DEFINITIONS VIEW
  # ============================================

  @happy_path @display
  Scenario: Member can view all level definitions
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And I am authenticated as "alice@example.com"
    When I view the level definitions
    Then I should see 9 levels displayed
    And level 1 should be named "Student" with threshold 0
    And level 9 should be named "Icon" with threshold 360

  @happy_path @display
  Scenario: Level definitions show percentage of members at each level
    Given the community has 100 members
    And 50 members are at level 1
    And 30 members are at level 2
    And 20 members are at level 3
    When I view the level definitions
    Then level 1 should show "50% of members"
    And level 2 should show "30% of members"
    And level 3 should show "20% of members"

  # ============================================
  # LEVEL-BASED COURSE ACCESS
  # ============================================

  @happy_path @level_gating
  Scenario: Member can access course when at required level
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And "alice@example.com" is at level 3
    And a course "Advanced Python" exists with minimum level 3
    When "alice@example.com" attempts to access the course "Advanced Python"
    Then access should be granted

  @happy_path @level_gating
  Scenario: Member cannot access course below required level
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And "alice@example.com" is at level 2
    And a course "Advanced Python" exists with minimum level 3
    When "alice@example.com" attempts to access the course "Advanced Python"
    Then access should be denied
    And the response should indicate "Unlock at Level 3 - Builder"

  @happy_path @level_gating
  Scenario: Locked course visible in course list with lock indicator
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And "alice@example.com" is at level 1
    And a course "Advanced Python" exists with minimum level 3
    When "alice@example.com" views the course list
    Then the course "Advanced Python" should be visible
    And the course "Advanced Python" should show a lock indicator
    And the course should display "Unlock at Level 3"

  @happy_path @level_gating
  Scenario: Course with no level requirement is accessible to all
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And "alice@example.com" is at level 1
    And a course "Beginner Python" exists with no minimum level
    When "alice@example.com" attempts to access the course "Beginner Python"
    Then access should be granted

  # ============================================
  # ADMIN — LEVEL CONFIGURATION
  # ============================================

  @happy_path @admin
  Scenario: Admin customizes level names
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And I am authenticated as "admin@example.com"
    When the admin updates level 1 name to "Beginner"
    And the admin updates level 9 name to "Grandmaster"
    Then level 1 should be named "Beginner"
    And level 9 should be named "Grandmaster"

  @happy_path @admin
  Scenario: Admin customizes point thresholds
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And I am authenticated as "admin@example.com"
    When the admin updates level thresholds:
      | level | threshold |
      | 2     | 20        |
      | 3     | 50        |
      | 4     | 100       |
      | 5     | 200       |
      | 6     | 350       |
      | 7     | 500       |
      | 8     | 700       |
      | 9     | 1000      |
    Then level 2 should have threshold 20
    And level 9 should have threshold 1000

  @happy_path @admin
  Scenario: Threshold change recalculates member levels
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And a user exists with email "alice@example.com" and role "MEMBER"
    And "alice@example.com" has 25 points
    And "alice@example.com" is at level 2
    And I am authenticated as "admin@example.com"
    When the admin updates level 3 threshold from 30 to 20
    Then "alice@example.com" should be at level 3

  # ============================================
  # VALIDATION ERRORS — POINTS
  # ============================================

  @error @points
  Scenario: No points awarded for self-like attempt
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And "alice@example.com" has 0 points
    And "alice@example.com" has created a post with title "My post"
    When "alice@example.com" attempts to like their own post
    Then the like should be rejected
    And "alice@example.com" should have 0 points

  # ============================================
  # VALIDATION ERRORS — ADMIN CONFIGURATION
  # ============================================

  @error @admin
  Scenario: Level name too long is rejected
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And I am authenticated as "admin@example.com"
    When the admin attempts to set level 1 name to a 31 character string
    Then the update should fail with error "Level name must be 30 characters or less"

  @error @admin
  Scenario: Empty level name is rejected
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And I am authenticated as "admin@example.com"
    When the admin attempts to set level 1 name to ""
    Then the update should fail with error "Level name is required"

  @error @admin
  Scenario: Duplicate level names are rejected
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And I am authenticated as "admin@example.com"
    And level 1 is named "Student"
    When the admin attempts to set level 2 name to "Student"
    Then the update should fail with error "Level name must be unique"

  @error @admin
  Scenario: Non-increasing thresholds are rejected
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And I am authenticated as "admin@example.com"
    When the admin attempts to set level 3 threshold to 5 when level 2 threshold is 10
    Then the update should fail with error "Thresholds must be strictly increasing"

  @error @admin
  Scenario: Zero threshold for level 2 is rejected
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And I am authenticated as "admin@example.com"
    When the admin attempts to set level 2 threshold to 0
    Then the update should fail with error "Level 2 threshold must be at least 1"

  # ============================================
  # SECURITY
  # ============================================

  @security
  Scenario: Unauthenticated user cannot view points
    When an unauthenticated user attempts to view member points
    Then the request should fail with a 401 error

  @security
  Scenario: Non-admin cannot configure levels
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And I am authenticated as "alice@example.com"
    When "alice@example.com" attempts to update level 1 name to "Noob"
    Then the request should fail with a 403 error

  @security
  Scenario: Non-admin cannot set course level requirements
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And I am authenticated as "alice@example.com"
    And a course "Python Basics" exists
    When "alice@example.com" attempts to set minimum level 3 on course "Python Basics"
    Then the request should fail with a 403 error

  @security
  Scenario: Level name input is sanitized
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And I am authenticated as "admin@example.com"
    When the admin attempts to set level 1 name to "<script>alert('xss')</script>"
    Then the level name should be sanitized
    And no script tags should be stored

  # ============================================
  # EDGE CASES
  # ============================================

  @edge_case @points
  Scenario: Multiple point sources accumulate correctly
    Given a user exists with email "alice@example.com" and role "MEMBER"
    And a user exists with email "bob@example.com" and role "MEMBER"
    And "alice@example.com" has 0 points
    When "alice@example.com" creates a post with title "Hello world"
    And "bob@example.com" likes the post by "alice@example.com"
    And "alice@example.com" comments on a post with "Great idea!"
    Then "alice@example.com" should have 4 points

  @edge_case @level_gating
  Scenario: Admin lowers course level requirement grants immediate access
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And a user exists with email "alice@example.com" and role "MEMBER"
    And "alice@example.com" is at level 2
    And a course "Advanced Python" exists with minimum level 5
    And I am authenticated as "admin@example.com"
    When the admin changes minimum level for "Advanced Python" from 5 to 2
    Then "alice@example.com" should be able to access "Advanced Python"

  @edge_case @level_gating
  Scenario: Admin raises course level requirement revokes access
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And a user exists with email "alice@example.com" and role "MEMBER"
    And "alice@example.com" is at level 2
    And a course "Python Basics" exists with minimum level 1
    And I am authenticated as "admin@example.com"
    When the admin changes minimum level for "Python Basics" from 1 to 3
    Then "alice@example.com" should not be able to access "Python Basics"

  @edge_case @admin
  Scenario: Level ratchet preserved when thresholds change
    Given a user exists with email "admin@example.com" and role "ADMIN"
    And a user exists with email "alice@example.com" and role "MEMBER"
    And "alice@example.com" has 25 points
    And "alice@example.com" is at level 3 due to a previous lower threshold
    And I am authenticated as "admin@example.com"
    When the admin updates level 3 threshold from 20 to 50
    Then "alice@example.com" should still be at level 3
