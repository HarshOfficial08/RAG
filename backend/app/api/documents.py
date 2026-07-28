import sqlite3
import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, status

from app.auth.dependencies import CurrentTenant
from app.ingestion.pipeline import run as run_ingestion
from app.models.schemas import DocumentPreview, DocumentRecord, DocumentStatus
from app.retrieval.vector_store import delete_document as delete_document_chunks
from app.retrieval.vector_store import get_document_chunks
from app.storage.db import get_connection

_UploadedFile = Annotated[UploadFile, File(...)]

router = APIRouter(prefix="/documents", tags=["documents"])


def _row_to_record(row: sqlite3.Row) -> DocumentRecord:
    return DocumentRecord(
        id=row["id"],
        filename=row["filename"],
        status=row["status"],
        uploaded_at=row["uploaded_at"],
        pii_masked=bool(row["pii_masked"]),
        failure_reason=row["failure_reason"],
    )


@router.get("")
async def list_documents(tenant: CurrentTenant) -> list[DocumentRecord]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM documents WHERE tenant_id = ? ORDER BY uploaded_at DESC", (tenant.tenant_id,)
    ).fetchall()
    conn.close()
    return [_row_to_record(row) for row in rows]


def _ingest(tenant_id: str, document_id: str, filename: str, file_bytes: bytes) -> None:
    status: DocumentStatus
    failure_reason: str | None
    try:
        pii_masked = run_ingestion(tenant_id, document_id, filename, file_bytes)
        status, failure_reason = "indexed", None
    except Exception as exc:
        # Any parse/mask/embed failure marks the document failed — it must
        # never be indexed partially or unmasked as a fallback.
        pii_masked, status, failure_reason = False, "failed", str(exc)

    conn = get_connection()
    conn.execute(
        "UPDATE documents SET status = ?, pii_masked = ?, failure_reason = ? "
        "WHERE id = ? AND tenant_id = ?",
        (status, int(pii_masked), failure_reason, document_id, tenant_id),
    )
    conn.commit()
    conn.close()


@router.post("")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: _UploadedFile,
    tenant: CurrentTenant,
) -> DocumentRecord:
    if tenant.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only an organization admin can upload documents",
        )
    document_id = str(uuid.uuid4())
    filename = file.filename or "unnamed"
    file_bytes = await file.read()

    record = DocumentRecord(
        id=document_id,
        filename=filename,
        status="processing",
        uploaded_at=datetime.now(UTC).isoformat(),
        pii_masked=False,
    )
    conn = get_connection()
    conn.execute(
        "INSERT INTO documents (id, tenant_id, filename, status, uploaded_at, pii_masked, "
        "failure_reason) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            record.id,
            tenant.tenant_id,
            record.filename,
            record.status,
            record.uploaded_at,
            int(record.pii_masked),
            record.failure_reason,
        ),
    )
    conn.commit()
    conn.close()

    background_tasks.add_task(_ingest, tenant.tenant_id, document_id, filename, file_bytes)
    return record


@router.get("/{document_id}/preview")
async def preview_document(document_id: str, tenant: CurrentTenant) -> DocumentPreview:
    conn = get_connection()
    row = conn.execute(
        "SELECT filename FROM documents WHERE id = ? AND tenant_id = ?",
        (document_id, tenant.tenant_id),
    ).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    chunks = get_document_chunks(tenant.tenant_id, document_id)
    text = "\n\n".join(c.text for c in chunks) or "(No preview available yet — still processing.)"
    return DocumentPreview(filename=row["filename"], text=text)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str, tenant: CurrentTenant) -> None:
    if tenant.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only an organization admin can delete documents",
        )
    conn = get_connection()
    existing = conn.execute(
        "SELECT 1 FROM documents WHERE id = ? AND tenant_id = ?", (document_id, tenant.tenant_id)
    ).fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    conn.execute(
        "DELETE FROM documents WHERE id = ? AND tenant_id = ?", (document_id, tenant.tenant_id)
    )
    conn.commit()
    conn.close()
    delete_document_chunks(tenant.tenant_id, document_id)
