"""Run the external-style challenge pack for CognitiveOS-v0.

This pack is not a third-party benchmark. It is a small, public-safe challenge
set that is intentionally separate from the internal seed benchmark so reviewers
can see where the current policy/risk heuristics do and do not generalize.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cognitive_os.benchmarks.cognitiveos_v0.run_adversarial import (  # noqa: E402
    run_adversarial_benchmark,
)


HERE = Path(__file__).resolve().parent


def run_challenge_pack() -> Dict[str, Any]:
    metrics = run_adversarial_benchmark(
        scenarios_path=HERE / "challenge_scenarios.json",
        expected_path=HERE / "challenge_expected_gates.json",
    )
    metrics["benchmark_type"] = "external_style_challenge_pack"
    metrics["third_party_benchmark"] = False
    metrics["interpretation"] = (
        "This is a small challenge pack for limitation discovery, not an "
        "external adoption or general safety result."
    )
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pretty", action="store_true", help="Print formatted JSON")
    args = parser.parse_args()
    indent = 2 if args.pretty else None
    print(json.dumps(run_challenge_pack(), indent=indent, ensure_ascii=False))


if __name__ == "__main__":
    main()
