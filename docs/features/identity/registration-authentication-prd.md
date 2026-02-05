# User Registration & Authentication - Product Requirements Document

**Version:** 1.3
**Last Updated:** February 5, 2026
**Status:** Draft
**Bounded Context:** Identity
**PRD Type:** Feature Specification

**Implementation Status:** Complete
**Summary:** `docs/summaries/registration-authentication-summary.md`

---

## 1. Overview

### 1.1 What

A complete user registration and authentication system enabling users to create accounts with email/password, verify their email, log in securely, and reset passwords.

### 1.2 Why

This is the foundational feature for Koulu. No other feature can function without user identity. Users need secure, frictionless ways to create accounts and access the platform.

### 1.3 Success Criteria

| Metric | Target |
|--------|--------|
| Registration completion rate | > 80% of started registrations |
| Email verification rate | > 70% within 24 hours |
| Login success rate | > 99% for valid credentials |
| Password reset completion | > 60% of requests |

---

## 2. User Stories

### 2.1 Registration

| ID | Story | Priority |
|----|-------|----------|
| US-R1 | As a new user, I want to register with my email and password so that I can create an account | Must Have |
| US-R2 | As a new user, I want to verify my email so that my account is activated | Must Have |
| US-R3 | As a new user, I want to set up my profile (display name) so that others can identify me | Must Have |
| US-R4 | As a new user, I want a default avatar generated for me so that I have a visual identity immediately | Should Have |

### 2.2 Authentication

| ID | Story | Priority |
|----|-------|----------|
| US-A1 | As a registered user, I want to log in with my email and password so that I can access my account | Must Have |
| US-A2 | As a user, I want to stay logged in ("Remember me") so that I don't have to log in every time | Should Have |
| US-A3 | As a user, I want to log out so that I can secure my account on shared devices | Must Have |

### 2.3 Password Management

| ID | Story | Priority |
|----|-------|----------|
| US-P1 | As a user who forgot my password, I want to reset it via email so that I can regain access | Must Have |
| US-P2 | As a user, I want the reset link to expire so that my account stays secure | Must Have |

---

## 3. Domain Model

### 3.1 Aggregates & Entities

```
┌─────────────────────────────────────────────────────────┐
│                    User (Aggregate Root)                │
├─────────────────────────────────────────────────────────┤
│ - id: UserId                                            │
│ - email: EmailAddress                                   │
│ - hashed_password: HashedPassword                       │
│ - is_verified: bool                                     │
│ - is_active: bool                                       │
│ - created_at: datetime                                  │
│ - updated_at: datetime                                  │
├─────────────────────────────────────────────────────────┤
│ + register(email, password)                             │
│ + verify_email()                                        │
│ + request_password_reset()                              │
│ + reset_password(new_password)                          │
│ + update_profile(profile)                               │
└─────────────────────────────────────────────────────────┘
                          │
                          │ 1:1
                          ▼
┌─────────────────────────────────────────────────────────┐
│                       Profile                           │
├─────────────────────────────────────────────────────────┤
│ - display_name: DisplayName                             │
│ - avatar_url: URL (nullable)                            │
│ - bio: str (nullable)                                   │
│ - is_complete: bool                                     │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Value Objects

| Value Object | Validation Rules |
|--------------|------------------|
| `UserId` | UUID v4, immutable |
| `EmailAddress` | Valid email format (RFC 5322), lowercase, max 254 chars |
| `HashedPassword` | Argon2id hash, never stores plaintext |
| `DisplayName` | 2-50 characters, no leading/trailing whitespace |

### 3.3 Domain Services

| Service | Responsibility |
|---------|----------------|
| `PasswordHasher` | Hash and verify passwords using Argon2id |
| `TokenGenerator` | Generate secure tokens for verification/reset |
| `AvatarGenerator` | Generate default avatar from initials |

---

## 4. Commands & Events

### 4.1 Commands

| Command | Input | Output | Triggered By |
|---------|-------|--------|--------------|
| `RegisterUser` | email, password | UserId | User submits registration form |
| `VerifyEmail` | verification_token | void | User clicks email link |
| `ResendVerification` | email | void | User requests new verification email |
| `Login` | email, password, remember_me | AuthTokens | User submits login form |
| `Logout` | refresh_token | void | User clicks logout |
| `RequestPasswordReset` | email | void | User submits forgot password form |
| `ResetPassword` | reset_token, new_password | void | User submits new password |
| `RefreshAccessToken` | refresh_token | AuthTokens | Client refreshes expired token |
| `CompleteProfile` | user_id, display_name, avatar? | void | User completes profile setup |

### 4.2 Domain Events

| Event | Published When | Subscribers |
|-------|----------------|-------------|
| `UserRegistered` | After successful registration (before verification) | Email service (send verification) |
| `UserVerified` | After email verification completes | Analytics, welcome email |
| `UserLoggedIn` | After successful login | Analytics, audit log |
| `PasswordResetRequested` | After reset request | Email service (send reset link) |
| `PasswordReset` | After password changed via reset | Email service (confirmation), audit log |
| `ProfileCompleted` | After user completes profile setup | Analytics |

---

## 5. Functional Requirements

### 5.1 Registration Capabilities

The system must provide the ability to:

| Capability | Required Inputs | Expected Outcomes | Error Conditions |
|------------|----------------|-------------------|------------------|
| **Register new user** | Email address, password | User account created (unverified), verification email sent | Invalid email format, password too short, email already exists |
| **Verify email** | Verification token | Account marked as verified, user authenticated | Invalid token, expired token, already verified |
| **Resend verification** | Email address | New verification email sent | N/A (always succeeds to prevent enumeration) |

### 5.2 Authentication Capabilities

The system must provide the ability to:

| Capability | Required Inputs | Expected Outcomes | Error Conditions |
|------------|----------------|-------------------|------------------|
| **Login** | Email, password, remember me flag (optional) | User authenticated, tokens issued, user info returned | Invalid credentials, email not verified, account disabled, rate limited |
| **Refresh session** | Refresh token | New tokens issued | Invalid token, expired token |
| **Logout** | Refresh token | Session invalidated | N/A |

### 5.3 Password Reset Capabilities

The system must provide the ability to:

| Capability | Required Inputs | Expected Outcomes | Error Conditions |
|------------|----------------|-------------------|------------------|
| **Request password reset** | Email address | Reset email sent | N/A (always succeeds to prevent enumeration) |
| **Reset password** | Reset token, new password | Password updated, all sessions invalidated, confirmation email sent | Invalid token, expired token, password too short |

### 5.4 Profile Management Capabilities

The system must provide the ability to:

| Capability | Required Inputs | Expected Outcomes | Error Conditions |
|------------|----------------|-------------------|------------------|
| **Update profile** | Display name, avatar URL (optional) | Profile updated and marked complete | Display name invalid length, not authenticated |
| **Get current user** | N/A (authenticated) | User info and profile returned | Not authenticated |

---

## 6. Business Rules

### 6.1 Registration Rules

| ID | Rule | Enforcement |
|----|------|-------------|
| BR-R1 | Email must be unique (case-insensitive) | Database unique constraint |
| BR-R2 | Password must be at least 8 characters | Validation |
| BR-R3 | Email must be valid format | Validation (RFC 5322) |
| BR-R4 | Verification email sent within 30 seconds of registration | Async event handler |
| BR-R5 | Verification token expires after 24 hours | Token with expiry |
| BR-R6 | User cannot log in until email is verified | Login check |

### 6.2 Authentication Rules

| ID | Rule | Enforcement |
|----|------|-------------|
| BR-A1 | Access tokens expire in 30 minutes | JWT exp claim |
| BR-A2 | Refresh tokens expire in 7 days (default) or 30 days (remember me) | JWT exp claim |
| BR-A3 | Refresh tokens are rotated on use (old token invalidated) | Token blacklist |
| BR-A4 | Maximum 5 login attempts per email per 15 minutes | Rate limiter |
| BR-A5 | Passwords are securely hashed using industry-standard algorithm | Password hasher |

### 6.3 Password Reset Rules

| ID | Rule | Enforcement |
|----|------|-------------|
| BR-P1 | Reset token expires after 1 hour | Token with expiry |
| BR-P2 | Reset token is single-use | Token invalidation |
| BR-P3 | All refresh tokens invalidated after password reset | Token blacklist |
| BR-P4 | Confirmation email sent after successful reset | Event handler |

### 6.4 Profile Rules

| ID | Rule | Enforcement |
|----|------|-------------|
| BR-PR1 | Display name is required (2-50 characters) | Validation |
| BR-PR2 | Avatar defaults to generated initials image | Default generator |
| BR-PR3 | Profile is marked complete when display_name is set | Profile entity |

---

## 7. UI Behavior

### 7.1 Screens

| Screen | Route | Purpose |
|--------|-------|---------|
| Registration | `/register` | Email/password signup |
| Login | `/login` | Email/password login |
| Email Verification | `/verify?token=...` | Auto-verify on load, show status |
| Forgot Password | `/forgot-password` | Enter email for reset link |
| Reset Password | `/reset-password?token=...` | Enter new password |
| Profile Setup | `/onboarding/profile` | Set display name, optional avatar |

### 7.2 Registration Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  /register  │────▶│ Submit form │────▶│ Check email │────▶│ /verify?... │
│             │     │             │     │   message   │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                   │
                    ┌─────────────┐     ┌─────────────┐            │
                    │    /feed    │◀────│  /onboarding │◀───────────┘
                    │  (complete) │     │   /profile   │
                    └─────────────┘     └─────────────┘
```

### 7.3 States & Feedback

| Action | Loading State | Success | Error |
|--------|---------------|---------|-------|
| Register | Button spinner | Redirect to "check email" | Inline error message |
| Verify email | Page spinner | Redirect to profile setup | Error message + resend link |
| Login | Button spinner | Redirect to feed (or profile if incomplete) | Inline error message |
| Forgot password | Button spinner | Success message | Inline error message |
| Reset password | Button spinner | Redirect to login with success toast | Inline error message |
| Profile setup | Button spinner | Redirect to feed | Inline error message |

### 7.4 Form Validation (Client-side)

| Field | Validation | Error Message |
|-------|------------|---------------|
| Email | Required, valid format | "Please enter a valid email address" |
| Password | Required, min 8 chars | "Password must be at least 8 characters" |
| Display name | Required, 2-50 chars | "Display name must be 2-50 characters" |

---

## 8. Edge Cases

### 8.1 Registration Edge Cases

| Scenario | Behavior |
|----------|----------|
| Email already registered | Return generic message (security) |
| User closes browser before verification | Can request resend anytime |
| Verification link clicked after 24 hours | Show expiry message + resend button |
| Verification link clicked twice | Second click shows "already verified" |

### 8.2 Authentication Edge Cases

| Scenario | Behavior |
|----------|----------|
| Correct password but email not verified | Return 401 with `email_not_verified` code |
| 5+ failed login attempts | Return 429, unlock after 15 minutes |
| Refresh token used after password reset | Reject (all tokens invalidated) |
| Access token expired, refresh token valid | Issue new tokens via /refresh |
| Both tokens expired | Redirect to login |

### 8.3 Password Reset Edge Cases

| Scenario | Behavior |
|----------|----------|
| Reset requested for non-existent email | Return 202 (no indication email doesn't exist) |
| Reset link clicked after 1 hour | Show expiry message + request new link |
| Reset link clicked twice | Second click shows "link already used" |
| New password same as old | Allow (don't check history in MVP) |

---

## 9. Security

### 9.1 Authentication Security

| Measure | Requirement |
|---------|-------------|
| Password hashing | Industry-standard secure hashing algorithm (memory-hard, resistant to GPU attacks) |
| JWT signing | Strong secret key (min 256-bit), secure signing algorithm |
| Token storage (frontend) | Access token in memory, refresh in httpOnly cookie |
| HTTPS | Required for all endpoints |
| CORS | Restrict to frontend origin |

### 9.2 Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /auth/register | 5 requests | 15 minutes per IP |
| POST /auth/login | 5 requests | 15 minutes per email |
| POST /auth/password/forgot | 3 requests | 15 minutes per email |
| POST /auth/verify/resend | 3 requests | 15 minutes per email |

### 9.3 Input Validation

| Input | Validation |
|-------|------------|
| Email | Lowercase, trim whitespace, RFC 5322 format, max 254 chars |
| Password | Min 8 chars, max 128 chars |
| Display name | Trim whitespace, 2-50 chars, no HTML |
| Tokens | Exact format match, constant-time comparison |

### 9.4 Audit Logging

Log these events with user ID, IP, timestamp, user agent:
- Registration attempts (success/failure)
- Login attempts (success/failure)
- Password reset requests
- Password changes
- Email verifications

---

## 10. Out of Scope (MVP)

The following are explicitly **NOT** included in this feature:

| Feature | Reason | Phase |
|---------|--------|-------|
| Google/Apple/Facebook OAuth | Simplify MVP | Phase 2 |
| Two-factor authentication (2FA) | Complexity | Phase 3 |
| Multiple sessions management | Nice-to-have | Phase 2 |
| Account deletion/deactivation | Regulatory, but not MVP | Phase 2 |
| Email change flow | Complexity | Phase 2 |
| CAPTCHA | Add if bot problem emerges | Phase 2 |
| Admin user management | Separate feature | Phase 2 |
| Password change (while logged in) | Lower priority than reset | Phase 2 |
| Login history/activity log (user-facing) | Nice-to-have | Phase 3 |

---

## 11. Acceptance Criteria Summary

| Requirement | Acceptance Criteria |
|-------------|---------------------|
| Email registration | User can register with valid email + password (8+ chars) |
| Email verification | User receives email with magic link, clicking verifies account |
| Login | User can login with correct credentials, receives tokens |
| Remember me | Session lasts 30 days when checked, 7 days otherwise |
| Password reset | User can reset password via email link (1hr expiry) |
| Profile setup | User must set display name before accessing main app |
| Rate limiting | Auth endpoints protected from brute force |
| Security | Passwords securely hashed, tokens properly signed |

---

## 12. Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-05 | Claude | Initial draft |
| 1.1 | 2026-02-05 | Claude | Removed Google OAuth (deferred to Phase 2) |
| 1.2 | 2026-02-05 | Claude | Removed library/DB schema details (moved to TDD) |
| 1.3 | 2026-02-05 | Claude | Removed API endpoint specs (moved to TDD), replaced with functional requirements |

---

## 13. References

- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [JWT Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)
