# Reviewer benchmark

Mode: fixtures_only; labels: agent_reviewed_pending_human

These are agreement measurements against proposed labels, not human-gold accuracy.

| Case | Repeat | Expected | Actual | Validator | Error |
|---|---:|---|---|---|---|
| A1 | 1 | accept | None | accept | None |
| A2 | 1 | accept | None | accept | None |
| A3 | 1 | accept | None | accept | None |
| R1 | 1 | reject | None | accept | None |
| R2 | 1 | reject | None | accept | None |
| R3 | 1 | reject | None | accept | None |
| R4 | 1 | reject | None | accept | None |
| N1 | 1 | needs_more_evidence | None | accept | None |
| N2 | 1 | needs_more_evidence | None | accept | None |
| N3 | 1 | needs_more_evidence | None | accept | None |
| V1 | 1 | None | None | reject | None |
| V2 | 1 | None | None | reject | None |

```json
{
  "eligible": 10,
  "valid_decisions": 0,
  "runtime_errors": 0,
  "confusion_matrix": {
    "accept": {
      "accept": 0,
      "reject": 0,
      "needs_more_evidence": 0
    },
    "reject": {
      "accept": 0,
      "reject": 0,
      "needs_more_evidence": 0
    },
    "needs_more_evidence": {
      "accept": 0,
      "reject": 0,
      "needs_more_evidence": 0
    }
  },
  "agreement": null,
  "false_reject_count": 0,
  "false_reject_denominator": 0,
  "false_reject_rate": null,
  "missed_reject_count": 0,
  "missed_reject_denominator": 0,
  "missed_reject_rate": null,
  "unsafe_accept_count": 0,
  "confidence_out_of_range": 0
}
```

## Proposed-label rationale
- A1: Quote explicitly states the backbone and application. No claim of global novelty or measured speed.
- A2: Direct paraphrase of the archived conclusion; no performance extrapolation.
- A3: An abstract can support a bounded architecture claim without full-text access.
- R1: The asserted backbone directly contradicts the quoted Transformer decoder backbone.
- R2: Quote explicitly includes a memory-based module.
- R3: A temporal graph architecture claim has no semantic support for catalytic yield, despite matching task IDs and high input relevance.
- R4: Overlap and difference explicitly contradict each other and the quote.
- N1: Architecture is supported, but the supplied quote contains no measurements. Request experiment evidence rather than infer falsehood from absence.
- N2: The quote does not identify the memory update architecture. Missing evidence cannot establish absence of RNNs.
- N3: Only an abstract architecture sentence is supplied, no theorem. The universal claim is unsupported; do not assert it has been disproved.
- V1: Missing DOI and URL is a deterministic Validator failure and must not consume a Reviewer call.
- V2: Missing source location belongs to Validator, not semantic Reviewer.
