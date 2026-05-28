# Cognitive OS API v0.1.4 Release Notes

## Release Name

Cognitive OS API v0.1.4

Traceable LLM gate/profile/decision governance reference architecture.

## Added

- Cognitive Gate Evidence decision envelope
- Protocol version `cognitive-gate-evidence-v0.1`
- Redacted public trace behavior
- Optional raw local audit trace controls
- Protocol conformance validator
- CognitiveOS-v0 conformance runner and JSON artifact
- Reference architecture and protocol docs

## Claim Boundary

Cognitive OS API v0.1.4 is a reference architecture for LLM decision
verification. It does not claim global LLM safety SOTA, universal harmful-output
blocking, or AGI OS status.

## Verification

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\python.exe -m cognitive_os.benchmarks.cognitiveos_v0.run_benchmark --pretty
.\.venv\Scripts\python.exe -m cognitive_os.benchmarks.cognitiveos_v0.run_baselines --pretty
.\.venv\Scripts\python.exe -m cognitive_os.benchmarks.cognitiveos_v0.run_conformance --pretty
```
