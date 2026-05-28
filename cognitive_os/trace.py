"""Auditable trace storage."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import threading
from typing import Dict, Optional, Union
from uuid import uuid4

from .schemas import CCP, Candidate, GateDecision, JudgmentResult, TraceRecord


class InMemoryTraceStore:
    def __init__(self) -> None:
        self._records: Dict[str, TraceRecord] = {}

    def create(
        self,
        ccp: CCP,
        candidate: Candidate,
        judgment: JudgmentResult,
        risk_tags: list[str],
        evidence: Optional[list[str]] = None,
    ) -> TraceRecord:
        trace = _build_trace(ccp, candidate, judgment, risk_tags, evidence=evidence)
        self._records[trace.trace_id] = trace
        return trace

    def get(self, trace_id: str) -> Optional[TraceRecord]:
        return self._records.get(trace_id)

    def clear(self) -> None:
        self._records.clear()


class JsonlTraceStore(InMemoryTraceStore):
    """Append-only JSONL trace store with an in-memory read index."""

    def __init__(self, path: Union[str, Path]) -> None:
        self.path = Path(path)
        self._lock = threading.Lock()
        super().__init__()
        self._load_existing()

    def create(
        self,
        ccp: CCP,
        candidate: Candidate,
        judgment: JudgmentResult,
        risk_tags: list[str],
        evidence: Optional[list[str]] = None,
    ) -> TraceRecord:
        trace = _build_trace(ccp, candidate, judgment, risk_tags, evidence=evidence)
        line = json.dumps(trace.to_dict(), ensure_ascii=False, sort_keys=True)
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")
            self._records[trace.trace_id] = trace
        return trace

    def clear(self) -> None:
        with self._lock:
            super().clear()
            if self.path.exists():
                self.path.unlink()

    def _load_existing(self) -> None:
        if not self.path.exists():
            return
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                trace = TraceRecord.from_dict(json.loads(line))
            except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                continue
            self._records[trace.trace_id] = trace


def default_trace_path() -> Path:
    configured = os.environ.get("COGNITIVE_OS_TRACE_PATH")
    if configured:
        return Path(configured)
    return Path(".cognitive_os") / "traces.jsonl"


def _build_trace(
    ccp: CCP,
    candidate: Candidate,
    judgment: JudgmentResult,
    risk_tags: list[str],
    evidence: Optional[list[str]] = None,
) -> TraceRecord:
    store_raw = raw_trace_enabled()
    return TraceRecord(
        trace_id=f"trace_{uuid4().hex[:12]}",
        profile=ccp.profile_name,
        candidate_action=candidate.candidate_action,
        gate=GateDecision(judgment.gate),
        dominant_axis=judgment.dominant_axis,
        risk_tags=list(risk_tags),
        reason=judgment.reason,
        counterfactual=judgment.counterfactual,
        risk_score=judgment.risk_score,
        contributions=dict(judgment.contributions),
        prompt=candidate.prompt if store_raw else "",
        provider=candidate.provider,
        candidate_response=candidate.response if store_raw else "",
        ccp_fingerprint=ccp.fingerprint,
        created_at=datetime.now(timezone.utc).isoformat(),
        evidence=list(evidence or []),
    )


GLOBAL_TRACE_STORE = JsonlTraceStore(default_trace_path())


def raw_trace_enabled() -> bool:
    raw = os.environ.get("COGNITIVE_OS_RAW_TRACE", "true").strip().lower()
    return raw not in {"0", "false", "no", "off"}
