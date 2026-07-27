"""Splits masked document text into overlapping chunks for embedding.

Word-count based (not a real tokenizer) — good enough for a prototype corpus;
swap for a proper tokenizer-aware splitter if chunk-size accuracy matters later.
See docs/plan/03-ingestion-pipeline.md.
"""


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start = end - overlap
    return chunks
