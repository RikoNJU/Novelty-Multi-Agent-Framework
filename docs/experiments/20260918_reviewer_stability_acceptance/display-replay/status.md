# Saved-artifact status replay

Input: the committed historical `trials/s1_summary_live/summary-review.json`. It has `status=insufficient_evidence` and `incomplete_reason=budget_exhausted`, with no model Draft. The old Runtime `summary.json` has run status `SUCCESS`, which describes a script-level completion mistake and is not authoritative for business adjudication.

The existing backend report binding copies `incomplete_reason` into each conclusion and uses an unfinished summary. The Markdown renderer labels that reason as `核验未完成，无法裁定`; backend tests pass. The API `RunSnapshot.result` is a dictionary and retains this field. The structured frontend now parses and displays `incomplete_reason`, showing `核验超时或预算耗尽，尚未完成` for this case. The browser/Node test is written but not executed in this environment, so no full page-level pass is claimed. This replay makes no model or retrieval call.
