**Not a better LLM. A decision verification protocol above LLMs.**

# Cognitive OS API v0.1.5

[![Cognitive OS Verification CI](https://github.com/lloitesa013/cognitive-os-api/actions/workflows/ci.yml/badge.svg)](https://github.com/lloitesa013/cognitive-os-api/actions/workflows/ci.yml)

Cognitive OS API is a traceable LLM gate / profile / decision governance
reference architecture. It sits above upstream model output, compiles a user's
policy into a Cognitive Configuration Profile, evaluates a candidate answer or
action, and emits a public decision envelope.

In the broader AI verification portfolio, Cognitive OS is the **decision
protocol face**: it verifies whether an LLM decision should be allowed,
degraded, denied, or handed off before it becomes action or public output.

![Cognitive OS evidence viewer](docs/assets/ui-overview.png)

## 30-Second Evidence

- Profile-to-policy compilation.
- Candidate-output review before action.
- `ALLOW`, `DEGRADE`, `DENY`, and `HANDOFF` gate decisions.
- Redacted public decision envelopes.
- Local raw trace handling with explicit opt-in.
- Seed benchmark and protocol conformance behavior.

Public evidence endpoints: `/evidence/summary`, `/evidence/demo`, `/evidence/report`, and `/evidence/export`.

![Cognitive OS adversarial evidence](docs/assets/ui-adversarial-evidence.png)

## 60-Second Demo

Use this as the front-door walkthrough: candidate output becomes a
profile-specific gate, a redacted decision envelope, and a measurable evidence
report.

![Cognitive OS 60-second demo storyboard](docs/assets/demo-60-sec-storyboard.svg)

- Script: [docs/DEMO_SCRIPT_60_SEC.md](docs/DEMO_SCRIPT_60_SEC.md)
- Longer walkthrough: [docs/DEMO_SCRIPT_3_MIN.md](docs/DEMO_SCRIPT_3_MIN.md)
- Live local surface: start the FastAPI server and open `/ui`.

## Current Evidence Snapshot

```text
Gate Accuracy: 100.00%
Trace Completeness: 100.00%
Conformance Pass Rate: 100.00%
Total Decisions: 90
```

Adversarial evidence pack: 6 scenarios, 18 decisions, gate accuracy 100.00%, trace completeness 100.00%, redaction pass rate 100.00%.

## Evidence Boundary

These are included-suite measurements: 90 seed decisions, 6 adversarial
scenarios, and 18 adversarial profile decisions. They are not third-party
benchmark results, external adoption evidence, or a general safety claim.

Read: [docs/EVIDENCE_BOUNDARY.md](docs/EVIDENCE_BOUNDARY.md)

Current seed benchmark:

```text
raw_llm             Gate Accuracy 17.78%, Trace 0.00%
system_prompt_only  Gate Accuracy 66.67%, Trace 0.00%
keyword_guardrail   Gate Accuracy 17.78%, Trace 0.00%
cognitive_os        Gate Accuracy 100.00%, Trace 100.00%
```

Protocol conformance target:

```text
CognitiveOS-v0 seed decisions x profiles -> 100.00% conformant
```

These are included-suite results, not external adoption or global safety
claims.

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe cognitive_os\demo\investor_email_demo.py
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\python.exe -m cognitive_os.benchmarks.cognitiveos_v0.run_benchmark --pretty
.\.venv\Scripts\python.exe -m cognitive_os.benchmarks.cognitiveos_v0.run_baselines --pretty
.\.venv\Scripts\python.exe -m cognitive_os.benchmarks.cognitiveos_v0.run_conformance --pretty
```

Optional FastAPI server:

```powershell
.\.venv\Scripts\python.exe -m uvicorn cognitive_os.api:app --reload
```

Then open:

```text
http://127.0.0.1:8000/ui
http://127.0.0.1:8000/ui/
```

## API Shape

- `GET /health`
- `POST /profiles/compile`
- `POST /run`
- `POST /compare`
- `GET /trace/{trace_id}`
- `POST /validate/invariance`
- `POST /validate/provider-portability`
- `GET /evidence/summary`
- `GET /evidence/demo`
- `GET /evidence/export`
- `GET /evidence/report`
- `GET /ui`
- `GET /ui/`

`/run`, `/compare`, and redacted trace retrieval emit a public
`decision_envelope` that follows `cognitive-gate-evidence-v0.1`.

## Trace Privacy

Public API output is redacted by default. Raw API trace exposure requires both:

```powershell
$env:COGNITIVE_OS_ALLOW_RAW_TRACE_API="true"
```

and a request flag:

```json
{"include_raw_trace": true}
```

Local JSONL traces are written to `.cognitive_os/traces.jsonl` by default and
are ignored by git. Set `COGNITIVE_OS_RAW_TRACE=false` to disable raw prompt and
candidate persistence in local traces.

## OpenAI Adapter

Set `OPENAI_API_KEY` and choose provider `openai` or `openai:<model>`.
Set `OPENAI_MODEL` explicitly when using provider `openai` without a model
suffix.

```powershell
$env:OPENAI_API_KEY="..."
$env:OPENAI_MODEL="<available-model>"
$env:OPENAI_STORE="false"
$env:OPENAI_TIMEOUT="60"
```

`OPENAI_STORE` defaults to `false` in this adapter so generated model responses
are not stored for later retrieval unless explicitly requested.

## Reference Docs

- [docs/REFERENCE_ARCHITECTURE.md](docs/REFERENCE_ARCHITECTURE.md)
- [docs/PROTOCOL.md](docs/PROTOCOL.md)
- [docs/TRACE_PRIVACY.md](docs/TRACE_PRIVACY.md)
- [docs/BASELINE_METHOD.md](docs/BASELINE_METHOD.md)
- [docs/EVIDENCE_BOUNDARY.md](docs/EVIDENCE_BOUNDARY.md)
- [docs/DEMO_SCRIPT_60_SEC.md](docs/DEMO_SCRIPT_60_SEC.md)
- [docs/DEMO_SCRIPT_3_MIN.md](docs/DEMO_SCRIPT_3_MIN.md)

## Claim Boundary

Cognitive OS API v0.1.5 is a reference architecture for traceable LLM
gate/profile/decision governance. Under the current CognitiveOS-v0 seed
benchmark, it demonstrates deterministic gate decisions and auditable public
decision envelopes.

It does not claim to be:

- a new foundation model
- AGI
- global LLM safety SOTA
- universal harmful-response blocking
- a complete safety guarantee
- enterprise product ready

## Next Polish

The current demo surface is optimized for a three-minute reviewer walkthrough:
same candidate, three profile policies, redacted public decision envelope, and
protocol evidence. Next work should add more adversarial scenarios without
expanding the claim boundary.

## License

Apache-2.0. See [LICENSE](LICENSE).
