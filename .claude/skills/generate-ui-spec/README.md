# Generate UI Spec Skill

Automatically generate `UI_SPEC.md` by analyzing Skool.com reference screenshots.

## How It Works

This skill leverages Claude's multimodal capabilities to:
1. **View** your Skool.com screenshots (PNG/JPG)
2. **Extract** design patterns (layout, colors, spacing, typography)
3. **Map** to Koulu's design system (Tailwind classes, design tokens)
4. **Generate** structured UI_SPEC.md with component specifications

## Usage

### Step 1: Prepare Screenshots

Save Skool.com reference screenshots to a directory:

```bash
docs/features/community-feed/screenshots/
├── 01-feed-overview.png
├── 02-post-card-detail.png
├── 03-category-filters.png
└── 04-sidebar-widgets.png
```

**Tips for good screenshots:**
- Capture full page layout (including sidebar if present)
- Zoom in on specific components for detail shots
- Include interactive states if visible (hover, active tabs)
- Capture mobile views separately if available

### Step 2: Invoke the Skill

```bash
/generate-ui-spec
```

Claude will prompt you for:
1. **PRD path** - e.g., `docs/features/community/feed-prd.md`
2. **Screenshot directory** - e.g., `docs/features/community/screenshots/`
3. **(Optional) Phase plan path** - e.g., `docs/features/community/feed-implementation-phases.md`
4. **(Optional) Focus areas** - e.g., "Focus on post card and comment section"

**Tip:** If your feature uses phased implementation (recommended for complex features), provide the phase plan. The skill will organize components by phase in the UI_SPEC.

### Step 3: Review Generated Spec

The skill creates: `docs/features/[feature-name]/UI_SPEC.md`

Contains:
- Layout structure (desktop/mobile)
- Component specifications with Tailwind classes
- Design token mappings
- Interactive state definitions
- Links to existing reusable components
- Implementation checklist

## What Gets Analyzed

### From Screenshots:
- ✅ **Layout:** Grid structure, sidebar width, responsive behavior
- ✅ **Components:** Cards, buttons, forms, lists, navigation
- ✅ **Colors:** Backgrounds, text, borders, brand colors
- ✅ **Typography:** Font sizes, weights, line heights
- ✅ **Spacing:** Padding, margins, gaps
- ✅ **Borders:** Radius, colors, widths
- ✅ **Icons:** Style, size, placement
- ✅ **States:** Hover, active, focus, loading, empty

### From PRD:
- ✅ **Feature scope:** What components are actually needed
- ✅ **User flows:** Which interactions to specify
- ✅ **Acceptance criteria:** Edge cases and states to cover

### From Phase Plan (if provided):
- ✅ **Phase structure:** How implementation is broken down
- ✅ **Component-to-phase mapping:** Which components belong to which phase
- ✅ **Phase dependencies:** What must be built first
- ✅ **Incremental scope:** What UI to focus on per phase

### From Existing Codebase:
- ✅ **Reusable components:** What can be reused vs. built new
- ✅ **Patterns:** How similar features were implemented
- ✅ **Design tokens:** Available Tailwind classes and custom colors

## Example Output

```markdown
# Community Feed - UI Specification

*Generated from Skool.com screenshots on 2026-02-07*

## Phase-to-Component Mapping

### Phase 1: Foundation - Posts Create & View
**Scope:** Create the foundation with Posts aggregate and basic CRUD. Users can create posts with categories and view individual posts.

**Components:**
- `<CreatePostModal />` - See section below
- `<PostDetail />` - See section below
- `<CategorySelect />` - Dropdown for category selection

**UI Elements:**
- Post creation form with title, content, category, optional image
- Individual post view with author, timestamp, content

### Phase 2: Roles, Permissions & Rate Limiting
**Scope:** Add role-based permissions, post pinning/locking, and rate limiting.

**Components:**
- `<PostActions />` - See section below (pin/lock buttons for admins)
- `<AdminBadge />` - Role indicator
- Enhancements to `<PostDetail />` from Phase 1 (show pinned/locked indicators)

**UI Elements:**
- Pin/unpin button (admin only)
- Lock/unlock button (admin only)
- Pinned indicator badge
- Locked indicator icon

### Phase 3: Comments & Reactions
**Scope:** Add Comments and Reactions (likes) to posts. Enable threaded discussions.

**Components:**
- `<CommentList />` - See section below
- `<CommentForm />` - See section below
- `<LikeButton />` - See section below
- Enhancements to `<PostDetail />` (add comments section, like button)

**UI Elements:**
- Comment thread display (max depth 1)
- Comment input form
- Like/unlike buttons for posts and comments
- Like count display
- Soft-deleted comment placeholders

### Phase 4: Feed Display & Category Management
**Scope:** Implement the feed with Hot/New/Top sorting, cursor pagination, category filtering.

**Components:**
- `<FeedView />` - See section below (main feed container)
- `<PostCard />` - See section below (feed item)
- `<CategorySidebar />` - See section below
- `<SortDropdown />` - See section below
- `<CategoryManagementModal />` - Admin category CRUD (new)

**UI Elements:**
- Feed layout with sort controls
- Category filter sidebar
- Pagination controls
- Empty feed state
- Category management UI (admin)

**Note:** This mapping helps you implement the feature incrementally. During each phase, focus only on the components listed for that phase. Later phase components are fully spec'd below but should be skipped until their phase.

---

## Layout Structure (Final - Phase 4)

### Desktop (>768px)
- Container: `max-w-[1100px] mx-auto px-4`
- Grid: `grid grid-cols-[1fr_360px] gap-6`
- Feed area: Flexible width, min 600px
- Sidebar: Fixed 360px

### Mobile (<768px)
- Single column layout
- Sidebar stacks below feed

---

## Component: CreatePostModal *(Phase 1)*

**Screenshot reference:** 02-post-creation.png

**Implementation phase:** Phase 1 - Foundation

**Purpose:** Modal form for creating new posts with title, content, category, and optional image.

[... rest of spec ...]

---

## Component: PostDetail *(Phase 1, enhanced in Phase 2 & 3)*

**Screenshot reference:** 03-post-detail.png

**Implementation phase:** Phase 1 (base), Phase 2 (pin/lock indicators), Phase 3 (comments)

**Purpose:** Display individual post with author, content, and actions.

[... rest of spec ...]

---

## Component: FeedPostCard *(Phase 4)*

**Screenshot reference:** 02-post-card-detail.png

**Existing pattern:** Reuse `src/components/ui/Card.tsx` wrapper

**Structure:**
```tsx
<Card className="p-4 space-y-3">
  <header className="flex items-center gap-3">
    <Avatar src={author.avatar} size="md" />
    <div className="flex-1">
      <h3 className="text-base font-semibold text-primary">
        {author.name}
      </h3>
      <p className="text-sm text-secondary">
        {timestamp}
      </p>
    </div>
  </header>

  <div className="space-y-2">
    <h2 className="text-lg font-semibold text-primary">
      {title}
    </h2>
    <div className="text-base text-primary prose">
      {content}
    </div>
  </div>

  <footer className="flex gap-4 pt-3 border-t border-subtle">
    <LikeButton count={likes} />
    <CommentButton count={comments} />
    <ShareButton />
  </footer>
</Card>
```

**Design tokens:**
- Background: `bg-card` (#FFFFFF)
- Border: `border-subtle` (#E4E6EB)
- Spacing: `p-4` (16px), `gap-3` (12px), `space-y-2` (8px)
- Text colors: `text-primary` (#1D2129), `text-secondary` (#65676B)
- Border radius: `rounded-lg` (8px)

**Interactive states:**
- Like button hover: `text-secondary` → `text-primary`
- Like button active: `text-primary-brand` with filled heart icon
- Card hover: Add subtle shadow `hover:shadow-sm` (optional)
```

## Integration with Workflow

**Recommended sequence:**

1. **Write feature spec:** `/write-feature-spec`
   - Creates `PRD.md` and `BDD.feature`

2. **Create phase plan** (for complex features)
   - Create `[feature]-implementation-phases.md`
   - Break feature into vertical slices (see `feed-implementation-phases.md` example)
   - Map BDD scenarios to phases
   - Define phase dependencies

3. **Gather screenshots**
   - Save Skool.com references to `screenshots/` folder
   - Capture complete feature (all phases) in screenshots

4. **Generate UI spec:** `/generate-ui-spec`
   - Analyzes screenshots + PRD + phase plan
   - Creates `UI_SPEC.md` with phase-to-component mapping
   - Documents complete UI, organized by phase

5. **Write technical design:** `/write-technical-design`
   - Uses PRD + UI_SPEC for detailed component architecture

6. **Implement feature:** `/implement-feature`
   - Uses PRD + BDD + TDD + UI_SPEC for implementation
   - For phased features: implement one phase at a time
   - Each phase reads only relevant UI_SPEC sections

## Benefits

✅ **Consistency:** All components mapped to design system tokens
✅ **Speed:** No manual screenshot annotation needed
✅ **Completeness:** Catches layout, spacing, color, typography in one pass
✅ **Reusability:** Identifies existing components to reuse
✅ **Precision:** Uses Claude's vision to extract exact measurements and patterns
✅ **Phase-aware:** Organizes specs by implementation phase for incremental development
✅ **Complete upfront, implement incrementally:** See entire UI before starting, but build piece by piece

## Limitations

⚠️ **Cannot infer behavior:** Animations and complex interactions may need manual description
⚠️ **Static screenshots only:** Cannot analyze actual Skool.com site
⚠️ **Approximations:** Font sizes/spacing estimated, not pixel-perfect
⚠️ **Context required:** Works best when PRD provides feature context

## Using Phase Mapping During Implementation

When you have a UI_SPEC.md with phase mapping:

### During Phase 1 Implementation:

```bash
# Start implementing Phase 1
User: I want to implement Community Feed Phase 1

Claude:
1. Reads feed-prd.md (understands full feature)
2. Reads feed-implementation-phases.md (knows Phase 1 scope)
3. Reads UI_SPEC.md "Phase-to-Component Mapping" section
4. Focuses on Phase 1 components:
   - CreatePostModal specification
   - PostDetail specification
5. Skips Phase 2/3/4 component specs (CommentList, FeedView, etc.)
6. Implements only Phase 1 UI
```

### During Phase 2 Implementation:

```bash
# Continue with Phase 2
User: Implement Community Feed Phase 2

Claude:
1. Reads Phase 2 scope from phases doc
2. Reads UI_SPEC.md sections for:
   - PostActions (new component)
   - PostDetail enhancements (add pin/lock indicators)
3. Enhances existing Phase 1 components
4. Still skips Phase 3/4 specs
```

### Benefits:

- ✅ **Clear scope:** Know exactly which UI to build each phase
- ✅ **No rework:** Component designed upfront with full context
- ✅ **Incremental value:** Each phase delivers working UI
- ✅ **Reduced context:** Focus on subset of specs per phase

---

## Tips for Best Results

1. **Provide multiple screenshots** showing different states and viewports
2. **Include close-ups** of complex components
3. **Add focus areas** in your prompt to emphasize specific components
4. **Review and refine** the generated spec - treat it as a strong starting point, not final truth
5. **Screenshot quality matters** - clear, high-resolution images work best
6. **For phased features:** Always provide the phase plan to get organized specs
7. **Capture complete feature:** Take screenshots of final state (all phases), not just Phase 1
