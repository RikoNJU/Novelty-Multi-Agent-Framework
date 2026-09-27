# 3.12 取消及响应解析失败的 usage 闭环

本项修复两个已在复核中发现的漏账路径。先新增确定性 HTTP/事件注入回归，在修改前得到 **6 failed / 1 passed**，见 [usage_before.log](usage_before.log)。修复后新增与相邻测试 **80 passed**，见 [usage_after.log](usage_after.log) 和 [usage_tests.xml](usage_tests.xml)。没有发起真实模型、Provider 或网络请求，没有改写历史运行产物。

## 已复现的问题

1. 传输在取消后完成，usage 只进入 `late_completion`；传输先完成再取消，usage 只留在 `transport_completion_before_cancel`。顶层 tokens/billing 被空取消事件清零或未更新，汇总只看顶层。`finish_run()` 后的单调用文件虽更新，summary 和其归档未同步对账。
2. HTTP 成功返回可解析 JSON 且含 usage，但 choices 缺失、content 类型错误或 tool arguments 非法时，客户端在构造 `ModelResponse` 前抛错。原 `RESPONSE_PARSED` 只记一个 usage_available 布尔值，因此实际返回的消耗丢失。

## 最小实现

修改 `backend/env/model_client.py` 与 `core/runtime_artifacts.py`，新增 `tests/test_usage_accounting_closure.py`。未修改 Evidence、Reviewer、Context admission 或实验输入。

`ModelCallEvent` 增加独立可选 `provider_usage`。客户端在收到并解析 HTTP JSON 后、校验 choices/content/tool_calls 之前，随原 `RESPONSE_PARSED` 事件保存 Provider usage。非 Mapping 或缺失 usage 仍视为不可用；应用输出解析标准和原错误保持不变。

Runtime 以既有 `client_call_id` 为账务身份，在同一个调用记录保存已观察的规范 usage/tokens/billing。取消或失败事件没有新 usage 时保留已有值；收到晚到 usage 时更新同一行，不新增调用、不累加两次。定价使用原调用起始时间，避免跨峰谷时段的晚到响应改变计价时段。

执行状态与消耗分别处理：取消后的调用仍是 `CANCELLED`，解析失败仍是 `FAILED`；旁路的 late_completion / transport_completion_before_cancel 继续解释事件顺序。真实已知 token 可以计入失败或取消请求，不表示任务成功。

`finish_run()` 后若消费汇总改变，在原互斥锁内重新计算账务，并原子更新运行目录及归档目录的 `summary.json` / `summary.md`。只更新 `llm_usage` 和 `llm_usage_reconciled_at`，不改变原 run 状态、结束时刻、耗时、outcome 或诊断结果。单调用文件仍同步两处。

## 验证边界

| 场景 | 断言 |
| --- | --- |
| cancel→complete、complete→cancel，包含重复终态事件 | 同一调用只计一次；CANCELLED 保留；1000 input + 500 output = 1500 total，cached=200、reasoning=100 |
| 固定已知价格与原请求时间 | 单次估价 0.00348 RMB；取消/重复事件不改变或翻倍 |
| finish_run 后收到晚到响应 | 本地与归档 call/summary 一致；run 状态、结束时间与耗时不变 |
| 真实异步 HTTP 替身，取消后正常响应或无效 choices | 两种都保留实际 usage；late_completion 分别是 SUCCESS / FAILED，调用仍 CANCELLED |
| HTTP 已完成且记录成功，coroutine 随后取消 | 通过控制 observer 的同步点确定事件顺序；消耗保留一次 |
| choices 缺失、非法 content、非法 tool arguments | 仍抛原 ModelClientError；保存 Provider usage/request ID；失败请求费用入汇总 |
| 解析失败后另一次修复请求 | 两个独立 call ID，各自记录并合计；不把修复请求折叠为前一次 |
| Provider 从未返回 usage，或晚到成功也不含 usage | `available=false`、`USAGE_UNAVAILABLE`、总费用 null、PARTIAL，不能推断免费 |

回归命令：

```bash
/home/lya3106643285/miniconda3/envs/Novelty-web/bin/python -m pytest \
  tests/test_usage_accounting_closure.py tests/test_llm_usage_tracking.py \
  tests/test_runtime_artifacts.py tests/test_context_admission.py \
  tests/test_model_tool_calling.py tests/test_web_model_budget.py \
  -o addopts='' -q \
  --junitxml=docs/experiments/20260927_harness_config_closure/usage_tests.xml
```

80 项通过，`git diff --check` 通过。此次关闭的是上述两类可复现的账务缺口，不把测试数量当作所有计费场景的证明。

仍须保留的成本边界：断网、截断/不可解析响应、进程被强制终止或 Provider 根本未报告 usage 时，实际消耗依旧 Unknown；此补丁不猜测服务端收费，不查询真实账单，也不采集 GPU/电力/租赁成本。历史取消记录没有自动重算；既有 242 调用对账仍只证明其已保存 provider_usage 与汇总一致。新汇总在迟到数据落盘前可能短暂未对齐；同一运行内使用锁和原子替换保证更新后精确一次，不能把多个 JSON 文件的更新视为跨文件数据库事务。
