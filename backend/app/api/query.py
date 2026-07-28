import re

from fastapi import APIRouter, HTTPException, status

from app.api.audit import log_query
from app.auth.dependencies import CurrentTenant
from app.generation.llm_client import GenerationUnavailableError, OllamaCloudClient
from app.generation.prompt import RetrievedChunk, build_prompt
from app.masking.presidio_service import mask
from app.models.schemas import QueryRequest, QueryResponse, QuerySource
from app.retrieval.embeddings import embed
from app.retrieval.vector_store import search

router = APIRouter(tags=["query"])

# Greetings/self-referential small talk never carries enough embedding
# signal to reliably fall below the relevance threshold (a generic "hi" can
# score above 0.35 against almost anything), which was surfacing as a cold
# "I don't have information on that" plus bogus source citations. Handled
# deterministically before retrieval — this is pure UX politeness and
# doesn't touch the actual document-grounding guardrail below.
_SMALL_TALK = re.compile(
    r"^\s*(hi|hello|hey|yo|hiya|sup|good\s(morning|afternoon|evening)|"
    r"who are you|what are you|what can you do|what is this( app| tool)?|"
    r"how does this work|help)\s*[!.?]*\s*$",
    re.IGNORECASE,
)
_FRIENDLY_INTRO = (
    "Hi! I'm the SecureRAG assistant. Ask me anything about the documents "
    "your organization has uploaded — I'll answer strictly from that "
    "content, and I'll say so if something isn't covered, rather than "
    "guessing."
)


@router.post("/query")
async def ask_question(request: QueryRequest, tenant: CurrentTenant) -> QueryResponse:
    if _SMALL_TALK.match(request.question):
        masked_question = mask(request.question)
        log_query(tenant.tenant_id, tenant.user_id, masked_question.masked_text, False)
        return QueryResponse(answer=_FRIENDLY_INTRO, sources=[])

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
            "I couldn't find anything about that in your organization's documents "
            "yet — feel free to try rephrasing, or ask about something else that's "
            "been uploaded."
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

    # Mask the question itself before logging — a user could type PII in
    # their question (e.g. "What is Sarah's SSN?") and we must not persist
    # that raw to the audit trail.
    masked_question_result = mask(request.question)
    masking_triggered = masking_triggered or masked_question_result.triggered
    log_query(tenant.tenant_id, tenant.user_id, masked_question_result.masked_text, masking_triggered)

    # Dedupe by document_id — repeated uploads of the same-named file (or
    # multiple chunks from one document) shouldn't show the same citation
    # over and over in the UI.
    seen_documents: set[str] = set()
    sources: list[QuerySource] = []
    for c in chunks:
        if c.document_id in seen_documents:
            continue
        seen_documents.add(c.document_id)
        sources.append(
            QuerySource(document_id=c.document_id, filename=c.filename, chunk_index=c.chunk_index)
        )

    return QueryResponse(answer=answer, sources=sources)
