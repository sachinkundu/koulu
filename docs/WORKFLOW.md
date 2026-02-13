# Development Workflow

This document describes the end-to-end workflow for building features in Koulu.

---

## Overview

```
OVERVIEW_PRD → Screenshots → Feature PRD + BDD → UI_SPEC → Technical Design → Phase Plan → Implementation → Testing → Review
   (Master)     (Skool.com)    (Product)          (Visual)   (Engineering)     (Planning)    (Code)          (BDD)     (PR)
```

**Key principle:** Screenshots come FIRST. They are the source of truth for Skool.com's design patterns and directly inform the PRD's UI Behavior section. This prevents backward iteration when the UI_SPEC later discovers discrepancies with the PRD.

---

## Phase 1: Master Planning (Done)

**Document:** `docs/prd_summary/PRD/OVERVIEW_PRD.md`

**Purpose:** High-level product vision, all features listed

**Owner:** Product/Founder

**Output:** List of features with priorities (Phase 1 MVP, Phase 2, Phase 3)

---

## Phase 2: Gather Screenshots (Before Specs)

**Purpose:** Capture how Skool.com implements this feature — the visual source of truth

**Owner:** Product Manager / Founder

**Workflow:**
1. Browse Skool.com and navigate to the feature being built
2. Capture screenshots of all relevant views (list/grid, filters, cards, modals, empty states)
3. Save to `docs/features/[context]/screenshots/`

**Output Files:**
- `docs/features/[context]/screenshots/*.png`

**Why this comes first:** Screenshots contain design decisions (list vs grid, pills vs dropdown, card content) that must flow INTO the PRD. If screenshots are analyzed after the PRD, discrepancies cascade backward through all documents.

---

## Phase 3: Feature Specification (PRD + BDD)

**Skill:** `/write-feature-spec`

**Purpose:** Define WHAT to build from product perspective, informed by Skool.com screenshots

**Owner:** Product Manager (or founder wearing PM hat)

**Workflow:**
1. Pick a feature from OVERVIEW_PRD
2. Claude analyzes Skool.com screenshots to extract design decisions (layout, filters, card content)
3. Claude researches codebase and asks clarifying questions
4. You answer questions about desired behavior
5. Claude generates:
   - **PRD**: Product requirements (what, why, user stories, business rules) — UI Behavior section informed by screenshots
   - **BDD Spec**: Executable acceptance criteria in Gherkin

**Output Files:**
- `docs/features/[context]/[feature]-prd.md`
- `tests/features/[context]/[feature].feature`

**Review:** You review PRD for correctness, completeness, alignment with vision

**What PRD Contains:**
- ✅ User stories, business rules, UI behavior (screenshot-informed), interactions
- ❌ NO libraries, DB schema, code patterns (those come later)

---

## Phase 4: UI Specification

**Skill:** `/generate-ui-spec`

**Purpose:** Detail the visual approach with component specs, design tokens, and spacing

**Owner:** Design / Engineering

**Workflow:**
1. Claude reads the approved PRD and the same screenshots used in Phase 3
2. Claude maps screenshot elements to the design system and existing components
3. Claude generates detailed component specifications with Tailwind classes

**Output Files:**
- `docs/features/[context]/UI_SPEC.md`

**Key principle:** Since the PRD already incorporates screenshot insights, the UI_SPEC **confirms and details** the visual approach. It should NOT discover discrepancies — if it does, the workflow was not followed correctly.

---

## Phase 5: Technical Design (TDD)

**Skill:** `/write-technical-design`

**Purpose:** Define HOW to build from engineering perspective

**Owner:** Engineering Lead/Architect

**Workflow:**
1. After PRD + UI_SPEC approval, start TDD
2. Claude reads PRD, BDD, and UI_SPEC (for frontend component names)
3. Claude researches industry-standard libraries and patterns
4. Claude asks technical questions if needed
5. Claude generates Technical Design Document

**Output File:**
- `docs/features/[context]/[feature]-tdd.md`

**Review:** Engineers review for architecture, technology choices, feasibility

**What TDD Contains:**
- ✅ Libraries, DB schema, implementation patterns, architecture
- ✅ Domain layer design, infrastructure setup
- ✅ Security implementation, observability strategy
- ✅ Frontend file checklist with component names from UI_SPEC

**Key Principle:** Use industry-standard libraries over custom code

---

## Phase 6a: Implementation Planning

**Skill:** `/create-phase-plan`

**Purpose:** Analyze specs and create phased implementation plan with granular tasks

**Owner:** Engineering Lead/Architect

**Workflow:**
1. Read PRD + BDD + TDD + UI_SPEC
2. Analyze complexity and choose phasing strategy
3. Distribute BDD scenarios across phases
4. Generate phase plan document
5. Generate Phase 1 granular task plan

**Output Files:**
- `docs/features/[context]/[feature]-implementation-phases.md`
- `docs/features/[context]/[feature]-phase-1-tasks.md`

**Review:** Engineers review phase plan for approach, scope, and feasibility

---

## Phase 6b: Implementation

**Skill:** `/implement-feature`

**Purpose:** Execute a single phase from the implementation plan

**Owner:** Engineers (or Claude as engineer)

**Workflow:**
1. Auto-detect granular task plan for the phase
2. Follow tasks in TDD order (failing test -> implement -> verify)
3. Run verification scripts
4. Generate manual testing guide

**Output:**
- Source code in `src/`
- Unit/integration tests

**Definition of Done:**
- All BDD scenarios for this phase pass
- Unit tests pass
- Verification scripts pass
- Code follows CLAUDE.md rules

---

## Phase 7: Review & Merge

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
| **Screenshots** | Visual reference | Product, design, engineers | Skool.com reference images — source of truth for UI patterns |
| **Feature PRD** | What to build | Product, stakeholders, engineers | User stories, business rules, UI behavior (screenshot-informed) |
| **BDD Spec** | Acceptance criteria | Product, QA, engineers | Executable scenarios in plain language |
| **UI_SPEC** | Visual details | Design, frontend engineers | Component specs, design tokens, spacing, interactive states |
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

## Example: Member Directory

```
1. OVERVIEW_PRD lists "Member Directory" in Phase 1 MVP

2. Screenshots (docs/features/members/screenshots/):
   - directory.png — Skool member list page (vertical list, pill tabs, sidebar)
   - invite.png — Invite modal overlay

3. Feature PRD (directory-prd.md):
   - User can browse a list of all community members
   - Filter by role via pill tabs with counts (informed by screenshots)
   - Vertical list layout with sidebar (informed by screenshots)
   - NO mention of SQL JOINs, TanStack Query, etc.

4. BDD Spec (directory.feature):
   - Scenario: View member directory as a community member
   - Scenario: Filter members by admin role
   - Etc.

5. UI_SPEC (UI_SPEC.md):
   - Component specs: MemberCard, MemberFilters, MemberList
   - Design tokens, spacing, interactive states
   - Confirms PRD's layout/filter decisions with detailed Tailwind classes

6. TDD (directory-tdd.md):
   - Infrastructure SQL JOIN for cross-context query
   - Cursor-based pagination
   - Frontend file checklist with component names from UI_SPEC (MemberList, not MemberGrid)

7. Implementation:
   - src/community/application/queries/list_members_query.py
   - frontend/src/features/members/components/MemberCard.tsx
   - Etc.

8. Testing:
   - BDD scenarios implemented with pytest-bdd
   - Unit tests for domain logic
   - E2E tests for UI

9. Review & Merge:
   - PR created with all files
   - Tests passing
   - Code reviewed
   - Merged to main
```

---

## Quick Reference

| I want to... | Skill / Action | Which creates... |
|--------------|----------------|------------------|
| Capture Skool.com reference | Manual screenshot capture | `docs/features/[context]/screenshots/*.png` |
| Define what feature to build | `/write-feature-spec` | PRD + BDD (screenshot-informed) |
| Detail the visual approach | `/generate-ui-spec` | UI_SPEC.md |
| Design how to implement | `/write-technical-design` | TDD (references UI_SPEC) |
| Plan implementation phases | `/create-phase-plan` | Phase plan + Phase 1 tasks |
| Execute implementation phases | `/implement-feature` | Source code |
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
