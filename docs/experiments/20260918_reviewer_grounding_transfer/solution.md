# Reviewer grounding: offline implementation

Baseline: `lya` at `546c59304eba32314df5d6bb79cd2d7d4f308cf4`. Scope: Reviewer summary assembly, citation integrity, prompts, Debug, and local tests. No business model or network calls were made in this round.

## Mechanism

`_compact_summary_rows` now orders evidence cited by a card ahead of selected background reads, while preserving the fixed 12,000-character budget per card. It records each exact original quote hash, displayed text hash, source fields where available, and `full`/`partial`/`omitted`. A selected read that is not in a comparison remains in the ledger as `selected=true`, `cited_by_card=false`; no semantic support is inferred. Empty displayed quotes are excluded from summary-citable IDs. `_verify_summary_payload` checks the serialized user message before the client call. Runtime records `summary_payload_prepared`, `summary_request_dispatched`, and `summary_response_received` separately. Only the last two stages can indicate an attempted real request and received response.

These rules inspect input identity, source and display bytes, not the identity or expected outcome of any paper. A full quote passes; a quote that exceeds budget is marked partial, while a later empty quote is omitted and cannot be cited. The harness does not decide whether a quoted statement entails a technical claim.

The three Reviewer prompts and fallback instructions now ask for per-feature supporting references, local relation scope, and a distinction between missing information and conflict. A background read can be selected without being used as a feature argument. No production rule matches known paper IDs, titles or domain terms. This can still fail semantically: tests of deterministic code and scripted clients cannot prove that a real model makes sound technical comparisons.

## Local result

Historical L1 S0 sent two nonempty original evidence quotes. Offline S1 assembly from the same frozen card reviews prepares nine nonempty quotes, including seven registered `rev_ev_*` items. See `payload-diff.json` and `evidence-lineage.json`. S1 is `sent_to_model=false`; this result establishes preparation and the scripted client boundary, not a new model judgment.

Two distinct music and attention related source Works from the existing MG archive were selected after the prompts were edited. Their card, point, source artifact and prompt hashes are frozen in `holdout-manifest.json`. No holdout model decision was run, so generalization is **not yet tested**.
