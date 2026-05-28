"""Run protocol conformance checks over CognitiveOS-v0."""

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

from cognitive_os.benchmarks.cognitiveos_v0.run_benchmark import (  # noqa: E402
    HERE,
    PROFILES,
    load_json,
)
from cognitive_os.conformance import validate_decision_envelope  # noqa: E402
from cognitive_os.runtime import run_prompt  # noqa: E402
from cognitive_os.version import PROTOCOL_VERSION  # noqa: E402


BENCHMARK_VERSION = "CognitiveOS-v0-seed-v0.1.4"
DEFAULT_ARTIFACT_PATH = HERE / "artifacts" / "conformance_latest.json"


def run_conformance(
    scenarios_path: Path = HERE / "scenarios.json",
    profiles: Iterable[str] = PROFILES,
    provider_name: str = "mock",
) -> Dict[str, Any]:
    scenarios: List[Mapping[str, Any]] = load_json(scenarios_path)
    profiles = tuple(profiles)
    total = 0
    passed = 0
    failure_counts: Dict[str, int] = {}
    details = []

    for scenario in scenarios:
        scenario_id = str(scenario["scenario_id"])
        prompt = str(scenario["prompt"])
        profile_results = {}
        for profile in profiles:
            result = run_prompt(prompt, profile=profile, provider_name=provider_name)
            conformance = validate_decision_envelope(result.decision_envelope)
            total += 1
            if conformance.valid:
                passed += 1
            for failure in conformance.failures:
                failure_counts[failure] = failure_counts.get(failure, 0) + 1
            profile_results[profile] = {
                "gate": result.gate.value,
                "valid": conformance.valid,
                "failures": conformance.failures,
                "trace_id": result.decision_envelope["trace_id"],
            }
        details.append(
            {
                "scenario_id": scenario_id,
                "category": scenario.get("category", ""),
                "profiles": profile_results,
            }
        )

    return {
        "benchmark_version": BENCHMARK_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "provider": provider_name,
        "scenario_count": len(scenarios),
        "profile_count": len(profiles),
        "total": total,
        "passed": passed,
        "conformance_pass_rate": passed / total if total else 0.0,
        "failure_counts": failure_counts,
        "details": details,
    }


def render_markdown(metrics: Mapping[str, Any]) -> str:
    lines = [
        "# CognitiveOS-v0 Protocol Conformance",
        "",
        f"- Benchmark Version: {metrics['benchmark_version']}",
        f"- Protocol Version: {metrics['protocol_version']}",
        f"- Provider: {metrics['provider']}",
        f"- Conformance Pass Rate: {metrics['conformance_pass_rate']:.2%}",
        f"- Total Decisions: {metrics['total']}",
    ]
    if metrics["failure_counts"]:
        lines.append("")
        lines.append("| Failure | Count |")
        lines.append("| --- | ---: |")
        for failure, count in sorted(metrics["failure_counts"].items()):
            lines.append(f"| {failure} | {count} |")
    return "\n".join(lines)


def write_artifact(metrics: Mapping[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pretty", action="store_true", help="Print markdown report")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_ARTIFACT_PATH,
        help="Path for the JSON conformance artifact.",
    )
    parser.add_argument("--no-write", action="store_true", help="Do not write JSON")
    args = parser.parse_args()
    metrics = run_conformance()
    if not args.no_write:
        write_artifact(metrics, args.output)
    if args.pretty:
        print(render_markdown(metrics))
    else:
        print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
