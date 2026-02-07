---
name: security
description: Apply OWASP security standards and prevent common vulnerabilities
model: opus
---

# Skill: Security Standards

## Core Principles (OWASP Top 10)
- **Least Privilege**: Minimum necessary permissions
- **Defense in Depth**: Multiple security layers
- **Fail Secure**: Deny access on error
- **Input Validation**: Validate all untrusted data
- **Output Encoding**: Encode before rendering

---

## Frontend Security

### XSS Prevention
```typescript
// ✅ React auto-escapes
<div>{userContent}</div>

// ❌ DANGEROUS - avoid unless absolutely necessary
<div dangerouslySetInnerHTML={{__html: sanitized}} />
// If required, sanitize with DOMPurify first
```

### Authentication
```typescript
// ❌ NEVER store tokens in localStorage/sessionStorage
// ✅ Use httpOnly cookies for sensitive tokens
```

### CSRF
- Implement Anti-CSRF tokens for all mutating requests

---

## Backend Security

### SQL Injection
```python
# ❌ NEVER concatenate user input
query = f"SELECT * FROM users WHERE email = '{email}'"

# ✅ ALWAYS use parameterized queries
query = "SELECT * FROM users WHERE email = :email"
db.execute(query, {"email": email})
```

### Authentication
- Hash passwords with **Argon2** or **bcrypt**
- Implement rate limiting on auth endpoints
- Encourage/require MFA for sensitive access

### Authorization
- RBAC/ABAC checks on EVERY protected endpoint
- Verify ownership—don't trust sequential IDs (IDOR prevention)

### Data Protection
- Encrypt sensitive data at rest and in transit (TLS 1.2+)
- NEVER log PII, tokens, or passwords

---

## Secrets Management

```yaml
# ❌ NEVER commit secrets
POSTGRES_PASSWORD: mypassword123

# ✅ Use environment variables
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

**Rules:**
- `.env` files for local dev only
- Secret managers for production
- `.gitignore` must include: `.env`, `*.key`, `*.pem`

---

## Dependencies

```bash
# Regular vulnerability scanning
npm audit
pip-audit  # or pip check
```

Keep dependencies updated to patched versions.

---

## Security Review Workflow

1. Load these standards into context
2. Identify scope (auth modules, API endpoints, recent changes)
3. Check for:
   - Hardcoded secrets
   - Unsanitized inputs
   - SQL/Command injection
   - Missing auth/authz checks
   - Information leakage in errors
4. Report findings with remediation steps
