"""Conformance checks for Cognitive Gate Evidence protocol envelopes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping

from .schemas import GateDecision
from .version import PROTOCOL_VERSION


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
    "evidence",
    "reason",
    "counterfactual",
    "ccp_fingerprint",
    "created_at",
    "prompt_hash",
    "candidate_hash",
    "redaction",
)


@dataclass(frozen=True)
class ConformanceResult:
    valid: bool
    failures: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {"valid": self.valid, "failures": list(self.failures)}


def validate_decision_envelope(envelope: Mapping[str, Any]) -> ConformanceResult:
    failures: List[str] = []
    for field in REQUIRED_ENVELOPE_FIELDS:
        if field not in envelope:
            failures.append(f"missing:{field}")

    if envelope.get("protocol_version") != PROTOCOL_VERSION:
        failures.append("invalid:protocol_version")

    try:
        GateDecision(envelope.get("gate"))
    except ValueError:
        failures.append("invalid:gate")

    if not isinstance(envelope.get("risk_score"), (int, float)):
        failures.append("invalid:risk_score")

    if not isinstance(envelope.get("risk_tags"), list):
        failures.append("invalid:risk_tags")

    if not isinstance(envelope.get("evidence"), list):
        failures.append("invalid:evidence")

    redaction = envelope.get("redaction")
    if not isinstance(redaction, Mapping):
        failures.append("invalid:redaction")
    else:
        redacted = bool(redaction.get("redacted"))
        raw_included = bool(redaction.get("raw_included"))
        if redacted and "raw" in envelope:
            failures.append("redaction:raw_present_when_redacted")
        if raw_included and "raw" not in envelope:
            failures.append("redaction:raw_missing_when_included")

    for field in ("trace_id", "profile_name", "provider", "reason", "counterfactual"):
        if field in envelope and not envelope.get(field):
            failures.append(f"empty:{field}")

    return ConformanceResult(valid=not failures, failures=failures)
