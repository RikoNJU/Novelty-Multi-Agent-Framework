# RV-GROUND-20260918 report

## Authorized S1 summary attempt

After the offline implementation was committed, the user authorized one S1 summary with at most two model calls including format repair, at most 2,048 output tokens per call, and an estimated 0.40 RMB total cap. The frozen L1 card reviews were reused; there was no new Reader, retrieval, or full-workflow call. The provider was SiliconFlow `deepseek-ai/DeepSeek-V4-Flash`, temperature 0, with a 180-second summary deadline. The source hashes and budget are in `trials/s1_summary_live/preflight.json`.

One request was dispatched. The actual user message hash was `ce29e2ae9facad0e04f71210eebe458032f94a96ef6ef876ad388ac504ee37d4`, identical to the offline S1 payload hash. It contained nine nonempty quotes, including all seven registered read quotes. This establishes actual client-boundary transmission of the prepared text. The request was cancelled after 180,091 ms without a model response, so there is **no new semantic result** and no format-repair call. The returned `insufficient_evidence` object has `incomplete_reason=budget_exhausted`; it is a timeout fallback, not a model judgment. The raw Runtime summary marked the run `SUCCESS` because the script treated a returned fallback as successful; `trial-status.json` records the correction. The script has since been fixed for future runs. No further paid request was made.

One call was reserved at 0.126717 RMB under the byte and token estimate. The actual provider charge is unknown because no usage response arrived; the 0.40 RMB cap was not reset or reused. See `trials/s1_summary_live/budget-ledger.json` and the raw `llm_calls/0001_deepseek-flash.json`.

| Set | Observation | Interpretation |
|---|---|---|
| regression_known | Historical S0 actual L1 summary input contains two quotes. S1 actual dispatched request contains those two plus seven registered read quotes, with the same hash as offline assembly. | Input transmission is verified. S1 timed out before response, so there is no paired model outcome comparison. |
| synthetic_controls | Scripted client captures a selected read in its actual `user` message even without a feature citation. Dropping it from the serialized payload fails verification. A budget-exhausted quote is marked omitted and excluded from citable IDs. Synchronized ID remapping preserves reachability. | Tests deterministic plumbing and reference scope. Scripted responses cannot establish model semantics. |
| transfer_holdout | Two distinct source Works and their local source files are frozen. No new model decision. | `generalization_not_yet_tested`. |

No label direction or semantic accuracy rate is inferred. The seven selected reads include material whose technical role must be assessed from the source context; registration, display, and support are separate facts. The original L1 card and summary judgments are preserved in the earlier trial archive. This round adds no J or H paid comparison and no new claim that the final verdict is correct.

The historical feature-by-feature reasons, relation and basis fields, cited IDs, and quotes actually sent to S0 are juxtaposed in `claim-evidence-review.md`. Several old reasons infer non-use from limited descriptions; that is a diagnostic concern, not an independently established contradiction. The new prompts have not yet produced model decisions, so any semantic effect or degradation remains unknown.

Remaining work requiring a new experiment budget: run S1 summary on frozen input, then if approved run controlled J0/J1 and holdout H cases, saving actual requests, raw replies, parsed Drafts, semantic claim and source comparisons, cost, and failures. The previous budget was exhausted or closed and is not carried forward.
