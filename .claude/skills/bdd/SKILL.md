---
name: bdd
description: Write BDD specifications using Gherkin for behavior-driven development
---

# Skill: BDD Specifications

## Tools
- **Python**: `pytest-bdd`
- **Frontend**: `cucumber-js`

---

## Writing Feature Files

Location: `tests/features/*.feature`

```gherkin
Feature: User Registration
  As a new user
  I want to register an account
  So that I can access the community

  Background:
    Given the system is initialized

  @happy_path
  Scenario: Successful registration with valid email
    Given no user exists with email "new@example.com"
    When the user registers with name "John Doe" and email "new@example.com"
    Then a new user account should be created
    And a "UserRegistered" event should be published

  @error
  Scenario: Registration fails with existing email
    Given a user exists with email "existing@example.com"
    When the user attempts to register with email "existing@example.com"
    Then registration should fail with "email already exists" error
```

---

## Step Guidelines

### Given (Setup)
```gherkin
# ✅ Domain state
Given a user with email "test@example.com" exists
Given the post has 5 comments

# ❌ UI details
Given I am on the login page
```

### When (Action)
```gherkin
# ✅ Domain action
When the user submits a new post with title "Hello"
When the admin locks the post

# ❌ UI details
When I click the "Submit" button
```

### Then (Assertion)
```gherkin
# ✅ Domain outcome
Then the post should be created
Then a "PostCreated" event should be published

# ❌ UI details
Then I see the success message
```

---

## Best Practices

| Do | Don't |
|----|-------|
| Declarative (what, not how) | Imperative UI steps |
| One behavior per scenario | Multiple unrelated assertions |
| Independent scenarios | Shared state between tests |
| Use data tables for complex data | Long inline parameter lists |
| Tags: `@happy_path`, `@error`, `@slow` | Unlabeled scenarios |

---

## Integration with DDD

- **Given** → Create aggregates via repositories/factories
- **When** → Invoke command on application service
- **Then** → Assert repository state, domain events, or service response

---

## Verification

```bash
# Python
pytest tests/features/

# Frontend
npm run test:bdd
```

**If tests fail:**
1. Check if scenario matches PRD requirements
2. Debug implementation code
3. Do NOT change test to match broken code (unless test was wrong)

---

## Anti-Patterns to Avoid

### Stub Implementations That Always Pass

```python
# ❌ WRONG - This hides missing functionality
@then('a verification email should be sent to "{email}"')
def verification_email_sent_to(email: str, context: dict[str, Any]) -> None:
    """Verify email was sent (mocked)."""
    pass  # NEVER DO THIS - test always passes!

# ✅ CORRECT - Actually verify the side effect
@then('a verification email should be sent to "{email}"')
async def verification_email_sent_to(email: str) -> None:
    """Verify email was sent via MailHog."""
    response = httpx.get(f"http://localhost:8025/api/v2/search?query=to:{email}")
    messages = response.json()["items"]
    assert len(messages) > 0, f"No email sent to {email}"
```

### Red Flags in Step Implementations

| Red Flag | Problem |
|----------|---------|
| Step body is just `pass` | Test does nothing, always passes |
| Comment says "mocked" with no mock setup | Side effect never tested |
| No assertions in `@then` step | Outcome not verified |
| Test "passes" but feature doesn't work | Missing integration |

---

## Verification Checklist

Before marking BDD scenarios as complete:

- [ ] **No `pass` statements** in step implementations (except `@given` setup that's truly a no-op)
- [ ] **Side effects are verified** (emails sent, events published, webhooks called)
- [ ] **Manual smoke test** passes for critical flows
- [ ] **Infrastructure integrations tested** (e.g., query MailHog, check Redis, verify DB state)
- [ ] **Mocks are intentional** - if mocking, document WHY and what the mock covers
