# Scenario: Login

**Status: implemented** — `frontend/e2e/login.spec.ts`

## Preconditions
Backend running with seed users loaded (in-memory, always present on startup —
`backend/app/auth/users.py`).

## Steps
1. Navigate to `/login`.
2. Fill Email with `alice@acme.example`, Password with `acme-demo-pass`.
3. Click "Sign in".

## Expected result
- Redirected to `/documents`.
- Tenant badge in the top bar reads "Acme Corp".
- No console errors during the flow.

## Negative cases (not yet automated — add here)
- Wrong password → error message shown, stays on `/login`, no token stored.
- Unknown email → same generic error (don't reveal whether the email exists —
  the backend already returns an identical 401 for both cases, per
  `backend/tests/test_auth.py`; the frontend spec should assert the UI doesn't
  differentiate either).
- Expired/tampered token in `localStorage` on page load → redirected to `/login`,
  not left on a broken authenticated page.
