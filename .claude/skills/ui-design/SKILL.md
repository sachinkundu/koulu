---
name: ui-design
description: Follow Koulu design system inspired by Skool.com for consistent UI implementation
model: sonnet
---

# Skill: UI Design System (Koulu)

Reference: Skool.com interface

## Design Philosophy
- **Content is King**: Minimal, distraction-free
- **Clean & Airy**: High whitespace usage
- **Card-Based**: Content blocks in white cards on gray background
- **Soft Geometry**: Consistent 8-12px border radius

---

## Color Palette

```css
:root {
  /* Backgrounds */
  --bg-page: #F7F9FA;        /* Main page background */
  --bg-card: #FFFFFF;        /* Cards, posts, widgets */
  --bg-input: #F0F2F5;       /* Search, comment inputs */
  --bg-hover: #F2F4F7;       /* List item hover */

  /* Text */
  --text-primary: #1D2129;   /* Headers, body */
  --text-secondary: #65676B; /* Meta, timestamps */
  --text-muted: #B0B3B8;     /* Placeholders */
  --text-link: #007AFF;      /* Links */

  /* Borders */
  --border-subtle: #E4E6EB;  /* Cards, dividers */
  --border-focus: #1D2129;   /* Input focus */

  /* Brand (dynamic per community) */
  --primary-brand: #F7B955;  /* Community accent */
  --primary-text-on-brand: #000000;
}
```

**Rule:** NEVER hardcode hex values—use CSS variables.

---

## Typography

```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
```

| Element | Size | Weight |
|---------|------|--------|
| Page title (H1) | 24-28px | Bold (700) |
| Card title (H2) | 18-20px | Semi-bold (600) |
| Body text | 15-16px | Regular (400) |
| Meta/small | 13px | Regular (400) |
| Navigation | 14-15px | Medium (500) |

---

## Layout

### Container
```css
.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 16px;
}
```

### Desktop Grid (>768px)
```
┌──────────────────────────────────────────┐
│                 Header (60px)             │
├──────────────────────────────────────────┤
│          Secondary Nav (tabs)             │
├─────────────────────────┬────────────────┤
│                         │                │
│   Feed/Main (~66%)      │  Sidebar       │
│                         │  (320-360px)   │
│                         │                │
└─────────────────────────┴────────────────┘

Gap: 24px
```

### Mobile (<768px)
- Stacked layout
- Sidebar moves below or to dedicated tab

---

## Components

### Header
- Fixed/sticky, 60px height
- White background
- `border-bottom: 1px solid var(--border-subtle)`
- Centered search bar (pill-shaped, `--bg-input`)

### Navigation Tabs
- Text-only tabs under header
- Active: high contrast text + optional pill background
- No heavy underlines

### Feed Cards
```css
.card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}
```

### Buttons
- Primary: `--primary-brand` fill, 4-6px radius
- Large click targets

### Inputs
- `--bg-input` background
- No border by default
- Border on focus
- Large clickable areas

### Category Pills
- Rounded buttons (General, Q&A, Wins, etc.)
- Active state: filled background
- Inactive: outlined or subtle

---

## Iconography
- Stroke-based set (Heroicons, Lucide, or Phosphor)
- Regular to medium weight
- 8px gap from adjacent text

---

## Implementation Rules

1. **Mobile First**: Base styles mobile, `md:` breakpoint for desktop
2. **Semantic HTML**: `<article>` for posts, `<aside>` for sidebar, `<nav>` for menus
3. **No Debug Styles**: Use design system colors immediately, no red borders
4. **TailwindCSS**: Configure design tokens in `tailwind.config.ts`:

```typescript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        page: '#F7F9FA',
        card: '#FFFFFF',
        input: '#F0F2F5',
        // ... etc
      },
      borderRadius: {
        card: '8px',
      },
    },
  },
}
```
