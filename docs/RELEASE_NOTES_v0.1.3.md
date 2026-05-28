# Cognitive OS API v0.1.3 Release Notes

## Release Name

Cognitive OS API v0.1.3

Benchmark-aware judgment-layer prototype.

## Positioning

Not a better LLM. A judgment layer above LLMs.

Cognitive OS API v0.1.3 is a benchmark-aware prototype of a user-owned judgment
layer for LLM systems. It does not claim to be a SOTA language model or a
universal AI safety solution.

## Included

- Five Anchors -> CCP compiler
- Mock and OpenAI provider adapters
- Analyzer, Judgment Core, Gate Layer, Trace Layer
- FastAPI endpoints
- Investor email demo
- CognitiveOS-v0 seed benchmark with 30 scenarios
- Baseline comparison runner
- JSON baseline artifact
- Apache-2.0 license

## Current Benchmark Result

```text
raw_llm             Gate Accuracy 17.78%, Trace 0.00%
system_prompt_only  Gate Accuracy 66.67%, Trace 0.00%
keyword_guardrail   Gate Accuracy 17.78%, Trace 0.00%
cognitive_os        Gate Accuracy 100.00%, Trace 100.00%
```

## Claim Boundary

Cognitive OS outperforms raw LLM, system-prompt-only, and keyword guardrail
baselines on the current CognitiveOS-v0 seed benchmark in gate accuracy and
trace completeness.

This is not a claim of universal guardrail superiority, SOTA AI safety, or
enterprise readiness.

## Verification

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\python.exe -m cognitive_os.benchmarks.cognitiveos_v0.run_benchmark --pretty
.\.venv\Scripts\python.exe -m cognitive_os.benchmarks.cognitiveos_v0.run_baselines --pretty
```
