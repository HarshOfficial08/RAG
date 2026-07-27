# Scenario: Document Upload and PII Masking

**Status: blocked on `docs/plan/03-ingestion-pipeline.md` and `docs/plan/04-pii-masking.md`**
(parser/masking/embedding aren't wired in yet — see `app/ingestion/pipeline.py`).

## Preconditions
Logged in as `alice@acme.example` (Acme Corp). A test fixture file exists containing
known fake PII, e.g. a `.txt` with:
```
Client ID: CID-48213
Contact: jane.doe@example.com, SSN 123-45-6789
Internal note: password: hunter2please-rotate
```

## Steps
1. On `/documents`, click "Upload document" and select the fixture file.
2. Wait for the row's status badge to transition `Processing` → `Indexed` (polling,
   currently every 5s per `frontend/src/pages/Documents.tsx`).
3. Assert a "PII Masked" badge appears on that row.

## Expected result
- Document reaches `Indexed` status within a reasonable timeout (define one once
  ingestion latency is known — start with 30s).
- "PII Masked" badge is present.
- (Backend-side, not UI-visible) querying the indexed chunks directly should show the
  Client ID, email, SSN, and password string replaced with mask tokens, never present
  verbatim — this part is better asserted as a backend integration test than through
  the UI, since the UI only shows a boolean badge, not the chunk content.

## Negative cases
- A document with **no** PII should index normally with no "PII Masked" badge
  (checks against over-masking ordinary text).
- A corrupted/unparseable file should reach `Failed` status with a visible reason,
  not silently disappear or hang at `Processing` forever.
