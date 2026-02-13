---
name: write-feature-spec
description: Generate PRD and BDD specifications for a feature from OVERVIEW_PRD
user_invocable: true
model: sonnet
---

# Write Feature Spec (PRD + BDD)

## Purpose

Create a Product Requirements Document (PRD) AND executable BDD specifications for a feature. This defines the WHAT (product requirements). After PRD approval, use `/write-technical-design` to create the HOW (technical implementation).

---

## Usage

`/write-feature-spec <context>/<feature-name>`

Example: `/write-feature-spec community/posts`

**Parse the argument:**
- Split on `/` to get `<context>` and `<feature-name>`
- If no `/` found, ask user to provide format: `context/feature-name`

**Determine the correct bounded context:**
- ALWAYS read `docs/architecture/CONTEXT_MAP.md` and `docs/domain/GLOSSARY.md` BEFORE confirming which context to use
- Cross-reference the feature's domain concepts against the Context Map's bounded contexts
- Use the Glossary to identify which context owns the primary entities involved
- If the feature spans multiple contexts, place it in the context that owns the primary aggregate
- If user-provided context doesn't match the architecture, flag the discrepancy and recommend the correct context

**Screenshots (required for user-facing features):**
- Check if `docs/features/{context}/screenshots/` directory exists
- If it exists: use screenshots as visual reference when writing UI Behavior (Section 4) and layout decisions
- If it does NOT exist: **ask the user to provide Skool.com screenshots** of the equivalent feature before proceeding
- If the user cannot provide screenshots: **do not proceed** — screenshots are the source of truth for Skool.com-aligned design decisions and must be analyzed before writing the PRD
- Exception: non-UI features (background jobs, internal APIs) do not need screenshots

**Output files:**
- PRD: `docs/features/{context}/{feature}-prd.md`
- BDD: `tests/features/{context}/{feature}.feature`

---

## Phase 1: Research (Do This First)

Before asking ANY questions, thoroughly research the existing codebase and documentation:

### 1.1 Read Required Documents
- `docs/prd_summary/PRD/OVERVIEW_PRD.md` — Find the feature in Section 3 and Appendix A
- `docs/domain/GLOSSARY.md` — Load ubiquitous language
- `docs/architecture/CONTEXT_MAP.md` — Identify which bounded context(s) this belongs to
- `.claude/skills/architecture/SKILL.md` — Review DDD patterns (context sizing, aggregates, compliance checklist)
- `.claude/skills/bdd/SKILL.md` — Review Gherkin standards

### 1.2 Analyze Skool.com Screenshots

**This step is mandatory for user-facing features.** Screenshots are the source of truth for how Skool.com implements this feature and directly inform the PRD's UI Behavior section.

1. **Locate screenshots:** Check `docs/features/{context}/screenshots/`
2. **If not found:** Ask the user to provide Skool.com screenshots before continuing. Do not proceed without them for user-facing features.
3. **For each screenshot, extract:**
   - **Layout pattern:** List vs grid, sidebar presence, column structure
   - **Component types:** Cards, pills, tabs, dropdowns, modals
   - **Filter/sort patterns:** How does Skool let users filter and sort?
   - **Card/item content:** What fields are shown on each item?
   - **Interactive elements:** Buttons, links, hover states visible
4. **Create a Screenshot Summary** noting key design decisions that will flow into the PRD:
   - Layout approach (e.g., "vertical list with sidebar" not "responsive grid")
   - Filter UI pattern (e.g., "pill tabs with counts" not "dropdown")
   - Content shown per item
   - What Skool shows that is out of MVP scope (note for Out of Scope section)

### 1.3 Check Existing Implementation
Search the codebase for:
- Existing screens, components, or API endpoints related to this feature
- Data models or entities that this feature will use or extend
- Related features that this interacts with
- Any existing tests or specs

### 1.4 Compile Research Summary
Create a structured summary of:
- What exists today (if anything)
- Which bounded context(s) this feature belongs to
- Key domain entities involved
- Dependencies on other features
- **Screenshot insights** — Key UI decisions derived from Skool.com reference

---

## Phase 2: Discovery Questions

After research, ask clarifying questions to extract the logic expected.

### Question Format
- Use multiple choice answers when possible
- Clearly mark which answer you recommend for MVP (with reasoning)
- Group questions by category
- Mark questions as [BLOCKING] or [NICE-TO-HAVE]
- DO NOT ask questions already answered in the OVERVIEW_PRD or existing docs

### Question Categories

**User Behavior:**
- What triggers this action?
- What does the user see/do at each step?
- What feedback do they receive?

**Business Rules:**
- What validations apply?
- What are the constraints?
- What permissions are required?

**Edge Cases:**
- What happens when X fails?
- What if the user does Y?
- What are the boundary conditions?

**Data & Outcomes:**
- What information is captured/displayed?
- What gets created, updated, or deleted?
- What errors can occur and what should users see?

**Integration & Side Effects:**
- How does this affect other parts of the product?
- What should happen automatically (e.g., "user gets points", "notification sent")?
- What other systems need to know about this?

---

## Phase 3: Iteration

After answers are provided:
- Ask follow-up questions if answers reveal new ambiguities
- Confirm understanding of complex flows
- Continue until ALL scenarios are clearly defined
- Summarize decisions before drafting

---

## Phase 4: Generate Specifications

Create TWO outputs:

### Output 1: Detailed PRD (Product Requirements)
Save to: `docs/features/{context}/{feature}-prd.md`

**CRITICAL: Write as a Product Manager, NOT as a Software Engineer.**
**Focus on WHAT users can do and WHY, NOT on HOW it's implemented.**

**CRITICAL: Follow the canonical PRD format below exactly. See `docs/features/community/feed-prd.md` as the reference implementation.**

#### PRD Header (required)
```markdown
# [Feature Name] — Product Requirements Document

**Feature:** [Feature Name]
**Module:** [Module Name]
**Status:** Draft
**Version:** 1.0
**Last Updated:** [Date]
**Implementation Status:** Not Started
**Bounded Context:** [Context from Context Map]
**PRD Type:** Feature Specification
```

#### PRD Sections (required, in this order)
```
1. Overview
   1.1 What — What the feature does (1-2 paragraphs)
   1.2 Why — Why it's needed (business justification)
   1.3 Success Criteria — Table of metrics and targets

2. User Stories
   Grouped by category in tables:
   | ID | Story | Priority |
   Use IDs like US-XX where XX is a category prefix (e.g., US-D1 for Directory)

3. Business Rules
   Numbered subsections (3.1, 3.2, ...) with descriptive titles
   Use tables for permission matrices
   Use bold + lists for content rules and constraints

4. UI Behavior (informed by Skool.com screenshots from Phase 1.2)
   Numbered subsections (4.1, 4.2, ...)
   Each screen/view as its own subsection
   Include: Layout, States (loading/empty/error), Interactions
   IMPORTANT: Use screenshot insights for layout decisions (list vs grid),
   filter patterns (pills vs dropdowns), and content structure.
   This prevents discrepancies with the downstream UI_SPEC.

5. Edge Cases
   Numbered subsections (5.1, 5.2, ...)
   Each with Scenario + Behavior format

6. Security Requirements
   Numbered subsections (6.1, 6.2, ...)
   Authentication, Authorization, Input Validation, Data Protection

7. Out of Scope
   Grouped by phase (7.1 Not in MVP, 7.2 Phase 2, 7.3 Phase 3)
   Bulleted list of excluded features

8. Success Metrics
   Tables grouped by category (Engagement, Quality, Technical)

9. Dependencies
   9.1 Upstream Dependencies — what this feature needs
   9.2 Downstream Consumers — what will consume this feature's events

10. Open Questions
    Numbered list of unresolved decisions (or "None" if all resolved)

11. Appendix
    11.1 Related Documents — links to glossary, context map, BDD spec
    11.2 Revision History — version table

12. Approval
    Placeholder signature lines
```

**Do NOT include (these belong in TDD):**
- Domain Model (entities, aggregates, value objects, properties)
- Commands & Events (CreatePost, PostCreated, event publishing)
- API Contracts (HTTP methods, endpoints, status codes, request/response schemas)
- Database schema, tables, columns, foreign keys
- Code snippets, class definitions, function signatures
- Technology stack decisions (libraries, frameworks)
- DDD terminology (aggregate roots, repositories, value objects)
- Architecture patterns (CQRS, event sourcing, hexagonal)

**Think like a PM:**
- "Users can create posts with titles and content" (not "Post aggregate root with title: string")
- "Admins can delete any post; members can only delete their own" (not "DeletePost command requires authorization")
- "When a post is liked, the author should see their points increase" (not "PostLiked event published via event bus")

### Output 2: BDD Specification
Save to: `tests/features/{context}/{feature}.feature`

Must follow:
- `.claude/skills/bdd/SKILL.md` standards
- Declarative style (WHAT not HOW)
- Ubiquitous language from GLOSSARY
- Tags: @happy_path, @error, @edge_case, @security

Structure:
```gherkin
Feature: [Feature Name]
  As a [role]
  I want [capability]
  So that [benefit]

  Background:
    Given [common setup]

  # === HAPPY PATH ===
  @happy_path
  Scenario: [Primary success case]
    Given [precondition]
    When [action]
    Then [expected outcome]
    And [domain event published]

  # === VALIDATION ERRORS ===
  @error
  Scenario: [Validation failure case]
    ...

  # === EDGE CASES ===
  @edge_case
  Scenario: [Boundary condition]
    ...

  # === SECURITY ===
  @security
  Scenario: [Authorization check]
    ...
```

---

## Spec Quality Checklist

Before finalizing, verify:

- [ ] Every user story has at least one BDD scenario
- [ ] All business rules are covered by scenarios
- [ ] Error cases have explicit scenarios
- [ ] Domain events are specified in Then steps
- [ ] No UI implementation details in Gherkin (no "click button")
- [ ] Ubiquitous language used consistently
- [ ] PRD and BDD are aligned (no contradictions)
- [ ] Out of scope is clearly defined
- [ ] **NO technical implementation details** (libraries, DB schema, etc.) — those go in TDD

---

## Tips for Answering Questions

### Be Specific
- "It should work normally" (bad)
- "When the user clicks submit, show a loading spinner, then redirect to the feed on success" (good)

### Resist Scope Creep
If a question reveals a new feature need, say: "That's out of scope for this feature. Add it to future considerations."

### Challenge Recommendations
Claude's MVP recommendations are educated guesses. If they don't match your vision, explain why.

### Think in Side Effects
When describing what happens, think about what else should happen automatically. For example: "When a post is created, the author should see it in their activity feed."

### Reference the PRD
You can say "As described in Section 3.2.1 of the OVERVIEW_PRD" instead of re-explaining.

---

## Next Steps

After the PRD is approved:

1. **Verify PRD-BDD alignment:**
   - Every user story has BDD scenarios
   - Every business rule is tested
   - All error cases are covered
   - Domain events in PRD match those in BDD

2. Use `/generate-ui-spec` to create the UI Specification from the same screenshots used during PRD creation. Since the PRD already incorporates screenshot insights, the UI_SPEC will detail and confirm the visual approach (component specs, design tokens, spacing) — not discover discrepancies.

3. Use `/write-technical-design` to create the Technical Design Document (TDD). The TDD will reference the UI_SPEC for frontend component names in its file checklist.

4. Then proceed to implementation with `/implement-feature`
