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
1. **PRD path** - e.g., `docs/features/community-feed/PRD.md`
2. **Screenshot directory** - e.g., `docs/features/community-feed/screenshots/`
3. **(Optional) Focus areas** - e.g., "Focus on post card and comment section"

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

### From Existing Codebase:
- ✅ **Reusable components:** What can be reused vs. built new
- ✅ **Patterns:** How similar features were implemented
- ✅ **Design tokens:** Available Tailwind classes and custom colors

## Example Output

```markdown
# Community Feed - UI Specification

## Layout Structure

### Desktop (>768px)
- Container: `max-w-[1100px] mx-auto px-4`
- Grid: `grid grid-cols-[1fr_360px] gap-6`
- Feed area: Flexible width, min 600px
- Sidebar: Fixed 360px

### Mobile (<768px)
- Single column layout
- Sidebar stacks below feed

---

## Component: FeedPostCard

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

1. Write feature spec: `/write-feature-spec`
   - Creates `PRD.md` and `BDD.feature`

2. **Gather screenshots**
   - Save Skool.com references to `screenshots/` folder

3. **Generate UI spec: `/generate-ui-spec`**
   - Analyzes screenshots + PRD
   - Creates `UI_SPEC.md`

4. Write technical design: `/write-technical-design`
   - Uses PRD + UI_SPEC for detailed component architecture

5. Implement feature: `/implement-feature`
   - Uses PRD + BDD + TDD + UI_SPEC for implementation

## Benefits

✅ **Consistency:** All components mapped to design system tokens
✅ **Speed:** No manual screenshot annotation needed
✅ **Completeness:** Catches layout, spacing, color, typography in one pass
✅ **Reusability:** Identifies existing components to reuse
✅ **Precision:** Uses Claude's vision to extract exact measurements and patterns

## Limitations

⚠️ **Cannot infer behavior:** Animations and complex interactions may need manual description
⚠️ **Static screenshots only:** Cannot analyze actual Skool.com site
⚠️ **Approximations:** Font sizes/spacing estimated, not pixel-perfect
⚠️ **Context required:** Works best when PRD provides feature context

## Tips for Best Results

1. **Provide multiple screenshots** showing different states and viewports
2. **Include close-ups** of complex components
3. **Add focus areas** in your prompt to emphasize specific components
4. **Review and refine** the generated spec - treat it as a strong starting point, not final truth
5. **Screenshot quality matters** - clear, high-resolution images work best
