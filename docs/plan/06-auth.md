# Auth & Tenant Context

## Depends on
Nothing upstream — this is the foundational module every other backend piece consumes.

## Scope (prototype-appropriate, not overbuilt)
Simple JWT auth is sufficient here — no need for a full Keycloak/OIDC deployment for a
prototype. Note Keycloak as the production-hardening upgrade in the doc, don't build it.

- `POST /auth/login` — accepts `{email, password}`, looks up a seeded user record
  (`{user_id, tenant_id, password_hash}`), returns a JWT.
- JWT claims: `{sub: user_id, tenant_id, exp}`. Signed with `HS256` for the prototype
  (a single shared secret from config is fine at this scale; note asymmetric `RS256` +
  rotating keys as the production upgrade).
- `get_current_tenant(request) -> TenantContext`: FastAPI dependency that verifies the
  token signature and expiry, then returns `TenantContext(tenant_id=..., user_id=...)`.
  This is the **only** function in the codebase allowed to read `tenant_id` from a
  token — every other module receives it as a parameter.

## Seed data for the demo
Seed at least two tenants with at least one user each (e.g. `acme-corp` /
`globex-inc`), each with a document uploaded containing distinctive fake PII, so the
cross-tenant isolation test (`05-tenant-isolation-vector-store.md`) and demo walkthrough
have something concrete to point at.

## What NOT to build for this scope
- No password reset flow, no refresh tokens, no RBAC beyond tenant scoping — these are
  real features but out of scope for what's being graded; don't spend prototype time
  here. Note them explicitly as "not implemented, here's how I'd add it" if asked.

## Definition of done
- A request to any protected endpoint without a valid JWT returns 401.
- A request with a JWT for tenant A cannot access tenant B's documents or audit log
  under any circumstance, including a tampered/expired token.
- Token expiry is enforced (short-lived, e.g. 1h, is fine for a demo).
