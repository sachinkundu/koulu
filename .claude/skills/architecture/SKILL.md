---
name: architecture
description: Apply DDD and Hexagonal Architecture patterns when designing or refactoring code
model: opus
---

# Skill: DDD Architecture

**This skill is the authority for all DDD design decisions.** Read this before writing any TDD or implementing any new bounded context.

Reference docs:
- `docs/domain/GLOSSARY.md` — Ubiquitous language (MUST use these terms in code, specs, and UI)
- `docs/architecture/CONTEXT_MAP.md` — Bounded context map and integration patterns

For folder structure and non-negotiable hexagonal rules, see CLAUDE.md "Architecture" section.

---

## Strategic Design: Right-Sized Contexts

### Bounded Context Sizing

A bounded context should be:
- **Small enough** that one team can own it and reason about it
- **Large enough** to encapsulate a coherent business capability
- **Independent** in its data ownership and deployment

### Koulu Contexts

| Context | Responsibility | Key Aggregates |
|---------|---------------|----------------|
| Identity | Users, authentication, profiles | User, Profile |
| Community | Posts, comments, reactions, feed | Post, Comment, Category |
| Classroom | Courses, modules, lessons, progress | Course, Module, Lesson |
| Membership | Plans, subscriptions, access control | Plan, Subscription |
| Gamification | Points, leaderboards, achievements | Score, Achievement |

### When to Create a New Context

✅ **Create a new context when:**
- Business language diverges (same word means different things in different areas)
- The aggregate has an independent lifecycle (can exist without others)
- Different rate of change (one part evolves much faster than the other)
- Different team ownership (current or planned)

❌ **Do NOT create a new context when:**
- It would result in a context with only 1-2 entities
- The "new" concept is tightly coupled to an existing aggregate
- You'd need synchronous calls between the contexts for basic operations

### Context Sizing Examples

```
# ❌ TOO GRANULAR - These belong together in Community
PostContext, CommentContext, ReactionContext

# ❌ TOO BROAD - These have different lifecycles and language
PlatformContext (users + posts + courses + payments all together)

# ✅ RIGHT-SIZED - Coherent business capability with shared language
Community (posts + comments + reactions + categories + feed)
```

### Evolving Context Boundaries

Contexts can be split or merged as domain understanding deepens:

1. **Start with fewer, broader contexts** — don't over-split prematurely
2. **Split when language diverges** — when the same word means different things
3. **Merge when boundaries create friction** — excessive cross-context events for simple operations signal a bad split
4. **Document decisions** — update `docs/architecture/CONTEXT_MAP.md` when boundaries change

---

## Tactical Design: Aggregates and Entities

### Aggregate Design Rules

1. **Aggregates are consistency boundaries** — all invariants within an aggregate are enforced in a single transaction
2. **Reference other aggregates by ID only** — never hold object references across aggregates
3. **Keep aggregates small** — prefer more, smaller aggregates over fewer, larger ones
4. **One aggregate per transaction** — if you need to update two aggregates, use domain events

```python
# ✅ CORRECT - Reference by ID, enforce invariants internally
class Post:
    author_id: UserId              # ID reference, not User object
    category_id: CategoryId        # ID reference, not Category object

    def add_comment(self, author_id: UserId, content: CommentContent) -> Comment:
        if self.is_locked:
            raise PostLockedError(self.id)
        comment = Comment(author_id=author_id, content=content)
        self._comments.append(comment)
        self._record_event(CommentAdded(post_id=self.id, comment_id=comment.id))
        return comment

# ❌ WRONG - Holding object references across aggregates
class Post:
    author: User                   # Object reference = tight coupling
    category: Category             # Breaks aggregate isolation
```

### Entity vs Value Object

| Use Entity when... | Use Value Object when... |
|--------------------|--------------------------|
| Has unique identity (ID) | Defined by its attributes only |
| Has a lifecycle (create, modify, delete) | Immutable once created |
| Is an aggregate root or part of one | Replaceable (swap with equal value) |
| Example: User, Post, Course | Example: EmailAddress, PostTitle, Money |

### Value Objects

```python
@dataclass(frozen=True)  # Immutable!
class EmailAddress:
    value: str

    def __post_init__(self) -> None:
        if not self._is_valid(self.value):
            raise InvalidEmailError(self.value)
```

**Rules:**
- Always `frozen=True` (immutable)
- Validate in `__post_init__`
- No ID field
- Equality by value, not reference

### Domain Events

```python
@dataclass(frozen=True)
class UserRegistered:  # Past tense naming
    user_id: UserId
    email: EmailAddress
    occurred_at: datetime
```

**Rules:**
- Past tense naming (something that happened)
- Immutable (frozen dataclass)
- Carry only IDs and essential data — not full objects
- Published by aggregate roots, consumed by other contexts

---

## Cross-Context Integration

### Communication Patterns

| Pattern | When to Use | Example |
|---------|------------|---------|
| **Domain Events** | Side effects across contexts | PostCreated → award points |
| **Shared Kernel** | ID value objects shared by all | UserId, CommunityId |
| **Anti-Corruption Layer** | External system integration | Payment provider adapter |

### Rules

- **No direct imports** across context boundaries
- **Events for side effects** — never direct calls between contexts
- **Shared Kernel** ONLY for ID value objects (in `src/shared/domain/`)
- **Each context owns its data** — no shared database tables

---

## DDD Compliance Checklist

Use this when writing TDDs or reviewing implementations:

### Context Level
- [ ] Bounded context identified and right-sized (not too granular, not too broad)
- [ ] Ubiquitous language from GLOSSARY.md used consistently in code and specs
- [ ] CONTEXT_MAP.md updated if new context or new integration added

### Domain Layer
- [ ] Aggregate roots identified with clear consistency boundaries
- [ ] Entities have behavior (not anemic data bags with only getters/setters)
- [ ] Value objects validate in constructor and are immutable (`frozen=True`)
- [ ] Domain events defined for cross-context side effects
- [ ] Domain exceptions are specific (not generic `ValueError`)
- [ ] ZERO external imports — no SQLAlchemy, no FastAPI, no HTTP

### Infrastructure Layer
- [ ] Repository interfaces defined in domain layer
- [ ] Repository implementations in infrastructure layer
- [ ] Cross-context references by ID only (no object references)
- [ ] Database tables owned by one context only

### Application Layer
- [ ] Commands represent user intent (imperative: CreatePost, VerifyEmail)
- [ ] Queries represent information retrieval (GetPost, ListFeedPosts)
- [ ] Handlers orchestrate domain objects — no business logic in handlers

---

## Design Workflow

When designing architecture for a new feature:

1. **Identify context** — Does this belong to an existing context or need a new one? Check CONTEXT_MAP.md
2. **Define ubiquitous language** — Add new terms to GLOSSARY.md
3. **Model aggregates** — Identify roots, entities, value objects, invariants
4. **Define events** — What business events does this feature produce/consume?
5. **Plan integration** — How does this connect to other contexts? Events? Shared kernel?
6. **Document in TDD** — All architecture decisions go in the Technical Design Document
