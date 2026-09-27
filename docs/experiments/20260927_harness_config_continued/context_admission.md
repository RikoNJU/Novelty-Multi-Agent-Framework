# 调用级 Context admission：实现与验证（2026-09-27）

已实现可选的输入 token + 输出预留窗口检查，放在 `OpenAICompatibleChatClient.complete` 的真实模型传输之前。默认 `off` 兼容既有运行；本地 guarded profile 显式启用 `enforce`。检查不会删除、截断、摘要或重排 Evidence/Reader 原文。

检查点使用最终合并调用参数后的 JSON 快照：同一快照用于记录、计数和 chat HTTP 请求。`acomplete` 经同一边界，Harness 的主循环、格式修复、最终输出调用均由该客户端覆盖。没有发现生产代码直接调用私有 `_complete` 绕过检查。可插入 Python `token_counter`，其契约是针对完整模板和工具 schema 返回精确计数；字符数估算、缺失输出预留、计数格式错误都不能标记为精确。

配置字段及默认值：

| 字段 | 默认 | 行为 |
| --- | --- | --- |
| `mode` | `off` | `off` 不测量；`observe` 记录而放行；`enforce` 拒绝确认超限 |
| `counter` | `none` | `vllm` 使用同一模型服务的 `/openapi.json` 和 `/tokenize`；也可代码注入精确计数器 |
| `on_unavailable` | `reject` | `enforce` 下无法可靠测量时默认拒绝；显式 `allow` 可恢复放行，记录 `measurement_unavailable` |
| `timeout_seconds` | `5.0` | 单次测量 HTTP 超时，不等同于整个 chat 调用的总截止时间 |
| `tokenize_path` | `/tokenize` | 只接受同源绝对路径，不能写外部 URL/query/fragment |
| `vllm_tools_mode` | `native` | `native` 要求服务 schema 原生支持模板字段；`v0_8_5_kwargs` 是下面说明的显式兼容路线 |

输出预留使用最终请求的 `max_completion_tokens`，否则使用 `max_tokens`；不接受未设置、非整数或非正数的预留。有效窗口取 `min(profile.context_window, tokenize.max_model_len)`，总量恰好等于窗口可放行，超过窗口返回 `CONTEXT_LIMIT_EXCEEDED`。服务端窗口小于静态 profile 时，静态配置不能把上限扩大。CLI preflight 的静态检查不能代替逐次请求的模板计数；运行时使用同一 profile 配置，并读取本次服务计数响应中的窗口。

每次测量保存配置模式、输入计数、输出预留、profile/server/effective 窗口、请求快照摘要及结论。`CONTEXT_MEASUREMENT_UNAVAILABLE` 与确认的 `CONTEXT_LIMIT_EXCEEDED` 分开。多模态内容、不能验证的 tool choice、未知 prompt 参数、模板默认值失配、计数与 token IDs 数量不一致都拒绝声称精确。诊断 endpoint 不含 URL userinfo/query/fragment；计数入口直接拒绝带这些组件的模型 URL，API key 不进入新增 metadata。

## 本地 vLLM 0.8.5 的工具模板差异

[服务协议探测记录](context_service_protocol_probe.json) 确认本地版本为 `0.8.5.post1`，模型 `qwen2.5-7b-instruct`，服务窗口 32768；该版本 `TokenizeChatRequest` 没有顶层 `tools` 字段。因此不能简单把 chat payload 贴到 `/tokenize` 后把结果标为精确。默认 `native` 在含工具的该服务上会记录 `tokenizer_missing_template_fields`，不会静默漏算工具。

官方 [v0.8.5 tokenization 实现](https://raw.githubusercontent.com/vllm-project/vllm/v0.8.5/vllm/entrypoints/openai/serving_tokenization.py) 将 `chat_template_kwargs` 送入 chat 预处理；[相同版本的 serving_engine](https://raw.githubusercontent.com/vllm-project/vllm/v0.8.5/vllm/entrypoints/openai/serving_engine.py) 先设置 tools，再应用这些 kwargs。显式兼容模式据此把工具传到 `chat_template_kwargs.tools`，保留调用者原 kwargs 的优先级，并核对 `/version` 仅接受 `0.8.5` 或 `0.8.5.post1`。新版本的 [官方 tokenizer 协议](https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/entrypoints/serve/tokenize/protocol.py) 已包含 tools，但本实现依然核对实际服务 schema，不用最新文档代替运行版本。

兼容路线仅在当前本地 Qwen 模板上做了实测，不能推广为所有模型/模板/工具解析器的证明。部署时应把显式选择此模式视为已验证该服务模板的声明；切换服务或模板后需重新验证。每次成功推理还对比 tokenizer 输入数与 provider `prompt_tokens`/`input_tokens`。失配会保存 `context_measurement_verification=mismatched`，使同一个 client 的后续测量返回 `prior_measurement_usage_mismatch`；`enforce+reject` 随后停止发送 chat。没有 usage 时只记录 `usage_unavailable`，不伪造匹配。失配发生的首个请求无法事后撤回，已经同时发出的并发请求也无法靠这个标记撤回。

## 固定请求与真实调用证据

[compare_vllm_tokenization.py](compare_vllm_tokenization.py) 使用已完成 Reader AB 的全部 16 个真实 request payload 和已记录的 provider usage，再调用 `/tokenize`，没有产生新推理。旧/新 Reader 状态的所有回合均精确匹配，包含工具往返及最终无工具请求，结果见 [vllm_tokenization_comparison.json](vllm_tokenization_comparison.json)：16 次 tokenize、0 次 generation、16/16 匹配。这验证当前模板下的兼容传参；不是 Reader 证据产出率实验。

[probe_context_admission_local.py](probe_context_admission_local.py) 随后通过生产客户端做了两个有界探针；[完整结果](context_guard_local/outcome.json) 和 runtime 记录均保留。

| 探针 | 输入 token | 输出预留 | profile/server/有效窗口 | 结果 | chat HTTP |
| --- | ---: | ---: | --- | --- | ---: |
| 原样重建归档 Reader 请求 | 5749 | 2048 | 100 / 32768 / 100 | `CONTEXT_LIMIT_EXCEEDED`，推理前拒绝 | 0 |
| 同一真实 Reader schema + 短控制指令 | 580 | 32 | 40000 / 32768 / 32768 | 放行，返回 `OK`；provider input=580，output=2 | 1 |

每个探针另有 schema/version/tokenize 各 1 次，合计 6 次测量相关 HTTP，只有 2 次实际 tokenize。工具没有执行，检索请求为 0。短指令是接口控制样本，不是研究质量样本。拒绝探针刻意缩小 profile 窗口以验证真实请求的传输边界，并未声称原 Reader 请求在正常 32768 窗口下超限。

Runtime `calls` 保留逻辑调用尝试数，用于运行预算；新增 `chat_transport_calls`、`context_measurement_requests`、`context_pre_dispatch_rejections` 分别统计推理传输、计数/协议 HTTP、预拒绝。`provider_usage` 只存生成服务返回的 usage，不能把 tokenizer 数量算作已收费输入；测量请求成本不在现有模型价格表中。失败或本地未定价时仍保留 Unknown/UNPRICED，不能把预拒绝的空 usage 当作节省的人民币金额。

## 离线覆盖及边界

定向回归覆盖默认关闭兼容、同步/异步统一检查、调用参数覆盖、输入快照不变、观察模式、测量缺失策略、较小服务窗口、旧版工具协议、版本拒绝、模板优先级、失配后的停止、诊断脱敏，以及测量期间取消后不会再启动 chat。取消不能强制停止已经发出的 tokenizer HTTP，但会阻止后续推理传输。

历史 HTTP 400 的两组已报告计数作为离线算术 fixture：`57360 + 4096 > 32768`（`run-33cb3cd33cca4fb28f4a2bd454c2179a/0018`）和 `4193 + 4096 > 8192`（`single-T-2-20260924T203054Z-de022d8d/0001`），均在 fake transport 调用前拒绝。这里复核的是历史服务报告的输入计数及窗口边界，没有把离线替身说成重跑了这两份长 prompt 的真实 tokenizer。

运行命令：

```bash
/home/lya3106643285/miniconda3/envs/Novelty-web/bin/python -m pytest \
  tests/test_context_admission.py tests/test_model_tool_calling.py \
  tests/test_model_env.py tests/test_model_profile.py tests/test_llm_usage_tracking.py \
  tests/test_runtime_artifacts.py tests/test_web_model_budget.py \
  --junitxml=docs/experiments/20260927_harness_config_continued/context-admission-tests.xml -q
```

79 项定向测试通过，见 [JUnit 记录](context-admission-tests.xml)。`git diff --check` 通过。此项没有重写 Evidence 语义，也没有使 0-card 的研究结果变成成功；它解决的是可测量的单次调用窗口准入。

尚有明确边界：纯本地 injected counter 的精确性由实现者保证；tokenize 与 chat 必须服务于同一模型和模板，前置代理改写或异构副本会破坏这个前提；版本/schema 每次核对减少陈旧缓存，但不能消除测量与生成之间的服务切换竞态。缺少可靠计数时，默认 enforce 策略拒绝，而不是退回字符估算。全流程默认 profile 仍关闭此功能，guarded profile 是显式实验配置。
