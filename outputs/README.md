# `outputs/` 目录说明

`outputs/` 是论文 PDF 解析和查新工作流的本地工作目录。每篇论文使用一个独立的
`paper_id`，所有阶段产物统一存放在 `outputs/<paper_id>/` 下，避免不同论文之间
相互覆盖。

本目录中的文件是可重新生成的运行产物，不应作为源代码维护或手工混放其他文件。
原始 PDF 仍保留在调用者指定的输入位置，当前解析流程不会把 PDF 复制到这里。

## 目录结构

```text
outputs/
└── <paper_id>/
    ├── paper-input/
    │   ├── full.md
    │   ├── content-list.json
    │   ├── images/
    │   └── others/
    │       └── paper.json
    ├── novelty-points.json
    ├── retrieval-plans.json
    ├── evidence-cards.json
    ├── report.json
    ├── run-metrics.json                 # 可选，真实实验统计
    └── report/
        └── <paper_id>-report.md
```

`paper_id` 默认取 PDF 文件名（不含扩展名），也可以在解析时显式指定。用于目录名时，
除字母、数字、点、下划线和连字符以外的字符会被替换为下划线，并移除首尾的点和
下划线。

## PDF 解析产物

PDF 解析阶段只写入 `paper-input/`：

| 路径 | 内容 |
| --- | --- |
| `paper-input/full.md` | 解析得到的论文全文文本，供检查解析质量和后续处理使用。 |
| `paper-input/content-list.json` | 解析摘要，包括标题、来源、页数、章节是否存在及字符数、中英文关键词、参考文献数量、解析警告，以及工作流输入文件位置。 |
| `paper-input/others/paper.json` | 符合 `PaperInput` 数据契约的结构化论文输入，是查新工作流和报告渲染器读取的正式输入。 |
| `paper-input/images/` | 论文图片产物的预留目录；即使当前解析未生成图片，也会创建。 |
| `paper-input/others/` | 除全文和图片外的结构化解析产物目录，当前保存 `paper.json`。 |

解析命令示例：

```bash
python -m novelty_agent_framework.processing.cli \
  --input examples/MF2033k6lC.pdf \
  --output outputs
```

如需覆盖默认 ID，可增加 `--paper-id <paper_id>`；如需跳过文本层质量判断并强制使用
OCR，可增加 `--force-ocr`。

如果工作流直接从 JSON 或 API 启动而未先处理 PDF，持久化层仍会建立相同的
`paper-input/` 结构：由 `PaperInput.full_text` 生成 `full.md`，生成简化的
`content-list.json`，并写出 `others/paper.json`。

## 查新过程产物

查新阶段的文件位于单篇论文工作目录根部，并按执行顺序逐步生成：

| 路径 | 生成阶段与用途 |
| --- | --- |
| `novelty-points.json` | PointExtractor 提取的查新点，包括中英文主张、技术特征和原文位置。 |
| `retrieval-plans.json` | 按查新点保存调研任务、数据库无关的语义检索计划、实际执行的数据库 Query 和检索轮次。 |
| `evidence-cards.json` | 保存校验前的原始证据、通过校验的证据，以及被拒证据和拒绝原因，便于审计。 |
| `report.json` | Coordinator 汇总并通过数据校验的结构化查新结论，是报告渲染的输入。 |
| `run-metrics.json` | 可选实验记录，通常包括运行时间、模型调用及 Token 用量、阶段统计、告警和最终结果摘要；不属于报告渲染的必需输入。 |
| `report/<paper_id>-report.md` | Renderer 根据上述结构化产物确定性生成的最终 Markdown 报告。 |

`retrieval-plans.json` 中每个查新点包含以下几层信息：

- `research_tasks`：Coordinator 分配的中文、英文等调研任务；
- `search_plans`：SearchPlanner 生成的概念、同义词和宽严不同的检索策略；
- `executed_queries`：Adapter 转换后真正提交给具体数据库的查询及执行信息；
- `query_plan.queries`：实际 Query 的去重列表，供当前 Renderer 展示；
- `query_plan.attempts`：该查新点涉及的检索尝试轮次。

渲染 Markdown 报告前，以下五个文件必须齐全：

```text
paper-input/others/paper.json
novelty-points.json
retrieval-plans.json
evidence-cards.json
report.json
```

渲染示例：

```python
from novelty_agent_framework.tools import render_report

path = render_report(output_format="markdown", paper_name="<paper_id>")
```

## 存放约定

- 一篇论文只使用一个 `outputs/<paper_id>/` 工作目录；重新运行同一阶段时，对应 JSON
  或 Markdown 文件会被覆盖，未被该阶段写入的其他文件会保留。
- 不要手工修改中间 JSON 后再把它视作可复现结果；如需修正内容，应修改输入、配置或
  生成逻辑后重新运行相应阶段。
- `report.json` 是结构化结论，`report/<paper_id>-report.md` 是展示文件，两者不要混淆。
- 路径统一相对于仓库根目录解释。自定义 `--output` 时，目录内部仍遵循同样的
  `<paper_id>/...` 结构。
- 本地运行产物默认不提交；`outputs/.gitkeep` 和本说明文件仅用于保留并说明目录结构。
