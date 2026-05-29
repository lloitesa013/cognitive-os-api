# Cognitive OS API 3-Minute Demo Script

## 0:00-0:30 - Problem

LLM applications can produce useful answers, but their final decisions are hard
to verify. When an answer is allowed, softened, denied, or escalated, teams need
to know which policy axis drove the decision and whether the output conforms to
a repeatable protocol.

## 0:30-1:00 - Baseline Gap

Raw LLM calls, system prompts, and keyword guardrails can improve behavior, but
they do not reliably emit auditable gate decisions, redacted public traces, or
protocol conformance evidence.

## 1:00-1:45 - Cognitive OS Position

Cognitive OS API is not a better LLM. It is a decision verification protocol
above LLMs. The upstream model generates candidates; Cognitive OS applies a
profile-specific CCP, analyzes risk, decides `ALLOW`, `DEGRADE`, `DENY`, or
`HANDOFF`, and returns a redacted Decision Envelope.

## 1:45-2:30 - UI Walkthrough

Open `/ui`. Start on Overview, then open `3-Minute Demo`. Show the sequence:
the candidate request appears as a hash, three profile policies gate the same
candidate differently, and the public artifact stays redacted by default. Point
to the four headline numbers: Gate Accuracy 100.00%, Trace Completeness
100.00%, Conformance Pass Rate 100.00%, and Total Decisions 90.

Then open Decision Envelope. Use the anatomy table first, then the JSON payload:
`trace_id`, `profile`, `gate`, `axis`, `reason`, `counterfactual`, and
`risk_tags` are the reviewable public fields. Close by opening Conformance and
Baseline Comparison to show why gate plus trace is the differentiator.

## 2:30-3:00 - Close

The claim is intentionally narrow: Cognitive OS is a traceable LLM gate /
profile / decision governance reference architecture. It is not AGI, not global
LLM safety SOTA, not universal harmful-response blocking, and not a complete
safety guarantee.

Final line: Not a better LLM. A decision verification protocol above LLMs.
