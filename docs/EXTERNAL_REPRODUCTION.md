# External Reproduction Path

This repository now separates three evidence levels:

1. Included-suite reproduction: fixtures and expected results checked into this repo.
2. External-style challenge reproduction: public-safe limitation-discovery fixtures checked into this repo.
3. Reviewer-provided local runs: a reviewer supplies their own CSV, JSONL, or JSON file and records only redacted metrics.

The third path is the important one for outside verification. It does not ask the
reviewer to publish raw prompts, private traces, API keys, or harmful dataset
content.

## Required Local File Shape

The external adapter accepts `.csv`, `.jsonl`, or `.json`.

Each item must include:

| Field | Meaning |
| --- | --- |
| `source` | Dataset or reviewer source label. |
| `item_id` | Stable local item id. |
| `category` | Reviewer-defined category. |
| `prompt` | Local prompt text. This is hashed, not exported. |

The bundled file `cognitive_os/benchmarks/cognitiveos_v0/external_reference_fixture.csv`
is a public-safe smoke test. It is not a third-party benchmark result.

## Commands

Run the bundled public-safe fixture:

```powershell
.\.venv\Scripts\python.exe -m cognitive_os.benchmarks.cognitiveos_v0.run_external_reference_pack --pretty
```

Run a reviewer-owned local file:

```powershell
.\.venv\Scripts\python.exe -m cognitive_os.benchmarks.cognitiveos_v0.run_external_reference_pack `
  --input C:\path\to\reviewer_dataset.jsonl `
  --dataset-label "reviewer-local-redteam-v1" `
  --pretty
```

## What The Report Emits

- source labels
- item ids
- categories
- prompt hashes
- gate decisions per profile
- trace completeness
- redaction pass rate
- gate distribution by profile and category

## What The Report Does Not Emit

- raw prompt text
- candidate text
- API keys
- local trace files
- private reviewer notes

## Reporting Back

Open a reproduction report issue and include:

- commit hash
- OS, shell, Python version
- exact command
- whether the file was bundled fixture or reviewer-provided
- dataset label, if public-safe
- redacted JSON summary
- any failure mode

Do not paste raw prompts, model outputs, private traces, or credentials into an
issue.

## External Benchmark References

This repo does not vendor third-party harmful prompt datasets. If a reviewer
wants to use a standardized red-team benchmark, they should obtain it from the
source project and transform it locally into the four-field schema above.

- JailbreakBench: https://github.com/JailbreakBench/jailbreakbench
- HarmBench: https://github.com/centerforaisafety/HarmBench

Any such run should be described as reviewer-provided local evidence unless the
dataset source, transformation, command, and environment are independently
auditable.
