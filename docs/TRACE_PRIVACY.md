# Trace Privacy

Cognitive OS separates public decision evidence from raw local audit data.

## Public Output

API responses expose redacted decision envelopes by default. They include stable
hashes for prompt and candidate content, but not the raw text.

## Raw Local Audit

Local JSONL traces are written to `.cognitive_os/traces.jsonl` by default. This
directory is ignored by git because traces may include user prompts and candidate
model outputs.

Disable raw local trace persistence:

```powershell
$env:COGNITIVE_OS_RAW_TRACE="false"
```

Allow raw API trace exposure only for local debugging:

```powershell
$env:COGNITIVE_OS_ALLOW_RAW_TRACE_API="true"
```

Then request raw trace explicitly with:

```json
{"include_raw_trace": true}
```
