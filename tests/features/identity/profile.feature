Feature: User Profile
  As a community member
  I want to manage my profile and view other profiles
  So that I can establish my identity and connect with others

  Background:
    Given the system is initialized
    And a verified user exists with email "member@example.com"

  # =============================================================================
  # PROFILE COMPLETION
  # =============================================================================

  @happy_path
  Scenario: Complete profile with display name only
    Given the user "member@example.com" has not completed their profile
    When the user completes their profile with display name "Jane Doe"
    Then the profile should be marked as complete
    And a "ProfileCompleted" event should be published
    And a default avatar should be generated from the initials "JD"

  @happy_path
  Scenario: Complete profile with all optional fields
    Given the user "member@example.com" has not completed their profile
    When the user completes their profile with:
      | field           | value                              |
      | display_name    | Jane Doe                           |
      | bio             | Software engineer and coffee lover |
      | city            | Austin                             |
      | country         | USA                                |
      | avatar_url      | https://example.com/avatar.jpg     |
      | twitter_url     | https://twitter.com/janedoe        |
      | linkedin_url    | https://linkedin.com/in/janedoe    |
      | instagram_url   | https://instagram.com/janedoe      |
      | website_url     | https://janedoe.com                |
    Then the profile should be marked as complete
    And the profile should contain all provided information
    And a "ProfileCompleted" event should be published

  @happy_path
  Scenario: Complete profile with partial optional fields
    Given the user "member@example.com" has not completed their profile
    When the user completes their profile with:
      | field        | value            |
      | display_name | Jane Doe         |
      | bio          | Just a bio       |
      | website_url  | https://jane.com |
    Then the profile should be marked as complete
    And the location should be empty
    And the twitter_url should be empty
    And the linkedin_url should be empty
    And the instagram_url should be empty

  # =============================================================================
  # PROFILE COMPLETION VALIDATION ERRORS
  # =============================================================================

  @error
  Scenario: Profile completion fails without display name
    Given the user "member@example.com" has not completed their profile
    When the user attempts to complete their profile without a display name
    Then profile completion should fail with "display name is required" error

  @error
  Scenario: Profile completion fails with display name too short
    Given the user "member@example.com" has not completed their profile
    When the user attempts to complete their profile with display name "J"
    Then profile completion should fail with "display name too short" error

  @error
  Scenario: Profile completion fails with display name too long
    Given the user "member@example.com" has not completed their profile
    When the user attempts to complete their profile with a display name of 51 characters
    Then profile completion should fail with "display name too long" error

  @error
  Scenario: Profile completion fails with bio too long
    Given the user "member@example.com" has not completed their profile
    When the user attempts to complete their profile with:
      | field        | value                    |
      | display_name | Jane Doe                 |
      | bio          | <501 character string>   |
    Then profile completion should fail with "bio too long" error

  @error
  Scenario: Profile completion fails with invalid avatar URL
    Given the user "member@example.com" has not completed their profile
    When the user attempts to complete their profile with:
      | field        | value           |
      | display_name | Jane Doe        |
      | avatar_url   | not-a-valid-url |
    Then profile completion should fail with "invalid URL format" error

  @error
  Scenario: Profile completion fails with city but no country
    Given the user "member@example.com" has not completed their profile
    When the user attempts to complete their profile with:
      | field        | value    |
      | display_name | Jane Doe |
      | city         | Austin   |
    Then profile completion should fail with "country is required when city is provided" error

  @error
  Scenario: Profile completion fails with country but no city
    Given the user "member@example.com" has not completed their profile
    When the user attempts to complete their profile with:
      | field        | value    |
      | display_name | Jane Doe |
      | country      | USA      |
    Then profile completion should fail with "city is required when country is provided" error

  @error
  Scenario: Profile completion fails with invalid social link URL
    Given the user "member@example.com" has not completed their profile
    When the user attempts to complete their profile with:
      | field        | value           |
      | display_name | Jane Doe        |
      | twitter_url  | not-a-valid-url |
    Then profile completion should fail with "invalid URL format" error

  # =============================================================================
  # VIEW OWN PROFILE
  # =============================================================================

  @happy_path
  Scenario: User views their own profile
    Given the user "member@example.com" has a completed profile with:
      | field        | value                    |
      | display_name | Jane Doe                 |
      | bio          | Software engineer        |
      | city         | Austin                   |
      | country      | USA                      |
      | twitter_url  | https://twitter.com/jane |
    When the user requests their own profile
    Then the profile should be returned with all stored information
    And the response should include contribution stats
    And the response should include an "Edit Profile" option indicator

  @happy_path
  Scenario: User views own profile with empty activity
    Given the user "member@example.com" has a completed profile
    And the user has no community activity
    When the user requests their profile activity
    Then the activity list should be empty
    And the contribution count should be 0

  # =============================================================================
  # VIEW OTHER USER'S PROFILE
  # =============================================================================

  @happy_path
  Scenario: User views another member's profile
    Given a verified user exists with email "other@example.com"
    And the user "other@example.com" has a completed profile with:
      | field        | value         |
      | display_name | John Smith    |
      | bio          | Entrepreneur  |
      | city         | New York      |
      | country      | USA           |
    When the user "member@example.com" requests the profile of "other@example.com"
    Then the profile should be returned with all stored information
    And the response should NOT include an "Edit Profile" option indicator

  @error
  Scenario: View profile of non-existent user
    When the user requests the profile of a non-existent user ID
    Then the request should fail with "profile not found" error

  # =============================================================================
  # UPDATE PROFILE
  # =============================================================================

  @happy_path
  Scenario: Update display name
    Given the user "member@example.com" has a completed profile with display name "Jane Doe"
    When the user updates their profile with display name "Jane Smith"
    Then the profile should reflect the new display name
    And a "ProfileUpdated" event should be published

  @happy_path
  Scenario: Update bio
    Given the user "member@example.com" has a completed profile
    When the user updates their profile with bio "New bio content"
    Then the profile bio should be "New bio content"
    And a "ProfileUpdated" event should be published

  @happy_path
  Scenario: Add location to profile
    Given the user "member@example.com" has a completed profile without location
    When the user updates their profile with:
      | field   | value  |
      | city    | London |
      | country | UK     |
    Then the profile location should be "London, UK"
    And a "ProfileUpdated" event should be published

  @happy_path
  Scenario: Remove location from profile
    Given the user "member@example.com" has a completed profile with location "Austin, USA"
    When the user updates their profile to remove the location
    Then the profile location should be empty
    And a "ProfileUpdated" event should be published

  @happy_path
  Scenario: Update social links
    Given the user "member@example.com" has a completed profile without social links
    When the user updates their profile with:
      | field       | value                        |
      | twitter_url | https://twitter.com/newjane  |
      | website_url | https://newsite.com          |
    Then the profile should contain the new social links
    And the linkedin_url should be empty
    And the instagram_url should be empty
    And a "ProfileUpdated" event should be published

  @happy_path
  Scenario: Update avatar URL
    Given the user "member@example.com" has a completed profile with auto-generated avatar
    When the user updates their profile with avatar_url "https://example.com/new-avatar.jpg"
    Then the profile avatar should be "https://example.com/new-avatar.jpg"
    And a "ProfileUpdated" event should be published

  @happy_path
  Scenario: Clear avatar URL reverts to auto-generated
    Given the user "member@example.com" has a completed profile with avatar_url "https://example.com/avatar.jpg"
    When the user updates their profile to remove the avatar URL
    Then a default avatar should be generated from the display name initials
    And a "ProfileUpdated" event should be published

  @happy_path
  Scenario: Update multiple fields at once
    Given the user "member@example.com" has a completed profile
    When the user updates their profile with:
      | field        | value               |
      | display_name | Updated Name        |
      | bio          | Updated bio         |
      | city         | Seattle             |
      | country      | USA                 |
      | website_url  | https://updated.com |
    Then the profile should reflect all updated fields
    And a single "ProfileUpdated" event should be published

  # =============================================================================
  # UPDATE PROFILE VALIDATION ERRORS
  # =============================================================================

  @error
  Scenario: Update fails with display name too short
    Given the user "member@example.com" has a completed profile
    When the user attempts to update their profile with display name "J"
    Then the update should fail with "display name too short" error

  @error
  Scenario: Update fails with display name too long
    Given the user "member@example.com" has a completed profile
    When the user attempts to update their profile with a display name of 51 characters
    Then the update should fail with "display name too long" error

  @error
  Scenario: Update fails with bio too long
    Given the user "member@example.com" has a completed profile
    When the user attempts to update their profile with a bio of 501 characters
    Then the update should fail with "bio too long" error

  @error
  Scenario: Update fails with invalid avatar URL
    Given the user "member@example.com" has a completed profile
    When the user attempts to update their profile with avatar_url "not-a-url"
    Then the update should fail with "invalid URL format" error

  @error
  Scenario: Update fails with partial location
    Given the user "member@example.com" has a completed profile
    When the user attempts to update their profile with city "Paris" but no country
    Then the update should fail with "country is required when city is provided" error

  # =============================================================================
  # PROFILE STATS
  # =============================================================================

  @happy_path
  Scenario: Profile stats show zero contributions for new user
    Given the user "member@example.com" has a completed profile
    And the user has no community activity
    When the user requests their profile stats
    Then the contribution count should be 0
    And the joined_at date should be the user registration date

  @edge_case
  Scenario: Profile stats show member since date
    Given the user "member@example.com" registered on "2026-01-15"
    And the user has a completed profile
    When the user requests their profile stats
    Then the joined_at should be "2026-01-15"

  # =============================================================================
  # ACTIVITY FEED
  # =============================================================================

  @happy_path
  Scenario: Activity feed is empty for user with no posts or comments
    Given the user "member@example.com" has a completed profile
    And the user has no community activity
    When the user requests their profile activity
    Then the activity list should be empty
    And the total_count should be 0

  @edge_case
  Scenario: Activity feed placeholder until Community feature exists
    Given the user "member@example.com" has a completed profile
    When the user requests their profile activity
    Then the activity list should be empty
    And the response should indicate "No activity yet"

  # =============================================================================
  # DAILY ACTIVITY CHART
  # =============================================================================

  @happy_path
  Scenario: Activity chart returns empty data for user with no activity
    Given the user "member@example.com" has a completed profile
    When the user requests their 30-day activity chart data
    Then the chart data should contain 30 days
    And all activity counts should be 0

  # =============================================================================
  # SECURITY
  # =============================================================================

  @security
  Scenario: Unauthenticated user cannot view profiles
    Given an unauthenticated request
    When the request attempts to view a user profile
    Then the request should fail with "authentication required" error

  @security
  Scenario: User cannot edit another user's profile
    Given a verified user exists with email "other@example.com"
    And the user "other@example.com" has a completed profile
    When the user "member@example.com" attempts to update the profile of "other@example.com"
    Then the request should fail with "unauthorized" error

  @security
  Scenario: Profile text inputs are sanitized
    Given the user "member@example.com" has not completed their profile
    When the user completes their profile with bio "<script>alert('xss')</script>"
    Then the bio should be sanitized to remove script tags
    And the profile should be saved successfully

  @security
  Scenario: Profile update requests are rate limited
    Given the user "member@example.com" has a completed profile
    When the user sends 20 profile update requests within 1 minute
    Then the requests should be rate limited after the threshold
    And subsequent requests should fail with "rate limit exceeded" error
