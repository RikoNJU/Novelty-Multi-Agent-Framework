# E2E-ACCEPT-20260918: preflight result

**What ran:** zero-business-call local integration preflight in WSL2, including FastAPI substitute tests, production build, 17 Playwright browser tests, in-process and connected-browser real-mode health checks, and a read-only archived Markdown display/download. **What did not run:** a new real PDF business task. This task document proposes, but does not grant, a new paid budget; the previous Reviewer-only cap has ended. No business run ID, fresh report, provider charge or live demonstration candidate exists yet.

| Acceptance layer | Current result | Evidence and limit |
|---|---|---|
| Local preflight | `passed_limited_scope` | 8/8 frontend component tests, TypeScript/build, 17/17 browser tests, 9/9 API + budget tests, 30/30 Runtime/usage/Reviewer regression tests. The browser used cached Chromium; a test-only Vite server and a real-mode backend serving frozen static files were each checked. The target demo computer and production proxy were not exercised. |
| One real execution | `not_run` | No new paid authorization or frozen live trial cap. Proposed mode A and candidate PDF are indexed; neither was submitted. |
| Retrieval/evidence transfer | `not_assessed` | There is no current real run trace. Existing historical Reviewer concerns remain open. |
| Actual page display | `passed_limited_scope` for intercepted browser behavior and archived Markdown; `not_run` for current backend | Historical source/download SHA matched. Stage business content is not exposed by the page's `/api/novelty` API. |
| This run's semantic quality | `not_assessed` | No new conclusions. |
| Overall repeatability | `not_established_by_single_run` | Even a future single completion would not prove it. |

## Integration findings

A real-mode backend served the frozen frontend on `127.0.0.1:8010`; the browser loaded the page and health endpoint with zero POSTs and no script error, then the server was stopped. This is a connected read-only preflight, not a business run. The current React page uses `/api/novelty/runs/files` (`paper` field, 30 MiB). The repository also mounts `/api/runs` with a different 25 MiB PDF contract and restart behavior; `docs/frontend/deployment.md` refers to that other stack. `preflight/interface-map.md` records the exact mapping. The page has six progress stages and an authoritative Markdown report path, but no stage-detail endpoint for its task IDs.

Minimal fixes before any paid run added same-intent upload deduplication, rejection of extra PDF parts, a run-scoped pre-dispatch model budget option, actual progress on supplement loops, and correct distinction between semantic evidence insufficiency and execution failure in structured fallback. A lost POST response now blocks another click on the same page. These changes were tested with local substitutes and no real model/search/parser requests. The model budget does not yet account for possible external MinerU billing; this must be resolved before mode A is launched.

## Candidate and decision

Mode A is proposed with `examples/MG19333vrw.pdf` (74 pages, 2,023,977 bytes, SHA-256 `82580951dfddb8e0fd815f8f3c573828a8ca8ff0dfee63219cb7606116a0b04c`). It is already in the repository and has an old trace for identity comparison; the selection does not depend on a desired verdict. Previous full-workflow archive reports 57 model calls and a usage-based 1.3417986 RMB estimate for a different version, which is context rather than a new-run price guarantee. The local frozen DeepSeek-V4-Flash rate table matches the [official SiliconFlow time-of-day pricing](https://docs.siliconflow.cn/docs/release-notes/overview) checked during this preflight, though usage estimates can differ from bills. The task's suggested 3.00 RMB cap remains unapproved, and no parser fee has been assumed zero. The production sources configured for this preflight are arXiv as active and Springer enabled, with `null_catalog` present but not selected.

At present the archived report can demonstrate the **display mechanism as historical replay**. It cannot be used as proof of a new live end-to-end run or as a certified novelty conclusion. After an explicit new budget and parser-cost decision, the next action is to freeze the trial commit/config/cache, perform exactly one PDF submit through the connected page, and fill the current empty run and claim-source ledgers from that run. Until then E14–E19 remain unrun.
