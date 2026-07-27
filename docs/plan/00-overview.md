# SecureRAG — Project Plan Overview

## Source requirement (from Assessment case study)
Build a RAG-based document query system that:
- Accepts document uploads, understands content, answers queries from them
- Guarantees **strict data isolation between customers** (no cross-tenant leakage, ever)
- **Masks confidential data** — passwords, client IDs, PII — before it reaches storage, the LLM, or the UI
- Is a **working prototype**
- Is reasonably **scalable**

The two security requirements are the actual grading criteria. Everything else (nice UI,
fast responses) is secondary to proving isolation and masking hold up under adversarial
testing, not just the happy path.

## Why AWS-native isn't used here
The natural AWS implementation (Bedrock Knowledge Bases, Comprehend PII, OpenSearch,
IAM/Verified Permissions) isn't available in this environment, so every AWS building
block below has a self-hosted/open-source substitute chosen for being the direct
functional equivalent, not just "something popular":

| Need | AWS way | This project |
|---|---|---|
| Vector store + tenant isolation | Bedrock KB (Silo/Bridge/Pool patterns) | Qdrant, per-tenant collections |
| PII/secret masking | Comprehend PII / Macie | Microsoft Presidio (Analyzer + Anonymizer) |
| Generation LLM | Bedrock model access | Ollama Cloud (`:cloud` models) |
| AuthN/tenant context | Cognito + IAM | JWT with server-validated `tenant_id` claim |
| Object storage | S3 | Local disk per tenant (prototype scope) |

## Tech stack (decided, don't re-litigate in sub-docs)
- **Backend**: Python, FastAPI
- **Frontend**: React + Vite, TypeScript 6.0 (not 7 — tooling/ESLint compat isn't there yet)
- **Vector DB**: Qdrant (Docker)
- **PII masking**: Microsoft Presidio
- **Embeddings**: local `sentence-transformers` model (e.g. `bge-small-en`) — no external
  API dependency, works offline, good enough for a prototype corpus size
- **Generation**: Ollama Cloud API
- **Testing**: pytest (backend), Vitest + React Testing Library (frontend), Playwright (E2E)
- **Code quality**: SonarQube/SonarCloud + Ruff/mypy (backend), ESLint/Prettier (frontend)
- **Containerization**: Docker Compose

## Document map
Each doc below is a scoped, independently-buildable unit. Read `01-architecture.md`
first — it defines the contracts (request/response shapes, the `tenant_id` propagation
rule) that every other doc depends on.

1. `01-architecture.md` — system design, data flow, module contracts
2. `02-backend-api.md` — FastAPI project structure, endpoints
3. `03-ingestion-pipeline.md` — upload → parse → chunk → embed
4. `04-pii-masking.md` — Presidio integration, custom recognizers
5. `05-tenant-isolation-vector-store.md` — Qdrant setup, isolation enforcement
6. `06-auth.md` — JWT auth, tenant context
7. `07-rag-generation.md` — retrieval + Ollama Cloud generation
8. `08-frontend.md` — React app, responsive UI, own design system
9. `09-testing-strategy.md` — unit/integration/E2E plan, isolation test cases
10. `10-code-quality-sonar.md` — SonarQube setup, DRY/lint rules
11. `11-documentation-standards.md` — docstrings, README, ADRs
12. `12-deployment.md` — Docker Compose, running it locally

## The one rule that overrides all others
**`tenant_id` is never accepted from the client.** It is derived server-side from the
verified JWT on every single request, and every module that touches tenant data (vector
store queries, file storage paths, audit logs) takes it as a parameter it received from
the auth layer, never from a request body/query param. Every sub-doc restates this where
relevant — if any implementation deviates from it, that's a bug regardless of what else
works.
