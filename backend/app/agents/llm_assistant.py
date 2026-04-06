"""LLM Assistant Agent - equation explanation and chat via Ollama."""
from app.core.config import settings
from app.services.domain_guard import DomainGuard, OUT_OF_SCOPE_MESSAGE


class LLMAssistantAgent:
    """Use Ollama for equation explanation and document Q&A."""

    def __init__(self):
        self._host = settings.ollama_host
        self._equation_model = settings.ollama_equation_model
        self._chat_model = settings.ollama_chat_model
        self._guard = DomainGuard()

    def _client(self):
        try:
            import ollama
            return ollama
        except ImportError:
            raise ImportError("ollama package required. pip install ollama")

    def explain_equation(self, equation_text: str, context: str | None = None) -> str:
        """Get natural language explanation of an equation from LLM."""
        guard_check = self._guard.check(
            query=f"Explain equation: {equation_text}",
            context=f"Equation: {equation_text}\n{context or ''}",
            require_context=False,
        )
        if not guard_check.allowed:
            return guard_check.reason or OUT_OF_SCOPE_MESSAGE

        prompt = f"""Explain the following scientific/mathematical equation in simple terms. Be concise (2-4 sentences).
Equation: {equation_text}
"""
        if context:
            prompt += f"\nContext: {context}\n"
        try:
            client = self._client()
            response = client.chat(
                model=self._equation_model,
                messages=[
                    {
                        "role": "system",
                        "content": self._guard.build_system_prompt(
                            context=f"Equation: {equation_text}\n{context or ''}"
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            return response["message"]["content"].strip()
        except Exception as e:
            return f"Could not get explanation (Ollama may be unavailable): {e}"

    def chat(self, message: str, document_context: str | None = None, history: list[dict] | None = None) -> str:
        """Chat about document/equations. document_context can be summary of equations and text."""
        guard_check = self._guard.check(
            query=message,
            context=document_context,
            require_context=True,
        )
        if not guard_check.allowed:
            return guard_check.reason or OUT_OF_SCOPE_MESSAGE

        messages = []
        messages.append(
            {
                "role": "system",
                "content": self._guard.build_system_prompt(context=document_context),
            }
        )
        if history:
            for h in history[-10:]:  # last 10 turns
                messages.append({"role": h.get("role", "user"), "content": h.get("content", h.get("message", ""))})
        messages.append({"role": "user", "content": message})
        try:
            client = self._client()
            response = client.chat(model=self._chat_model, messages=messages)
            return response["message"]["content"].strip()
        except Exception as e:
            return f"Could not get response (Ollama may be unavailable): {e}"
