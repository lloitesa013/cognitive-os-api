"""Orchestration helpers for running Cognitive OS judgments."""

from __future__ import annotations

from typing import Iterable, Mapping, Optional, Union

from .analyzer import analyze_scenario
from .compiler import compile_profile
from .gate import apply_gate
from .judgment import judge
from .protocol import build_decision_envelope
from .provider import get_provider
from .schemas import CCP, FiveAnchors, RunResult
from .trace import GLOBAL_TRACE_STORE, InMemoryTraceStore


ProfileInput = Union[str, FiveAnchors, Mapping[str, object], CCP]


def run_prompt(
    prompt: str,
    profile: ProfileInput = "truth_first",
    provider_name: str = "mock",
    trace_store: Optional[InMemoryTraceStore] = None,
) -> RunResult:
    ccp = profile if isinstance(profile, CCP) else compile_profile(profile)
    provider = get_provider(provider_name)
    candidate = provider.generate(prompt)
    analysis = analyze_scenario(prompt, candidate.response, ccp)
    judgment = judge(ccp, analysis)
    final_response = apply_gate(candidate, judgment, analysis.risk_tags)
    store = trace_store or GLOBAL_TRACE_STORE
    trace = store.create(
        ccp,
        candidate,
        judgment,
        analysis.risk_tags,
        evidence=analysis.evidence,
    )
    decision_envelope = build_decision_envelope(
        trace,
        include_raw=False,
        raw_available=bool(trace.prompt or trace.candidate_response),
    )
    return RunResult(
        gate=judgment.gate,
        final_response=final_response,
        trace=trace,
        candidate_response=candidate.response,
        risk_tags=analysis.risk_tags,
        decision_envelope=decision_envelope,
    )


def compare_profiles(
    prompt: str,
    profiles: Iterable[ProfileInput] = ("guardian", "truth_first", "progress_max"),
    provider_name: str = "mock",
    trace_store: Optional[InMemoryTraceStore] = None,
) -> dict[str, dict[str, object]]:
    output: dict[str, dict[str, object]] = {}
    for profile in profiles:
        ccp = profile if isinstance(profile, CCP) else compile_profile(profile)
        result = run_prompt(
            prompt=prompt,
            profile=ccp,
            provider_name=provider_name,
            trace_store=trace_store,
        )
        output[ccp.profile_name] = result.to_dict()
    return output
