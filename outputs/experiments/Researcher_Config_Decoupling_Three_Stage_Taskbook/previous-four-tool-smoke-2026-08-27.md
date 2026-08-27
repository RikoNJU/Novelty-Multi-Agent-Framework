# Researcher 四工具真实能力实验报告（2026-08-27）

## 1. 实验目的

验证单个 `TaskResearcherWorkflow` 在真实模型环境中能否连通以下正式业务工具：

```text
database_search
web_search
browser
reader
```

本实验使用实验性 system instruction 要求模型依次覆盖四类能力。因此它只用于验证能力连通性，不用于评价 Researcher 的自主检索策略质量。

## 2. 执行信息

- 执行日期：2026-08-27（Asia/Shanghai）
- 实验入口：`novelty_agent_framework.experiments.researcher_four_tool_smoke`
- 执行参数：`--require-all`
- Researcher 模型：`deepseek-flash`
- SearchPlanner 模型：`r1-qwen3-8b`
- Harness 最大工具调用数：10
- 实际耗时：234.921 秒
- 实验进程：正常退出并输出结构化 JSON

执行命令：

```bash
conda run -n Novelty python \
  -m novelty_agent_framework.experiments.researcher_four_tool_smoke \
  --require-all
```

## 3. 工具注册与实际序列

模型可见的正式工具为：

```text
database_search
web_search
browser
reader
```

未注册 `structured_source_retrieval`、arXiv 内部工具或 Skill 工具。

本次实际调用序列：

```text
database_search
→ web_search
→ browser
→ browser
→ browser
→ browser
→ browser
→ browser
→ browser
→ browser
→ tool-call budget exhausted
```

| 工具 | 调用次数 |
| --- | ---: |
| database_search | 1 |
| web_search | 1 |
| browser | 8 |
| reader | 0 |

模型调用了 DatabaseSearch、WebSearch 和 Browser，但没有进入 Reader，因此本次没有完成四工具全链路。

## 4. 模型调用与 Token

### 4.1 Researcher

- 调用次数：11
- Prompt tokens：65,175
- Completion tokens：1,335
- 其中 reasoning tokens：683
- 总 tokens：66,510

每轮总 token：

```text
[1837, 1973, 5785, 5928, 6279, 6608, 6945, 7281, 7622, 7957, 8295]
```

### 4.2 SearchPlanner

- 调用次数：2
- Prompt tokens：2,249
- Completion tokens：4,243
- 其中 reasoning tokens：3,436
- 总 tokens：6,492

两次调用分别使用 1,991 和 4,501 tokens。`SearchPlannerAgent` 最多尝试两次生成并校验 SearchPlan，因此这里表明本次规划发生了一次重试。

### 4.3 总计

- Researcher + SearchPlanner：73,002 tokens
- 模型隔离符合预期：主 Researcher 未被替换为 SearchPlanner 的轻量模型

## 5. Manifest 与正式输出

实验结束时 Manifest 快照：

| 对象 | 数量 |
| --- | ---: |
| Work | 8 |
| SourceRecord | 18 |
| Artifact | 16 |

注意：实验脚本使用固定的 `subject_paper_id`，本次是对同一 required-all smoke workspace 的再次运行。因此以上是去重后的累计 Manifest 快照，不能全部归因于本次单次调用；它仍可证明稳定 ID 和重复持久化没有造成冲突。

TaskResearchResult：

| 字段 | 结果 |
| --- | ---: |
| finish status | `partial` |
| trusted reads | 0 |
| evidence | 0 |
| evidence cards | 0 |
| research bundles | 0 |

告警：

```text
native tool harness failed: tool-call budget exhausted
```

## 6. 验收判断

| 验收项 | 结果 | 说明 |
| --- | --- | --- |
| LLM 能看到四个正式工具 | PASS | 注册列表完整 |
| 真实模型合法调用 DatabaseSearch | PASS | 实际调用 1 次 |
| SearchPlanner 使用独立轻量模型 | PASS | `r1-qwen3-8b`，调用 2 次 |
| 主 Researcher 保持原模型 | PASS | `deepseek-flash` |
| WebSearch/Browser 可被真实模型调用 | PASS | 分别调用 1 次和 8 次 |
| DatabaseSearch 候选持久化体系可用 | PASS | Manifest 中存在 Work、SourceRecord、Artifact；独立 smoke 已验证单次写入 |
| Reader 读取 DB/Web Artifact | FAIL | 本次 Reader 调用数为 0 |
| Builder 从 trusted reads 构建证据 | FAIL | 没有 trusted read，Builder 无输入 |
| Native `research_bundles` 保持为空 | PASS | 数量为 0 |
| 正常 finish | FAIL | 工具预算耗尽，状态为 partial |
| 四工具真实全链路 | FAIL | 缺少 Reader 与 finish |

## 7. 与上一次 required-all 实验对比

上一次序列为：

```text
database_search → reader → web_search → browser × 7
```

上一次至少完成了一次 DB Artifact → Reader；本次则在 Web Browser 阶段重复调用并未进入 Reader。两次都因 Browser 重复调用耗尽预算，说明问题具有重复性，但具体序列受模型采样和外部 observation 影响。

## 8. 结论

```text
工具注册：PASS
真实 DatabaseSearch 调用：PASS
SearchPlanner 模型隔离：PASS
ReferenceStore / ResearchBundle 边界：PASS
真实四工具全链路：FAIL
实验总体：FAIL（partial，工具预算耗尽）
```

本次失败不属于 DatabaseSearch 的机械连通性问题。离线 scripted 测试已经通过完整的：

```text
database_search → reader → web_search → browser → reader → finish
```

真实模型当前的主要问题是 Browser 调用重复，导致 Reader 和 finish 没有执行。由于本轮任务明确禁止进行 per-tool budget 调优，本实验没有修改 Harness 预算或引入 Progress/Skill 控制框架。
