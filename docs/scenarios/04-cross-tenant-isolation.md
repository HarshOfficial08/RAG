# Scenario: Cross-Tenant Isolation (the one that matters most)

**Status: partially implemented at the API layer** —
`backend/tests/test_tenant_isolation.py` already proves this at the in-memory-store
level (document listing and audit log are strictly scoped by `tenant_id` from the
verified JWT). The full-stack version below, through the actual chat UI against a
real vector store, is **blocked on `docs/plan/05-tenant-isolation-vector-store.md`**.

This is the literal grading requirement from the case study ("ensure strict data
isolation between customers") — treat this scenario as done only once the E2E
version below passes, not just the backend unit-level version.

## Preconditions
- Tenant Acme (`alice@acme.example`) has a document indexed containing a unique,
  never-otherwise-used string, e.g. `"PROJECT-NIGHTHAWK-48213"`.
- Tenant Globex (`bob@globex.example`) has zero documents referencing that string.

## Steps
1. Log in as Globex (`bob@globex.example`).
2. On `/ask`, ask a question specifically designed to surface the Acme secret if
   isolation were broken, e.g. "What do you know about PROJECT-NIGHTHAWK-48213?"
3. Also attempt the API directly (not just through the UI) with a crafted request —
   e.g. a `POST /query` call with a manually-added `tenant_id` field in the body set
   to Acme's tenant ID, still authenticated as Globex — to prove the backend ignores
   any client-supplied tenant identifier.

## Expected result
- The UI answer never contains `"PROJECT-NIGHTHAWK-48213"` or any paraphrase of Acme's
  document content — it should state no relevant document was found.
- The crafted API request in step 3 returns Globex-scoped results only (or none),
  proving the `tenant_id` in the request body is ignored in favor of the JWT-derived
  value. If this test fails, it fails the entire assessment's core requirement —
  treat any deviation here as a blocker, not a nice-to-have.

## Why this is written as its own scenario, not folded into "ask a question"
Every other scenario can degrade gracefully (a slightly wrong answer, a missed PII
pattern). This one can't — a single leak here means the system fails the assessment's
actual requirement regardless of how polished everything else is. Keep it as the
first thing demoed, and the last thing cut from the test suite under time pressure.
