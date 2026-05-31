"""Run the public adversarial evidence pack for CognitiveOS-v0.

The exported report intentionally keeps raw prompt and candidate text out of the
public payload. Scenario fixtures remain in the repository for reproduction, but
runtime evidence uses stable hashes plus gate/trace/redaction metrics.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cognitive_os.protocol import stable_text_hash  # noqa: E402
from cognitive_os.runtime import run_prompt  # noqa: E402


HERE = Path(__file__).resolve().parent
PROFILES = ("guardian", "truth_first", "progress_max")
REQUIRED_ENVELOPE_FIELDS = (
    "protocol_version",
    "trace_id",
    "profile_name",
    "candidate_action",
    "provider",
    "gate",
    "dominant_axis",
    "risk_score",
    "risk_tags",
    "reason",
    "counterfactual",
    "ccp_fingerprint",
    "prompt_hash",
    "candidate_hash",
    "redaction",
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def run_adversarial_benchmark(
    scenarios_path: Path = HERE / "adversarial_scenarios.json",
    expected_path: Path = HERE / "adversarial_expected_gates.json",
    profiles: Iterable[str] = PROFILES,
    provider_name: str = "mock",
) -> Dict[str, Any]:
    scenarios: List[Mapping[str, Any]] = load_json(scenarios_path)
    expected: Mapping[str, Mapping[str, str]] = load_json(expected_path)
    profiles = tuple(profiles)

    total = 0
    correct = 0
    trace_complete = 0
    redaction_pass = 0
    profile_separated = 0
    details = []
    categories: Dict[str, MutableMapping[str, Any]] = {}

    for scenario in scenarios:
        scenario_id = str(scenario["scenario_id"])
        category = str(scenario.get("category", "uncategorized"))
        prompt = str(scenario["prompt"])
        actual_gates: Dict[str, str] = {}
        risk_tags_by_profile: Dict[str, List[str]] = {}
        redaction_by_profile: Dict[str, bool] = {}
        trace_by_profile: Dict[str, bool] = {}
        category_row = categories.setdefault(
            category,
            {"scenario_count": 0, "decision_count": 0, "correct": 0},
        )
        category_row["scenario_count"] += 1

        for profile in profiles:
            result = run_prompt(prompt, profile=profile, provider_name=provider_name)
            envelope = result.decision_envelope
            gate = result.gate.value
            actual_gates[profile] = gate
            risk_tags_by_profile[profile] = list(result.risk_tags)
            trace_ok = _envelope_complete(envelope)
            redaction_ok = _redaction_ok(envelope)
            redaction_by_profile[profile] = redaction_ok
            trace_by_profile[profile] = trace_ok

            total += 1
            category_row["decision_count"] += 1
            if gate == expected[scenario_id][profile]:
                correct += 1
                category_row["correct"] += 1
            if trace_ok:
                trace_complete += 1
            if redaction_ok:
                redaction_pass += 1

        if len(set(actual_gates.values())) > 1:
            profile_separated += 1

        details.append(
            {
                "scenario_id": scenario_id,
                "category": category,
                "prompt_hash": stable_text_hash(prompt),
                "actual_gates": actual_gates,
                "expected_gates": expected[scenario_id],
                "risk_tags_by_profile": risk_tags_by_profile,
                "trace_complete_by_profile": trace_by_profile,
                "redaction_pass_by_profile": redaction_by_profile,
            }
        )

    category_summary = {
        category: {
            "scenario_count": int(row["scenario_count"]),
            "decision_count": int(row["decision_count"]),
            "gate_accuracy": (
                row["correct"] / row["decision_count"] if row["decision_count"] else 0.0
            ),
        }
        for category, row in sorted(categories.items())
    }
    scenario_count = len(scenarios)
    return {
        "provider": provider_name,
        "scenario_count": scenario_count,
        "profile_count": len(profiles),
        "total_decisions": total,
        "gate_accuracy": correct / total if total else 0.0,
        "trace_completeness": trace_complete / total if total else 0.0,
        "redaction_pass_rate": redaction_pass / total if total else 0.0,
        "profile_separation_rate": (
            profile_separated / scenario_count if scenario_count else 0.0
        ),
        "category_summary": category_summary,
        "public_export_rule": (
            "Public adversarial evidence emits scenario ids, categories, hashes, "
            "gates, trace checks, and redaction checks; raw prompt and candidate "
            "text are not emitted."
        ),
        "details": details,
    }


def _envelope_complete(envelope: Mapping[str, Any]) -> bool:
    return all(
        field in envelope and envelope[field] is not None
        for field in REQUIRED_ENVELOPE_FIELDS
    )


def _redaction_ok(envelope: Mapping[str, Any]) -> bool:
    redaction = envelope.get("redaction")
    return (
        isinstance(redaction, Mapping)
        and redaction.get("redacted") is True
        and redaction.get("raw_included") is False
        and "raw" not in envelope
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pretty", action="store_true", help="Print compact JSON")
    args = parser.parse_args()
    metrics = run_adversarial_benchmark()
    indent = 2 if args.pretty else None
    print(json.dumps(metrics, indent=indent, ensure_ascii=False))


if __name__ == "__main__":
    main()
