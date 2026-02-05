# Development Workflow

This document describes the end-to-end workflow for building features in Koulu.

---

## Overview

```
OVERVIEW_PRD → Feature PRD + BDD → Technical Design → Implementation → Testing → Review
   (Master)      (Product)            (Engineering)      (Code)         (BDD)     (PR)
```

---

## Phase 1: Master Planning (Done)

**Document:** `docs/prd_summary/PRD/OVERVIEW_PRD.md`

**Purpose:** High-level product vision, all features listed

**Owner:** Product/Founder

**Output:** List of features with priorities (Phase 1 MVP, Phase 2, Phase 3)

---

## Phase 2: Feature Specification (PRD + BDD)

**Prompt:** `prompts/write-feature-spec.md`

**Purpose:** Define WHAT to build from product perspective

**Owner:** Product Manager (or founder wearing PM hat)

**Workflow:**
1. Pick a feature from OVERVIEW_PRD
2. Claude researches codebase and asks clarifying questions
3. You answer questions about desired behavior
4. Claude generates:
   - **PRD**: Product requirements (what, why, user stories, business rules)
   - **BDD Spec**: Executable acceptance criteria in Gherkin

**Output Files:**
- `docs/features/[context]/[feature]-prd.md`
- `tests/features/[context]/[feature].feature`

**Review:** You review PRD for correctness, completeness, alignment with vision

**What PRD Contains:**
- ✅ User stories, business rules, API contracts, UI behavior
- ❌ NO libraries, DB schema, code patterns (those come next)

---

## Phase 3: Technical Design (TDD)

**Prompt:** `prompts/write-technical-design.md`

**Purpose:** Define HOW to build from engineering perspective

**Owner:** Engineering Lead/Architect

**Workflow:**
1. After PRD approval, start TDD
2. Claude researches industry-standard libraries and patterns
3. Claude asks technical questions if needed
4. Claude generates Technical Design Document

**Output File:**
- `docs/features/[context]/[feature]-tdd.md`

**Review:** Engineers review for architecture, technology choices, feasibility

**What TDD Contains:**
- ✅ Libraries, DB schema, implementation patterns, architecture
- ✅ Domain layer design, infrastructure setup
- ✅ Security implementation, observability strategy

**Key Principle:** Use industry-standard libraries over custom code

---

## Phase 4: Implementation

**Prompt:** `prompts/implement-feature.md` (to be created)

**Purpose:** Write the actual code

**Owner:** Engineers (or Claude as engineer)

**Workflow:**
1. Read PRD + BDD + TDD
2. Implement following hexagonal architecture + DDD
3. Write tests as you go
4. Run verification scripts

**Output:**
- Source code in `src/`
- Unit/integration tests

**Definition of Done:**
- All BDD scenarios pass
- Unit tests pass
- Verification scripts pass
- Code follows CLAUDE.md rules

---

## Phase 5: Review & Merge

**Purpose:** Quality gate before merging

**Workflow:**
1. Create PR
2. Review code against TDD
3. Verify BDD tests pass
4. Check verification scripts
5. Merge to main

---

## Document Separation of Concerns

| Document Type | Focus | Audience | Contains |
|---------------|-------|----------|----------|
| **OVERVIEW_PRD** | All features | Product, stakeholders | Feature list, priorities, high-level vision |
| **Feature PRD** | What to build | Product, stakeholders, engineers | User stories, business rules, API contracts, UI flows |
| **BDD Spec** | Acceptance criteria | Product, QA, engineers | Executable scenarios in plain language |
| **TDD** | How to build | Engineers | Architecture, libraries, DB schema, patterns |
| **Code** | Implementation | Engineers | Actual working software |

---

## Why This Separation?

| Benefit | Explanation |
|---------|-------------|
| **Clear ownership** | PM owns WHAT, engineers own HOW |
| **Technology flexibility** | Can change tech stack without rewriting PRD |
| **Better reviews** | Stakeholders review PRD, engineers review TDD |
| **Focused documents** | Each doc has one clear purpose and audience |
| **Decoupled decisions** | Product decisions independent from tech decisions |

---

## Example: User Authentication

```
1. OVERVIEW_PRD lists "User Registration & Authentication" in Phase 1

2. Feature PRD (registration-authentication-prd.md):
   - User can register with email/password
   - Email verification required
   - Password must be 8+ characters
   - API endpoint: POST /api/v1/auth/register
   - Returns 202 Accepted
   - NO mention of Argon2id, fastapi-users, etc.

3. BDD Spec (registration_authentication.feature):
   - Scenario: Successful registration with valid email
   - Scenario: Registration fails with password too short
   - Etc.

4. TDD (registration-authentication-tdd.md):
   - Use fastapi-users library (justification)
   - Password hashing: Argon2id via pwdlib
   - Database schema with SQL
   - JWT implementation details
   - Repository pattern with SQLAlchemy

5. Implementation:
   - src/identity/domain/entities/user.py
   - src/identity/application/commands/register_user.py
   - src/identity/infrastructure/repositories/user_repository.py
   - Etc.

6. Testing:
   - BDD scenarios implemented with pytest-bdd
   - Unit tests for domain logic
   - Integration tests for API

7. Review & Merge:
   - PR created with all files
   - Tests passing
   - Code reviewed
   - Merged to main
```

---

## Quick Reference

| I want to... | Use this document... | Which creates... |
|--------------|---------------------|------------------|
| Define what feature to build | `prompts/write-feature-spec.md` | PRD + BDD |
| Design how to implement | `prompts/write-technical-design.md` | TDD |
| Write the code | `prompts/implement-feature.md` | Source code |
| Understand project rules | `CLAUDE.md` | - |
| See all features | `docs/prd_summary/PRD/OVERVIEW_PRD.md` | - |

---

## Status: Current Feature

**Feature:** User Registration & Authentication

**Status:** PRD + BDD Complete (v1.2)

**Files:**
- ✅ `docs/features/identity/registration-authentication-prd.md`
- ✅ `tests/features/identity/registration_authentication.feature`
- ⏳ `docs/features/identity/registration-authentication-tdd.md` (Next step)

**Next Action:** Create TDD using `prompts/write-technical-design.md`
