# Backend API

## Depends on
`01-architecture.md` (contracts), `06-auth.md` (tenant context dependency)

## Folder structure

```
backend/
  app/
    main.py                 # FastAPI app, router registration
    config.py                # env-driven settings (pydantic-settings)
    auth/
      jwt.py                 # token verify/issue
      dependencies.py         # get_current_tenant()
    ingestion/
      parser.py               # Docling/unstructured wrapper
      chunker.py
      pipeline.py              # orchestrates parse -> mask -> chunk -> embed -> upsert
    masking/
      presidio_service.py
      recognizers.py           # custom Client ID / secret recognizers
    retrieval/
      vector_store.py          # Qdrant client wrapper: upsert(), search()
      embeddings.py
    generation/
      llm_client.py            # generate() interface, Ollama Cloud implementation
      prompt.py
    api/
      documents.py              # POST /documents, GET /documents
      query.py                  # POST /query
      audit.py                  # GET /audit-log
    models/
      schemas.py                # pydantic request/response models
    tests/
  Dockerfile
  pyproject.toml
```

## Endpoints (minimum for prototype)

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/auth/login` | none | issues JWT with `tenant_id`, `user_id` claims |
| POST | `/documents` | JWT | multipart upload, returns `{id, status: "processing"}` |
| GET | `/documents` | JWT | list current tenant's documents only |
| POST | `/query` | JWT | `{question}` → `{answer, sources[]}` |
| GET | `/audit-log` | JWT | current tenant's query history only |

## Non-negotiable rule
Every handler in `api/*.py` takes `tenant: TenantContext = Depends(get_current_tenant)`
and passes `tenant.id` explicitly into the service layer. No handler reads `tenant_id`
from the request body, query params, or path — if a client sends one, ignore it.

## DRY guidance
- One pydantic response envelope shape reused across endpoints, not ad hoc dicts.
- Vector store, masking, and generation are each a thin class with one obvious
  entrypoint — resist adding configuration options that aren't used yet.
- Config (Qdrant URL, Ollama Cloud key, JWT secret) lives in one `config.py` via
  `pydantic-settings`, read from `.env` — no scattered `os.environ.get()` calls.

## Definition of done
- `uvicorn app.main:app` runs locally against Docker-composed Qdrant.
- OpenAPI docs (`/docs`) reflect all endpoints with example payloads.
- No endpoint accepts a client-supplied tenant identifier.
