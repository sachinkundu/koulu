---
name: architecture
description: Apply DDD and Hexagonal Architecture patterns when designing or refactoring code
---

# Skill: DDD Architecture

## Strategic Design

### Bounded Contexts
- **Strict isolation**: Never import domain models across contexts
- **Communication**: Only via public APIs, domain events, or ACL
- **Naming**: Use ubiquitous language from `docs/domain/GLOSSARY.md`

### Koulu Contexts (Proposed)
```
Identity        → Users, authentication, profiles
Community       → Posts, comments, reactions, feed
Classroom       → Courses, modules, lessons, progress
Membership      → Plans, subscriptions, access control
Gamification    → Points, leaderboards, achievements
```

---

## Hexagonal Architecture

```
┌─────────────────────────────────────────┐
│              Interface                   │
│         (Controllers, CLI)               │
├─────────────────────────────────────────┤
│             Application                  │
│      (Commands, Queries, Use Cases)      │
├─────────────────────────────────────────┤
│               Domain                     │
│  (Entities, Value Objects, Events)       │
│         ⚠️ NO EXTERNAL DEPS ⚠️           │
├─────────────────────────────────────────┤
│            Infrastructure                │
│   (DB, APIs, External Services)          │
└─────────────────────────────────────────┘

Dependencies point INWARD only.
```

---

## Tactical Patterns

### Aggregates
```python
# Aggregate Root is the only entry point
class Post:  # Aggregate Root
    def add_comment(self, author: UserId, content: CommentContent) -> None:
        # Enforces invariants
        if self.is_locked:
            raise PostLockedError()
        comment = Comment(author=author, content=content)
        self._comments.append(comment)
        self._events.append(CommentAdded(post_id=self.id, comment_id=comment.id))
```

### Value Objects
```python
@dataclass(frozen=True)  # Immutable!
class EmailAddress:
    value: str

    def __post_init__(self) -> None:
        if not self._is_valid(self.value):
            raise InvalidEmailError(self.value)
```

### Domain Events
```python
@dataclass(frozen=True)
class UserRegistered:  # Past tense naming
    user_id: UserId
    email: EmailAddress
    occurred_at: datetime
```

---

## Rules

| ✅ DO | ❌ DON'T |
|-------|----------|
| Rich domain models with behavior | Anemic models (data bags) |
| Validate in constructors | Allow invalid state |
| Use factory methods | Public setters |
| Throw domain exceptions | Generic exceptions |
| Repository interfaces in domain | SQL in domain layer |

---

## Design Workflow

1. **Analyze**: Extract terms, define ubiquitous language
2. **Context**: Identify bounded context (existing or new?)
3. **Model**: Identify aggregates, roots, invariants, value objects
4. **Interface**: Define commands, queries, events
5. **Document**: Update `docs/architecture/` with design decisions
