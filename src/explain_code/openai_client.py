"""OpenAI API client wrapper for code explanation."""

from __future__ import annotations

import json
import re
from typing import Any

from openai import OpenAI

from explain_code.config import Settings
from explain_code.errors import ConfigurationError, OpenAIResponseError
from explain_code.models import CodeTarget, ComplexityReport, ExplanationResult
from explain_code.prompting import SYSTEM_PROMPT, build_user_prompt


class OpenAIExplainer:
    """Handles requests to OpenAI and converts output into typed results."""

    def __init__(self, settings: Settings) -> None:
        if not settings.api_key:
            raise ConfigurationError(
                "OPENAI_API_KEY is not set. Export it before running explain-code."
            )

        self.client = OpenAI(api_key=settings.api_key)
        self.model = settings.model
        self.temperature = settings.temperature

    def explain(
        self, target: CodeTarget, static_complexity: ComplexityReport
    ) -> ExplanationResult:
        content = self._request_chat_completion(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=build_user_prompt(target=target, complexity=static_complexity),
        )
        payload = self._parse_json_payload(content)
        return ExplanationResult.from_model_payload(
            payload=payload, static_complexity=static_complexity
        )

    def _request_chat_completion(self, system_prompt: str, user_prompt: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=messages,
                response_format={"type": "json_object"},
            )
        except Exception as first_exc:
            # Fallback for models/endpoints that do not support JSON mode.
            if "response_format" not in str(first_exc):
                raise OpenAIResponseError(f"OpenAI request failed: {first_exc}") from first_exc
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    temperature=self.temperature,
                    messages=messages,
                )
            except Exception as second_exc:
                raise OpenAIResponseError(f"OpenAI request failed: {second_exc}") from second_exc

        content = response.choices[0].message.content if response.choices else ""
        if not content:
            raise OpenAIResponseError("Received an empty response from OpenAI.")
        return content

    def _parse_json_payload(self, raw: str) -> dict[str, Any]:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.DOTALL)

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
            if not match:
                raise OpenAIResponseError(
                    "OpenAI response was not valid JSON."
                ) from None
            try:
                parsed = json.loads(match.group(0))
            except json.JSONDecodeError as exc:
                raise OpenAIResponseError(
                    "OpenAI response contained malformed JSON."
                ) from exc

        if not isinstance(parsed, dict):
            raise OpenAIResponseError("OpenAI response JSON must be an object.")
        return parsed

