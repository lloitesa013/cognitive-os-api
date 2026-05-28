"""Shared schemas for Cognitive OS v0.1.

The project intentionally uses standard-library dataclasses for the core
engine so the judgment layer stays portable and easy to inspect.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
import hashlib
import json
from typing import Any, Dict, Iterable, List, Mapping, Optional


class GateDecision(str, Enum):
    ALLOW = "ALLOW"
    DEGRADE = "DEGRADE"
    DENY = "DENY"
    HANDOFF = "HANDOFF"


AXES = ("safety", "truth", "privacy", "autonomy", "efficiency")


@dataclass(frozen=True)
class FiveAnchors:
    profile_name: str
    desire: str
    fear: str
    goal: str
    priority: str
    alternative: str

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "FiveAnchors":
        missing = [
            key
            for key in (
                "profile_name",
                "desire",
                "fear",
                "goal",
                "priority",
                "alternative",
            )
            if key not in data
        ]
        if missing:
            raise ValueError(f"Missing Five Anchors fields: {', '.join(missing)}")
        return cls(
            profile_name=str(data["profile_name"]),
            desire=str(data["desire"]),
            fear=str(data["fear"]),
            goal=str(data["goal"]),
            priority=str(data["priority"]),
            alternative=str(data["alternative"]),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CCP:
    ccp_id: str
    profile_name: str
    drive_weights: Dict[str, float]
    gate_thresholds: Dict[str, float]
    forbidden_modes: List[str]
    dominant_priority: str
    version: str = "0.1"
    fingerprint: str = ""

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "CCP":
        return cls(
            ccp_id=str(data["ccp_id"]),
            profile_name=str(data["profile_name"]),
            drive_weights={str(k): float(v) for k, v in data["drive_weights"].items()},
            gate_thresholds={
                str(k): float(v) for k, v in data["gate_thresholds"].items()
            },
            forbidden_modes=[str(item) for item in data.get("forbidden_modes", [])],
            dominant_priority=str(data["dominant_priority"]),
            version=str(data.get("version", "0.1")),
            fingerprint=str(data.get("fingerprint", "")),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Candidate:
    prompt: str
    response: str
    provider: str
    candidate_action: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AnalysisResult:
    risk_tags: List[str]
    axis_risks: Dict[str, float]
    uncertainty_penalty: float
    efficiency_need: float
    forbidden_modes_triggered: List[str]
    evidence: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class JudgmentResult:
    gate: GateDecision
    risk_score: float
    dominant_axis: str
    contributions: Dict[str, float]
    reason: str
    counterfactual: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["gate"] = self.gate.value
        return data


@dataclass(frozen=True)
class TraceRecord:
    trace_id: str
    profile: str
    candidate_action: str
    gate: GateDecision
    dominant_axis: str
    risk_tags: List[str]
    reason: str
    counterfactual: str
    risk_score: float
    contributions: Dict[str, float]
    prompt: str
    provider: str
    candidate_response: str
    ccp_fingerprint: str
    created_at: str
    evidence: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["gate"] = self.gate.value
        return data

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "TraceRecord":
        return cls(
            trace_id=str(data["trace_id"]),
            profile=str(data["profile"]),
            candidate_action=str(data["candidate_action"]),
            gate=GateDecision(data["gate"]),
            dominant_axis=str(data["dominant_axis"]),
            risk_tags=[str(item) for item in data.get("risk_tags", [])],
            reason=str(data["reason"]),
            counterfactual=str(data["counterfactual"]),
            risk_score=float(data["risk_score"]),
            contributions={
                str(key): float(value)
                for key, value in data.get("contributions", {}).items()
            },
            prompt=str(data["prompt"]),
            provider=str(data["provider"]),
            candidate_response=str(data["candidate_response"]),
            ccp_fingerprint=str(data["ccp_fingerprint"]),
            created_at=str(data["created_at"]),
            evidence=[str(item) for item in data.get("evidence", [])],
        )


@dataclass(frozen=True)
class RunResult:
    gate: GateDecision
    final_response: str
    trace: TraceRecord
    candidate_response: str
    risk_tags: List[str]
    decision_envelope: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gate": self.gate.value,
            "final_response": self.final_response,
            "trace": self.trace.to_dict(),
            "candidate_response": self.candidate_response,
            "risk_tags": list(self.risk_tags),
            "decision_envelope": dict(self.decision_envelope),
        }


def canonical_json(value: Any) -> str:
    """Return a stable JSON representation for fingerprints and tests."""

    if is_dataclass(value):
        value = asdict(value)
    elif isinstance(value, Enum):
        value = value.value
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def stable_fingerprint(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()[:16]


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def dedupe(items: Iterable[str]) -> List[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result


def normalize_weights(weights: Mapping[str, float]) -> Dict[str, float]:
    complete = {axis: max(0.0, float(weights.get(axis, 0.0))) for axis in AXES}
    total = sum(complete.values())
    if total <= 0:
        return {axis: 1.0 / len(AXES) for axis in AXES}
    return {axis: round(value / total, 4) for axis, value in complete.items()}
