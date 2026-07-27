"""Custom Presidio recognizers not covered by the built-ins.

See docs/plan/04-pii-masking.md. Patterns here approximate a generic customer
document format (a "CID-NNNNN" client identifier, and password/secret-looking
`key: value` lines) — tune the regex against real sample documents before
relying on this for anything beyond the prototype.
"""

from presidio_analyzer import Pattern, PatternRecognizer

CLIENT_ID_RECOGNIZER = PatternRecognizer(
    supported_entity="CLIENT_ID",
    patterns=[Pattern(name="client_id", regex=r"\bCID-\d{4,8}\b", score=0.9)],
)

SECRET_RECOGNIZER = PatternRecognizer(
    supported_entity="SECRET",
    patterns=[
        Pattern(
            name="password_or_key",
            regex=r"(?i)\b(password|api[_-]?key|secret|token)\s*[:=]\s*\S+",
            score=0.85,
        ),
    ],
)

# Backstop for presidio-analyzer's built-in EMAIL_ADDRESS recognizer, which
# silently fails to match long/uncommon TLDs (verified: it misses
# "x@acme-corp.example" but correctly matches "x@acme-corp.com" — RFC 2606
# reserved TLDs like .example, .test, .invalid are exactly where this shows
# up). Reuses the same entity type so it produces the same <EMAIL_ADDRESS>
# mask token and doesn't create a second, differently-labeled finding for the
# same span.
EMAIL_FALLBACK_RECOGNIZER = PatternRecognizer(
    supported_entity="EMAIL_ADDRESS",
    patterns=[
        Pattern(
            name="email_permissive_tld",
            regex=r"\b[\w.+-]+@[\w-]+\.[A-Za-z]{2,24}\b",
            score=0.6,
        )
    ],
)

CUSTOM_RECOGNIZERS = [CLIENT_ID_RECOGNIZER, SECRET_RECOGNIZER, EMAIL_FALLBACK_RECOGNIZER]
