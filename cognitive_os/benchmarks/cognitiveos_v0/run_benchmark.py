"""Run the CognitiveOS-v0 seed benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List, Mapping


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cognitive_os.runtime import run_prompt  # noqa: E402
from cognitive_os.benchmarks.cognitiveos_v0.report import render_markdown  # noqa: E402


HERE = Path(__file__).resolve().parent
PROFILES = ("guardian", "truth_first", "progress_max")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def run_benchmark(
    scenarios_path: Path = HERE / "scenarios.json",
    expected_path: Path = HERE / "expected_gates.json",
    profiles: Iterable[str] = PROFILES,
    provider_name: str = "mock",
) -> Dict[str, Any]:
    scenarios: List[Mapping[str, Any]] = load_json(scenarios_path)
    expected: Mapping[str, Mapping[str, str]] = load_json(expected_path)
    profiles = tuple(profiles)

    total = 0
    correct = 0
    separated = 0
    separation_scores = []
    complete_traces = 0
    details = []

    for scenario in scenarios:
        scenario_id = str(scenario["scenario_id"])
        prompt = str(scenario["prompt"])
        actual_gates: Dict[str, str] = {}
        trace_ok = 0

        for profile in profiles:
            result = run_prompt(prompt, profile=profile, provider_name=provider_name)
            actual_gates[profile] = result.gate.value
            total += 1
            if result.gate.value == expected[scenario_id][profile]:
                correct += 1
            if _trace_complete(result.trace.to_dict()):
                trace_ok += 1

        unique_gate_count = len(set(actual_gates.values()))
        if unique_gate_count > 1:
            separated += 1
        separation_scores.append((unique_gate_count - 1) / max(1, len(profiles) - 1))
        if trace_ok == len(profiles):
            complete_traces += 1

        details.append(
            {
                "scenario_id": scenario_id,
                "category": scenario.get("category", ""),
                "actual_gates": actual_gates,
                "expected_gates": expected[scenario_id],
                "profile_separated": unique_gate_count > 1,
            }
        )

    scenario_count = len(scenarios)
    return {
        "provider": provider_name,
        "scenario_count": scenario_count,
        "profile_count": len(profiles),
        "gate_accuracy": correct / total if total else 0.0,
        "gate_difference_rate": separated / scenario_count if scenario_count else 0.0,
        "profile_separation_score": (
            sum(separation_scores) / len(separation_scores) if separation_scores else 0.0
        ),
        "trace_completeness": complete_traces / scenario_count if scenario_count else 0.0,
        "details": details,
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
    args = parser.parse_args()
    metrics = run_benchmark()
    if args.pretty:
        print(render_markdown(metrics))
    else:
        print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
