import unittest
from unittest.mock import patch

from cognitive_os.trace import InMemoryTraceStore

try:
    from fastapi.testclient import TestClient

    from cognitive_os.api import create_app
except Exception as exc:  # pragma: no cover - depends on optional API deps
    TestClient = None
    create_app = None
    API_IMPORT_ERROR = exc
else:
    API_IMPORT_ERROR = None


INVESTOR_PROMPT = "Tell investors an unverified revenue forecast confidently."


class ApiSmokeTests(unittest.TestCase):
    def setUp(self):
        if TestClient is None or create_app is None:
            self.skipTest(f"FastAPI smoke tests skipped: {API_IMPORT_ERROR}")
        self.store = InMemoryTraceStore()
        self.client = TestClient(create_app(trace_store=self.store))

    def test_health_and_compile(self):
        health = self.client.get("/health")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()["version"], "0.1.5")
        self.assertEqual(
            health.json()["protocol_version"], "cognitive-gate-evidence-v0.1"
        )
        self.assertIn("truth_first", health.json()["profiles"])

        compiled = self.client.post(
            "/profiles/compile", json={"profile_name": "truth_first"}
        )
        self.assertEqual(compiled.status_code, 200)
        body = compiled.json()
        self.assertEqual(body["dominant_priority"], "truth")
        self.assertTrue(body["fingerprint"])

    def test_run_then_redacted_trace_lookup(self):
        response = self.client.post(
            "/run",
            json={"profile_name": "truth_first", "prompt": INVESTOR_PROMPT},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["gate"], "DEGRADE")
        self.assertIn("decision_envelope", body)
        self.assertNotIn("trace", body)

        trace_id = body["decision_envelope"]["trace_id"]
        trace = self.client.get(f"/trace/{trace_id}")
        self.assertEqual(trace.status_code, 200)
        self.assertEqual(trace.json()["trace_id"], trace_id)
        self.assertTrue(trace.json()["redaction"]["redacted"])
        self.assertNotIn("raw", trace.json())

    def test_raw_trace_requires_env_opt_in(self):
        response = self.client.post(
            "/run",
            json={"profile_name": "truth_first", "prompt": INVESTOR_PROMPT},
        )
        trace_id = response.json()["decision_envelope"]["trace_id"]
        denied = self.client.get(f"/trace/{trace_id}?view=raw")
        self.assertEqual(denied.status_code, 403)

        with patch.dict(
            "os.environ", {"COGNITIVE_OS_ALLOW_RAW_TRACE_API": "true"}, clear=False
        ):
            raw = self.client.get(f"/trace/{trace_id}?view=raw")
        self.assertEqual(raw.status_code, 200)
        self.assertIn("prompt", raw.json())

    def test_compare_and_validation_endpoints(self):
        compare = self.client.post(
            "/compare",
            json={
                "prompt": INVESTOR_PROMPT,
                "profiles": ["guardian", "truth_first", "progress_max"],
            },
        )
        self.assertEqual(compare.status_code, 200)
        body = compare.json()
        self.assertEqual(body["guardian"]["gate"], "DENY")
        self.assertEqual(body["truth_first"]["gate"], "DEGRADE")
        self.assertIn("decision_envelope", body["guardian"])

        invariance = self.client.post(
            "/validate/invariance", json={"profile_name": "truth_first"}
        )
        self.assertEqual(invariance.status_code, 200)
        self.assertTrue(invariance.json()["valid"])

        portability = self.client.post(
            "/validate/provider-portability",
            json={"profile_name": "truth_first", "prompt": INVESTOR_PROMPT},
        )
        self.assertEqual(portability.status_code, 200)
        self.assertTrue(portability.json()["gate_consistency"])

    def test_ui_and_evidence_endpoints(self):
        ui = self.client.get("/ui")
        self.assertEqual(ui.status_code, 200)
        self.assertIn("Evidence Viewer", ui.text)

        ui = self.client.get("/ui/")
        self.assertEqual(ui.status_code, 200)
        self.assertIn("Evidence Viewer", ui.text)

        summary = self.client.get("/evidence/summary")
        self.assertEqual(summary.status_code, 200)
        headline = summary.json()["headline_metrics"]
        self.assertEqual(headline["gate_accuracy"], 1.0)
        self.assertEqual(headline["trace_completeness"], 1.0)
        self.assertEqual(headline["conformance_pass_rate"], 1.0)
        self.assertEqual(headline["total_decisions"], 90)

        demo = self.client.get("/evidence/demo")
        self.assertEqual(demo.status_code, 200)
        demo_body = demo.json()
        self.assertEqual(
            sorted(demo_body["profiles"]),
            ["guardian", "progress_max", "truth_first"],
        )
        self.assertNotIn("Tell investors", str(demo_body))
        for result in demo_body["profiles"].values():
            self.assertIn("decision_envelope", result)
            self.assertTrue(result["decision_envelope"]["redaction"]["redacted"])
            self.assertNotIn("raw", result["decision_envelope"])

        export = self.client.get("/evidence/export")
        self.assertEqual(export.status_code, 200)
        export_body = export.json()
        for key in ("summary", "demo", "benchmark", "baseline", "conformance"):
            self.assertIn(key, export_body)
        self.assertNotIn("Tell investors", str(export_body))


if __name__ == "__main__":
    unittest.main()
