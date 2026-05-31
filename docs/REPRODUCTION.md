# Reproduction Guide

This guide is for reviewers who want to clone the repository, run the evidence
commands, and compare their local result with the public README claims.

## Scope

This is a reference architecture reproduction path. It checks deterministic
gate behavior, redacted evidence exports, benchmark scripts, and protocol
conformance for the included CognitiveOS-v0 suites.

It does not establish third-party adoption, broad model capability, complete
safety coverage, or production readiness.

## Environment

CI currently runs on:

- Ubuntu 22.04
- Python 3.7
- `requirements-dev.txt`

Local Windows PowerShell reproduction is expected to work with Python 3.7 or
newer.

## Fresh Clone

```powershell
git clone https://github.com/lloitesa013/cognitive-os-api.git
cd cognitive-os-api
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

## Verification Commands

```powershell
.\.venv\Scripts\python.exe -m unittest -v tests.test_api tests.test_benchmark tests.test_provider
.\.venv\Scripts\python.exe -m cognitive_os.benchmarks.cognitiveos_v0.run_adversarial
.\.venv\Scripts\python.exe -m cognitive_os.benchmarks.cognitiveos_v0.run_challenge_pack --pretty
.\.venv\Scripts\python.exe -m cognitive_os.benchmarks.cognitiveos_v0.run_benchmark --pretty
.\.venv\Scripts\python.exe -m cognitive_os.benchmarks.cognitiveos_v0.run_baselines --pretty
.\.venv\Scripts\python.exe -m cognitive_os.benchmarks.cognitiveos_v0.run_conformance --pretty
```

## Expected Result

The unit command should report 16 tests passing, with one OpenAI integration
test skipped unless explicitly enabled.

Included seed/adversarial suites should reproduce the README's headline
metrics. The external-style challenge pack is intentionally harder and should
currently report:

```text
scenario_count: 8
total_decisions: 24
gate_accuracy: 0.375
trace_completeness: 1.0
redaction_pass_rate: 1.0
third_party_benchmark: false
```

The lower challenge-pack gate score is limitation evidence. It should not be
rewritten into a success claim.

## Evidence Privacy Check

Public evidence endpoints and exports should not expose raw prompt text or raw
candidate text. They should emit scenario ids, categories, prompt hashes, gate
decisions, trace checks, and redaction checks.

Local raw traces are controlled by the settings in
[TRACE_PRIVACY.md](TRACE_PRIVACY.md). Do not publish local trace files.

## OpenAI Adapter Smoke Test

The OpenAI integration test is off by default. To run it, set:

```powershell
$env:COGNITIVE_OS_RUN_OPENAI_INTEGRATION="1"
$env:OPENAI_API_KEY="<redacted>"
$env:OPENAI_MODEL="<available-model>"
```

Do not paste API keys, raw prompts, or private traces into issues.

## Reporting A Mismatch

Open a reproduction report with:

- OS and shell
- Python version
- Commit hash
- Exact command
- Full terminal output
- Whether `.venv` was freshly created
- Any environment variables used, with secrets redacted

Use the reproduction report issue template so the result can be compared without
guesswork.
