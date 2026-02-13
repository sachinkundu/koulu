# Member Directory — UI Specification

*Generated from Skool.com screenshots on 2026-02-13*

---

## Visual References

- **directory.png**: Main members page — list view with filter tabs, member cards, sidebar with community stats
- **invite.png**: Invite modal overlay — share link dialog (out of MVP scope)

---

## Design Decisions (Resolved)

All documents (PRD, TDD, UI_SPEC) are harmonized to follow Skool.com's approach:

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Layout | Vertical list (full-width cards) | Matches Skool; better for info-dense member cards than a multi-column grid |
| Role filter | Pill tabs with counts | More discoverable than a dropdown; shows counts at a glance |
| Sort control | Dropdown (Most Recent / Alphabetical) | Not visible in Skool screenshot, but needed per PRD requirements |
| Member card fields | Avatar, name, role badge, bio, join date | Follows PRD MVP scope — excludes online status, location, chat, username (Phase 2+) |

---

## Layout Structure

### Desktop (>1024px)

```
┌──────────────────────────────────────────────────────────┐
│  Header (sticky, 60px) — logo, search bar, nav icons     │
├──────────────────────────────────────────────────────────┤
│  Tab Navigation: Community | Classroom | Calendar | Members │
├────────────────────────────────────┬─────────────────────┤
│                                    │                     │
│  Main Content (~66%)               │  Sidebar (320px)    │
│  ┌──────────────────────────────┐  │  ┌─────────────────┐│
│  │ Filter Tabs + Sort + Search  │  │  │ Promo Card      ││
│  └──────────────────────────────┘  │  ├─────────────────┤│
│  ┌──────────────────────────────┐  │  │ Community Stats ││
│  │ Member Card (full width)     │  │  │ + Invite Button ││
│  ├──────────────────────────────┤  │  └─────────────────┘│
│  │ Member Card (full width)     │  │                     │
│  ├──────────────────────────────┤  │                     │
│  │ Member Card (full width)     │  │                     │
│  ├──────────────────────────────┤  │                     │
│  │ ... infinite scroll          │  │                     │
│  └──────────────────────────────┘  │                     │
│                                    │                     │
└────────────────────────────────────┴─────────────────────┘
```

- Container: `max-w-[1100px] mx-auto px-4`
- Grid: `grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-6`
- Main column: flexible
- Sidebar: fixed 320px, hidden on mobile (`hidden lg:block`)

### Mobile (<1024px)

- Single column, full width
- Sidebar hidden (community stats accessible via existing sidebar pattern)
- Filter tabs scroll horizontally if needed
- Member cards stack vertically

---

## Component Specifications

### 1. MembersPage (Page Container)

**Purpose:** Top-level page for `/members` route. Orchestrates filters, member list, and sidebar.

**Structure:**
```tsx
<div className="mx-auto max-w-[1100px] px-4 py-6">
  <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_320px]">
    {/* Main content */}
    <main>
      <MemberFilters />
      <MemberList />
    </main>

    {/* Sidebar — reuse existing CommunitySidebar */}
    <CommunitySidebar />
  </div>
</div>
```

**Existing pattern reference:** Follows the same two-column layout as the Community feed page.

---

### 2. MemberFilters

**Screenshot reference:** Top of directory.png — "Members 678 | Admins 12 | Online 4" tabs + search

**Purpose:** Controls for filtering, sorting, and searching the member list.

**Structure:**
```tsx
<div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
  {/* Left: Role filter tabs */}
  <div className="flex items-center gap-2">
    <button className="rounded-full bg-gray-900 px-4 py-1.5 text-sm font-medium text-white">
      Members 42
    </button>
    <button className="rounded-full bg-gray-100 px-4 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-200">
      Admins 3
    </button>
  </div>

  {/* Right: Sort dropdown + Search */}
  <div className="flex items-center gap-2">
    <SortDropdown />
    <div className="relative">
      <svg className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
      <input
        type="text"
        placeholder="Search members..."
        className="rounded-lg bg-gray-100 py-2 pl-9 pr-4 text-sm text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-300"
      />
    </div>
  </div>
</div>
```

**Design tokens used:**
- Active tab: `bg-gray-900 text-white rounded-full px-4 py-1.5`
- Inactive tab: `bg-gray-100 text-gray-700 rounded-full px-4 py-1.5 hover:bg-gray-200`
- Search input: `bg-gray-100 rounded-lg text-sm` (matches `SortDropdown` trigger style)
- Gap between controls: `gap-2`

**Interactive states:**
- Active tab: Dark fill (`bg-gray-900 text-white`)
- Inactive tab hover: `bg-gray-200`
- Search input focus: `focus:ring-2 focus:ring-gray-300`
- Counts update dynamically as filters change

**Note:** For MVP, role tabs are "All" (default) and "Admin" and "Moderator" per PRD. "Online" tab is out of scope.

---

### 3. MemberCard

**Screenshot reference:** directory.png — individual member rows (Eric Pureheart, Maxence Tison, Tim Ungacta)

**Purpose:** Displays a single member's summary. Clickable to navigate to profile.

**Structure:**
```tsx
<article
  className="cursor-pointer rounded-lg border border-gray-200 bg-white p-4 transition-shadow hover:shadow-sm"
>
  <div className="flex items-start gap-4">
    {/* Avatar */}
    <Avatar src={member.avatar_url} alt={name} fallback={name} size="lg" />

    {/* Info */}
    <div className="min-w-0 flex-1">
      <div className="flex items-center gap-2">
        <h3 className="truncate text-base font-semibold text-gray-900">
          {member.display_name}
        </h3>
        {/* Role badge — Admin/Moderator only */}
        {role !== 'member' && (
          <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-800">
            {role}
          </span>
        )}
      </div>

      {/* Bio */}
      <p className="mt-1 text-sm text-gray-500 line-clamp-2">
        {member.bio || 'No bio'}
      </p>

      {/* Join date */}
      <div className="mt-2 flex items-center gap-1.5 text-xs text-gray-400">
        <svg className="h-3.5 w-3.5" /* calendar icon */ />
        <span>Joined {relativeDate(member.joined_at)}</span>
      </div>
    </div>
  </div>
</article>
```

**Design tokens used:**
- Card: `bg-white border border-gray-200 rounded-lg p-4`
- Name: `text-base font-semibold text-gray-900 truncate`
- Bio: `text-sm text-gray-500 line-clamp-2`
- Join date: `text-xs text-gray-400`
- Role badge (Admin): `bg-yellow-100 text-yellow-800 rounded-full px-2 py-0.5 text-xs font-medium`
- Role badge (Moderator): `bg-blue-100 text-blue-800 rounded-full px-2 py-0.5 text-xs font-medium`
- Avatar: Reuse existing `<Avatar size="lg" />` (48x48, circular)

**Interactive states:**
- Hover: `hover:shadow-sm` (subtle elevation, matching `FeedPostCard`)
- Click: Navigates to `/profile/:userId`

**Existing pattern reference:** Card layout follows `FeedPostCard` conventions (border, padding, hover shadow).

---

### 4. MemberList

**Purpose:** Renders the scrollable list of `MemberCard` components with infinite scroll.

**Structure:**
```tsx
<div className="space-y-3">
  {/* Member cards */}
  {members.map(member => (
    <MemberCard key={member.id} member={member} />
  ))}

  {/* Loading more indicator */}
  {isFetchingNextPage && (
    <div className="flex justify-center py-4">
      <div className="h-6 w-6 animate-spin rounded-full border-2 border-gray-300 border-t-gray-600" />
    </div>
  )}

  {/* Infinite scroll sentinel */}
  <div ref={sentinelRef} />
</div>
```

**Design tokens used:**
- Card gap: `space-y-3`
- Spinner: `h-6 w-6 animate-spin border-2 border-gray-300 border-t-gray-600`

---

### 5. MemberCardSkeleton

**Purpose:** Loading placeholder shown during initial directory load.

**Structure:**
```tsx
<div className="animate-pulse rounded-lg border border-gray-200 bg-white p-4">
  <div className="flex items-start gap-4">
    {/* Avatar skeleton */}
    <div className="h-12 w-12 rounded-full bg-gray-200" />

    <div className="flex-1 space-y-2">
      {/* Name skeleton */}
      <div className="h-4 w-32 rounded bg-gray-200" />
      {/* Bio skeleton */}
      <div className="h-3 w-64 rounded bg-gray-100" />
      {/* Date skeleton */}
      <div className="h-3 w-24 rounded bg-gray-100" />
    </div>
  </div>
</div>
```

**Design tokens used:**
- Skeleton colors: `bg-gray-200` (primary), `bg-gray-100` (secondary)
- Animation: `animate-pulse`

---

### 6. MemberEmptyState

**Purpose:** Shown when no members match the current search/filter.

**Structure:**
```tsx
<div className="flex flex-col items-center justify-center rounded-lg border border-gray-200 bg-white py-12 text-center">
  <svg className="mb-3 h-12 w-12 text-gray-300" /* users icon */ />
  <p className="text-base font-medium text-gray-500">
    No members found
  </p>
  <p className="mt-1 text-sm text-gray-400">
    Try adjusting your search or filters.
  </p>
</div>
```

---

### 7. Members Tab (in TabBar)

**Screenshot reference:** directory.png — "Members" tab in navigation, underlined/bold when active

**Purpose:** Add "Members" to the existing `TabBar` navigation.

**Implementation:** No new component needed — add entry to the existing `tabs` array:
```tsx
{ label: 'Members', path: '/members' }
```

The tab should show a member count badge. Extend `TabBar` `Tab` interface to support an optional `badge` field:
```tsx
interface Tab {
  label: string;
  path: string;
  badge?: number; // e.g., "Members (42)"
}
```

**Badge styling:** `ml-1.5 rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600`

---

## Color Palette Usage

From screenshots observed, mapped to existing codebase conventions:

| Element | Skool Color | Tailwind Class | Notes |
|---------|-------------|----------------|-------|
| Page background | `#F7F9FA` | `bg-gray-50` | Closest existing token |
| Card background | `#FFFFFF` | `bg-white` | Standard |
| Primary text | `#1D2129` | `text-gray-900` | Names, headings |
| Secondary text | `#65676B` | `text-gray-500` | Bio, metadata |
| Muted text | `#B0B3B8` | `text-gray-400` | Timestamps, placeholders |
| Borders | `#E4E6EB` | `border-gray-200` | Card borders, dividers |
| Active filter bg | Dark | `bg-gray-900 text-white` | Active pill tab |
| Inactive filter bg | Light gray | `bg-gray-100 text-gray-700` | Inactive pill tab |
| Admin badge | Yellow | `bg-yellow-100 text-yellow-800` | Role indicator |
| Moderator badge | Blue | `bg-blue-100 text-blue-800` | Role indicator |
| Brand accent | `#F7B955` | `bg-yellow-400` | Used in sidebar promo |

---

## Typography Scale

| Element | Tailwind Class | Weight | Usage |
|---------|----------------|--------|-------|
| Member name | `text-base` (16px) | `font-semibold` | Card heading |
| Bio text | `text-sm` (14px) | `font-normal` | Card body |
| Join date | `text-xs` (12px) | `font-normal` | Card metadata |
| Filter tab text | `text-sm` (14px) | `font-medium` | Filter controls |
| Filter count | `text-sm` (14px) | `font-medium` | Inline with tab label |
| Empty state title | `text-base` (16px) | `font-medium` | Empty state heading |
| Empty state body | `text-sm` (14px) | `font-normal` | Empty state description |

---

## Spacing System

| Gap Type | Tailwind Class | Where Used |
|----------|----------------|------------|
| Page-to-content | `py-6` | MembersPage top/bottom padding |
| Main-to-sidebar | `gap-6` | Grid gap between columns |
| Between member cards | `space-y-3` | MemberList vertical spacing |
| Card padding | `p-4` | MemberCard internal padding |
| Avatar-to-info | `gap-4` | Inside MemberCard flex row |
| Name-to-badge | `gap-2` | Name + role badge inline |
| Bio-to-date | `mt-2` | Vertical spacing inside card |
| Filter-to-list | `mb-4` | Below MemberFilters |
| Between filter pills | `gap-2` | Filter tab group |

---

## Interactive Patterns

### Card Hover
**Where:** MemberCard
**Behavior:** Subtle shadow appears on hover, indicating clickability
**Implementation:**
- Default: `border border-gray-200 bg-white`
- Hover: `hover:shadow-sm`
- Matches existing `FeedPostCard` hover pattern

### Card Click
**Where:** MemberCard
**Behavior:** Navigates to `/profile/:userId`
**Implementation:** Entire `<article>` is clickable via `onClick` + `cursor-pointer`

### Filter Tab Toggle
**Where:** MemberFilters
**Behavior:** Clicking a tab filters the list; active tab fills dark
**Implementation:**
- Default: `bg-gray-100 text-gray-700`
- Active: `bg-gray-900 text-white`
- Transition: `transition-colors`

### Search Debounce
**Where:** MemberFilters search input
**Behavior:** Types → debounce 300ms → re-filters member list
**Implementation:** `useEffect` with `setTimeout` / dedicated `useDebouncedValue` hook

### Infinite Scroll
**Where:** MemberList
**Behavior:** Loading spinner appears, new batch of 20 members loads
**Implementation:** `IntersectionObserver` on a sentinel `<div>` at list bottom

---

## Implementation Checklist

- [ ] Load `ui-design` skill before coding
- [ ] Reuse components: `Avatar`, `TabBar`, `CommunitySidebar`, `SortDropdown` pattern
- [ ] Create new components: `MemberCard`, `MemberFilters`, `MemberList`, `MemberCardSkeleton`, `MemberEmptyState`
- [ ] Create new page: `MembersPage`
- [ ] Add "Members" tab to navigation `TabBar`
- [ ] Follow mobile-first approach (`grid-cols-1` → `lg:grid-cols-[1fr_320px]`)
- [ ] Use semantic HTML (`<article>` for cards, `<main>` for content area)
- [ ] Use `line-clamp-2` for bio truncation
- [ ] Implement search debounce (300ms)
- [ ] Implement infinite scroll with IntersectionObserver
- [ ] Test responsive breakpoints (mobile single-column, desktop two-column)
- [ ] Verify color contrast (WCAG AA)
- [ ] Add focus states for keyboard accessibility on cards and tabs
- [ ] Add `data-testid` attributes for E2E testing

---

## Notes for Implementation

1. **Reuse `CommunitySidebar`** — the right sidebar in the screenshot is identical to the existing component. No new sidebar work needed.

2. **Adapt `SortDropdown`** — the existing component uses `'hot' | 'new' | 'top'` values. Create a variant or new component with `'recent' | 'alphabetical'` sort options for the directory.

3. **Avatar size** — the screenshot shows larger avatars (~48px) for member cards. The existing `Avatar` component has `lg` size at 48px (`h-12 w-12`), which matches.

4. **No username/@handle** — the PRD does not include usernames. The screenshot shows them, but they're out of MVP scope.

5. **No "Online" filter tab** — requires WebSocket presence tracking, explicitly out of scope per PRD Section 7.1.

6. **No "Chat" button** — depends on unbuilt DM feature, out of scope.

7. **No location field** — not in PRD member card fields.

8. **Role filter tabs** — pill tabs with counts, matching Skool's approach. MVP tabs: "All (N)", "Admin (N)", "Moderator (N)". PRD and TDD harmonized to match.
