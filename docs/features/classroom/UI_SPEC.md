# Classroom - UI Specification

*Generated from Skool.com screenshots on 2026-02-07*

## Visual References

- **Screenshot 1 (classroom_list.png)**: Course grid view showing 6 courses in 3-column layout with progress indicators
- **Screenshot 2 (classroom_module_view.png)**: Course detail view with left sidebar (lesson list) and main content area (video player + summary)
- **Screenshot 3 (classroon_bottom_view.png)**: Course grid with pagination controls at bottom

---

## Overview

The Classroom feature follows Skool.com's clean, card-based design with three main views:

1. **Course List** - Grid of course cards with progress tracking
2. **Course Overview** - Module accordion with lesson navigation
3. **Lesson View** - Two-column layout with sidebar navigation and content area

**Design Principles:**
- Clean, minimal interface with high whitespace
- Card-based content blocks on gray background
- Progress visualization through bars and checkmarks
- Clear visual hierarchy with typography and spacing

---

## Layout Structure

### Desktop (>768px)

```
┌──────────────────────────────────────────────────────────┐
│                    Header (60px)                          │
│  Logo  |  Search  |  Community  Classroom*  Calendar...   │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐            │
│  │  Course   │  │  Course   │  │  Course   │            │
│  │   Card    │  │   Card    │  │   Card    │            │
│  └───────────┘  └───────────┘  └───────────┘            │
│                                                            │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐            │
│  │  Course   │  │  Course   │  │  Course   │            │
│  └───────────┘  └───────────┘  └───────────┘            │
│                                                            │
│              [Previous] 1 [Next]  1-14 of 14              │
└──────────────────────────────────────────────────────────┘
```

**Container:**
- Max width: `1100px`
- Margin: `0 auto`
- Padding: `24px 16px`

**Grid:**
- Desktop (≥1024px): 3 columns
- Tablet (768-1023px): 2 columns
- Mobile (<768px): 1 column
- Gap: `24px` (grid-gap-6)

### Mobile (<768px)

- Single column stacked layout
- Cards full width with 16px horizontal padding
- Sidebar converts to collapsible drawer or separate page

---

## Component Specifications

### 1. CourseCard (Grid View)

**Screenshot reference:** classroom_list.png, classroon_bottom_view.png

**Purpose:** Display course summary with visual preview and progress tracking

**Structure:**
```tsx
<article className="group relative flex flex-col overflow-hidden rounded-lg bg-white shadow-md transition-shadow hover:shadow-lg">
  {/* Cover Image */}
  <div className="relative aspect-video w-full overflow-hidden">
    <img
      src={coverImageUrl}
      alt={courseTitle}
      className="h-full w-full object-cover"
    />
    {isPrivate && (
      <div className="absolute right-2 top-2 rounded bg-black/60 px-2 py-1">
        <LockIcon className="h-4 w-4 text-white" />
      </div>
    )}
  </div>

  {/* Content */}
  <div className="flex flex-1 flex-col p-4">
    {/* Title */}
    <h3 className="mb-2 text-lg font-semibold text-gray-900 line-clamp-2">
      {courseTitle}
    </h3>

    {/* Description */}
    <p className="mb-4 flex-1 text-sm text-gray-600 line-clamp-3">
      {description}
    </p>

    {/* Progress Bar */}
    {progress !== null && (
      <div className="mb-2">
        <div className="mb-1 flex items-center justify-between text-xs">
          <span className="text-gray-500">Progress</span>
          <span className="font-medium text-gray-700">{progress}%</span>
        </div>
        <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200">
          <div
            className="h-full rounded-full bg-green-500 transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    )}
  </div>
</article>
```

**Design tokens used:**
- Card background: `bg-white`
- Border radius: `rounded-lg` (8px)
- Shadow: `shadow-md` (default), `shadow-lg` (hover)
- Text colors: `text-gray-900` (title), `text-gray-600` (description)
- Progress bar: `bg-green-500` (filled), `bg-gray-200` (track)
- Spacing: `p-4` (card padding), `mb-2`, `mb-4` (vertical spacing)

**Interactive states:**
- **Hover:** Shadow increases from `md` to `lg`, subtle scale transform optional
- **Active:** Click navigates to course overview page
- **Focus:** Ring outline for keyboard navigation

**Responsive behavior:**
- Cover image: Fixed 16:9 aspect ratio (`aspect-video`)
- Title: Clamp to 2 lines with ellipsis (`line-clamp-2`)
- Description: Clamp to 3 lines with ellipsis (`line-clamp-3`)

**Empty state:** Shows placeholder image gradient if no cover image provided

**Existing pattern reference:** Similar to `ProfileSidebar` card pattern (`rounded-lg bg-white p-6 shadow`)

---

### 2. CourseGrid

**Screenshot reference:** classroom_list.png, classroon_bottom_view.png

**Purpose:** Container for course cards with responsive grid layout

**Structure:**
```tsx
<div className="mx-auto max-w-7xl px-4 py-6">
  {/* Grid */}
  <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
    {courses.map(course => (
      <CourseCard key={course.id} course={course} />
    ))}
  </div>

  {/* Pagination */}
  {totalPages > 1 && (
    <div className="mt-8 flex items-center justify-center gap-4 text-sm">
      <button
        disabled={currentPage === 1}
        className="rounded-md px-3 py-2 text-gray-700 hover:bg-gray-100 disabled:text-gray-400 disabled:hover:bg-transparent"
      >
        Previous
      </button>
      <span className="font-medium text-gray-900">{currentPage}</span>
      <button
        disabled={currentPage === totalPages}
        className="rounded-md px-3 py-2 text-gray-700 hover:bg-gray-100 disabled:text-gray-400 disabled:hover:bg-transparent"
      >
        Next
      </button>
      <span className="text-gray-500">
        {startIndex}-{endIndex} of {totalCount}
      </span>
    </div>
  )}
</div>
```

**Design tokens:**
- Container: `max-w-7xl mx-auto px-4 py-6`
- Grid: `grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6`
- Pagination text: `text-sm text-gray-700`

**Empty state:**
```tsx
<div className="flex flex-col items-center justify-center py-16 text-center">
  <div className="mb-4 text-6xl">📚</div>
  <h3 className="mb-2 text-xl font-semibold text-gray-900">
    No courses available yet
  </h3>
  <p className="text-gray-600">
    {isAdmin ? "Create your first course to get started" : "Check back soon for new content"}
  </p>
  {isAdmin && (
    <button className="mt-4 rounded-md bg-primary-500 px-4 py-2 text-white hover:bg-primary-600">
      Create Course
    </button>
  )}
</div>
```

**Loading state:** Skeleton cards (3 visible on desktop)

---

### 3. LessonSidebar

**Screenshot reference:** classroom_module_view.png

**Purpose:** Navigation sidebar showing course structure and progress

**Structure:**
```tsx
<aside className="w-80 flex-shrink-0 border-r border-gray-200 bg-white">
  <div className="h-full overflow-y-auto p-6">
    {/* Course Header */}
    <div className="mb-6">
      <h2 className="mb-3 text-xl font-bold text-gray-900">
        {courseTitle}
      </h2>

      {/* Progress Bar */}
      <div className="mb-2">
        <div className="mb-1 flex items-center justify-between text-sm">
          <span className="text-gray-600">Course Progress</span>
          <span className="font-semibold text-gray-900">{progress}%</span>
        </div>
        <div className="h-2.5 w-full overflow-hidden rounded-full bg-gray-200">
          <div
            className="h-full rounded-full bg-green-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </div>

    {/* Lesson List */}
    <nav className="space-y-1">
      {lessons.map((lesson) => (
        <button
          key={lesson.id}
          onClick={() => navigateToLesson(lesson.id)}
          className={cn(
            "flex w-full items-start gap-3 rounded-md p-3 text-left text-sm transition-colors",
            lesson.isActive
              ? "bg-yellow-50 text-gray-900"
              : "text-gray-700 hover:bg-gray-50"
          )}
        >
          {/* Completion Checkmark */}
          <div className="mt-0.5 flex-shrink-0">
            {lesson.isComplete ? (
              <CheckCircleIcon className="h-5 w-5 text-green-500" />
            ) : (
              <div className="h-5 w-5 rounded-full border-2 border-gray-300" />
            )}
          </div>

          {/* Lesson Title */}
          <span className="flex-1 font-medium leading-tight">
            {lesson.title}
          </span>
        </button>
      ))}
    </nav>
  </div>
</aside>
```

**Design tokens used:**
- Width: `w-80` (320px)
- Background: `bg-white`
- Border: `border-r border-gray-200`
- Padding: `p-6`
- Active lesson: `bg-yellow-50` (beige highlight from screenshot)
- Completed: `text-green-500` (checkmark icon)
- Spacing: `space-y-1` (tight list), `gap-3` (icon-to-text)

**Interactive states:**
- **Default:** `text-gray-700`
- **Hover:** `hover:bg-gray-50`
- **Active/Current:** `bg-yellow-50 text-gray-900`
- **Completed:** Green checkmark icon
- **Incomplete:** Empty circle outline

**Responsive behavior:**
- Desktop (≥768px): Fixed sidebar on left
- Mobile (<768px): Collapsible drawer or separate page

**Existing pattern reference:** Similar to navigation patterns in app

---

### 4. VideoPlayer

**Screenshot reference:** classroom_module_view.png

**Purpose:** Display embedded video lessons with responsive sizing

**Structure:**
```tsx
<div className="relative mb-6 aspect-video w-full overflow-hidden rounded-lg bg-black">
  {/* YouTube/Vimeo/Loom Embed */}
  <iframe
    src={embedUrl}
    title={lessonTitle}
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowFullScreen
    className="absolute inset-0 h-full w-full"
  />

  {/* Error State */}
  {loadError && (
    <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
      <div className="text-center text-white">
        <div className="mb-4 text-6xl">⚠️</div>
        <p className="mb-2 text-lg font-semibold">Unable to load video</p>
        <p className="mb-4 text-sm text-gray-300">Please try again later</p>
        <button
          onClick={retry}
          className="rounded-md bg-white px-4 py-2 text-sm font-medium text-gray-900 hover:bg-gray-100"
        >
          Retry
        </button>
      </div>
    </div>
  )}
</div>
```

**Design tokens:**
- Aspect ratio: `aspect-video` (16:9)
- Border radius: `rounded-lg`
- Background: `bg-black` (letterbox)

**Interactive states:**
- **Loading:** Black background with spinner
- **Error:** Error message with retry button
- **Playing:** Standard video player controls

**Notes:**
- Uses iframe embedding (no custom player needed)
- Supports YouTube, Vimeo, Loom URLs
- Responsive sizing maintains 16:9 aspect ratio

---

### 5. LessonContent (Text)

**Screenshot reference:** classroom_module_view.png (below video)

**Purpose:** Display formatted text content for text-based lessons

**Structure:**
```tsx
<div className="prose prose-gray max-w-none">
  {/* Summary/Section Title */}
  <h3 className="mb-4 text-xl font-bold text-gray-900">
    {sectionTitle}
  </h3>

  {/* Rich Text Content */}
  <div
    className="text-gray-700 leading-relaxed"
    dangerouslySetInnerHTML={{ __html: sanitizedContent }}
  />
</div>
```

**Design tokens:**
- Typography: `prose prose-gray` (Tailwind Typography plugin)
- Max width: `max-w-none` (full width within container)
- Heading: `text-xl font-bold text-gray-900`
- Body: `text-gray-700 leading-relaxed`

**Rich text support:**
- Headings (H1-H6)
- Bold, italic, underline
- Bulleted and numbered lists
- Links (open in new tab)
- Code blocks (if supported)

**Security:** Content must be sanitized server-side before rendering

---

### 6. LessonHeader

**Screenshot reference:** classroom_module_view.png (top of content area)

**Purpose:** Display lesson title and completion toggle

**Structure:**
```tsx
<header className="mb-6 flex items-start justify-between border-b border-gray-200 pb-4">
  {/* Left: Title and Badge */}
  <div>
    <h1 className="mb-2 text-2xl font-bold text-gray-900">
      {lessonTitle}
    </h1>

    {/* Content Type Badge */}
    <div className="inline-flex items-center gap-1.5 rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-700">
      {contentType === 'video' ? (
        <>
          <PlayIcon className="h-4 w-4" />
          <span>Video</span>
        </>
      ) : (
        <>
          <DocumentIcon className="h-4 w-4" />
          <span>Text</span>
        </>
      )}
    </div>
  </div>

  {/* Right: Completion Toggle */}
  <button
    onClick={toggleComplete}
    className={cn(
      "flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors",
      isComplete
        ? "bg-green-50 text-green-700 hover:bg-green-100"
        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
    )}
  >
    {isComplete ? (
      <>
        <CheckCircleIcon className="h-5 w-5" />
        <span>Completed</span>
      </>
    ) : (
      <>
        <CircleIcon className="h-5 w-5" />
        <span>Mark as Complete</span>
      </>
    )}
  </button>
</header>
```

**Design tokens:**
- Title: `text-2xl font-bold text-gray-900`
- Border: `border-b border-gray-200`
- Badge: `rounded-full bg-gray-100 px-3 py-1 text-sm`
- Complete button: `bg-green-50 text-green-700` (checked), `bg-gray-100 text-gray-700` (unchecked)
- Icon size: `h-4 w-4` (badge), `h-5 w-5` (button)

**Interactive states:**
- **Uncomplete:** Gray background, empty circle icon
- **Complete:** Green background, filled checkmark icon
- **Hover:** Slightly darker background
- **Saving:** Brief spinner, then success message

**Feedback:** Brief toast notification "Progress saved" after toggle

---

### 7. LessonNavigation (Previous/Next)

**Screenshot reference:** Not directly visible but implied from PRD

**Purpose:** Navigate between lessons with Previous/Next buttons

**Structure:**
```tsx
<footer className="mt-8 flex items-center justify-between border-t border-gray-200 pt-6">
  {/* Previous Button */}
  <button
    onClick={goToPrevious}
    disabled={isFirstLesson}
    className="flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 disabled:text-gray-400 disabled:hover:bg-transparent"
  >
    <ChevronLeftIcon className="h-5 w-5" />
    <span>Previous Lesson</span>
  </button>

  {/* Progress Indicator */}
  <span className="text-sm text-gray-500">
    Lesson {currentIndex} of {totalLessons}
  </span>

  {/* Next Button */}
  <button
    onClick={goToNext}
    disabled={isLastLesson}
    className="flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 disabled:text-gray-400 disabled:hover:bg-transparent"
  >
    <span>Next Lesson</span>
    <ChevronRightIcon className="h-5 w-5" />
  </button>
</footer>
```

**Design tokens:**
- Border: `border-t border-gray-200`
- Padding: `pt-6`
- Button: `rounded-md px-4 py-2 text-sm`
- Text: `text-gray-700` (enabled), `text-gray-400` (disabled)
- Hover: `hover:bg-gray-100`

**Interactive states:**
- **Enabled:** Default gray, hover background
- **Disabled:** Lighter gray, no hover effect
- **Hover tooltip:** Shows adjacent lesson title

**Edge cases:**
- First lesson: Previous button disabled
- Last lesson: Next button disabled
- Cross-module navigation: Button shows "Next: [Module Name]"

---

### 8. CourseOverviewHeader

**Screenshot reference:** Implied from PRD, similar to classroom_module_view.png structure

**Purpose:** Display course details and primary action button

**Structure:**
```tsx
<header className="mb-8 rounded-lg bg-white p-6 shadow-md">
  {/* Breadcrumb */}
  <nav className="mb-4 text-sm text-gray-500">
    <a href="/classroom" className="hover:text-gray-700">Courses</a>
    <span className="mx-2">›</span>
    <span className="text-gray-900">{courseTitle}</span>
  </nav>

  {/* Cover Image (if provided) */}
  {coverImageUrl && (
    <img
      src={coverImageUrl}
      alt={courseTitle}
      className="mb-6 aspect-video w-full rounded-lg object-cover"
    />
  )}

  {/* Title and Metadata */}
  <div className="mb-6">
    <h1 className="mb-3 text-3xl font-bold text-gray-900">
      {courseTitle}
    </h1>

    {/* Instructor Info */}
    <div className="mb-4 flex items-center gap-3">
      <img
        src={instructorAvatar}
        alt={instructorName}
        className="h-10 w-10 rounded-full"
      />
      <div>
        <p className="text-sm font-medium text-gray-900">{instructorName}</p>
        <p className="text-xs text-gray-500">Instructor</p>
      </div>
    </div>

    {/* Description */}
    <p className="mb-4 text-gray-700 leading-relaxed">
      {description}
    </p>

    {/* Course Stats */}
    <div className="mb-4 flex flex-wrap gap-4 text-sm text-gray-600">
      <span>{moduleCount} modules</span>
      <span>•</span>
      <span>{lessonCount} lessons</span>
      {estimatedDuration && (
        <>
          <span>•</span>
          <span>{estimatedDuration}</span>
        </>
      )}
      {isComplete && (
        <>
          <span>•</span>
          <span className="flex items-center gap-1 text-green-600">
            <CheckCircleIcon className="h-4 w-4" />
            Completed
          </span>
        </>
      )}
    </div>

    {/* Progress Bar (if started) */}
    {progress !== null && (
      <div className="mb-4">
        <div className="mb-2 flex items-center justify-between text-sm">
          <span className="text-gray-600">Overall Progress</span>
          <span className="font-semibold text-gray-900">{progress}%</span>
        </div>
        <div className="h-2.5 w-full overflow-hidden rounded-full bg-gray-200">
          <div
            className="h-full rounded-full bg-green-500 transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    )}
  </div>

  {/* Primary Action Button */}
  <div className="flex gap-3">
    <button className="rounded-md bg-primary-500 px-6 py-3 font-semibold text-white hover:bg-primary-600">
      {!isStarted ? "Start Course" : progress === 100 ? "Review Course" : "Continue"}
    </button>
  </div>
</header>
```

**Design tokens:**
- Background: `bg-white`
- Shadow: `shadow-md`
- Border radius: `rounded-lg`
- Title: `text-3xl font-bold`
- Stats: `text-sm text-gray-600`
- Primary button: `bg-primary-500` with `hover:bg-primary-600`

---

### 9. ModuleAccordion

**Screenshot reference:** Implied from PRD, structure shown in classroom_module_view.png

**Purpose:** Collapsible list of modules containing lessons

**Structure:**
```tsx
<div className="space-y-4">
  {modules.map((module) => (
    <div key={module.id} className="rounded-lg border border-gray-200 bg-white">
      {/* Module Header (Clickable) */}
      <button
        onClick={() => toggleModule(module.id)}
        className="flex w-full items-center justify-between p-4 text-left hover:bg-gray-50"
      >
        <div className="flex-1">
          <h3 className="mb-1 text-lg font-semibold text-gray-900">
            {module.title}
          </h3>
          {module.description && (
            <p className="text-sm text-gray-600">
              {module.description}
            </p>
          )}

          {/* Progress Indicator */}
          <div className="mt-2 flex items-center gap-2 text-xs text-gray-500">
            <span>{module.completedLessons} of {module.totalLessons} lessons complete</span>
            <div className="h-1 w-24 overflow-hidden rounded-full bg-gray-200">
              <div
                className="h-full rounded-full bg-green-500"
                style={{ width: `${(module.completedLessons / module.totalLessons) * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Expand/Collapse Icon */}
        <ChevronDownIcon
          className={cn(
            "h-5 w-5 text-gray-400 transition-transform",
            isExpanded && "rotate-180"
          )}
        />
      </button>

      {/* Lesson List (Collapsible) */}
      {isExpanded && (
        <div className="border-t border-gray-200 p-2">
          {module.lessons.map((lesson, index) => (
            <button
              key={lesson.id}
              onClick={() => navigateToLesson(lesson.id)}
              className="flex w-full items-center gap-3 rounded-md p-3 text-left hover:bg-gray-50"
            >
              {/* Lesson Number */}
              <span className="text-sm font-medium text-gray-500 w-6">
                {index + 1}.
              </span>

              {/* Content Type Icon */}
              {lesson.contentType === 'video' ? (
                <PlayCircleIcon className="h-5 w-5 flex-shrink-0 text-gray-400" />
              ) : (
                <DocumentTextIcon className="h-5 w-5 flex-shrink-0 text-gray-400" />
              )}

              {/* Lesson Title */}
              <span className="flex-1 text-sm text-gray-900">
                {lesson.title}
              </span>

              {/* Completion Checkmark */}
              {lesson.isComplete && (
                <CheckCircleIcon className="h-5 w-5 flex-shrink-0 text-green-500" />
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  ))}
</div>
```

**Design tokens:**
- Border: `border border-gray-200`
- Background: `bg-white`
- Hover: `hover:bg-gray-50`
- Spacing: `space-y-4` (between modules), `p-4` (module header)
- Title: `text-lg font-semibold text-gray-900`
- Mini progress bar: `h-1 w-24`

**Interactive states:**
- **Collapsed:** Chevron pointing down
- **Expanded:** Chevron rotated 180° (pointing up), lessons visible
- **Hover:** Light gray background

**Empty state:** "No lessons in this module yet" (admin sees "Add lessons" button)

---

## Color Palette Usage

From screenshots observed:

| Purpose | Hex Value | Tailwind Class |
|---------|-----------|----------------|
| Page background | `#F7F9FA` | `bg-gray-50` |
| Card background | `#FFFFFF` | `bg-white` |
| Primary text | `#1D2129` | `text-gray-900` |
| Secondary text | `#65676B` | `text-gray-600` |
| Muted text | `#B0B3B8` | `text-gray-400` |
| Borders | `#E4E6EB` | `border-gray-200` |
| Progress bar (filled) | `#22C55E` | `bg-green-500` |
| Progress bar (track) | `#E5E7EB` | `bg-gray-200` |
| Active/Current highlight | `#FFFBEB` | `bg-yellow-50` (beige from screenshot) |
| Hover background | `#F9FAFB` | `hover:bg-gray-50` |
| Success/Complete | `#22C55E` | `text-green-500` or `bg-green-500` |

**Notes:**
- Screenshots use a soft yellow/beige highlight for active lessons (`bg-yellow-50`)
- Green is consistently used for progress and completion states
- Gray scale provides hierarchy without heavy colors

---

## Typography Scale

| Element | Screenshot Size | Tailwind Class | Weight |
|---------|----------------|----------------|--------|
| Page heading (H1) | ~28-30px | `text-3xl` | `font-bold` (700) |
| Course title (grid) | ~18px | `text-lg` | `font-semibold` (600) |
| Module title | ~18-20px | `text-lg` | `font-semibold` (600) |
| Lesson title (sidebar) | ~14-15px | `text-sm` | `font-medium` (500) |
| Body text | ~15px | `text-base` | `font-normal` (400) |
| Description | ~14px | `text-sm` | `font-normal` (400) |
| Metadata/labels | ~13px | `text-xs` | `font-normal` (400) |
| Button text | ~14-15px | `text-sm` | `font-medium` (500) |

**Line height:**
- Headings: `leading-tight` (1.25)
- Body text: `leading-relaxed` (1.625)
- Tight spaces: `leading-tight` or `leading-snug`

---

## Spacing System

| Gap Type | Screenshot Measurement | Tailwind Class |
|----------|----------------------|----------------|
| Between course cards | ~24px | `gap-6` |
| Card internal padding | ~16px | `p-4` |
| Section gaps (header to content) | ~24px | `mb-6` |
| List item gaps | ~4px | `space-y-1` |
| Icon to text | ~8-12px | `gap-2` or `gap-3` |
| Module to module | ~16px | `space-y-4` |
| Container padding | ~16-24px | `px-4 py-6` |

**Vertical rhythm:**
- Use consistent spacing scale: 4px, 8px, 12px, 16px, 24px, 32px, 48px
- Larger gaps between major sections
- Tighter gaps within related content groups

---

## Interactive Patterns

### Course Card Hover
**Where:** Course grid cards
**Behavior:** Shadow elevation on hover, cursor pointer
**Implementation:**
- Default: `shadow-md`
- Hover: `shadow-lg transition-shadow`
- Optional: Subtle scale `hover:scale-[1.02]`

### Lesson Selection
**Where:** Sidebar lesson list, module accordion
**Behavior:** Background color change on hover, active highlight
**Implementation:**
- Default: `text-gray-700`
- Hover: `hover:bg-gray-50`
- Active: `bg-yellow-50 text-gray-900` (current lesson)

### Progress Toggle
**Where:** Lesson header "Mark as Complete" button
**Behavior:** Icon and color change on toggle
**Implementation:**
- Uncomplete: Gray background, empty circle
- Complete: Green background, checkmark icon
- Transition: `transition-colors`
- Feedback: Toast notification "Progress saved"

### Module Accordion Expand/Collapse
**Where:** Module list headers
**Behavior:** Chevron rotation, content reveal/hide
**Implementation:**
- Collapsed: Chevron down
- Expanded: Chevron rotated 180° with `transition-transform`
- Content: Slide down animation (optional, can be instant)

### Pagination Buttons
**Where:** Bottom of course grid
**Behavior:** Disabled state when at boundaries
**Implementation:**
- Enabled: `text-gray-700 hover:bg-gray-100`
- Disabled: `text-gray-400 cursor-not-allowed`
- Active page: `font-medium text-gray-900`

### Video Player Loading
**Where:** Video lesson content area
**Behavior:** Black background with spinner until iframe loads
**Implementation:**
- Loading: Black background, centered spinner
- Error: Error message with retry button
- Loaded: Standard iframe controls

---

## Responsive Breakpoints

| Breakpoint | Width | Layout Changes |
|------------|-------|----------------|
| Mobile | < 768px | - Single column grid<br>- Sidebar converts to drawer/separate page<br>- Stack navigation vertically |
| Tablet | 768-1023px | - 2 column grid<br>- Narrower sidebar (if shown)<br>- Reduced padding |
| Desktop | ≥ 1024px | - 3 column grid<br>- Full sidebar navigation<br>- Max container width 1100px |

**Mobile-specific adjustments:**
- Course cards: Full width, reduced padding
- Lesson view: Sidebar hidden by default, accessible via hamburger menu
- Video player: Full width, maintains 16:9 aspect ratio
- Buttons: Full width or centered

---

## Implementation Checklist

### Setup
- [ ] Load `ui-design` skill before coding
- [ ] Configure Tailwind theme with design tokens
- [ ] Install dependencies: `react-router-dom`, icon library (Heroicons or Lucide)
- [ ] Set up rich text sanitization library (DOMPurify)

### Components to Build
- [ ] `CourseCard` - Reuse card pattern from existing components
- [ ] `CourseGrid` - New component with responsive grid
- [ ] `LessonSidebar` - New component for lesson navigation
- [ ] `VideoPlayer` - New component for iframe embeds
- [ ] `LessonContent` - New component for rich text display
- [ ] `LessonHeader` - New component with completion toggle
- [ ] `LessonNavigation` - New component for prev/next buttons
- [ ] `CourseOverviewHeader` - New component for course details
- [ ] `ModuleAccordion` - New component for collapsible modules

### Reusable Patterns
- [ ] Button styles (primary, secondary, disabled states)
- [ ] Form inputs (if admin forms needed)
- [ ] Loading skeletons
- [ ] Empty state illustrations
- [ ] Toast notifications for feedback

### Testing
- [ ] Test responsive breakpoints (mobile, tablet, desktop)
- [ ] Verify color contrast (WCAG AA compliance)
- [ ] Add focus states for accessibility
- [ ] Test keyboard navigation (Tab, arrows)
- [ ] Test with screen readers (semantic HTML)

---

## Notes for Implementation

### Phase Recommendation

Based on screenshot analysis, suggested implementation phases:

**Phase 1: Course Discovery (Screenshots 1 & 3)**
- Components: `CourseGrid`, `CourseCard`, pagination
- Pages: Course list page
- Features: View courses, progress display, navigation to course detail

**Phase 2: Course Overview**
- Components: `CourseOverviewHeader`, `ModuleAccordion`
- Pages: Course detail page
- Features: View modules/lessons, navigate to lessons, "Start Course" / "Continue" buttons

**Phase 3: Lesson Consumption (Screenshot 2)**
- Components: `LessonSidebar`, `VideoPlayer`, `LessonContent`, `LessonHeader`, `LessonNavigation`
- Pages: Lesson view page
- Features: Watch videos, read text, mark complete, navigate between lessons

**Phase 4: Admin Management**
- Components: Course/Module/Lesson forms, drag-and-drop reordering
- Pages: Admin course editor
- Features: CRUD operations, reordering, rich text editor integration

### Key Technical Decisions

1. **Rich Text Editor:** Recommend TipTap or Quill for admin forms (deferred to TDD)
2. **Icons:** Use Heroicons (stroke-based, matches design system)
3. **Video Embeds:** Simple iframe approach (no custom player library needed)
4. **Drag-and-Drop:** Use `@dnd-kit/core` or `react-beautiful-dnd` for reordering (Phase 4)
5. **State Management:** React Context or TanStack Query for course data
6. **Routing:** React Router with nested routes for course > module > lesson hierarchy

### Accessibility Considerations

- Use semantic HTML: `<article>` for cards, `<nav>` for lesson lists, `<aside>` for sidebar
- Add ARIA labels for icons and buttons without text
- Ensure focus states are visible (ring outline)
- Support keyboard navigation (Tab, Enter, Arrows)
- Maintain color contrast ratios (WCAG AA: 4.5:1 for text)
- Add `alt` text for all images
- Use proper heading hierarchy (H1 > H2 > H3)

### Performance Optimizations

- Lazy load course cover images with placeholders
- Paginate course grid (shown in screenshots: 14 items per page)
- Implement virtual scrolling for long lesson lists (if needed)
- Optimize video iframe loading (defer offscreen iframes)
- Cache course progress data locally (reduce API calls)

### Edge Cases to Handle

- Missing cover images (show default gradient placeholder)
- Empty states (no courses, no modules, no lessons)
- Long titles/descriptions (use `line-clamp` for truncation)
- Video load failures (show error message with retry)
- Progress save failures (show error toast with retry)
- Slow network (show skeleton loaders)

---

## Existing Component Reuse

| New Component | Existing Pattern | Reuse Level |
|--------------|------------------|-------------|
| `CourseCard` | `ProfileSidebar` card | High - Same card pattern (`rounded-lg bg-white shadow`) |
| `CourseGrid` | None | Medium - Use Tailwind grid utilities |
| Form inputs (admin) | `LoginForm` | High - Reuse input styles and validation patterns |
| Buttons | Existing button styles | High - Reuse primary/secondary button classes |
| Avatars | `ProfileSidebar` avatar | High - Reuse circular avatar with fallback |
| Progress bars | None | Low - New component (simple div-based) |
| Icons | None | Low - Install Heroicons or Lucide |

---

## Design System Compliance

✅ **Follows Koulu design system:**
- Card-based layout on gray background (`bg-gray-50`)
- Consistent 8px border radius (`rounded-lg`)
- Clean typography hierarchy with system fonts
- Minimal color palette (grays + green for progress)
- High whitespace usage for readability
- Soft shadows for depth (`shadow-md`, `shadow-lg`)

✅ **Matches Skool.com reference:**
- Course cards with cover images and progress bars
- Two-column lesson view (sidebar + content)
- Beige/yellow highlight for active lesson
- Green checkmarks for completion
- Simple pagination controls

✅ **Mobile-first approach:**
- Responsive grid (1/2/3 columns)
- Stacked layout for mobile
- Touch-friendly button sizes

---

## Summary

**Total Components Identified:** 9 major components
- **Reusable:** CourseCard, LessonSidebar, VideoPlayer, LessonContent, Progress bars
- **New Patterns:** ModuleAccordion, LessonNavigation, CourseGrid with pagination
- **Existing Patterns:** Card wrapper, buttons, forms, avatars

**Design Tokens:**
- Colors: 8 primary colors from gray scale + green for success
- Typography: 8 size classes (xs to 3xl)
- Spacing: 6-step scale (1 to 12 in Tailwind units)
- Border radius: Consistent 8px (`rounded-lg`)

**Complexity Estimate:** **Medium**
- Well-defined components with clear patterns
- Reuses existing design system extensively
- Some new patterns (accordion, video player) but straightforward
- Admin features (drag-and-drop) add complexity in later phases

**Implementation Time Estimate (Member View):**
- Phase 1 (Course Grid): ~8-12 hours
- Phase 2 (Course Overview): ~12-16 hours
- Phase 3 (Lesson View): ~16-20 hours
- **Total: ~36-48 hours** for core member experience

**Next Steps:**
1. Use this UI_SPEC to create a detailed phased implementation plan
2. Write Technical Design Document (TDD) with component architecture
3. Implement Phase 1 (Course Grid) first to validate design system
4. Iterate through phases with user testing between each

---

**Document Status:** ✅ Complete - Ready for phased implementation planning
**Last Updated:** 2026-02-07
**Generated By:** Claude Sonnet 4.5
