# Cognitive OS API 60-Second Demo Script

## 0:00-0:10 - Problem

LLM apps often stop at generated text. Cognitive OS starts after generation:
it verifies whether a candidate decision should be allowed, degraded, denied,
or handed off before it becomes action or public output.

## 0:10-0:25 - Profile-Specific Gates

Show the same candidate request under three policy profiles. The public demo
does not need the raw prompt: the useful evidence is that each profile produces
a repeatable gate, axis, reason, and counterfactual.

## 0:25-0:40 - Redacted Decision Envelope

Open the Decision Envelope view. Point to the reviewable public fields:
`trace_id`, `profile_name`, `gate`, `dominant_axis`, `risk_tags`, `reason`,
`counterfactual`, `prompt_hash`, `candidate_hash`, and `redaction`.

## 0:40-0:55 - Evidence Report

Open the evidence report surface. The current public evidence pack reports
6 adversarial scenarios, 18 profile decisions, gate accuracy 100.00%, trace
completeness 100.00%, and redaction pass rate 100.00% for the included suite.

## 0:55-1:00 - Boundary

Close with the boundary: Cognitive OS API is not AGI, not global LLM safety
SOTA, not universal harmful-response blocking, and not a complete safety
guarantee. It is a decision verification protocol above LLMs.

Final line: Not a better LLM. A decision verification protocol above LLMs.
