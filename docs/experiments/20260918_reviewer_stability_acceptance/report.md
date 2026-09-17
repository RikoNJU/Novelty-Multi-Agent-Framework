# RV-STABLE-20260918: offline acceptance result

## Four independent conclusions

| Layer | Status | Evidence and limit |
|---|---|---|
| Deterministic mechanism | `passed_limited_scope` | Production client and Reviewer boundary tests exercise local response, cancellation, late completion, deadline expiry, and status projection. No provider behavior is inferred. |
| Fixed S1 summary repetition | `not_tested` | `S-repeat-1/2/3` registered in `acceptance-status.json`, all unrun because this task has no new paid authorization. The historical S1 timed out and is not silently included as a success. |
| Semantic and transfer performance | `not_tested` | Two previously frozen source Works and four synthetic conditions indexed; no new model decisions or semantic accuracy estimate. |
| Live full-product stability | `not_tested` | No new complete workflow, upload or live frontend run was authorized. |

The historical timeout reached the model client and was cancelled after 180.091 seconds without a captured response header, body, response ID or usage. The new local reproducer shows a possible `asyncio.to_thread()` wakeup problem in this environment; the historical remote cause remains unknown. Details and excluded claims are in `timeout-findings.md`.

The implementation keeps the prior evidence transmission repair and quote ledger. It changes transport observation, cancellation/late-result handling, deadline checks and structured-report status display. The old raw Runtime `SUCCESS` is preserved as an artifact, with the timeout correction in `analysis/status-consistency.json`; it is never counted as a completed Reviewer judgment. Prior fee reservation 0.126717 RMB is not a bill. This task made no external model request.

The generated Markdown renderer and report binding already distinguish a program fallback from semantic insufficiency. The API `RunSnapshot.result` carries the structured report without dropping `incomplete_reason`; the frontend structured fallback now displays this reason. This is a stored-artifact contract replay, not a launched browser or live upload. JavaScript runtime checks remain contingent on a Node executable in the environment.

A future live acceptance batch requires a new unified budget and the exact frozen model payload, fixed business date, three pre-registered S1 runs, and the two frozen holdout cases. Any repeated unexplained timeout stops the affected unit. Even three completions would support only limited node-level repeatability, not whole-system reliability.
