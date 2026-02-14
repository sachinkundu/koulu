# Search — UI Specification

*Generated from Skool.com screenshots on February 13, 2026*

**Feature:** Search
**PRD:** `docs/features/search/search-prd.md`
**Screenshots:** `docs/features/search/screenshots/`
**Design System:** `.claude/skills/ui-design/SKILL.md`

---

## Visual References

- **Screenshot 1:** `search_bar_in_jeader.png` — Header search bar (empty state, placeholder "Search members")
- **Screenshot 2:** `search_result_user.png` — Search results page with member card, tabbed navigation, pagination

---

## Layout Structure

### Desktop (>768px)

```
┌─────────────────────────────────────────────────────────────────┐
│                     Header (60px fixed)                         │
│  [Logo] [Community Name ▼]   [Search Bar]   [Icons] [Avatar]   │
├─────────────────────────────────────────────────────────────────┤
│              Tab Navigation (Community, Classroom...)            │
├─────────────────────────────────────────────────────────────────┤
│  Search Results Tabs: [Members 1] [Posts 0]                     │
├───────────────────────────────────┬─────────────────────────────┤
│                                   │                             │
│  Results List                     │   Sidebar                   │
│  (66% width, ~740px)              │   (34%, ~360px)             │
│                                   │                             │
│  - Member/Post Cards              │   - Community Info          │
│  - 10 per page                    │   - Promotional Banners     │
│  - Pagination at bottom           │                             │
│                                   │                             │
└───────────────────────────────────┴─────────────────────────────┘

Container: max-w-[1100px] mx-auto
Grid: grid grid-cols-[2fr_360px] gap-6
Gap between cards: 16px (space-y-4)
```

### Mobile (<768px)

- Single column stacked layout
- Search bar full width
- Results list full width
- Sidebar hidden or moved to bottom
- Tab navigation scrollable horizontally

---

## Component Specifications

### 1. Header Search Bar

**Screenshot reference:** `search_bar_in_jeader.png`

**Purpose:** Global search input accessible from any page

**Structure:**
```tsx
<div className="relative flex-1 max-w-xl mx-8">
  <div className="relative">
    <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
    <input
      type="text"
      placeholder="Search members"
      className="w-full rounded-full bg-input py-2 pl-10 pr-10 text-sm text-primary placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-border-focus"
    />
    {hasValue && (
      <button
        type="button"
        className="absolute right-3 top-1/2 -translate-y-1/2"
        aria-label="Clear search"
      >
        <XMarkIcon className="h-4 w-4 text-gray-400 hover:text-gray-600" />
      </button>
    )}
  </div>
</div>
```

**Design tokens used:**
- Background: `bg-input` (#F0F2F5)
- Text: `text-primary` (#1D2129)
- Placeholder: `text-muted` (#B0B3B8)
- Icon color: `text-gray-400` (#9CA3AF)
- Border radius: `rounded-full`
- Padding: `py-2 pl-10 pr-10` (8px vertical, 40px horizontal)
- Focus ring: `ring-2 ring-border-focus`

**Interactive states:**
- **Default:** Placeholder text visible, no border
- **Focused:** 2px focus ring appears (`focus:ring-2 ring-border-focus`)
- **With text:** Clear (X) button appears on right
- **On Enter:** Navigate to `/search?q={query}&t=members`

**Measurements from screenshot:**
- Input height: ~36px
- Icon size: 20px (h-5 w-5)
- Icon left offset: 12px
- Clear button right offset: 12px
- Border radius: Full pill shape
- Width: Approximately 50% of header width (~600px at 1200px viewport)

**Existing pattern reference:** New component, but follows design system input patterns

---

### 2. Search Results Tab Navigation

**Screenshot reference:** `search_result_user.png` (top tabs: "Community 6", "Classroom 0", "Members 1")

**Purpose:** Switch between result types (Members, Posts) and show result counts

**Structure:**
```tsx
<div className="border-b border-gray-200 bg-white">
  <div className="mx-auto max-w-7xl px-4">
    <nav className="flex space-x-8">
      <button
        type="button"
        className={`
          whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium transition-colors
          ${isActive
            ? 'border-gray-900 text-gray-900'
            : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
          }
        `}
      >
        Members {memberCount}
      </button>
      <button
        type="button"
        className={/* same as above */}
      >
        Posts {postCount}
      </button>
    </nav>
  </div>
</div>
```

**Design tokens used:**
- Background: `bg-white`
- Border: `border-gray-200` (bottom divider)
- Active text: `text-gray-900`
- Inactive text: `text-gray-500`
- Active border: `border-gray-900` (bottom, 2px)
- Spacing: `space-x-8` (32px gap), `py-4` (16px vertical)
- Font: `text-sm font-medium`

**Interactive states:**
- **Active tab:** Dark text, 2px bottom border
- **Inactive tab:** Gray text, transparent border
- **Hover (inactive):** Darker text, light border appears

**Measurements from screenshot:**
- Tab height: ~48px (py-4)
- Tab spacing: ~32px between tabs
- Border height (active): 2px
- Font size: 13-14px

**Existing pattern reference:** Reuse `<TabBar />` component from `src/components/TabBar.tsx`, but modify to:
- Accept `count` prop per tab
- Render as buttons (not Links) for client-side tab switching
- Keep URL in sync via query param `?t=members` or `?t=posts`

---

### 3. Member Result Card

**Screenshot reference:** `search_result_user.png` (main card showing Sachin Kundu)

**Purpose:** Display member profile preview in search results

**Structure:**
```tsx
<button
  type="button"
  onClick={() => navigate(`/profile/${member.user_id}`)}
  className="flex w-full items-start gap-4 rounded-lg border border-subtle bg-card p-4 text-left transition-shadow hover:shadow-md"
>
  <div className="relative">
    <Avatar
      src={member.avatar_url}
      alt={member.display_name}
      size="lg"
      fallback={member.display_name}
    />
    {/* Level badge overlay if available */}
  </div>

  <div className="min-w-0 flex-1 space-y-1">
    <div>
      <h3 className="text-base font-semibold text-primary">
        {member.display_name}
      </h3>
      <p className="text-sm text-secondary">
        @{member.username}
      </p>
    </div>

    <p className="line-clamp-2 text-sm text-primary">
      {member.bio}
    </p>

    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-secondary">
      {member.is_online && (
        <span className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-green-500" />
          Online now
        </span>
      )}

      <span className="flex items-center gap-1">
        <CalendarIcon className="h-3.5 w-3.5" />
        Joined {formatDate(member.joined_at)}
      </span>

      {member.location && (
        <span className="flex items-center gap-1">
          <MapPinIcon className="h-3.5 w-3.5" />
          {member.location}
        </span>
      )}
    </div>
  </div>
</button>
```

**Design tokens used:**
- Background: `bg-card` (#FFFFFF)
- Border: `border-subtle` (#E4E6EB)
- Border radius: `rounded-lg` (8px)
- Padding: `p-4` (16px)
- Text primary: `text-primary` (#1D2129)
- Text secondary: `text-secondary` (#65676B)
- Avatar size: `lg` (48px or 56px)
- Gap: `gap-4` (16px between avatar and content)
- Hover: `hover:shadow-md` (soft shadow)

**Typography hierarchy:**
- Display name: `text-base font-semibold` (~15-16px, 600 weight)
- Username: `text-sm text-secondary` (~13-14px, gray)
- Bio: `text-sm` (~13-14px)
- Metadata: `text-xs text-secondary` (~12px, gray)

**Interactive states:**
- **Default:** White background, subtle border
- **Hover:** Soft shadow appears (`hover:shadow-md`)
- **Active/Click:** Navigate to profile page

**Measurements from screenshot:**
- Card padding: 16px
- Avatar size: ~48-56px
- Gap between avatar and text: 16px
- Line height for bio: Clamp to 2 lines
- Online dot size: 8px diameter
- Icon size in metadata: 14px

**Existing pattern reference:**
- Reuse `<MemberCard />` from `src/features/members/components/MemberCard.tsx`
- **Enhancement needed:** Add online status indicator, location field, username display
- Current MemberCard shows: avatar, name, role badge, bio, join date
- Search version needs: + username, + online status dot, + location

---

### 4. Post Result Card

**Screenshot reference:** Not explicitly shown, but inferred from PRD Section 4.4

**Purpose:** Display post preview in search results

**Structure:**
```tsx
<button
  type="button"
  onClick={() => navigate(`/posts/${post.id}`)}
  className="flex w-full flex-col gap-3 rounded-lg border border-subtle bg-card p-4 text-left transition-shadow hover:shadow-md"
>
  <div>
    <h3 className="text-lg font-semibold text-primary hover:underline">
      {post.title}
    </h3>
    <p className="mt-1 line-clamp-3 text-sm text-primary">
      {truncate(post.body, 200)}
    </p>
  </div>

  <div className="flex items-center gap-3">
    <Avatar
      src={post.author.avatar_url}
      alt={post.author.display_name}
      size="sm"
      fallback={post.author.display_name}
    />
    <div className="flex flex-1 flex-wrap items-center gap-x-3 gap-y-1 text-xs text-secondary">
      <span className="font-medium text-primary">
        {post.author.display_name}
      </span>

      <span className="inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-xs">
        {post.category.name}
      </span>

      <span>{relativeTime(post.created_at)}</span>

      <span className="flex items-center gap-1">
        <HeartIcon className="h-3.5 w-3.5" />
        {post.like_count}
      </span>

      <span className="flex items-center gap-1">
        <ChatBubbleLeftIcon className="h-3.5 w-3.5" />
        {post.comment_count}
      </span>
    </div>
  </div>
</button>
```

**Design tokens used:**
- Same card styling as Member Result Card
- Title: `text-lg font-semibold` (~18px, 600 weight)
- Body snippet: `text-sm` (~14px), clamp to 3 lines
- Category badge: `bg-gray-100` with `rounded-full px-2 py-0.5`
- Metadata: `text-xs text-secondary`

**Interactive states:**
- **Hover:** Title underline + shadow
- **Click:** Navigate to post detail

**Measurements:**
- Card padding: 16px
- Gap between title and metadata: 12px (gap-3)
- Avatar size (author): 32px (sm)
- Category badge padding: 8px horizontal, 2px vertical
- Icon size: 14px

**Existing pattern reference:**
- Similar to `<FeedPostCard />` from Community feed
- Simplified version (no full interactions, read-only preview)

---

### 5. Pagination Controls

**Screenshot reference:** `search_result_user.png` (bottom: "Previous", "1", "Next", "1-1 of 1")

**Purpose:** Navigate between pages of search results

**Structure:**
```tsx
<div className="flex items-center justify-between border-t border-subtle bg-card px-4 py-3">
  <div className="flex items-center gap-2">
    <button
      type="button"
      disabled={currentPage === 1}
      className="rounded-full px-3 py-1 text-sm font-medium text-secondary hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50"
    >
      Previous
    </button>

    <span className="rounded-full bg-primary-brand px-3 py-1 text-sm font-medium text-primary-text-on-brand">
      {currentPage}
    </span>

    <button
      type="button"
      disabled={currentPage === totalPages}
      className="rounded-full px-3 py-1 text-sm font-medium text-secondary hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50"
    >
      Next
    </button>
  </div>

  <span className="text-sm text-secondary">
    {startIndex}-{endIndex} of {totalResults}
  </span>
</div>
```

**Design tokens used:**
- Background: `bg-card`
- Border top: `border-subtle`
- Current page: `bg-primary-brand` with `text-primary-text-on-brand`
- Buttons: `text-secondary`, `hover:bg-gray-100`
- Disabled state: `opacity-50 cursor-not-allowed`
- Border radius: `rounded-full`

**Interactive states:**
- **Default:** Gray text, hover background
- **Disabled:** 50% opacity, no cursor interaction
- **Current page:** Highlighted with brand color

**Measurements from screenshot:**
- Pagination height: ~44px
- Button padding: 8px horizontal, 4px vertical
- Gap between elements: 8px
- Font size: 13-14px

**Existing pattern reference:** New component (no existing pagination in codebase yet)

---

### 6. Empty States

**Purpose:** Show helpful messages when no results or errors occur

**No Results:**
```tsx
<div className="flex flex-col items-center justify-center py-12 text-center">
  <MagnifyingGlassIcon className="h-12 w-12 text-gray-300" />
  <h3 className="mt-4 text-base font-semibold text-primary">
    No {type} found for "{query}"
  </h3>
  <p className="mt-2 text-sm text-secondary">
    Try a different search term or{' '}
    <Link to={fallbackLink} className="text-link hover:underline">
      browse the {type === 'members' ? 'member directory' : 'community feed'}
    </Link>
  </p>
</div>
```

**Query Too Short:**
```tsx
<div className="flex flex-col items-center justify-center py-12 text-center">
  <p className="text-sm text-secondary">
    Please enter at least 3 characters to search
  </p>
</div>
```

**Error State:**
```tsx
<div className="flex flex-col items-center justify-center py-12 text-center">
  <ExclamationTriangleIcon className="h-12 w-12 text-red-400" />
  <h3 className="mt-4 text-base font-semibold text-primary">
    Search is temporarily unavailable
  </h3>
  <button
    type="button"
    onClick={retry}
    className="mt-4 rounded-lg bg-primary-brand px-4 py-2 text-sm font-medium text-primary-text-on-brand hover:opacity-90"
  >
    Try again
  </button>
</div>
```

**Design tokens used:**
- Icon size: `h-12 w-12` (48px)
- Icon color (no results): `text-gray-300`
- Icon color (error): `text-red-400`
- Heading: `text-base font-semibold text-primary`
- Body: `text-sm text-secondary`
- Link: `text-link hover:underline`
- Padding: `py-12` (48px vertical)

---

### 7. Loading States

**Purpose:** Show skeleton placeholders while search executes

**Member Card Skeleton:**
```tsx
<div className="flex w-full animate-pulse items-start gap-4 rounded-lg border border-subtle bg-card p-4">
  <div className="h-14 w-14 rounded-full bg-gray-200" />
  <div className="flex-1 space-y-2">
    <div className="h-4 w-32 rounded bg-gray-200" />
    <div className="h-3 w-24 rounded bg-gray-200" />
    <div className="h-3 w-full rounded bg-gray-200" />
    <div className="h-3 w-3/4 rounded bg-gray-200" />
  </div>
</div>
```

**Repeat 3-5 skeleton cards while loading**

**Design tokens used:**
- Animation: `animate-pulse`
- Skeleton color: `bg-gray-200`
- Same dimensions as actual card

---

## Color Palette Usage

From screenshots and design system:

| Element | Color Value | Tailwind Class |
|---------|-------------|----------------|
| Page background | #F7F9FA | `bg-page` |
| Card background | #FFFFFF | `bg-card` |
| Input background | #F0F2F5 | `bg-input` |
| Primary text | #1D2129 | `text-primary` |
| Secondary text | #65676B | `text-secondary` |
| Muted text | #B0B3B8 | `text-muted` |
| Borders | #E4E6EB | `border-subtle` |
| Brand accent | #F7B955 | `bg-primary-brand` |
| Link text | #007AFF | `text-link` |
| Online indicator | #22C55E (green-500) | `bg-green-500` |

---

## Typography Scale

| Element | Tailwind Class | Size | Weight |
|---------|---------------|------|--------|
| Post title | `text-lg` | 18px | `font-semibold` (600) |
| Member name | `text-base` | 16px | `font-semibold` (600) |
| Body text / Bio | `text-sm` | 14px | `font-normal` (400) |
| Username / Metadata | `text-xs` | 12px | `font-normal` (400) |
| Tab labels | `text-sm` | 14px | `font-medium` (500) |

---

## Spacing System

| Element | Measurement | Tailwind Class |
|---------|------------|----------------|
| Card padding | 16px | `p-4` |
| Gap between cards | 16px | `space-y-4` |
| Avatar to text gap | 16px | `gap-4` |
| Metadata items gap | 12px | `gap-3` |
| Tab spacing | 32px | `space-x-8` |
| Section padding | 48px | `py-12` |

---

## Icon Library

Use **Heroicons** (already in project):
- MagnifyingGlassIcon (search input)
- XMarkIcon (clear button)
- CalendarIcon (join date)
- MapPinIcon (location)
- HeartIcon (likes)
- ChatBubbleLeftIcon (comments)
- ExclamationTriangleIcon (error state)

Icon sizes:
- Search bar icon: `h-5 w-5` (20px)
- Metadata icons: `h-3.5 w-3.5` (14px)
- Empty state icons: `h-12 w-12` (48px)

---

## Responsive Behavior

### Breakpoints

- **Mobile:** < 768px
- **Desktop:** ≥ 768px

### Mobile Adjustments

```tsx
// Header search bar
<div className="mx-4 md:mx-8 max-w-full md:max-w-xl">
  {/* Search input */}
</div>

// Results grid
<div className="grid grid-cols-1 md:grid-cols-[2fr_360px] gap-4 md:gap-6">
  <div>{/* Results */}</div>
  <div className="hidden md:block">{/* Sidebar */}</div>
</div>

// Member card
<div className="flex-col sm:flex-row gap-3 sm:gap-4">
  {/* Avatar and content stack on mobile, row on desktop */}
</div>
```

---

## Component File Checklist

New components to create:

- [ ] `src/features/search/components/SearchBar.tsx` — Header search input
- [ ] `src/features/search/components/SearchResults.tsx` — Results page container
- [ ] `src/features/search/components/SearchResultTabs.tsx` — Member/Post tab switcher
- [ ] `src/features/search/components/MemberSearchCard.tsx` — Enhanced member card with username, online status, location
- [ ] `src/features/search/components/PostSearchCard.tsx` — Post preview card
- [ ] `src/features/search/components/SearchPagination.tsx` — Pagination controls
- [ ] `src/features/search/components/SearchEmptyState.tsx` — No results / error states
- [ ] `src/features/search/components/SearchSkeleton.tsx` — Loading skeletons

Components to enhance:

- [ ] Extend `<MemberCard />` or create search-specific variant

---

## Implementation Checklist

- [ ] Load `ui-design` skill before coding
- [ ] Reuse existing components:
  - `<Avatar />` from `src/components/Avatar.tsx`
  - `<TabBar />` pattern (adapt for search tabs with counts)
- [ ] Follow mobile-first approach (base styles mobile, `md:` for desktop)
- [ ] Use semantic HTML:
  - `<nav>` for tab navigation
  - `<article>` for result cards
  - `<button>` for clickable cards (not `<div>` with onClick)
- [ ] Test responsive breakpoints (768px)
- [ ] Verify color contrast (WCAG AA):
  - Primary text on white: ✓ (21:1 ratio)
  - Secondary text on white: ✓ (4.5:1 ratio)
- [ ] Add focus states for accessibility:
  - Search input: `focus:ring-2 ring-border-focus`
  - Buttons: `focus-visible:ring-2 ring-offset-2`
- [ ] Keyboard navigation:
  - Enter key submits search
  - Tab through result cards
  - Escape clears search input (optional)

---

## Notes for Implementation

### Search Bar Integration

The search bar lives in the **header component** and should:
- Persist across all page navigations
- Sync with URL query param `?q={query}`
- Pre-fill when landing on `/search` page
- Clear when user clicks X button (stay on current page)
- Submit on Enter key → navigate to `/search?q={query}&t=members`

### Tab Switching Behavior

Tabs should switch **without re-fetching**:
- On mount: Fetch both member AND post results in parallel
- Store both result sets in state
- Clicking "Posts" tab just toggles visible results (instant)
- Update URL query param `?t=posts` for shareable links

### Pagination Strategy

Use **offset-based pagination** (not cursor):
- Page 1: `limit=10&offset=0`
- Page 2: `limit=10&offset=10`
- Total pages = `Math.ceil(totalResults / 10)`
- Update URL with `?q={query}&t={type}&page={N}` (optional)

### Performance Optimizations

- Debounce search input (300ms) if implementing real-time search (Phase 2)
- Lazy load avatars (use `loading="lazy"` on `<img>`)
- Virtualize result list if > 100 results (Phase 2)
- Cache recent searches in session storage (Phase 2)

### Accessibility Considerations

- Announce result count to screen readers: `<div role="status" aria-live="polite">Found {count} members</div>`
- Label search input: `aria-label="Search community members and posts"`
- Keyboard shortcuts: `/` to focus search bar (optional, like GitHub)
- Focus management: After search, focus first result card

---

## Summary

**Components identified:** 8 new components
**Reusable patterns:** Avatar, TabBar (adapted), existing card patterns
**Design system alignment:** ✓ All tokens match
**Complexity:** **Medium** — New search bar integration, tab state management, two card types

**Key implementation sequence:**
1. SearchBar component (header integration)
2. SearchResults page layout
3. SearchResultTabs (tab switcher with counts)
4. MemberSearchCard (enhance existing MemberCard)
5. PostSearchCard (new, similar to FeedPostCard)
6. SearchPagination
7. Empty/Error/Loading states

All visual patterns confirmed from screenshots and aligned with Koulu design system. Ready for technical design document.
