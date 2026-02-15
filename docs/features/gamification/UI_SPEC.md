# Points & Levels - UI Specification

*Generated from Skool.com screenshots on February 15, 2026*

## Visual References

- **Screenshot 1 (14-22-02.png):** Leaderboards page showing level definitions grid and profile with level badge
- **Screenshot 2 (14-22-24.png):** Community feed showing level badges on avatars and leaderboard sidebar widget
- **Screenshot 3 (14-23-29.png):** Member profile page with level badge, level name, and "points to level up" display
- **Screenshot 4 & 5 (14-24-39, Classroom Brave_001.png):** Classroom showing locked courses with level requirements

---

## Layout Structure

### Desktop (>768px)

The points & levels feature integrates into existing layouts without requiring new page structures:

- **Leaderboards Page:** 2-column layout with left sidebar (profile + level) and main content (level definitions grid + leaderboard tables)
- **Profile Page:** Right sidebar displays level information alongside avatar
- **Community Feed:** Level badges appear on all avatars; leaderboard widget in right sidebar
- **Classroom:** Lock overlays appear on course cards in the existing grid layout

### Mobile (<768px)

- Level badges remain visible on all avatars (scaled appropriately)
- Level definitions grid stacks vertically
- Profile level section remains in sidebar (scrollable)

---

## Component Specifications

### LevelBadge *(Enhances existing Avatar component)*

**Screenshot reference:** All screenshots - appears on every avatar

**Purpose:** Display member's level as a numbered badge overlaying the bottom-right corner of their avatar

**Structure:**
```tsx
<div className="relative inline-block">
  <Avatar {...avatarProps} />
  <div className="absolute -bottom-0.5 -right-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-blue-600 border-2 border-white text-white text-xs font-semibold">
    {level}
  </div>
</div>
```

**Design tokens used:**
- Badge background: `bg-blue-600` (Skool uses blue for level badges)
- Badge border: `border-2 border-white` (creates separation from avatar)
- Badge size: `h-5 w-5` for md avatars (scale proportionally for xs/sm/lg)
- Text: `text-white text-xs font-semibold`
- Position: `absolute -bottom-0.5 -right-0.5`

**Responsive sizing by avatar size:**
| Avatar Size | Badge Size | Text Size | Position |
|-------------|-----------|-----------|----------|
| xs (h-6 w-6) | h-4 w-4 | text-[10px] | -bottom-0.5 -right-0.5 |
| sm (h-8 w-8) | h-4 w-4 | text-[10px] | -bottom-0.5 -right-0.5 |
| md (h-10 w-10) | h-5 w-5 | text-xs | -bottom-0.5 -right-0.5 |
| lg (h-12 w-12) | h-6 w-6 | text-sm | -bottom-1 -right-1 |

**Interactive states:**
- Static display (no hover or interaction)
- Always visible (no conditional rendering — all members have Level 1 minimum)

**Existing pattern reference:** Enhance `frontend/src/components/Avatar.tsx` - wrap in container div with relative positioning and add badge overlay

**Implementation notes:**
- Add optional `level?: number` prop to Avatar component
- Default to not showing badge if level is undefined (maintains backward compatibility)
- Badge should be a separate internal component for cleanliness

---

### LevelDefinitionsGrid *(New component)*

**Screenshot reference:** Screenshot 1 (14-22-02.png) - top section of Leaderboards page

**Purpose:** Display all 9 levels with names, point thresholds, and member distribution percentages

**Structure:**
```tsx
<section className="rounded-lg bg-white p-6 shadow">
  <h2 className="text-lg font-semibold text-gray-900 mb-4">Levels</h2>

  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
    {levels.map((level) => (
      <div
        key={level.number}
        className={`flex items-center gap-3 p-3 rounded-lg border ${
          level.number === currentLevel
            ? 'bg-blue-50 border-blue-200'
            : 'bg-gray-50 border-gray-200'
        }`}
      >
        {/* Level badge icon */}
        <div className="flex-shrink-0">
          {level.number <= currentLevel ? (
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 text-white font-semibold">
              {level.number}
            </div>
          ) : (
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-300 text-gray-500 font-semibold relative">
              <LockIcon className="h-5 w-5" />
            </div>
          )}
        </div>

        {/* Level info */}
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-gray-900 text-sm">
            Level {level.number} - {level.name}
          </p>
          <p className="text-xs text-gray-500 mt-0.5">
            {level.memberPercentage}% of members
          </p>
        </div>
      </div>
    ))}
  </div>
</section>
```

**Design tokens used:**
- Container: `rounded-lg bg-white p-6 shadow`
- Grid: `grid-cols-1 md:grid-cols-3 gap-4` (3 columns on desktop, stacked on mobile)
- Card for current level: `bg-blue-50 border-blue-200`
- Card for other levels: `bg-gray-50 border-gray-200`
- Unlocked badge: `bg-blue-600 text-white` (same as level badge)
- Locked badge: `bg-gray-300 text-gray-500` with lock icon overlay
- Spacing: `p-3 gap-3` within each level card

**Interactive states:**
- Current level highlighted with `bg-blue-50 border-blue-200`
- Unlocked levels (1 to current): Show numbered badge
- Locked levels (above current): Show lock icon overlay on grayed badge
- No click interaction (informational only)

**Empty state:**
- N/A - always shows all 9 levels

**Existing pattern reference:** Similar to member cards in members directory - grid layout with cards

---

### ProfileLevelSection *(Enhances ProfileSidebar)*

**Screenshot reference:** Screenshot 1 & 3 (14-22-02.png, 14-23-29.png) - profile sidebar

**Purpose:** Display member's level, level name, and points-to-level-up on their profile

**Structure (viewing own profile):**
```tsx
<aside className="rounded-lg bg-white p-6 shadow">
  {/* Avatar with level badge */}
  <div className="flex flex-col items-center">
    <div className="relative inline-block">
      <img
        src={avatarUrl}
        className="h-24 w-24 rounded-full object-cover"
      />
      <div className="absolute -bottom-1 -right-1 flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 border-2 border-white text-white text-sm font-semibold">
        {level}
      </div>
    </div>

    {/* Level name */}
    <p className="mt-3 text-sm font-medium text-gray-700">
      Level {level} - {levelName}
    </p>

    {/* Points to level up (only if not max level) */}
    {!isMaxLevel && (
      <div className="mt-2 flex items-center gap-1.5 text-xs text-gray-500">
        <ClockIcon className="h-4 w-4" />
        <span>{pointsToNextLevel} points to level up</span>
      </div>
    )}

    {/* Display name */}
    <h1 className="mt-4 text-xl font-bold text-gray-900">
      {displayName}
    </h1>

    {/* Bio, location, etc. - existing content */}
  </div>
</aside>
```

**Structure (viewing another member's profile):**
- Same as above but WITHOUT "points to level up" section
- Level badge and level name remain visible

**Design tokens used:**
- Large avatar badge: `h-8 w-8` with `text-sm`
- Level text: `text-sm font-medium text-gray-700`
- Points text: `text-xs text-gray-500`
- Clock icon: `h-4 w-4` (from heroicons or lucide)
- Spacing: `mt-3` after avatar, `mt-2` after level name

**Interactive states:**
- Static display (no interaction)
- Max level (Level 9): Omit "points to level up" section entirely

**Empty state:**
- N/A - all members have a level (minimum Level 1)

**Existing pattern reference:** Enhance `frontend/src/features/identity/components/ProfileSidebar.tsx` - add level section after avatar and before display name

---

### CourseCardLock *(Enhances CourseCard)*

**Screenshot reference:** Screenshot 4 & 5 (14-24-39.png, Classroom Brave_001.png) - locked courses

**Purpose:** Display lock overlay on courses that require a higher level than the member currently has

**Structure:**
```tsx
<div className="cursor-pointer rounded-lg bg-white p-6 shadow hover:shadow-md transition-shadow relative">
  {/* Existing course card content (dimmed if locked) */}
  <div className={isLocked ? 'opacity-60' : ''}>
    {coverImage && <img src={coverImage} className="..." />}
    <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
    <p className="mt-2 text-sm text-gray-600">{description}</p>
  </div>

  {/* Lock overlay (only if locked) */}
  {isLocked && (
    <div className="absolute inset-0 flex flex-col items-center justify-center bg-white/80 rounded-lg">
      <LockIcon className="h-12 w-12 text-gray-400 mb-2" />
      <p className="text-sm font-semibold text-gray-700">
        Unlock at Level {requiredLevel}
      </p>
      <p className="text-xs text-gray-500 mt-1">
        {requiredLevelName}
      </p>
    </div>
  )}
</div>
```

**Design tokens used:**
- Lock overlay: `absolute inset-0 bg-white/80` (80% opacity white)
- Lock icon: `h-12 w-12 text-gray-400` (large, muted)
- Text: `text-sm font-semibold text-gray-700` for main message
- Level name: `text-xs text-gray-500` for subtitle
- Dimmed content: `opacity-60` on card content when locked

**Interactive states:**
- **Unlocked:** Normal course card behavior (no lock overlay)
- **Locked:** Dimmed content with lock overlay
  - Hover: Lock overlay remains (prevents click-through)
  - Click: Show modal/toast explaining level requirement (optional - could also just prevent navigation)

**Empty state:**
- N/A - lock appears conditionally based on member level vs. course requirement

**Existing pattern reference:** Enhance `frontend/src/features/classroom/components/CourseCard.tsx` - add conditional lock overlay

**Implementation notes:**
- Add `requiredLevel?: number` and `requiredLevelName?: string` to course data
- Compare against current user's level to determine `isLocked` state
- Prevent course start/continue actions when locked

---

## Color Palette Usage

From screenshots observed:

| Element | Skool Color | Tailwind Class | Usage |
|---------|-------------|----------------|-------|
| Level badge background | Blue (#0D6EFD approx) | `bg-blue-600` | Badge on avatar |
| Level badge text | White | `text-white` | Number on badge |
| Current level highlight | Light blue | `bg-blue-50 border-blue-200` | Level definitions grid |
| Locked badge | Gray | `bg-gray-300 text-gray-500` | Level definitions grid (locked) |
| Lock overlay background | White 80% opacity | `bg-white/80` | Course cards |
| Lock icon | Gray | `text-gray-400` | Course lock overlay |
| Level text | Dark gray | `text-gray-700` | Profile sidebar |
| Points text | Medium gray | `text-gray-500` | Profile sidebar |

**Note:** Skool uses a consistent blue color (`#0D6EFD`) for level badges. Koulu should use `bg-blue-600` from Tailwind's default palette, which is close enough.

---

## Typography Scale

| Element | Size | Weight | Tailwind Class |
|---------|------|--------|----------------|
| Level badge number (md avatar) | ~12px | Semibold | `text-xs font-semibold` |
| Level badge number (lg avatar) | ~14px | Semibold | `text-sm font-semibold` |
| "Level X - Name" (profile) | ~14px | Medium | `text-sm font-medium` |
| "X points to level up" | ~12px | Regular | `text-xs` |
| Level definition card title | ~14px | Semibold | `text-sm font-semibold` |
| "Unlock at Level X" | ~14px | Semibold | `text-sm font-semibold` |
| Level name subtitle (lock) | ~12px | Regular | `text-xs` |

---

## Spacing System

| Element | Spacing | Tailwind Class | Description |
|---------|---------|----------------|-------------|
| Badge position offset (md) | -2px | `-bottom-0.5 -right-0.5` | Overlaps avatar edge |
| Badge border width | 2px | `border-2` | White border separates from avatar |
| Level text spacing (profile) | 12px | `mt-3` | After avatar |
| Points text spacing | 8px | `mt-2` | After level name |
| Icon-to-text gap | 6px | `gap-1.5` | Clock icon + points text |
| Level grid gap | 16px | `gap-4` | Between level cards |
| Card padding | 12px | `p-3` | Inside level cards |

---

## Interactive Patterns

### Level Badge on Avatar
**Where:** Everywhere avatars appear (feed, comments, profile, members, leaderboard)
**Behavior:** Static display - no interaction
**Implementation:**
- Default state: Blue badge with white number
- No hover effect needed
- Always visible (Level 1 minimum for all members)

---

### Level Definitions Grid
**Where:** Leaderboards page (top section)
**Behavior:** Informational display - no click actions
**Implementation:**
- Default state: Gray cards with lock icon for locked levels, blue badge for unlocked
- Current level: Highlighted with `bg-blue-50 border-blue-200`
- No hover effects (informational only)

---

### Profile Level Section
**Where:** Profile page sidebar
**Behavior:** Static display
**Implementation:**
- Default state: Level badge on avatar + level name + points to level up (own profile)
- Viewing others: Level badge + level name only (no points to level up)
- Max level (9): No points message

---

### Course Card Lock Overlay
**Where:** Classroom course grid
**Behavior:** Prevents access to locked courses
**Implementation:**
- Default state (unlocked): Normal course card
- Locked state: Dimmed card with lock overlay (`bg-white/80`)
- Hover on locked card: No change to lock overlay (prevents click-through)
- Click on locked card: Optional - show toast/modal explaining requirement (or just prevent navigation)
- Focus: Standard focus ring on card (accessibility)

---

## Implementation Checklist

- [ ] Load `ui-design` skill before coding
- [ ] **Enhance existing components:**
  - [ ] `Avatar.tsx` - Add optional level badge overlay
  - [ ] `ProfileSidebar.tsx` - Add level section below avatar
  - [ ] `CourseCard.tsx` - Add lock overlay for level-gated courses
- [ ] **Create new components:**
  - [ ] `LevelDefinitionsGrid.tsx` - For leaderboards page
  - [ ] `LevelBadge.tsx` - Internal component for badge rendering (reusable)
- [ ] Use semantic HTML (`<aside>` for profile sidebar, `<section>` for level grid)
- [ ] Test responsive breakpoints (badge sizing scales with avatar)
- [ ] Verify color contrast (WCAG AA compliance)
- [ ] Add focus states for accessibility on interactive elements

---

## Component Dependencies

```
LevelBadge (internal utility component)
  ↓
Avatar (enhanced with level prop)
  ↓ used by
  ├─ FeedPostCard
  ├─ CommentCard
  ├─ MemberCard
  ├─ ProfileSidebar (enhanced with level section)
  └─ LeaderboardWidget (future)

LevelDefinitionsGrid (new)
  → Leaderboards page (future)

CourseCard (enhanced with lock overlay)
  → Classroom page (existing)
```

---

## Notes for Implementation

### Avatar Enhancement Strategy
The cleanest approach is to:
1. Create an internal `LevelBadge` component that renders the badge
2. Update `Avatar` component to accept optional `level?: number` prop
3. When `level` is provided, wrap avatar in `relative` container and render badge overlay
4. This maintains backward compatibility (existing Avatar usage without level prop works unchanged)

### Profile Sidebar Enhancement
- Insert level section between avatar and display name
- Conditionally render "points to level up" only for own profile AND not max level
- Use existing `profile.is_own_profile` pattern from ProfileSidebar
- Level data should come from a new API endpoint or be added to profile response

### Course Card Lock Logic
- Add `required_level?: number` to Course type
- Add `current_user_level: number` from auth context or user state
- Calculate `isLocked = requiredLevel > currentUserLevel`
- When locked: dim content, show overlay, prevent navigation

### Color Consistency
- Use `bg-blue-600` for level badges (matches Tailwind's default blue-600)
- Do NOT use custom hex colors - stick to Tailwind palette
- If exact Skool blue is critical, add to `tailwind.config.ts`:
  ```ts
  colors: {
    'level-badge': '#0D6EFD', // Skool's exact blue
  }
  ```

### Icon Library
- Use existing icon library (likely Heroicons or Lucide)
- Lock icon: `LockClosedIcon` (Heroicons) or `Lock` (Lucide)
- Clock icon: `ClockIcon` (Heroicons) or `Clock` (Lucide)

### Accessibility
- Level badge has no semantic meaning for screen readers (decorative)
  - Add `aria-hidden="true"` to badge element
  - Include level in avatar's alt text: e.g., `alt="John Doe, Level 3"`
- Lock overlay should have proper ARIA labels:
  - `aria-label="Locked - Requires Level {X}"`
  - Prevent keyboard focus on locked course cards (or trap focus and announce requirement)

### Performance
- Level badges are small and render frequently (every avatar) - ensure minimal re-renders
- Memoize LevelBadge component if necessary
- Level data should be cached (part of user session state, not fetched per-component)

---

## Edge Cases

### No Level Data Available
- **Scenario:** API hasn't returned level data yet (loading state)
- **Behavior:** Render avatar without badge (graceful degradation)
- **Implementation:** Only render badge if `level !== undefined`

### Level 9 (Max Level)
- **Scenario:** Member has reached the maximum level
- **Behavior:** Badge shows "9", but no "points to level up" message on profile
- **Implementation:** Conditional render based on `level === 9` or `isMaxLevel` flag

### New Member (Level 1, 0 Points)
- **Scenario:** Brand new member with 0 points
- **Behavior:** Badge shows "1", profile shows "0 points to level up" (or "10 points to level up" with default thresholds)
- **Implementation:** Normal rendering - Level 1 is the starting level

### Admin Customizes Level Names
- **Scenario:** Admin changes "Student" to "Newbie"
- **Behavior:** UI reflects new name immediately
- **Implementation:** Level names come from API response, not hardcoded

### Admin Changes Thresholds (Member Levels Up/Down)
- **Scenario:** Admin lowers Level 3 threshold, member now qualifies
- **Behavior:** Badge updates to "3" immediately (real-time via WebSocket or on next page load)
- **Implementation:** Level recalculation happens backend, frontend re-fetches user level

### Course Locked by Level
- **Scenario:** Member tries to access locked course
- **Behavior:** Click on locked course does NOT navigate - instead shows requirement
- **Implementation:**
  - Prevent `navigate()` call when `isLocked === true`
  - Show toast: "This course requires Level {X} - {LevelName}"
  - OR: Show modal with progress bar toward required level

---

## Future Enhancements (Out of Scope for MVP)

- **Level-up celebration animation:** Confetti effect when member crosses level threshold
- **Real-time point notifications:** Toast "+1 point" when receiving a like
- **Level progress bar:** Visual indicator on profile showing progress toward next level
- **Leaderboard integration:** Sidebar widget showing top members (separate feature)
- **Level badge customization:** Allow admins to choose badge color per level
- **Hover tooltip on badge:** Show level name on hover
- **Animated level transitions:** Smooth badge number change when leveling up

---

## Approval

**Product Owner:** _________________
**Engineering Lead:** _________________
**Design Lead:** _________________

**Status:** Draft — Ready for Implementation
