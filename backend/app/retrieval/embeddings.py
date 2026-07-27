"""Embedding model wrapper (sentence-transformers). See docs/plan/03-ingestion-pipeline.md.

Loaded once as a module-level singleton — instantiating SentenceTransformer per
call would reload the model from disk on every request.
"""

from sentence_transformers import SentenceTransformer

from app.config import settings

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def embed(text: str) -> list[float]:
    vector = _get_model().encode(text, normalize_embeddings=True)
    return [float(x) for x in vector]


def vector_size() -> int:
    dimension = _get_model().get_embedding_dimension()
    if dimension is None:
        raise RuntimeError(
            f"Model {settings.embedding_model!r} did not report an embedding dimension"
        )
    return dimension
