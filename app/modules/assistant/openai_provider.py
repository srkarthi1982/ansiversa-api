from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"

SYSTEM_INSTRUCTIONS = """You are Ansiversa AI, a concise platform assistant.
Ansiversa is a fixed ecosystem of exactly 100 carefully curated solution apps.
The supplied context is your only factual authority.
Do not guess unsupported facts, routes, prices, policies, features, or availability.
Do not browse repositories, mention internal systems, or reveal operational details.
Use only the permitted action labels from the context when suggesting navigation.
If the supplied context is insufficient, acknowledge uncertainty and suggest browsing Apps or FAQ.
Do not provide legal, medical, financial, emergency, professional, or guaranteed advice.
Keep responses practical, user-facing, and brief."""


class OpenAIProviderError(RuntimeError):
    """Raised when the assistant cannot obtain a usable OpenAI response."""


def _extract_response_text(data: dict[str, Any]) -> str:
    output_text = data.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    parts: list[str] = []
    output = data.get("output")
    if isinstance(output, list):
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for content_item in content:
                if not isinstance(content_item, dict):
                    continue
                text = content_item.get("text")
                if isinstance(text, str) and text.strip():
                    parts.append(text.strip())

    return "\n".join(parts).strip()


class OpenAIResponseProvider:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else settings.OPENAI_API_KEY
        self.model = model or settings.ASSISTANT_OPENAI_MODEL
        self.timeout_seconds = timeout_seconds or settings.ASSISTANT_OPENAI_TIMEOUT_SECONDS
        self.max_output_tokens = max_output_tokens or settings.ASSISTANT_OPENAI_MAX_OUTPUT_TOKENS
        self.temperature = (
            temperature if temperature is not None else settings.ASSISTANT_OPENAI_TEMPERATURE
        )

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and settings.AI_GATEWAY_ENABLED and settings.ASSISTANT_OPENAI_ENABLED)

    def generate_answer(self, question: str, context: str) -> str | None:
        if not self.is_configured:
            return None

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(
                    OPENAI_RESPONSES_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "instructions": SYSTEM_INSTRUCTIONS,
                        "input": (
                            f"User question:\n{question}\n\n"
                            f"Approved public Ansiversa context:\n{context}"
                        ),
                        "max_output_tokens": self.max_output_tokens,
                        "temperature": self.temperature,
                    },
                )
                response.raise_for_status()
                answer = _extract_response_text(response.json())
        except (httpx.HTTPError, ValueError) as exc:
            raise OpenAIProviderError("Assistant provider unavailable.") from exc

        if not answer:
            raise OpenAIProviderError("Assistant provider returned an empty answer.")

        return answer
