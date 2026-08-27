# Researcher Config Decoupling 三阶段实验报告

执行日期：2026-08-27（Asia/Shanghai）

## Config Integrity

结果：**PASS**

- Project settings、models、Researcher、SearchPlanner 分文件加载成功。
- Typed Config 全部校验成功。
- Researcher 模型：`deepseek-flash`。
- SearchPlanner 模型：`r1-qwen3-8b`。
- 正式工具：`database_search`、`web_search`、`browser`、`reader`。
- Effective config 不包含 API key 或环境变量值。
- 详细安全配置见
  `outputs/experiments/Researcher_Config_Decoupling_Three_Stage_Taskbook/config-integrity.json`。

## Parameter Perturbation

结果：**PASS**

只修改临时 JSON 配置，未修改 Python，明显非默认值全部到达最终 runtime object：Researcher/Planner invocation、Harness 总预算与 per-tool budget、Reader 单次与累计字符、DB 数量与并发、arXiv 节流/timeout/retry/fulltext、Baidu timeout、Browser timeout/内容限制。

详细值见
`outputs/experiments/Researcher_Config_Decoupling_Three_Stage_Taskbook/parameter-perturbation.json`。

## Scripted 四工具链

结果：**PASS**

```text
database_search → reader → web_search → browser → reader → finish
```

- 共享 ReferenceStore：PASS
- trusted reads：2
- Evidence：2
- EvidenceCard：2
- `research_bundles`：0

## 真实 LLM required-all 实验

结果：**PARTIAL**

实际序列：

```text
database_search → web_search → browser → browser → browser
→ browser tool-call budget exhausted
```

调用统计：

| 工具 | 次数 |
| --- | ---: |
| database_search | 1 |
| web_search | 1 |
| browser | 3 |
| reader | 0 |

模型与 token：

| Agent | calls | prompt | completion | reasoning | total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Researcher (`deepseek-flash`) | 6 | 28,236 | 2,792 | 2,350 | 31,028 |
| SearchPlanner (`r1-qwen3-8b`) | 2 | 2,121 | 1,868 | 893 | 3,989 |
| 合计 | 8 | 30,357 | 4,660 | 3,243 | 35,017 |

- elapsed：239.716 秒
- Manifest：0 Work、10 SourceRecord、0 Artifact
- trusted reads：0
- Evidence：0
- EvidenceCard：0
- finish status：`partial`
- ResearchBundle：0

告警：

```text
query compilation NP-live-four/T-live-four/S4 failed:
QueryAdapterError: 检索表达式包含不支持的 token：'NOT'

native tool harness failed: browser tool-call budget exhausted
```

Browser 的第 4 次调用被 `per_tool_limits.browser = 3` 精确拦截，证明 runtime enforcement 生效。真实策略仍因 Browser 重复而未进入 Reader；这属于 Research Strategy Quality，不影响配置系统验收。

原始结果见
`outputs/experiments/Researcher_Config_Decoupling_Three_Stage_Taskbook/real-llm-required-all.json`。

## 最终判断

```text
Config split                  PASS
Typed config                  PASS
Factory construction          PASS
Runtime parameter injection   PASS
Runtime parameter enforcement PASS
Four-tool integration         PASS
Real LLM smoke                PARTIAL
```

本任务没有引入 Progress Projection、Skill、phase gating，没有迁移 Validator/Reviewer，也没有修改 EvidenceCardBuilder contract。
