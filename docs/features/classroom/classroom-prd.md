# Classroom - Product Requirements Document

**Version:** 2.0
**Last Updated:** 2026-02-07
**Status:** Draft
**Implementation Status:** Phase 1 Complete (Course Foundation)
**Bounded Context:** Classroom
**PRD Type:** Feature Specification

---

## 1. Overview

### 1.1 What

A structured learning system where admins create courses organized into modules and lessons. Members can browse courses, consume content (text and embedded video), track their progress, and pick up where they left off. The system supports flexible navigation (non-linear) and provides progress tracking at lesson, module, and course levels.

### 1.2 Why

Koulu communities need a way to deliver educational content beyond discussions. Courses provide:
- **Structured knowledge transfer** - Complex topics broken into digestible lessons
- **Progress motivation** - Visual feedback on learning achievements
- **Content organization** - Modules group related lessons logically
- **Flexible learning** - Members learn at their own pace, on their own schedule
- **Creator value** - Admins can monetize expertise through educational content
- **Retention driver** - Educational content increases member lifetime value

Without Classroom, Koulu is limited to discussions and events. Classroom transforms communities into learning platforms.

### 1.3 Success Criteria

| Metric | Target |
|--------|--------|
| Course completion rate | > 25% of members who start complete at least 1 course |
| Average lesson completion time | < 15 minutes per lesson |
| Course engagement (7-day return rate) | > 50% of course starters return within 7 days |
| "Continue" feature usage | > 70% of course navigation uses "Continue" vs manual selection |
| Admin course creation | > 1 course per community within 30 days |

---

## 2. User Stories

### 2.1 Course Management (Admin)

| ID | Story | Priority |
|----|-------|----------|
| US-CM1 | As an admin, I want to create a course with title, description, and cover image, so that I can organize learning content | Must Have |
| US-CM2 | As an admin, I want to view all courses I've created, so that I can manage my course library | Must Have |
| US-CM3 | As an admin, I want to edit course details, so that I can keep information current | Must Have |
| US-CM4 | As an admin, I want to delete a course, so that I can remove outdated content | Must Have |

### 2.2 Module Management (Admin)

| ID | Story | Priority |
|----|-------|----------|
| US-MM1 | As an admin, I want to add modules to a course, so that I can organize lessons into sections | Must Have |
| US-MM2 | As an admin, I want to reorder modules via drag-and-drop, so that I can control the learning sequence | Must Have |
| US-MM3 | As an admin, I want to edit module title and description, so that I can clarify each section's purpose | Must Have |
| US-MM4 | As an admin, I want to delete a module, so that I can remove irrelevant sections | Must Have |

### 2.3 Lesson Management (Admin)

| ID | Story | Priority |
|----|-------|----------|
| US-LM1 | As an admin, I want to create text lessons with formatting, so that I can deliver written content clearly | Must Have |
| US-LM2 | As an admin, I want to create video lessons by embedding YouTube/Vimeo/Loom URLs, so that I can deliver video without hosting | Must Have |
| US-LM3 | As an admin, I want to reorder lessons within a module, so that I can structure the learning flow | Must Have |
| US-LM4 | As an admin, I want to edit lesson title and content, so that I can update material | Must Have |
| US-LM5 | As an admin, I want to delete a lesson, so that I can remove outdated content | Must Have |

### 2.4 Course Discovery (Member)

| ID | Story | Priority |
|----|-------|----------|
| US-CD1 | As a member, I want to see all available courses in a grid, so that I can discover learning opportunities | Must Have |
| US-CD2 | As a member, I want to see course cards with cover images, titles, descriptions, and my progress, so that I can decide what to learn | Must Have |
| US-CD3 | As a member, I want to click a course card to view the full course outline, so that I understand what I'll learn | Must Have |

### 2.5 Course Consumption (Member)

| ID | Story | Priority |
|----|-------|----------|
| US-CC1 | As a member, I want to click "Start Course" to begin the first lesson, so that I can start learning | Must Have |
| US-CC2 | As a member, I want to click "Continue" to jump to my next incomplete lesson, so that I don't waste time finding my place | Must Have |
| US-CC3 | As a member, I want to navigate freely to any lesson, so that I can review or skip ahead | Must Have |
| US-CC4 | As a member, I want to read text lessons with formatting, so that the material is clear | Must Have |
| US-CC5 | As a member, I want to watch embedded videos without leaving the platform, so that my learning experience is seamless | Must Have |
| US-CC6 | As a member, I want Previous/Next buttons to navigate between lessons, so that I can move through content easily | Must Have |

### 2.6 Progress Tracking (Member)

| ID | Story | Priority |
|----|-------|----------|
| US-PT1 | As a member, I want to mark a lesson as complete, so that I can track my progress | Must Have |
| US-PT2 | As a member, I want to un-mark a lesson, so that I can review it again if needed | Must Have |
| US-PT3 | As a member, I want to see completion percentage for each course and module, so that I know how far I've progressed | Must Have |
| US-PT4 | As a member, I want the system to remember my progress when I leave and return, so that I don't lose my place | Must Have |

---

## 3. Business Rules

### 3.1 Course Rules

**Creation & Editing:**
- Title: Required, 2-200 characters, no leading/trailing whitespace
- Description: Optional, max 2000 characters, plain text
- Cover image: Optional, must be valid HTTPS URL if provided
- Estimated duration: Optional, free-form text (e.g., "2 hours", "3 weeks")
- Only admins can create, edit, or delete courses
- Instructor name displayed is the admin who created the course

**Deletion:**
- Deletion is always soft delete (hidden from members, but progress retained)
- Deleted courses are hidden from course lists
- Members viewing a deleted course see "This course is no longer available"
- Progress on deleted courses is preserved in the database

**Visibility:**
- All non-deleted courses visible to all authenticated members
- No level-gating or payment restrictions in MVP

---

### 3.2 Module Rules

**Creation & Editing:**
- Title: Required, 2-200 characters
- Description: Optional, max 1000 characters
- Position is auto-assigned as the next sequential number when created
- Admins can reorder modules by dragging and dropping
- Empty modules (no lessons) are allowed

**Deletion:**
- Deletion is soft delete
- Deleted modules are excluded from course detail views
- Progress for lessons in deleted modules is retained

---

### 3.3 Lesson Rules

**Content Types:**
- Two types: Text or Video (not both in a single lesson)
- Each lesson has exactly one content type

**Text Lessons:**
- Title: Required, 2-200 characters
- Content: Required, 1-50,000 characters
- Supports rich text formatting (bold, italic, lists, links, headings)

**Video Lessons:**
- Title: Required, 2-200 characters
- Content: Required, valid YouTube, Vimeo, or Loom embed URL
- Videos displayed as responsive embedded players
- Invalid video URLs rejected at creation time

**Positioning & Deletion:**
- Position auto-assigned as next sequential number when created
- Admins can reorder lessons via drag-and-drop
- Deletion is soft delete
- Deleted lessons excluded from module views but progress retained

---

### 3.4 Progress Tracking Rules

**Progress Creation:**
- Progress record created automatically when member accesses first lesson ("Start Course")
- One progress record per member per course
- Progress persists even if course/modules/lessons are deleted

**Lesson Completion:**
- Members can mark any lesson as complete (no sequential enforcement)
- Members can toggle completion on/off freely
- Marking a lesson complete updates progress percentages immediately

**Completion Calculations:**
- Module completion = (completed lessons in module / total non-deleted lessons in module) × 100
- Course completion = (completed lessons in all modules / total non-deleted lessons in course) × 100
- Only non-deleted lessons count toward totals

**Navigation Memory:**
- "Last accessed lesson" updated whenever member views a lesson
- "Next incomplete lesson" is the first lesson (by position) not yet completed
- If all lessons complete, "next incomplete" is null

---

### 3.5 Navigation Rules

**Start Course:**
- Navigates to the first lesson of the first module (by position)
- Creates progress record if not already started

**Continue:**
- Navigates to the first incomplete lesson (by module/lesson position order)
- If all lessons complete, navigates to the last lesson with "Course Complete!" message

**Previous/Next Buttons:**
- Previous on first lesson of module → Last lesson of previous module (if exists)
- Next on last lesson of module → First lesson of next module (if exists)
- Previous on first lesson of first module → Disabled
- Next on last lesson of last module → Disabled

**Free Navigation:**
- Members can jump directly to any lesson from the course overview
- No locks or prerequisites
- Can navigate backward to review material

---

### 3.6 Permission Rules

| Action | Member | Admin |
|--------|--------|-------|
| View courses | ✓ | ✓ |
| View lessons | ✓ | ✓ |
| Track progress | ✓ | ✓ |
| Create course | ✗ | ✓ |
| Edit course | ✗ | ✓ |
| Delete course | ✗ | ✓ |
| Create module | ✗ | ✓ |
| Edit module | ✗ | ✓ |
| Delete module | ✗ | ✓ |
| Reorder modules | ✗ | ✓ |
| Create lesson | ✗ | ✓ |
| Edit lesson | ✗ | ✓ |
| Delete lesson | ✗ | ✓ |
| Reorder lessons | ✗ | ✓ |

---

## 4. UI Behavior

### 4.1 Course List Page (Member View)

**Layout:** Grid of course cards (responsive: 1 column mobile, 2 tablet, 3 desktop)

**Course Card (per course):**
- Cover image (default placeholder if none provided)
- Course title (bold, prominent)
- Short description (truncated to 2 lines with ellipsis)
- Instructor display name with small avatar
- Module count badge (e.g., "5 modules")
- Lesson count badge (e.g., "23 lessons")
- Estimated duration (if provided, e.g., "~2 hours")
- Progress bar showing completion percentage (if started, hidden if not started)
- Call-to-action button:
  - "Start Course" if not started
  - "Continue" if started but not complete
  - "Review" if 100% complete

**Empty State:**
- Illustration + message: "No courses available yet"
- Message for admins: "Create your first course to get started"

**Loading State:**
- Skeleton cards (3 visible) while loading

**Interactions:**
- Click card (anywhere except button) → Navigate to course overview
- Click "Start Course" → Navigate to first lesson, create progress record
- Click "Continue" → Navigate to next incomplete lesson
- Hover card → Slight elevation/shadow effect

---

### 4.2 Course Overview Page

**Layout:** Full-width header + module accordion

**Breadcrumb:**
- "Courses" > "Course Title" (clickable navigation)

**Course Header:**
- Large cover image (hero section)
- Course title (large, bold)
- Instructor info (avatar, display name, label "Instructor")
- Full description (expanded, no truncation)
- Course stats:
  - X modules
  - Y lessons
  - Estimated duration (if provided)
  - Completion badge if 100% (e.g., "✓ Completed")
- Overall progress bar with percentage (if started)
- Primary action button:
  - "Start Course" if not started
  - "Continue" if in progress
  - "Review Course" if 100% complete

**Module Accordion:**
- Each module displayed as collapsible section:
  - Module title (bold)
  - Module description (smaller font)
  - Completion indicator: "X of Y lessons complete" with mini progress bar
  - Expand/collapse icon (chevron)
- Clicking module header expands/collapses lesson list

**Lesson List (within expanded module):**
- Each lesson shows:
  - Lesson number (sequential within module, e.g., "1.", "2.")
  - Content type icon (document icon for text, play icon for video)
  - Lesson title
  - Checkmark icon if complete (green)
  - Estimated time (future feature, shows "—" for now)
- Click lesson → Navigate to lesson view
- Current lesson highlighted (if member is viewing a lesson)

**States:**
- Loading: Skeleton header + accordion placeholders
- Empty course (no modules): "This course has no content yet" (admin sees "Add your first module")
- Empty module (no lessons): "No lessons in this module yet" (admin sees "Add lessons")

---

### 4.3 Lesson View Page

**Layout:** Three sections - breadcrumb, lesson content, navigation footer

**Breadcrumb:**
- "Courses" > "Course Title" > "Module Title" > "Lesson Title"
- All clickable for navigation

**Lesson Header:**
- Lesson title (large)
- Content type badge (e.g., "📝 Text" or "🎥 Video")
- "Mark as Complete" toggle (checkbox or toggle switch)
  - Checked if complete, unchecked if not
  - Clicking toggles state immediately (optimistic update)
  - Shows brief success message: "Progress saved"

**Lesson Content Area:**

**For Text Lessons:**
- Rich text content with formatting preserved:
  - Headings (H1-H6)
  - Bold, italic, underline
  - Bulleted and numbered lists
  - Links (open in new tab)
  - Code blocks (if supported)
  - Images (if URLs embedded in content)
- Readable typography (comfortable line height, max width ~800px)

**For Video Lessons:**
- Responsive embedded video player (16:9 aspect ratio)
- Player controls (play, pause, volume, fullscreen)
- Fallback message if video fails to load: "Unable to load video. Please try again later."

**Sidebar (optional, desktop only):**
- Module outline showing all lessons
- Current lesson highlighted
- Click any lesson to navigate
- Shows completion checkmarks
- Collapsible (hide/show button)

**Navigation Footer:**
- "Previous Lesson" button (left side)
  - Disabled and grayed out if on first lesson of first module
  - Shows previous lesson title on hover
- Progress indicator (center): "Lesson X of Y in this module"
- "Next Lesson" button (right side)
  - Disabled and grayed out if on last lesson of last module
  - Shows next lesson title on hover
  - If next lesson is in a different module, button says "Next: [Module Name]"

**States:**
- Loading: Skeleton content area
- Video load error: Error message with "Retry" button
- Completion success: Brief toast notification "Progress saved"
- Network error on progress save: "Failed to save progress. Retry?" with retry button

**Keyboard Navigation:**
- Arrow keys (left/right) navigate previous/next
- Spacebar toggles completion (when not in video player)

---

### 4.4 Course Creation/Editing (Admin)

**Trigger:** "Create Course" button on course list page (admin only)

**Form (modal or dedicated page):**

**Fields:**
1. **Cover Image URL** (optional)
   - Text input for HTTPS URL
   - Image preview below input (live preview as URL is typed)
   - Validation: Must be valid HTTPS URL if provided
   - Placeholder: "https://example.com/image.jpg"

2. **Course Title** (required)
   - Text input, max 200 characters
   - Character counter below input: "150/200"
   - Validation: 2-200 characters, no leading/trailing spaces
   - Error message: "Title must be 2-200 characters"

3. **Description** (optional)
   - Textarea, max 2000 characters
   - Character counter: "1500/2000"
   - Auto-expanding height as user types

4. **Estimated Duration** (optional)
   - Text input, free-form (e.g., "2 hours", "4 weeks")
   - Placeholder: "e.g., 2 hours, 3 weeks"
   - Hint text: "Help members plan their time"

**Actions:**
- "Cancel" button (secondary) - Closes form, discards changes
- "Create Course" / "Save Changes" button (primary)
  - Disabled if title invalid or loading
  - Shows spinner when submitting

**States:**
- Validation errors: Inline, red text below invalid fields
- Submitting: Spinner on button, form fields disabled
- Success: Redirect to course module management page
- Error: Toast notification "Failed to create course. Please try again."

---

### 4.5 Module Management (Admin)

**Location:** Course detail page, admin view

**Layout:** List of modules with management controls

**Module List:**
- Each module shows:
  - Drag handle icon (⋮⋮) on left
  - Module number (e.g., "Module 1")
  - Module title (editable inline or via modal)
  - Module description (smaller text)
  - Lesson count: "X lessons"
  - Actions: "Edit", "Delete", "Add Lesson"
  - Expand/collapse to show lesson list

**Interactions:**
- **Reordering:** Drag module by handle to new position, auto-save
- **Add Module:** "Add Module" button at bottom of list
  - Opens inline form or modal with title/description fields
  - Saves and appends to end of list
- **Edit Module:** Opens edit form (inline or modal)
- **Delete Module:** Confirmation modal:
  - "Delete this module? Lessons will be hidden but progress will be preserved."
  - "Cancel" / "Delete" buttons

**Visual Feedback:**
- Drag preview: Semi-transparent module card follows cursor
- Drop zones: Highlighted areas between modules
- Save success: Brief green flash or toast notification
- Delete success: Module fades out

---

### 4.6 Lesson Management (Admin)

**Location:** Within expanded module in module management view

**Layout:** Nested list under each module

**Lesson List:**
- Each lesson shows:
  - Drag handle icon
  - Lesson number (e.g., "1.", "2.")
  - Content type icon
  - Lesson title
  - Actions: "Edit", "Delete", "Preview"

**Add Lesson Form (modal):**

**Fields:**
1. **Lesson Title** (required)
   - Text input, 2-200 characters
   - Character counter

2. **Content Type** (required)
   - Radio buttons: "Text" or "Video"
   - Changes content field based on selection

3. **Content** (required)
   - **If Text selected:** Rich text editor (WYSIWYG)
     - Toolbar: Bold, Italic, Headings, Lists, Links
     - Character counter: "X / 50,000"
   - **If Video selected:** Text input for embed URL
     - Placeholder: "https://www.youtube.com/watch?v=..."
     - Validation: Must match YouTube, Vimeo, or Loom URL pattern
     - Video preview below input (live preview)
     - Error: "Invalid video URL. Supported: YouTube, Vimeo, Loom"

**Actions:**
- "Cancel" - Close modal, discard
- "Create Lesson" / "Save Changes" - Save and close

**Reordering:**
- Drag lessons within module to reorder
- Auto-save on drop
- Visual feedback (drag preview, drop zones)

**Delete:**
- Confirmation: "Delete this lesson? Progress will be preserved but lesson will be hidden."
- "Cancel" / "Delete"

---

### 4.7 Notifications & Feedback

**Success Messages (toasts):**
- "Course created successfully"
- "Module added"
- "Lesson created"
- "Progress saved"
- "Lesson marked as complete"
- "Module order updated"

**Error Messages (toasts or inline):**
- "Failed to load course. Please try again."
- "Invalid video URL. Supported platforms: YouTube, Vimeo, Loom"
- "Title must be 2-200 characters"
- "Failed to save progress. Retry?"
- "You don't have permission to edit this course"

**Loading Indicators:**
- Skeleton loaders for course cards, lesson content
- Spinner on buttons during submit
- Loading bar at top of page for navigation

---

## 5. Edge Cases

### 5.1 Empty States

**EC-1: No courses exist**
- Display: "No courses available yet"
- Admin sees: "Create your first course" with prominent button

**EC-2: Course with no modules**
- Member view: "This course has no content yet"
- Admin view: Empty state with "Add your first module" button

**EC-3: Module with no lessons**
- Member view: Module shows "0 lessons" and doesn't expand
- Admin view: Module expands but shows "Add your first lesson" button

**EC-4: All lessons in course are deleted (soft delete)**
- Progress shows 0% (no lessons to complete)
- Member sees: "This course currently has no available lessons"
- Admin sees: Deleted lessons with "Restore" option (future feature)

---

### 5.2 Soft Delete Behavior

**EC-5: Course deleted while member viewing**
- Member redirected to course list
- Message: "This course is no longer available"
- Progress retained in database (not visible to member)

**EC-6: Module deleted while member viewing lesson in that module**
- Lesson still visible (current session)
- On refresh or navigation, lesson not accessible
- Progress for lesson retained

**EC-7: Lesson deleted while member viewing**
- Lesson still visible (current session)
- On navigation away and back, lesson not accessible from course outline
- Completion status retained but doesn't count toward course progress

**EC-8: Member completes course, then admin deletes lessons**
- Completion percentage recalculated based on remaining lessons
- May show 100% if all remaining lessons were completed
- Historical "CourseCompleted" event not revoked (idempotent)

---

### 5.3 Progress Edge Cases

**EC-9: Mark last lesson complete**
- Completion percentage jumps to 100%
- "Course Completed" event published
- Completion badge appears on course card
- Future: Certificate generated, notification sent

**EC-10: Un-mark last lesson of completed course**
- Completion percentage drops below 100%
- Completion badge removed
- "Course Completed" event NOT un-published (events are immutable)

**EC-11: All lessons complete, click "Continue"**
- Navigates to last lesson
- Message: "You've completed this course! Review any lesson or explore other courses."
- "Continue" button becomes "Review"

**EC-12: Start course, immediately mark first lesson complete, click Next**
- Navigation works normally
- Progress shows 1/N complete
- "Next incomplete lesson" updates to second lesson

**EC-13: Progress on lessons that are later deleted**
- Completion marks retained in database
- Don't count toward visible progress percentage
- If lesson restored (future feature), progress reappears

---

### 5.4 Navigation Edge Cases

**EC-14: Previous on first lesson of first module**
- Button disabled and grayed out
- Tooltip: "This is the first lesson"

**EC-15: Next on last lesson of last module**
- Button disabled and grayed out
- Tooltip: "This is the last lesson"

**EC-16: Next on last lesson of Module 1**
- Navigates to first lesson of Module 2
- Button label: "Next: Module 2" (shows module name)

**EC-17: Previous on first lesson of Module 2**
- Navigates to last lesson of Module 1
- Button label: "Previous: Module 1"

**EC-18: Module reordered while member viewing lesson**
- Current lesson view unaffected
- On Next/Previous, uses new module order
- Breadcrumb updates on navigation

---

### 5.5 Video Embed Edge Cases

**EC-19: Invalid YouTube URL format**
- Validation error on save: "Invalid YouTube URL. Example: https://www.youtube.com/watch?v=..."
- Form stays open, user can correct

**EC-20: Valid Vimeo URL, but video is private**
- Lesson saves successfully (URL is valid)
- On lesson view, video player shows "This video is private"
- Fallback message: "Unable to load video. Contact the instructor."

**EC-21: Valid Loom URL, but video is deleted**
- Lesson saves successfully
- On lesson view, player shows error
- Fallback message with "Report issue" link

**EC-22: Video URL that doesn't match any supported platform**
- Validation error: "Only YouTube, Vimeo, and Loom videos are supported"
- Form stays open for correction

**EC-23: Text lesson with video URL pasted in rich text**
- URL appears as clickable link (not embedded)
- Opens in new tab when clicked
- Not validated as video embed

---

### 5.6 Reordering Edge Cases

**EC-24: Drag module to same position**
- No change, no API call
- Visual feedback: Module returns to original position

**EC-25: Drag module, then release outside drop zone**
- Module returns to original position
- No save

**EC-26: Admin reorders modules while member viewing lesson**
- Member's current view unaffected
- On navigation (Next/Previous), new order applies
- Course overview page refreshes to show new order

**EC-27: Two admins reorder modules simultaneously**
- Last write wins (no conflict resolution in MVP)
- Both see the final order after refresh
- Future: Optimistic locking with version field

---

### 5.7 Concurrent Edit Scenarios

**EC-28: Admin edits course while member viewing**
- Member sees old data until they refresh
- No real-time updates in MVP

**EC-29: Admin deletes lesson while member viewing it**
- Member can finish viewing current lesson
- On navigation away and back, lesson not accessible
- Progress save still works (lesson reference retained)

**EC-30: Two admins edit same lesson simultaneously**
- Last save wins
- No merge conflict resolution
- Future: Show "This lesson was modified by [Admin Name]. Reload to see changes?"

---

### 5.8 Access Control Edge Cases

**EC-31: Member tries to access admin course management URL directly**
- 403 Forbidden or redirect to course overview
- Message: "You don't have permission to edit courses"

**EC-32: Admin demoted to member while editing course**
- Current edit session continues
- On save attempt, 403 error
- Message: "Your permissions have changed. Refresh to continue."

**EC-33: Unauthenticated user accesses course URL**
- Redirect to login page
- After login, redirect back to course

---

## 6. Security Requirements

### 6.1 Authentication

- All Classroom pages and API endpoints require valid authentication
- JWT token must be present and not expired
- Expired tokens rejected with redirect to login

---

### 6.2 Authorization

**Role Verification:**
- Admin actions (create, edit, delete courses/modules/lessons) require admin role
- Verify role on every admin API request, not just UI checks
- Members can view content and track their own progress only

**Progress Isolation:**
- Members can only view and modify their own progress
- API requests must verify user ID matches the authenticated user
- Cannot view or modify other members' progress

**Course Visibility:**
- All non-deleted courses visible to authenticated members
- Deleted courses only visible to admins (in management view)

---

### 6.3 Input Validation

**All user input sanitized and validated:**

**Text Fields:**
- Titles: 2-200 characters, strip leading/trailing whitespace
- Descriptions: Max lengths enforced (course: 2000, module: 1000)
- No HTML tags in titles or descriptions (escaped or stripped)

**Rich Text Content:**
- Sanitize HTML to prevent XSS
- Allow only safe tags: `<p>`, `<h1>`-`<h6>`, `<strong>`, `<em>`, `<ul>`, `<ol>`, `<li>`, `<a>`, `<code>`, `<pre>`
- Strip `<script>`, `<iframe>`, `<object>`, event handlers (`onclick`, etc.)
- Validate link URLs (only http/https protocols allowed)

**Video URLs:**
- Must match YouTube, Vimeo, or Loom URL patterns
- Only HTTPS URLs accepted
- Reject URLs with suspicious characters or patterns

**Cover Image URLs:**
- Must be valid HTTPS URLs
- Validated on backend (not just frontend)

---

### 6.4 Data Protection

**Soft Delete:**
- Courses, modules, and lessons soft-deleted (flagged, not removed)
- Allows audit trail and potential restoration
- Progress always retained (even for deleted content)

**Personal Data:**
- Progress data associated with user ID
- If user account deleted, progress data must be deleted or anonymized (GDPR compliance)

**Rate Limiting:**
- Limit course creation: 10 courses per hour per admin (prevent spam)
- Limit lesson creation: 100 lessons per hour per admin
- Limit progress updates: 1000 per hour per member (generous, prevents abuse)

---

### 6.5 Content Security

**XSS Prevention:**
- All user-generated content (course descriptions, lesson content) sanitized
- Rich text editor output sanitized server-side (don't trust client)
- Video embeds use iframe sandbox attributes when possible

**CSRF Protection:**
- All state-changing operations (POST, PUT, DELETE) require CSRF token
- Token validated on server

**Iframe Embedding:**
- Video embeds use Content Security Policy to restrict capabilities
- Only YouTube, Vimeo, Loom domains allowed in iframe src

---

## 7. Out of Scope

The following features are explicitly **NOT** included in this version:

### 7.1 Not in MVP

| Feature | Reason | Future Phase |
|---------|--------|--------------|
| Native video upload | Requires S3/CDN integration, transcoding, significant storage costs | Phase 2 |
| PDF/document attachments | Requires file storage, viewer, download management | Phase 2 |
| Audio lessons | Similar to video, but less common use case | Phase 3 |
| External link content type | Simplicity - embeds cover most use cases | Phase 2 |
| Quiz/assessment lessons | Significant complexity, scoring, analytics | Phase 3 |
| Certificates on completion | Requires design, generation, verification system | Phase 3 |
| Lesson prerequisites/locks | Free navigation is simpler, more flexible for MVP | Phase 3 |
| Drip content (scheduled release) | Requires scheduler, time-based unlocking | Phase 2 |
| Discussion threads per lesson | Requires Community context integration | Phase 2 |
| Downloadable resources | Requires file storage, management | Phase 2 |
| Video transcripts/captions | Requires video processing or external API | Phase 3 |
| Automatic progress tracking | Requires video player integration, watch time tracking | Phase 3 |
| Lesson notes (member annotations) | Nice-to-have, adds complexity | Phase 3 |
| Course categories/tags | Simple list view sufficient for MVP | Phase 2 |
| Course search/filtering | Overkill for small course libraries | Phase 2 |
| Course bookmarks | Low priority for MVP | Phase 3 |
| Course ratings/reviews | Community feature, better in Phase 2 | Phase 2 |

### 7.2 Admin Features (Phase 2+)

| Feature | Reason | Future Phase |
|---------|--------|--------------|
| Course duplication | Convenience feature, not critical | Phase 3 |
| Bulk lesson import | Nice-to-have for admins | Phase 3 |
| Lesson templates | Low value for MVP | Phase 3 |
| Course analytics | Views, completion rates, drop-off points | Phase 2 |
| Draft mode (unpublished courses) | Publish/unpublish adds complexity | Phase 2 |
| Instructor collaboration | Multi-instructor courses | Phase 3 |
| Course versioning | Track changes, rollback | Phase 3 |

### 7.3 Gating & Monetization (Phase 2+)

| Feature | Reason | Future Phase |
|---------|--------|--------------|
| Level-gating | Requires Gamification context | Phase 2 |
| Payment-gated courses | Requires Membership/Payment context | Phase 2 |
| Subscription tiers | Requires Membership context | Phase 2 |
| Course bundles | Requires payment system | Phase 3 |

---

## 8. Success Metrics

### 8.1 Engagement Metrics

| Metric | Measurement | Target |
|--------|-------------|--------|
| Course start rate | % of members who start at least 1 course | > 40% within 30 days |
| Course completion rate | % of course starters who complete | > 25% |
| Lesson completion rate | % of lesson views that result in mark complete | > 60% |
| Average lessons per session | Lessons viewed per learning session | 3-5 |
| 7-day return rate | % of course starters who return within 7 days | > 50% |
| "Continue" usage | % of course navigation using "Continue" vs manual | > 70% |

### 8.2 Content Quality Metrics

| Metric | Measurement | Target |
|--------|-------------|--------|
| Average course size | Lessons per course | 10-20 |
| Average lesson length | Characters (text) or duration (video) | Text: 500-2000 chars, Video: 5-15 min |
| Module organization | Modules per course | 3-7 |
| Course deletion rate | % of courses deleted by admins within 30 days | < 10% |
| Lesson skip rate | % of lessons skipped (not viewed) | < 30% |

### 8.3 Technical Metrics

| Metric | Measurement | Target |
|--------|-------------|--------|
| Course list load time | Time to display course cards | < 800ms (p95) |
| Lesson load time | Time to render lesson content | < 1s (p95) |
| Progress save latency | Time from mark complete to confirmation | < 300ms (p95) |
| Video embed success rate | % of video lessons that load successfully | > 95% |
| Error rate | % of API requests failing | < 1% |

---

## 9. Dependencies

### 9.1 Upstream Dependencies (Required)

**Identity Context:** ✅ Complete
- User authentication (JWT tokens)
- User IDs for instructor and progress tracking
- User display names and avatars for instructor display
- Role verification (admin vs member)

**Infrastructure:**
- PostgreSQL database (for courses, modules, lessons, progress)
- Domain event bus (for publishing LessonCompleted, CourseCompleted events)

**External Services:**
- YouTube, Vimeo, Loom (for video embeds) - no API integration required, just iframe embedding

---

### 9.2 Downstream Consumers (Future)

**Gamification Context (Phase 2):**
- Consumes `LessonCompleted` event → Award points to member
- Consumes `CourseCompleted` event → Award bonus points, achievement badge
- Uses completion data for leaderboards

**Notification Context (Phase 2):**
- Consumes `CourseCompleted` event → Send congratulations notification
- Consumes `CourseCreated` event → Notify members of new course
- Consumes `ModuleAdded` event → Notify enrolled members of new content

**Community Context (Phase 2):**
- Course announcements appear in feed
- Lesson-specific discussion threads
- "Share my completion" posts

---

## 10. Open Questions

1. **Rich text editor: Which library?**
   - Decision deferred to TDD phase
   - Options: TipTap, Quill, Slate, Lexical
   - Must support sanitization and safe HTML output

2. **Progress auto-save: On what triggers?**
   - Proposal: Auto-mark complete when member reaches end of text lesson or finishes video
   - Decision: Manual marking only for MVP (simpler, clearer user control)

3. **Video embeds: Sandbox restrictions?**
   - Decision deferred to TDD phase
   - Consider iframe sandbox attributes for security

4. **Course image hosting: Allow uploads or URLs only?**
   - Decision: URLs only for MVP (no file upload/storage needed)
   - Phase 2: Add native image uploads

5. **Lesson timing: Track actual time spent?**
   - Decision: No for MVP (requires analytics infrastructure)
   - Phase 2: Add time tracking for engagement metrics

6. **Course visibility: Public preview for non-members?**
   - Decision: No for MVP (members-only)
   - Phase 2: Add public course previews for marketing

---

## 11. Appendix

### 11.1 Related Documents

- `docs/OVERVIEW_PRD.md` - Master product roadmap
- `docs/domain/GLOSSARY.md` - Ubiquitous language definitions
- `docs/architecture/CONTEXT_MAP.md` - Bounded context relationships
- `tests/features/classroom/*.feature` - BDD specifications for this feature
- `docs/features/classroom/classroom-tdd.md` - Technical Design Document (to be created)

### 11.2 Design References

- Skool.com classroom UI (inspiration)
- Teachable course player (best practices)
- Thinkific module/lesson structure (reference)

### 11.3 Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-07 | Claude | Initial draft with technical details |
| 2.0 | 2026-02-07 | Claude | Rewritten to match Feed PRD style: product-focused, removed technical implementation details |

---

## 12. Approval

**Product Owner:** _________________
**Date:** __________

**Engineering Lead:** _________________
**Date:** __________

**Design Lead:** _________________
**Date:** __________

**Status:** Draft - Pending Review
