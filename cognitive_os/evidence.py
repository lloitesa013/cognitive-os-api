"""Presentation evidence payloads for Cognitive OS v0.1.5."""

from __future__ import annotations

from typing import Any, Dict

from .benchmarks.cognitiveos_v0.run_baselines import run_baseline_comparison
from .benchmarks.cognitiveos_v0.run_adversarial import run_adversarial_benchmark
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
    adversarial = run_adversarial_benchmark()
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
            "adversarial_gate_accuracy": adversarial["gate_accuracy"],
            "adversarial_redaction_pass_rate": adversarial["redaction_pass_rate"],
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
        "adversarial": {
            "scenario_count": adversarial["scenario_count"],
            "profile_count": adversarial["profile_count"],
            "total_decisions": adversarial["total_decisions"],
            "gate_accuracy": adversarial["gate_accuracy"],
            "trace_completeness": adversarial["trace_completeness"],
            "redaction_pass_rate": adversarial["redaction_pass_rate"],
            "profile_separation_rate": adversarial["profile_separation_rate"],
            "category_summary": adversarial["category_summary"],
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
    profile_outcomes = {
        "guardian": {
            "profile_label": "Guardian",
            "profile_policy": "Prioritize safety and refuse unsafe execution paths.",
            "expected_reading": "The same candidate is denied when the profile treats unverified investor messaging as high-risk.",
        },
        "truth_first": {
            "profile_label": "Truth First",
            "profile_policy": "Preserve momentum while removing unsupported certainty.",
            "expected_reading": "The same candidate is degraded into an evidence-bounded version.",
        },
        "progress_max": {
            "profile_label": "Progress Max",
            "profile_policy": "Keep work moving when risk can be made visible.",
            "expected_reading": "The same candidate is allowed only as a cautious draft with visible risk tags.",
        },
    }
    return {
        "demo_id": "canonical_investor_gate_demo",
        "story": {
            "title": "Same candidate, three policy profiles, three gate outcomes.",
            "problem": "A model can produce confident language faster than a reviewer can verify it.",
            "protocol": "Cognitive OS inserts a profile-owned decision gate before model output becomes action.",
            "completion_signal": "A reviewer can explain the gate decision without seeing raw private prompt text.",
        },
        "prompt_hash": stable_text_hash(CANONICAL_DEMO_PROMPT),
        "prompt_label": "unverified investor-forecast request",
        "steps": [
            {
                "label": "Candidate output arrives",
                "detail": "The upstream model output is represented by a stable prompt hash in the public demo.",
            },
            {
                "label": "Profile policy evaluates it",
                "detail": "Guardian, Truth First, and Progress Max compile different priorities into the gate.",
            },
            {
                "label": "Decision envelope is exported",
                "detail": "The public artifact records gate, axis, reason, counterfactual, risk tags, and redaction state.",
            },
        ],
        "envelope_anatomy": [
            {"field": "trace_id", "meaning": "Stable handle for the public decision record."},
            {"field": "profile", "meaning": "Which compiled policy profile judged the candidate."},
            {"field": "gate", "meaning": "ALLOW, DEGRADE, DENY, or HANDOFF."},
            {"field": "axis", "meaning": "The policy axis that most shaped the gate."},
            {"field": "reason", "meaning": "Short public explanation of the gate."},
            {"field": "counterfactual", "meaning": "What would need to change for a different gate."},
            {"field": "risk_tags", "meaning": "Reviewable risk labels without raw private content."},
        ],
        "privacy_boundary": {
            "public_default": "Prompt and candidate content stay redacted in public evidence.",
            "raw_trace_rule": "Raw trace API access requires explicit local environment opt-in and request opt-in.",
            "public_artifact": "The reviewer sees hashes, gates, reasons, and risk tags.",
        },
        "profiles": {
            profile: {
                **profile_outcomes.get(profile, {}),
                "gate": result["gate"],
                "risk_tags": result["risk_tags"],
                "decision_envelope": result["decision_envelope"],
            }
            for profile, result in results.items()
        },
    }


def build_evidence_report() -> Dict[str, Any]:
    """Build the reviewer-facing evidence report without raw private content."""

    summary = build_evidence_summary()
    adversarial = run_adversarial_benchmark()
    return {
        "version": __version__,
        "protocol_version": PROTOCOL_VERSION,
        "title": "Cognitive OS public evidence report",
        "thesis": "A profile-owned gate can make LLM actions traceable, measurable, and bounded.",
        "reviewer_standard": [
            {
                "principle": "It works",
                "evidence": "The demo API returns profile-specific gates and redacted decision envelopes.",
            },
            {
                "principle": "It is reproducible",
                "evidence": "Seed benchmark fixtures, expected gates, and runner scripts are checked into the repository.",
            },
            {
                "principle": "It is measurable",
                "evidence": "Gate accuracy, trace completeness, conformance pass rate, and redaction pass rate are reported.",
            },
            {
                "principle": "It is understandable",
                "evidence": "The UI separates overview, demo, envelope, benchmarks, baselines, and export views.",
            },
            {
                "principle": "It does not overclaim",
                "evidence": "The public report includes explicit non-claims and scoped benchmark boundaries.",
            },
        ],
        "claim_boundary": summary["positioning"]["not_claims"],
        "headline_metrics": summary["headline_metrics"],
        "adversarial": adversarial,
    }


def build_evidence_export() -> Dict[str, Any]:
    summary = build_evidence_summary()
    return {
        "version": __version__,
        "protocol_version": PROTOCOL_VERSION,
        "summary": summary,
        "demo": build_evidence_demo(),
        "report": build_evidence_report(),
        "benchmark": run_benchmark(),
        "adversarial": run_adversarial_benchmark(),
        "baseline": run_baseline_comparison(),
        "conformance": run_conformance(),
    }
