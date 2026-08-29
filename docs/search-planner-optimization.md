# SearchPlanner 契约优化开发方案

> 状态：方案已确认，范围已收敛。**不修改 tools/ 下任何内容**（web_search、database_search、browser、reader 等一律不动）。

## 一、目标

1. 模型契约最小化：SearchPlanner 只输出语义载荷 `concepts[].terms` 与 `strategies[].expression`；
2. 机械字段（concept_id、strategy_id、task_id、novelty_point_id、level、name、description）全部由确定性补全器代码生成；
3. 运行时 `SearchPlan` schema 不变，下游（adapter / persistence / renderer / 审计）零改动；
4. 校验失败面收窄：ID 格式/重复/绑定/level 顺序等由"校验"变为"赋值"，重试率下降。

## 二、范围边界（用户确认）

- ✅ 可改：`schemas/`（新增 draft 契约）、`agents/`（SearchPlannerAgent + 新增补全器）、`prompts/search_planner/plan.md`、`tests/`
- ❌ 不改：`tools/` 全部内容、web_search / database_search / browser / reader 参数与行为
- ❌ 不做：web query_suggestion 注入与工具层一致性校验（二期取消）

## 三、设计

### 3.1 最小模型契约（新增 `schemas/search_plan_draft.py`）

```python
class SearchConceptDraft(StrictModel):
    terms: list[str]          # 唯一必填；concept_id 由系统按顺序分配 C1..Cn

class SearchStrategyDraft(StrictModel):
    expression: str           # 引用 C1..Cn + AND/OR/括号；strategy_id/level 由系统分配

class SearchPlanDraft(StrictModel):
    concepts: list[SearchConceptDraft]    # 顺序即编号
    strategies: list[SearchStrategyDraft] # 顺序即 level（strict/medium/broad）
```

### 3.2 确定性补全器（新增 `agents/search_plan_compiler.py`）

```python
def build_runtime_plan(draft: SearchPlanDraft, *, task: ResearchTask) -> SearchPlan
```

职责（纯代码，无 LLM、无网络）：
1. draft 校验：terms 非空、expression 非空、无数据库语法、引用概念必须已定义、literature_search 必须恰好 3 条策略；
2. 编号：concept_id=`C{i+1}`、strategy_id=`S{j+1}`（按位置）；
3. 注入：task_id / novelty_point_id 取自 `task`（绑定天然成立，无需再校验）；
4. 标注：level 按位置取 `["strict","medium","broad"]`，超出补 broad；
5. 派生：name=`terms[0]`；description=表达式中的概念 ID 替换为概念名。

### 3.3 校验架构变化

| 现状 | 改后 |
| --- | --- |
| 4 处绑定校验 | 1 处（补全器注入）；schema validator 保留 2 处防御 |
| `C\d+`/`S\d+` 格式、重复 ID 校验 | 删除（编号代码生成，不可能非法） |
| level 顺序校验 | 变为按位置赋值 |
| 数据库语法拦截、引用完整性 | 保留（移入补全器） |

### 3.4 双视图：补全服务机器/审计，投影服务模型（关键设计决策）

补全器生成的完整 SearchPlan 只流向**机器与审计**（adapter 编译、persistence、execution_id）。
Researcher 提示词**不得**注入完整 plan——只投影最小语义（concepts.terms + strategies.expression），因为：

- Researcher 是执行者，不需要 ID/level/name/description/绑定（上下文里已有 NoveltyPoint/ResearchTask）；
- native_tool_loop.md 是 system prompt，每轮工具循环（最多 12 轮）都重复携带 plan，投影越小省得越多；
- 实测 NP-1/T-1 完整 plan ~1.5KB，ID/name/level/description/绑定约占 30-40%，投影后单任务可省数千 token。

渲染示意（workflows/research_task.py 中实现，不碰 tools/）：

    "search_plan_json": json.dumps({
        "concepts":   [{"terms": c.terms} for c in plan.concepts],
        "strategies": [{"expression": s.expression} for s in plan.strategies],
    }, ensure_ascii=False)

## 四、改动文件清单

| 文件 | 动作 | 阶段 |
| --- | --- | --- |
| `schemas/search_plan_draft.py` | 新增（draft 契约） | M1 |
| `schemas/__init__.py` | 导出 draft 类 | M1 |
| `agents/search_plan_compiler.py` | 新增（补全器） | M1 |
| `tests/test_plan_compiler.py` | 新增（补全器单测） | M1 |
| `agents/search_planner.py` | `plan()` 走 draft → 补全 → 校验 | M2 |
| `prompts/search_planner/plan.md` | 最小契约 + 编号语义说明 | M2 |
| `tests/test_search_planner.py` | 适配 draft 契约 | M2 |
| `workflows/research_task.py` | 提示词注入改为最小投影（terms + expression） | M2（可选但推荐） |
| `prompts/research/native_tool_loop.md` | 说明最小投影结构（若上项实施） | M2（可选） |

## 五、实施步骤

- **M1（纯新增，零风险）**：draft schema + 补全器 + 单测；不接线，现有行为不变，跑全量回归确认。
- **M2（切换）**：改 `SearchPlannerAgent.plan()` 与 prompt，适配测试；回归基线：离线全量 `352 passed / 6 skipped`。
- **M3（实跑验证）**：复用 `run_one_raw.py` 模式，对比基线（1 次尝试 / 172.8s / ~1.5KB 原始返回）。

## 六、验收标准

- 模型输出字段：9 类 → 2 类（terms + expression）；
- 全量离线测试通过（基线 352 passed / 6 skipped）；
- 下游（adapter/persistence/renderer/审计）零改动、其测试零改动通过；
- 单任务实跑 ok，原始返回体积目标 -30%+。
- Researcher 提示词注入体积 -30%+（12 轮循环端到端省数千 token；若实施投影）。

## 七、风险与回滚

| 风险 | 缓解 |
| --- | --- |
| 模型不适应"无 ID 契约" | prompt 加编号语义示例；失败走 retry_reason 重试 |
| 现有测试 mock 完整 SearchPlan | 运行时 schema 不变，多数零改动；仅 mock Planner 输出的测试更新 |
| 回滚 | M1 纯新增可独立保留；M2 回滚只需恢复 `plan()` 一行 |
