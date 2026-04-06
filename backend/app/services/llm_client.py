"""Shared Ollama LLM client utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.config import settings
from app.services.domain_guard import DomainGuard, OUT_OF_SCOPE_MESSAGE


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

    def chat(
        self,
        prompt: str,
        *,
        model: str | None = None,
        system: str | None = None,
        query: str | None = None,
        domain_context: str | None = None,
        require_context: bool = False,
    ) -> str:
        """Send a single-turn chat prompt to a model."""
        guard = DomainGuard()
        guard_check = guard.check(
            query=query or prompt,
            context=domain_context,
            require_context=require_context,
        )
        if not guard_check.allowed:
            return guard_check.reason or OUT_OF_SCOPE_MESSAGE

        messages: list[dict[str, Any]] = []
        messages.append(
            {
                "role": "system",
                "content": system or guard.build_system_prompt(context=domain_context),
            }
        )
        messages.append({"role": "user", "content": prompt})
        try:
            client = self._client()
            response = client.chat(model=model or self.chat_model, messages=messages)
            return response["message"]["content"].strip()
        except Exception as e:  # pragma: no cover - external dependency
            return f"LLM error: {e}"

