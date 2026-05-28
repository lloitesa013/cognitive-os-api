"""Gate Layer response shaping."""

from __future__ import annotations

import re
from typing import Iterable

from .schemas import Candidate, GateDecision, JudgmentResult


def apply_gate(candidate: Candidate, judgment: JudgmentResult, risk_tags: Iterable[str]) -> str:
    tags = set(risk_tags)
    if judgment.gate == GateDecision.ALLOW:
        return candidate.response
    if judgment.gate == GateDecision.DEGRADE:
        return _degraded_response(candidate, tags)
    if judgment.gate == GateDecision.DENY:
        return _denied_response(candidate, judgment)
    return _handoff_response(candidate, judgment)


def _degraded_response(candidate: Candidate, tags: set[str]) -> str:
    if _looks_korean(candidate.prompt):
        if "unverified_claim" in tags or "unverified_confident_claim" in tags:
            return (
                "검증되지 않은 내용을 확신처럼 표현하지 않는 조건으로만 도와드릴 수 있습니다.\n\n"
                "제목: 확인 중인 업데이트 공유\n\n"
                "안녕하세요,\n\n"
                "현재 일부 지표와 전망은 아직 검증 중입니다. 그래서 확정된 사실처럼 "
                "말하기보다는, 확인된 내용과 가설을 구분해 공유드리고자 합니다. "
                "검증이 완료되는 대로 근거와 함께 업데이트드리겠습니다.\n\n"
                "감사합니다."
            )
        return (
            "요청은 진행할 수 있지만, 중요한 위험을 낮추기 위해 표현을 제한했습니다.\n\n"
            f"{_soften_confidence(candidate.response)}"
        )

    if "unverified_claim" in tags or "unverified_confident_claim" in tags:
        return (
            "I can help only if the draft clearly marks unverified claims as uncertain.\n\n"
            "Subject: Update under review\n\n"
            "Hi,\n\n"
            "Some figures and projections are still being verified. Rather than present "
            "them as settled facts, I want to separate confirmed information from current "
            "assumptions and follow up with evidence once validation is complete.\n\n"
            "Best,"
        )
    return (
        "The request can proceed in a safer, narrower form:\n\n"
        f"{_soften_confidence(candidate.response)}"
    )


def _denied_response(candidate: Candidate, judgment: JudgmentResult) -> str:
    if _looks_korean(candidate.prompt):
        return (
            "이 요청은 현재 정책 기준에서는 실행할 수 없습니다. "
            f"{judgment.reason} {judgment.counterfactual}"
        )
    return (
        "I cannot execute this request under the current policy. "
        f"{judgment.reason} {judgment.counterfactual}"
    )


def _handoff_response(candidate: Candidate, judgment: JudgmentResult) -> str:
    if _looks_korean(candidate.prompt):
        return (
            "이 요청은 사람 또는 더 좁은 전문 검토로 넘겨야 합니다. "
            f"{judgment.reason} {judgment.counterfactual}"
        )
    return (
        "This request needs human or specialist-tool handoff. "
        f"{judgment.reason} {judgment.counterfactual}"
    )


def _soften_confidence(text: str) -> str:
    replacements = {
        r"\bguarantee\b": "currently expect",
        r"\bcertain\b": "not yet certain",
        r"\bdefinitely\b": "currently expect",
        r"확신합니다": "현재로서는 조심스럽게 보고 있습니다",
        r"반드시": "가능성이 있습니다",
        r"절대": "현재 근거로는 단정하기 어렵지만",
    }
    softened = text
    for pattern, replacement in replacements.items():
        softened = re.sub(pattern, replacement, softened, flags=re.IGNORECASE)
    return softened


def _looks_korean(text: str) -> bool:
    return bool(re.search(r"[가-힣]", text))
