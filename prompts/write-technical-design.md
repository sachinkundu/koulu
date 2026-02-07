# Prompt: Write Technical Design Document (TDD)

## Purpose

After a PRD is approved, create a Technical Design Document that specifies HOW to implement the feature using the project's technology stack.

---

## Context

You are an engineering architect translating product requirements into technical implementation specifications.

**Input:**
- Approved PRD from `docs/features/[context]/[feature]-prd.md`
- BDD specification from `tests/features/[context]/[feature].feature`
- Project architecture (CLAUDE.md, architecture docs, GLOSSARY)

**Output:**
- Technical Design Document at `docs/features/[context]/[feature]-tdd.md`

---

## Research Phase

Before writing the TDD, research:

1. **Review the PRD and BDD specs** - Understand all requirements
2. **Check existing architecture patterns** - How similar features are implemented
3. **Read project constraints** - Tech stack from CLAUDE.md, DDD patterns from architecture docs
4. **Research libraries** - Find industry-standard solutions (see Library Research Protocol below)
5. **Review domain model** - Ensure technical design aligns with DDD principles

---

## Library Research Protocol

**IMPORTANT: Always prefer industry-standard libraries over custom implementation.**

For each technical need:
1. Web search for "best [technology] library 2025/2026" (e.g., "FastAPI authentication library 2026")
2. Evaluate options based on:
   - Production readiness and maturity
   - Active maintenance and community
   - Integration with existing stack
   - Documentation quality
   - Performance and security
3. Document library choices with justification

---

## TDD Structure

```markdown
# [Feature Name] - Technical Design Document

**Version:** 1.0
**Date:** [Date]
**Status:** Draft
**Related PRD:** `[path-to-prd]`
**Bounded Context:** [Context Name]

---

## 1. Overview

### 1.1 Summary
[1-2 sentence summary of what this TDD covers]

### 1.2 Goals
- [Technical goal 1]
- [Technical goal 2]

### 1.3 Non-Goals
- [What this TDD does NOT cover]

---

## 2. Architecture

### 2.1 System Context

[Diagram or description of where this feature fits in the system]

### 2.2 Component Architecture

[Hexagonal architecture layers for this feature]

```
┌─────────────────────────────────────────┐
│           Interface Layer               │
│     (Controllers, API routes)           │
├─────────────────────────────────────────┤
│         Application Layer               │
│    (Commands, Queries, Use Cases)       │
├─────────────────────────────────────────┤
│           Domain Layer                  │
│  (Entities, Value Objects, Events)      │
├─────────────────────────────────────────┤
│       Infrastructure Layer              │
│   (Repositories, External Services)     │
└─────────────────────────────────────────┘
```

### 2.3 Domain-Driven Design

**Aggregates:**
- [Aggregate Root 1] - [Responsibility]
- [Aggregate Root 2] - [Responsibility]

**Value Objects:**
- [Value Object 1] - [Purpose]

**Domain Events:**
- [Event 1] - [When published]

**Repositories:**
- [Repository 1] - [Interface definition]

---

## 3. Technology Stack

### 3.1 Backend

| Technology | Version | Purpose | Justification |
|------------|---------|---------|---------------|
| [Library 1] | ^X.Y | [Purpose] | [Why chosen over alternatives] |
| [Library 2] | ^X.Y | [Purpose] | [Why chosen] |

### 3.2 Frontend

| Technology | Version | Purpose | Justification |
|------------|---------|---------|---------------|
| [Library 1] | ^X.Y | [Purpose] | [Why chosen] |

### 3.3 Infrastructure

| Technology | Purpose |
|------------|---------|
| PostgreSQL | Primary database |
| Redis | Caching, rate limiting |

---

## 4. Database Design

### 4.1 Schema

```sql
-- [Table 1]
CREATE TABLE [table_name] (
    -- columns with types, constraints, indexes
);

-- [Table 2]
...
```

### 4.2 Indexes

| Table | Index | Columns | Justification |
|-------|-------|---------|---------------|
| [table] | [name] | [cols] | [Why needed] |

### 4.3 Migrations

- Migration strategy (e.g., Alembic for Python)
- Migration file naming convention

---

## 5. API Implementation

### 5.1 Endpoint Implementation

For each API endpoint from the PRD, specify:

#### POST `/api/v1/[endpoint]`

**Controller:** `[ModuleName]Controller.method_name()`

**Request Validation:**
```python
class [RequestSchema](BaseModel):
    field: type = Field(validation_rules)
```

**Use Case:** `[UseCaseName]`

**Flow:**
1. Controller receives request
2. Validates with schema
3. Calls use case
4. Use case invokes domain logic
5. Publishes events
6. Returns response

**Error Handling:**
- [ErrorType1] → HTTP 4XX with error code
- [ErrorType2] → HTTP 5XX with error code

---

## 6. Domain Layer Design

### 6.1 Aggregate Structure

**[Aggregate Root Name]:**
- **Responsibilities:** [What it controls]
- **Invariants:** [Rules it enforces]
- **Key Operations:** [Domain methods list]
- **Events Published:** [List of events]

**Relationship Diagram:**
```
[Aggregate Root]
    ├── [Child Entity 1]
    └── [Child Entity 2]
```

### 6.2 Value Objects

| Value Object | Properties | Validation Rules | Purpose |
|--------------|------------|------------------|---------|
| [Name] | [Fields] | [Rules] | [Why needed] |

### 6.3 Domain Events

| Event | Trigger | Payload | Consumers |
|-------|---------|---------|-----------|
| [EventName] | [When published] | [Data fields] | [Who listens] |

### 6.4 State Transitions

**[Entity] State Machine:**
```
[State 1] --[action]--> [State 2]
[State 2] --[action]--> [State 3]
```

---

## 7. Application Layer

### 7.1 Command/Query Flow

**Sequence Diagram for [Key Use Case]:**
```
Client → Controller → Use Case → Repository → Database
                          ↓
                    Event Publisher → Event Handlers
```

### 7.2 Commands

| Command | Inputs | Outputs | Triggered By |
|---------|--------|---------|--------------|
| [CommandName] | [Data] | [Result] | [Trigger] |

### 7.3 Queries

| Query | Inputs | Outputs | Caching |
|-------|--------|---------|---------|
| [QueryName] | [Params] | [Data] | [Strategy] |

### 7.4 Use Case Patterns

**[UseCaseName] Flow:**
1. Validate command inputs
2. Load aggregate from repository
3. Execute domain operation
4. Collect and publish domain events
5. Save aggregate
6. Return result

---

## 8. Infrastructure Layer

### 8.1 Repository Pattern

**Interface:** `I[Entity]Repository`
- get_by_id(id) → Entity
- get_by_[field](value) → Entity
- save(entity) → void
- delete(id) → void

**Implementation:** SQLAlchemy-based with async/await

**Mapping Strategy:** Separate database models from domain entities

### 8.2 External Services

| Service | Purpose | Library | Integration Pattern |
|---------|---------|---------|---------------------|
| Email | Transactional emails | [library] | Async event handler |
| [Other] | [Purpose] | [library] | [Pattern] |

### 8.3 Configuration

**Environment Variables Structure:**
```
DATABASE_URL=postgresql://...
JWT_SECRET=...
EMAIL_*=...
REDIS_URL=...
```

See detailed list in implementation phase.

---

## 9. Security Implementation

### 9.1 Authentication

- Token generation: [How]
- Token validation: [How]
- Token storage: [Where]

### 9.2 Authorization

- Permission checks: [Where and how]
- Role-based access: [Implementation]

### 9.3 Data Protection

- Password hashing: [Algorithm and library]
- Sensitive data encryption: [Approach]
- Input sanitization: [Tools]

### 9.4 Rate Limiting

- Implementation: [Library/approach]
- Storage: [Redis/in-memory]
- Configuration per endpoint

---

## 10. Error Handling

### 10.1 Error Types

| Domain Exception | HTTP Status | Error Code | User Message |
|------------------|-------------|------------|--------------|
| [DomainError1] | 400 | `error_code` | [Message] |

### 10.2 Error Response Format

```json
{
  "error": {
    "code": "error_code",
    "message": "User-friendly message",
    "details": {}
  }
}
```

---

## 11. Testing Strategy

### 11.1 Unit Tests

- Domain logic (entities, value objects)
- Use cases
- Utilities

### 11.2 Integration Tests

- API endpoints
- Repository implementations
- External service integrations

### 11.3 BDD Tests

- Implement scenarios from `[feature].feature`
- Use pytest-bdd for Python, cucumber-js for frontend

---

## 12. Performance Considerations

### 12.1 Database

- Query optimization strategies
- Index strategy
- Connection pooling

### 12.2 Caching

- What to cache
- Cache invalidation strategy
- TTL values

### 12.3 Async Operations

- Email sending (background job)
- Event publishing (async)

---

## 13. Observability

### 13.1 Logging

**Structured logs for:**
- Authentication attempts
- Domain events
- Error scenarios

**Format:** JSON with context (user_id, request_id, timestamp)

### 13.2 Metrics

- Request latency (p50, p95, p99)
- Error rates
- Authentication success/failure rates

### 13.3 Tracing

- OpenTelemetry spans for key operations
- Distributed tracing across services

---

## 14. Migration & Deployment

### 14.1 Database Migrations

```bash
# Create migration
alembic revision -m "create users table"

# Apply migration
alembic upgrade head
```

### 14.2 Deployment Steps

1. [Step 1]
2. [Step 2]
3. [Step 3]

### 14.3 Rollback Plan

- How to rollback database changes
- How to rollback code deployment

---

## 15. Open Questions

- [ ] Question 1 - [Need input from]
- [ ] Question 2 - [Need decision on]

---

## 16. Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [Date] | [Author] | Initial draft |

---

## 17. References

- PRD: `[path]`
- BDD Spec: `[path]`
- Related TDDs: `[paths]`
- Library documentation links
```

---

## Quality Checklist

Before finalizing:

- [ ] All PRD requirements have technical specifications
- [ ] Library choices researched and justified
- [ ] Database schema aligns with domain model
- [ ] Security requirements have concrete implementations
- [ ] Error handling covers all edge cases from PRD
- [ ] Testing strategy covers BDD scenarios
- [ ] No product/business decisions (those stay in PRD)
- [ ] Implementation is concrete enough to start coding
- [ ] Follows project architecture patterns (DDD, hexagonal)
- [ ] **Create ALIGNMENT_VERIFICATION.md** (mandatory - see below)

---

## Alignment Verification (MANDATORY)

After completing the TDD, create an alignment verification document:

**File:** `docs/features/[context]/ALIGNMENT_VERIFICATION.md`

**Purpose:** Ensure PRD, BDD, and TDD are perfectly aligned

**Contents:**
1. Verification matrix mapping PRD requirements → BDD scenarios → TDD sections
2. Domain events consistency check
3. API endpoints alignment check
4. Business rules coverage
5. Summary with alignment percentage

**Example structure:**
```markdown
# PRD-BDD-TDD Alignment Verification

| Requirement | PRD | BDD | TDD | Status |
|-------------|-----|-----|-----|--------|
| Email registration | ✅ Section 5.1 | ✅ Scenario: Successful registration | ✅ Section 5.1 | ✅ |
| Invalid email error | ✅ Section 5.1 | ✅ Scenario: Registration fails with invalid email | ✅ Section 5.1 | ✅ |
...
```

**If misalignment found:**
1. Fix the mismatch (update PRD, BDD, or TDD as needed)
2. Re-verify alignment
3. Document the fix in ALIGNMENT_VERIFICATION.md

---

## Notes

- **Think like a Technical Architect, not a Developer**
  - Focus on architecture, patterns, and design decisions
  - Use diagrams: UML, sequence, state machines, data flow
  - Describe component interactions and contracts
  - NO detailed code implementations (those come in implementation phase)

- **What TO include:**
  - Architecture diagrams and component relationships
  - Technology choices with justifications
  - API request/response payload structures
  - Database schema (SQL)
  - State transition diagrams
  - Sequence diagrams for complex flows
  - Integration points and contracts

- **What NOT to include:**
  - Full class implementations with method bodies
  - Detailed Python/TypeScript code
  - Line-by-line pseudo-code
  - Complete function implementations

- **Code snippets only for:**
  - Configuration examples
  - Data structure shapes (schemas)
  - SQL DDL (CREATE TABLE)
  - Critical algorithm descriptions (high-level)

- **Example comparison:**
  - ❌ "```python\nclass User:\n    def register(self, email, password):\n        if len(password) < 8:\n            raise PasswordTooShortError()\n        ...\n```"
  - ✅ "User aggregate implements registration with password validation (min 8 chars). On success, publishes UserRegistered event. See sequence diagram for flow."

- **Reference standards** - Link to OWASP, security best practices, etc.
- **Consider future phases** - Design for extensibility where mentioned in PRD
