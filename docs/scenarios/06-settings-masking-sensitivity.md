# Scenario: Settings — Masking Sensitivity

**Status: UI-only stub** — `frontend/src/pages/Settings.tsx` has working local state
and the three-tier selector (Low/Medium/High), but there's no backend endpoint yet to
persist it or a mechanism in `docs/plan/04-pii-masking.md` for the masking module to
read a per-tenant sensitivity level. Needs a small addition to the plan before this is
implementable end-to-end: a `GET/PUT /settings` endpoint and a sensitivity parameter
threaded into `presidio_service.mask()`.

## Preconditions
Logged in as `alice@acme.example`.

## Steps
1. Navigate to `/settings`.
2. Select "High" sensitivity and click "Save changes".
3. Upload a document containing a proper noun that only "High" sensitivity would mask
   (per the UI's own description: "redacts locations, dates, and all proper nouns").

## Expected result
- The selection persists across a page reload (currently it does not — this is the
  gap to close first).
- A subsequent document upload is masked according to the newly-selected sensitivity
  level, not the previous default.

## Note
This scenario is the best evidence that "Settings" isn't just a UI mockup — don't
consider it done until sensitivity actually changes masking behavior, not just what
the radio button visually shows selected.
