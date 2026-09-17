# 基线与材料核对

- 冻结当前代码身份见 `source-manifest.json`；历史输入来自 `20260916_233840/runs/full/0004–0006`。
- 选择 run 4 的 NP-2/T-1：它是预定顺序中的首个完整样本，不按结果优劣选择。
- 三次都有编译后的 SearchPlan、任务结果、Runtime Debug；原始 SearchPlanDraft 未归档。
  因而 C0/C1 输入均为 `derived_projection`，不可宣称为精确历史 Draft × Compiler 重放。
- 当前职责链：`agents/search_planner.py:SearchPlannerAgent.plan` 生成一次计划；`agents/search_plan_compiler.py:build_runtime_plan` 纯本地编译；`tools/database_search/structured_retrieval.py` 消费传入计划并只生成 fallback 链，不在工具内再次调用 Planner。任务级 Researcher 的工具注册位于 `agents/research.py`。
- 本轮仅执行本地文件读取与表达式组合，模型、Provider、Reader 调用均为 0。
