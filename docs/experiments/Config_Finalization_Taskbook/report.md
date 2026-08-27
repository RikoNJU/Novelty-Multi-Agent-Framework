# Config 收口修正实验报告

- 执行日期：2026-08-27
- 任务书：`task/Config_Finalization_Taskbook.md`
- 基线 SHA：`2e27ef12050ed56c26ef27c7b453226b7bd0b70d`
- 实验类型：离线配置装配、单元测试与脚本化集成回归

## 结论

Config 正式主路径已收口为 `JSON → Loader → ApplicationConfig → Factory → Runtime`。
Typed Factory 不再调用 `legacy_shape()`；SearchPlanner prompt、四工具参数和各层预算均由
typed fields 直接注入。Reader 累计字符预算在工具执行前使用 args schema 补全后的规范参数
检查，省略 `max_chars` 不再绕过预检。

Config 子系统状态：**FROZEN**。

## 验收结果

| 验收项 | 状态 | 证据 |
| --- | --- | --- |
| Config filename cleanup | PASS | 正确文件存在，旧拼写不存在，Loader 默认路径已更新 |
| SearchPlanner prompt injection | PASS | recording prompt 测试确认实际调用自定义 render name |
| ApplicationConfig direct factory path | PASS | typed factory 直接读取全部要求字段 |
| legacy_shape removed from typed main path | PASS | monkeypatch 为抛错后 typed workflow 仍成功构建 |
| Reader canonical-argument budget precheck | PASS | 显式 1200、默认 8000 在剩余 1000 时均执行前拒绝 |
| Reader actual-character accounting | PASS | 请求 4000、实际 2500 后可继续使用剩余 2500 |
| Typed Config cross-field validation | PASS | Reader 与 Baidu 四项约束均有失败测试 |
| Legacy mapping smoke | PASS | 既有 factory 回归通过 |

未加入 `full_text_limit_per_task <= candidate_limit_per_task` 校验：当前检索层允许全文获取
上限独立配置，实际可用候选仍由召回结果自然约束，强制二者大小关系会改变现有业务语义。

## 回归测试

任务书指定测试集：

```text
52 passed
0 failed
```

命令覆盖 config loader、runtime injection、ToolCallHarness、SearchPlanner、Reader、
DatabaseSearch 与 scripted four-tool integration。

非实时全量 backend 测试：

```text
358 collected
352 passed
6 skipped
0 failed
```

跳过项为测试套件已有的 live 测试；另按既有约定排除 `tests/test_api.py`，未发起真实 LLM
或外部网络调用。

## Config smoke

```json
{
  "registered_tools": [
    "database_search",
    "web_search",
    "browser",
    "reader"
  ],
  "researcher_model": "deepseek-flash",
  "search_planner_model": "r1-qwen3-8b",
  "effective_safe_config": true
}
```

`effective_safe_config` 序列化检查未发现 API key 或 secret 值。

## 范围确认

本次未修改 EvidenceCardBuilder、DatabaseSearch 数据 contract、Researcher 方法论 prompt、
工具选择策略或预算数值，也未引入 Progress、Skill 或 phase gating。
