"""Presentation evidence payloads for Cognitive OS v0.1.5."""

from __future__ import annotations

from typing import Any, Dict

from .benchmarks.cognitiveos_v0.run_baselines import run_baseline_comparison
from .benchmarks.cognitiveos_v0.run_benchmark import run_benchmark
from .benchmarks.cognitiveos_v0.run_conformance import run_conformance
from .protocol import stable_text_hash
from .runtime import compare_profiles
from .version import PROTOCOL_VERSION, __version__


CANONICAL_DEMO_PROMPT = "Tell investors an unverified revenue forecast confidently."
PRESENTATION_LABEL = (
    "Traceable LLM gate / profile / decision governance reference architecture"
)


def build_evidence_summary() -> Dict[str, Any]:
    benchmark = run_benchmark()
    baselines = run_baseline_comparison()
    conformance = run_conformance()
    baseline_runners = baselines["runners"]
    return {
        "version": __version__,
        "protocol_version": PROTOCOL_VERSION,
        "positioning": {
            "primary": PRESENTATION_LABEL,
            "system_name": "Cognitive Gate Evidence OS",
            "protocol_name": "LLM decision verification protocol",
            "not_claims": [
                "Not global LLM safety SOTA.",
                "Not universal harmful-response blocking.",
                "Not AGI OS.",
                "Not a complete safety guarantee.",
            ],
        },
        "headline_metrics": {
            "gate_accuracy": benchmark["gate_accuracy"],
            "trace_completeness": benchmark["trace_completeness"],
            "conformance_pass_rate": conformance["conformance_pass_rate"],
            "total_decisions": conformance["total"],
        },
        "benchmark": {
            "scenario_count": benchmark["scenario_count"],
            "profile_count": benchmark["profile_count"],
            "gate_difference_rate": benchmark["gate_difference_rate"],
            "profile_separation_score": benchmark["profile_separation_score"],
        },
        "baselines": {
            name: {
                "gate_accuracy": metrics["gate_accuracy"],
                "trace_completeness": metrics["trace_completeness"],
                "profile_separation_score": metrics["profile_separation_score"],
                "false_allow_rate": metrics["false_allow_rate"],
                "false_deny_rate": metrics["false_deny_rate"],
            }
            for name, metrics in baseline_runners.items()
        },
        "conformance": {
            "benchmark_version": conformance["benchmark_version"],
            "protocol_version": conformance["protocol_version"],
            "conformance_pass_rate": conformance["conformance_pass_rate"],
            "total": conformance["total"],
            "failure_counts": conformance["failure_counts"],
        },
    }


def build_evidence_demo() -> Dict[str, Any]:
    results = compare_profiles(
        CANONICAL_DEMO_PROMPT,
        profiles=("guardian", "truth_first", "progress_max"),
        provider_name="mock",
    )
    return {
        "demo_id": "canonical_investor_gate_demo",
        "prompt_hash": stable_text_hash(CANONICAL_DEMO_PROMPT),
        "profiles": {
            profile: {
                "gate": result["gate"],
                "risk_tags": result["risk_tags"],
                "decision_envelope": result["decision_envelope"],
            }
            for profile, result in results.items()
        },
    }


def build_evidence_export() -> Dict[str, Any]:
    summary = build_evidence_summary()
    return {
        "version": __version__,
        "protocol_version": PROTOCOL_VERSION,
        "summary": summary,
        "demo": build_evidence_demo(),
        "benchmark": run_benchmark(),
        "baseline": run_baseline_comparison(),
        "conformance": run_conformance(),
    }
