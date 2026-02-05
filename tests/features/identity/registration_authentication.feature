@identity @authentication
Feature: User Registration and Authentication
  As a new user
  I want to register and authenticate with email/password
  So that I can access the Koulu platform

  Background:
    Given the system is initialized
    And email delivery is enabled

  # ============================================================================
  # EMAIL/PASSWORD REGISTRATION
  # ============================================================================

  @happy_path @registration
  Scenario: Successful registration with email and password
    Given no user exists with email "newuser@example.com"
    When a user registers with email "newuser@example.com" and password "securepass123"
    Then a new user account should be created with email "newuser@example.com"
    And the user should not be verified
    And a "UserRegistered" event should be published
    And a verification email should be sent to "newuser@example.com"

  @happy_path @registration
  Scenario: Verification email contains valid magic link
    Given a user registered with email "unverified@example.com"
    And the user has not verified their email
    When the verification email is sent
    Then the email should contain a verification link
    And the verification link should be valid for 24 hours

  @happy_path @registration
  Scenario: Successful email verification via magic link
    Given a user registered with email "unverified@example.com"
    And the user has a valid verification token
    When the user verifies their email with the token
    Then the user should be marked as verified
    And a "UserVerified" event should be published
    And the user should receive authentication tokens

  @error @registration
  Scenario: Registration fails with invalid email format
    When a user attempts to register with email "not-an-email" and password "securepass123"
    Then registration should fail with error code "invalid_email"
    And no user account should be created

  @error @registration
  Scenario: Registration fails with password too short
    When a user attempts to register with email "newuser@example.com" and password "short"
    Then registration should fail with error code "password_too_short"
    And no user account should be created

  @error @registration
  Scenario: Registration with existing email returns generic message
    Given a user exists with email "existing@example.com"
    When a user attempts to register with email "existing@example.com" and password "securepass123"
    Then the response should indicate to check email
    And no duplicate user should be created
    # Note: Generic response prevents email enumeration attacks

  @edge_case @registration
  Scenario: Verification token expires after 24 hours
    Given a user registered with email "expired@example.com"
    And the user has a verification token created 25 hours ago
    When the user attempts to verify their email with the expired token
    Then verification should fail with error code "invalid_token"
    And the user should remain unverified

  @edge_case @registration
  Scenario: Resend verification email
    Given a user registered with email "unverified@example.com"
    And the user has not verified their email
    When the user requests a new verification email
    Then a new verification email should be sent
    And the old verification token should be invalidated

  @edge_case @registration
  Scenario: Verification link used twice
    Given a user registered with email "verified@example.com"
    And the user has verified their email
    When the user attempts to verify their email again with the same token
    Then verification should fail with error code "already_verified"

  # ============================================================================
  # EMAIL/PASSWORD LOGIN
  # ============================================================================

  @happy_path @login
  Scenario: Successful login with email and password
    Given a verified user exists with email "user@example.com" and password "correctpassword"
    When the user logs in with email "user@example.com" and password "correctpassword"
    Then the user should receive authentication tokens
    And a "UserLoggedIn" event should be published

  @happy_path @login
  Scenario: Login with "remember me" extends session duration
    Given a verified user exists with email "user@example.com" and password "correctpassword"
    When the user logs in with "remember me" enabled
    Then the refresh token should be valid for 30 days

  @happy_path @login
  Scenario: Login without "remember me" has standard session duration
    Given a verified user exists with email "user@example.com" and password "correctpassword"
    When the user logs in without "remember me"
    Then the refresh token should be valid for 7 days

  @error @login
  Scenario: Login fails with incorrect password
    Given a verified user exists with email "user@example.com" and password "correctpassword"
    When the user attempts to log in with email "user@example.com" and password "wrongpassword"
    Then login should fail with error code "invalid_credentials"

  @error @login
  Scenario: Login fails with non-existent email
    Given no user exists with email "nonexistent@example.com"
    When the user attempts to log in with email "nonexistent@example.com" and password "anypassword"
    Then login should fail with error code "invalid_credentials"
    # Note: Same error as wrong password to prevent email enumeration

  @error @login
  Scenario: Login fails for unverified user
    Given a user registered with email "unverified@example.com" and password "correctpassword"
    And the user has not verified their email
    When the user attempts to log in with email "unverified@example.com" and password "correctpassword"
    Then login should fail with error code "email_not_verified"

  @error @login
  Scenario: Login fails for disabled account
    Given a verified user exists with email "disabled@example.com"
    And the user account is disabled
    When the user attempts to log in with email "disabled@example.com" and password "correctpassword"
    Then login should fail with error code "account_disabled"

  # ============================================================================
  # TOKEN MANAGEMENT
  # ============================================================================

  @happy_path @tokens
  Scenario: Access token expires and is refreshed
    Given a user is authenticated with valid tokens
    And the access token has expired
    When the user refreshes their access token using the refresh token
    Then a new access token should be issued
    And a new refresh token should be issued
    And the old refresh token should be invalidated

  @error @tokens
  Scenario: Refresh fails with expired refresh token
    Given a user is authenticated
    And the refresh token has expired
    When the user attempts to refresh their access token
    Then refresh should fail with error code "invalid_token"

  @edge_case @tokens
  Scenario: Refresh token rotation prevents reuse
    Given a user is authenticated with refresh token "old_token"
    When the user refreshes their access token using "old_token"
    And receives a new refresh token "new_token"
    And attempts to use "old_token" again
    Then refresh should fail with error code "invalid_token"

  # ============================================================================
  # LOGOUT
  # ============================================================================

  @happy_path @logout
  Scenario: Successful logout
    Given a user is authenticated with valid tokens
    When the user logs out
    Then the refresh token should be invalidated
    And subsequent requests with the old access token should fail after expiry

  # ============================================================================
  # PASSWORD RESET
  # ============================================================================

  @happy_path @password_reset
  Scenario: Successful password reset request
    Given a verified user exists with email "user@example.com"
    When the user requests a password reset for email "user@example.com"
    Then a password reset email should be sent to "user@example.com"
    And a "PasswordResetRequested" event should be published

  @happy_path @password_reset
  Scenario: Successful password reset with valid token
    Given a user has requested a password reset
    And the user has a valid password reset token
    When the user resets their password to "newsecurepassword"
    Then the password should be updated
    And a "PasswordReset" event should be published
    And all existing refresh tokens should be invalidated
    And a confirmation email should be sent

  @error @password_reset
  Scenario: Password reset fails with expired token
    Given a user has a password reset token created 2 hours ago
    When the user attempts to reset their password
    Then password reset should fail with error code "invalid_token"

  @error @password_reset
  Scenario: Password reset fails with already used token
    Given a user has used their password reset token
    When the user attempts to use the same token again
    Then password reset should fail with error code "invalid_token"

  @error @password_reset
  Scenario: Password reset fails with password too short
    Given a user has a valid password reset token
    When the user attempts to reset their password to "short"
    Then password reset should fail with error code "password_too_short"

  @security @password_reset
  Scenario: Password reset request for non-existent email returns generic response
    Given no user exists with email "nonexistent@example.com"
    When the user requests a password reset for email "nonexistent@example.com"
    Then the response should indicate to check email
    And no email should be sent
    # Note: Generic response prevents email enumeration attacks

  # ============================================================================
  # PROFILE COMPLETION
  # ============================================================================

  @happy_path @profile
  Scenario: Successful profile completion
    Given a verified user with incomplete profile
    When the user sets their display name to "John Doe"
    Then the profile should be updated with display name "John Doe"
    And the profile should be marked as complete
    And a "ProfileCompleted" event should be published

  @happy_path @profile
  Scenario: Default avatar is generated when no avatar provided
    Given a verified user with incomplete profile
    When the user sets their display name to "John Doe" without providing an avatar
    Then the profile should have a generated avatar based on initials "JD"

  @error @profile
  Scenario: Profile completion fails with display name too short
    Given a verified user with incomplete profile
    When the user attempts to set their display name to "J"
    Then profile update should fail with error code "invalid_display_name"

  @error @profile
  Scenario: Profile completion fails with display name too long
    Given a verified user with incomplete profile
    When the user attempts to set their display name to a 51 character string
    Then profile update should fail with error code "invalid_display_name"

  # ============================================================================
  # RATE LIMITING
  # ============================================================================

  @security @rate_limiting
  Scenario: Registration is rate limited
    Given 5 registration attempts from the same IP in 15 minutes
    When a 6th registration attempt is made from the same IP
    Then the request should be rejected with error code "rate_limited"

  @security @rate_limiting
  Scenario: Login is rate limited per email
    Given 5 failed login attempts for email "user@example.com" in 15 minutes
    When a 6th login attempt is made for email "user@example.com"
    Then the request should be rejected with error code "rate_limited"

  @security @rate_limiting
  Scenario: Rate limit resets after window expires
    Given 5 failed login attempts for email "user@example.com"
    And 15 minutes have passed
    When a login attempt is made for email "user@example.com"
    Then the request should not be rate limited

  # ============================================================================
  # SECURITY
  # ============================================================================

  @security
  Scenario: Passwords are hashed with Argon2id
    Given a user registers with password "plaintextpassword"
    Then the stored password should be hashed with Argon2id
    And the plaintext password should not be stored

  @security
  Scenario: Authentication tokens are properly signed
    Given a user is authenticated
    Then the access token should be a valid JWT signed with HS256
    And the access token should contain the user ID
    And the access token should expire in 30 minutes

  @security
  Scenario: Email enumeration is prevented on login
    Given a user exists with email "exists@example.com"
    When login fails for email "exists@example.com" with wrong password
    And login fails for email "notexists@example.com"
    Then both error responses should be identical
