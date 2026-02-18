# Leaderboards - UI Specification

*Generated from Skool.com screenshots on February 18, 2026*

## Visual References

- **leaderboard-page-top.png:** Full leaderboards page — profile card (left), level definitions grid (right), timestamp, three side-by-side ranking panels with medal icons and member rows
- **leaderboard-page-bottom-your-rank.png:** Same page scrolled to show "Your rank" rows below the top 10 in the 30-day and all-time panels
- **sidebar-leaderboard-widget.png:** Community feed page — right sidebar showing compact 5-member 30-day leaderboard widget with "See all leaderboards" link

---

## Layout Structure

### Desktop (>768px)

```
┌──────────────────────────────────────────────────┐
│               Header (60px, existing)             │
├──────────────────────────────────────────────────┤
│               Tabs Nav (existing)                 │
├──────────────────────────────────────────────────┤
│                                                  │
│  max-w-[1100px] mx-auto px-4 py-8               │
│  ┌──────────────────────────────────────────┐   │
│  │  ProfileCard (~280px)  │ LevelDefs (~grow)│   │
│  └──────────────────────────────────────────┘   │
│  Last updated: Feb 18th 2026 11:16am             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ 7-day    │  │ 30-day   │  │ All-time │       │
│  │ Panel    │  │ Panel    │  │ Panel    │       │
│  │          │  │          │  │          │       │
│  │          │  │ - - - -  │  │ - - - -  │       │
│  │          │  │ Your rank│  │ Your rank│       │
│  └──────────┘  └──────────┘  └──────────┘       │
│                                                  │
└──────────────────────────────────────────────────┘
```

- Container: `max-w-[1100px] mx-auto px-4 py-8`
- Top section grid: `grid grid-cols-[280px_1fr] gap-6` (profile card left, level definitions right)
- Three panels: `grid grid-cols-3 gap-4 mt-6`

### Mobile (<768px)

- Top section: profile card stacks above level definitions grid
- Three panels stack vertically (`grid-cols-1`)
- Each panel shows full content (no accordion/tabs needed for MVP)

### Community Feed Sidebar

The `LeaderboardSidebarWidget` is added to `CommunitySidebar.tsx` as a new card below the community stats card, visible on the community feed page at `/community`.

---

## Component Inventory

| Screenshot Element | Koulu Component | Status | Notes |
|---|---|---|---|
| Leaderboards page layout | `LeaderboardsPage` (existing — enhance) | Enhance | Add profile card, timestamp, three panels |
| Profile card (left top) | `LeaderboardProfileCard` | New | Avatar + level + points to level up |
| Level definitions grid (right top) | `LevelDefinitionsGrid` | Existing | Already implemented, reuse as-is |
| "Last updated" timestamp | Inline in `LeaderboardsPage` | Inline | Simple `<p>` element |
| Three-panel container | Inline in `LeaderboardsPage` | Inline | CSS grid wrapper |
| Single ranking panel | `LeaderboardPanel` | New | Card with header + rows + your rank |
| Ranked member row | `LeaderboardRow` | New | Rank/medal + avatar + name + points |
| Medal icon (top 3) | `RankMedal` | New | Gold/silver/bronze icon |
| "Your rank" section | `YourRankSection` | New | Divider + label + row |
| Sidebar 30-day widget | `LeaderboardSidebarWidget` | New | Compact 5-row version |
| CommunitySidebar | `CommunitySidebar` (existing — enhance) | Enhance | Add widget below stats card |

---

## Component Specifications

### LeaderboardsPage *(Enhance existing)*

**Screenshot reference:** leaderboard-page-top.png

**Purpose:** Full leaderboards page at `/leaderboards`. Replaces current stub with complete layout.

**Structure:**
```tsx
<div className="mx-auto max-w-[1100px] px-4 py-8">
  {/* Top section: Profile card + Level definitions */}
  <div className="grid grid-cols-1 gap-6 md:grid-cols-[280px_1fr]">
    <LeaderboardProfileCard
      avatarUrl={currentUser.avatarUrl}
      displayName={currentUser.displayName}
      level={currentUser.level}
      levelName={currentUser.levelName}
      pointsToNextLevel={currentUser.pointsToNextLevel}
      isMaxLevel={currentUser.isMaxLevel}
    />
    <LevelDefinitionsGrid
      levels={levels}
      currentUserLevel={currentUser.level}
    />
  </div>

  {/* Timestamp */}
  <p className="mt-4 text-sm text-gray-500">
    Last updated: {formattedTimestamp}
  </p>

  {/* Three leaderboard panels */}
  <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">
    <LeaderboardPanel
      title="Leaderboard (7-day)"
      entries={sevenDayEntries}
      yourRank={sevenDayYourRank}
      period="7day"
      isLoading={isLoading}
    />
    <LeaderboardPanel
      title="Leaderboard (30-day)"
      entries={thirtyDayEntries}
      yourRank={thirtyDayYourRank}
      period="30day"
      isLoading={isLoading}
    />
    <LeaderboardPanel
      title="Leaderboard (All-time)"
      entries={allTimeEntries}
      yourRank={allTimeYourRank}
      period="alltime"
      isLoading={isLoading}
    />
  </div>
</div>
```

**Design tokens used:**
- Container: `max-w-[1100px] mx-auto px-4 py-8`
- Top grid: `grid-cols-1 md:grid-cols-[280px_1fr] gap-6`
- Timestamp: `text-sm text-gray-500 mt-4`
- Panel grid: `grid-cols-1 md:grid-cols-3 gap-4 mt-6`

---

### LeaderboardProfileCard *(New component)*

**Screenshot reference:** leaderboard-page-top.png — left side of top section

**Purpose:** Display the current member's avatar (with level badge), name, level, and points to level up. Left column of the top section.

**Structure:**
```tsx
<div className="flex flex-col items-center rounded-lg border border-gray-200 bg-white p-6">
  {/* Avatar with level badge */}
  <Avatar
    src={avatarUrl}
    alt={displayName}
    size="lg"
    fallback={displayName}
    level={level}
  />

  {/* Display name */}
  <h2 className="mt-3 text-lg font-bold text-gray-900">{displayName}</h2>

  {/* Level label */}
  <p className="mt-1 text-sm font-medium text-gray-600">
    Level {level} - {levelName}
  </p>

  {/* Points to level up (hidden at max level) */}
  {!isMaxLevel && (
    <p className="mt-1 text-xs text-gray-400">
      {pointsToNextLevel} points to level up
    </p>
  )}
</div>
```

**Design tokens used:**
- Card: `rounded-lg border border-gray-200 bg-white p-6`
- Avatar: `size="lg"` with `level` prop (uses existing Avatar component)
- Name: `text-lg font-bold text-gray-900 mt-3`
- Level label: `text-sm font-medium text-gray-600 mt-1`
- Points text: `text-xs text-gray-400 mt-1`
- Layout: `flex flex-col items-center` (centered column)

**Interactive states:**
- Static display (no hover or click)

**Existing pattern reference:** `ProfileLevelSection.tsx` — similar structure, adapted for centered card layout

---

### LeaderboardPanel *(New component)*

**Screenshot reference:** leaderboard-page-top.png — three panels in lower section

**Purpose:** White card containing the ranked list for one period (7-day, 30-day, all-time). Shows up to 10 member rows, then conditionally the "Your rank" section.

**Props:**
```ts
interface LeaderboardPanelProps {
  title: string;                    // "Leaderboard (7-day)"
  entries: LeaderboardEntry[];      // Top 10 ranked members
  yourRank: YourRankEntry | null;   // null if user is in top 10
  period: '7day' | '30day' | 'alltime';
  isLoading?: boolean;
}
```

**Structure:**
```tsx
<div className="rounded-lg border border-gray-200 bg-white">
  {/* Panel header */}
  <div className="border-b border-gray-100 px-4 py-3">
    <h3 className="text-sm font-semibold text-gray-700">{title}</h3>
  </div>

  {/* Loading state */}
  {isLoading && (
    <div className="divide-y divide-gray-50">
      {Array.from({ length: 5 }).map((_, i) => (
        <LeaderboardRowSkeleton key={i} />
      ))}
    </div>
  )}

  {/* Rank entries */}
  {!isLoading && entries.length > 0 && (
    <div className="divide-y divide-gray-50">
      {entries.map((entry) => (
        <LeaderboardRow
          key={entry.userId}
          entry={entry}
          period={period}
        />
      ))}
    </div>
  )}

  {/* Empty state */}
  {!isLoading && entries.length === 0 && (
    <div className="px-4 py-8 text-center">
      <p className="text-sm text-gray-400">
        No rankings yet — be the first to earn points!
      </p>
    </div>
  )}

  {/* Your rank section */}
  {!isLoading && yourRank !== null && (
    <YourRankSection entry={yourRank} period={period} />
  )}
</div>
```

**Design tokens used:**
- Card: `rounded-lg border border-gray-200 bg-white`
- Header: `border-b border-gray-100 px-4 py-3`
- Header text: `text-sm font-semibold text-gray-700`
- Row dividers: `divide-y divide-gray-50` (very subtle)
- Empty text: `text-sm text-gray-400`

---

### LeaderboardRow *(New component)*

**Screenshot reference:** leaderboard-page-top.png — individual rows within panels

**Purpose:** A single ranked entry showing rank/medal, avatar with level badge, member name, and points.

**Props:**
```ts
interface LeaderboardRowProps {
  entry: {
    rank: number;
    userId: string;
    displayName: string;
    avatarUrl: string | null;
    level: number;
    points: number;
  };
  period: '7day' | '30day' | 'alltime';
  highlight?: boolean;  // true for current user when in top 10
}
```

**Structure:**
```tsx
<div className={`flex items-center gap-3 px-4 py-2.5 ${highlight ? 'bg-blue-50' : 'hover:bg-gray-50'}`}>
  {/* Rank or medal */}
  <div className="flex w-6 shrink-0 items-center justify-center">
    {entry.rank <= 3 ? (
      <RankMedal rank={entry.rank} />
    ) : (
      <span className="text-sm font-medium text-gray-400">{entry.rank}</span>
    )}
  </div>

  {/* Avatar with level badge */}
  <Avatar
    src={entry.avatarUrl}
    alt={entry.displayName}
    size="sm"
    fallback={entry.displayName}
    level={entry.level}
  />

  {/* Name */}
  <span className="min-w-0 flex-1 truncate text-sm font-medium text-gray-900">
    {entry.displayName}
  </span>

  {/* Points */}
  <span className="shrink-0 text-sm font-semibold text-gray-700">
    {period !== 'alltime' ? `+${entry.points}` : entry.points}
  </span>
</div>
```

**Design tokens used:**
- Row: `flex items-center gap-3 px-4 py-2.5`
- Hover: `hover:bg-gray-50`
- Current user highlight: `bg-blue-50` (when `highlight=true`)
- Rank number area: `w-6 shrink-0` (fixed width for alignment)
- Rank number text (4-10): `text-sm font-medium text-gray-400`
- Avatar: `size="sm"` with `level` prop
- Name: `text-sm font-medium text-gray-900 flex-1 min-w-0 truncate`
- Points: `text-sm font-semibold text-gray-700 shrink-0`
- Points prefix: `+` prefix for 7-day and 30-day, no prefix for all-time

**Interactive states:**
- Default: white background
- Hover: `bg-gray-50` (subtle)
- Current user in top 10: `bg-blue-50` (highlighted but not interactive)

---

### RankMedal *(New component)*

**Screenshot reference:** leaderboard-page-top.png — gold/silver/bronze icons at ranks 1, 2, 3

**Purpose:** Render a gold, silver, or bronze medal icon for the top 3 ranked members.

**Structure:**
```tsx
const medalEmoji: Record<1 | 2 | 3, string> = {
  1: '🥇',
  2: '🥈',
  3: '🥉',
};

// Alternative: SVG/icon approach if emoji is not desired
// Gold: text-yellow-400, Silver: text-gray-400, Bronze: text-amber-700

export function RankMedal({ rank }: { rank: 1 | 2 | 3 }): JSX.Element {
  return (
    <span
      className="text-base leading-none"
      role="img"
      aria-label={rank === 1 ? 'Gold medal' : rank === 2 ? 'Silver medal' : 'Bronze medal'}
    >
      {medalEmoji[rank]}
    </span>
  );
}
```

**Design notes:**
- Uses emoji medals (🥇🥈🥉) — matches Skool's visual appearance closely
- Size: `text-base` (~16px) to align with the rank number area
- Container is `w-6` fixed-width to maintain row alignment whether showing medal or number
- `aria-label` provided for accessibility

---

### YourRankSection *(New component)*

**Screenshot reference:** leaderboard-page-bottom-your-rank.png — below the top 10 in 30-day and all-time panels

**Purpose:** Visually separated section below the top 10 showing the current member's own rank.

**Structure:**
```tsx
<div>
  {/* Separator */}
  <div className="flex items-center gap-2 px-4 py-2">
    <div className="h-px flex-1 bg-gray-200" />
    <span className="text-xs font-medium text-gray-400 uppercase tracking-wide">
      Your rank
    </span>
    <div className="h-px flex-1 bg-gray-200" />
  </div>

  {/* Your rank row — same format as LeaderboardRow */}
  <LeaderboardRow entry={entry} period={period} highlight={true} />
</div>
```

**Design tokens used:**
- Separator container: `flex items-center gap-2 px-4 py-2`
- Separator lines: `h-px flex-1 bg-gray-200`
- Label: `text-xs font-medium text-gray-400 uppercase tracking-wide`
- Row: Reuses `LeaderboardRow` with `highlight={true}` → `bg-blue-50`

**Notes:**
- The separator uses a centered label between two horizontal rules — cleaner than a plain `<hr>`
- "Your rank" label is uppercase+tracked to visually distinguish it from member names
- Row reuses `LeaderboardRow` for consistency; `highlight=true` applies `bg-blue-50`

---

### LeaderboardRowSkeleton *(New component)*

**Purpose:** Shimmer placeholder row while leaderboard data loads.

**Structure:**
```tsx
<div className="flex items-center gap-3 px-4 py-2.5">
  <div className="h-4 w-4 animate-pulse rounded-full bg-gray-200" />
  <div className="h-8 w-8 animate-pulse rounded-full bg-gray-200" />
  <div className="h-4 flex-1 animate-pulse rounded bg-gray-200" />
  <div className="h-4 w-8 animate-pulse rounded bg-gray-200" />
</div>
```

**Design tokens used:**
- Shimmer: `animate-pulse bg-gray-200`
- Rank placeholder: `h-4 w-4 rounded-full` (circle)
- Avatar placeholder: `h-8 w-8 rounded-full`
- Name placeholder: `h-4 flex-1 rounded` (full width bar)
- Points placeholder: `h-4 w-8 rounded` (short right bar)

---

### LeaderboardSidebarWidget *(New component)*

**Screenshot reference:** sidebar-leaderboard-widget.png — right sidebar of community feed page

**Purpose:** Compact 5-member 30-day leaderboard widget shown in the community feed right sidebar.

**Structure:**
```tsx
<div className="rounded-lg border border-gray-200 bg-white p-4">
  {/* Widget header */}
  <h3 className="mb-3 text-sm font-semibold text-gray-700">
    Leaderboard (30-day)
  </h3>

  {/* Loading state */}
  {isLoading && (
    <div className="space-y-1">
      {Array.from({ length: 5 }).map((_, i) => (
        <LeaderboardRowSkeleton key={i} />
      ))}
    </div>
  )}

  {/* Compact rank rows */}
  {!isLoading && entries.length > 0 && (
    <div className="divide-y divide-gray-50">
      {entries.map((entry) => (
        <div
          key={entry.userId}
          className="flex items-center gap-2 py-1.5"
        >
          {/* Rank or medal */}
          <div className="flex w-5 shrink-0 items-center justify-center">
            {entry.rank <= 3 ? (
              <RankMedal rank={entry.rank} />
            ) : (
              <span className="text-xs font-medium text-gray-400">{entry.rank}</span>
            )}
          </div>

          {/* Avatar with level badge */}
          <Avatar
            src={entry.avatarUrl}
            alt={entry.displayName}
            size="xs"
            fallback={entry.displayName}
            level={entry.level}
          />

          {/* Name */}
          <span className="min-w-0 flex-1 truncate text-xs font-medium text-gray-900">
            {entry.displayName}
          </span>

          {/* Points */}
          <span className="shrink-0 text-xs font-semibold text-gray-600">
            +{entry.points}
          </span>
        </div>
      ))}
    </div>
  )}

  {/* Empty: widget hidden silently — CommunitySidebar omits widget when entries=[] */}

  {/* See all link */}
  {!isLoading && entries.length > 0 && (
    <div className="mt-3 border-t border-gray-100 pt-3">
      <Link
        to="/leaderboards"
        className="text-xs font-medium text-blue-600 hover:text-blue-700 hover:underline"
      >
        See all leaderboards →
      </Link>
    </div>
  )}
</div>
```

**Design tokens used:**
- Card: `rounded-lg border border-gray-200 bg-white p-4`
- Header: `text-sm font-semibold text-gray-700 mb-3`
- Row padding: `py-1.5 gap-2` (tighter than full panel rows)
- Rank area: `w-5 shrink-0` (slightly narrower than full panel)
- Avatar: `size="xs"` with `level` prop
- Name: `text-xs font-medium text-gray-900 flex-1 min-w-0 truncate`
- Points: `text-xs font-semibold text-gray-600`
- Divider + link: `border-t border-gray-100 pt-3 mt-3`
- "See all" link: `text-xs font-medium text-blue-600 hover:text-blue-700 hover:underline`

**States:**
- Loading: 5 skeleton rows
- Empty: Widget not rendered (CommunitySidebar omits it — error should fail silently)
- Error: Widget not rendered — feed must not break on leaderboard API failure

**Integration point:** Add `<LeaderboardSidebarWidget />` inside `CommunitySidebar.tsx` after the community stats card div.

---

## CommunitySidebar Enhancement

**File:** `frontend/src/features/community/components/CommunitySidebar.tsx`

**Change:** Add `LeaderboardSidebarWidget` after the existing community stats card.

```tsx
// After the community stats card div:
<LeaderboardSidebarWidget />
```

The widget handles its own loading/error/empty states. `CommunitySidebar` itself needs no conditional logic — the widget renders nothing when data is unavailable.

---

## Color Palette Usage

| Element | Observed Color | Tailwind Class | Notes |
|---|---|---|---|
| Page background | `#F7F9FA` | `bg-page` / `bg-gray-50` | Existing |
| Card background | `#FFFFFF` | `bg-white` | Existing |
| Card border | `#E4E6EB` | `border-gray-200` | Existing |
| Panel header text | ~`#4B5563` | `text-gray-700` | Medium dark |
| Rank number (4-10) | ~`#9CA3AF` | `text-gray-400` | Muted |
| Member name | `#1D2129` | `text-gray-900` | Dark primary |
| Points value | ~`#374151` | `text-gray-700` | Semi-dark |
| Timestamp text | ~`#6B7280` | `text-gray-500` | Muted |
| Row divider | ~`#F9FAFB` | `divide-gray-50` | Very subtle |
| Current user row | Light blue | `bg-blue-50` | Consistent with LevelDefinitionsGrid |
| "Your rank" separator | `#E5E7EB` | `bg-gray-200` | Soft separator line |
| "See all" link | Blue | `text-blue-600` | Consistent with existing links |
| Level badge | Blue | `bg-blue-600` | Existing LevelBadge |
| Gold medal | emoji 🥇 | — | Native emoji |
| Silver medal | emoji 🥈 | — | Native emoji |
| Bronze medal | emoji 🥉 | — | Native emoji |

---

## Typography Scale

| Element | Tailwind Class | Weight | Notes |
|---|---|---|---|
| Panel header "Leaderboard (30-day)" | `text-sm font-semibold` | 600 | ~14px |
| Member name (full panel) | `text-sm font-medium` | 500 | ~14px |
| Points value (full panel) | `text-sm font-semibold` | 600 | ~14px |
| Rank number (4-10) | `text-sm font-medium` | 500 | `text-gray-400` |
| "Your rank" label | `text-xs uppercase tracking-wide font-medium` | 500 | ~12px |
| Profile card name | `text-lg font-bold` | 700 | ~18px |
| Profile card level text | `text-sm font-medium` | 500 | ~14px |
| Profile card points text | `text-xs` | 400 | ~12px |
| Timestamp | `text-sm` | 400 | ~14px |
| Widget header | `text-sm font-semibold` | 600 | Same as panel header |
| Widget member name | `text-xs font-medium` | 500 | ~12px (compact) |
| Widget points | `text-xs font-semibold` | 600 | ~12px (compact) |
| "See all leaderboards" | `text-xs font-medium` | 500 | ~12px |

---

## Spacing System

| Context | Tailwind Class | Value | Notes |
|---|---|---|---|
| Full panel row padding | `px-4 py-2.5` | 16px / 10px | Comfortable row height |
| Widget row padding | `py-1.5` (no px — parent has `px-4`) | 6px | Compact |
| Panel rank column width | `w-6` | 24px | Fixed, holds number or medal |
| Widget rank column width | `w-5` | 20px | Slightly narrower |
| Row internal gap (full) | `gap-3` | 12px | Between rank, avatar, name, points |
| Row internal gap (widget) | `gap-2` | 8px | Compact |
| Panel header padding | `px-4 py-3` | 16px / 12px | Standard card header |
| Card to panel grid gap | `gap-4` | 16px | Between 3 panels |
| Top section to panels gap | `mt-6` | 24px | Breathing room |
| Timestamp to panels gap | `mt-6` | 24px | After timestamp |
| Widget "see all" separator | `mt-3 pt-3` | 12px | Border-top + spacing |

---

## Interactive Patterns

### Rank Row Hover
**Where:** All rows in LeaderboardPanel
**Behavior:** Light gray background on hover — confirms rows are scannable
**Implementation:**
- Default: `bg-white` (from parent card)
- Hover: `hover:bg-gray-50`
- Current user highlight: `bg-blue-50` (overrides hover)

### "See all leaderboards" Link
**Where:** Bottom of LeaderboardSidebarWidget
**Behavior:** Navigates to `/leaderboards`
**Implementation:**
- Default: `text-blue-600`
- Hover: `text-blue-700 underline`
- Uses React Router `<Link to="/leaderboards">`

### Loading Skeletons
**Where:** All panels and the sidebar widget
**Behavior:** Shimmer animation while data fetches
**Implementation:**
- `animate-pulse bg-gray-200` on placeholder elements
- 5 skeleton rows shown for sidebar widget (matches real row count)
- 5 rows shown during panel loading (full 10 would be too long)

### Error States
**Panels:** Show `"Failed to load leaderboard. Please try again."` inside the panel card
**Widget:** Widget is not rendered at all (no error message in sidebar — non-critical)

---

## File Structure

```
frontend/src/features/gamification/
├── components/
│   ├── LeaderboardPanel.tsx        # New — card with rows + your rank
│   ├── LeaderboardPanel.test.tsx   # New
│   ├── LeaderboardRow.tsx          # New — single rank row
│   ├── LeaderboardRow.test.tsx     # New
│   ├── LeaderboardRowSkeleton.tsx  # New — shimmer placeholder row
│   ├── RankMedal.tsx               # New — gold/silver/bronze medal
│   ├── RankMedal.test.tsx          # New
│   ├── YourRankSection.tsx         # New — separator + rank row
│   ├── YourRankSection.test.tsx    # New
│   ├── LeaderboardSidebarWidget.tsx        # New — compact 5-row widget
│   ├── LeaderboardSidebarWidget.test.tsx   # New
│   ├── LeaderboardProfileCard.tsx          # New — profile card for page top
│   ├── LeaderboardProfileCard.test.tsx     # New
│   ├── LevelBadge.tsx              # Existing
│   ├── LevelDefinitionsGrid.tsx    # Existing
│   └── ...
└── hooks/
    ├── useLeaderboards.ts          # New — fetch all three periods
    ├── useLeaderboardWidget.ts     # New — fetch 30-day top 5
    └── useLevelDefinitions.ts      # Existing

frontend/src/pages/
└── LeaderboardsPage.tsx            # Existing — enhance with full layout

frontend/src/features/community/components/
└── CommunitySidebar.tsx            # Existing — add LeaderboardSidebarWidget
```

---

## Implementation Checklist

- [ ] Load `ui-design` skill before coding
- [ ] **New components to create:**
  - [ ] `RankMedal.tsx` — emoji medal for ranks 1/2/3
  - [ ] `LeaderboardRowSkeleton.tsx` — shimmer placeholder
  - [ ] `LeaderboardRow.tsx` — single ranked member row
  - [ ] `YourRankSection.tsx` — separator + highlighted row
  - [ ] `LeaderboardPanel.tsx` — full ranking card
  - [ ] `LeaderboardProfileCard.tsx` — current user profile card
  - [ ] `LeaderboardSidebarWidget.tsx` — compact 5-member widget
- [ ] **Existing components to enhance:**
  - [ ] `LeaderboardsPage.tsx` — full layout with profile card + timestamp + 3 panels
  - [ ] `CommunitySidebar.tsx` — add `LeaderboardSidebarWidget`
- [ ] **Hooks to create:**
  - [ ] `useLeaderboards.ts` — fetches all three leaderboard periods
  - [ ] `useLeaderboardWidget.ts` — fetches 30-day top 5 for sidebar
- [ ] Use `Avatar` component with `level` prop on all member rows
- [ ] Use `LevelDefinitionsGrid` (existing) in `LeaderboardProfileCard` parent page
- [ ] Use semantic HTML (`<section>` for leaderboard panels, `<h3>` for panel headers)
- [ ] Test responsive layout (3 columns → 1 column on mobile)
- [ ] Verify 4-digit rank numbers don't overflow row layout
- [ ] Verify name truncation with `truncate` on long display names
- [ ] Add `aria-label` to medal emojis for screen readers
- [ ] Widget fails silently — never disrupts community feed rendering

---

## Edge Cases

### Very Long Rank Number (1000+)
- `rank` column is `w-6` (24px) — rank 1247 is 4 chars which fits at `text-sm`
- If overflow occurs, use `text-xs` for rank numbers > 99 as a conditional

### Very Long Member Names
- Name column has `flex-1 min-w-0 truncate` — truncates to single line with ellipsis
- Points column has `shrink-0` — never compressed, always fully visible

### 0 Points in Period
- Display `+0` for period boards — consistent with `+` prefix rule
- Member still appears in "Your rank" row (per PRD §3.4)

### All Members in Top 10 (<10 members)
- "Your rank" section does not render (user IS in the top 10 list)
- `YourRankSection` receives `null` and is conditionally skipped in `LeaderboardPanel`

### Medal for Rank 1-3
- `RankMedal` renders emoji `🥇 🥈 🥉`
- If emoji support is a concern, an SVG/icon approach using `text-yellow-400`, `text-gray-400`, `text-amber-700` can replace emoji with a trophy icon

### Widget Empty/Error
- `CommunitySidebar` renders `LeaderboardSidebarWidget` unconditionally
- Widget internally manages its loading/error/empty states
- On error or empty data: widget renders `null` (no visible content, no layout disruption)

---

## Notes for Implementation

### API Shape
Each leaderboard entry returned by the API should include:
```ts
interface LeaderboardEntry {
  rank: number;
  userId: string;
  displayName: string;
  avatarUrl: string | null;
  level: number;
  points: number;    // net points for period, or total for all-time
}

interface YourRankEntry extends LeaderboardEntry {}

interface LeaderboardsResponse {
  sevenDay: { entries: LeaderboardEntry[]; yourRank: YourRankEntry | null };
  thirtyDay: { entries: LeaderboardEntry[]; yourRank: YourRankEntry | null };
  allTime: { entries: LeaderboardEntry[]; yourRank: YourRankEntry | null };
  lastUpdated: string;  // ISO 8601 timestamp
}
```

### Points Formatting
- 7-day and 30-day panels: prefix with `+` (e.g., `+7`, `+0`)
- All-time panel: no prefix (e.g., `942`)
- Format is determined by the `period` prop passed to `LeaderboardRow`

### "Last Updated" Timestamp Formatting
- Backend returns ISO timestamp; frontend formats as `"Feb 15th 2026 2:11pm"` using a date formatter
- Use `date-fns` (already likely available) or `Intl.DateTimeFormat`

### Medal Implementation Decision
- **Recommended:** Use emoji (`🥇 🥈 🥉`) — faithful to Skool's appearance, no extra dependencies
- **Alternative:** Use Lucide `Trophy` icon with color classes (`text-yellow-400` / `text-gray-400` / `text-amber-700`) if emoji consistency across platforms is a concern

### Hook Architecture
- `useLeaderboards()` should fetch all three periods in a single API call (not three separate calls)
- `useLeaderboardWidget()` fetches only the 30-day top 5 — separate endpoint or derived from the same leaderboards call

---

## Approval

**Product Owner:** _________________
**Engineering Lead:** _________________
**Design Lead:** _________________

**Status:** Draft — Ready for Technical Design
