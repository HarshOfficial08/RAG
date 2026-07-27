# Scenario: Audit Log Visibility

**Status: scaffolded** — `GET /audit-log` is implemented and tenant-scoped
(`backend/app/api/audit.py`, covered by `test_audit_log_is_scoped_per_tenant`), but
it's always empty until `/query` actually logs entries, which depends on
`docs/plan/07-rag-generation.md`.

## Preconditions
Logged in as `alice@acme.example`, having asked at least one question via `/ask`
(depends on scenario 03) — one of which should contain PII that gets masked (depends
on scenario 02/04-pii-masking).

## Steps
1. Navigate to `/audit-log`.

## Expected result
- An entry exists for each question asked, showing timestamp, user, and the question
  text.
- Any query where masking was triggered shows a "Triggered" badge; others show "None".
- Only the logged-in tenant's own entries appear — verify this by logging in as the
  other seed tenant and confirming a disjoint set of entries (this overlaps with
  scenario 04's isolation guarantee — reuse the same seed data rather than
  re-deriving it).

## Negative case
- Raw retrieved document text or the full generated answer is never present in the
  audit log if masking was triggered on it — only the question and a boolean flag
  (per `docs/plan/07-rag-generation.md`'s logging rule). This is worth a backend
  test asserting the log entry shape, since it's not something the UI surfaces
  directly.
