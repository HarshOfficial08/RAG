# PII / Secret Masking (Presidio)

## Depends on
Nothing — this is a leaf module other pieces call into. Runs self-hosted, in-process;
no data ever leaves the backend to perform masking (see prior conversation note: this
matters because it's the layer that prevents PII from reaching the external LLM API,
not a third-party call itself).

## Components
- `presidio-analyzer` — detection: built-in recognizers (PERSON, EMAIL_ADDRESS,
  PHONE_NUMBER, CREDIT_CARD, US_SSN, IP_ADDRESS, etc.) via spaCy NER + regex + checksum
  validators.
- `presidio-anonymizer` — replaces detected spans with a token, e.g. `<EMAIL_ADDRESS>`,
  `<CLIENT_ID>`.

## Custom recognizers required (built-ins don't cover these — this is the actual work)
1. **Client ID** — regex pattern matching your document format, e.g. `CID-\d{4,8}` or
   whatever the real customer documents use. Write this against real sample data, don't
   guess the format.
2. **Password / secret-looking strings** — patterns like `password:\s*\S+`,
   `api[_-]?key:\s*\S+`, high-entropy token detection for things that look like secrets
   but don't match a known format.
3. Register both via `AnalyzerEngine().registry.add_recognizer(...)` — keep them in
   `masking/recognizers.py`, not inline in the pipeline code, so they're independently
   testable.

## Where masking runs (defense in depth, three places, not one)
1. **At ingestion** — full document text, before chunking/embedding/storage.
2. **At retrieval** — re-scan retrieved chunks before they go into the LLM prompt
   (catches anything missed at ingestion, or added via a later re-index).
3. **At output** — scan the LLM's generated answer before returning it to the user
   (LLMs can reconstruct or paraphrase PII from context even when the source chunk
   was masked).

## Known limitation to state upfront, not hide
Presidio is NER + regex, not a guarantee — it will miss novel formats and can
false-negative on messy OCR text. This is exactly why masking runs three times instead
of once; be ready to say this plainly if asked in the interview rather than claiming
100% coverage.

## Definition of done
- Unit tests feed known PII strings (email, phone, SSN, custom Client ID pattern,
  password-looking string) through the analyzer+anonymizer and assert masked output.
- A test with a document containing zero PII passes through unchanged (no
  over-masking of ordinary business text).
