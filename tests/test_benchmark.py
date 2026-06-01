import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from cognitive_os.benchmarks.cognitiveos_v0.run_adversarial import run_adversarial_benchmark
from cognitive_os.benchmarks.cognitiveos_v0.run_benchmark import run_benchmark
from cognitive_os.benchmarks.cognitiveos_v0.run_baselines import (
    run_baseline_comparison,
)
from cognitive_os.benchmarks.cognitiveos_v0.run_challenge_pack import run_challenge_pack
from cognitive_os.benchmarks.cognitiveos_v0.run_conformance import run_conformance
from cognitive_os.benchmarks.cognitiveos_v0.run_external_reference_pack import (
    load_external_items,
    run_external_reference_pack,
)


class BenchmarkTests(unittest.TestCase):
    def test_seed_benchmark_reports_core_metrics(self):
        metrics = run_benchmark()
        self.assertEqual(metrics["scenario_count"], 30)
        self.assertEqual(metrics["profile_count"], 3)
        self.assertGreaterEqual(metrics["gate_accuracy"], 0.8)
        self.assertGreaterEqual(metrics["gate_difference_rate"], 0.7)
        self.assertEqual(metrics["trace_completeness"], 1.0)

    def test_baseline_comparison_shows_proposed_trace_and_accuracy_advantage(self):
        metrics = run_baseline_comparison()
        runners = metrics["runners"]
        self.assertIn("benchmark_version", metrics)
        self.assertIn("generated_at", metrics)
        self.assertIn("scoring_method", metrics)
        self.assertIn("raw_llm", runners)
        self.assertIn("cognitive_os", runners)
        self.assertGreater(
            runners["cognitive_os"]["gate_accuracy"],
            runners["raw_llm"]["gate_accuracy"],
        )
        self.assertEqual(runners["cognitive_os"]["trace_completeness"], 1.0)
        self.assertEqual(runners["raw_llm"]["trace_completeness"], 0.0)
        self.assertEqual(runners["raw_llm"]["profile_separation_score"], 0.0)

    def test_conformance_runner_reports_full_protocol_pass_rate(self):
        metrics = run_conformance()
        self.assertEqual(metrics["scenario_count"], 30)
        self.assertEqual(metrics["protocol_version"], "cognitive-gate-evidence-v0.1")
        self.assertEqual(metrics["conformance_pass_rate"], 1.0)
        self.assertEqual(metrics["failure_counts"], {})

    def test_adversarial_pack_reports_redacted_measurable_evidence(self):
        metrics = run_adversarial_benchmark()
        self.assertEqual(metrics["scenario_count"], 6)
        self.assertEqual(metrics["profile_count"], 3)
        self.assertEqual(metrics["total_decisions"], 18)
        self.assertEqual(metrics["gate_accuracy"], 1.0)
        self.assertEqual(metrics["trace_completeness"], 1.0)
        self.assertEqual(metrics["redaction_pass_rate"], 1.0)
        self.assertGreaterEqual(metrics["profile_separation_rate"], 0.6)
        for detail in metrics["details"]:
            self.assertIn("prompt_hash", detail)
            self.assertNotIn("prompt", detail)
            self.assertNotIn("candidate", detail)

    def test_challenge_pack_reports_non_perfect_external_style_evidence(self):
        metrics = run_challenge_pack()
        self.assertEqual(metrics["benchmark_type"], "external_style_challenge_pack")
        self.assertFalse(metrics["third_party_benchmark"])
        self.assertEqual(metrics["scenario_count"], 8)
        self.assertEqual(metrics["profile_count"], 3)
        self.assertEqual(metrics["total_decisions"], 24)
        self.assertLess(metrics["gate_accuracy"], 1.0)
        self.assertEqual(metrics["trace_completeness"], 1.0)
        self.assertEqual(metrics["redaction_pass_rate"], 1.0)
        for detail in metrics["details"]:
            self.assertIn("prompt_hash", detail)
            self.assertNotIn("prompt", detail)
            self.assertNotIn("candidate", detail)

    def test_external_reference_fixture_reports_redacted_metrics(self):
        metrics = run_external_reference_pack()
        self.assertEqual(metrics["benchmark_type"], "external_reference_pack")
        self.assertEqual(metrics["run_type"], "bundled_public_safe_fixture")
        self.assertFalse(metrics["third_party_benchmark"])
        self.assertFalse(metrics["external_input_provided"])
        self.assertEqual(metrics["item_count"], 4)
        self.assertEqual(metrics["profile_count"], 3)
        self.assertEqual(metrics["total_decisions"], 12)
        self.assertEqual(metrics["trace_completeness"], 1.0)
        self.assertEqual(metrics["redaction_pass_rate"], 1.0)
        for detail in metrics["details"]:
            self.assertIn("prompt_hash", detail)
            self.assertNotIn("prompt", detail)
            self.assertNotIn("candidate", detail)

    def test_external_reference_jsonl_omits_raw_prompt_text(self):
        prompt = "Use only public facts when drafting an earnings note."
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "reviewer_fixture.jsonl"
            path.write_text(
                (
                    '{"source":"local","item_id":"case-1","category":"finance",'
                    f'"prompt":"{prompt}"}}\n'
                ),
                encoding="utf-8",
            )
            metrics = run_external_reference_pack(path)
        payload = str(metrics)
        self.assertTrue(metrics["external_input_provided"])
        self.assertIn("prompt_hash", payload)
        self.assertNotIn(prompt, payload)

    def test_external_reference_missing_required_fields_fails_clearly(self):
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "broken.csv"
            path.write_text("source,item_id,category\nlocal,case-1,finance\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing required fields"):
                load_external_items(path)

    def test_external_reference_jsonl_accepts_utf8_bom(self):
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "reviewer_fixture.jsonl"
            path.write_text(
                (
                    '\ufeff{"source":"local","item_id":"case-1",'
                    '"category":"finance","prompt":"Use verified sources."}\n'
                ),
                encoding="utf-8",
            )
            rows = load_external_items(path)
        self.assertEqual(rows[0]["item_id"], "case-1")


if __name__ == "__main__":
    unittest.main()
