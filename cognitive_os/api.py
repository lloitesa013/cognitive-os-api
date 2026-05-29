"""FastAPI surface for Cognitive OS v0.1."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from .compiler import compile_profile
from .evidence import (
    build_evidence_demo,
    build_evidence_export,
    build_evidence_report,
    build_evidence_summary,
)
from .profiles import list_default_profiles
from .protocol import build_decision_envelope
from .runtime import compare_profiles, run_prompt
from .schemas import CCP, canonical_json, stable_fingerprint
from .trace import GLOBAL_TRACE_STORE, InMemoryTraceStore
from .version import PROTOCOL_VERSION, __version__

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles
except ImportError:  # pragma: no cover - exercised only when FastAPI is absent
    FastAPI = None  # type: ignore
    HTTPException = Exception  # type: ignore
    FileResponse = None  # type: ignore
    StaticFiles = None  # type: ignore


UI_DIR = Path(__file__).resolve().parent / "static" / "ui"


def create_app(trace_store: Optional[InMemoryTraceStore] = None):
    if FastAPI is None:
        raise RuntimeError("FastAPI is not installed. Install fastapi and uvicorn to serve.")

    app = FastAPI(title="Cognitive OS API", version=__version__)
    store = trace_store or GLOBAL_TRACE_STORE
    app.state.trace_store = store

    @app.get("/ui", include_in_schema=False)
    def ui_index():
        return FileResponse(str(UI_DIR / "index.html"))

    if StaticFiles is not None:
        app.mount("/ui", StaticFiles(directory=str(UI_DIR), html=True), name="ui")

    @app.get("/health")
    def health() -> Dict[str, Any]:
        return {
            "status": "ok",
            "version": __version__,
            "protocol_version": PROTOCOL_VERSION,
            "profiles": list_default_profiles(),
        }

    @app.post("/profiles/compile")
    def profiles_compile(payload: Dict[str, Any]) -> Dict[str, Any]:
        profile_input = payload.get("profile_name") or payload
        ccp = compile_profile(profile_input)
        return ccp.to_dict()

    @app.post("/run")
    def run(payload: Dict[str, Any]) -> Dict[str, Any]:
        prompt = _require(payload, "prompt")
        provider_name = payload.get("provider", "mock")
        profile = _profile_from_payload(payload)
        result = run_prompt(
            prompt,
            profile=profile,
            provider_name=provider_name,
            trace_store=store,
        )
        include_raw = _raw_trace_requested(payload)
        return _public_run_result(result, include_raw=include_raw)

    @app.post("/compare")
    def compare(payload: Dict[str, Any]) -> Dict[str, Any]:
        prompt = _require(payload, "prompt")
        profiles: Iterable[Any] = payload.get(
            "profiles", ["guardian", "truth_first", "progress_max"]
        )
        provider_name = payload.get("provider", "mock")
        results = compare_profiles(
            prompt,
            profiles=profiles,
            provider_name=provider_name,
            trace_store=store,
        )
        include_raw = _raw_trace_requested(payload)
        if include_raw:
            _require_raw_trace_api_allowed()
            return results
        return {
            profile: {
                "gate": result["gate"],
                "final_response": result["final_response"],
                "risk_tags": result["risk_tags"],
                "decision_envelope": result["decision_envelope"],
            }
            for profile, result in results.items()
        }

    @app.get("/trace/{trace_id}")
    def get_trace(trace_id: str, view: str = "redacted") -> Dict[str, Any]:
        trace = store.get(trace_id)
        if trace is None:
            raise HTTPException(status_code=404, detail="Trace not found")
        if view == "raw":
            _require_raw_trace_api_allowed()
            return trace.to_dict()
        if view != "redacted":
            raise HTTPException(status_code=400, detail="view must be redacted or raw")
        return build_decision_envelope(
            trace,
            include_raw=False,
            raw_available=bool(trace.prompt or trace.candidate_response),
        )

    @app.post("/validate/invariance")
    def validate_invariance(payload: Dict[str, Any]) -> Dict[str, Any]:
        profile = _profile_from_payload(payload)
        ccp = profile if isinstance(profile, CCP) else compile_profile(profile)
        reloaded = CCP.from_dict(ccp.to_dict())
        canonical = canonical_json(reloaded.to_dict())
        return {
            "valid": ccp.fingerprint == reloaded.fingerprint,
            "fingerprint": ccp.fingerprint,
            "reload_fingerprint": reloaded.fingerprint,
            "canonical_hash": stable_fingerprint(canonical),
        }

    @app.post("/validate/provider-portability")
    def validate_provider_portability(payload: Dict[str, Any]) -> Dict[str, Any]:
        prompt = _require(payload, "prompt")
        profile = payload.get("profile_name", "truth_first")
        providers = payload.get(
            "providers", ["mock_openai", "mock_claude", "mock_gemini", "mock_local"]
        )
        gates = {}
        for provider in providers:
            result = run_prompt(prompt, profile=profile, provider_name=provider)
            gates[provider] = result.gate.value
        return {
            "profile": profile,
            "gates": gates,
            "gate_consistency": len(set(gates.values())) == 1,
        }

    @app.get("/evidence/summary")
    def evidence_summary() -> Dict[str, Any]:
        return build_evidence_summary()

    @app.get("/evidence/demo")
    def evidence_demo() -> Dict[str, Any]:
        return build_evidence_demo()

    @app.get("/evidence/report")
    def evidence_report() -> Dict[str, Any]:
        return build_evidence_report()

    @app.get("/evidence/export")
    def evidence_export() -> Dict[str, Any]:
        return build_evidence_export()

    return app


def _require(payload: Dict[str, Any], key: str) -> Any:
    if key not in payload:
        raise HTTPException(status_code=400, detail=f"Missing required field: {key}")
    return payload[key]


def _profile_from_payload(payload: Dict[str, Any]) -> Any:
    if "ccp" in payload:
        return CCP.from_dict(payload["ccp"])
    if "profile" in payload:
        return payload["profile"]
    if "anchors" in payload:
        return payload["anchors"]
    return payload.get("profile_name", "truth_first")


def _public_run_result(result, include_raw: bool = False) -> Dict[str, Any]:
    if include_raw:
        _require_raw_trace_api_allowed()
    envelope = build_decision_envelope(
        result.trace,
        include_raw=include_raw,
        raw_available=bool(result.trace.prompt or result.trace.candidate_response),
    )
    payload = {
        "gate": result.gate.value,
        "final_response": result.final_response,
        "risk_tags": list(result.risk_tags),
        "decision_envelope": envelope,
    }
    if include_raw:
        payload["trace"] = result.trace.to_dict()
        payload["candidate_response"] = result.candidate_response
    return payload


def _raw_trace_requested(payload: Dict[str, Any]) -> bool:
    return bool(payload.get("include_raw_trace", False))


def _require_raw_trace_api_allowed() -> None:
    allowed = os.environ.get("COGNITIVE_OS_ALLOW_RAW_TRACE_API", "false")
    if allowed.strip().lower() not in {"1", "true", "yes", "on"}:
        raise HTTPException(
            status_code=403,
            detail="Raw trace API access requires COGNITIVE_OS_ALLOW_RAW_TRACE_API=true",
        )


app = create_app() if FastAPI is not None else None
