from fastapi import APIRouter, Depends, HTTPException, status

from app.api.audit import log_query
from app.auth.dependencies import TenantContext, get_current_tenant
from app.generation.llm_client import GenerationUnavailableError, OllamaCloudClient
from app.generation.prompt import RetrievedChunk, build_prompt
from app.masking.presidio_service import mask
from app.models.schemas import QueryRequest, QueryResponse, QuerySource
from app.retrieval.embeddings import embed
from app.retrieval.vector_store import search

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
async def ask_question(
    request: QueryRequest,
    tenant: TenantContext = Depends(get_current_tenant),
) -> QueryResponse:
    query_vector = embed(request.question)
    chunks = search(tenant.tenant_id, query_vector)

    masking_triggered = False
    retrieved: list[RetrievedChunk] = []
    for chunk in chunks:
        # Defense in depth: re-scan retrieved chunks even though they were
        # already masked at ingestion — see docs/plan/04-pii-masking.md.
        result = mask(chunk.text)
        masking_triggered = masking_triggered or result.triggered
        retrieved.append(RetrievedChunk(filename=chunk.filename, text=result.masked_text))

    if not retrieved:
        answer = (
            "I couldn't find anything relevant to that question in "
            "your organization's documents."
        )
    else:
        prompt = build_prompt(tenant.tenant_name, request.question, retrieved)
        try:
            answer = OllamaCloudClient().generate(prompt)
        except GenerationUnavailableError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
            ) from exc
        # Output re-scan, in case generation reconstructed something from context.
        output_result = mask(answer)
        masking_triggered = masking_triggered or output_result.triggered
        answer = output_result.masked_text

    log_query(tenant.tenant_id, tenant.user_id, request.question, masking_triggered)

    return QueryResponse(
        answer=answer,
        sources=[
            QuerySource(document_id=c.document_id, filename=c.filename, chunk_index=c.chunk_index)
            for c in chunks
        ],
    )
