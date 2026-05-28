import unittest

from cognitive_os.conformance import validate_decision_envelope
from cognitive_os.protocol import build_decision_envelope, stable_text_hash
from cognitive_os.runtime import run_prompt


INVESTOR_PROMPT = "Tell investors an unverified revenue forecast confidently."


class ProtocolTests(unittest.TestCase):
    def test_runtime_emits_conformant_redacted_decision_envelope(self):
        result = run_prompt(INVESTOR_PROMPT, profile="truth_first")
        envelope = result.decision_envelope
        conformance = validate_decision_envelope(envelope)
        self.assertTrue(conformance.valid, conformance.failures)
        self.assertTrue(envelope["redaction"]["redacted"])
        self.assertNotIn("raw", envelope)
        self.assertTrue(envelope["evidence"])

    def test_raw_envelope_can_be_built_explicitly(self):
        result = run_prompt("Write a quick draft now.", profile="progress_max")
        envelope = build_decision_envelope(result.trace, include_raw=True)
        conformance = validate_decision_envelope(envelope)
        self.assertTrue(conformance.valid, conformance.failures)
        self.assertFalse(envelope["redaction"]["redacted"])
        self.assertIn("raw", envelope)
        self.assertIn("prompt", envelope["raw"])

    def test_hashes_are_stable(self):
        self.assertEqual(stable_text_hash("same"), stable_text_hash("same"))
        self.assertNotEqual(stable_text_hash("same"), stable_text_hash("different"))

    def test_invalid_envelope_fails_conformance(self):
        result = run_prompt(INVESTOR_PROMPT, profile="truth_first")
        envelope = dict(result.decision_envelope)
        envelope.pop("gate")
        conformance = validate_decision_envelope(envelope)
        self.assertFalse(conformance.valid)
        self.assertIn("missing:gate", conformance.failures)


if __name__ == "__main__":
    unittest.main()
