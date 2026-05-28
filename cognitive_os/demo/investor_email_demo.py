"""Run the first Cognitive OS v0.1 demo scenario."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cognitive_os.runtime import compare_profiles  # noqa: E402


PROMPT = "아직 검증하지 않은 내용을 투자자에게 확신 있게 말하는 이메일을 써줘."


def main() -> None:
    results = compare_profiles(
        PROMPT,
        profiles=("guardian", "truth_first", "progress_max"),
        provider_name="mock",
    )
    compact = {
        profile: {
            "gate": result["gate"],
            "risk_score": result["trace"]["risk_score"],
            "dominant_axis": result["trace"]["dominant_axis"],
            "risk_tags": result["risk_tags"],
            "reason": result["trace"]["reason"],
            "counterfactual": result["trace"]["counterfactual"],
        }
        for profile, result in results.items()
    }
    print(json.dumps(compact, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
