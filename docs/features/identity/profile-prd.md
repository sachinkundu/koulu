# User Profile - Product Requirements Document

**Version:** 1.0
**Last Updated:** 2026-02-06
**Status:** In Progress (Phase 3 of 5 Complete)
**Implementation Status:** Phases 1-3 Complete (Domain, Read Operations, Write Operations)
**Context:** Identity
**Dependencies:** Registration & Authentication (complete)

**Implementation Summaries:**
- Phase 1: `docs/summaries/profile-phase1-summary.md`
- Phase 2: `docs/summaries/profile-phase2-summary.md`
- Phase 3: `docs/summaries/profile-phase3-summary.md`

---

## 1. Overview

### 1.1 What

The User Profile feature enables users to create, view, and edit their public-facing profile information. Profiles display personal details, social links, location, activity history, and contribution statistics.

### 1.2 Why

- Users need identity within the community beyond just authentication
- Profiles enable social connections and trust between members
- Activity visibility encourages engagement and contribution
- Location data enables future Map feature for member discovery

### 1.3 Success Criteria

- Users can complete their profile with display name, avatar, bio, social links, and location
- Users can view any other member's profile
- Users can edit their own profile at any time
- Profile pages display activity feed and contribution stats (empty states until Community feature exists)
- All profile fields except display name are optional

---

## 2. User Stories

### 2.1 Profile Completion

**US-1:** As a new user, I want to complete my profile after registration, so that other community members can learn about me.

**US-2:** As a user, I want to add social links to my profile, so that others can connect with me on other platforms.

**US-3:** As a user, I want to set my location, so that I can be discovered by nearby members (future Map feature).

### 2.2 Profile Viewing

**US-4:** As a community member, I want to view another member's profile, so that I can learn about them before engaging.

**US-5:** As a user, I want to see my own profile as others see it, so that I can verify how I appear to the community.

### 2.3 Profile Editing

**US-6:** As a user, I want to edit my profile information at any time, so that I can keep it current.

**US-7:** As a user, I want to update my avatar via URL, so that I can personalize my appearance.

### 2.4 Activity & Stats

**US-8:** As a user viewing a profile, I want to see the member's recent activity, so that I can understand their engagement level.

**US-9:** As a user viewing a profile, I want to see contribution statistics, so that I can gauge their community involvement.

---

## 3. Domain Model

### 3.1 Entities

#### Profile (extends existing)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| user_id | UserId | Yes | Reference to User aggregate |
| display_name | DisplayName | Yes | Public name (2-50 characters) |
| avatar_url | URL | No | Profile image URL (auto-generated if not set) |
| bio | Bio | No | Short description (max 500 characters) |
| location | Location | No | City and country |
| social_links | SocialLinks | No | External profile URLs |
| is_complete | Boolean | Yes | Profile completion status |
| created_at | DateTime | Yes | Profile creation timestamp |
| updated_at | DateTime | Yes | Last modification timestamp |

### 3.2 Value Objects

#### DisplayName
- String, 2-50 characters
- Alphanumeric, spaces, and common punctuation allowed
- No leading/trailing whitespace

#### Bio
- String, 0-500 characters
- Supports plain text only (no HTML/markdown)

#### Location
- city: String (2-100 characters)
- country: String (2-100 characters)
- Display format: "City, Country"

#### SocialLinks
- twitter_url: URL | null
- linkedin_url: URL | null
- instagram_url: URL | null
- website_url: URL | null
- All fields optional
- URLs must be valid format when provided

### 3.3 Aggregates

**User** remains the aggregate root. Profile is an entity within the User aggregate, accessed through User operations.

---

## 4. Commands & Events

### 4.1 Commands

| Command | Actor | Description |
|---------|-------|-------------|
| CompleteProfile | User | Initial profile setup with required display name |
| UpdateProfile | User | Modify any profile fields |

### 4.2 Domain Events

| Event | Trigger | Data |
|-------|---------|------|
| ProfileCompleted | First-time profile completion | user_id, display_name |
| ProfileUpdated | Any profile field change | user_id, changed_fields |

### 4.3 Queries

| Query | Actor | Description |
|-------|-------|-------------|
| GetProfile | Any authenticated user | Retrieve profile by user ID |
| GetCurrentUserProfile | Authenticated user | Retrieve own profile |
| GetProfileActivity | Any authenticated user | Retrieve user's recent activity |
| GetProfileStats | Any authenticated user | Retrieve contribution statistics |

---

## 5. API Contracts

### 5.1 Endpoints Overview

| Operation | Method | Route Pattern | Auth Required |
|-----------|--------|---------------|---------------|
| Get own profile | GET | Current user profile | Yes |
| Get any profile | GET | Profile by user ID | Yes |
| Complete profile | PUT | Current user profile | Yes |
| Update profile | PATCH | Current user profile | Yes |
| Get profile activity | GET | Profile activity by user ID | Yes |
| Get profile stats | GET | Profile stats by user ID | Yes |

### 5.2 Data Shapes

#### Profile Response
```
{
  user_id: UUID
  display_name: string
  avatar_url: string | null
  bio: string | null
  location: {
    city: string
    country: string
  } | null
  social_links: {
    twitter_url: string | null
    linkedin_url: string | null
    instagram_url: string | null
    website_url: string | null
  }
  is_complete: boolean
  created_at: datetime
  updated_at: datetime
}
```

#### Complete Profile Request
```
{
  display_name: string (required, 2-50 chars)
  avatar_url: string | null
  bio: string | null (max 500 chars)
  location: {
    city: string (2-100 chars)
    country: string (2-100 chars)
  } | null
  social_links: {
    twitter_url: string | null
    linkedin_url: string | null
    instagram_url: string | null
    website_url: string | null
  } | null
}
```

#### Update Profile Request
```
{
  display_name: string | null (2-50 chars if provided)
  avatar_url: string | null
  bio: string | null (max 500 chars)
  location: {
    city: string
    country: string
  } | null
  social_links: {
    twitter_url: string | null
    linkedin_url: string | null
    instagram_url: string | null
    website_url: string | null
  } | null
}
```

#### Profile Activity Response
```
{
  items: [
    {
      type: "post" | "comment"
      id: UUID
      title: string | null (for posts)
      preview: string (truncated content)
      created_at: datetime
    }
  ]
  total_count: number
}
```

Note: Returns empty list until Community feature is implemented.

#### Profile Stats Response
```
{
  contributions: number (posts + comments count)
  joined_at: datetime
}
```

Note: Returns 0 contributions until Community feature is implemented.

### 5.3 Error Responses

| Error | Condition |
|-------|-----------|
| Profile not found | User ID does not exist |
| Validation error | Invalid field values |
| Unauthorized | Not authenticated |
| Display name required | Completing profile without display name |
| Display name too short | Less than 2 characters |
| Display name too long | More than 50 characters |
| Bio too long | More than 500 characters |
| Invalid URL format | Malformed URL in avatar or social links |

---

## 6. Business Rules

### 6.1 Profile Completion

- **BR-1:** Display name is required to complete a profile
- **BR-2:** All other fields (avatar, bio, location, social links) are optional
- **BR-3:** If no avatar URL provided, system generates one from display name initials
- **BR-4:** Profile must be completed before accessing community features

### 6.2 Field Validation

- **BR-5:** Display name: 2-50 characters, trimmed whitespace
- **BR-6:** Bio: 0-500 characters
- **BR-7:** Location city: 2-100 characters when provided
- **BR-8:** Location country: 2-100 characters when provided
- **BR-9:** Social link URLs must be valid URL format when provided
- **BR-10:** Avatar URL must be valid URL format when provided

### 6.3 Profile Visibility

- **BR-11:** All profile information is public to authenticated users
- **BR-12:** Users can view any member's profile within the platform
- **BR-13:** Unauthenticated users cannot view profiles

### 6.4 Profile Updates

- **BR-14:** Users can only edit their own profile
- **BR-15:** Display name can be changed after initial completion
- **BR-16:** Updating profile publishes ProfileUpdated event
- **BR-17:** Avatar URL can be cleared (reverts to auto-generated)

---

## 7. UI Behavior

### 7.1 Profile View Page

**Layout:** Left sidebar + right content area (Skool-style)

**Left Sidebar:**
- Avatar (large, circular)
- Display name (prominent)
- Bio (if set)
- Location (if set, format: "City, Country")
- Social links (icons with links, only show if set)
- "Edit Profile" button (only for own profile)

**Right Content Area:**
- **Stats Bar:** Contributions count, Member since date
- **Activity Chart:** Last 30 days heatmap (empty state until Community exists)
- **Recent Activity:** List of posts/comments (empty state until Community exists)

**Empty States:**
- Activity chart: "No activity yet" message
- Recent activity: "No posts or comments yet" message

### 7.2 Edit Profile Page

**Form Fields:**
- Display name (text input, required)
- Avatar URL (text input, optional, with preview)
- Bio (textarea, optional, character counter)
- Location: City (text input), Country (text input)
- Social Links:
  - Twitter/X URL (text input)
  - LinkedIn URL (text input)
  - Instagram URL (text input)
  - Website URL (text input)

**Actions:**
- Save button (validates and submits)
- Cancel button (returns to profile view)

**Feedback:**
- Inline validation errors per field
- Success toast on save
- Loading state during submission

### 7.3 Profile Setup Flow (Post-Registration)

- Shown after email verification
- Minimum required: display name
- Optional: all other fields
- Skip option for optional fields
- Redirect to home/community on completion

### 7.4 Navigation

- Click on any user avatar/name → opens their profile
- Header user menu → "My Profile" link
- Header user menu → "Edit Profile" link

---

## 8. Edge Cases

### 8.1 Avatar Handling

- **EC-1:** No avatar URL provided → Auto-generate from initials
- **EC-2:** Invalid avatar URL → Show validation error, don't save
- **EC-3:** Avatar URL cleared → Revert to auto-generated

### 8.2 Location Handling

- **EC-4:** City provided without country → Validation error
- **EC-5:** Country provided without city → Validation error
- **EC-6:** Both cleared → Location removed from profile

### 8.3 Social Links Handling

- **EC-7:** Invalid URL format → Validation error on that field
- **EC-8:** All social links cleared → Social links section hidden on profile view

### 8.4 Profile Not Found

- **EC-9:** Viewing deleted/non-existent user → 404 with "Profile not found" message

### 8.5 Activity & Stats

- **EC-10:** No community activity yet → Show empty state with encouraging message
- **EC-11:** Activity from deleted posts → Exclude from activity feed

---

## 9. Security Requirements

### 9.1 Authorization

- All profile endpoints require authentication
- Users can only modify their own profile
- All profiles are readable by any authenticated user

### 9.2 Data Protection

- Sanitize all text inputs (prevent XSS)
- Validate URL formats strictly
- Rate limit profile update requests

### 9.3 Privacy Considerations

- Location is optional and user-controlled
- No exact addresses, city-level only
- Users can remove location at any time

---

## 10. Out of Scope

The following are explicitly NOT part of this feature:

| Item | Reason | Future Phase |
|------|--------|--------------|
| Avatar file upload | Requires S3 integration | Phase 2 |
| Follow/unfollow system | Separate feature | Phase 2 |
| Follower/following counts | Requires follow system | Phase 2 |
| Profile privacy settings | MVP has public profiles | Phase 2 |
| Block/report users | Separate moderation feature | Phase 2 |
| Cover/banner image | Nice-to-have | Phase 3 |
| Profile badges/achievements | Requires gamification | Phase 2 |
| Real-time activity updates | Nice-to-have | Phase 3 |
| Profile search | Part of Members feature | Phase 1 |

---

## 11. Dependencies

### 11.1 Requires (Upstream)

- **Registration & Authentication** ✅ Complete
  - User entity and authentication
  - Basic profile completion flow

### 11.2 Required By (Downstream)

- **Community Feed** - Posts show author profile info
- **Members Directory** - Lists member profiles
- **Map Feature** - Uses location data
- **Leaderboards** - Links to profiles

---

## 12. Acceptance Criteria Summary

1. ✅ User can complete profile with display name (required) and optional fields
2. ✅ User can add/edit bio (up to 500 characters)
3. ✅ User can add/edit location (city + country)
4. ✅ User can add/edit social links (Twitter, LinkedIn, Instagram, Website)
5. ✅ User can update avatar via URL
6. ✅ System generates avatar from initials when none provided
7. ✅ Any authenticated user can view any profile
8. ✅ Profile displays activity feed (empty state for now)
9. ✅ Profile displays contribution stats (zero for now)
10. ✅ Profile displays 30-day activity chart (empty for now)
11. ✅ ProfileUpdated event published on changes
12. ✅ All validation rules enforced

---

## 13. Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-05 | Claude | Initial draft |
