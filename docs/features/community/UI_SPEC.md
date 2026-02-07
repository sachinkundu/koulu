# Community Feed - UI Specification

*Generated from Skool.com screenshots on 2026-02-07*

---

## Visual References

- **Screenshot 1:** `community_feed.png` - Main feed view with posts, category filter, and sidebar
- **Screenshot 2:** `community_new_post.png` - Create post modal with category dropdown
- **Screenshot 3:** `community_post_upon_clicking.png` - Post detail view with full content and comments
- **Screenshot 4:** `community_sorting_posts.png` - Sort dropdown menu (Default/New/Top/Pinned)
- **Screenshot 5:** `community_focus_comments.png` - Comments section with threaded replies and interactions
- **Screenshot 6:** `community_create_post_profile.png` - User profile dropdown menu

---

## Layout Structure

### Desktop (>768px)

```
┌─────────────────────────────────────────────────────────────┐
│                    Header (60px, fixed)                      │
│  [Logo] Community Classroom Calendar Members Map...  [User]  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────┬────────────────────────┬──────────────┐ │
│  │ Category Pills │                        │              │ │
│  │ (sidebar-like  │   Main Feed Area       │   Sidebar    │ │
│  │  but inline)   │                        │   (360px)    │ │
│  │                │  [Write something...]  │              │ │
│  │  All           │                        │  [Promo Card]│ │
│  │  General       │  [Post Card 1]         │              │ │
│  │  Q&A           │  [Post Card 2]         │  Community   │ │
│  │  Roast 🔥      │  [Post Card 3]         │  Info        │ │
│  │  Wins          │  ...                   │              │ │
│  │  Tools & Res   │                        │  692 Members │ │
│  │  Meet & Greet  │                        │  4 Online    │ │
│  │  More...       │                        │  12 Admins   │ │
│  │                │                        │              │ │
│  └────────────────┴────────────────────────┴──────────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘

Container: max-w-[1100px] mx-auto px-4
Grid: 3-column flexible layout
- Category Pills: inline horizontal scroll on mobile, vertical list on tablet+
- Main Feed: ~60% width, flex-1
- Sidebar: 360px fixed width
Gap: 24px (gap-6)
```

### Mobile (<768px)

```
┌──────────────────────┐
│      Header          │
├──────────────────────┤
│ [Category Pills]     │
│ (horizontal scroll)  │
├──────────────────────┤
│ [Write something...] │
├──────────────────────┤
│ [Post Card 1]        │
├──────────────────────┤
│ [Post Card 2]        │
├──────────────────────┤
│ ...                  │
└──────────────────────┘

Sidebar moves to bottom or separate tab
Categories become horizontal scrollable pills
```

---

## Component Specifications

### 1. FeedPostCard

**Screenshot reference:** `community_feed.png` - Post cards in main feed

**Purpose:** Display a post summary in the feed with author info, engagement metrics, and preview of content

**Structure:**

```tsx
<article className="bg-white border border-gray-200 rounded-lg p-4 mb-4 hover:shadow-sm transition-shadow">
  {/* Header: Author info */}
  <header className="flex items-start gap-3 mb-3">
    <img
      src={author.avatar}
      alt={author.name}
      className="w-10 h-10 rounded-full"
    />
    <div className="flex-1 min-w-0">
      <div className="flex items-center gap-2">
        <h3 className="font-semibold text-gray-900 text-base">
          {author.display_name}
        </h3>
        {author.verified && (
          <svg className="w-4 h-4 text-blue-500">✓</svg>
        )}
      </div>
      <p className="text-sm text-gray-600">
        {category.name} · {timeAgo}
      </p>
    </div>
    {isPinned && (
      <span className="flex items-center gap-1 text-sm text-gray-700">
        📌 Pinned
      </span>
    )}
  </header>

  {/* Content */}
  <div className="mb-3">
    <h2 className="font-bold text-lg text-gray-900 mb-2 cursor-pointer hover:text-blue-600">
      {post.title}
    </h2>
    <p className="text-gray-700 text-base line-clamp-3">
      {post.content}
    </p>
    {isTruncated && (
      <button className="text-blue-600 text-sm hover:underline">
        See more
      </button>
    )}
  </div>

  {/* Image (if present) */}
  {post.image_url && (
    <div className="mb-3 rounded-lg overflow-hidden">
      <img
        src={post.image_url}
        alt="Post attachment"
        className="w-full h-auto max-h-96 object-cover"
      />
    </div>
  )}

  {/* Engagement Footer */}
  <footer className="flex items-center gap-4 pt-3 border-t border-gray-100">
    <button className="flex items-center gap-1.5 text-gray-600 hover:text-blue-600 transition-colors">
      <span className="text-lg">👍</span>
      <span className="text-sm font-medium">{likeCount}</span>
    </button>

    <button className="flex items-center gap-1.5 text-gray-600 hover:text-blue-600 transition-colors">
      <svg className="w-5 h-5">💬</svg>
      <span className="text-sm font-medium">{commentCount}</span>
    </button>

    {/* Avatars of likers */}
    <div className="ml-auto flex -space-x-2">
      {likers.slice(0, 5).map(liker => (
        <img
          key={liker.id}
          src={liker.avatar}
          className="w-6 h-6 rounded-full border-2 border-white"
          title={liker.name}
        />
      ))}
      {likers.length > 5 && (
        <span className="text-xs text-gray-600 ml-2">
          +{likers.length - 5} more
        </span>
      )}
    </div>

    {isEdited && (
      <span className="text-xs text-gray-500">(edited)</span>
    )}
  </footer>
</article>
```

**Design tokens used:**
- Card background: `bg-white`
- Border: `border-gray-200` (subtle)
- Hover: `hover:shadow-sm`
- Spacing: `p-4`, `mb-4`, `gap-3`, `gap-4`
- Text colors: `text-gray-900` (primary), `text-gray-600` (secondary), `text-gray-500` (muted)
- Border radius: `rounded-lg` (8px)
- Avatar: `w-10 h-10 rounded-full`

**Interactive states:**
- **Hover:** Card gets subtle shadow (`hover:shadow-sm`)
- **Title hover:** Text color changes to blue (`hover:text-blue-600`)
- **Button hover:** Icon/text color changes to blue
- **Click title/content:** Navigate to post detail view
- **Click like:** Optimistic update, fill icon, increment count
- **Click comment icon:** Navigate to post detail, scroll to comments

**Empty state:** (Feed level) "No posts yet. Be the first to post!"

**Loading state:** Skeleton version with gray rectangles

**Existing pattern reference:** None - new pattern (but can reference card layout from `ProfileSetupForm`)

---

### 2. CategoryTabs

**Screenshot reference:** `community_feed.png` - Horizontal category pills below "Write something"

**Purpose:** Filter feed by category and show active category

**Structure:**

```tsx
<nav className="flex gap-2 overflow-x-auto pb-2 mb-4 scrollbar-hide">
  <button
    className={cn(
      "px-4 py-2 rounded-full whitespace-nowrap text-sm font-medium transition-colors",
      isActive
        ? "bg-gray-900 text-white"
        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
    )}
    onClick={() => filterByCategory(null)}
  >
    All
  </button>

  {categories.map(category => (
    <button
      key={category.id}
      className={cn(
        "px-4 py-2 rounded-full whitespace-nowrap text-sm font-medium transition-colors flex items-center gap-1.5",
        category.slug === activeCategory
          ? "bg-gray-900 text-white"
          : "bg-gray-100 text-gray-700 hover:bg-gray-200"
      )}
      onClick={() => filterByCategory(category.slug)}
    >
      {category.emoji && <span>{category.emoji}</span>}
      {category.name}
      <span className="text-xs opacity-75">({category.post_count})</span>
    </button>
  ))}

  <button className="px-4 py-2 rounded-full bg-gray-100 text-gray-700 hover:bg-gray-200">
    More...
  </button>
</nav>
```

**Design tokens used:**
- Active: `bg-gray-900 text-white`
- Inactive: `bg-gray-100 text-gray-700`
- Hover: `hover:bg-gray-200`
- Spacing: `px-4 py-2`, `gap-2`
- Border radius: `rounded-full` (pill shape)
- Typography: `text-sm font-medium`

**Interactive states:**
- **Inactive:** Gray background, dark text
- **Hover (inactive):** Lighter gray background
- **Active:** Black background, white text
- **Click:** Update active state, filter feed, update URL query param

**Mobile behavior:** Horizontal scroll with hidden scrollbar (`overflow-x-auto scrollbar-hide`)

**Existing pattern reference:** Similar to tab navigation, new pill-based implementation

---

### 3. CreatePostInput

**Screenshot reference:** `community_feed.png` - "Write something..." input at top of feed

**Purpose:** Quick access to create post modal

**Structure:**

```tsx
<div className="bg-white border border-gray-200 rounded-lg p-4 mb-4">
  <div className="flex gap-3">
    <img
      src={currentUser.avatar}
      alt={currentUser.name}
      className="w-10 h-10 rounded-full"
    />
    <button
      onClick={openCreatePostModal}
      className="flex-1 text-left px-4 py-2.5 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-600 text-sm transition-colors"
    >
      Write something...
    </button>
  </div>
</div>
```

**Design tokens used:**
- Card: `bg-white border border-gray-200 rounded-lg`
- Input mimic: `bg-gray-100 rounded-full`
- Hover: `hover:bg-gray-200`
- Text: `text-gray-600`

**Interactive states:**
- **Hover:** Background lightens
- **Click:** Opens CreatePostModal

**Existing pattern reference:** Similar to input fields in `ProfileSetupForm`, but styled as button

---

### 4. CreatePostModal

**Screenshot reference:** `community_new_post.png` - Modal with form fields

**Purpose:** Full form for creating a new post with title, content, category, and optional image

**Structure:**

```tsx
<div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
  <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
    {/* Header */}
    <header className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <img src={user.avatar} className="w-10 h-10 rounded-full" />
        <div>
          <p className="font-semibold text-gray-900">{user.display_name}</p>
          <p className="text-sm text-gray-600">posting in {community.name}</p>
        </div>
      </div>
      <button
        onClick={onClose}
        className="text-gray-500 hover:text-gray-700"
      >
        ✕
      </button>
    </header>

    {/* Form */}
    <form className="p-6 space-y-4">
      {/* Title Input */}
      <div>
        <input
          type="text"
          placeholder="Title"
          className="w-full text-2xl font-bold border-none outline-none placeholder-gray-400"
          maxLength={200}
        />
        <p className="text-xs text-gray-500 text-right mt-1">
          {titleLength}/200
        </p>
      </div>

      {/* Content Textarea */}
      <div>
        <textarea
          placeholder="Write something..."
          className="w-full min-h-[200px] text-base border-none outline-none resize-none placeholder-gray-400"
          maxLength={5000}
        />
        <p className="text-xs text-gray-500 text-right mt-1">
          {contentLength}/5000
        </p>
      </div>

      {/* Image URL Input (if provided) */}
      {showImageInput && (
        <div className="border border-gray-200 rounded-lg p-4">
          <input
            type="url"
            placeholder="https://..."
            className="w-full text-sm border-none outline-none"
          />
          {imagePreview && (
            <img src={imagePreview} className="mt-3 rounded-lg max-h-64" />
          )}
        </div>
      )}

      {/* Toolbar */}
      <div className="flex items-center gap-3 pt-4 border-t border-gray-200">
        <button type="button" className="p-2 hover:bg-gray-100 rounded-lg">
          📎
        </button>
        <button type="button" className="p-2 hover:bg-gray-100 rounded-lg">
          🔗
        </button>
        <button type="button" className="p-2 hover:bg-gray-100 rounded-lg">
          📹
        </button>
        <button type="button" className="p-2 hover:bg-gray-100 rounded-lg">
          📊
        </button>
        <button type="button" className="p-2 hover:bg-gray-100 rounded-lg">
          😀
        </button>
        <button type="button" className="p-2 hover:bg-gray-100 rounded-lg">
          GIF
        </button>

        {/* Category Dropdown */}
        <div className="ml-auto relative">
          <button
            type="button"
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium"
          >
            <span>{selectedCategory.emoji}</span>
            <span>Select a category</span>
            <span>▼</span>
          </button>

          {/* Dropdown menu */}
          {isDropdownOpen && (
            <div className="absolute right-0 mt-2 w-56 bg-white border border-gray-200 rounded-lg shadow-lg py-2 z-10">
              {categories.map(cat => (
                <button
                  key={cat.id}
                  type="button"
                  className="w-full text-left px-4 py-2 hover:bg-gray-100 flex items-center gap-2"
                  onClick={() => selectCategory(cat)}
                >
                  <span>{cat.emoji}</span>
                  <span className="text-sm">{cat.name}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </form>

    {/* Footer */}
    <footer className="sticky bottom-0 bg-white border-t border-gray-200 px-6 py-4 flex gap-3 justify-end">
      <button
        type="button"
        onClick={onClose}
        className="px-6 py-2.5 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
      >
        CANCEL
      </button>
      <button
        type="submit"
        disabled={!isValid || isSubmitting}
        className="px-6 py-2.5 bg-gray-900 hover:bg-gray-800 disabled:bg-gray-300 text-white rounded-lg text-sm font-medium"
      >
        {isSubmitting ? 'POSTING...' : 'POST'}
      </button>
    </footer>
  </div>
</div>
```

**Design tokens used:**
- Modal overlay: `bg-black/50`
- Modal card: `bg-white rounded-lg`
- Border: `border-gray-200`
- Input style: Borderless, large placeholder text
- Primary button: `bg-gray-900 text-white`
- Secondary button: `border border-gray-300`
- Disabled: `bg-gray-300`

**Interactive states:**
- **Typing:** Character count updates in real-time
- **Category select:** Dropdown opens below button
- **Image URL:** Preview appears below input
- **Submit disabled:** When title/content empty or exceeds limits
- **Submitting:** Button shows spinner, form disabled

**Validation:**
- Title: Required, 1-200 chars
- Content: Required, 1-5000 chars
- Image URL: Optional, must be HTTPS
- Category: Required, defaults to "General"

**Existing pattern reference:** Similar to form patterns in `RegisterForm`, `LoginForm`, but in modal format

---

### 5. PostDetailView

**Screenshot reference:** `community_post_upon_clicking.png` - Full post with comments

**Purpose:** Display complete post content with all metadata, engagement stats, and comments section

**Structure:**

```tsx
<div className="max-w-3xl mx-auto">
  {/* Post Card */}
  <article className="bg-white border border-gray-200 rounded-lg p-6 mb-4">
    {/* Header */}
    <header className="flex items-start justify-between mb-4">
      <div className="flex items-start gap-3">
        <img src={author.avatar} className="w-12 h-12 rounded-full" />
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-gray-900">{author.display_name}</h3>
            {author.verified && <span>✓</span>}
          </div>
          <p className="text-sm text-gray-600">{timeAgo}</p>
        </div>
      </div>

      <button className="p-2 hover:bg-gray-100 rounded-lg">
        ⋯
      </button>
    </header>

    {/* Content */}
    <div className="mb-4">
      <h1 className="text-2xl font-bold text-gray-900 mb-3">
        {post.title}
      </h1>
      <div className="text-base text-gray-700 leading-relaxed whitespace-pre-wrap">
        {post.content}
      </div>
    </div>

    {/* Image */}
    {post.image_url && (
      <div className="mb-4 rounded-lg overflow-hidden">
        <img src={post.image_url} className="w-full h-auto" />
      </div>
    )}

    {/* Engagement Stats */}
    <div className="flex items-center gap-4 py-3 border-y border-gray-200 mb-4">
      <button
        className={cn(
          "flex items-center gap-2 px-4 py-2 rounded-lg transition-colors",
          userLiked
            ? "bg-blue-50 text-blue-600"
            : "bg-gray-100 text-gray-700 hover:bg-gray-200"
        )}
      >
        <span className="text-lg">{userLiked ? '👍' : '👍'}</span>
        <span className="font-medium text-sm">{likeCount}</span>
      </button>

      <div className="flex items-center gap-2">
        <span className="text-gray-700 font-medium text-sm">
          💬 {commentCount} comments
        </span>
      </div>
    </div>

    {/* Likers */}
    {likers.length > 0 && (
      <div className="flex items-center gap-2 mb-4">
        <div className="flex -space-x-2">
          {likers.slice(0, 5).map(liker => (
            <img
              key={liker.id}
              src={liker.avatar}
              className="w-8 h-8 rounded-full border-2 border-white"
            />
          ))}
        </div>
        <p className="text-sm text-gray-600">
          {likers.length > 5
            ? `${likers.slice(0, 2).map(l => l.name).join(', ')} and ${likers.length - 2} others`
            : likers.map(l => l.name).join(', ')
          }
        </p>
      </div>
    )}
  </article>

  {/* Comments Section */}
  <CommentsSection postId={post.id} />
</div>
```

**Design tokens used:**
- Same as FeedPostCard but larger padding (`p-6`)
- Title: `text-2xl font-bold`
- Like button active: `bg-blue-50 text-blue-600`
- Like button inactive: `bg-gray-100`

**Interactive states:**
- **Like button:** Toggle between liked/unliked states
- **Menu (⋯):** Opens dropdown with Edit/Delete/Pin/Lock options
- **Author click:** Navigate to author profile

**Existing pattern reference:** Extended version of `FeedPostCard`

---

### 6. CommentsSection

**Screenshot reference:** `community_focus_comments.png` - Comments with replies and interactions

**Purpose:** Display threaded comments with like functionality and reply capability

**Structure:**

```tsx
<div className="bg-white border border-gray-200 rounded-lg p-6">
  <h2 className="font-bold text-lg text-gray-900 mb-4">
    {commentCount} Comments
  </h2>

  {/* Comment List */}
  <div className="space-y-4">
    {comments.map(comment => (
      <div key={comment.id}>
        {/* Top-level Comment */}
        <div className="flex gap-3">
          <img src={comment.author.avatar} className="w-10 h-10 rounded-full" />

          <div className="flex-1">
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-semibold text-sm text-gray-900">
                  {comment.author.display_name}
                </span>
                <span className="text-xs text-gray-600">
                  {timeAgo} {comment.edited && '(edited)'}
                </span>
              </div>
              <p className="text-sm text-gray-800 leading-relaxed">
                {comment.content}
              </p>
            </div>

            {/* Comment Actions */}
            <div className="flex items-center gap-3 mt-2 ml-3">
              <button className="flex items-center gap-1 text-xs text-gray-600 hover:text-blue-600">
                <span>👍</span>
                <span>{comment.like_count > 0 && comment.like_count}</span>
              </button>
              <button className="text-xs text-gray-600 hover:text-blue-600 font-medium">
                Reply
              </button>
            </div>

            {/* Replies (indented) */}
            {comment.replies?.length > 0 && (
              <div className="ml-6 mt-3 space-y-3">
                {comment.replies.map(reply => (
                  <div key={reply.id} className="flex gap-3">
                    <img src={reply.author.avatar} className="w-8 h-8 rounded-full" />
                    <div className="flex-1">
                      <div className="bg-gray-50 rounded-lg p-3">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-semibold text-sm text-gray-900">
                            {reply.author.display_name}
                          </span>
                          <span className="text-xs text-gray-600">
                            {timeAgo}
                          </span>
                        </div>
                        <p className="text-sm text-gray-800">
                          <span className="text-blue-600">@{comment.author.display_name}</span>
                          {' '}{reply.content}
                        </p>
                      </div>
                      <div className="flex items-center gap-3 mt-2 ml-3">
                        <button className="flex items-center gap-1 text-xs text-gray-600 hover:text-blue-600">
                          <span>👍</span>
                          <span>{reply.like_count > 0 && reply.like_count}</span>
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    ))}

    {/* "View 5 more replies" link if collapsed */}
    <button className="text-sm text-blue-600 hover:underline ml-14">
      ↓ View 5 more replies
    </button>

    {/* Jump to latest */}
    <button className="flex items-center gap-2 mx-auto px-4 py-2 bg-white border border-gray-300 rounded-full text-sm font-medium hover:bg-gray-50">
      ↓ Jump to latest comment
    </button>
  </div>

  {/* Add Comment Form */}
  <div className="mt-6 pt-6 border-t border-gray-200">
    <div className="flex gap-3">
      <img src={currentUser.avatar} className="w-10 h-10 rounded-full" />
      <div className="flex-1">
        <textarea
          placeholder="Write a comment..."
          className="w-full p-3 border border-gray-300 rounded-lg text-sm resize-none focus:outline-none focus:border-gray-900"
          rows={3}
        />
        <div className="flex justify-end mt-2">
          <button
            className="px-6 py-2 bg-gray-900 hover:bg-gray-800 text-white rounded-lg text-sm font-medium disabled:bg-gray-300"
            disabled={!commentText.trim()}
          >
            Comment
          </button>
        </div>
      </div>
    </div>
  </div>

  {/* Locked state */}
  {isLocked && (
    <div className="text-center py-8 text-gray-600">
      🔒 Comments are disabled on this post
    </div>
  )}
</div>
```

**Design tokens used:**
- Comment bubble: `bg-gray-50 rounded-lg p-3`
- Avatar size: `w-10 h-10` (main), `w-8 h-8` (replies)
- Reply indent: `ml-6`
- Text: `text-sm` for comments, `text-xs` for meta
- Border: `border-gray-300` for inputs
- Focus: `focus:border-gray-900`

**Interactive states:**
- **Like:** Emoji fills, count increments
- **Reply click:** Opens reply input below comment
- **Submit:** Optimistic update, new comment appears
- **Load more:** Expands to show additional replies
- **Jump to latest:** Scrolls to bottom

**Threading rules:**
- Maximum 1 level deep (comment → reply only)
- Replies visually indented with smaller avatars
- Mentions highlighted in blue (`@username`)

**Existing pattern reference:** New pattern for threaded comments

---

### 7. SortDropdown

**Screenshot reference:** `community_sorting_posts.png` - Dropdown menu with sort options

**Purpose:** Allow users to change feed sort order (Default/New/Top/Pinned)

**Structure:**

```tsx
<div className="relative">
  <button
    onClick={toggleDropdown}
    className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium"
  >
    <span>⚡</span>
    <span>{activeSortLabel}</span>
    <span className="text-xs">▼</span>
  </button>

  {isOpen && (
    <div className="absolute right-0 mt-2 w-40 bg-white border border-gray-200 rounded-lg shadow-lg py-2 z-10">
      <button
        className={cn(
          "w-full text-left px-4 py-2 text-sm flex items-center gap-2",
          activeSort === 'default'
            ? "bg-yellow-50 text-gray-900 font-medium"
            : "text-gray-700 hover:bg-gray-100"
        )}
        onClick={() => setSort('default')}
      >
        <span>⚡</span>
        <span>Default</span>
      </button>

      <button
        className={cn(
          "w-full text-left px-4 py-2 text-sm flex items-center gap-2",
          activeSort === 'new' ? "bg-yellow-50 font-medium" : "hover:bg-gray-100"
        )}
        onClick={() => setSort('new')}
      >
        <span>🆕</span>
        <span>New</span>
      </button>

      <button
        className={cn(
          "w-full text-left px-4 py-2 text-sm flex items-center gap-2",
          activeSort === 'top' ? "bg-yellow-50 font-medium" : "hover:bg-gray-100"
        )}
        onClick={() => setSort('top')}
      >
        <span>🔝</span>
        <span>Top</span>
      </button>

      <button
        className={cn(
          "w-full text-left px-4 py-2 text-sm flex items-center gap-2",
          activeSort === 'pinned' ? "bg-yellow-50 font-medium" : "hover:bg-gray-100"
        )}
        onClick={() => setSort('pinned')}
      >
        <span>📌</span>
        <span>Pinned</span>
      </button>
    </div>
  )}
</div>
```

**Design tokens used:**
- Button: `bg-gray-100 hover:bg-gray-200 rounded-lg`
- Dropdown: `bg-white border border-gray-200 shadow-lg rounded-lg`
- Active item: `bg-yellow-50 font-medium`
- Hover: `hover:bg-gray-100`
- Icon size: Emoji (16px equivalent)

**Interactive states:**
- **Closed:** Shows current sort with icon
- **Open:** Dropdown appears below button
- **Active item:** Yellow highlight background
- **Hover (inactive):** Gray highlight
- **Click option:** Close dropdown, update feed

**Existing pattern reference:** Standard dropdown pattern, new implementation

---

### 8. CommunitySidebar

**Screenshot reference:** `community_feed.png` - Right sidebar with promo card and stats

**Purpose:** Display community information, member stats, and promotional content

**Structure:**

```tsx
<aside className="w-80 space-y-4 sticky top-20">
  {/* Promo Card */}
  <div className="bg-gray-800 text-white rounded-lg overflow-hidden">
    <div className="h-32 bg-gradient-to-br from-gray-700 to-gray-900 flex items-center justify-center">
      <h3 className="text-2xl font-bold italic">
        Launch and<br/>grow your<br/><span className="text-yellow-400">business</span>
      </h3>
    </div>
    <div className="p-4">
      <h4 className="font-bold text-base mb-2">{community.name}</h4>
      <p className="text-sm text-gray-300 mb-3">{community.tagline}</p>
      <p className="text-xs text-gray-400 mb-4">
        {community.description}
      </p>
      <button className="w-full bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-semibold py-2.5 rounded-lg text-sm">
        JOIN NOW
      </button>
    </div>
  </div>

  {/* Community Stats */}
  <div className="bg-white border border-gray-200 rounded-lg p-4">
    <h3 className="font-bold text-base text-gray-900 mb-3">
      {community.name}
    </h3>
    <div className="flex gap-6 mb-4">
      <div className="text-center">
        <p className="text-2xl font-bold text-gray-900">{memberCount}</p>
        <p className="text-xs text-gray-600">Members</p>
      </div>
      <div className="text-center">
        <p className="text-2xl font-bold text-gray-900">{onlineCount}</p>
        <p className="text-xs text-gray-600">Online</p>
      </div>
      <div className="text-center">
        <p className="text-2xl font-bold text-gray-900">{adminCount}</p>
        <p className="text-xs text-gray-600">Admins</p>
      </div>
    </div>

    {/* Member Avatars */}
    <div className="flex -space-x-2 mb-3">
      {topMembers.slice(0, 6).map(member => (
        <img
          key={member.id}
          src={member.avatar}
          className="w-8 h-8 rounded-full border-2 border-white"
        />
      ))}
    </div>

    <button className="w-full bg-gray-900 hover:bg-gray-800 text-white font-semibold py-2.5 rounded-lg text-sm">
      INVITE PEOPLE
    </button>
  </div>
</aside>
```

**Design tokens used:**
- Card: `bg-white border border-gray-200 rounded-lg`
- Promo dark bg: `bg-gray-800`
- Stats text: `text-2xl font-bold`
- Primary CTA: `bg-yellow-400` (brand color)
- Secondary CTA: `bg-gray-900`
- Sticky position: `sticky top-20`

**Interactive states:**
- **Hover CTA:** Darken background
- **Click member avatar:** Navigate to profile
- **Click invite:** Open invite modal

**Responsive behavior:**
- Desktop: Fixed 360px width, sticky
- Tablet: Moves below feed
- Mobile: Hidden or in separate tab

**Existing pattern reference:** Card layout similar to other white cards

---

## Color Palette Usage

From screenshots observed:

| UI Element | Screenshot Color | Tailwind Class | Design System Variable |
|------------|-----------------|----------------|------------------------|
| Page background | `#F7F9FA` | `bg-gray-50` | `--bg-page` |
| Card background | `#FFFFFF` | `bg-white` | `--bg-card` |
| Primary text | `#1D2129` | `text-gray-900` | `--text-primary` |
| Secondary text | `#65676B` | `text-gray-600` | `--text-secondary` |
| Muted text | `#B0B3B8` | `text-gray-500` | `--text-muted` |
| Borders | `#E4E6EB` | `border-gray-200` | `--border-subtle` |
| Input background | `#F0F2F5` | `bg-gray-100` | `--bg-input` |
| Hover background | `#F2F4F7` | `hover:bg-gray-200` | `--bg-hover` |
| Brand accent | `#F7B955` | `bg-yellow-400` | `--primary-brand` |
| Active state bg | `#000000` | `bg-gray-900` | Black for emphasis |
| Link/interactive | `#007AFF` | `text-blue-600` | `--text-link` |
| Like active bg | Light blue | `bg-blue-50` | New token needed |

**Note:** Current `tailwind.config.ts` uses blue/purple primary colors. Need to update to yellow/gold brand color (`#F7B955`) to match Skool design.

---

## Typography Scale

| Element | Screenshot Size | Tailwind Class | Weight | Usage |
|---------|----------------|----------------|--------|-------|
| Page heading | ~28px | `text-3xl` | `font-bold` | Page titles (not visible in feed) |
| Post title (detail) | ~24px | `text-2xl` | `font-bold` | Post detail view heading |
| Post title (card) | ~18px | `text-lg` | `font-bold` | Feed post card title |
| Card heading | ~16px | `text-base` | `font-semibold` | Component headers |
| Body text | ~15px | `text-base` | `font-normal` | Post content, comments |
| Author name | ~15px | `text-base` | `font-semibold` | User display names |
| Metadata | ~13px | `text-sm` | `font-normal` | Timestamps, category, counts |
| Button text | ~14px | `text-sm` | `font-medium` | Buttons, CTAs |
| Small text | ~12px | `text-xs` | `font-normal` | Character counts, labels |

**Font family:** System font stack (already configured as Inter in `tailwind.config.ts`)

---

## Spacing System

| Gap Type | Screenshot Measurement | Tailwind Class | Pixels |
|----------|----------------------|----------------|--------|
| Between cards | ~16px | `space-y-4` or `mb-4` | 16px |
| Card padding | ~16px | `p-4` | 16px |
| Card padding (detail) | ~24px | `p-6` | 24px |
| Section gap | ~24px | `gap-6` | 24px |
| Icon-to-text | ~8px | `gap-2` | 8px |
| Button padding | 16px × 10px | `px-4 py-2.5` | 16×10px |
| Avatar gap | ~12px | `gap-3` | 12px |
| Comment indent | ~24px | `ml-6` | 24px |
| Layout columns | ~24px | `gap-6` | 24px |

---

## Interactive Patterns

### 1. Like Button Pattern

**Where:** Post cards, post detail, comments

**Behavior:**
- Click toggles like state
- Optimistic update (immediate visual feedback)
- Like count increments/decrements
- Icon fills when liked

**Implementation:**
- Default state: `bg-gray-100 text-gray-700`
- Liked state: `bg-blue-50 text-blue-600`
- Hover: `hover:bg-gray-200` (default), `hover:bg-blue-100` (liked)
- Transition: `transition-colors`

### 2. Card Hover Pattern

**Where:** Post cards, comment replies

**Behavior:**
- Subtle shadow on hover
- Cursor changes to pointer on clickable areas

**Implementation:**
- Default: `border border-gray-200`
- Hover: `hover:shadow-sm`
- Transition: `transition-shadow`

### 3. Button States

**Primary (Post, Comment):**
- Default: `bg-gray-900 text-white`
- Hover: `hover:bg-gray-800`
- Disabled: `disabled:bg-gray-300 disabled:cursor-not-allowed`
- Active: Slight scale down

**Secondary (Cancel):**
- Default: `border border-gray-300 text-gray-700`
- Hover: `hover:bg-gray-50`

**Tertiary (Icon buttons):**
- Default: Transparent
- Hover: `hover:bg-gray-100 rounded-lg`

### 4. Dropdown Open/Close

**Where:** Sort menu, category selector, user menu

**Behavior:**
- Click button toggles dropdown
- Click outside closes dropdown
- Arrow icon rotates when open
- Active item highlighted

**Implementation:**
- Dropdown: `absolute` positioned, `shadow-lg`
- Active item: `bg-yellow-50 font-medium`
- Animation: Fade in/out with scale

### 5. Modal Open/Close

**Where:** Create post modal

**Behavior:**
- Opens centered with overlay
- Overlay click closes modal
- ESC key closes modal
- Body scroll locked when open

**Implementation:**
- Overlay: `fixed inset-0 bg-black/50 z-50`
- Modal: `rounded-lg max-w-2xl`
- Animation: Fade + slide in from top

### 6. Infinite Scroll

**Where:** Feed view

**Behavior:**
- Load more posts when scrolling near bottom
- Show loading indicator during fetch
- Smooth append (no jump)

**Implementation:**
- Intersection Observer on sentinel element
- Loading: Show skeleton cards
- Cursor-based pagination

---

## Responsive Breakpoints

| Breakpoint | Width | Layout Changes |
|------------|-------|----------------|
| Mobile | < 768px | Single column, horizontal category scroll, sidebar hidden |
| Tablet | 768px - 1023px | Two columns (feed + sidebar), vertical categories |
| Desktop | ≥ 1024px | Three columns (categories + feed + sidebar) |

**Tailwind breakpoints:**
- Use `md:` for tablet+ (768px)
- Use `lg:` for desktop (1024px)
- Default styles are mobile-first

---

## Accessibility Considerations

1. **Semantic HTML:**
   - `<article>` for posts
   - `<aside>` for sidebar
   - `<nav>` for category filters
   - `<button>` for interactive elements (not `<div>`)

2. **Focus States:**
   - All interactive elements have visible focus ring
   - Use `focus:outline-none focus:ring-2 focus:ring-gray-900`

3. **Color Contrast:**
   - Text on white: `text-gray-900` (AAA), `text-gray-600` (AA)
   - Button text on dark: White on `bg-gray-900` (AAA)
   - Link color: `text-blue-600` on white (AA)

4. **Screen Readers:**
   - Alt text for all images
   - ARIA labels for icon-only buttons
   - Live regions for optimistic updates

5. **Keyboard Navigation:**
   - Tab through all interactive elements
   - Enter/Space to activate buttons
   - ESC to close modals/dropdowns
   - Arrow keys in dropdown menus

---

## Implementation Checklist

- [ ] Update `tailwind.config.ts` to include Skool-inspired color tokens
  - [ ] Add `bg-page: '#F7F9FA'`
  - [ ] Add `bg-card: '#FFFFFF'`
  - [ ] Update primary brand to yellow (`#F7B955`)
  - [ ] Add text color variables
  - [ ] Add border color variables
- [ ] Load `ui-design` skill before coding
- [ ] Create base components first:
  - [ ] `FeedPostCard` (reusable post display)
  - [ ] `CategoryTabs` (category filter)
  - [ ] `CreatePostInput` (quick access)
  - [ ] `SortDropdown` (sort selector)
- [ ] Create complex components:
  - [ ] `CreatePostModal` (full post form)
  - [ ] `PostDetailView` (complete post page)
  - [ ] `CommentsSection` (threaded comments)
  - [ ] `CommunitySidebar` (info + stats)
- [ ] Follow mobile-first approach
- [ ] Test responsive breakpoints (mobile, tablet, desktop)
- [ ] Verify color contrast (WCAG AA minimum)
- [ ] Add focus states for keyboard navigation
- [ ] Test with screen reader
- [ ] Implement loading states (skeletons)
- [ ] Implement empty states (no posts, no comments)
- [ ] Add error handling (failed to load, failed to submit)

---

## Notes for Implementation

### Current State Analysis

**Existing in codebase:**
- Tailwind configured with Inter font ✓
- Form patterns in Identity features (RegisterForm, LoginForm) ✓
- Basic card components (can be extended) ✓

**Gaps to fill:**
- No Skool-inspired color tokens in tailwind.config.ts
- No community-specific components yet
- No threaded comment component pattern

### Design System Alignment

The screenshots show **perfect alignment** with the Skool design system outlined in `ui-design` skill:
- ✓ Card-based layout on gray background
- ✓ Soft border radius (8px)
- ✓ Minimal, clean aesthetic
- ✓ High whitespace usage
- ✓ Stroke-based icons (emojis used for category)
- ✓ Pill-shaped buttons for categories

### Key Technical Decisions

1. **Category Filter Layout:**
   - Desktop: Horizontal scrollable pills above feed (not sidebar)
   - Mobile: Same horizontal scroll, more compact
   - This differs from typical sidebar filters but matches Skool

2. **Comment Threading:**
   - Strict 1-level depth (no recursive rendering needed)
   - Use margin-left for visual indent
   - Smaller avatars for replies (10px → 8px)

3. **Optimistic Updates:**
   - Like button toggles immediately
   - Post/comment appears before API confirms
   - Revert on error with toast notification

4. **Infinite Scroll:**
   - Use cursor pagination (not offset)
   - Load trigger at 80% scroll
   - 20 posts per page

5. **State Management:**
   - Consider using React Query for feed data
   - Local state for UI (modals, dropdowns)
   - Context for current user + community

### Edge Cases to Handle

1. **Very long post titles:** Truncate in feed, show full in detail
2. **No avatar URL:** Show initials in colored circle
3. **Broken image URLs:** Show placeholder icon
4. **Empty feed:** Show empty state with CTA
5. **Locked post:** Hide comment form, show lock icon
6. **Deleted comment with replies:** Show "[deleted]" placeholder
7. **Rate limit hit:** Disable submit, show retry time
8. **Concurrent edits:** Last write wins (show edited indicator)

### Performance Considerations

1. **Virtual scrolling:** Not needed for MVP (test with 100+ posts first)
2. **Image optimization:** Use next/image or similar (lazy load, blur placeholder)
3. **Debounce search:** If adding search later
4. **Memoize components:** Expensive renders (PostCard with many likers)
5. **Code splitting:** Lazy load CreatePostModal

---

## Component Dependency Graph

```
Feed Page
├── CategoryTabs
├── CreatePostInput → CreatePostModal
├── SortDropdown
├── FeedPostCard (multiple)
│   └── (Click) → PostDetailView
│       ├── PostDetailCard
│       └── CommentsSection
│           ├── CommentItem (multiple)
│           │   └── CommentReply (multiple)
│           └── AddCommentForm
└── CommunitySidebar
    ├── PromoCard
    └── CommunityStatsCard
```

**Load order:**
1. Shared UI primitives (Button, Input, Avatar)
2. Simple components (CategoryTabs, SortDropdown)
3. Card components (FeedPostCard, CommentsSection)
4. Page layouts (FeedPage, PostDetailPage)
5. Modals (CreatePostModal)

---

**Generated:** 2026-02-07
**Analyzed:** 6 Skool.com screenshots
**Components Identified:** 8 major components
**Complexity:** Medium-High (threaded comments, optimistic updates, infinite scroll)
**Design System Alignment:** Excellent - all patterns match existing Skool aesthetic
**Reusable Components:** Form inputs, buttons, card layouts from Identity feature
**New Patterns Needed:** Threaded comments, infinite scroll feed, pill-based category filter
