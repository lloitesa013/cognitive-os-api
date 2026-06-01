# External Result Reporting

Use this document when you want to report a local reproduction or external
reference run without leaking private data.

## Paste This

- Repository commit hash.
- OS, shell, and Python version.
- Exact command.
- Whether the input was bundled fixture or reviewer-provided.
- Dataset label or source name, if it is safe to name.
- Redacted metrics JSON.
- Pass/fail summary.
- Any mismatch or unclear behavior.

## Do Not Paste This

- Raw prompts.
- Candidate/model output text.
- API keys.
- Local trace files.
- Private user data.
- Brown/admissions material or unrelated personal documents.

## Evidence Labels

Use these labels precisely:

| Label | Meaning |
| --- | --- |
| Included-suite run | Uses fixtures and expected gates included in this repository. |
| External-style challenge run | Uses this repository's public-safe challenge pack. |
| Bundled external fixture run | Uses the small public-safe external adapter smoke test. |
| Reviewer-provided local run | Uses a local file supplied by the reviewer. |
| Third-party benchmark result | Only use when dataset source, transformation, command, and environment are auditable. |

## Minimal Issue Template Text

```text
Commit:
OS / shell / Python:
Command:
Input type: bundled fixture / reviewer-provided local file
Dataset label:
Raw prompts included in this issue: no
Candidate text included in this issue: no
Summary metrics:
Observed mismatch:
```

## Why This Exists

The goal is outside verification without moving private or harmful raw text into
the public repository. The public artifact should show behavior, hashes, and
metrics, not the underlying sensitive content.
