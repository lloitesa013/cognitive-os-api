"""Compare Cognitive OS against simple deterministic baselines."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List, Mapping


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cognitive_os.baselines import BASELINE_NAMES, run_baseline  # noqa: E402
from cognitive_os.runtime import run_prompt  # noqa: E402
from cognitive_os.benchmarks.cognitiveos_v0.run_benchmark import (  # noqa: E402
    HERE,
    PROFILES,
    load_json,
)


RUNNERS = (*BASELINE_NAMES, "cognitive_os")
BENCHMARK_VERSION = "CognitiveOS-v0-seed-v0.1.4"
SCORING_METHOD = (
    "For non-gated baselines, gate accuracy is evaluated by mapping the baseline "
    "output to the expected gate label through the benchmark evaluator. Trace "
    "completeness is zero unless the baseline emits a structured auditable trace."
)
DEFAULT_ARTIFACT_PATH = HERE / "artifacts" / "baseline_comparison_latest.json"


def run_baseline_comparison(
    scenarios_path: Path = HERE / "scenarios.json",
    expected_path: Path = HERE / "expected_gates.json",
    profiles: Iterable[str] = PROFILES,
    provider_name: str = "mock",
) -> Dict[str, Any]:
    scenarios: List[Mapping[str, Any]] = load_json(scenarios_path)
    expected: Mapping[str, Mapping[str, str]] = load_json(expected_path)
    profiles = tuple(profiles)

    results = {
        runner: _empty_metrics(runner, provider_name, len(scenarios), len(profiles))
        for runner in RUNNERS
    }

    for scenario in scenarios:
        scenario_id = str(scenario["scenario_id"])
        prompt = str(scenario["prompt"])
        expected_gates = expected[scenario_id]
        for runner in RUNNERS:
            actual_gates: Dict[str, str] = {}
            trace_complete_count = 0
            risk_tags: List[str] = []
            for profile in profiles:
                if runner == "cognitive_os":
                    result = run_prompt(
                        prompt, profile=profile, provider_name=provider_name
                    )
                    gate = result.gate.value
                    trace_complete = _trace_complete(result.trace.to_dict())
                    risk_tags = sorted(set([*risk_tags, *result.risk_tags]))
                else:
                    result = run_baseline(runner, prompt, provider_name=provider_name)
                    gate = result.gate.value
                    trace_complete = result.trace_complete
                    risk_tags = sorted(set([*risk_tags, *result.risk_tags]))

                actual_gates[profile] = gate
                _update_counts(results[runner], gate, expected_gates[profile])
                if trace_complete:
                    trace_complete_count += 1

            unique_gate_count = len(set(actual_gates.values()))
            if unique_gate_count > 1:
                results[runner]["separated_scenarios"] += 1
            results[runner]["separation_scores"].append(
                (unique_gate_count - 1) / max(1, len(profiles) - 1)
            )
            if trace_complete_count == len(profiles):
                results[runner]["complete_trace_scenarios"] += 1

            results[runner]["details"].append(
                {
                    "scenario_id": scenario_id,
                    "category": scenario.get("category", ""),
                    "actual_gates": actual_gates,
                    "expected_gates": expected_gates,
                    "risk_tags": risk_tags,
                }
            )

    return {
        "benchmark_version": BENCHMARK_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "provider": provider_name,
        "scoring_method": SCORING_METHOD,
        "runners": {
            runner: _finalize_metrics(metrics) for runner, metrics in results.items()
        },
    }


def render_markdown(metrics: Mapping[str, Mapping[str, Any]]) -> str:
    runners = metrics.get("runners", metrics)
    lines = [
        "# CognitiveOS-v0 Baseline Comparison",
        "",
        f"- Benchmark Version: {metrics.get('benchmark_version', BENCHMARK_VERSION)}",
        f"- Provider: {metrics.get('provider', 'mock')}",
        f"- Scoring Method: {metrics.get('scoring_method', SCORING_METHOD)}",
        "",
        "| Runner | Gate Accuracy | Profile Separation | Trace Completeness | False Allow | False Deny |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for runner in RUNNERS:
        row = runners[runner]
        lines.append(
            "| {runner} | {accuracy:.2%} | {separation:.2%} | {trace:.2%} | {false_allow:.2%} | {false_deny:.2%} |".format(
                runner=runner,
                accuracy=row["gate_accuracy"],
                separation=row["profile_separation_score"],
                trace=row["trace_completeness"],
                false_allow=row["false_allow_rate"],
                false_deny=row["false_deny_rate"],
            )
        )
    return "\n".join(lines)


def write_artifact(metrics: Mapping[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
    return output_path


def _empty_metrics(
    runner: str, provider_name: str, scenario_count: int, profile_count: int
) -> Dict[str, Any]:
    return {
        "runner": runner,
        "provider": provider_name,
        "scenario_count": scenario_count,
        "profile_count": profile_count,
        "total": 0,
        "correct": 0,
        "false_allow": 0,
        "false_deny": 0,
        "separated_scenarios": 0,
        "separation_scores": [],
        "complete_trace_scenarios": 0,
        "details": [],
    }


def _update_counts(metrics: Dict[str, Any], actual: str, expected: str) -> None:
    metrics["total"] += 1
    if actual == expected:
        metrics["correct"] += 1
    if actual == "ALLOW" and expected != "ALLOW":
        metrics["false_allow"] += 1
    if actual in {"DENY", "HANDOFF"} and expected in {"ALLOW", "DEGRADE"}:
        metrics["false_deny"] += 1


def _finalize_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    total = metrics["total"]
    scenario_count = metrics["scenario_count"]
    separation_scores = metrics["separation_scores"]
    return {
        "runner": metrics["runner"],
        "provider": metrics["provider"],
        "scenario_count": scenario_count,
        "profile_count": metrics["profile_count"],
        "gate_accuracy": metrics["correct"] / total if total else 0.0,
        "gate_difference_rate": (
            metrics["separated_scenarios"] / scenario_count if scenario_count else 0.0
        ),
        "profile_separation_score": (
            sum(separation_scores) / len(separation_scores) if separation_scores else 0.0
        ),
        "trace_completeness": (
            metrics["complete_trace_scenarios"] / scenario_count
            if scenario_count
            else 0.0
        ),
        "false_allow_rate": metrics["false_allow"] / total if total else 0.0,
        "false_deny_rate": metrics["false_deny"] / total if total else 0.0,
        "details": metrics["details"],
    }


def _trace_complete(trace: Mapping[str, Any]) -> bool:
    required_nonempty = (
        "trace_id",
        "profile",
        "candidate_action",
        "gate",
        "dominant_axis",
        "reason",
        "counterfactual",
    )
    return all(bool(trace.get(key)) for key in required_nonempty) and "risk_tags" in trace


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pretty", action="store_true", help="Print markdown report")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_ARTIFACT_PATH,
        help="Path for the JSON artifact.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Do not write a JSON artifact.",
    )
    args = parser.parse_args()
    metrics = run_baseline_comparison()
    if not args.no_write:
        write_artifact(metrics, args.output)
    if args.pretty:
        print(render_markdown(metrics))
    else:
        print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
