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

### 1.2 Check Existing Implementation
Search the codebase for:
- Existing screens, components, or API endpoints related to this feature
- Data models or entities that this feature will use or extend
- Related features that this interacts with
- Any existing tests or specs

### 1.3 Compile Research Summary
Create a structured summary of:
- What exists today (if anything)
- Which bounded context(s) this feature belongs to
- Key domain entities involved
- Dependencies on other features

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

Must include:
1. **Overview** — What the feature does, why it's needed, success metrics
2. **User Stories** — As a [role], I want [goal], so that [benefit]
3. **Business Rules** — Validations, constraints, permissions, calculations, behavior rules
4. **UI Behavior** — What users see, screens, states, transitions, feedback messages
5. **Edge Cases** — What happens in error conditions, boundary scenarios, failure modes
6. **Security Requirements** — Who can do what, authorization rules (not how to implement)
7. **Out of Scope** — What this feature explicitly does NOT include

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

2. Use `/write-technical-design` to create the Technical Design Document (TDD)

3. TDD will specify HOW to implement using specific libraries, patterns, and architecture

4. Then proceed to implementation with `/implement-feature`
