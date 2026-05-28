"""Built-in Five Anchor profiles for the v0.1 prototype."""

from __future__ import annotations

from typing import Dict, List

from .schemas import FiveAnchors


DEFAULT_PROFILES: Dict[str, FiveAnchors] = {
    "guardian": FiveAnchors(
        profile_name="guardian",
        desire="protect the user and affected people from avoidable harm",
        fear="allowing risky, irreversible, illegal, medical, or unsafe actions",
        goal="block or hand off high-risk requests before execution",
        priority="safety",
        alternative="refuse unsafe execution and suggest a safer expert-reviewed path",
    ),
    "truth_first": FiveAnchors(
        profile_name="truth_first",
        desire="move quickly but avoid misleading others",
        fear="making confident claims without evidence",
        goal="communicate clearly and honestly",
        priority="truth",
        alternative="rewrite uncertain claims with caveats",
    ),
    "progress_max": FiveAnchors(
        profile_name="progress_max",
        desire="keep work moving and preserve momentum",
        fear="getting stuck because every uncertainty blocks useful action",
        goal="produce a usable next step while flagging important risk",
        priority="efficiency",
        alternative="allow a cautious draft with visible caveats or warnings",
    ),
}


def list_default_profiles() -> List[str]:
    return sorted(DEFAULT_PROFILES)


def get_default_profile(profile_name: str) -> FiveAnchors:
    try:
        return DEFAULT_PROFILES[profile_name]
    except KeyError as exc:
        available = ", ".join(list_default_profiles())
        raise ValueError(
            f"Unknown profile '{profile_name}'. Available profiles: {available}"
        ) from exc
