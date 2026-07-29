"""Small OpenAI-compatible LLM client for research summaries and Q&A."""

from __future__ import annotations

import os
from typing import Any

import requests


def ai_is_configured() -> bool:
    return bool(os.getenv("LLM_API_KEY"))


def _chat(messages: list[dict[str, str]], temperature: float = 0.2) -> str:
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        raise RuntimeError("AI is not configured. Add LLM_API_KEY to your .env file.")

    endpoint = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1/chat/completions")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    response = requests.post(
        endpoint,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "messages": messages, "temperature": temperature},
        timeout=60,
    )
    response.raise_for_status()
    payload: dict[str, Any] = response.json()
    return payload["choices"][0]["message"]["content"].strip()


def research_brief(context: str) -> str:
    """Generate a concise, balanced research brief from supplied facts."""

    return _chat(
        [
            {
                "role": "system",
                "content": (
                    "You are a careful financial research assistant helping a high school student learn. "
                    "Use only the supplied data, label uncertainty, separate facts from interpretation, "
                    "and never present this as personalized financial advice. Use clear markdown headings."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Create a research brief with: business snapshot, recent performance, financial statement "
                    "signals, news themes, risks/questions to investigate, and a 3-sentence takeaway.\n\n"
                    f"DATA:\n{context}"
                ),
            },
        ]
    )


def answer_question(context: str, question: str) -> str:
    """Answer a user question using only the current research context."""

    return _chat(
        [
            {
                "role": "system",
                "content": (
                    "You answer questions about a company using only the provided research context. "
                    "If the answer is not in the context, say so. Explain calculations briefly, avoid hype, "
                    "and include a short reminder that this is educational information, not financial advice."
                ),
            },
            {
                "role": "user",
                "content": f"CONTEXT:\n{context}\n\nQUESTION:\n{question}",
            },
        ],
        temperature=0.1,
    )
