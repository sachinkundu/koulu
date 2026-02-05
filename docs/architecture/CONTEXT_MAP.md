# Context Map - Koulu

## Bounded Contexts

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │   Identity   │      │  Community   │      │  Classroom   │  │
│  │              │      │              │      │              │  │
│  │ - User       │──────│ - Post       │      │ - Course     │  │
│  │ - Profile    │      │ - Comment    │      │ - Module     │  │
│  │ - Auth       │      │ - Reaction   │      │ - Lesson     │  │
│  └──────────────┘      │ - Category   │      │ - Progress   │  │
│         │              └──────────────┘      └──────────────┘  │
│         │                     │                     │          │
│         │                     │                     │          │
│         ▼                     ▼                     ▼          │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │  Membership  │      │ Gamification │      │ Notification │  │
│  │              │      │              │      │  (Future)    │  │
│  │ - Plan       │      │ - Points     │      │              │  │
│  │ - Subscript. │◀─────│ - Level      │      │              │  │
│  │ - Access     │      │ - Leaderboard│      │              │  │
│  └──────────────┘      └──────────────┘      └──────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Context Relationships

### Identity → Community
- **Type**: Customer/Supplier
- **Flow**: Identity provides User ID to Community for authorship
- **Integration**: Shared Kernel (UserId value object)

### Identity → Membership
- **Type**: Customer/Supplier
- **Flow**: Identity provides User for subscription management
- **Integration**: Domain Events (UserRegistered → create member)

### Community → Gamification
- **Type**: Publisher/Subscriber
- **Flow**: Community publishes engagement events
- **Integration**: Domain Events (PostCreated, CommentAdded → award points)

### Gamification → Membership
- **Type**: Conformist
- **Flow**: Gamification reads access levels to determine point multipliers
- **Integration**: Read-only query

### Classroom → Gamification
- **Type**: Publisher/Subscriber
- **Flow**: Classroom publishes completion events
- **Integration**: Domain Events (LessonCompleted → award points)

---

## Integration Patterns

### Domain Events (Async)
```python
# Published by Community
class PostCreated:
    post_id: PostId
    author_id: UserId
    community_id: CommunityId
    occurred_at: datetime

# Consumed by Gamification
@event_handler(PostCreated)
def award_post_points(event: PostCreated) -> None:
    gamification_service.award_points(
        user_id=event.author_id,
        points=10,
        reason="post_created"
    )
```

### Shared Kernel
```python
# Shared value objects (owned by Identity context)
# Other contexts import and use these

@dataclass(frozen=True)
class UserId:
    value: UUID
    
@dataclass(frozen=True)  
class CommunityId:
    value: UUID
```

---

## Anti-Corruption Layers

When integrating with external systems (future):
- Payment provider → Membership ACL
- Email service → Notification ACL
- Video hosting → Classroom ACL

---

## Rules

1. **No direct imports** across context boundaries
2. **Events for side effects** - never direct calls
3. **Shared Kernel** only for ID value objects
4. **Each context owns its data** - no shared database tables
