"""Judgment Core for Cognitive OS v0.1."""

from __future__ import annotations

from typing import Dict

from .schemas import CCP, AXES, AnalysisResult, GateDecision, JudgmentResult, clamp


FORBIDDEN_MODE_PENALTY = 0.16


def judge(ccp: CCP, analysis: AnalysisResult) -> JudgmentResult:
    contributions = _axis_contributions(ccp, analysis)
    forbidden_penalty = min(
        0.36, FORBIDDEN_MODE_PENALTY * len(analysis.forbidden_modes_triggered)
    )
    efficiency_credit = (
        ccp.drive_weights.get("efficiency", 0.0) * analysis.efficiency_need * 0.20
    )
    risk_score = (
        sum(contributions.values())
        + analysis.uncertainty_penalty
        + forbidden_penalty
        - efficiency_credit
    )
    risk_score = round(clamp(risk_score, upper=1.20), 4)
    gate = _gate_for_score(risk_score, ccp.gate_thresholds)
    dominant_axis = _dominant_axis(contributions, ccp.dominant_priority)
    return JudgmentResult(
        gate=gate,
        risk_score=risk_score,
        dominant_axis=dominant_axis,
        contributions={
            **contributions,
            "uncertainty_penalty": round(analysis.uncertainty_penalty, 4),
            "forbidden_mode_penalty": round(forbidden_penalty, 4),
            "efficiency_credit": round(-efficiency_credit, 4),
        },
        reason=_reason(gate, dominant_axis, analysis),
        counterfactual=_counterfactual(analysis),
    )


def _axis_contributions(ccp: CCP, analysis: AnalysisResult) -> Dict[str, float]:
    return {
        axis: round(
            ccp.drive_weights.get(axis, 0.0) * analysis.axis_risks.get(axis, 0.0), 4
        )
        for axis in AXES
    }


def _gate_for_score(score: float, thresholds: Dict[str, float]) -> GateDecision:
    if score < thresholds["degrade"]:
        return GateDecision.ALLOW
    if score < thresholds["deny"]:
        return GateDecision.DEGRADE
    if score < thresholds["handoff"]:
        return GateDecision.DENY
    return GateDecision.HANDOFF


def _dominant_axis(contributions: Dict[str, float], fallback: str) -> str:
    axis, value = max(contributions.items(), key=lambda item: item[1])
    if value <= 0:
        return fallback
    return axis


def _reason(gate: GateDecision, dominant_axis: str, analysis: AnalysisResult) -> str:
    tags = ", ".join(analysis.risk_tags) or "no material risk tags"
    if gate == GateDecision.ALLOW:
        return f"Risk stayed below policy thresholds; observed tags: {tags}."
    if gate == GateDecision.DEGRADE:
        return (
            f"The candidate can proceed only in a weaker form because {dominant_axis} "
            f"risk is material; observed tags: {tags}."
        )
    if gate == GateDecision.DENY:
        return (
            f"The candidate conflicts with the CCP on {dominant_axis} strongly enough "
            f"to block execution; observed tags: {tags}."
        )
    return (
        f"The candidate exceeds the handoff threshold on {dominant_axis}; observed "
        f"tags: {tags}."
    )


def _counterfactual(analysis: AnalysisResult) -> str:
    tags = set(analysis.risk_tags)
    if "unverified_claim" in tags or "unverified_confident_claim" in tags:
        return (
            "If supporting evidence were provided and uncertainty were disclosed, "
            "the request could move to a lower-risk gate."
        )
    if "privacy_leakage" in tags:
        return (
            "If personal or confidential data were removed or consent were verified, "
            "the request could be reconsidered."
        )
    if "medical_overconfidence" in tags or "legal_overreach" in tags:
        return (
            "If framed as general information with expert review rather than final "
            "advice, the request could be safer."
        )
    if "unsafe_automation" in tags:
        return (
            "If irreversible execution were replaced by a reversible dry run, the "
            "request could be reconsidered."
        )
    return "If material risks remain absent, the request can be allowed."
