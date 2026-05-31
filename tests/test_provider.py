import json
import os
import unittest
from unittest.mock import patch

from cognitive_os.provider import (
    OpenAIProvider,
    ProviderConfigurationError,
    get_provider,
)


class OpenAIProviderTests(unittest.TestCase):
    def test_openai_provider_requires_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ProviderConfigurationError):
                OpenAIProvider().generate("Hello")

    def test_openai_provider_requires_explicit_model(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            with self.assertRaises(ProviderConfigurationError):
                OpenAIProvider().generate("Hello")

    def test_openai_provider_uses_responses_payload_and_extracts_output_text(self):
        calls = []

        def fake_transport(url, headers, body, timeout):
            calls.append(
                {
                    "url": url,
                    "headers": dict(headers),
                    "payload": json.loads(body.decode("utf-8")),
                    "timeout": timeout,
                }
            )
            return {"output_text": "Candidate from OpenAI"}

        provider = OpenAIProvider(
            model="gpt-test",
            api_key="test-key",
            base_url="https://example.test/v1",
            transport=fake_transport,
        )
        candidate = provider.generate("Write a draft")

        self.assertEqual(candidate.response, "Candidate from OpenAI")
        self.assertEqual(candidate.provider, "openai:gpt-test")
        self.assertEqual(calls[0]["url"], "https://example.test/v1/responses")
        self.assertEqual(
            calls[0]["payload"],
            {"model": "gpt-test", "input": "Write a draft", "store": False},
        )
        self.assertEqual(calls[0]["headers"]["Authorization"], "Bearer test-key")

    def test_get_provider_supports_openai_model_suffix(self):
        provider = get_provider("openai:gpt-test")
        self.assertIsInstance(provider, OpenAIProvider)
        self.assertEqual(provider.model, "gpt-test")

    def test_openai_provider_env_controls_store_model_and_timeout(self):
        calls = []

        def fake_transport(url, headers, body, timeout):
            calls.append({"payload": json.loads(body.decode("utf-8")), "timeout": timeout})
            return {"output_text": "ok"}

        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "test-key",
                "OPENAI_MODEL": "gpt-env",
                "OPENAI_STORE": "true",
                "OPENAI_TIMEOUT": "12.5",
            },
            clear=True,
        ):
            OpenAIProvider(transport=fake_transport).generate("Hello")

        self.assertEqual(calls[0]["payload"]["model"], "gpt-env")
        self.assertEqual(calls[0]["payload"]["store"], True)
        self.assertEqual(calls[0]["timeout"], 12.5)

    def test_openai_integration_smoke_skips_without_api_key(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            self.skipTest("OPENAI_API_KEY is not set")
        if os.environ.get("COGNITIVE_OS_RUN_OPENAI_INTEGRATION") != "1":
            self.skipTest("Set COGNITIVE_OS_RUN_OPENAI_INTEGRATION=1 to call OpenAI")
        model = os.environ.get("OPENAI_MODEL")
        if not model:
            self.skipTest("OPENAI_MODEL is not set")
        provider = OpenAIProvider(
            api_key=api_key, model=model, timeout_seconds=30.0, store=False
        )
        candidate = provider.generate("Reply with the single word: ok")
        self.assertTrue(candidate.response)


if __name__ == "__main__":
    unittest.main()
