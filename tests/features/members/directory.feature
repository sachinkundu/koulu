Feature: Member Directory
  As a community member
  I want to browse, search, and filter the member directory
  So that I can discover and connect with other community members

  Background:
    Given the system is initialized
    And a community "Test Community" exists
    And the following members exist in the community:
      | display_name    | role      | bio                          | joined_days_ago |
      | Alice Admin     | admin     | Community founder and coach  | 90              |
      | Bob Moderator   | moderator | Helping the community grow   | 60              |
      | Charlie Member  | member    | Excited to learn             | 30              |
      | Diana Member    | member    | New here, hello!             | 7               |
      | Eve Member      | member    | Passionate about coding      | 1               |

  # === HAPPY PATH ===

  @happy_path
  Scenario: View member directory as a community member
    Given the user is an authenticated member of the community
    When the user requests the member directory
    Then the directory should return a list of active members
    And each member entry should include display name, avatar URL, role, bio, and join date
    And the members should be ordered by join date descending by default

  @happy_path
  Scenario: Member directory shows correct member count
    Given the user is an authenticated member of the community
    When the user requests the member directory
    Then the total member count should be 5

  @happy_path
  Scenario: Search members by name
    Given the user is an authenticated member of the community
    When the user searches the directory for "Alice"
    Then the directory should return 1 member
    And the result should include "Alice Admin"

  @happy_path
  Scenario: Search is case-insensitive
    Given the user is an authenticated member of the community
    When the user searches the directory for "alice"
    Then the directory should return 1 member
    And the result should include "Alice Admin"

  @happy_path
  Scenario: Search with partial name match
    Given the user is an authenticated member of the community
    When the user searches the directory for "Mem"
    Then the directory should return 3 members
    And the results should include "Charlie Member", "Diana Member", and "Eve Member"

  @happy_path
  Scenario: Filter members by admin role
    Given the user is an authenticated member of the community
    When the user filters the directory by role "admin"
    Then the directory should return 1 member
    And the result should include "Alice Admin"

  @happy_path
  Scenario: Filter members by moderator role
    Given the user is an authenticated member of the community
    When the user filters the directory by role "moderator"
    Then the directory should return 1 member
    And the result should include "Bob Moderator"

  @happy_path
  Scenario: Filter members by member role
    Given the user is an authenticated member of the community
    When the user filters the directory by role "member"
    Then the directory should return 3 members

  @happy_path
  Scenario: Sort members alphabetically
    Given the user is an authenticated member of the community
    When the user requests the member directory sorted by "alphabetical"
    Then the first member in the list should be "Alice Admin"
    And the last member in the list should be "Eve Member"

  @happy_path
  Scenario: Sort members by most recent
    Given the user is an authenticated member of the community
    When the user requests the member directory sorted by "most_recent"
    Then the first member in the list should be "Eve Member"
    And the last member in the list should be "Alice Admin"

  @happy_path
  Scenario: Combine search with role filter
    Given the user is an authenticated member of the community
    And 2 additional admin members exist with names containing "Test"
    When the user searches the directory for "Test" and filters by role "admin"
    Then the directory should return 2 members
    And all returned members should have the role "admin"

  @happy_path
  Scenario: Paginated member loading
    Given the user is an authenticated member of the community
    And the community has 45 active members
    When the user requests the first page of the member directory with a limit of 20
    Then the directory should return 20 members
    And the response should indicate there are more members to load

  @happy_path
  Scenario: Load second page of members
    Given the user is an authenticated member of the community
    And the community has 45 active members
    When the user requests the second page of the member directory with a limit of 20
    Then the directory should return 20 members
    And the response should indicate there are more members to load

  @happy_path
  Scenario: Load final page of members
    Given the user is an authenticated member of the community
    And the community has 45 active members
    When the user requests the third page of the member directory with a limit of 20
    Then the directory should return 5 members
    And the response should indicate there are no more members to load

  # === VALIDATION ERRORS ===

  @error
  Scenario: Search returns no results
    Given the user is an authenticated member of the community
    When the user searches the directory for "NonexistentPerson"
    Then the directory should return 0 members
    And the response should indicate no members were found

  @error
  Scenario: Filter returns no results
    Given the user is an authenticated member of the community
    And no moderators exist in the community
    When the user filters the directory by role "moderator"
    Then the directory should return 0 members

  # === EDGE CASES ===

  @edge_case
  Scenario: Deactivated members are excluded from directory
    Given the user is an authenticated member of the community
    And "Charlie Member" has been deactivated
    When the user requests the member directory
    Then the directory should return 4 members
    And the results should not include "Charlie Member"

  @edge_case
  Scenario: Members without completed profiles appear with defaults
    Given the user is an authenticated member of the community
    And "Eve Member" has not completed their profile
    When the user requests the member directory
    Then the member entry for "Eve Member" should have a null avatar URL
    And the member entry for "Eve Member" should have an empty bio

  @edge_case
  Scenario: Empty search query returns all members
    Given the user is an authenticated member of the community
    When the user searches the directory for ""
    Then the directory should return all active members

  @edge_case
  Scenario: Member directory for community with single member
    Given the user is the only member of a new community
    When the user requests the member directory
    Then the directory should return 1 member

  # === SECURITY ===

  @security
  Scenario: Unauthenticated user cannot access member directory
    Given the user is not authenticated
    When the user requests the member directory
    Then the request should be rejected with an authentication error

  @security
  Scenario: Non-member cannot access community directory
    Given the user is authenticated but not a member of the community
    When the user requests the member directory for that community
    Then the request should be rejected with an authorization error

  @security
  Scenario: Member directory does not expose private information
    Given the user is an authenticated member of the community
    When the user requests the member directory
    Then no member entry should contain an email address
    And no member entry should contain private settings
