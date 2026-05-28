# LLM Decision Verification Protocol

Protocol version: `cognitive-gate-evidence-v0.1`

The public decision envelope is the reference artifact emitted by Cognitive OS.
It is designed to make LLM gate decisions inspectable without exposing raw user
prompts or candidate model outputs by default.

## Required Fields

- `protocol_version`
- `trace_id`
- `profile_name`
- `candidate_action`
- `provider`
- `gate`
- `dominant_axis`
- `risk_score`
- `risk_tags`
- `evidence`
- `reason`
- `counterfactual`
- `ccp_fingerprint`
- `created_at`
- `prompt_hash`
- `candidate_hash`
- `redaction`

## Gate Values

- `ALLOW`
- `DEGRADE`
- `DENY`
- `HANDOFF`

## Redaction Rule

When `redaction.redacted` is `true`, the envelope must not include a `raw`
object. Raw prompt and candidate output may be exposed only when explicitly
requested and enabled by environment configuration.

## Conformance

A conformant envelope has all required fields, a valid gate, the expected
protocol version, redaction metadata, and no raw fields in redacted mode.
