import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile

from app.auth.dependencies import TenantContext, get_current_tenant
from app.ingestion.pipeline import run as run_ingestion
from app.models.schemas import DocumentRecord, DocumentStatus

router = APIRouter(prefix="/documents", tags=["documents"])

# In-memory store: tenant_id -> document_id -> record. A real deployment would
# back this with a database, but the isolation contract (strictly keyed by
# tenant_id from the verified JWT) is the same shape either way.
_documents: dict[str, dict[str, DocumentRecord]] = {}


@router.get("", response_model=list[DocumentRecord])
async def list_documents(
    tenant: TenantContext = Depends(get_current_tenant),
) -> list[DocumentRecord]:
    return list(_documents.get(tenant.tenant_id, {}).values())


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

    existing = _documents[tenant_id][document_id]
    _documents[tenant_id][document_id] = existing.model_copy(
        update={"status": status, "pii_masked": pii_masked, "failure_reason": failure_reason}
    )


@router.post("", response_model=DocumentRecord)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    tenant: TenantContext = Depends(get_current_tenant),
) -> DocumentRecord:
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
    _documents.setdefault(tenant.tenant_id, {})[document_id] = record
    background_tasks.add_task(_ingest, tenant.tenant_id, document_id, filename, file_bytes)
    return record
