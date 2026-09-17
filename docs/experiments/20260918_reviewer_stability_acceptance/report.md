# RV-STABLE-20260918: stability acceptance

## Four separate conclusions

| Layer | Status | Result and boundary |
|---|---|---|
| Deterministic mechanism | `passed_limited_scope` | Local production-boundary tests cover response milestones, cancellation, late completion, deadline expiry and status projection. |
| Fixed S1 summary repetition | `passed_limited_scope` | First sandbox batch: one EPERM attempt, then two stopped runs. Under the same cap after the network gate, the exact frozen S1 request completed 3/3 times, one physical call each, with identical feature relations. This supports fixed-input node completion in a small batch. |
| Semantic / cross-case | `inconclusive` | Two frozen abstract-only holdouts completed; four authored controls produced expected scoped observations. S1 still has multiple possible absence-to-contradiction overclaims; see `analysis/claim-evidence-comparison.md`. |
| Live full-product stability | `not_tested` | No new whole-paper workflow, upload or live browser run. |

## Timeout location and repairs

Historical S1 was cancelled after 180.091 seconds at the model-client wait, with no captured response header, body, response ID or usage. Its remote cause is unknown. A local minimal reproducer showed a possible `asyncio.to_thread()` wakeup fault, so `acomplete()` now uses a daemon transport worker with event-loop polling. It records transport milestones and a separate HTTP timeout, while Runtime preserves cancellation, in-flight uncertainty, late completion and usage. Reviewer summary uses one deadline from assembly through validation, and a no-response fallback is marked technical rather than semantic. The old raw Runtime `SUCCESS` is preserved with a separate corrected status. Existing material permission, quote ledger, prompts and retrieval were not changed.

The successful new S1 batch demonstrates that the repaired path can finish on the same payload. It does not identify the historical remote cause. The initial new EPERM was a local sandbox network denial, not a provider timeout.

## Live batches and semantic limits

The S1 system/user/schema/model/options payload was byte-equivalent to the historical request, 36,095 bytes, with business date `2026-09-17`. Three network-approved repeats returned `reviewed/partially_novel`, no repair or retry. All ten feature relations repeated; cited IDs were the two original abstract Evidence items. Several `contradicted` reasons infer non-use from what abstracts omit, so relation repeatability is not semantic accuracy. The prior seven registered reads were present in the payload but not cited in final feature relations.

Both frozen holdouts completed card and summary. NP-1's four supported features align with its 1,367-character abstract; NP-2 gave one partial match and three unknowns from a 943-character abstract. Four synthetic controls covered equivalent wording, compatible coexistence, baseline attribution and a local difference with a secondary unknown. Their supplied quotes were short authored controls, with no Reader reads. Case details and limits are in `analysis/claim-evidence-comparison.md`.

## Budget, status and display

The user authorized one new cap of **3.00 RMB estimated reserve and 24 physical attempts**. This task recorded **18 attempts**: one local EPERM with unknown billing, three S1 responses, ten holdout responses and four synthetic responses. Reservation totals **1.542420 RMB**; usage-based charges for 17 responses estimate **0.345225 RMB**. Actual provider bill is unknown, and the EPERM reservation remains held. Historical S1 reserve of 0.126717 RMB is separate and did not carry over. Per-attempt hashes and accounting are in `analysis/live-budget-ledger.json` and `analysis/attempt-ledger.csv`. No extra requests are needed for this acceptance.

Stored-artifact API/Markdown contract and frontend source behavior distinguish program fallback from semantic insufficiency. Node/npm were unavailable, so frontend tests/build and browser replay did not run; no live display claim follows. Full-product stability needs its own end-to-end acceptance. Test commands and results are archived under `tests/`; no prompt or production semantic rule was tuned after observing holdouts.
