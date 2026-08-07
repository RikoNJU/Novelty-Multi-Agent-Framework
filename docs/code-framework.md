# 论文查新代码框架说明

## 1. 框架定位

该框架实现论文查新的“总—分—总”闭环：Coordinator 提取查新点并规划任务，多个 Research Agent 并行调研文献，最后基于可追溯证据形成查新报告。

当前代码是可运行骨架，不绑定具体大模型、Prompt 或学术数据库。

当前后端代码统一放在 `backend/src/novelty_agent_framework/`，并在包内按职责拆分目录，避免核心逻辑堆在少数单文件里。

## 2. 运行流程

```text
论文输入
→ 生成 Novelty Brief 和调研任务
→ Research Agent 并行生成 Evidence Card
→ 校验证据来源、相关性和置信度
→ 评估每个查新点的证据覆盖
→ 证据不足时定向补充检索（最多两轮）
→ 生成 Novelty Report
```

单个调研任务失败不会丢失其他并行结果；达到轮次上限后，证据不足的查新点会被明确标记。

## 3. 核心模块

| 目录 | 职责 |
|---|---|
| `schemas/` | 定义论文、查新点、调研任务、Evidence Card 和查新报告 |
| `ports/` | 定义 Coordinator、Research Agent 及文献工具接口 |
| `agents/` | 放置查新主 Agent、文献调研 Agent、Demo Agent 和证据校验 Agent |
| `backend/env/` | 统一模型配置、消息格式、多模型注册表和 Prompt 渲染，避免不同 Agent 各自实现模型请求 |
| `prompts/` | 生产 Agent 的版本化提示词模板（front matter + 变量占位符） |
| `config/` | Web 设置与组合根 `build_workflow()`：从 `models` / `agents` 配置装配工作流 |
| `workflows/` | 编排并行调研、证据校验、补充检索和报告生成，并装配默认工作流 |
| `routers/` | 提供可选 API 入口 |
| `services/` | 管理任务生命周期和运行状态 |

## 3.1 多模型与提示词配置

`settings.example.json` 中 `models` 注册模型别名（provider、base_url、model、
api_key_env、context_window、supported_params、defaults），`agents` 为每个角色
指定使用的模型别名、温度和提示词文件。组合根 `build_workflow()` 读取配置，
构建 `ModelRegistry` 与 `PromptLibrary`，再按角色装配 Agent。

环境变量可按角色覆盖模型：`NOVELTY_COORDINATOR_MODEL`、`NOVELTY_RESEARCH_MODEL`。
厂商私有参数（如 `enable_thinking`）通过 `ModelCallOptions.extra_body` 透传，
发送前按 `supported_params` 白名单过滤，换模型不会因多余参数失败。

## 4. 输入与输出

- 输入：`PaperInput`，包含论文正文、摘要、参考文献和作者声明的贡献。
- 中间结果：`NoveltyBrief`、`ResearchTask`、`EvidenceCard`。
- 输出：`NoveltyRunResult`，其中 `NoveltyReport` 给出各查新点结论、缺失文献、缺失 Baseline、引用问题和检索局限。

重要结论必须关联可追溯文献来源，模型自身判断不能直接代替证据。

## 5. 接入真实能力

生产实现主要替换以下接口：

- `NoveltyCoordinator`：论文理解、查新规划、补检规划和最终汇总；
- `LiteratureResearchAgent`：检索、阅读和文献对比；
- `SearchTool`、`FullTextTool`、`MetadataTool`：学术搜索、全文获取和元数据核验。

工作流、数据契约和证据门槛通常不需要随模型一起重写。

## 6. 运行

```powershell
conda activate langgraph
cd D:\novelty-multi-agent-framework
pip install -e ".[dev,web]"
novelty-demo --input examples\paper.json --output output\result.json
```

`novelty-demo` 只用于验证框架闭环，输出不代表真实查新结果。
