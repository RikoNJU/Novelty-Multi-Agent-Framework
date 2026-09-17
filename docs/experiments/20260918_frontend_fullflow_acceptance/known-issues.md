# Known issues and limits

1. The previous Reviewer acceptance still contains possible absence-to-contradiction overclaims on the S1 graph partitioning case. This integration patch does not alter those model judgments or declare them correct.
2. The page's `/api/novelty` task store is in memory; a backend restart invalidates its task IDs. The separate `/api/runs` persistent stack is not the current page contract.
3. The page shows aggregate progress and report but has no `/api/novelty` stage-artifact detail endpoint. No stage business content was verified in the product page. The separate `/api/runs/.../artifacts` endpoint cannot be assumed compatible.
4. The historical browser replay used an explicit test route intercept. The connected browser + real backend run, normal PDF parsing, retrieval, Reviewer and final report were not exercised.
5. The optional Web model budget covers requests through the shared model client. MinerU's local subprocess and any external parser pricing have not been established; model usage estimates are not invoices. A live trial requires an explicit new budget and parser-cost decision.
6. On ambiguous POST failure, the current page blocks another submit until navigation; it cannot recover the task ID after a lost first response. The backend idempotency key prevents duplicate execution only when the same ID is reused during the same service lifetime.
7. The candidate demo computer, production same-origin proxy, backend restart behavior under a paid run, and live browser download were not tested. Cached Chromium plus temporary shared libraries enabled local test-browser preflight only.
