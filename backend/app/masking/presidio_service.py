"""PII/secret masking via Microsoft Presidio. See docs/plan/04-pii-masking.md.

Masking runs at three points in the wider system (ingestion, retrieval, output)
— see the plan doc for why a single pass isn't sufficient. This module is the
one shared implementation all three call into.

Runs entirely in-process against a local spaCy model — no network call, no
data leaves the backend to perform masking.
"""

from dataclasses import dataclass

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine

from app.masking.recognizers import CUSTOM_RECOGNIZERS

_NLP_CONFIGURATION = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
}

# DATE_TIME is deliberately excluded: Presidio's default recognizer flags any
# duration or date-like phrase (verified: it masked "30 days" in an ordinary
# refund-policy sentence), which isn't PII per the case study's actual
# requirements (passwords, client IDs, PII like names/emails/SSNs) and
# directly degrades RAG answer quality by redacting the fact being asked
# about. Revisit if real customer documents show a genuine need for it.
_EXCLUDED_ENTITIES = {"DATE_TIME"}

_analyzer: AnalyzerEngine | None = None
# presidio_anonymizer ships without a fully-typed constructor signature.
_anonymizer = AnonymizerEngine()  # type: ignore[no-untyped-call]


def _build_analyzer() -> AnalyzerEngine:
    nlp_engine = NlpEngineProvider(nlp_configuration=_NLP_CONFIGURATION).create_engine()
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
    for recognizer in CUSTOM_RECOGNIZERS:
        analyzer.registry.add_recognizer(recognizer)
    return analyzer


_active_entities: list[str] | None = None


def _get_analyzer() -> AnalyzerEngine:
    global _analyzer, _active_entities
    if _analyzer is None:
        _analyzer = _build_analyzer()
        _active_entities = [
            e for e in _analyzer.get_supported_entities() if e not in _EXCLUDED_ENTITIES
        ]
    return _analyzer


@dataclass(frozen=True)
class MaskResult:
    masked_text: str
    triggered: bool


def mask(text: str) -> MaskResult:
    if not text.strip():
        return MaskResult(masked_text=text, triggered=False)

    analyzer = _get_analyzer()
    results = analyzer.analyze(text=text, language="en", entities=_active_entities)
    if not results:
        return MaskResult(masked_text=text, triggered=False)

    # presidio_anonymizer's own type stub for `analyzer_results` names its
    # package-local RecognizerResult, but passing presidio_analyzer's results
    # directly is Presidio's own documented usage pattern and works correctly
    # (verified at runtime) — the two classes are structurally identical.
    anonymized = _anonymizer.anonymize(text=text, analyzer_results=results)  # type: ignore[arg-type]
    return MaskResult(masked_text=anonymized.text, triggered=True)
