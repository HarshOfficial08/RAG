# Frontend

## Depends on
`02-backend-api.md` (endpoint contracts)

## Explicit constraint
**Do not reuse any code/markup from the `stitch_securerag_enterprise_ai_dashboard`
folder** — that was a visual reference only and will be deleted. Re-implement the look
(charcoal/teal, Linear/Vercel-inspired, minimal) from scratch as a small, real design
system: a handful of shared components (Button, Input, Badge, Card, Table, Sidebar
layout), not page-specific one-off styling.

## Stack
- React + Vite, **TypeScript 6.0**
- Styling: Tailwind CSS (fast, keeps the "own design system" constraint honest since
  utility classes discourage copy-pasted bespoke CSS per page)
- Routing: `react-router`
- Server state: `@tanstack/react-query` for all API calls (caching, loading/error
  states handled once, not reimplemented per page)
- No global client state library needed at this scope — auth token in a small context
  provider is enough.

## Pages (same set as previously reviewed, rebuilt independently)
1. Login
2. Document Library (upload + list + status)
3. Ask a Question (chat + sources)
4. Audit Log
5. Settings (masking sensitivity, org info)

## Responsiveness — concrete, testable requirements, not "should look fine"
- Mobile-first Tailwind breakpoints: base styles for ≤640px, `md:`/`lg:` overrides for
  tablet/desktop.
- Sidebar collapses to a bottom nav or hamburger drawer below `md`.
- Tables (Document Library, Audit Log) become stacked cards below `md` — never a
  horizontally-scrolling table with no affordance.
- Test at three widths minimum during dev: 375px (mobile), 768px (tablet), 1440px
  (desktop) — actually resize the browser, don't eyeball it at one size.

## DRY guidance specific to frontend
- One `<ApiClient>` wrapper (axios/fetch instance with the JWT attached in an
  interceptor) — no component calls `fetch` directly.
- One `useAuth()` hook exposing `{tenantId, userId, login, logout}` — components never
  read the JWT or `localStorage` directly.
- Status badges (Indexed/Processing/Failed, PII Masked, Triggered/None) are one shared
  `<Badge variant=... />` component, not per-page conditional className strings.

## Definition of done
- All 5 pages functional against the real backend (no mocked data left in by the end).
- Verified responsive at the three widths above.
- Zero direct `fetch`/`axios` calls outside the API client module (this is exactly the
  kind of thing a SonarQube duplication/complexity rule will also catch).
