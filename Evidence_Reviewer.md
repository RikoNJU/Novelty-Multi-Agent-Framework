标题：`feat(reviewer): 实现数据库无关的证据审查与质量门控`

## 背景

当前工作流已经具备：

* Research Agent生成`EvidenceCard`；
* `DefaultEvidenceValidator`执行确定性校验；
* 低置信度、低相关性、缺少来源、任务归属错误和重复证据会被拒绝；
* 校验前后证据写入`outputs/<paper_id>/evidence-cards.json`；
* Coordinator使用通过校验的证据生成报告。

但当前校验主要停留在字段和阈值层面，还没有真正审查：

* Evidence Card是否准确对应目标查新点；
* `overlaps`和`differences`是否有来源支撑；
* `main_contribution`是否超出文献内容；
* 引文能否支持对应判断；
* 是否把摘要级信息误写成全文级结论；
* Evidence Card内部是否自相矛盾；
* 证据强度是否支持其置信度和相关性评分。

本任务实现数据库无关的证据Reviewer。Reviewer只依赖标准化的查新点、调研任务、Evidence Card及系统已经提供的证据内容，不绑定arXiv、OpenAlex、X-MOL、ChinaXiv等具体来源。

开发基线：

```text
lya @ 63952f5ad624a20203370d23220c460497a5643e
```

建议开发分支：

```text
feat/evidence-reviewer
```

## 目标

在当前流程中形成：

```text
Research Agent生成原始Evidence Card
→ 确定性Validator执行基础门控
→ Evidence Reviewer进行语义和证据一致性审查
→ 接受、拒绝或要求补充
→ 结果写入evidence-cards.json
→ Coordinator只使用最终通过的证据
```

Reviewer不能直接修改Research Agent生成的证据，也不能自行创造引用、来源、相同点或不同点。

## 职责边界

### Reviewer负责

1. 检查Evidence Card是否对应指定`NoveltyPoint`
2. 检查`task_id`与`novelty_point_id`的语义目标是否一致
3. 检查`main_contribution`是否被来源内容支持
4. 检查每项`overlaps`是否有明确证据
5. 检查每项`differences`是否有明确证据
6. 检查直接引文与结论之间是否存在合理推导关系
7. 检查摘要级证据是否被夸大为全文级结论
8. 检查相关性和置信度是否明显虚高
9. 检查Evidence Card内部是否存在矛盾
10. 输出结构化审查决定和问题列表

### Reviewer不负责

* 重新执行完整文献检索
* 判断整个数据库范围是否已经覆盖充分
* 宣称“未发现即不存在”
* 自动补写不存在的引用
* 自动修改原始Evidence Card
* 绕过登录、验证码或付费墙核验论文
* 绑定特定数据库API
* 取代Coordinator生成最终查新结论
* 取代现有`DefaultEvidenceValidator`
* 重构Research Agent Harness
* 修改PDF Parser

检索完整性、网页核验和跨来源元数据真实性依赖后续Research Harness，本Issue只预留接口或问题代码，不假装已经完成。

## 现有实现说明

开始开发前阅读：

```text
backend/src/novelty_agent_framework/agents/evidence_validator.py
backend/src/novelty_agent_framework/ports/interfaces.py
backend/src/novelty_agent_framework/schemas/domain.py
backend/src/novelty_agent_framework/workflows/novelty.py
backend/src/novelty_agent_framework/persistence.py
backend/src/novelty_agent_framework/prompts/reviewer/
outputs/README.md
tests/test_workflow.py
```

注意：

```text
prompts/reviewer/review_points.md
```

当前只负责候选查新点去重。不要直接改变它的语义来实现证据Reviewer，以免破坏查新点提取流程。证据审查应新增独立Prompt和实现，例如：

```text
prompts/reviewer/review_evidence.md
agents/evidence_reviewer.py
```

具体命名可以按项目风格调整。

## 设计要求

### 1. 保留确定性Validator

`DefaultEvidenceValidator`继续负责便宜、稳定、可测试的硬规则：

* task归属；
* 查新点绑定；
* 最低置信度；
* 最低相关性；
* 来源存在；
* DOI或URL存在；
* quote与location存在；
* 重复证据消除。

不要把这些规则全部迁移到LLM Prompt。

推荐顺序：

```text
原始Evidence Card
→ DefaultEvidenceValidator
→ Evidence Reviewer
→ 最终Evidence Card
```

确定性Validator已经拒绝的卡片不再调用LLM，避免浪费Token。

### 2. 增加Reviewer接口

建议增加数据库无关接口，例如：

```python
class EvidenceReviewer(Protocol):
    def review(
        self,
        cards: Sequence[EvidenceCard],
        *,
        points: Sequence[NoveltyPoint],
        tasks: Sequence[ResearchTask],
    ) -> ReviewResult:
        ...
```

具体输入可以根据当前工作流调整，但必须满足：

* 不传入数据库专有响应；
* 不要求document_id必须是arXiv ID；
* 不依赖某个具体MetadataTool；
* 支持同步或异步实现；
* 可以提供Null/Demo Reviewer，保持默认测试无真实模型也能运行。

### 3. 增加结构化审查结果

建议新增严格Schema，示例：

```python
class ReviewVerdict(StrEnum):
    ACCEPT = "accept"
    REJECT = "reject"
    NEEDS_MORE_EVIDENCE = "needs_more_evidence"


class EvidenceReviewIssue(StrictModel):
    code: str
    message: str
    severity: IssueSeverity = IssueSeverity.WARNING
    field: str | None = None
    source_index: int | None = None


class EvidenceReviewDecision(StrictModel):
    card_id: str
    verdict: ReviewVerdict
    issues: list[EvidenceReviewIssue] = Field(default_factory=list)
    reviewed_confidence: float = Field(ge=0.0, le=1.0)
```

可根据现有模型进一步简化，但需要：

* 严格拒绝未声明字段；
* 每个决定必须绑定已有`card_id`；
* Reviewer不能返回修改后的Evidence Card；
* `reviewed_confidence`是Reviewer对该卡可信程度的评价，不覆盖原始`confidence`；
* 不能只返回自由文本。

### 4. 受控问题代码

优先使用稳定的问题代码，例如：

```text
unsupported_main_contribution
unsupported_overlap
unsupported_difference
quote_not_supporting_claim
scope_overstatement
abstract_only_overclaim
novelty_point_mismatch
task_mismatch
internal_contradiction
confidence_overstated
relevance_overstated
missing_evidence_detail
metadata_unverified
fulltext_unavailable
retrieval_coverage_unknown
```

其中：

* `metadata_unverified`表示当前没有足够条件核验，不等于论文为假；
* `retrieval_coverage_unknown`表示Reviewer无法判断整体召回，不应直接拒绝单张有效证据；
* 不得把“无法核验”写成“已经证伪”。

### 5. Prompt要求

新增证据审查Prompt，至少包含：

* Reviewer只能依据输入内容判断；
* 不允许使用模型记忆补充论文事实；
* 不允许生成新DOI、URL、引文或页码；
* 不允许重写Evidence Card；
* 每个问题必须绑定具体字段；
* 相同点和不同点需要分别判断；
* 没有全文时必须降低结论范围；
* 无法判断时输出`needs_more_evidence`，不能猜测；
* 输出必须严格符合JSON Schema；
* 禁止输出开场白和解释性Markdown。

输入内容至少包括：

```text
NoveltyPoint
ResearchTask
EvidenceCard
审查输出Schema
```

如果系统已经取得候选文献摘要或全文片段，可以作为明确标注的`source_content`传入；如果没有，不得让Reviewer声称已核对原文。

### 6. Workflow接入

在当前工作流中增加独立审查阶段：

```text
parallel_research
→ validate_evidence
→ review_evidence
→ assess_coverage
```

要求：

* 确定性Validator先执行；
* Reviewer只处理基础校验通过的卡片；
* Reviewer不可用时的行为由配置决定；
* 默认Demo/离线环境不依赖真实LLM；
* Review失败不能静默接受全部证据；
* 单张卡片审查失败不应导致整个工作流崩溃；
* 失败应生成`WorkflowIssue`；
* Coordinator只能接收最终通过审查的Evidence Card；
* `needs_more_evidence`应进入coverage gap或补充调研提示，但本Issue不重构检索流程。

Reviewer可配置开关示例：

```json
{
  "agents": {
    "reviewer": {
      "enabled": false,
      "model": "deepseek-flash",
      "temperature": 0.0,
      "prompt": "reviewer/review_evidence"
    }
  }
}
```

实际配置应复用现有ModelRegistry和PromptLibrary，不直接在Reviewer中创建模型客户端。

### 7. 配置与失败策略

建议支持：

```text
enabled
model
temperature
max_cards_per_call
fail_closed
```

其中：

* `temperature`默认接近0；
* `max_cards_per_call`避免一次输入过长；
* `fail_closed=true`时，审查失败的卡片不进入最终证据；
* `fail_closed=false`仅适用于开发兼容，应产生明确warning；
* 示例配置默认不得依赖真实API Key。

不要给Reviewer单独新增密钥读取逻辑，继续使用现有模型配置和环境变量机制。

## 输出文件约定

遵循：

```text
outputs/<paper_id>/evidence-cards.json
```

不得新增另一套论文输出根目录。

在保持现有字段的基础上，建议扩展为：

```json
{
  "paper_id": "...",
  "raw_evidence_cards": [],
  "validator_accepted_cards": [],
  "review_decisions": [],
  "accepted_evidence_cards": [],
  "rejected_evidence": []
}
```

含义：

* `raw_evidence_cards`：Research Agent原始输出；
* `validator_accepted_cards`：通过确定性Validator的证据；
* `review_decisions`：Reviewer的逐卡结构化决定；
* `accepted_evidence_cards`：最终允许Coordinator使用的证据；
* `rejected_evidence`：所有拒绝项及原因。

如果为了兼容性不增加`validator_accepted_cards`，也必须保证：

* 原始证据不丢失；
* Reviewer决定可追踪；
* 最终接受证据与原始证据可以通过`card_id`对应；
* 现有Renderer读取不被破坏；
* 重跑审查阶段只覆盖`evidence-cards.json`；
* 不覆盖其他阶段产物。

## 测试要求

建议新增：

```text
tests/test_evidence_reviewer.py
tests/test_workflow_reviewer.py
tests/test_live_evidence_reviewer.py
```

### 离线测试至少覆盖

1. 合法Evidence Card通过审查
2. `card_id`不存在时拒绝Reviewer输出
3. Reviewer返回额外字段时Schema校验失败
4. Reviewer尝试修改Evidence Card时不被采纳
5. main contribution缺乏支撑
6. overlap缺乏支撑
7. difference缺乏支撑
8. 引文与判断不一致
9. 摘要证据被夸大成全文结论
10. 查新点与Evidence Card不一致
11. task绑定错误
12. confidence明显虚高
13. Reviewer返回`needs_more_evidence`
14. 单张卡片审查失败不导致全流程崩溃
15. Reviewer禁用时维持兼容行为
16. fail-closed与fail-open配置行为
17. 确定性Validator拒绝的卡片不调用LLM
18. 审查结果正确写入`evidence-cards.json`
19. Coordinator只接收最终通过的证据
20. 现有工作流和Renderer测试保持通过

离线测试使用Fake Model或Mock Client，不访问真实网络，不消耗Token。

### 真实模型测试

使用：

```python
pytest.mark.live
```

默认测试集必须跳过。

测试输入使用仓库内人工构造的小型Evidence Card，不依赖真实网页访问。至少验证：

* 模型返回合法Schema；
* 对明显缺乏支撑的证据可以拒绝；
* 对证据不足情况返回`needs_more_evidence`；
* 不生成输入中不存在的DOI、URL、引文或页码。

运行方式：

```bash
pytest tests/test_evidence_reviewer.py tests/test_workflow_reviewer.py -q
pytest -m live tests/test_live_evidence_reviewer.py -s
```

## 验收标准

* [ ] 保留并复用现有`DefaultEvidenceValidator`
* [ ] 新增独立、数据库无关的Evidence Reviewer
* [ ] 未改变现有查新点去重Prompt的职责
* [ ] Reviewer输出采用严格结构化Schema
* [ ] Reviewer不能修改或创造Evidence Card内容
* [ ] 能识别缺乏支撑的贡献、相同点和不同点
* [ ] 能区分摘要级证据和全文级证据
* [ ] 无法核验时不会猜测
* [ ] Reviewer接入Validator之后、coverage assessment之前
* [ ] Coordinator只使用最终通过的证据
* [ ] 审查决定可在`evidence-cards.json`中追踪
* [ ] Reviewer禁用时默认工作流仍可运行
* [ ] 单卡失败不会使整个工作流崩溃
* [ ] 离线测试不访问网络、不消耗Token
* [ ] 现有默认测试集保持通过
* [ ] 未绑定arXiv、OpenAlex或其他具体来源
* [ ] 未提交API Key、真实论文全文或运行产物

## 非目标

本Issue不负责：

* Research Agent Harness重构
* 通用网页搜索或浏览器工具
* OpenAlex、ChinaXiv、X-MOL、万方等数据源接入
* 全量检索覆盖率判断
* 自动重新检索缺失文献
* 生成最终NoveltyReport
* PDF解析或MinerU接入
* 前端Reviewer页面
* 人工审核工作台
* 自动合并或改写Evidence Card

## 交付要求

* 不要自动合并到`lya`，完成后由组内Review。
