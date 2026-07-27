# RAG Generation (Retrieval + Ollama Cloud)

## Depends on
`05-tenant-isolation-vector-store.md` (search results), `04-pii-masking.md` (output
re-scan)

## Flow for `POST /query`
1. Embed the incoming question (same embedding model as ingestion — this must match,
   it's a common bug source).
2. `vector_store.search(tenant_id, query_vector, k=5)`.
3. Re-run masking over retrieved chunk text (defense in depth — see `04`).
4. Build prompt: system instruction + retrieved chunks (with source doc names) +
   question.
5. Call `generate(prompt)` → Ollama Cloud.
6. Re-run masking over the generated answer before returning.
7. Return `{answer, sources: [{document_id, filename, chunk_index}]}`.
8. Log the query to the audit log (question text, `masking_triggered: bool`,
   `tenant_id`, `user_id`, timestamp) — never log raw retrieved chunk text or the raw
   answer if masking triggered on it.

## Generation client interface (swap-friendly, per architecture doc)
```python
class LLMClient(Protocol):
    def generate(self, prompt: str) -> str: ...

class OllamaCloudClient:
    def __init__(self, api_key: str, model: str = "qwen3.5:cloud"): ...
    def generate(self, prompt: str) -> str:
        # POST https://ollama.com/api/chat, Authorization: Bearer {api_key}
        # body: {"model": self.model, "messages": [{"role": "user", "content": prompt}]}
        ...
```
Keep this the only place that knows about Ollama Cloud's specific request shape — if
the model provider changes later, only this file changes.

## Prompt template (keep simple, explicit about grounding)
```
You are answering questions using ONLY the provided document excerpts from {tenant_name}.
If the answer isn't in the excerpts, say so — do not use outside knowledge.

Excerpts:
{chunks}

Question: {question}
```

## Definition of done
- A question answerable from an indexed document returns a grounded answer with
  correct source citations.
- A question with no relevant indexed content returns an explicit "not found in your
  documents" response rather than a hallucinated answer.
- No PII/secret pattern used in test documents ever appears verbatim in a generated
  answer.
