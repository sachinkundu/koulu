# Domain Glossary - Koulu

This is the **ubiquitous language** for the Koulu project. All code, documentation, and communication must use these terms consistently.

---

## Identity Context

| Term | Definition |
|------|------------|
| **User** | A person registered in the system |
| **Profile** | Public-facing information about a user (name, avatar, bio) |
| **Member** | A user who has joined a specific community |

---

## Community Context

| Term | Definition |
|------|------------|
| **Community** | A group space (equivalent to a Skool group) |
| **Post** | User-created content in the community feed |
| **Comment** | A reply to a post |
| **Reaction** | A user's response to a post (like, etc.) |
| **Category** | Post classification (General, Q&A, Wins, etc.) |
| **Pin** | Marking a post to stay at top of feed |

---

## Classroom Context

| Term | Definition |
|------|------------|
| **Course** | A structured learning path with modules |
| **Module** | A section within a course containing lessons |
| **Lesson** | Individual learning content (video, text, etc.) |
| **Progress** | A member's completion status within a course |
| **Drip** | Scheduled release of content over time |

---

## Membership Context

| Term | Definition |
|------|------------|
| **Plan** | Pricing tier for community access |
| **Subscription** | A member's active payment relationship |
| **Access Level** | What content/features a member can use |

---

## Gamification Context

| Term | Definition |
|------|------------|
| **Points** | Numeric score earned for engagement |
| **Level** | Member rank based on accumulated points |
| **Leaderboard** | Ranked list of members by points |
| **Achievement** | Badge earned for specific accomplishments |

---

## Usage Rules

1. **Code**: Class names, method names, variables must use these terms
2. **BDD**: Gherkin scenarios must use this language
3. **UI**: Labels and copy should reflect these terms
4. **Discussion**: Team communication should use these terms

**Example:**
```python
# ✅ Correct
class Post:
    def add_comment(self, author: Member, content: str) -> Comment:
        ...

# ❌ Wrong
class Article:  # Not our term
    def add_reply(self, user: User, text: str) -> Reply:  # Wrong terms
        ...
```
