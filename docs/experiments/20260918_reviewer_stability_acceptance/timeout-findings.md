# S1 timeout facts and limits

Source: prior S1 `llm_calls/0001_deepseek-flash.json`, Reviewer events, and the frozen request indexed in `fixtures/input-index.json`. This file does not alter the prior run.

| Boundary | Observed fact |
|---|---|
| Last confirmed pre-transport boundary | Reviewer recorded `summary_request_dispatched` and the model client recorded `START`; actual request payload with full system/user text is archived. The old event name means client entry, not proof of remote receipt. |
| Next absent boundary | No response headers, body, parsed response, provider request ID, or usage were recorded. The old client had no intermediate transport milestone instrumentation. |
| Timing | Model call started at 2026-09-17 18:13:50.606569 UTC; trace status `CANCELLED` after 180,091 ms. Outer summary deadline was 180 seconds and old inner request timeout option was also 180 seconds. |
| Request | 36,095 serialized request bytes recorded by the budget wrapper; model `deepseek-ai/DeepSeek-V4-Flash`, temperature 0, max output 2,048 tokens, non-streaming, tool choice `none`, thinking disabled. |
| Process and transport | The async client used `asyncio.to_thread()` around synchronous `urllib.request.urlopen()` and full `response.read()`. No thread or socket completion state from the historical call was captured after cancellation. |
| Business result | Program fallback `insufficient_evidence` with `incomplete_reason=budget_exhausted`; no model Draft. Raw Runtime summary said `SUCCESS`, corrected sidecar says timeout and no semantic completion. |
| Cost | 0.126717 RMB was a budget reservation estimate; actual provider charge is unknown because usage is absent. |

A local minimal thread experiment in this execution environment returned from its worker but did not wake an `asyncio.to_thread()` waiter before an external timeout; its source and output are in `tests/thread_wakeup_probe.py` and `tests/thread-wakeup-probe.log`. This demonstrates a possible local waiting failure. It does **not** prove that the historical provider returned a response: network transfer, remote queueing, and generation time remain unobserved. The new client uses a bounded async polling loop over a daemon transport thread, and tests verify that a late worker result is recorded without reviving an already cancelled business result.

The recorder now distinguishes transport invocation, response headers, body completion, response parse, and late completion. It cannot split DNS, TLS, remote queueing, and generation. A cancelled thread with no late event remains `transport_inflight_unknown`; cancellation alone does not establish a zero charge.
