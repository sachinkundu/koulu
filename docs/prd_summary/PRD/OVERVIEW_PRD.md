# Koulu - Product Requirements Document (Overview)

**Version:** 1.0  
**Last Updated:** February 5, 2026  
**Status:** Draft  
**Document Type:** Master Overview PRD

---

## 1. Executive Summary

### 1.1 Product Vision

Koulu is a community-first learning platform that combines discussion forums, structured courses, event scheduling, and gamification into a single, cohesive experience. Inspired by Skool.com, Koulu eliminates the need for creators to juggle multiple tools (Facebook Groups + Teachable + Calendly) by providing everything in one clean, distraction-free environment.

### 1.2 Mission Statement

> Enable creators, educators, and coaches to build thriving paid communities around their expertise by providing an all-in-one platform that makes engagement effortless and learning social.

### 1.3 Target Users

| User Type | Description | Primary Goals |
|-----------|-------------|---------------|
| **Community Creators** | Coaches, educators, course creators, influencers | Monetize expertise, build engaged audience, deliver courses |
| **Community Members** | Learners, enthusiasts, professionals | Learn new skills, connect with peers, access exclusive content |
| **Community Admins** | Moderators, assistants | Manage content, moderate discussions, support members |

### 1.4 Key Value Propositions

1. **Simplicity**: Clean, Facebook-like interface with zero learning curve
2. **All-in-One**: Community + Courses + Calendar + Gamification in one place
3. **Engagement**: Built-in gamification drives participation without external incentives
4. **Monetization**: Simple pricing tools for free, paid, or tiered communities

---

## 2. Product Overview

### 2.1 Core Modules

Koulu consists of six primary modules, each accessible via the main navigation:

```
┌─────────────────────────────────────────────────────────────┐
│  Community │ Classroom │ Calendar │ Members │ Map │ Leaderboards │ About │
└─────────────────────────────────────────────────────────────┘
```

| Module | Purpose | Key Features |
|--------|---------|--------------|
| **Community** | Discussion feed | Posts, comments, reactions, categories, pinning |
| **Classroom** | Course delivery | Modules, lessons, progress tracking, drip content |
| **Calendar** | Event scheduling | Events, timezone conversion, reminders |
| **Members** | Directory | Profiles, search, filtering, admin tools |
| **Map** | Geographic view | Member locations, meetup discovery |
| **Leaderboards** | Gamification | Points, levels, rankings, achievements |
| **About** | Community info | Description, links, rules, resources |

### 2.2 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Web Application                         │
│              (React + TypeScript + TailwindCSS)              │
├─────────────────────────────────────────────────────────────┤
│                        API Gateway                           │
│                    (FastAPI + Python)                        │
├─────────────────────────────────────────────────────────────┤
│  Identity  │ Community │ Classroom │ Membership │ Gamification│
│  Context   │  Context  │  Context  │   Context  │   Context   │
├─────────────────────────────────────────────────────────────┤
│                      Data Layer                              │
│              (PostgreSQL + Redis + S3)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Feature Specifications

### 3.1 Identity & Authentication

#### 3.1.1 User Registration
- Email/password registration
- Social login (Google, optional: Apple, Facebook)
- Email verification required
- Profile completion flow

#### 3.1.2 User Profile
- Display name and avatar
- Bio/description
- Social links (Twitter, LinkedIn, Instagram, website)
- Location (optional, for map feature)
- Activity feed (posts, comments)
- Stats: followers, following, contributions
- Daily activity chart

#### 3.1.3 Authentication
- Secure login with rate limiting
- Password reset via email
- Session management
- Remember me functionality

#### 3.1.4 User Settings
- Notification preferences (email, push, digest)
- Privacy settings
- Chat availability toggle
- Connected accounts

---

### 3.2 Community Module

The Community module is the heart of Koulu—a discussion feed where members interact.

#### 3.2.1 Feed

**Post Types:**
- Text posts (with rich text formatting)
- Image posts (single or multiple)
- Video posts (embedded or native)
- Link posts (with preview cards)
- Poll posts

**Post Features:**
- Title (optional)
- Body content with formatting
- Category assignment
- Attachments (images, files)
- Mentions (@username)
- Edit and delete (author/admin)

**Post Metadata:**
- Author info (name, avatar, level badge)
- Timestamp (relative: "3h ago")
- Category tag
- Pin indicator (for admin-pinned posts)
- Like count
- Comment count
- Last activity indicator

#### 3.2.2 Categories

Categories organize posts into topics. Examples from Skool:
- All (default view)
- General
- Q&A
- Wins
- Roast 🍖
- Tools & Resources
- Meet & Greet
- More... (expandable)

**Category Features:**
- Admin-defined categories
- Custom names and emojis
- Filter feed by category
- Category-specific posting rules (optional)

#### 3.2.3 Comments & Replies

- Threaded comments (single level nesting)
- Rich text in comments
- Reactions on comments
- Edit/delete own comments
- Mention other users
- "New comment" indicator on posts

#### 3.2.4 Reactions

- Like button (primary reaction)
- Like count displayed
- Likers list viewable
- 1 like = 1 point for post/comment author

#### 3.2.5 Post Actions

**For Authors:**
- Edit post
- Delete post
- Pin to profile

**For Admins:**
- Pin/unpin post
- Lock comments
- Move to category
- Delete post
- Ban user + delete recent activity

**For Members:**
- Like/unlike
- Comment
- Follow thread (bell icon)
- Report to admins

#### 3.2.6 Feed Algorithms

**Sorting Options:**
- Hot (engagement-weighted recency)
- New (chronological)
- Top (most liked, time-filtered)

**Special Sections:**
- Pinned posts (always at top)
- Upcoming event banner (e.g., "Vibe Coding Coaching is happening in 12 hours")

#### 3.2.7 Search

- Full-text search across posts and comments
- Search within categories
- Filter by date range
- Results show post snippets with highlighted matches

---

### 3.3 Classroom Module

The Classroom delivers structured learning content.

#### 3.3.1 Course Structure

```
Community
└── Course
    └── Module
        └── Lesson
            ├── Content (video, text, files)
            └── Discussion (optional)
```

#### 3.3.2 Course Card (List View)

Each course displays:
- Cover image/thumbnail
- Title
- Description (truncated)
- Progress bar (X% complete)
- Lock indicator (if level-gated)
- "Unlock in X days" (if drip-scheduled)

#### 3.3.3 Course Features

**Course Metadata:**
- Title and description
- Cover image
- Instructor(s)
- Estimated duration
- Access requirements (level, payment)

**Course Settings (Admin):**
- Drip schedule (release content over time)
- Level-lock (require minimum level to access)
- Visibility (all members vs. paid tiers)

#### 3.3.4 Module Features

- Title and description
- Ordered lessons
- Collapse/expand view
- Module-level completion tracking

#### 3.3.5 Lesson Features

**Content Types:**
- Video (native upload or embed: YouTube, Vimeo, Loom)
- Text/Rich content (formatted text, images)
- PDF/Document attachments
- External links

**Lesson Features:**
- Mark as complete (manual)
- Searchable transcripts (for video)
- Linked discussion thread (optional)
- Previous/Next navigation

#### 3.3.6 Progress Tracking

- Per-lesson completion status
- Per-module completion percentage
- Per-course completion percentage
- Visual progress bar on course cards
- "Continue where you left off" functionality

---

### 3.4 Calendar Module

The Calendar manages community events.

#### 3.4.1 Event Types

- Live calls (Zoom, Google Meet, etc.)
- Webinars
- Q&A sessions
- In-person meetups
- Product launches
- Deadlines

#### 3.4.2 Event Features

**Event Details:**
- Title
- Date and time
- Duration (optional)
- Description
- External link (Zoom link, registration page)
- Host information

**Timezone Handling:**
- Events stored in UTC
- Displayed in member's local timezone
- "Add to calendar" export (Google, iCal, Outlook)

**Reminders:**
- Email reminder 24 hours before
- In-app notification
- Banner on Community feed ("Event happening in X hours")

#### 3.4.3 Calendar Views

- Month view (traditional calendar grid)
- List view (upcoming events chronologically)
- Past events archive

---

### 3.5 Members Module

The Members module provides a directory of all community members.

#### 3.5.1 Member List

**Display:**
- Grid or list view
- Avatar, name, level badge
- Short bio
- Join date
- Online status indicator

**Sorting:**
- Alphabetical
- Most recent
- Most active
- Level (highest first)

**Filtering:**
- By role (Admin, Moderator, Member)
- By level
- By online status
- Search by name

#### 3.5.2 Member Profile View

- Full profile information
- Activity feed (recent posts/comments)
- Stats (posts, comments, likes received)
- Mutual connections (optional)
- "Message" button (DM)
- "Follow" button

#### 3.5.3 Admin Tools

- Invite members (email, link, CSV import)
- Approve/reject membership requests
- Assign roles (Admin, Moderator)
- Ban/remove members
- View membership question answers

---

### 3.6 Map Module

The Map shows geographic distribution of members.

#### 3.6.1 Features

- World map with member pins
- Clustered markers for dense areas
- Click to see members in area
- Member cards on hover/click
- Filter by level or other criteria

#### 3.6.2 Privacy

- Location is optional (member opt-in)
- City-level precision only (not exact address)
- Members can update/remove location anytime

---

### 3.7 Leaderboards Module

Leaderboards drive engagement through gamification.

#### 3.7.1 Points System

- Members earn points when others like their posts or comments
- 1 like = 1 point for the content author
- Points accumulate over time

#### 3.7.2 Levels

- 9 levels (1-9)
- Level displayed as badge on avatar
- Custom level names (admin-configurable)
  - Example: Level 1 = "Newbie", Level 9 = "Legend"
- Level-up thresholds (configurable points per level)

#### 3.7.3 Leaderboard Views

**Time Periods:**
- 7-day (weekly)
- 30-day (monthly)
- All-time

**Display:**
- Rank position
- Member avatar and name
- Points earned (in period)
- Level badge
- Point change indicator (+X)

#### 3.7.4 Level-Based Unlocks

Admins can gate features by level:
- Course access (unlock at level X)
- Chat access (unlock at level X)
- Posting privileges
- Custom rewards

---

### 3.8 About Module

The About page provides community information.

#### 3.8.1 Content

- Community name and tagline
- Description/mission
- Cover image
- Admin/creator profiles
- Community links (website, social, resources)
- Rules/guidelines

#### 3.8.2 Sidebar Widget

Displayed on Community feed:
- Community branding (logo, cover)
- Tagline/description
- Stats (members, online, admins)
- Quick links
- "Invite People" button (for members)

---

### 3.9 Direct Messaging (Chat)

Private 1-on-1 communication between members.

#### 3.9.1 Features

- Real-time messaging
- Message history
- Read receipts (optional)
- Typing indicators
- Image/file sharing in chat
- Emoji support

#### 3.9.2 Access Control

- Chat can be level-gated (e.g., level 3+ to message)
- Members can disable incoming DMs
- Block/report functionality

#### 3.9.3 Auto-DM

- Admin-configured welcome message
- Sent automatically to new members (1-5 min after joining)
- One-time only (no re-send if conversation exists)

---

### 3.10 Notifications

#### 3.10.1 Notification Types

**In-App:**
- New follower
- Like on post/comment
- Comment on your post
- Reply to your comment
- Mention (@you)
- Event reminder
- New member (admin)
- Membership request (admin)
- Reported content (admin)

**Email:**
- Digest (popular posts summary)
- Notification summary (unread activity)
- Admin announcements
- Event reminders (24h before)

#### 3.10.2 Notification Preferences

- Per-notification-type toggle
- Email frequency (instant, daily, weekly, off)
- Per-community settings

---

### 3.11 Search

#### 3.11.1 Global Search

- Search from header bar
- Results tabbed by type:
  - Posts
  - Comments
  - Members
  - Courses/Lessons

#### 3.11.2 Contextual Search

- Within Community feed
- Within Classroom
- Within Members list

---

### 3.12 Admin & Settings

#### 3.12.1 Community Settings

**General:**
- Name, URL slug, description
- Logo and cover image
- Theme color (brand accent)

**Access:**
- Public vs. private community
- Free vs. paid membership
- Membership questions (up to 3)
- Approval required toggle

**Features:**
- Enable/disable tabs (Map, Leaderboards, etc.)
- Category management
- Level names customization
- Gamification settings

#### 3.12.2 Payment Settings

- Pricing (monthly subscription)
- Free trial period
- Payment processor integration
- Affiliate program (optional)

#### 3.12.3 Moderation Tools

- Post/comment moderation queue
- Auto-moderation rules (optional)
- Ban list management
- Activity logs

---

## 4. User Journeys

### 4.1 New Member Onboarding

```
1. Discover community (search, referral, direct link)
2. View About page and public content
3. Click "Join" → Registration/login
4. Answer membership questions (if configured)
5. Await approval (if required) or instant access
6. Receive Auto-DM welcome message
7. Complete profile (name, avatar, bio)
8. Set location (optional, for map)
9. Browse Community feed
10. Like posts to start earning points
11. Explore Classroom and start a course
```

### 4.2 Creator Community Setup

```
1. Create account
2. Create new community
3. Configure settings (name, description, access)
4. Set up categories
5. Create "Welcome" pinned post
6. Add first course with modules/lessons
7. Schedule first event
8. Customize level names
9. Set up Auto-DM
10. Invite initial members
11. Monitor and engage daily
```

### 4.3 Member Daily Engagement

```
1. Open Koulu → see notification badge
2. Check notifications (new likes, comments)
3. View Community feed (Hot sort)
4. Read/like/comment on interesting posts
5. Check upcoming events
6. Continue course lesson
7. Check leaderboard ranking
8. Send DM to connect with member
```

---

## 5. Non-Functional Requirements

### 5.1 Performance

| Metric | Target |
|--------|--------|
| Page load time | < 2 seconds |
| API response time (p95) | < 200ms |
| Real-time message latency | < 500ms |
| Feed scroll performance | 60 FPS |

### 5.2 Scalability

- Support 10,000+ members per community
- Support 100+ concurrent users per community
- Horizontal scaling for API and workers

### 5.3 Availability

- 99.9% uptime target
- Graceful degradation for non-critical features
- Automatic failover for database

### 5.4 Security

- HTTPS everywhere
- Secure password hashing (Argon2)
- CSRF protection
- Rate limiting on auth endpoints
- Input validation and sanitization
- RBAC for admin functions
- See `security-standards.md` for full requirements

### 5.5 Accessibility

- WCAG 2.1 AA compliance
- Keyboard navigation
- Screen reader support
- Color contrast compliance
- See `accessibility-standards.md` for full requirements

### 5.6 Observability

- Structured logging (JSON)
- Distributed tracing (OpenTelemetry)
- Metrics dashboard
- Error alerting
- See `observability-standards.md` for full requirements

---

## 6. Feature Prioritization

### 6.1 MVP (Phase 1)

**Must Have:**
- ✅ User registration and authentication
- ✅ Basic profile management
- ✅ Community feed (posts, comments, likes)
- ✅ Categories and filtering
- ✅ Basic course structure (modules, lessons)
- ✅ Lesson progress tracking
- ✅ Member directory
- ⚠️ Basic search (Phase 2/3 — member & post search working, pagination UI complete, edge cases & security hardening pending)

### 6.2 Phase 2

**Should Have:**
- ❌ Leaderboards and gamification
- ❌ Calendar and events
- ❌ Direct messaging
- ❌ Notifications (in-app)
- ❌ Level-based access control
- ❌ Email notifications

### 6.3 Phase 3

**Nice to Have:**
- ❌ Map feature
- ❌ Native video hosting
- ❌ Advanced analytics
- ❌ Payment integration
- ❌ Affiliate program
- ❌ Mobile app

---

## 7. Technical Constraints

### 7.1 Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React (Vite), TypeScript, TailwindCSS |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| Cache | Redis |
| File Storage | S3-compatible |
| Search | PostgreSQL FTS (MVP), Elasticsearch (future) |
| Real-time | WebSockets |

### 7.2 Architecture Style

- Domain-Driven Design (DDD)
- Hexagonal Architecture
- Event-driven communication between bounded contexts
- See `global-ddd.md` for full architecture rules

### 7.3 Development Practices

- BDD specifications for all features
- 80%+ test coverage
- Strict TypeScript
- No `any` types (TypeScript or Python)
- See `CLAUDE.md` for full development rules

---

## 8. Success Metrics

### 8.1 Engagement Metrics

| Metric | Description |
|--------|-------------|
| DAU/MAU | Daily/Monthly active users ratio |
| Posts per day | Average posts created per day |
| Comments per post | Average comments per post |
| Course completion rate | % of started courses completed |
| Session duration | Average time spent per session |

### 8.2 Growth Metrics

| Metric | Description |
|--------|-------------|
| New member signups | Daily/weekly signups |
| Member retention | % active after 30/60/90 days |
| Community creation | New communities created |
| Invites sent | Viral growth indicator |

### 8.3 Business Metrics

| Metric | Description |
|--------|-------------|
| MRR | Monthly recurring revenue |
| ARPU | Average revenue per user |
| Churn rate | Monthly membership cancellations |
| LTV | Customer lifetime value |

---

## 9. Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Scope creep | High | High | Strict scope management rules in CLAUDE.md |
| Performance issues at scale | High | Medium | Load testing, caching strategy, horizontal scaling |
| Security vulnerabilities | High | Medium | Security standards, regular audits, pen testing |
| Low engagement | High | Medium | Gamification, notifications, community guidelines |
| Technical debt | Medium | High | BDD specs, code reviews, refactoring sprints |

---

## 10. Glossary

See `docs/domain/GLOSSARY.md` for the complete ubiquitous language definitions.

**Key Terms:**
- **Community**: A group space where members interact
- **Post**: User-created content in the feed
- **Course**: Structured learning path with modules
- **Level**: Member rank based on accumulated points
- **Drip**: Scheduled release of content over time

---

## 11. Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-05 | Claude | Initial draft |

---

## 12. Appendices

### Appendix A: Feature Breakdown Index

Each feature will have a detailed PRD and BDD specification. The index below maps features to their specification documents.

| Feature Area | PRD Document | BDD Spec | Status |
|--------------|--------------|----------|--------|
| User Registration & Authentication | `docs/features/identity/registration-authentication-prd.md` | `tests/features/identity/registration_authentication.feature` | ✅ Complete |
| User Profile | `docs/features/identity/profile-prd.md` | `tests/features/identity/profile.feature` | ✅ Complete |
| Community Feed | `docs/features/community/feed-prd.md` | `tests/features/community/feed.feature` | ✅ Complete (70/70 scenarios) |
| Posts | `docs/features/community/posts-prd.md` | `tests/features/community/posts.feature` | ✅ Complete (included in Feed Phases 1-4) |
| Comments | `docs/features/community/comments-prd.md` | `tests/features/community/comments.feature` | ✅ Complete (included in Feed Phase 2) |
| Reactions | `docs/features/community/reactions-prd.md` | `tests/features/community/reactions.feature` | ✅ Complete (included in Feed Phase 2) |
| Categories | `docs/features/community/categories-prd.md` | `tests/features/community/categories.feature` | ✅ Complete (included in Feed Phase 3) |
| Classroom | `docs/features/classroom/classroom-prd.md` | `tests/features/classroom/classroom.feature` | ✅ Complete (71/71 scenarios) |
| Events | `docs/features/calendar/events-prd.md` | `tests/features/calendar/events.feature` | ❌ Not started |
| Member Directory | `docs/features/members/directory-prd.md` | `tests/features/members/directory.feature` | ✅ Complete — Browse, Search, Filter, Sort, Edge Cases & Security (23/23 scenarios) |
| Member Map | `docs/features/members/map-prd.md` | `tests/features/members/map.feature` | ❌ Not started |
| Leaderboards | `docs/features/gamification/leaderboards-prd.md` | `tests/features/gamification/leaderboards.feature` | ❌ Not started |
| Points & Levels | `docs/features/gamification/points-prd.md` | `tests/features/gamification/points.feature` | ❌ Not started |
| Direct Messages | `docs/features/messaging/dm-prd.md` | `tests/features/messaging/dm.feature` | ❌ Not started |
| Notifications | `docs/features/notifications/notifications-prd.md` | `tests/features/notifications/notifications.feature` | ❌ Not started |
| Search | `docs/features/search/search-prd.md` | `tests/features/search/search.feature` | ⚠️ Partial — Phase 1 complete (11/30 scenarios), Phase 2-3 pending |
| Admin Settings | `docs/features/admin/settings-prd.md` | `tests/features/admin/settings.feature` | ❌ Not started |
| Payments | `docs/features/membership/payments-prd.md` | `tests/features/membership/payments.feature` | ❌ Not started |

### Appendix B: UI Reference

See screenshots in `/docs/ui/references/` for visual design guidance:
- `community-feed.png` - Main feed layout
- `classroom.png` - Course grid view
- `user-dropdown.png` - Header user menu

### Appendix C: Related Documents

- `CLAUDE.md` - Development rules and scope management
- `.claude/skills/ui-design/SKILL.md` - Visual design system
- `docs/domain/GLOSSARY.md` - Ubiquitous language
- `docs/architecture/CONTEXT_MAP.md` - Bounded contexts
