---
name: frontend
description: Follow frontend development standards for React, TypeScript, and TailwindCSS
---

# Skill: Frontend Development

## Stack
- **Framework**: React (Vite)
- **Language**: TypeScript with `strict: true`
- **Styling**: TailwindCSS
- **Testing**: Vitest + React Testing Library
- **State**: React Context (simple) or Zustand (complex)

---

## TypeScript Rules

```typescript
// ✅ Always define props interfaces
interface ButtonProps {
  label: string;
  onClick: () => void;
  disabled?: boolean;
}

// ❌ NEVER use `any` - use `unknown` if truly dynamic
// ❌ NEVER disable strict mode
```

---

## React Patterns

- Functional components with hooks only
- One component per file, named `PascalCase.tsx`
- Prefer composition (`children`) over configuration props
- Follow rules of hooks strictly

---

## TailwindCSS

```typescript
// Use this utility for conditional classes
import { twMerge } from 'tailwind-merge';
import { clsx, type ClassValue } from 'clsx';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

**Rules:**
- Utility classes only—no `@apply` in CSS
- Extend `tailwind.config.ts` with design tokens (see `.claude/skills/ui-design.md`)
- Mobile-first: `block md:flex`
- No hardcoded colors—use CSS variables

---

## Accessibility (WCAG 2.1 AA)

**Must Have:**
- All `<img>` have `alt` (empty for decorative)
- Semantic HTML: `<button>`, `<nav>`, `<main>`, `<article>`
- Focus visible—NEVER `outline: none` without replacement
- Color contrast: 4.5:1 normal text, 3:1 large text
- Keyboard reachable for all interactive elements
- `aria-label` for icon-only buttons

**Headings:** Use `<h1>`-`<h6>` in logical order, never skip levels

---

## Observability

```typescript
// Initialize OpenTelemetry at app entry
// Ensure traceparent header injected into all API calls
```

---

## Verification

Run before completing any frontend task:

```bash
./scripts/verify-frontend.sh
```

**Must pass:**
1. `npm run lint` (ESLint)
2. `npm run typecheck` (tsc)
3. `npm run test` (Vitest)
4. `npm run build`

Only mark done when script prints "All Frontend Checks Passed!"
