"""Prompt construction for the generation step. See docs/plan/07-rag-generation.md."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievedChunk:
    filename: str
    text: str


def build_prompt(tenant_name: str, question: str, chunks: list[RetrievedChunk]) -> str:
    excerpts = "\n\n".join(f"[{c.filename}]\n{c.text}" for c in chunks)
    return (
        f"You are answering questions using ONLY the provided document excerpts "
        f"from {tenant_name}.\n"
        "If the answer isn't in the excerpts, say so — do not use outside knowledge.\n\n"
        f"Excerpts:\n{excerpts}\n\n"
        f"Question: {question}"
    )
