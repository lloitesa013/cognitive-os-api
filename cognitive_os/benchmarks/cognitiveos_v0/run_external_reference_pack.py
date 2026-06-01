"""Run a reviewer-provided external reference pack through Cognitive OS.

This adapter is intentionally conservative: it can read local CSV, JSON, or
JSONL files owned by the reviewer, but it never exports raw prompt text in the
public metrics payload. The bundled default fixture is public-safe and is not a
third-party benchmark.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cognitive_os.benchmarks.cognitiveos_v0.run_adversarial import (  # noqa: E402
    PROFILES,
    _envelope_complete,
    _redaction_ok,
)
from cognitive_os.protocol import stable_text_hash  # noqa: E402
from cognitive_os.runtime import run_prompt  # noqa: E402


HERE = Path(__file__).resolve().parent
DEFAULT_FIXTURE = HERE / "external_reference_fixture.csv"
REQUIRED_FIELDS = ("source", "item_id", "category", "prompt")


def load_external_items(path: Path) -> List[Mapping[str, str]]:
    """Load and validate an external reference file."""

    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
    elif suffix == ".jsonl":
        rows = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        ]
    elif suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        rows = payload.get("items", payload) if isinstance(payload, dict) else payload
    else:
        raise ValueError("External reference input must be .csv, .jsonl, or .json.")

    if not isinstance(rows, list):
        raise ValueError("External reference input must contain a list of items.")

    normalized: List[Mapping[str, str]] = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            raise ValueError(f"Row {index} is not an object.")
        missing = [
            field
            for field in REQUIRED_FIELDS
            if field not in row or str(row[field]).strip() == ""
        ]
        if missing:
            raise ValueError(
                "External reference input is missing required fields at row "
                f"{index}: {', '.join(missing)}"
            )
        normalized.append(
            {
                field: str(row[field]).strip()
                for field in REQUIRED_FIELDS
            }
        )
    return normalized


def run_external_reference_pack(
    input_path: Path = DEFAULT_FIXTURE,
    profiles: Iterable[str] = PROFILES,
    provider_name: str = "mock",
    dataset_label: str = "",
) -> Dict[str, Any]:
    """Run a local external reference file and emit redacted metrics."""

    input_path = Path(input_path)
    items = load_external_items(input_path)
    profiles = tuple(profiles)
    is_bundled_fixture = input_path.resolve() == DEFAULT_FIXTURE.resolve()
    run_type = (
        "bundled_public_safe_fixture"
        if is_bundled_fixture
        else "reviewer_provided_local_file"
    )

    total = 0
    trace_complete = 0
    redaction_pass = 0
    profile_separated = 0
    details = []
    categories: Dict[str, MutableMapping[str, Any]] = {}
    gate_distribution: Dict[str, MutableMapping[str, int]] = {
        profile: {} for profile in profiles
    }

    for item in items:
        prompt = item["prompt"]
        item_id = item["item_id"]
        category = item["category"]
        category_row = categories.setdefault(
            category,
            {"item_count": 0, "decision_count": 0, "gates": {}},
        )
        category_row["item_count"] += 1
        actual_gates: Dict[str, str] = {}
        risk_tags_by_profile: Dict[str, List[str]] = {}
        trace_by_profile: Dict[str, bool] = {}
        redaction_by_profile: Dict[str, bool] = {}

        for profile in profiles:
            result = run_prompt(prompt, profile=profile, provider_name=provider_name)
            envelope = result.decision_envelope
            gate = result.gate.value
            actual_gates[profile] = gate
            risk_tags_by_profile[profile] = list(result.risk_tags)
            trace_ok = _envelope_complete(envelope)
            redaction_ok = _redaction_ok(envelope)
            trace_by_profile[profile] = trace_ok
            redaction_by_profile[profile] = redaction_ok

            total += 1
            category_row["decision_count"] += 1
            if trace_ok:
                trace_complete += 1
            if redaction_ok:
                redaction_pass += 1

            profile_gates = gate_distribution[profile]
            profile_gates[gate] = profile_gates.get(gate, 0) + 1
            category_gates = category_row["gates"]
            category_gates[gate] = category_gates.get(gate, 0) + 1

        if len(set(actual_gates.values())) > 1:
            profile_separated += 1

        details.append(
            {
                "source": item["source"],
                "item_id": item_id,
                "category": category,
                "prompt_hash": stable_text_hash(prompt),
                "actual_gates": actual_gates,
                "risk_tags_by_profile": risk_tags_by_profile,
                "trace_complete_by_profile": trace_by_profile,
                "redaction_pass_by_profile": redaction_by_profile,
            }
        )

    item_count = len(items)
    category_summary = {
        category: {
            "item_count": int(row["item_count"]),
            "decision_count": int(row["decision_count"]),
            "gate_distribution": dict(sorted(row["gates"].items())),
        }
        for category, row in sorted(categories.items())
    }
    return {
        "benchmark_type": "external_reference_pack",
        "run_type": run_type,
        "third_party_benchmark": False,
        "external_input_provided": not is_bundled_fixture,
        "dataset_label": dataset_label or ("public_safe_fixture" if is_bundled_fixture else ""),
        "provider": provider_name,
        "item_count": item_count,
        "profile_count": len(profiles),
        "total_decisions": total,
        "trace_completeness": trace_complete / total if total else 0.0,
        "redaction_pass_rate": redaction_pass / total if total else 0.0,
        "profile_separation_rate": profile_separated / item_count if item_count else 0.0,
        "gate_distribution_by_profile": {
            profile: dict(sorted(gates.items()))
            for profile, gates in gate_distribution.items()
        },
        "category_summary": category_summary,
        "public_export_rule": (
            "External reference evidence emits source ids, item ids, categories, "
            "prompt hashes, gates, trace checks, and redaction checks; raw prompt "
            "and candidate text are not emitted."
        ),
        "interpretation": (
            "The bundled fixture is public-safe smoke-test data. Reviewer-provided "
            "files can exercise third-party-style inputs, but this repository does "
            "not certify dataset authenticity or external adoption."
        ),
        "details": details,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default=str(DEFAULT_FIXTURE),
        help="Path to a CSV, JSONL, or JSON file with source,item_id,category,prompt.",
    )
    parser.add_argument("--dataset-label", default="", help="Optional dataset label.")
    parser.add_argument("--provider", default="mock", help="Provider name.")
    parser.add_argument("--pretty", action="store_true", help="Print formatted JSON.")
    args = parser.parse_args()
    metrics = run_external_reference_pack(
        input_path=Path(args.input),
        provider_name=args.provider,
        dataset_label=args.dataset_label,
    )
    indent = 2 if args.pretty else None
    print(json.dumps(metrics, indent=indent, ensure_ascii=False))


if __name__ == "__main__":
    main()
