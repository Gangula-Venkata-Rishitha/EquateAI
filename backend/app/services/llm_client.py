"""Shared Ollama LLM client utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.config import settings


@dataclass
class LLMClient:
    """Thin wrapper around Ollama chat completions."""

    equation_model: str = settings.ollama_equation_model
    chat_model: str = settings.ollama_chat_model
    code_model: str = settings.ollama_code_model

    def _client(self):
        try:
            import ollama

            return ollama
        except ImportError:
            raise ImportError("ollama package required. pip install ollama")

    def chat(self, prompt: str, *, model: str | None = None, system: str | None = None) -> str:
        """Send a single-turn chat prompt to a model."""
        messages: list[dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        try:
            client = self._client()
            response = client.chat(model=model or self.chat_model, messages=messages)
            return response["message"]["content"].strip()
        except Exception as e:  # pragma: no cover - external dependency
            return f"LLM error: {e}"

