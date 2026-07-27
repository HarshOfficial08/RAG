# Tenant Isolation & Vector Store (Qdrant)

## Depends on
`01-architecture.md` for the isolation strategy decision (Pool with hard filter,
Silo as upgrade path). This doc is the actual grading-critical piece — treat it as the
highest-priority workstream.

## Setup
- Qdrant via Docker (`qdrant/qdrant` image), one collection e.g. `documents`.
- Payload schema per point: `{tenant_id: keyword, document_id: keyword, chunk_index:
  int, text: str}`.
- **Create a payload index on `tenant_id`** (`create_payload_index`) — this is what
  makes the tenant filter get pushed into the HNSW graph traversal instead of being a
  slow/leaky post-filter. Don't skip this step; it's the difference between a real
  isolation boundary and a performance-degrading afterthought.

## The module's public interface (only two functions, on purpose)
```python
def upsert(tenant_id: str, document_id: str, chunks: list[Chunk]) -> None: ...

def search(tenant_id: str, query_vector: list[float], k: int = 5) -> list[Chunk]:
    # MUST always include Filter(must=[FieldCondition(key="tenant_id",
    # match=MatchValue(value=tenant_id))]) — no code path calls Qdrant's search
    # without this filter attached, ever.
    ...
```
Do not add a third function or a "search without filter" escape hatch, even for
debugging — that's exactly the kind of thing that gets left in and becomes the bug.

## Silo upgrade path (mention in interview even if you ship Pool)
Parameterize the collection name by `tenant_id` (`f"documents_{tenant_id}"`) instead of
a shared collection + filter. Same `upsert`/`search` signatures, different backing
collection. Worth having this as a documented alternative even if you only implement
Pool, since it shows you understand AWS's own Silo/Bridge/Pool tradeoff (Silo = physical
isolation, higher ops cost; Pool = logical isolation, cheaper, requires the filter to be
bulletproof).

## Definition of done — this is the test that matters most
Write and pass this test before anything else in the project is considered "working":
1. Ingest a document for tenant A containing a unique, distinctive string.
2. Authenticate as tenant B, query for that exact string.
3. Assert **zero** results returned to tenant B, even though the vector is
   semantically identical/near-identical to what tenant A has.
4. Repeat with a crafted query attempting to pass `tenant_id=A` as a query parameter
   while authenticated as B — assert it's ignored and B still gets B's own results only.
