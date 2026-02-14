Feature: Search
  As a community member
  I want to search for members and posts from the header bar
  So that I can quickly find people and discussions in my community

  Background:
    Given a community "Startup Empire" exists
    And the community has the following members:
      | display_name  | username          | bio                                     |
      | Sachin Kundu  | sachin-kundu-3386 | Experienced software engineer            |
      | Alice Chen    | alice-chen-1234   | Product designer and startup enthusiast  |
      | Bob Martinez  | bob-martinez-5678 | Marketing expert in SaaS growth          |
    And the community has the following posts:
      | title                          | body                                                    | author       |
      | Welcome to Startup Empire      | This is the official welcome post for all new members   | Sachin Kundu |
      | Tips for SaaS Growth           | Here are my top 10 tips for growing your SaaS startup   | Bob Martinez |
      | Design Systems Best Practices  | A guide to building scalable design systems             | Alice Chen   |

  # === HAPPY PATH: MEMBER SEARCH ===

  @happy_path
  Scenario: Search for a member by display name
    Given the member "Sachin Kundu" is authenticated
    When the member searches for "Alice" with type "members"
    Then the search results should contain 1 member
    And the member result should include "Alice Chen"

  @happy_path
  Scenario: Search for a member by username
    Given the member "Sachin Kundu" is authenticated
    When the member searches for "bob-martinez" with type "members"
    Then the search results should contain 1 member
    And the member result should include "Bob Martinez"

  @happy_path
  Scenario: Search for a member by bio content
    Given the member "Sachin Kundu" is authenticated
    When the member searches for "software engineer" with type "members"
    Then the search results should contain 1 member
    And the member result should include "Sachin Kundu"

  @happy_path
  Scenario: Member results are sorted alphabetically
    Given the member "Sachin Kundu" is authenticated
    When the member searches for "startup" with type "members"
    Then the member results should be sorted alphabetically by display name

  @happy_path
  Scenario: Member result card shows expected fields
    Given the member "Sachin Kundu" is authenticated
    When the member searches for "Alice" with type "members"
    Then the member result for "Alice Chen" should include:
      | field        | present |
      | display_name | true    |
      | username     | true    |
      | bio          | true    |
      | role         | true    |
      | joined_at    | true    |

  # === HAPPY PATH: POST SEARCH ===

  @happy_path
  Scenario: Search for a post by title
    Given the member "Sachin Kundu" is authenticated
    When the member searches for "Welcome" with type "posts"
    Then the search results should contain 1 post
    And the post result should include "Welcome to Startup Empire"

  @happy_path
  Scenario: Search for a post by body content
    Given the member "Sachin Kundu" is authenticated
    When the member searches for "SaaS startup" with type "posts"
    Then the search results should contain 1 post
    And the post result should include "Tips for SaaS Growth"

  @happy_path
  Scenario: Post results are sorted by newest first
    Given the member "Sachin Kundu" is authenticated
    When the member searches for "post OR tips OR guide" with type "posts"
    Then the post results should be sorted by creation date descending

  @happy_path
  Scenario: Post result card shows expected fields
    Given the member "Sachin Kundu" is authenticated
    When the member searches for "Welcome" with type "posts"
    Then the post result for "Welcome to Startup Empire" should include:
      | field        | present |
      | title        | true    |
      | body_snippet | true    |
      | author_name  | true    |
      | category     | true    |
      | created_at   | true    |

  # === HAPPY PATH: TABBED RESULTS ===

  @happy_path
  Scenario: Search returns counts for both tabs
    Given the member "Sachin Kundu" is authenticated
    When the member searches for "startup" with type "members"
    Then the response should include a member count
    And the response should include a post count

  @happy_path
  Scenario: Switch between member and post tabs
    Given the member "Sachin Kundu" is authenticated
    When the member searches for "startup" with type "members"
    Then the search results should contain members
    When the member searches for "startup" with type "posts"
    Then the search results should contain posts

  # === HAPPY PATH: PAGINATION ===

  @happy_path
  Scenario: Search results are paginated
    Given the community has 25 members with "developer" in their bio
    And the member "Sachin Kundu" is authenticated
    When the member searches for "developer" with type "members" and limit 10
    Then the search results should contain 10 members
    And the response should indicate more results are available

  @happy_path
  Scenario: Navigate to next page of results
    Given the community has 25 members with "developer" in their bio
    And the member "Sachin Kundu" is authenticated
    When the member searches for "developer" with type "members" and limit 10 and offset 10
    Then the search results should contain 10 members
    And the results should be from the second page

  # === HAPPY PATH: STEMMING ===

  @happy_path
  Scenario: Search uses stemming for member bio
    Given the member "Sachin Kundu" is authenticated
    When the member searches for "engineering" with type "members"
    Then the search results should contain 1 member
    And the member result should include "Sachin Kundu"

  @happy_path
  Scenario: Search uses stemming for post content
    Given the member "Sachin Kundu" is authenticated
    When the member searches for "growing" with type "posts"
    Then the search results should contain 1 post
    And the post result should include "Tips for SaaS Growth"

  # === VALIDATION ERRORS ===

  @error
  Scenario: Search with query shorter than 3 characters
    Given the member "Sachin Kundu" is authenticated
    When the member searches for "ab" with type "members"
    Then the search should fail with a "query too short" error

  @error
  Scenario: Search with empty query
    Given the member "Sachin Kundu" is authenticated
    When the member searches for "" with type "members"
    Then the search should fail with a "query required" error

  @error
  Scenario: Search with invalid type parameter
    Given the member "Sachin Kundu" is authenticated
    When the member searches for "test" with type "invalid"
    Then the search should fail with a "invalid search type" error

  @error
  Scenario: Search with query exceeding maximum length
    Given the member "Sachin Kundu" is authenticated
    When the member searches with a 201-character query
    Then the search query should be truncated to 200 characters
    And the search should execute successfully

  # === EDGE CASES ===

  @edge_case
  Scenario: Search returns no results
    Given the member "Sachin Kundu" is authenticated
    When the member searches for "xyznonexistent" with type "members"
    Then the search results should contain 0 members
    And the response should indicate no results found

  @edge_case
  Scenario: Search with special characters
    Given the member "Sachin Kundu" is authenticated
    When the member searches for "<script>alert('xss')</script>" with type "members"
    Then the search should execute successfully
    And the search results should contain 0 members

  @edge_case
  Scenario: Deleted posts do not appear in search results
    Given the member "Sachin Kundu" is authenticated
    And the post "Welcome to Startup Empire" has been deleted
    When the member searches for "Welcome" with type "posts"
    Then the search results should contain 0 posts

  @edge_case
  Scenario: Inactive members do not appear in search results
    Given the member "Sachin Kundu" is authenticated
    And the member "Alice Chen" has been deactivated
    When the member searches for "Alice" with type "members"
    Then the search results should contain 0 members

  @edge_case
  Scenario: Search with only whitespace
    Given the member "Sachin Kundu" is authenticated
    When the member searches for "   " with type "members"
    Then the search should fail with a "query required" error

  @edge_case
  Scenario: Member with no bio is still found by name
    Given a member "Jane Smith" exists with username "jane-smith-9999" and no bio
    And the member "Sachin Kundu" is authenticated
    When the member searches for "Jane" with type "members"
    Then the search results should contain 1 member
    And the member result should include "Jane Smith"

  @edge_case
  Scenario: Search query matches across multiple members
    Given the member "Sachin Kundu" is authenticated
    When the member searches for "startup" with type "members"
    Then the search results should contain at least 1 member

  # === SECURITY ===

  @security
  Scenario: Unauthenticated user cannot search
    Given no user is authenticated
    When an unauthenticated user attempts to search for "test"
    Then the search should fail with an "authentication required" error

  @security
  Scenario: Non-member cannot search a community
    Given a user "Outsider" exists but is not a member of "Startup Empire"
    And the user "Outsider" is authenticated
    When the user searches for "Sachin" in community "Startup Empire"
    Then the search should fail with a "not a member" error

  @security
  Scenario: Search input is sanitized against SQL injection
    Given the member "Sachin Kundu" is authenticated
    When the member searches for "'; DROP TABLE users; --" with type "members"
    Then the search should execute successfully
    And the search results should contain 0 members

  @security
  Scenario: Search respects rate limiting
    Given the member "Sachin Kundu" is authenticated
    When the member performs 31 searches within 1 minute
    Then the 31st search should fail with a "rate limit exceeded" error
