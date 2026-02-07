---
name: write-feature-spec
description: Generate PRD and BDD specifications for a feature from OVERVIEW_PRD
model: sonnet
---

# Usage
`/write-feature-spec <context>/<feature-name>`

Example: `/write-feature-spec community/posts`

---

When invoked, read the template at `prompts/write-feature-spec.md` and execute the prompt with these substitutions:

**Parse the argument:**
- Split on `/` to get `<context>` and `<feature-name>`
- If no `/` found, ask user to provide format: `context/feature-name`

**Substitutions:**
- `[FEATURE_NAME]` → Full formatted name (e.g., "Community Posts")
- `[context]` → Context directory name (e.g., "community")
- `[feature]` → Feature slug (e.g., "posts")

**Output file paths after generation:**
- PRD: `docs/features/{context}/{feature}-prd.md`
- BDD: `tests/features/{context}/{feature}.feature`

---

## Instructions

1. Parse the provided argument to extract context and feature
2. Read the `prompts/write-feature-spec.md` file
3. Extract "## The Prompt" section (lines 30-206)
4. Replace all placeholders:
   - `[FEATURE_NAME]` with title-cased version (e.g., "identity/registration" → "Identity Registration")
   - `[context]` with context name
   - `[feature]` with feature slug
5. Execute the filled prompt exactly as if the user had pasted it
6. Follow all instructions in the prompt:
   - **Phase 1**: Research the codebase and documentation
   - **Phase 2**: Ask discovery questions (grouped, with recommendations)
   - **Phase 3**: Iterate on answers until all scenarios are defined
   - **Phase 4**: Generate the PRD and BDD specifications

**Critical**:
- Do NOT skip the research phase. Always read required documents first.
- Do NOT skip the discovery questions. Always ask clarifying questions before generating specs.
- Wait for user answers before proceeding to spec generation.
