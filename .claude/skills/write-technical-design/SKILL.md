---
name: write-technical-design
description: Generate Technical Design Document (TDD) from approved PRD and BDD specs
---

# Usage
`/write-technical-design <context>/<feature-name>`

Example: `/write-technical-design identity/registration-authentication`

---

When invoked, read the template at `prompts/write-technical-design.md` and execute the prompt to create a TDD.

**Parse the argument:**
- Split on `/` to get `<context>` and `<feature-name>`
- If no `/` found, ask user to provide format: `context/feature-name`

**Substitutions:**
- `[FEATURE_NAME]` → Full formatted name (e.g., "Identity Registration Authentication")
- `[context]` → Context directory name (e.g., "identity")
- `[feature]` → Feature slug (e.g., "registration-authentication")

**Expected input files:**
- PRD: `docs/features/{context}/{feature}-prd.md`
- BDD: `tests/features/{context}/{feature}.feature`

**Output files:**
- TDD: `docs/features/{context}/{feature}-tdd.md`
- Alignment: `docs/features/{context}/ALIGNMENT_VERIFICATION.md`

---

## Instructions

1. Parse the provided argument to extract context and feature
2. Verify PRD and BDD files exist (error if missing)
3. Read the `prompts/write-technical-design.md` file
4. Execute the TDD creation workflow:

**Research Phase:**
- Read the approved PRD at `docs/features/{context}/{feature}-prd.md`
- Read the BDD spec at `tests/features/{context}/{feature}.feature`
- Read project architecture docs (CLAUDE.md, architecture skills)
- Check existing implementation patterns in the codebase
- Research libraries using web search for best practices

**Design Phase:**
- Create TDD following the template structure in the prompt
- Include all 17 sections from the template
- Focus on architecture and design decisions, NOT implementation code
- Research and justify all library choices

**Verification Phase:**
- Create ALIGNMENT_VERIFICATION.md (mandatory)
- Verify PRD → BDD → TDD alignment
- Ensure all requirements are covered

**Critical:**
- Do NOT start without an approved PRD
- Do NOT include detailed code implementations
- Do research library choices - never assume from memory
- Always create the alignment verification document
