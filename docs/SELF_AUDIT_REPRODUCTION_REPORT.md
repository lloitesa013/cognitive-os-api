# Maintainer Self-Audit Reproduction Report

This is a maintainer self-audit, not an outside reproduction report and not a
third-party benchmark result. Its purpose is to test the reviewer-provided local
file path before asking an outside person to use it.

## Result

- Reproduced as documented: yes
- Input type: reviewer-style local JSONL
- Dataset label: `maintainer-self-audit-v1`
- Provider: `mock`
- Network required: no
- API key required: no
- OpenAI model name required: no
- Raw prompts included in this report: no
- Candidate/model output text included in this report: no

## Environment

- OS: Windows
- Shell: PowerShell
- Python: local `.venv` Python
- Commit tested before this report: `f7f48f0`

## Command Shape

The local JSONL contained one public-safe item with the required fields:
`source`, `item_id`, `category`, and `prompt`. The prompt itself is not pasted
here; the adapter emitted only the prompt hash.

```powershell
.\.venv\Scripts\python.exe -m cognitive_os.benchmarks.cognitiveos_v0.run_external_reference_pack `
  --input .self_audit_reviewer.jsonl `
  --dataset-label maintainer-self-audit-v1 `
  --pretty
```

OS-neutral equivalent:

```bash
python -m cognitive_os.benchmarks.cognitiveos_v0.run_external_reference_pack \
  --input ./self_audit_reviewer.jsonl \
  --dataset-label maintainer-self-audit-v1 \
  --pretty
```

## Redacted Summary Metrics

```json
{
  "benchmark_type": "external_reference_pack",
  "run_type": "reviewer_provided_local_file",
  "third_party_benchmark": false,
  "external_input_provided": true,
  "dataset_label": "maintainer-self-audit-v1",
  "provider": "mock",
  "item_count": 1,
  "profile_count": 3,
  "total_decisions": 3,
  "trace_completeness": 1.0,
  "redaction_pass_rate": 1.0,
  "profile_separation_rate": 1.0,
  "gate_distribution_by_profile": {
    "guardian": {"DENY": 1},
    "truth_first": {"DEGRADE": 1},
    "progress_max": {"DEGRADE": 1}
  }
}
```

## Friction Found And Fixed

The first PowerShell-created JSONL file included a UTF-8 byte-order mark. The
adapter initially rejected that file with a JSON decode error. The loader now
reads `.json` and `.jsonl` inputs with `utf-8-sig`, matching the already tolerant
CSV path.

This matters because a reviewer using Windows tooling can create a valid-looking
JSONL file that carries a BOM. The adapter should handle that case clearly.

## Boundary

This report proves only that the maintainer could run the local-file path and
that the default adapter path does not require network access. It does not prove
external adoption, third-party benchmark performance, broad model safety, or
production readiness.
