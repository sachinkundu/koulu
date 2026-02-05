---
name: implement-feature
description: Implement a feature from completed PRD and BDD specs
---

# Usage
`/implement-feature <context>/<feature-name>`

Example: `/implement-feature identity/registration-authentication`

---

When invoked, read the template at `prompts/implement-feature.md` and execute the prompt with these substitutions:

**Parse the argument:**
- Split on `/` to get `<context>` and `<feature-name>`
- If no `/` found, ask user to provide format: `context/feature-name`

**Substitutions:**
- `[FEATURE_NAME]` → Full formatted name (e.g., "Identity Registration Authentication")
- `[context]` → Context directory name (e.g., "identity")
- `[feature]` → Feature slug (e.g., "registration-authentication")

**Expected file paths after substitution:**
- PRD: `docs/features/{context}/{feature}-prd.md`
- BDD: `tests/features/{context}/{feature}.feature`

---

## Instructions

1. Parse the provided argument to extract context and feature
2. Read the `prompts/implement-feature.md` file
3. Extract "## The Prompt" section (lines 26-204)
4. Replace all placeholders:
   - `[FEATURE_NAME]` with title-cased version
   - `[context]` with context name
   - `[feature]` with feature slug
5. Execute the filled prompt exactly as if the user had pasted it
6. Follow all instructions in the prompt (Phase 1 through Phase 5)

**Critical**: Do NOT skip the mandatory stop at Phase 3. Always wait for user approval before implementing.
