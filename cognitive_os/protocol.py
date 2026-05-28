"""Public decision protocol envelopes for Cognitive OS."""

from __future__ import annotations

import hashlib
from typing import Any, Dict

from .schemas import TraceRecord
from .version import PROTOCOL_VERSION


def build_decision_envelope(
    trace: TraceRecord,
    include_raw: bool = False,
    raw_available: bool = True,
) -> Dict[str, Any]:
    envelope: Dict[str, Any] = {
        "protocol_version": PROTOCOL_VERSION,
        "trace_id": trace.trace_id,
        "profile_name": trace.profile,
        "candidate_action": trace.candidate_action,
        "provider": trace.provider,
        "gate": trace.gate.value,
        "dominant_axis": trace.dominant_axis,
        "risk_score": trace.risk_score,
        "risk_tags": list(trace.risk_tags),
        "evidence": list(trace.evidence),
        "reason": trace.reason,
        "counterfactual": trace.counterfactual,
        "ccp_fingerprint": trace.ccp_fingerprint,
        "created_at": trace.created_at,
        "prompt_hash": stable_text_hash(trace.prompt),
        "candidate_hash": stable_text_hash(trace.candidate_response),
        "redaction": {
            "redacted": not include_raw,
            "raw_available": raw_available,
            "raw_included": include_raw,
        },
    }
    if include_raw:
        envelope["raw"] = {
            "prompt": trace.prompt,
            "candidate_response": trace.candidate_response,
        }
    return envelope


def stable_text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
