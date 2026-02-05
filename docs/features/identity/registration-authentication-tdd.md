# User Registration & Authentication - Technical Design Document

**Version:** 1.1
**Date:** February 5, 2026
**Status:** Draft
**Related PRD:** `registration-authentication-prd.md`
**Related BDD:** `tests/features/identity/registration_authentication.feature`
**Bounded Context:** Identity

---

## 1. Overview

### 1.1 Summary

Technical design for implementing email/password-based user registration, authentication, email verification, password reset, and profile management for the Koulu platform.

### 1.2 Goals

- Implement secure, production-ready authentication system
- Leverage industry-standard libraries to avoid reinventing solved problems
- Follow hexagonal architecture and DDD principles
- Ensure all BDD scenarios pass
- Provide extensibility for future OAuth integration (Phase 2)

### 1.3 Non-Goals

- OAuth/social login (deferred to Phase 2)
- Two-factor authentication (Phase 3)
- Account deletion flows (Phase 2)
- Admin user management UI (separate feature)

---

## 2. Architecture

### 2.1 System Context

```
┌─────────────────────────────────────────────────────────┐
│                    Koulu Platform                        │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         Identity Context (This Feature)        │    │
│  │                                                 │    │
│  │  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │    │
│  │  │  Users   │  │ Profiles │  │ Auth Tokens │  │    │
│  │  └──────────┘  └──────────┘  └─────────────┘  │    │
│  └────────────────────────────────────────────────┘    │
│                       │                                  │
│                       │ UserRegistered, UserVerified     │
│                       ▼                                  │
│  ┌────────────────────────────────────────────────┐    │
│  │            Future Contexts                      │    │
│  │  (Community, Membership, Gamification)          │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘

External Services:
- Email (SMTP/SendGrid/etc.)
- Redis (rate limiting, token blacklist)
```

### 2.2 Component Architecture

Hexagonal architecture layers:

```
┌─────────────────────────────────────────────────────────┐
│                   Interface Layer                        │
│  FastAPI Controllers (auth_controller.py, user_controller.py) │
├─────────────────────────────────────────────────────────┤
│                  Application Layer                       │
│  Commands: RegisterUser, LoginUser, VerifyEmail, etc.   │
│  Queries: GetCurrentUser                                 │
│  Use Cases: RegisterUserUseCase, LoginUseCase, etc.     │
├─────────────────────────────────────────────────────────┤
│                    Domain Layer                          │
│  Entities: User (aggregate root), Profile                │
│  Value Objects: UserId, EmailAddress, HashedPassword    │
│  Events: UserRegistered, UserVerified, PasswordReset    │
│  Services: PasswordHasher, TokenGenerator               │
│  ⚠️ NO EXTERNAL DEPENDENCIES ⚠️                          │
├─────────────────────────────────────────────────────────┤
│                Infrastructure Layer                      │
│  Repositories: SqlAlchemyUserRepository                  │
│  External Services: EmailService, TokenBlacklist        │
│  Adapters: fastapi-users integration                    │
└─────────────────────────────────────────────────────────┘
```

### 2.3 Domain-Driven Design

**Aggregates:**
- **User** (Aggregate Root) - Controls user account lifecycle, email verification, password management
- **Profile** (Entity within User aggregate) - User profile data, owned by User

**Value Objects:**
- `UserId` - UUID v4, immutable
- `EmailAddress` - Validated, normalized (lowercase)
- `HashedPassword` - Never stored in plaintext
- `DisplayName` - 2-50 characters, trimmed
- `VerificationToken` - Time-limited, single-use
- `ResetToken` - Time-limited, single-use

**Domain Events:**
- `UserRegistered(user_id, email, occurred_at)` - After successful registration
- `UserVerified(user_id, occurred_at)` - After email verification
- `UserLoggedIn(user_id, ip_address, occurred_at)` - After successful login
- `PasswordResetRequested(user_id, email, occurred_at)` - After reset request
- `PasswordReset(user_id, occurred_at)` - After password changed
- `ProfileCompleted(user_id, occurred_at)` - After profile setup

**Repositories (Interfaces in Domain):**
- `IUserRepository` - get_by_id, get_by_email, save, delete
- `IProfileRepository` - get_by_user_id, save

**Domain Services:**
- `PasswordHasher` - hash(), verify()
- `TokenGenerator` - generate_verification_token(), generate_reset_token()
- `AvatarGenerator` - generate_from_initials(name)

---

## 3. Technology Stack

### 3.1 Backend

| Technology | Version | Purpose | Justification |
|------------|---------|---------|---------------|
| **[fastapi-users](https://github.com/fastapi-users/fastapi-users)** | ^14.0 | Complete auth framework | Production-ready, handles registration/login/reset/verify out of the box, SQLAlchemy integration, generates OpenAPI docs. Saves significant development time. |
| **[fastapi-mail](https://pypi.org/project/fastapi-mail/)** | ^1.4 | Async email sending | Native FastAPI integration, async/await support, template rendering, widely used. |
| **pwdlib[argon2]** | ^0.2 | Password hashing | FastAPI recommended, Argon2id is memory-hard (GPU-resistant), faster than bcrypt. Industry standard as of 2025. |
| **PyJWT** | ^2.8 | JWT encoding/decoding | De facto standard for JWT in Python, widely audited. |
| **pydantic-settings** | ^2.0 | Configuration management | Type-safe env var loading, integrates with Pydantic v2. |
| **SQLAlchemy** | ^2.0 | ORM (async) | Industry standard ORM, async support, type hints, works seamlessly with fastapi-users. |
| **asyncpg** | ^0.29 | PostgreSQL async driver | Fastest async PostgreSQL driver for Python. |
| **redis[asyncio]** | ^5.0 | Caching, rate limiting | Token blacklist storage, rate limiting counters. |
| **slowapi** | ^0.1.9 | Rate limiting | FastAPI rate limiting middleware, Redis-backed. |
| **python-multipart** | ^0.0.6 | Form data parsing | Required for OAuth2PasswordBearer forms. |

**Why fastapi-users over custom implementation?**
- Saves ~2-3 weeks of development
- Battle-tested (3K+ GitHub stars, used in production)
- Customizable via inheritance and configuration
- Handles edge cases (race conditions, token expiry, etc.)
- Maintains security best practices
- Active maintenance and updates

### 3.2 Frontend

| Technology | Version | Purpose | Justification |
|------------|---------|---------|---------------|
| **react-hook-form** | ^7.50 | Form handling | Less boilerplate than Formik, better performance, built-in validation. |
| **zod** | ^3.22 | Schema validation | TypeScript-first, integrates with react-hook-form, generates types. |
| **@tanstack/react-query** | ^5.0 | Server state management | Handles caching, refetching, optimistic updates. Industry standard. |
| **axios** | ^1.6 | HTTP client | Interceptors for auth tokens, request/response transformation. |

**Auth State Management:**
- Custom React Context + hooks
- Simpler than adding Auth0/Clerk for MVP
- Full control over auth flow

### 3.3 Infrastructure

| Technology | Purpose |
|------------|---------|
| **PostgreSQL 15+** | Primary database, ACID guarantees |
| **Redis 7+** | Token blacklist, rate limiting, session storage (future) |
| **SMTP Service** | Email delivery (SendGrid, AWS SES, or Mailgun) |

---

## 4. Database Design

### 4.1 Schema

```sql
-- Users table (managed by fastapi-users with extensions)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(254) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_verified BOOLEAN NOT NULL DEFAULT false,
    is_superuser BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Profiles table (separate table, 1:1 with users)
CREATE TABLE profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    display_name VARCHAR(50),
    avatar_url VARCHAR(500),
    bio TEXT,
    is_complete BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Verification tokens (managed by custom logic, stored temporarily)
CREATE TABLE verification_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Reset tokens (managed by custom logic, stored temporarily)
CREATE TABLE reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    used_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_verification_tokens_token ON verification_tokens(token);
CREATE INDEX idx_verification_tokens_expires_at ON verification_tokens(expires_at);
CREATE INDEX idx_reset_tokens_token ON reset_tokens(token);
CREATE INDEX idx_reset_tokens_expires_at ON reset_tokens(expires_at);

-- Cleanup expired tokens (run periodically via cron/scheduler)
-- DELETE FROM verification_tokens WHERE expires_at < now();
-- DELETE FROM reset_tokens WHERE expires_at < now();
```

### 4.2 Indexes

| Table | Index | Columns | Justification |
|-------|-------|---------|---------------|
| users | idx_users_email | email | Frequent lookups during login and registration |
| users | idx_users_created_at | created_at | Analytics queries, recent user lists |
| verification_tokens | idx_verification_tokens_token | token | Lookup by token during verification |
| verification_tokens | idx_verification_tokens_expires_at | expires_at | Cleanup job efficiency |
| reset_tokens | idx_reset_tokens_token | token | Lookup by token during reset |
| reset_tokens | idx_reset_tokens_expires_at | expires_at | Cleanup job efficiency |

### 4.3 Migrations

**Tool:** Alembic (SQLAlchemy standard)

**File naming:** `YYYYMMDD_HHMM_description.py`

**Example:**
```bash
alembic revision -m "create_users_and_profiles_tables"
alembic upgrade head
alembic downgrade -1  # Rollback
```

**Migration strategy:**
- All schema changes via Alembic (no manual SQL)
- Migrations run before deployment
- Each migration includes upgrade and downgrade

---

## 5. API Implementation

### 5.1 Endpoint Design

All endpoints under `/api/v1/auth` and `/api/v1/users`.

#### POST `/api/v1/auth/register`

Register a new user with email and password.

**Controller:** `AuthController.register()`

**Request Schema:**
```python
class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., max_length=254)
    password: str = Field(..., min_length=8, max_length=128)

    @validator('email')
    def normalize_email(cls, v):
        return v.lower().strip()
```

**Use Case:** `RegisterUserUseCase`

**Flow:**
1. Controller validates request with Pydantic
2. Check rate limit (5 req/15min per IP)
3. Call `RegisterUserUseCase.execute(email, password)`
4. Use case creates User aggregate
5. User.register() validates email uniqueness, hashes password
6. Save to UserRepository
7. Publish `UserRegistered` event
8. Event handler sends verification email
9. Return 202 Accepted

**Response:**
```json
{
  "message": "Verification email sent. Please check your inbox."
}
```

**Error Handling:**
| Exception | HTTP Status | Error Code | Message |
|-----------|-------------|------------|---------|
| `InvalidEmailError` | 400 | `invalid_email` | "Please enter a valid email address" |
| `PasswordTooShortError` | 400 | `password_too_short` | "Password must be at least 8 characters" |
| `EmailAlreadyExistsError` | 409 | `email_exists` | "An account with this email already exists" |
| `RateLimitExceeded` | 429 | `rate_limited` | "Too many registration attempts. Try again in 15 minutes." |

---

#### POST `/api/v1/auth/verify`

Verify email address with token.

**Controller:** `AuthController.verify_email()`

**Request Schema:**
```python
class VerifyEmailRequest(BaseModel):
    token: str = Field(..., min_length=32, max_length=255)
```

**Use Case:** `VerifyEmailUseCase`

**Flow:**
1. Lookup token in verification_tokens table
2. Validate not expired (24h)
3. Load User aggregate
4. Call User.verify_email()
5. Mark user as verified
6. Delete token from table
7. Publish `UserVerified` event
8. Generate JWT access + refresh tokens
9. Return tokens

**Response:**
```json
{
  "message": "Email verified successfully.",
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Error Handling:**
| Exception | HTTP Status | Error Code |
|-----------|-------------|------------|
| `InvalidTokenError` | 400 | `invalid_token` |
| `TokenExpiredError` | 400 | `invalid_token` |
| `AlreadyVerifiedError` | 400 | `already_verified` |

---

#### POST `/api/v1/auth/verify/resend`

Resend verification email.

**Controller:** `AuthController.resend_verification()`

**Request Schema:**
```python
class ResendVerificationRequest(BaseModel):
    email: EmailStr
```

**Use Case:** `ResendVerificationEmailUseCase`

**Flow:**
1. Rate limit (3 req/15min per email)
2. Lookup user by email
3. If user exists and not verified:
   - Invalidate old tokens
   - Generate new token
   - Send verification email
4. Always return 202 (security: no email enumeration)

**Response:**
```json
{
  "message": "If this email is registered and unverified, a verification email has been sent."
}
```

---

#### POST `/api/v1/auth/login`

Login with email and password.

**Controller:** `AuthController.login()`

**Request Schema:**
```python
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False
```

**Use Case:** `LoginUseCase`

**Flow:**
1. Rate limit (5 req/15min per email)
2. Lookup user by email
3. Verify password with PasswordHasher
4. Check is_verified = true
5. Check is_active = true
6. Generate JWT tokens (access: 30min, refresh: 7d or 30d if remember_me)
7. Publish `UserLoggedIn` event
8. Return tokens + user info

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "profile": {
      "display_name": "John Doe",
      "avatar_url": "https://...",
      "is_complete": true
    }
  }
}
```

**Error Handling:**
| Exception | HTTP Status | Error Code |
|-----------|-------------|------------|
| `InvalidCredentialsError` | 401 | `invalid_credentials` |
| `EmailNotVerifiedError` | 401 | `email_not_verified` |
| `AccountDisabledError` | 403 | `account_disabled` |
| `RateLimitExceeded` | 429 | `rate_limited` |

---

#### POST `/api/v1/auth/refresh`

Refresh access token using refresh token.

**Controller:** `AuthController.refresh_token()`

**Request Schema:**
```python
class RefreshTokenRequest(BaseModel):
    refresh_token: str
```

**Use Case:** `RefreshTokenUseCase`

**Flow:**
1. Decode and validate refresh token (JWT signature, expiry)
2. Check token not in blacklist (Redis)
3. Extract user_id from token
4. Generate new access + refresh tokens
5. Blacklist old refresh token (Redis, TTL = token expiry)
6. Return new tokens

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

#### POST `/api/v1/auth/logout`

Logout and invalidate refresh token.

**Controller:** `AuthController.logout()`

**Request Schema:**
```python
class LogoutRequest(BaseModel):
    refresh_token: str
```

**Use Case:** `LogoutUseCase`

**Flow:**
1. Validate refresh token
2. Add token to blacklist (Redis)
3. Return success

**Response:**
```json
{
  "message": "Logged out successfully."
}
```

---

#### POST `/api/v1/auth/password/forgot`

Request password reset.

**Controller:** `AuthController.forgot_password()`

**Request Schema:**
```python
class ForgotPasswordRequest(BaseModel):
    email: EmailStr
```

**Use Case:** `RequestPasswordResetUseCase`

**Flow:**
1. Rate limit (3 req/15min per email)
2. Lookup user by email
3. If user exists:
   - Generate reset token (1h expiry)
   - Store in reset_tokens table
   - Publish `PasswordResetRequested` event
   - Event handler sends reset email
4. Always return 202 (security: no email enumeration)

**Response:**
```json
{
  "message": "If this email is registered, a password reset link has been sent."
}
```

---

#### POST `/api/v1/auth/password/reset`

Reset password with token.

**Controller:** `AuthController.reset_password()`

**Request Schema:**
```python
class ResetPasswordRequest(BaseModel):
    token: str
    password: str = Field(..., min_length=8, max_length=128)
```

**Use Case:** `ResetPasswordUseCase`

**Flow:**
1. Lookup token in reset_tokens table
2. Validate not expired (1h)
3. Validate not already used
4. Load User aggregate
5. Call User.reset_password(new_password)
6. Hash password with PasswordHasher
7. Mark token as used
8. Invalidate all refresh tokens (blacklist via Redis)
9. Publish `PasswordReset` event
10. Event handler sends confirmation email
11. Return success

**Response:**
```json
{
  "message": "Password reset successfully. Please log in with your new password."
}
```

---

#### PUT `/api/v1/users/me/profile`

Update current user's profile.

**Controller:** `UserController.update_profile()`

**Authentication:** Required (JWT)

**Request Schema:**
```python
class UpdateProfileRequest(BaseModel):
    display_name: str = Field(..., min_length=2, max_length=50)
    avatar_url: Optional[HttpUrl] = None

    @validator('display_name')
    def trim_display_name(cls, v):
        return v.strip()
```

**Use Case:** `UpdateProfileUseCase`

**Flow:**
1. Validate JWT token, extract user_id
2. Load User aggregate
3. Call User.update_profile(display_name, avatar_url)
4. If avatar_url is None, generate default avatar
5. Mark profile as complete
6. Save
7. Publish `ProfileCompleted` event (if first time)
8. Return updated user + profile

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "profile": {
    "display_name": "John Doe",
    "avatar_url": "https://...",
    "is_complete": true
  }
}
```

---

#### GET `/api/v1/users/me`

Get current user information.

**Controller:** `UserController.get_current_user()`

**Authentication:** Required (JWT)

**Use Case:** `GetCurrentUserUseCase`

**Flow:**
1. Validate JWT token, extract user_id
2. Load User aggregate
3. Return user + profile data

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "is_verified": true,
  "created_at": "2026-02-05T10:00:00Z",
  "profile": {
    "display_name": "John Doe",
    "avatar_url": "https://...",
    "bio": null,
    "is_complete": true
  }
}
```

---

## 6. Domain Layer Design

### 6.1 Aggregate Structure

**User Aggregate (Root):**
- **Responsibilities:**
  - Controls user account lifecycle (registration, verification, password management)
  - Enforces email uniqueness and password strength invariants
  - Manages relationship with Profile entity
  - Publishes domain events for all state changes

- **Invariants:**
  - Email must be unique across the system
  - Password must be hashed (never stored in plaintext)
  - Unverified users cannot log in
  - Disabled accounts cannot authenticate

- **Key Operations:**
  - `register(email, password)` - Factory method, creates new user, publishes UserRegistered
  - `verify_email()` - Marks email as verified, publishes UserVerified
  - `reset_password(new_password)` - Updates password, invalidates sessions, publishes PasswordReset
  - `update_profile(display_name, avatar_url)` - Updates or creates profile
  - `verify_password(password)` - Validates password for login

- **Events Published:**
  - UserRegistered (on successful registration)
  - UserVerified (on email verification)
  - PasswordReset (on password change)
  - ProfileCompleted (on first profile setup)

**Aggregate Structure:**
```
User (Aggregate Root)
├── id: UserId
├── email: EmailAddress
├── hashed_password: HashedPassword
├── is_active: bool
├── is_verified: bool
├── is_superuser: bool
├── timestamps
└── profile: Profile (1:1)
    ├── display_name: DisplayName
    ├── avatar_url: string
    ├── bio: string
    └── is_complete: bool
```

**Profile Entity:**
- Part of User aggregate, not standalone
- Cannot exist without User
- Managed through User aggregate methods only

### 6.2 Value Objects

| Value Object | Properties | Validation Rules | Immutability |
|--------------|------------|------------------|--------------|
| `UserId` | UUID v4 | Valid UUID format | Frozen |
| `EmailAddress` | string | RFC 5322 format, lowercase, max 254 chars | Frozen |
| `HashedPassword` | string | Argon2id hash format | Frozen |
| `DisplayName` | string | 2-50 chars, trimmed, no leading/trailing whitespace | Frozen |
| `VerificationToken` | string | Secure random, 32+ chars | Frozen |
| `ResetToken` | string | Secure random, 32+ chars, time-limited | Frozen |

**Value Object Pattern:**
- All validation in constructor
- Immutable (frozen dataclasses)
- Self-validating
- Can be compared by value
- Throw domain exceptions on invalid input

### 6.3 Domain Events

| Event | Trigger | Payload | Consumers |
|-------|---------|---------|-----------|
| `UserRegistered` | After registration (before verification) | user_id, email, occurred_at | Email service (send verification) |
| `UserVerified` | After email verification | user_id, occurred_at | Analytics, welcome email |
| `UserLoggedIn` | After successful login | user_id, ip_address, occurred_at | Audit log, analytics |
| `PasswordResetRequested` | After reset request | user_id, email, occurred_at | Email service (send reset link) |
| `PasswordReset` | After password changed | user_id, occurred_at | Email service (confirmation), session invalidation |
| `ProfileCompleted` | After profile setup | user_id, occurred_at | Analytics, onboarding flow |

**Event Pattern:**
- Past tense naming
- Immutable (frozen dataclasses)
- Include occurred_at timestamp
- Contain minimal data (IDs, not full entities)

### 6.4 User State Machine

**User Account States:**
```
┌─────────────┐
│   Created   │ (Registration)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Unverified  │ (Email not verified, cannot login)
└──────┬──────┘
       │ verify_email()
       ▼
┌─────────────┐
│  Verified   │ (Can login, normal operations)
└──────┬──────┘
       │
       ├─────────► [Disabled] (Admin action, cannot login)
       │
       └─────────► [Password Reset Flow] (Temporary state)
```

**Profile Completion States:**
```
[Incomplete] ──set_display_name()──► [Complete]
     │                                     │
     └──────────── update() ──────────────┘
```

### 6.5 Domain Services

| Service | Responsibility | Dependencies |
|---------|---------------|--------------|
| `PasswordHasher` | Hash passwords with Argon2id, verify hashes | pwdlib |
| `TokenGenerator` | Generate secure verification/reset tokens | secrets module, uuid |
| `AvatarGenerator` | Generate default avatar from initials | Pillow or external service |

**Service Pattern:**
- Stateless
- Encapsulates algorithms that don't belong to entities
- Injected as dependencies

---

## 7. Application Layer Design

### 7.1 Command Flow Architecture

**Registration Sequence:**
```
Client Request
     │
     ▼
[AuthController] ──validate──► [Pydantic Schema]
     │
     ▼
[RegisterUserUseCase] ──check uniqueness──► [UserRepository]
     │
     ▼
[User.register()] ──creates──► [User Aggregate]
     │                                │
     │                                ├─► Publishes UserRegistered
     │                                │
     ▼                                ▼
[UserRepository.save()]      [EventPublisher]
     │                                │
     │                                ▼
     ▼                         [EmailEventHandler]
[Response 202]                       │
                                     ▼
                             [Send Verification Email]
```

**Login Sequence:**
```
Client Request (email, password)
     │
     ▼
[AuthController] ──validate──► [LoginRequest Schema]
     │
     ▼
[LoginUseCase] ──load user──► [UserRepository]
     │
     ▼
[User.verify_password()] ──check hash──► [PasswordHasher]
     │
     ├─ if invalid ──► 401 Error
     ├─ if not verified ──► 401 Error
     ├─ if disabled ──► 403 Error
     │
     ▼
[JWTService.create_tokens()] ──generates──► Access + Refresh Tokens
     │
     ▼
[EventPublisher] ──publishes──► UserLoggedIn
     │
     ▼
[Response with tokens + user data]
```

### 7.2 Use Cases (Commands)

| Use Case | Command Input | Domain Operations | Events Published | Return |
|----------|---------------|-------------------|------------------|--------|
| RegisterUser | email, password | User.register() | UserRegistered | UserId |
| VerifyEmail | token | User.verify_email() | UserVerified | AuthTokens |
| ResendVerification | email | Generate new token | (reuses UserRegistered handler) | void |
| LoginUser | email, password, remember_me | User.verify_password() | UserLoggedIn | AuthTokens + UserInfo |
| RefreshToken | refresh_token | Validate, blacklist old | none | New AuthTokens |
| LogoutUser | refresh_token | Blacklist token | none | void |
| RequestPasswordReset | email | Generate reset token | PasswordResetRequested | void |
| ResetPassword | token, new_password | User.reset_password() | PasswordReset | void |
| UpdateProfile | user_id, display_name, avatar | User.update_profile() | ProfileCompleted (first time) | UserInfo |
| GetCurrentUser | user_id | Load user + profile | none | UserInfo |

### 7.3 Use Case Pattern

**Standard Flow:**
1. **Validation** - Controller validates request with Pydantic schema
2. **Load** - Use case loads aggregate(s) from repository
3. **Execute** - Use case invokes domain method on aggregate
4. **Collect Events** - Aggregate collects domain events
5. **Persist** - Use case saves aggregate via repository
6. **Publish** - Use case publishes collected events to event bus
7. **Return** - Use case returns result to controller

**Transactional Boundary:**
- Use case is the transaction boundary
- All database operations in one transaction
- Events published after successful commit

### 7.4 Queries (Read Operations)

| Query | Input | Data Source | Caching | Return |
|-------|-------|-------------|---------|--------|
| GetUserById | user_id | users table | 5 min (profile data) | User + Profile |
| GetUserByEmail | email | users table (indexed) | No cache (auth) | User + Profile |

**Query Pattern:**
- Separate from commands (CQRS-lite)
- Can bypass domain layer for simple reads
- Direct database queries for performance
- Cache when appropriate

---

## 8. Infrastructure Layer Design

### 8.1 Repository Pattern

**IUserRepository Interface (Domain):**
```
Interface: IUserRepository
  - get_by_id(user_id: UserId) → User | None
  - get_by_email(email: str) → User | None
  - save(user: User) → void
  - delete(user_id: UserId) → void
```

**Implementation: SqlAlchemyUserRepository (Infrastructure)**
- Maps between domain entities and SQLAlchemy models
- Handles database transactions
- Converts database rows to domain objects
- Converts domain objects to database rows

**Mapping Strategy:**
```
Domain Entity (User) ←→ Database Model (UserModel)
       │                        │
       │                        ├─ Table: users
       │                        ├─ Columns: id, email, hashed_password, etc.
       │                        │
       └─ Profile ←→ ProfileModel
                                │
                                └─ Table: profiles
```

**Key Principles:**
- Domain entities don't know about database
- Repository implementation knows both
- Separate models for persistence
- Async/await throughout

### 8.2 External Service Integration

| Service | Purpose | Integration Pattern | Error Handling |
|---------|---------|---------------------|----------------|
| **Email (SMTP)** | Send verification/reset emails | Async event handler | Log error, don't fail request |
| **Redis** | Token blacklist, rate limiting | Direct async calls | Graceful degradation (fail open for reads) |
| **PostgreSQL** | Primary data store | SQLAlchemy async | Transaction rollback, propagate error |

**Email Service Architecture:**
```
Domain Event (UserRegistered)
     │
     ▼
[Event Handler] ──prepares data──► [EmailService]
                                         │
                                         ├─ loads template
                                         ├─ renders with data
                                         │
                                         ▼
                                   [fastapi-mail]
                                         │
                                         ▼
                                   [SMTP Server]
```

**Error Handling Strategy:**
- Email failures don't fail the request (async)
- Redis failures degrade gracefully (no rate limiting temporarily)
- Database failures propagate (critical errors)

### 8.3 Token Management

**JWT Token Generation:**
- Access tokens: Short-lived (30 min), stateless
- Refresh tokens: Long-lived (7-30 days), blacklist tracked in Redis

**Token Structure:**
```json
{
  "sub": "user_id",
  "type": "access" | "refresh",
  "exp": 1234567890,
  "iat": 1234567890
}
```

**Blacklist (Redis):**
- Key: `blacklist:{token_hash}`
- Value: "1"
- TTL: Token expiry time
- Purpose: Invalidate refresh tokens on logout/password reset

### 8.4 Rate Limiting Architecture

**Implementation:** slowapi middleware + Redis backend

**Storage:**
```
Redis Key: rate_limit:{endpoint}:{identifier}
Value: request count
TTL: window duration (15 minutes)
```

**Identifier Strategy:**
- Registration: IP address
- Login: Email address
- Password reset: Email address

**Limits:**
- `/auth/register`: 5 requests per IP per 15 min
- `/auth/login`: 5 requests per email per 15 min
- `/auth/password/forgot`: 3 requests per email per 15 min

### 8.5 Configuration Management

**Configuration Structure:**
```
AuthSettings (pydantic_settings.BaseSettings)
├── Database
│   └── DATABASE_URL
├── JWT
│   ├── JWT_SECRET
│   ├── JWT_ALGORITHM
│   ├── ACCESS_TOKEN_EXPIRE_MINUTES
│   └── REFRESH_TOKEN_EXPIRE_DAYS
├── Email
│   ├── EMAIL_SMTP_HOST
│   ├── EMAIL_SMTP_PORT
│   ├── EMAIL_SMTP_USER
│   └── EMAIL_SMTP_PASSWORD
├── Redis
│   └── REDIS_URL
└── Tokens
    ├── VERIFICATION_TOKEN_EXPIRE_HOURS
    └── RESET_TOKEN_EXPIRE_HOURS
```

**Loading Strategy:**
- Environment variables (.env file)
- Validation via Pydantic
- Type-safe access
- Fail fast on missing required config

### 8.6 Database Access Pattern

**Connection Management:**
- Async connection pool (SQLAlchemy)
- Pool size: 5-20 connections
- Connection timeout: 30 seconds
- Statement timeout: 10 seconds

**Transaction Pattern:**
```
async with get_db_session() as session:
    async with session.begin():
        # All database operations
        # Auto-commit on success
        # Auto-rollback on exception
```

**Query Optimization:**
- Use indexes on all foreign keys
- Use indexes on frequently queried columns (email, created_at)
- Eager load relationships when needed (joinedload)
- Avoid N+1 queries

### 9.1 Password Hashing

**Algorithm:** Argon2id via pwdlib

```python
# src/identity/domain/services/password_hasher.py

from pwdlib import PasswordHash

class PasswordHasher:
    def __init__(self):
        self._hasher = PasswordHash.recommended()

    def hash(self, password: str) -> HashedPassword:
        """Hash password with Argon2id"""
        hashed = self._hasher.hash(password)
        return HashedPassword(hashed)

    def verify(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return self._hasher.verify(password, hashed)
```

**Why Argon2id:**
- Memory-hard (resistant to GPU attacks)
- Industry standard (PHC winner 2015)
- Recommended by OWASP
- Faster verification than bcrypt

### 9.2 JWT Token Generation

```python
# src/identity/infrastructure/services/jwt_service.py

import jwt
from datetime import datetime, timedelta
from typing import Dict


class JWTService:
    def __init__(self, secret: str, algorithm: str = "HS256"):
        self._secret = secret
        self._algorithm = algorithm

    def create_access_token(
        self,
        user_id: str,
        expires_delta: timedelta
    ) -> str:
        payload = {
            "sub": user_id,
            "type": "access",
            "exp": datetime.utcnow() + expires_delta,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def create_refresh_token(
        self,
        user_id: str,
        expires_delta: timedelta
    ) -> str:
        payload = {
            "sub": user_id,
            "type": "refresh",
            "exp": datetime.utcnow() + expires_delta,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode_token(self, token: str) -> Dict:
        return jwt.decode(
            token,
            self._secret,
            algorithms=[self._algorithm]
        )
```

### 9.3 Rate Limiting

**Library:** slowapi (FastAPI middleware)

```python
# src/identity/interface/api/middleware/rate_limit.py

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379"
)

# Apply to specific endpoints
@app.post("/api/v1/auth/register")
@limiter.limit("5/15minutes")
async def register(request: Request, ...):
    ...
```

### 9.4 Input Sanitization

All input validated via Pydantic schemas:
- Email: Validated with EmailStr
- Passwords: Length checks (8-128 chars)
- Display names: Trim, length check, no HTML
- Tokens: Format validation

---

## 9. Security Implementation

### 9.1 Password Hashing

**Algorithm:** Argon2id (via pwdlib)

**Properties:**
- Memory-hard (resistant to GPU/ASIC attacks)
- Configurable memory cost, time cost, parallelism
- Recommended by OWASP for password storage
- Faster verification than bcrypt for legitimate users

**Implementation Pattern:**
- PasswordHasher domain service encapsulates hashing logic
- Hash passwords during registration and password reset
- Verify passwords during login
- Never log or expose plaintext passwords

### 9.2 JWT Token Security

**Token Types:**
1. **Access Token**
   - Purpose: API authorization
   - Lifetime: 30 minutes
   - Claims: user_id (sub), type, exp, iat
   - Algorithm: HS256
   - Secret: 256-bit minimum

2. **Refresh Token**
   - Purpose: Obtain new access tokens
   - Lifetime: 7 days (default) or 30 days (remember me)
   - Claims: user_id (sub), type, exp, iat
   - Blacklist: Tracked in Redis for revocation
   - Rotation: New refresh token issued on each refresh

**Security Measures:**
- Strong secret key (random, 256+ bits)
- Token rotation on refresh (old token blacklisted)
- Blacklist check on every refresh request
- All tokens invalidated on password reset
- Short access token lifetime limits exposure

### 9.3 Token Storage (Frontend)

**Recommended Strategy:**
- **Access Token:** Memory only (React state/context)
  - Lost on page refresh (acceptable - use refresh token)
  - Not accessible to XSS attacks

- **Refresh Token:** httpOnly cookie
  - Cannot be accessed by JavaScript
  - Secure flag (HTTPS only)
  - SameSite=Strict (CSRF protection)
  - Automatic inclusion in requests

**Alternative (if cookies not feasible):**
- Both tokens in memory
- Implement token refresh on app load
- Shorter refresh token lifetime

### 9.4 Rate Limiting Implementation

**Tool:** slowapi + Redis

**Configuration per Endpoint:**
```
Registration: 5 requests / 15 minutes per IP
Login: 5 requests / 15 minutes per email
Password Reset: 3 requests / 15 minutes per email
Verification Resend: 3 requests / 15 minutes per email
```

**Storage Pattern:**
- Redis key: `rate_limit:{endpoint}:{identifier}`
- Value: counter
- TTL: window duration
- Increment on each request
- Return 429 when limit exceeded

**Response on Rate Limit:**
```json
{
  "error": {
    "code": "rate_limited",
    "message": "Too many attempts. Please try again in X minutes.",
    "retry_after": 900
  }
}
```

### 9.5 Input Validation & Sanitization

**Validation Layers:**
1. **Pydantic Schemas** (API layer)
   - Type checking
   - Format validation (email, URL)
   - Length constraints
   - Pattern matching

2. **Value Objects** (Domain layer)
   - Business rule validation
   - Normalization (lowercase email, trim strings)
   - Immutability enforcement

3. **Database Constraints**
   - Unique constraints (email)
   - NOT NULL constraints
   - Foreign key constraints
   - Check constraints

**Sanitization:**
- Email: Lowercase, trim whitespace
- Display name: Trim whitespace, reject HTML/scripts
- Passwords: Length check only (no character restrictions per NIST guidance)
- Tokens: Constant-time comparison (prevent timing attacks)

### 9.6 CORS Configuration

**Development:**
```
Allowed Origins: http://localhost:5173, http://localhost:3000
Allowed Methods: GET, POST, PUT, DELETE, OPTIONS
Allowed Headers: Content-Type, Authorization
Credentials: true (for cookies)
```

**Production:**
```
Allowed Origins: https://koulu.app (specific domain)
Allowed Methods: GET, POST, PUT, DELETE, OPTIONS
Allowed Headers: Content-Type, Authorization
Credentials: true
Max Age: 86400 (cache preflight for 24h)
```

### 9.7 Security Headers

**Required Headers:**
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
```

### 9.8 Audit Logging

**Logged Events:**
- Registration attempts (success/failure)
- Login attempts (success/failure, with IP)
- Email verification attempts
- Password reset requests
- Password changes
- Failed authentication (rate limiting triggers)

**Log Format (Structured JSON):**
```json
{
  "event": "login_attempt",
  "result": "success" | "failure",
  "user_id": "uuid",
  "email": "user@example.com",
  "ip_address": "192.168.1.1",
  "user_agent": "...",
  "timestamp": "2026-02-05T10:00:00Z",
  "error_code": "invalid_credentials" (if failure)
}
```

**Retention:**
- Store in separate audit log table or external service
- Retention period: 90 days minimum (configurable)
- Never log passwords or tokens

---

## 10. Error Handling

### 10.1 Error Response Format

```json
{
  "error": {
    "code": "invalid_email",
    "message": "Please enter a valid email address",
    "details": {
      "field": "email",
      "value": "not-an-email"
    }
  }
}
```

### 10.2 Domain Exceptions → HTTP Mapping

| Domain Exception | HTTP Status | Error Code | User Message |
|------------------|-------------|------------|--------------|
| `InvalidEmailError` | 400 | `invalid_email` | "Please enter a valid email address" |
| `PasswordTooShortError` | 400 | `password_too_short` | "Password must be at least 8 characters" |
| `EmailAlreadyExistsError` | 409 | `email_exists` | "An account with this email already exists" |
| `InvalidCredentialsError` | 401 | `invalid_credentials` | "Invalid email or password" |
| `EmailNotVerifiedError` | 401 | `email_not_verified` | "Please verify your email before logging in" |
| `AccountDisabledError` | 403 | `account_disabled` | "This account has been disabled" |
| `InvalidTokenError` | 400 | `invalid_token` | "Invalid or expired token" |
| `AlreadyVerifiedError` | 400 | `already_verified` | "Email is already verified" |
| `InvalidDisplayNameError` | 400 | `invalid_display_name` | "Display name must be 2-50 characters" |

### 10.3 Exception Handler Middleware

```python
# src/identity/interface/api/middleware/error_handler.py

from fastapi import Request, status
from fastapi.responses import JSONResponse
from ...domain.exceptions import DomainException


async def domain_exception_handler(
    request: Request,
    exc: DomainException
) -> JSONResponse:
    """Convert domain exceptions to HTTP responses"""
    return JSONResponse(
        status_code=exc.http_status,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )
```

---

## 11. Testing Strategy

### 11.1 Unit Tests

**Scope:** Domain logic (entities, value objects, services)

**Framework:** pytest

**Examples:**
- `test_user_register()` - User.register() creates valid user
- `test_email_validation()` - EmailAddress rejects invalid formats
- `test_password_hasher()` - PasswordHasher hashes and verifies correctly
- `test_display_name_validation()` - DisplayName enforces length rules

### 11.2 Integration Tests

**Scope:** API endpoints, repository implementations

**Framework:** pytest + httpx

**Examples:**
- `test_register_endpoint()` - POST /api/v1/auth/register creates user in DB
- `test_login_endpoint()` - POST /api/v1/auth/login returns valid JWT
- `test_user_repository()` - SqlAlchemyUserRepository CRUD operations

### 11.3 BDD Tests

**Scope:** All 36 scenarios in `registration_authentication.feature`

**Framework:** pytest-bdd

**Implementation:**
```python
# tests/features/identity/test_registration_authentication.py

from pytest_bdd import scenarios, given, when, then

scenarios('registration_authentication.feature')

@given('no user exists with email "newuser@example.com"')
def no_user_exists(db_session):
    # Clean up any existing user
    pass

@when('a user registers with email "newuser@example.com" and password "securepass123"')
async def user_registers(client, context):
    response = await client.post('/api/v1/auth/register', json={
        'email': 'newuser@example.com',
        'password': 'securepass123'
    })
    context['response'] = response

@then('a new user account should be created with email "newuser@example.com"')
async def user_created(db_session, context):
    user = await db_session.execute(
        select(User).where(User.email == 'newuser@example.com')
    )
    assert user is not None
```

### 11.4 Test Coverage Goal

- Domain layer: 100%
- Application layer: 90%
- Infrastructure layer: 80%
- Overall: 85%+

---

## 12. Performance Considerations

### 12.1 Database Optimizations

- **Connection pooling:** SQLAlchemy async pool (min=5, max=20)
- **Indexes:** All foreign keys and frequently queried fields indexed
- **Query optimization:** Use select() with specific columns, avoid N+1 queries
- **Prepared statements:** SQLAlchemy uses prepared statements by default

### 12.2 Caching Strategy

| Cache Target | TTL | Invalidation |
|--------------|-----|--------------|
| User profile (by user_id) | 5 minutes | On profile update |
| Token blacklist | Token expiry | Automatic (Redis TTL) |

### 12.3 Async Operations

- **Email sending:** Fire-and-forget with event handlers
- **Token cleanup:** Background scheduler (APScheduler) every hour
- **Audit logging:** Async write to separate log stream

---

## 13. Observability

### 13.1 Logging

**Library:** structlog

**Log Levels:**
- INFO: Successful operations (login, registration)
- WARNING: Failed auth attempts, rate limits hit
- ERROR: Unexpected errors, email sending failures

**Structured Log Example:**
```json
{
  "event": "user_registered",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "ip_address": "192.168.1.1",
  "timestamp": "2026-02-05T10:00:00Z",
  "level": "info"
}
```

### 13.2 Metrics

**Library:** OpenTelemetry + Prometheus

**Key Metrics:**
- `auth_registration_total` (counter) - Total registrations
- `auth_registration_failures_total` (counter, by reason) - Failed registrations
- `auth_login_total` (counter) - Total logins
- `auth_login_failures_total` (counter, by reason) - Failed logins
- `auth_email_verification_time` (histogram) - Time to verify email
- `auth_request_duration_seconds` (histogram) - Endpoint latency

### 13.3 Tracing

**Library:** OpenTelemetry

**Traced Operations:**
- HTTP request/response
- Database queries
- External service calls (email)
- Domain event publishing

**Span naming:** `{service}.{operation}` (e.g., `identity.register_user`)

---

## 14. Migration & Deployment

### 14.1 Database Migrations

```bash
# Create initial migration
alembic revision -m "create_identity_tables"

# Generated migration file: migrations/versions/20260205_1000_create_identity_tables.py
# - Create users table
# - Create profiles table
# - Create verification_tokens table
# - Create reset_tokens table
# - Create indexes

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### 14.2 Deployment Steps

1. **Pre-deployment:**
   - Run database migrations
   - Update environment variables
   - Test in staging environment

2. **Deployment:**
   - Deploy backend API (FastAPI)
   - Deploy frontend (React build)
   - Restart services

3. **Post-deployment:**
   - Smoke tests (health check endpoint)
   - Monitor error rates for 1 hour
   - Verify email sending works

### 14.3 Rollback Plan

**If deployment fails:**
1. Rollback code to previous version
2. Rollback database migration: `alembic downgrade -1`
3. Restart services
4. Investigate root cause

**Database rollback safety:**
- All migrations include `downgrade()` method
- No data loss on rollback (only schema changes)
- Test rollbacks in staging first

---

## 15. Open Questions

- [x] Email provider choice? → Use SendGrid (or configurable SMTP)
- [x] Redis cluster or single instance? → Single instance for MVP, cluster for production
- [ ] Avatar upload storage? → S3 or Cloudinary (TBD Phase 2)
- [ ] Audit log retention period? → 90 days (TBD)

---

## 16. Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-05 | Claude | Initial technical design with code samples |
| 1.1 | 2026-02-05 | Claude | Refactored to architectural level (removed code, added diagrams/flows) |

---

## 17. References

- **PRD:** `docs/features/identity/registration-authentication-prd.md`
- **BDD Spec:** `tests/features/identity/registration_authentication.feature`
- **GLOSSARY:** `docs/domain/GLOSSARY.md`
- **CONTEXT_MAP:** `docs/architecture/CONTEXT_MAP.md`
- **Library Documentation:**
  - [fastapi-users](https://fastapi-users.github.io/fastapi-users/)
  - [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
  - [pwdlib](https://github.com/fastapi/pwdlib)
  - [fastapi-mail](https://sabuhish.github.io/fastapi-mail/)
  - [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- **Security Standards:**
  - [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
  - [JWT Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)
