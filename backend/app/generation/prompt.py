"""Prompt construction for the generation step. See docs/plan/07-rag-generation.md."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievedChunk:
    filename: str
    text: str


def build_prompt(tenant_name: str, question: str, chunks: list[RetrievedChunk]) -> str:
    excerpts = "\n\n".join(f"[{c.filename}]\n{c.text}" for c in chunks)
    return (
        f"You are a helpful assistant answering questions using ONLY the provided "
        f"document excerpts from {tenant_name}. Be warm and conversational in tone — "
        "this is a real person you're helping, not a form to fill out.\n"
        "If the answer isn't in the excerpts, say so plainly and kindly — don't guess, "
        "and don't use outside knowledge — but don't be curt about it either.\n\n"
        f"Excerpts:\n{excerpts}\n\n"
        f"Question: {question}"
    )
