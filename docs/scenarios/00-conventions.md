# E2E Scenario Conventions

These docs describe user-facing flows precisely enough to become Playwright specs
without re-deriving requirements from scratch. `frontend/e2e/login.spec.ts` is the
first real implementation and sets the pattern every scenario below should follow.

## Seed data (already implemented, `backend/app/auth/users.py`)

| Tenant | User email | Password | Tenant ID |
|---|---|---|---|
| Acme Corp | `alice@acme.example` | `acme-demo-pass` | `tenant-acme` |
| Globex Inc | `bob@globex.example` | `globex-demo-pass` | `tenant-globex` |

Every scenario below should log in as one or both of these — don't invent new demo
accounts per scenario, or the seed data drifts from what's actually implemented.

## Selector conventions

- Prefer `getByLabel`, `getByRole`, `getByText` over CSS selectors/`data-testid` —
  the components (`Input`, `Button`, `Badge`) already expose accessible labels/roles,
  so role-based selectors double as an accessibility check.
- Only add `data-testid` where no accessible role/text exists to hook into (rare with
  this component set).

## Structure every scenario spec follows

1. **Preconditions** — which seed user(s), what state the backend/vector store must
   already be in (e.g., "tenant Acme has one indexed document containing X").
2. **Steps** — the literal user actions, in order.
3. **Expected result** — what must be true afterward, phrased so it's a direct
   `expect(...)` assertion, not a vague description.
4. **Negative case** — what must NOT happen (most important for the security-critical
   scenarios — isolation and masking).

## Running these once implemented

```
cd backend && source .venv/bin/activate && uvicorn app.main:app --port 8000 &
cd frontend && npm run dev &
cd frontend && npm run test:e2e
```
