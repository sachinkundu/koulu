---
name: write-technical-design
description: Generate Technical Design Document (TDD) from approved PRD and BDD specs
---

# Write Technical Design Document (TDD)

## Purpose

Create a **design document** (not implementation guide) that explains:
- **Architecture** - how components fit together
- **Design decisions** - what choices were made and why
- **Technology strategy** - what tools/patterns to use
- **Integration patterns** - how systems communicate
- **Tradeoffs** - alternatives considered and rejected

Think like a **technical architect presenting to senior engineers**, not a developer writing a tutorial.

---

## Usage

`/write-technical-design <context>/<feature-name>`

Example: `/write-technical-design identity/profile`

---

## Input Requirements

**Must exist before starting:**
- PRD: `docs/features/{context}/{feature}-prd.md` (approved)
- BDD: `tests/features/{context}/{feature}.feature` (approved)

**Output files:**
- TDD: `docs/features/{context}/{feature}-tdd.md`
- Alignment: `docs/features/{context}/ALIGNMENT_VERIFICATION.md`

---

## TDD Structure (17 Sections)

### 1. Overview (1 page)
- Summary: What problem does this solve?
- Goals: What are we achieving?
- Non-goals: What are we explicitly NOT doing?

### 2. Architecture (2-3 pages)
- **System Context Diagram**: How does this fit in the platform?
- **Component Architecture**: Layers and responsibilities
- **DDD Design**: Aggregates, entities, value objects (concepts, not code)
- **Integration Points**: How does this connect to other contexts?

**Focus on:** Boxes and arrows, responsibilities, boundaries
**Avoid:** Code snippets, class definitions

### 3. Technology Stack (1-2 pages)
- **Backend**: Libraries and frameworks needed
- **Frontend**: Libraries and frameworks needed
- **Infrastructure**: Database, cache, external services
- **Justification**: WHY each technology (with research, never assume)
- **Alternatives**: What was considered and rejected

**Example:**
```markdown
### bleach (^6.1.0) - NEW dependency
**Purpose:** HTML sanitization to prevent XSS attacks
**Why:** Mozilla-maintained, battle-tested (10+ years), OWASP recommended
**Alternatives considered:**
- html.escape() - Too basic, doesn't handle nested tags
- Custom regex - Security risk, reinventing the wheel
**Research:** https://bleach.readthedocs.io/
```

### 4. Data Model (2-3 pages)
- **Conceptual Schema**: What data do we store? (logical model)
- **Relationships**: How entities relate
- **Indexes**: What queries need optimization?
- **Migrations**: How do we evolve the schema?
- **Design Decisions**: Why this structure vs alternatives?

**Focus on:** Logical design, tradeoffs (e.g., JSON vs columns)
**Avoid:** Actual SQL code, detailed CREATE TABLE statements

### 5. API Design (2-3 pages)
- **Endpoint Overview**: RESTful resource design
- **Request/Response Contracts**: Data shapes (logical, not Pydantic code)
- **Authentication/Authorization**: Security model
- **Error Handling**: Error taxonomy and HTTP mapping
- **Versioning Strategy**: How will this evolve?

**Focus on:** Interface contracts, design principles (REST, consistency)
**Avoid:** Controller implementation, decorator syntax

### 6. Domain Model (2-3 pages)
- **Aggregates**: What are the consistency boundaries?
- **Value Objects**: What concepts need validation? (purpose, not code)
- **Domain Events**: What business events occur?
- **Invariants**: What rules must always be true?
- **Design Patterns**: What DDD patterns apply?

**Focus on:** Domain concepts, business rules, boundaries
**Avoid:** Dataclass definitions, validation code

### 7. Application Layer (1-2 pages)
- **Commands**: What user intentions exist?
- **Queries**: What information is retrieved?
- **Use Case Flow**: High-level orchestration
- **Event Handling**: What happens when events fire?

**Focus on:** Responsibilities, flow, orchestration
**Avoid:** Handler implementation code

### 8. Integration Strategy (1-2 pages)
- **Cross-Context Communication**: Events, APIs, shared kernel
- **External Services**: Email, storage, etc.
- **Anti-Corruption Layers**: How do we protect our domain?
- **Failure Modes**: What can go wrong and how do we handle it?

### 9. Security Design (1-2 pages)
- **Authentication**: How do we verify identity?
- **Authorization**: Who can do what?
- **Input Validation**: How do we prevent attacks?
- **Data Protection**: Encryption, sanitization, etc.
- **Threat Model**: What attacks are we defending against?

**Focus on:** Security architecture, not implementation

### 10. Performance & Scalability (1-2 pages)
- **Performance Targets**: Response times, throughput
- **Caching Strategy**: What to cache and where?
- **Query Optimization**: Index strategy
- **Scalability Considerations**: Bottlenecks and solutions

### 11. Error Handling (1 page)
- **Error Taxonomy**: Domain exceptions and their meaning
- **HTTP Mapping**: How errors map to status codes
- **User Feedback**: What messages do users see?

### 12. Testing Strategy (1 page)
- **BDD Tests**: What scenarios are covered?
- **Unit Tests**: What domain logic needs unit coverage?
- **Integration Tests**: What integrations need testing?

### 13. Observability (1 page)
- **Logging**: What events to log?
- **Metrics**: What to measure?
- **Tracing**: What flows to trace?

### 14. Deployment Strategy (1 page)
- **Migration Plan**: How to roll out schema changes
- **Rollback Plan**: How to undo if needed
- **Feature Flags**: Gradual rollout strategy

### 15. Future Considerations (1 page)
- **Phase 2 Enhancements**: What's deferred?
- **Known Limitations**: What are we not solving?
- **Technical Debt**: What shortcuts are we taking?

### 16. Alignment Verification (reference)
- See ALIGNMENT_VERIFICATION.md
- Ensure PRD → BDD → TDD coverage

### 17. Appendices
- **File Checklist**: What files will be created/modified (paths only)
- **Dependencies**: What packages to add
- **References**: Links to docs, RFCs, research

---

## What NOT to Include

❌ **Detailed Code Implementations**
- No Python/TypeScript class definitions
- No function implementations
- No line-by-line "here's how to code it"

❌ **Step-by-Step Instructions**
- No "Step 1: Create file X, Step 2: Add code Y"
- No tutorial-style guidance

❌ **Low-Level Details**
- No decorator syntax (@dataclass, @router.get)
- No import statements
- No specific variable names

❌ **Assumed Knowledge**
- Never assume library APIs from memory
- Always research and cite sources
- Include links to documentation

---

## What TO Include

✅ **Architecture Diagrams**
- System context
- Component interactions
- Data flow
- Integration patterns

✅ **Design Decisions with Rationale**
- "We chose X over Y because..."
- "This tradeoff means..."
- "Alternatives considered: A, B, C"

✅ **Conceptual Models**
- Domain concepts
- Data relationships
- Logical schemas

✅ **Design Patterns**
- "Use Repository pattern for..."
- "Apply Strategy pattern for..."
- "Event-driven communication because..."

✅ **Non-Functional Requirements**
- Performance targets
- Security requirements
- Scalability considerations

---

## Research Requirements

Before writing TDD:

1. **Read existing implementation** - Understand patterns already in codebase
2. **Research libraries** - Look up APIs, don't guess
3. **Review architecture docs** - CLAUDE.md, DDD patterns
4. **Study similar features** - How were related features designed?

When justifying technology choices:
- Include links to documentation
- Cite version numbers
- Explain alternatives considered
- Provide concrete reasons (not "it's popular")

---

## Workflow

### Phase 1: Research (15 min)
- Read approved PRD and BDD specs
- Understand business requirements
- Check existing codebase patterns
- Research technology options

### Phase 2: Design (30 min)
- Sketch architecture (boxes and arrows)
- Design data model (logical schema)
- Design API contracts (endpoints and shapes)
- Identify integration points
- Document design decisions

### Phase 3: Write TDD (45 min)
- Follow 17-section structure
- Focus on "what" and "why", not "how"
- Include diagrams (ASCII art is fine)
- Justify all decisions
- Keep it high-level

### Phase 4: Verification (15 min)
- Create ALIGNMENT_VERIFICATION.md
- Check PRD → BDD → TDD coverage
- Verify all requirements mapped
- Ensure no gaps

---

## Example: Good vs Bad

### ❌ BAD (Too detailed, implementation-focused)

```markdown
### Value Objects

**File:** `src/identity/domain/value_objects/location.py`

```python
from dataclasses import dataclass
from src.shared.domain.base_value_object import BaseValueObject

@dataclass(frozen=True)
class Location(BaseValueObject):
    city: str
    country: str

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not (2 <= len(self.city) <= 100):
            raise InvalidLocationError("City must be 2-100 characters")
```
```

### ✅ GOOD (Design-focused, architectural)

```markdown
### Value Objects

**Location**
- Represents a user's geographic location (city + country)
- Both fields required together (consistency rule)
- Validation: 2-100 characters each, no HTML
- Immutable once created
- Design decision: Separate fields vs free-text
  - Chose structured (city + country) for future Map feature
  - Allows filtering by city or country
  - Prevents ambiguous entries like "NYC" vs "New York City"
```

---

## Tone and Style

**Write like a technical architect presenting to senior engineers:**
- Explain the "why" behind decisions
- Discuss tradeoffs openly
- Reference industry patterns
- Be concise but comprehensive

**NOT like a tutorial author:**
- Don't write "Step 1, Step 2..."
- Don't include code you'd copy-paste
- Don't explain basic concepts

---

## Deliverables

1. **TDD Document** (`docs/features/{context}/{feature}-tdd.md`)
   - 17 sections as outlined above
   - 15-25 pages typically
   - Focus on design and architecture

2. **Alignment Verification** (`docs/features/{context}/ALIGNMENT_VERIFICATION.md`)
   - PRD → BDD → TDD mapping
   - Gap analysis
   - Coverage verification
   - Approval checklist

---

## Quality Checklist

Before finalizing TDD:

- [ ] Architecture diagrams included
- [ ] All design decisions justified
- [ ] Technology choices researched and cited
- [ ] Alternatives considered and documented
- [ ] Integration patterns explained
- [ ] Security architecture defined
- [ ] Performance considerations addressed
- [ ] No implementation code snippets
- [ ] No step-by-step instructions
- [ ] Alignment verification complete
- [ ] All PRD requirements covered
- [ ] All BDD scenarios mapped

---

## Next Steps After TDD Approval

Once TDD is approved:
1. Use `/implement-feature` to begin implementation
2. Developers will follow the architecture and design
3. TDD serves as reference, not line-by-line guide
