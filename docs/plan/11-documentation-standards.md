# Documentation Standards

## Depends on
Nothing structurally — applied last, across all modules, once behavior is stable
(docs written against code that's still changing just rot immediately).

## Code-level documentation
- **Python**: Google-style docstrings on every public function/class in `masking/`,
  `retrieval/`, `auth/`, `generation/` — the modules whose *why* isn't obvious from the
  name. Skip docstrings on simple pydantic schemas or trivial getters.
- **TypeScript**: TSDoc comments on shared components/hooks (`ApiClient`, `useAuth`,
  `Badge`) — not on every component, just the ones other code depends on.
- Follow the project-wide rule: comment the *why*, not the *what*. E.g. worth a
  comment: "masking runs before chunking so NER sees full-document context, not
  fragments" — not worth a comment: "this function uploads a file."

## Repo-level docs
- `README.md` (root): what this is, the two security guarantees it makes, quick-start
  (`docker compose up`), architecture diagram (reuse the mermaid diagram from
  `01-architecture.md`).
- `docs/adr/` — short Architecture Decision Records for the choices worth defending in
  an interview: why Pool over Silo (or vice versa, once decided), why Presidio over a
  custom regex-only approach, why Qdrant over pgvector/Weaviate. 1 page each, format:
  Context / Decision / Consequences.

## Interview-specific deliverable
A short `docs/DEMO_SCRIPT.md`: the exact sequence to run live — seed two tenants,
show the isolation E2E test passing, upload a document with fake PII and show the
masked result in the audit log, ask a question and show sourced answer. This turns
"explain your architecture" into "watch it prove itself."

## Definition of done
- A new reader can go from `README.md` to a running app with no other context.
- Every ADR states a real tradeoff, not just a restatement of the choice made.
