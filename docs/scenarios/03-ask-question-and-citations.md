# Scenario: Ask a Question and See Cited Sources

**Status: blocked on `docs/plan/05-tenant-isolation-vector-store.md` and
`docs/plan/07-rag-generation.md`** (`/query` currently returns `501 Not Implemented`,
per `backend/app/api/query.py`).

## Preconditions
Logged in as `alice@acme.example`, with at least one document already indexed
(depends on scenario 02) containing a known, findable fact — e.g. a policy document
stating "refunds are processed within 5 business days."

## Steps
1. On `/ask`, type a question the indexed document can answer, e.g. "How long do
   refunds take?"
2. Submit and wait for the response.

## Expected result
- An answer appears referencing the correct information ("5 business days").
- At least one source chip is shown, naming the source document's filename.
- No PII/secret pattern from any test fixture ever appears verbatim in the answer,
  even if the question is phrased to try to surface it.

## Negative case
- A question with no relevant indexed content returns an explicit "not found in your
  documents" style response — not a hallucinated answer using outside knowledge.
  Assert the response text does NOT confidently state a specific fact when nothing
  in the tenant's documents supports it.
