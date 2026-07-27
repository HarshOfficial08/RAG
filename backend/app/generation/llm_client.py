"""Ollama Cloud generation client. See docs/plan/07-rag-generation.md.

Keeps the provider-specific request shape isolated to this one file — if the
model provider changes later, only this module changes.
"""

from typing import Protocol

import httpx

from app.config import settings


class LLMClient(Protocol):
    def generate(self, prompt: str) -> str: ...


class GenerationUnavailableError(Exception):
    """Raised when the configured LLM can't be reached or isn't configured.

    Distinct from a generic exception so the API layer can return a clear
    503 instead of an opaque 500 — an unconfigured/unreachable provider is an
    operational condition, not a bug.
    """


class OllamaCloudClient:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.ollama_api_key
        self.model = model or settings.ollama_model

    def generate(self, prompt: str) -> str:
        if not self.api_key:
            raise GenerationUnavailableError(
                "OLLAMA_API_KEY is not configured — set it in .env to enable generation."
            )

        try:
            response = httpx.post(
                "https://ollama.com/api/chat",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return str(data["message"]["content"])
        except httpx.HTTPError as exc:
            raise GenerationUnavailableError(f"Ollama Cloud request failed: {exc}") from exc
