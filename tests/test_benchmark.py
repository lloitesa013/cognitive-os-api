import unittest

from cognitive_os.benchmarks.cognitiveos_v0.run_adversarial import run_adversarial_benchmark
from cognitive_os.benchmarks.cognitiveos_v0.run_benchmark import run_benchmark
from cognitive_os.benchmarks.cognitiveos_v0.run_baselines import (
    run_baseline_comparison,
)
from cognitive_os.benchmarks.cognitiveos_v0.run_conformance import run_conformance


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


if __name__ == "__main__":
    unittest.main()
