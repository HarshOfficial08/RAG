"""Orchestrates parse -> mask -> chunk -> embed -> upsert.

See docs/plan/03-ingestion-pipeline.md. Masking runs on the full document text
before chunking (not per-chunk) — full-document context gives Presidio's NER
better accuracy than isolated fragments.
"""

from app.ingestion.chunker import chunk_text
from app.ingestion.parser import extract_text
from app.masking.presidio_service import mask
from app.retrieval.vector_store import upsert


def run(tenant_id: str, document_id: str, filename: str, file_bytes: bytes) -> bool:
    """Runs the full ingestion flow. Returns whether masking was triggered.

    Raises ValueError if the file has no extractable text — callers must treat
    that as an ingestion failure (status: failed), never index nothing while
    reporting success.
    """
    text = extract_text(file_bytes, filename)
    if not text.strip():
        raise ValueError("No extractable text found in document")

    mask_result = mask(text)
    chunks = chunk_text(mask_result.masked_text)
    upsert(tenant_id, document_id, filename, chunks)
    return mask_result.triggered
