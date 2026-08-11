"""Thin wrapper around the Anthropic SDK.

Handles the model-specific rules so the rest of the code doesn't have to:
- claude-fable-5: thinking is always on (omit the param), no sampling params,
  and requests can come back with stop_reason == "refusal" — we surface that
  as a typed error instead of crashing on empty content.
- Structured outputs via output_config.format (json_schema).
- Server-side web search with pause_turn continuation.
"""

from __future__ import annotations

import json

from anthropic import Anthropic


class RefusalError(RuntimeError):
    pass


class LLM:
    def __init__(self, model: str):
        self.client = Anthropic()
        self.model = model

    # -- internals ---------------------------------------------------------

    @staticmethod
    def _check_refusal(response) -> None:
        if response.stop_reason == "refusal":
            details = getattr(response, "stop_details", None)
            category = getattr(details, "category", None) if details else None
            raise RefusalError(f"model declined the request (category={category})")

    @staticmethod
    def _text(response) -> str:
        return "".join(b.text for b in response.content if b.type == "text")

    # -- public API --------------------------------------------------------

    def ask(self, prompt: str, *, system: str | None = None,
            max_tokens: int = 8000, effort: str = "high") -> str:
        kwargs: dict = dict(
            model=self.model,
            max_tokens=max_tokens,
            output_config={"effort": effort},
            messages=[{"role": "user", "content": prompt}],
        )
        if system:
            kwargs["system"] = system
        response = self.client.messages.create(**kwargs)
        self._check_refusal(response)
        return self._text(response)

    def ask_json(self, prompt: str, schema: dict, *, system: str | None = None,
                 max_tokens: int = 8000, effort: str = "high") -> dict:
        """Structured output constrained to the given JSON schema."""
        kwargs: dict = dict(
            model=self.model,
            max_tokens=max_tokens,
            output_config={
                "effort": effort,
                "format": {"type": "json_schema", "schema": schema},
            },
            messages=[{"role": "user", "content": prompt}],
        )
        if system:
            kwargs["system"] = system
        response = self.client.messages.create(**kwargs)
        self._check_refusal(response)
        return json.loads(self._text(response))

    def ask_with_web_search(self, prompt: str, *, max_tokens: int = 16000,
                            effort: str = "high", max_continuations: int = 5) -> str:
        """Run a prompt with the server-side web search tool, continuing
        through pause_turn until the model finishes."""
        messages: list[dict] = [{"role": "user", "content": prompt}]
        tools = [{"type": "web_search_20260209", "name": "web_search"}]
        for _ in range(max_continuations):
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                output_config={"effort": effort},
                tools=tools,
                messages=messages,
            )
            self._check_refusal(response)
            if response.stop_reason == "pause_turn":
                messages.append({"role": "assistant", "content": response.content})
                continue
            return self._text(response)
        return self._text(response)
