# Evidence Boundary

Cognitive OS API reports included-suite evidence. The current public numbers
are useful for checking whether the reference architecture is internally
consistent, reproducible, and traceable. They are not evidence of external
adoption or general safety.

## What The Current Evidence Supports

- The included seed benchmark can be rerun locally and in CI.
- The public API emits redacted decision envelopes by default.
- The included profile policies produce repeatable gate decisions under the
  mock provider.
- The public adversarial evidence report keeps raw prompt and candidate text
  out of reviewer-facing payloads.

## What The Current Evidence Does Not Support

- It is not a third-party benchmark result.
- It is not external adoption evidence.
- It is not a claim of general LLM safety.
- It is not a claim of universal harmful-response blocking.
- It is not a complete safety guarantee.

## Current Evidence Scale

| Evidence surface | Current size |
| --- | ---: |
| Seed benchmark decisions | 90 |
| Adversarial scenarios | 6 |
| Adversarial profile decisions | 18 |

The 100.00% values in the README are included-suite measurements. They should
be read as a reproducibility and protocol-conformance signal, not as a global
performance claim.
