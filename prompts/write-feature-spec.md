# Write Feature Spec Prompt (PRD + BDD)

Use this prompt to create a Product Requirements Document (PRD) AND executable BDD tests for a feature.

**Note:** This creates the WHAT (product requirements). After PRD approval, use `write-technical-design.md` to create the HOW (technical implementation).

---

## When to Use

- When starting a new feature from the OVERVIEW_PRD
- When a feature needs detailed product requirements before implementation
- When you need executable acceptance criteria from a product perspective

---

## Instructions

1. Start a new Claude Code conversation (fresh context)
2. Provide the feature name from `docs/OVERVIEW_PRD.md` Appendix A
3. Paste this prompt
4. Answer Claude's clarifying questions
5. Review the generated PRD + BDD spec
6. Iterate until complete

---

## The Prompt

```
I want to write a detailed spec for [FEATURE_NAME] that includes:
1. A detailed PRD (markdown)
2. Executable BDD specifications (Gherkin .feature files)

Follow the instructions below carefully.

---

## Phase 1: Research (Do This First)

Before asking me ANY questions, thoroughly research the existing codebase and documentation:

### 1.1 Read Required Documents
- `docs/OVERVIEW_PRD.md` — Find the feature in Section 3 and Appendix A
- `docs/domain/GLOSSARY.md` — Load ubiquitous language
- `docs/architecture/CONTEXT_MAP.md` — Identify which bounded context(s) this belongs to
- `.claude/skills/architecture.md` — Review DDD patterns
- `.claude/skills/bdd.md` — Review Gherkin standards

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

After research, ask me clarifying questions to extract the logic I expect.

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

**Data & API:**
- What data is created/read/updated/deleted?
- What are the request/response shapes?
- What errors can occur?

**Integration:**
- How does this affect other features?
- What events should be published?
- What notifications are triggered?

---

## Phase 3: Iteration

After I answer:
- Ask follow-up questions if my answers reveal new ambiguities
- Confirm your understanding of complex flows
- Continue until ALL scenarios are clearly defined
- Summarize my decisions before drafting

---

## Phase 4: Generate Specifications

Create TWO outputs:

### Output 1: Detailed PRD (Product Requirements)
Save to: `docs/features/[context]/[feature]-prd.md`

**Focus on WHAT, not HOW. No technical implementation details.**

Must include:
1. **Overview** — What, why, and success criteria
2. **User Stories** — As a [role], I want [goal], so that [benefit]
3. **Domain Model** — Entities, value objects, aggregates (conceptual, DDD-aligned)
4. **Commands & Events** — What actions and what domain events
5. **API Contracts** — Routes, request/response shapes, status codes (from API consumer perspective)
6. **Business Rules** — Validations, calculations, constraints
7. **UI Behavior** — Screens, states, transitions, feedback
8. **Edge Cases** — Error handling, boundary conditions
9. **Security Requirements** — Authorization rules, data protection requirements (not implementation)
10. **Out of Scope** — What this feature explicitly does NOT include

**Do NOT include:**
- Specific libraries or frameworks
- Database schema (SQL)
- API endpoint paths (e.g., POST /api/v1/auth/register)
- Request/response JSON schemas
- HTTP status codes
- Code snippets or implementation patterns
- Technology stack decisions

**Think of it as:** Describe capabilities and data needs, not technical contracts.

### Output 2: BDD Specification
Save to: `tests/features/[context]/[feature].feature`

Must follow:
- `.claude/skills/bdd.md` standards
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
- [ ] **NO technical implementation details** (libraries, DB schema, etc.) - those go in TDD
```

---

## Next Steps

After the PRD is approved:

1. **Verify PRD-BDD alignment:**
   - Every user story has BDD scenarios
   - Every business rule is tested
   - All error cases are covered
   - Domain events in PRD match those in BDD

2. Use the `write-technical-design.md` prompt to create the Technical Design Document (TDD)

3. TDD will specify HOW to implement using specific libraries, patterns, and architecture

4. Then proceed to implementation phase

---

## Tips for Answering Questions

### Be Specific
❌ "It should work normally"  
✅ "When the user clicks submit, show a loading spinner, then redirect to the feed on success"

### Resist Scope Creep
If a question reveals a new feature need, say: "That's out of scope for this feature. Add it to future considerations."

### Challenge Recommendations
Claude's MVP recommendations are educated guesses. If they don't match your vision, explain why.

### Think in Events
When describing what happens, think about what domain events should be published. This helps identify side effects and integrations.

### Reference the PRD
You can say "As described in Section 3.2.1 of the OVERVIEW_PRD" instead of re-explaining.

---

## Example Session

**You:** I want to write a detailed spec for Post Creation following the instructions above.

**Claude:** *[Reads OVERVIEW_PRD, GLOSSARY, CONTEXT_MAP, checks codebase]*

**Research Summary:**
- Feature belongs to Community bounded context
- Key entities: Post, Category, User
- Commands: CreatePost
- Events: PostCreated
- No existing implementation found

**Clarifying Questions:**

**User Behavior [BLOCKING]:**
1. Can users create posts without a title?
   - A) Title required ← *Recommended for MVP (clearer feed)*
   - B) Title optional
   - C) Title required only for certain categories

2. What content types are supported in MVP?
   - A) Text only ← *Recommended for MVP*
   - B) Text + single image
   - C) Text + multiple images + video

**Business Rules [BLOCKING]:**
3. Is there a maximum post length?
   - A) No limit
   - B) 5,000 characters ← *Recommended for MVP*
   - C) 10,000 characters

...

**You:** 1-A, 2-B, 3-B

**Claude:** *[Asks follow-up questions, then generates PRD + BDD spec]*

---

## Output File Locations

```
docs/features/
├── community/
│   ├── posts-prd.md
│   ├── comments-prd.md
│   └── reactions-prd.md
├── classroom/
│   ├── courses-prd.md
│   └── lessons-prd.md
└── ...

tests/features/
├── community/
│   ├── posts.feature
│   ├── comments.feature
│   └── reactions.feature
├── classroom/
│   ├── courses.feature
│   └── lessons.feature
└── ...
```
