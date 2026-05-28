# Reference Architecture

Cognitive OS API v0.1.4 is a traceable LLM gate/profile/decision governance
reference architecture.

## Layers

```text
User Input
  -> Profile Layer
  -> CCP Compiler
  -> Upstream Provider
  -> Scenario Analyzer
  -> Judgment Core
  -> Gate Layer
  -> Trace Layer
  -> Decision Envelope
```

The upstream provider generates candidate content. Cognitive OS judges the
candidate against a user-owned CCP and emits a gate plus evidence-backed trace.

## Reference Architecture Claims

- Profile-dependent policy behavior
- Final gate authority
- Redacted public decision envelope
- Optional raw local audit trace
- Reproducible benchmark and conformance runners

## Non-Claims

- Not global LLM safety SOTA
- Not a universal harmful-response blocker
- Not an AGI OS
- Not enterprise-ready without further hardening
