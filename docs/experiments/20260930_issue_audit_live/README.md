# 2026-09-30 核查补测：本地 Qwen + 真实外部检索

用户明确授权测试、本地小模型、外部检索，并再次确认 arXiv / Springer 目的地、论文派生查询与现有 Springer 凭据。审查源码提交为 `2bd79ff672658605b3962d6833e121506751b7b9`；该提交相对上一核查基线仅增加问题文档。本实验没有修改生产源码、默认配置、历史任务包或既有实验；所有新增配置和产物位于本目录。本次补测产物按阶段和种类提交到本地 main，未推送远端。

## 结果

| 范围 | 实际结果 | 原始证据 |
| --- | --- | --- |
| 完整离线测试 | `Novelty-web`：1267 passed，1 failed，6 deselected，33.18 s | [日志](offline-web-tests.log)、[JUnit](offline-web-tests.xml) |
| 初始环境 | `Novelty` 缺少 python-multipart，3 个收集错误；未据此判产品回归 | [初始日志](offline-tests.log) |
| 两轮完整真实工作流 | 486.94 s，46 次本地模型调用，3 个点、3 张通过结构校验的卡；3 点均无法裁定 | [运行身份](runs/0001/run.json)、[结构化结果](runs/0001/result.json)、[分析](workflow-analysis.json) |
| 真实检索 | arXiv API/Web 均成功；网页全文 43,348 字符；Springer 普通检索成功，OA 限定查询 403，带前缀 DOI 的 OA 请求 404 | [独立 HTTP 计数](provider-results.json)、[OA 检索](springer-oa-results.json)、[DOI 对照](springer-identifier-results.json) |
| 确定性边界反例 | 8 组：预算 debug、恢复、汇总原因、Reader 重用、namespace、收尾、配置注入、Web usage/价格 | [结果](boundary-results.json)、[脚本](reproduce_boundaries.py) |
| 真实模型上下文与预算 | 400 归 transport；严格准入归 context_limit，但仍耗次数；debug=false 时 cap=1 仍成功调用两次 | [结果](local-context-results.json)、[脚本](probe_local_context.py) |
| 真实 Reviewer 对照 | 修正溯源夹具后的 3 类 × 2 次：4 次非法 read_id 技术失败，2 次无关特征被判 contradicted；预声明关系判断 0/6 符合 | [预声明](semantic-controls-v2/plan.json)、[结果](semantic-controls-v2/results.json)、[脚本](reviewer_live_controls_v2.py) |
| wheel | 临时目录构建成功；仓库外 CLI/config 导入均 `No module named 'backend'`，agent JSON 未进入 wheel | [结果](packaging-results.json)、[脚本](probe_packaging.py) |
| 冻结输入重渲染 | 仅第 9 行生成时间变化，字节 hash 不同 | [分析](workflow-analysis.json)、[新报告](rerendered-report.md) |

唯一离线测试失败：`tests/test_runtime_config_injection.py:69` 假设 arXiv 检索器具有 API 私有字段 `_min_interval`，实际默认是 `ArxivWebSearchTool`。定向 API/Web 双配置测试证实各自 interval/timeout/retry 参数生效；这是过时测试假设，不是已证实的注入失效。

## 真实运行的关键发现

1. **运行 SUCCESS 不等于查新完成。** NP-1 没有卡；NP-2 两卡但比较关系不可靠；NP-3 一卡但 Reviewer 非法 read_id 导致 technical_error。NP-3 的点级 execution_issues 被汇总短路丢失，最终恢复列表没有 NP-3。
2. **卡片正文会误归属。** EvoFormer 的卡 `card_8ba33651c1b41b8432c27c59` 将目标论文的 Sketch-DBH 贡献写为该文献的主要贡献，绑定引文实际介绍 EvoFormer。Gate A/B 均通过，报告仍展示该错误卡片。不能把结构合法称作语义已核验。
3. **不提及不等于矛盾。** NP-2 的四条关系理由均以 does not mention / different problem 等表述解释 contradicted；同类错误在固定公开材料对照中两次出现。完整性门控挡住不满足要求的 not_novel，不能修复关系语义。
4. **抽取已看见的信息仍会遗漏。** trace.digest 中包含图自编码/重构误差、DSGNN 注意力与梯度同步，生成候选和最终点集未保留相应机制；这些具体漏项不能只归于 2,000 字符截断。此次保守去重拒绝了删除 DSGNN 的提议，应区分有效防护和残余遗漏。
5. **资源统计存在两种不一致。** arXiv 全文独立观测到 1 HTTP/2 预留；完整工作流 30 次预留分为 arxiv_web=21、authenticated_database=6、arxiv_auxiliary=3，但物理事件摘要只有 arXiv=21。Springer 没有同等物理事件，不能直接把摘要当全部 Provider 总量。
6. **冷 Springer 实例不识别裸 DOI。** `fetch('10.…')` 零请求直接返回 None，`fetch('doi:10.…')` 才请求 OA 端点。后者这次返回 404，不证明该全文存在；只证明标识符处理不一致。检索结果 document_id 正是裸 DOI，而元数据缓存仅在实例内。

## 用量与可复现边界

本地服务 `/version` 返回 `0.8.5.post1`，模型 `qwen2.5-7b-instruct`，`max_model_len=32768`；详见 [环境检查](environment.json)。测试环境为已有 `Novelty-web`，Python 3.11.16，具体依赖和有效配置在 [启动清单](runs/0001/experiment-manifest.json)。没有冻结远端权重或 chat-template 文件，不能声称服务部署完全可重建。

[模型对账](usage-summary.json)：**67 次实际 chat 派发，66 个成功响应、1 个服务端 HTTP 400**；另有 1 次本地上下文准入拒绝，没有 chat 派发。已观测 input=381,256、output=17,223、total=398,479 token。400 没有 usage，准入测量请求另计，本地 GPU 成本未计价；没有云模型推理调用。关闭 debug 的两次成功响应直接保存并单列，archive 副本不重复加总。

完整工作流记录 **21 个 arXiv 物理请求事件，另有 6 次 Springer 预算预留和对应成功检索**；Springer 缺少逐次物理事件，不能伪称独立计量完备。独立 Provider 探针另记录 API/Web/全文/Springer 普通检索共 4 次 HTTP、OA 检索 1 次、带前缀 DOI 1 次。预留次数和真实 HTTP 次数分别保存。

完整链路固定论文 SHA256 `89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66`，复用经过当前 references digest 校验的 91 条参考文献缓存。动态 arXiv/Springer 网络结果没有冻结为可重演服务器；不同查询和时刻不能直接比较召回率。全链路只跑一份论文一次，两个配置不同的语义批次不合并成模型准确率；修正批次 0/6 仅描述这组六个预声明对照，不代表总体模型能力。

## 实验自身失败记录

- 离线套件另在默认 archive_root 产生一份 Demo 运行归档；已完整移动到 `offline-test-runtime/`，没有修改其中记录的历史路径，见 `offline-archive-relocation.json`。
- 初始 `Novelty` 测试收集失败保留；切换现成完整环境，没有安装依赖或改环境。
- 边界脚本最初汇总夹具未注入 ModelClient，构造即失败；[原结果](boundary-results-initial.json)保留，修正夹具后仅重跑该项，模型没有调用。
- 首个 Provider 批次所有案例完成后，实验脚本误用非法终态 `COMPLETED_WITH_CASE_RESULTS`，收尾失败；[日志](provider-probes.log)和原 manager RUNNING 状态保留，案例 HTTP 计数仍有效。脚本已改为合法 SUCCESS 供后续复现，未为修饰终态重发请求。
- Reviewer 第一次构建夹具 SourceKind 写错，尚未推理即退出；[日志](reviewer-controls-setup-failed.log)和 setup-failed 目录保留。
- 初始六例缺少 checkpoint 要求的原始 Reader range/locator，导致 checkpoint_unavailable；其 10 次调用计入用量，但不作为有效 checkpoint 验收。v2 使用真实 store 读取、精确 quote 区间，并在每例推理前调用 `_source_snapshot` 通过验证；六例 checkpoint 均可建立，保留其实际失败/完成状态。v2 同时换用中性编号，并将无关特征换为材料没有涉及的蛋白质定位任务；两个批次不是单因素性能对照。
- Springer 第一批沿用默认 `full_text_mode=disabled`，两次 no_material/0 请求不说明 OA 服务不可用；后续显式 openaccess 的探针已独立记录。

## 复现与文件索引

在仓库根目录使用 `/home/lya3106643285/miniconda3/envs/Novelty-web/bin/python`，`PYTHONPATH=backend/src:.`。本地无鉴权服务测试使用临时环境变量 `LOCAL_VLLM_API_KEY=local`，没有写入默认配置或 .env。

离线入口：`python -m pytest -m 'not live' -p no:cacheprovider`。live 标记的旧用例未整组执行，其中包含云模型入口；这里以受控本地模型实验覆盖实际链路，不把 6 deselected 写成通过。

完整链路入口：`scripts/run_full_workflow_live.py --paper-json outputs/MF2033k6lC/paper-input/others/paper.json --profile docs/experiments/20260930_issue_audit_live/live-profile.json --runs-root <新的隔离目录> --isolated-config`。模型上限 100，Provider 预留上限 36，max_rounds=2，concurrency=1；开启 Reader 复用、checkpoint、状态投影和精确 context admission，禁用 null_catalog，数据库启用 arXiv/Springer。复现必须使用新目录；现有编号目录拒绝覆盖。

其他入口为本目录 `reproduce_boundaries.py`、`probe_local_context.py`、`probe_providers.py`、`probe_springer_oa.py`、`probe_springer_identifier.py`、`reviewer_live_controls_v2.py`、`probe_packaging.py`。其中固定命名的探针也需调整为新目录，避免复写原始证据。`analyze_workflow.py` 和 `summarize_usage.py` 仅分析本轮文件，前者另生成新报告副本。

未覆盖：无凭据的 Elsevier/IEEE；默认禁用的浏览器/Baidu；云模型四格消融；多论文统计评估；论文方案算法复现；GPU/服务端账单；多进程并发发布混写实验。不能宣称“所有问题已找全”。本轮已覆盖现有核心离线套件、真实本地五角色、实时外部数据库、全文/Reader、两轮恢复、报告和关键边界。

逐任务问题、原因和源码位置见 [docs/issues 索引](../../issues/08_证据索引与边界.md)。
