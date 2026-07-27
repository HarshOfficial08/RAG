# Testing Strategy

## Depends on
All backend/frontend modules — this doc's test cases should be written alongside each
module, not bolted on at the end. The isolation and masking tests in particular are the
actual deliverable proof for the assessment's core requirements.

## Layers

### Backend unit tests — pytest
- `masking/`: known PII strings in → masked tokens out (per `04-pii-masking.md`
  definition of done); custom recognizers tested individually.
- `retrieval/vector_store.py`: mock/local Qdrant, assert `search()` always includes the
  tenant filter (inspect the constructed query object, don't just check results).
- `generation/`: prompt construction produces expected structure given fixed chunks.
- `auth/`: token verification accepts valid tokens, rejects expired/tampered/wrong-
  secret tokens.

### Backend integration tests — pytest + httpx + a real (test) Qdrant instance
- Full ingestion flow: upload → parse → mask → embed → upsert → status becomes
  `indexed`.
- Full query flow: seed two tenants' documents, query as each, assert correct scoping.

### Frontend unit tests — Vitest + React Testing Library
- Shared components (`Badge`, `ApiClient` error handling, `useAuth`) tested in
  isolation — these are the highest-leverage tests since every page depends on them.
- Avoid testing implementation details (internal state) — test what the user sees.

### E2E — Playwright
This is where the **cross-tenant isolation guarantee gets demonstrated end-to-end**,
which is the single most important test in the whole project:
1. Seed tenant A with a document containing a unique string, e.g. `"PROJECT-NIGHTHAWK-42"`.
2. Log in as tenant B via the UI.
3. Ask a question in the chat UI that would surface that string if isolation were
   broken.
4. Assert the answer never contains it and/or explicitly states no relevant document
   was found.

Other E2E flows: login → upload → see status transition to Indexed → ask a question →
see sourced answer → check audit log entry appended. Run against mobile viewport
(375px) at least once to validate the responsive requirement, not just desktop.

## Coverage expectations (proportionate to a prototype, not aspirational)
- Masking and isolation modules: high coverage, since they're the graded requirement —
  treat every recognizer and every `search()` call site as needing a test.
- General CRUD/UI glue: cover the happy path and one failure path each; don't chase a
  coverage percentage for its own sake.

## CI
All three layers run in CI (GitHub Actions or equivalent) on every push — this is also
what feeds SonarQube's coverage metric (`10-code-quality-sonar.md`).

## Definition of done
- `pytest` and `vitest` both green locally and in CI.
- The cross-tenant isolation E2E test exists, passes, and is the one test you'd show
  first if asked "how do you know this actually works."
