# Ingestion Pipeline

## Depends on
`04-pii-masking.md` (must run before chunking), `05-tenant-isolation-vector-store.md`
(upsert target)

## Flow
1. Receive file (PDF/DOCX/TXT) + `tenant_id` (from auth layer) + `document_id` (new uuid).
2. Extract text — use **Docling** (handles PDF/DOCX/tables well, actively maintained) or
   fall back to PyMuPDF for plain PDFs if Docling is overkill for the prototype timeline.
3. Run the **masking module** over the full extracted text (not per-chunk yet — full
   document context gives Presidio's NER better accuracy than isolated fragments).
4. Chunk the masked text (target ~500 tokens, ~50 token overlap — simple recursive
   character/token splitter, no need for anything fancier at prototype scale).
5. Embed each chunk (`sentence-transformers`, e.g. `bge-small-en-v1.5`).
6. Upsert to Qdrant via the vector store module: `upsert(tenant_id, document_id, chunks)`.
7. Update document status: `processing` → `indexed` (or `failed` with a reason).

## Async handling
Steps 2-6 run as a FastAPI `BackgroundTask` (or a simple in-process queue if you want to
demonstrate a slightly more realistic pattern) so the upload endpoint returns
immediately. Document status is polled via `GET /documents`.

## Failure modes to handle explicitly
- Corrupt/unreadable file → status `failed`, reason stored, never silently drops it.
- Empty extracted text (e.g. scanned image PDF with no OCR) → status `failed`, clear
  reason ("no extractable text"), don't index an empty chunk.
- Presidio raising on unexpected input → fail the document, don't skip masking and
  index raw text as a fallback. Masking failing closed (reject) not open (index
  anyway) is the correct default for this requirement.

## Definition of done
- Uploading a PDF with a fake SSN/email/"Client ID: CID-12345" string results in
  masked tokens in the indexed chunks (verify by querying Qdrant directly, not just
  through the chat UI).
- A corrupted file upload ends in `status: failed`, not a silent no-op or a crash.
