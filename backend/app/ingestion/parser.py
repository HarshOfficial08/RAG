"""Document text extraction. See docs/plan/03-ingestion-pipeline.md.

Supports the three formats named in the case study: PDF, DOCX, TXT.
"""

import io

import pymupdf
from docx import Document as DocxDocument


def extract_text(file_bytes: bytes, filename: str) -> str:
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if suffix == "pdf":
        return _extract_pdf(file_bytes)
    if suffix == "docx":
        return _extract_docx(file_bytes)
    if suffix == "txt":
        return file_bytes.decode("utf-8", errors="replace")

    raise ValueError(f"Unsupported file type: .{suffix or 'unknown'}")


def _extract_pdf(file_bytes: bytes) -> str:
    # pymupdf.open is an alias for its untyped Document constructor.
    with pymupdf.open(stream=file_bytes, filetype="pdf") as doc:  # type: ignore[no-untyped-call]
        return "\n".join(page.get_text() for page in doc)


def _extract_docx(file_bytes: bytes) -> str:
    doc = DocxDocument(io.BytesIO(file_bytes))
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)
