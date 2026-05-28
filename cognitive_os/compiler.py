"""Deterministic Five Anchors -> CCP compiler."""

from __future__ import annotations

import re
from typing import Dict, Iterable, List, Mapping, Union

from .profiles import get_default_profile
from .schemas import CCP, AXES, FiveAnchors, dedupe, normalize_weights, stable_fingerprint


KEYWORDS = {
    "safety": (
        "safe",
        "safety",
        "harm",
        "risk",
        "danger",
        "illegal",
        "medical",
        "legal",
        "unsafe",
        "protect",
        "위험",
        "안전",
        "피하",
        "막",
        "보호",
        "의료",
        "법률",
    ),
    "truth": (
        "truth",
        "honest",
        "evidence",
        "verified",
        "mislead",
        "confident",
        "accuracy",
        "caveat",
        "진실",
        "정직",
        "검증",
        "근거",
        "확신",
        "과장",
        "정확",
    ),
    "privacy": (
        "privacy",
        "private",
        "secret",
        "confidential",
        "personal data",
        "개인정보",
        "사생활",
        "비밀",
        "기밀",
    ),
    "autonomy": (
        "autonomy",
        "consent",
        "choice",
        "control",
        "manipulate",
        "coerce",
        "자율",
        "동의",
        "선택",
        "통제",
        "조종",
        "강요",
    ),
    "efficiency": (
        "quick",
        "fast",
        "speed",
        "efficient",
        "progress",
        "momentum",
        "execute",
        "usable",
        "빨리",
        "속도",
        "효율",
        "진행",
        "실행",
        "성과",
    ),
}


PRESET_WEIGHTS = {
    "guardian": {
        "safety": 0.48,
        "truth": 0.24,
        "privacy": 0.12,
        "autonomy": 0.10,
        "efficiency": 0.06,
    },
    "truth_first": {
        "safety": 0.20,
        "truth": 0.44,
        "privacy": 0.12,
        "autonomy": 0.10,
        "efficiency": 0.14,
    },
    "progress_max": {
        "safety": 0.12,
        "truth": 0.22,
        "privacy": 0.08,
        "autonomy": 0.10,
        "efficiency": 0.48,
    },
}


PRESET_THRESHOLDS = {
    "guardian": {"degrade": 0.25, "deny": 0.52, "handoff": 0.82},
    "truth_first": {"degrade": 0.29, "deny": 0.70, "handoff": 0.88},
    "progress_max": {"degrade": 0.23, "deny": 0.88, "handoff": 0.97},
}


BASE_FORBIDDEN_MODES = {
    "safety": [
        "unsafe_automation",
        "medical_overconfidence",
        "legal_overreach",
        "hidden_material_risk",
    ],
    "truth": [
        "unverified_confident_claim",
        "fabricated_authority",
        "emotional_manipulation",
        "hidden_material_risk",
    ],
    "privacy": ["privacy_leakage", "hidden_material_risk"],
    "autonomy": ["emotional_manipulation", "hidden_material_risk"],
    "efficiency": ["privacy_leakage", "unsafe_irreversible_action"],
}


def compile_profile(profile: Union[str, FiveAnchors, Mapping[str, object]]) -> CCP:
    """Compile a profile name or Five Anchors payload into a stable CCP."""

    anchors = _coerce_anchors(profile)
    weights = _compile_weights(anchors)
    dominant = max(weights, key=weights.get)
    thresholds = _compile_thresholds(anchors, dominant)
    forbidden = _compile_forbidden_modes(anchors, dominant)
    base_id = _slug(anchors.profile_name)

    unsigned = {
        "ccp_id": f"{base_id}_v1",
        "profile_name": anchors.profile_name,
        "drive_weights": weights,
        "gate_thresholds": thresholds,
        "forbidden_modes": forbidden,
        "dominant_priority": dominant,
        "version": "0.1",
    }
    fingerprint = stable_fingerprint(unsigned)
    return CCP(fingerprint=fingerprint, **unsigned)


def _coerce_anchors(profile: Union[str, FiveAnchors, Mapping[str, object]]) -> FiveAnchors:
    if isinstance(profile, FiveAnchors):
        return profile
    if isinstance(profile, str):
        return get_default_profile(profile)
    return FiveAnchors.from_dict(profile)


def _compile_weights(anchors: FiveAnchors) -> Dict[str, float]:
    if anchors.profile_name in PRESET_WEIGHTS:
        return normalize_weights(PRESET_WEIGHTS[anchors.profile_name])

    text = " ".join(
        [anchors.desire, anchors.fear, anchors.goal, anchors.priority, anchors.alternative]
    ).lower()
    weights = {axis: 0.2 for axis in AXES}
    for axis, keywords in KEYWORDS.items():
        hits = _count_hits(text, keywords)
        weights[axis] += min(0.30, hits * 0.035)

    priority = anchors.priority.lower()
    for axis, keywords in KEYWORDS.items():
        if axis in priority or any(keyword in priority for keyword in keywords):
            weights[axis] += 0.25

    return normalize_weights(weights)


def _compile_thresholds(anchors: FiveAnchors, dominant: str) -> Dict[str, float]:
    if anchors.profile_name in PRESET_THRESHOLDS:
        return dict(PRESET_THRESHOLDS[anchors.profile_name])

    if dominant == "safety":
        return {"degrade": 0.28, "deny": 0.55, "handoff": 0.82}
    if dominant == "truth":
        return {"degrade": 0.35, "deny": 0.70, "handoff": 0.88}
    if dominant == "efficiency":
        return {"degrade": 0.42, "deny": 0.86, "handoff": 0.96}
    if dominant == "privacy":
        return {"degrade": 0.30, "deny": 0.62, "handoff": 0.84}
    return {"degrade": 0.34, "deny": 0.72, "handoff": 0.90}


def _compile_forbidden_modes(anchors: FiveAnchors, dominant: str) -> List[str]:
    text = " ".join(
        [anchors.desire, anchors.fear, anchors.goal, anchors.priority, anchors.alternative]
    ).lower()
    modes: List[str] = list(BASE_FORBIDDEN_MODES.get(dominant, []))
    for axis, keywords in KEYWORDS.items():
        if _count_hits(text, keywords):
            modes.extend(BASE_FORBIDDEN_MODES.get(axis, []))

    if anchors.profile_name == "progress_max":
        modes = [
            mode
            for mode in modes
            if mode
            in {"privacy_leakage", "unsafe_irreversible_action", "hidden_material_risk"}
        ]
    elif anchors.profile_name == "guardian":
        modes.extend(
            [
                "unverified_confident_claim",
                "fabricated_authority",
                "privacy_leakage",
                "emotional_manipulation",
            ]
        )

    return dedupe(modes)


def _count_hits(text: str, keywords: Iterable[str]) -> int:
    return sum(1 for keyword in keywords if keyword in text)


def _slug(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9가-힣]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "profile"
