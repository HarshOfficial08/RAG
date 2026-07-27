"""Proves tenant isolation at the actual vector store, not just the in-memory
API layer (see tests/test_tenant_isolation.py for that version). This is the
literal grading requirement from the case study — see docs/plan/05.
"""

import uuid

from app.retrieval.embeddings import embed
from app.retrieval.vector_store import search, upsert


def test_search_never_returns_other_tenants_chunks() -> None:
    marker = f"UNIQUE-MARKER-{uuid.uuid4().hex[:12]}"
    tenant_a = f"tenant-iso-a-{uuid.uuid4().hex[:8]}"
    tenant_b = f"tenant-iso-b-{uuid.uuid4().hex[:8]}"

    upsert(tenant_a, "doc-a", "a.txt", [f"{marker} belongs to tenant A only."])
    upsert(tenant_b, "doc-b", "b.txt", ["Unrelated content for tenant B."])

    query_vector = embed(marker)

    results_a = search(tenant_a, query_vector, k=5)
    results_b = search(tenant_b, query_vector, k=5)

    assert any(marker in c.text for c in results_a)
    assert not any(marker in c.text for c in results_b), (
        "tenant B must never see tenant A's chunk, even for a semantically "
        "identical query vector"
    )


def test_search_ignores_empty_result_gracefully() -> None:
    tenant = f"tenant-empty-{uuid.uuid4().hex[:8]}"
    query_vector = embed("anything")
    assert search(tenant, query_vector, k=5) == []
