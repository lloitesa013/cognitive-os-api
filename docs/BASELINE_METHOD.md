# Baseline Scoring Method

CognitiveOS-v0 compares Cognitive OS with three deterministic baselines:

- `raw_llm`: upstream provider output with no gate.
- `system_prompt_only`: upstream provider output with a generic safety prompt.
- `keyword_guardrail`: a simple blocklist-style guardrail.

For non-gated baselines, gate accuracy is evaluated by mapping the baseline
output to the expected gate label through the benchmark evaluator. Trace
completeness is zero unless the baseline emits a structured auditable trace.

This makes the comparison narrow: it tests whether a method produces the
expected benchmark gate and an auditable trace. It is not a claim that Cognitive
OS is superior to every guardrail, safety system, or provider policy.

Current claim boundary:

> Cognitive OS outperforms raw LLM, system-prompt-only, and keyword guardrail
> baselines on the current CognitiveOS-v0 seed benchmark in gate accuracy and
> trace completeness.

Non-claims:

- Cognitive OS is not claimed to be a SOTA language model.
- Cognitive OS is not claimed to solve universal AI alignment.
- Cognitive OS is not yet validated across all OpenAI, Claude, Gemini, local,
  and enterprise deployments.
- Cognitive OS is not yet enterprise product ready.
