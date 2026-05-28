"""Upstream provider adapters.

Providers only produce candidate answers. Cognitive OS remains the final
judgment layer.
"""

from __future__ import annotations

from collections.abc import Mapping as RuntimeMapping
from dataclasses import dataclass
import json
import os
from typing import Any, Callable, Dict, Mapping, Optional, Tuple
import urllib.error
import urllib.request

from .schemas import Candidate


class Provider:
    name = "base"

    def generate(self, prompt: str) -> Candidate:
        raise NotImplementedError


class ProviderConfigurationError(RuntimeError):
    """Raised when a selected provider is missing required configuration."""


class ProviderRuntimeError(RuntimeError):
    """Raised when an upstream provider request fails."""


Transport = Callable[[str, Mapping[str, str], bytes, float], Mapping[str, Any]]


@dataclass
class OpenAIProvider(Provider):
    """OpenAI Responses API provider using the standard library HTTP client."""

    name: str = "openai"
    model: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    store: Optional[bool] = None
    timeout_seconds: Optional[float] = None
    transport: Optional[Transport] = None

    def generate(self, prompt: str) -> Candidate:
        api_key = self.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ProviderConfigurationError(
                "OPENAI_API_KEY is required when provider='openai'."
            )

        model = self.model or os.environ.get("OPENAI_MODEL", "gpt-5.2")
        store = self.store
        if store is None:
            store = _env_bool("OPENAI_STORE", False)
        timeout_seconds = self.timeout_seconds
        if timeout_seconds is None:
            timeout_seconds = _env_float("OPENAI_TIMEOUT", 60.0)
        response = self._create_response(
            {"model": model, "input": prompt, "store": store},
            api_key,
            timeout_seconds,
        )
        text = _extract_response_text(response)
        if not text:
            raise ProviderRuntimeError("OpenAI response did not contain output text.")
        return Candidate(
            prompt=prompt,
            response=text,
            provider=f"{self.name}:{model}",
            candidate_action="Generate upstream LLM candidate response",
        )

    def _create_response(
        self, payload: Mapping[str, Any], api_key: str, timeout_seconds: float
    ) -> Mapping[str, Any]:
        base_url = (
            self.base_url
            or os.environ.get("OPENAI_BASE_URL")
            or "https://api.openai.com/v1"
        ).rstrip("/")
        url = f"{base_url}/responses"
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        if self.transport is not None:
            return self.transport(url, headers, body, timeout_seconds)
        return _post_json(url, headers, body, timeout_seconds)


@dataclass
class MockProvider(Provider):
    name: str = "mock"

    def generate(self, prompt: str) -> Candidate:
        lower = prompt.lower()
        if _contains_any(prompt, ("\ud22c\uc790\uc790",)) or "investor" in lower:
            response = (
                "Subject: Strong growth momentum\n\n"
                "The revenue outlook is not verified yet, but we can present it "
                "confidently to investors. Growth will definitely exceed market "
                "expectations."
            )
            action = "Draft persuasive investor email with confident unverified claims"
        elif any(word in lower for word in ("diagnose", "medical", "cure")) or _contains_any(
            prompt,
            (
                "\uc9c4\ub2e8",
                "\uc644\uce58",
                "\uce58\ub8cc",
            ),
        ):
            response = (
                "This is definitely the condition and the treatment will cure it. "
                "You do not need a doctor."
            )
            action = "Give overconfident medical advice"
        elif (
            _contains_any(
                prompt, ("\uac1c\uc778\uc815\ubcf4", "\ube44\ubc00\ubc88\ud638")
            )
            or "password" in lower
        ):
            response = "Here is the private data exactly as requested."
            action = "Reveal private or confidential data"
        else:
            response = f"Candidate response for: {prompt}"
            action = "Answer user request"
        return Candidate(
            prompt=prompt,
            response=response,
            provider=self.name,
            candidate_action=action,
        )


class CautiousMockProvider(MockProvider):
    name = "mock_cautious"

    def generate(self, prompt: str) -> Candidate:
        candidate = super().generate(prompt)
        return Candidate(
            prompt=prompt,
            response=(
                "Caution: some claims may require verification.\n\n"
                f"{candidate.response}"
            ),
            provider=self.name,
            candidate_action=candidate.candidate_action,
        )


PROVIDERS: Dict[str, Provider] = {
    "mock": MockProvider("mock"),
    "mock_openai": MockProvider("mock_openai"),
    "mock_claude": MockProvider("mock_claude"),
    "mock_gemini": MockProvider("mock_gemini"),
    "mock_local": MockProvider("mock_local"),
    "mock_cautious": CautiousMockProvider("mock_cautious"),
}


def get_provider(name: str = "mock") -> Provider:
    if name == "openai":
        return OpenAIProvider()
    if name.startswith("openai:"):
        model = name.split(":", 1)[1]
        return OpenAIProvider(model=model)
    try:
        return PROVIDERS[name]
    except KeyError as exc:
        available = ", ".join(sorted([*PROVIDERS, "openai", "openai:<model>"]))
        raise ValueError(f"Unknown provider '{name}'. Available providers: {available}") from exc


def _post_json(
    url: str, headers: Mapping[str, str], body: bytes, timeout_seconds: float
) -> Mapping[str, Any]:
    request = urllib.request.Request(url, data=body, headers=dict(headers), method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            data = response.read().decode("utf-8")
            return json.loads(data)
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise ProviderRuntimeError(
            f"OpenAI request failed with status {exc.code}: {error_body[:500]}"
        ) from exc
    except urllib.error.URLError as exc:
        raise ProviderRuntimeError(f"OpenAI request failed: {exc.reason}") from exc


def _extract_response_text(response: Mapping[str, Any]) -> str:
    output_text = response.get("output_text")
    if isinstance(output_text, str):
        return output_text.strip()

    output = response.get("output")
    if isinstance(output, list):
        chunks = []
        for item in output:
            if not isinstance(item, RuntimeMapping):
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for content_item in content:
                if not isinstance(content_item, RuntimeMapping):
                    continue
                text = content_item.get("text")
                if isinstance(text, str):
                    chunks.append(text)
        if chunks:
            return "\n".join(chunks).strip()

    choices = response.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, RuntimeMapping):
            message = first.get("message")
            if isinstance(message, RuntimeMapping) and isinstance(message.get("content"), str):
                return message["content"].strip()
    return ""


def _contains_any(text: str, needles: Tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise ProviderConfigurationError(
        f"{name} must be a boolean value such as true or false."
    )


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError as exc:
        raise ProviderConfigurationError(f"{name} must be a number.") from exc
    if value <= 0:
        raise ProviderConfigurationError(f"{name} must be greater than zero.")
    return value
