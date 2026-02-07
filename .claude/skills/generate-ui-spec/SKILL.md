---
name: generate-ui-spec
description: Generate UI_SPEC.md by analyzing Skool.com screenshots and PRD
user_invocable: true
model: sonnet
---

# Skill: Generate UI Specification from Screenshots

**Purpose:** Automate UI specification creation by analyzing Skool.com reference screenshots and mapping them to Koulu's design system.

**Usage:** `/generate-ui-spec`

---

## Input Requirements

User must provide:
1. **PRD path** - The feature's PRD.md file
2. **Screenshot directory** - Folder containing Skool.com reference images
3. **(Optional) Phase plan path** - Path to implementation phases document (e.g., `feed-implementation-phases.md`)
4. **(Optional) Focus areas** - Specific components or interactions to emphasize

---

## Skill Workflow

### Phase 1: Context Gathering

1. **Read the PRD**
   - Understand feature scope and requirements
   - Identify key user flows
   - Extract component needs from acceptance criteria

2. **Read Phase Plan (if provided)**
   - Load implementation phases document
   - Extract phase structure (Phase 1, 2, 3, etc.)
   - Note which components/features belong to each phase
   - Understand phase dependencies
   - This will be used to organize UI_SPEC.md by phase

3. **Load Design System**
   - Read `.claude/skills/ui-design/SKILL.md`
   - Review `tailwind.config.ts` for available tokens
   - Note: Design system is Skool.com-inspired, so screenshots should align

4. **Scan Existing Components**
   - Use Glob to find existing components: `src/components/**/*.tsx`, `src/features/*/components/*.tsx`
   - Identify reusable patterns (Card, Form, Button, etc.)
   - Note component props and styling patterns

### Phase 2: Screenshot Analysis

For each screenshot provided:

1. **View the Image**
   - Use Read tool to load the screenshot
   - Claude can view images directly - analyze visual content

2. **Extract Design Elements**
   Identify and document:
   - **Layout structure:** Grid, sidebar width, spacing
   - **Components:** Cards, buttons, forms, lists
   - **Typography:** Heading sizes, font weights, text hierarchy
   - **Colors:** Background, text, borders, brand colors
   - **Spacing:** Padding, margins, gaps between elements
   - **Border radius:** Card corners, button corners
   - **Iconography:** Icon style, size, placement

3. **Map to Design Tokens**
   Convert visual observations to Tailwind classes:
   - Gray background → `bg-page`
   - White cards → `bg-card border border-subtle`
   - Primary button → `bg-primary-brand text-primary-text-on-brand`
   - Card spacing → `p-4 space-y-3`

4. **Identify Interactive States**
   Look for visual cues:
   - Hover effects (darker backgrounds, underlines)
   - Active states (filled vs. outlined)
   - Focus states (borders, shadows)
   - Loading states (skeletons, spinners)

5. **Note Responsive Patterns**
   - Desktop layout vs. mobile (if multiple screenshots)
   - Breakpoint behavior (sidebar collapse, stacking)

### Phase 3: Component Mapping

1. **Match to Existing Components**
   For each UI element in screenshots:
   - Check if similar component exists in codebase
   - If exists: reference it with file path
   - If new: describe what needs to be built

2. **Map Components to Phases** (if phase plan provided)
   For each phase in the plan:
   - Extract phase name and scope description
   - Identify which UI components are needed for that phase
   - Look for frontend file lists in phase scope sections
   - Note component enhancements vs. new components
   - Track dependencies (Phase 2 enhances Phase 1 components)

   **What to extract from phase plan:**
   - Phase number and name (e.g., "Phase 1: Foundation")
   - Scope description (what user can do after this phase)
   - Frontend file paths listed in phase scope
   - Component names from file paths (e.g., `CreatePostModal.tsx` → `<CreatePostModal />`)
   - Enhancement notes (e.g., "Update PostDetail.tsx - show pinned indicators")

3. **Create Component Inventory**
   Table format:
   | Screenshot Element | Koulu Component | Phase | Status | Notes |
   |-------------------|-----------------|-------|--------|-------|
   | Post card | `<FeedPostCard />` | Phase 4 | New | Similar to existing Card pattern |
   | Category pills | `<CategoryTabs />` | Phase 4 | New | See screenshot 2 |
   | Create post form | `<CreatePostModal />` | Phase 1 | New | Reuse Form components |
   | Pin button | `<PostActions />` | Phase 2 | New | Admin only |

### Phase 4: Generate UI_SPEC.md

Create structured specification document:

```markdown
# [Feature Name] - UI Specification

*Generated from Skool.com screenshots on [date]*

## Visual References

- Screenshot 1: [Brief description]
- Screenshot 2: [Brief description]
...

## Phase-to-Component Mapping

*(If phase plan provided)*

### Phase 1: [Phase Name]
**Scope:** [Brief description from phase plan]

**Components:**
- `<ComponentName />` - See section below (Line X)
- `<AnotherComponent />` - See section below (Line Y)

**UI Elements:**
- [List of UI elements to implement in this phase]

### Phase 2: [Phase Name]
**Scope:** [Brief description]

**Components:**
- `<ComponentName />` - See section below
- Enhancements to `<ExistingComponent />` from Phase 1

**UI Elements:**
- [List of new/enhanced UI elements]

### Phase 3: [Phase Name]
...

**Note:** This mapping helps you implement the feature incrementally. During each phase, focus only on the components listed for that phase. Later phase components are fully spec'd below but should be skipped until their phase.

---

## Layout Structure

### Desktop (>768px)
[ASCII diagram or description]
- Container: `max-w-[1100px]`
- Grid: `grid-cols-[2fr_360px] gap-6`
- Main area: [width/behavior]
- Sidebar: [width/behavior]

### Mobile (<768px)
[Description of stacked layout]

---

## Component Specifications

### [Component Name] *(Phase N)*

**Screenshot reference:** [File name]

**Implementation phase:** Phase N - [Phase name]

**Purpose:** [What it does]

**Structure:**
```tsx
<div className="bg-card border border-subtle rounded-lg p-4">
  <header className="flex items-center gap-3 mb-3">
    <Avatar />
    <div>
      <h3 className="text-primary font-semibold text-base">Title</h3>
      <p className="text-secondary text-sm">Metadata</p>
    </div>
  </header>
  <div className="space-y-2">
    [Content area]
  </div>
  <footer className="flex gap-4 mt-3 pt-3 border-t border-subtle">
    [Actions]
  </footer>
</div>
```

**Design tokens used:**
- Background: `bg-card`
- Border: `border-subtle`
- Spacing: `p-4`, `gap-3`, `space-y-2`
- Text: `text-primary`, `text-secondary`
- Border radius: `rounded-lg` (8px)

**Interactive states:**
- Hover: [Description + classes]
- Active: [Description + classes]
- Loading: [Description]
- Empty: [Description]

**Existing pattern reference:** [Path to similar component or "None - new pattern"]

---

[Repeat for each component]

## Color Palette Usage

From screenshots observed:
- Page background: `#F7F9FA` → `bg-page`
- Card background: `#FFFFFF` → `bg-card`
- Primary text: `#1D2129` → `text-primary`
- Secondary text: `#65676B` → `text-secondary`
- Brand accent: `#F7B955` → `bg-primary-brand`
- Borders: `#E4E6EB` → `border-subtle`

## Typography Scale

| Element | Screenshot Size | Tailwind Class | Weight |
|---------|----------------|----------------|--------|
| Page heading | ~28px | `text-3xl` | `font-bold` |
| Card title | ~18px | `text-lg` | `font-semibold` |
| Body text | ~15px | `text-base` | `font-normal` |
| Metadata | ~13px | `text-sm` | `font-normal` |

## Spacing System

| Gap Type | Screenshot Measurement | Tailwind Class |
|----------|----------------------|----------------|
| Between cards | ~16px | `space-y-4` |
| Card padding | ~16px | `p-4` |
| Section gap | ~24px | `gap-6` |
| Icon-to-text | ~8px | `gap-2` |

## Interactive Patterns

### [Pattern Name]
**Where:** [Location in screenshot]
**Behavior:** [Describe interaction]
**Implementation:**
- Default state: [Classes]
- Hover: [Classes]
- Active: [Classes]
- Focus: [Classes]

---

## Implementation Checklist

- [ ] Load `ui-design` skill before coding
- [ ] Reuse components: [List existing components to reuse]
- [ ] Create new components: [List new components needed]
- [ ] Follow mobile-first approach
- [ ] Use semantic HTML (`<article>`, `<aside>`, `<nav>`)
- [ ] Test responsive breakpoints
- [ ] Verify color contrast (WCAG AA)
- [ ] Add focus states for accessibility

## Notes for Implementation

[Any specific guidance, edge cases, or considerations]
```

---

## Analysis Questions to Answer

While analyzing screenshots, systematically address:

### Layout
- What is the main layout structure? (sidebar? tabs? single column?)
- What are the container widths?
- How does spacing work between major sections?
- What changes on mobile?

### Component Hierarchy
- What are the primary UI components visible?
- How do they nest or relate to each other?
- Which components repeat (lists, grids)?

### Visual Design
- What background colors are used?
- What is the card/container styling?
- What border styles are applied?
- What border radius values are used?
- What shadows (if any) are applied?

### Typography
- What font sizes are used for different text types?
- What font weights are applied?
- What is the text color hierarchy?
- What is the line height / spacing?

### Interactive Elements
- How do buttons look (filled? outlined? text-only?)
- What hover states are visible or implied?
- Are there tabs, pills, or filter buttons? How do they look?
- What icons are used? What style?

### Content Patterns
- How is user-generated content displayed?
- How are metadata (timestamps, counts, authors) shown?
- What empty states might be needed?
- What loading states are shown?

### Consistency Check
- Does this match the existing design system?
- Are there any deviations from Koulu's standard patterns?
- Do custom colors/spacing need to be justified?

---

## Output

**Primary:** Create `docs/features/[feature-name]/UI_SPEC.md`

**Secondary (optional):**
- Create annotated versions of screenshots with labeled measurements
- Generate a component dependency graph if complex

**Report to user:**
1. Summary of components identified
2. List of reusable vs. new components
3. Any design system deviations noted
4. Implementation complexity estimate (simple/medium/complex)
5. Path to generated UI_SPEC.md

---

## Example Usage

```bash
User: /generate-ui-spec

Claude: I'll help you generate a UI specification from Skool.com screenshots.

Please provide:
1. Path to your PRD:
2. Path to screenshot directory:
3. (Optional) Path to phase plan:
4. (Optional) Specific focus areas:

User:
1. docs/features/community/feed-prd.md
2. docs/features/community/screenshots/
3. docs/features/community/feed-implementation-phases.md
4. Focus on the post card and category filter components

Claude:
[Reads PRD]
[Reads phase plan - extracts 4 phases and component mapping]
[Loads design system]
[Scans existing components]
[Views each screenshot]
[Analyzes visual patterns]
[Maps to design tokens]
[Maps components to phases]
[Generates UI_SPEC.md with phase organization]

Generated UI specification at:
docs/features/community/UI_SPEC.md

Summary:
- 5 screenshots analyzed
- 4 phases identified from implementation plan
- 8 components mapped to phases:
  Phase 1: CreatePostModal, PostDetail
  Phase 2: PostActions (pin/lock)
  Phase 3: CommentList, CommentForm, LikeButton
  Phase 4: FeedView, PostCard, CategorySidebar
- 6 can reuse existing patterns (Card, Avatar, Button, Form, etc.)
- 2 need new components (FeedPostCard, CategoryTabs)
- Design tokens: All patterns match existing system
- Complexity: Medium (new components follow established patterns)

The UI_SPEC includes a Phase-to-Component Mapping section to guide incremental implementation.
```

---

## Edge Cases

- **No screenshots provided:** Ask user for screenshot directory
- **Screenshots don't match feature:** Ask for clarification or refocus
- **Pattern conflicts with design system:** Flag discrepancies, ask which to follow
- **Ambiguous visual elements:** Note uncertainty in UI_SPEC, mark for user clarification
- **Missing PRD:** Can still generate UI spec, but less context-aware

---

## Integration with Other Skills

**Before this skill:**
- `write-feature-spec` - Creates PRD/BDD
- Phase planning (manual) - Creates `[feature]-implementation-phases.md` for complex features

**After this skill:**
- `write-technical-design` - Uses UI_SPEC for detailed component design
- `implement-feature` - Uses UI_SPEC for implementation guidance

**Workflow (Simple Feature):**
1. Write PRD (`write-feature-spec`)
2. Gather Skool.com screenshots
3. **Generate UI spec (`generate-ui-spec`)** ← This skill
4. Write TDD (`write-technical-design`)
5. Implement feature (`implement-feature`)

**Workflow (Complex/Phased Feature):**
1. Write PRD (`write-feature-spec`)
2. Create phase plan (e.g., `feed-implementation-phases.md`)
3. Gather Skool.com screenshots (complete feature)
4. **Generate UI spec (`generate-ui-spec` with phase plan)** ← This skill
5. Write TDD (`write-technical-design`)
6. Implement Phase 1 (`implement-feature` - reads Phase 1 sections of UI_SPEC)
7. Implement Phase 2 (`implement-feature` - reads Phase 2 sections of UI_SPEC)
8. ... continue until all phases complete
