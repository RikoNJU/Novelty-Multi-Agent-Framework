# Issue 1：LangGraph 异步循环工作流结束后不返回

## 1. 问题摘要

论文查新工作流的所有业务节点看起来都已完成，但调用方一直无法收到最终结果：

```python
final = await self.graph.ainvoke(initial)
```

`ainvoke()` 持续等待且不抛出异常，导致以下入口同时阻塞：

- `NoveltyWorkflow.run()`；
- `NoveltyWorkflow.arun()`；
- `tests/test_workflow.py` 中的工作流测试；
- FastAPI 创建查新任务后的后台执行流程。

最终采用的解决方案是：把异步 LangGraph 中剩余的同步覆盖评估节点和同步条件路由改为异步 callable，使整张带补检回边的图保持一致的异步执行模型。

修复提交：`8786efb fix: prevent async LangGraph workflow hang`。

## 2. 运行环境

问题排查时使用项目已有的 conda 环境：

```text
/home/lya3106643285/miniconda3/envs/Novelty
Python 3.11.15
langgraph 1.2.10
langgraph-checkpoint 4.1.1
langgraph-prebuilt 1.1.0
```

工作流使用 LangGraph 的异步入口 `ainvoke()`，内部还使用 `asyncio.gather()` 和 `asyncio.Semaphore` 并发运行 Research Agent。

## 3. 工作流结构

发生问题的图不是简单的单向 DAG，而是包含条件路由和补检回边：

```text
START
  ↓
extract_points
  ↓
plan
  ↓
parallel_research
  ↓
validate_evidence
  ↓
assess_coverage
  ├─ supplement → plan_supplement → parallel_research
  └─ synthesize → synthesize_report → END
```

图中大部分节点原本已经是异步函数：

```python
async def _extract_points(...)
async def _plan(...)
async def _parallel_research(...)
async def _validate_evidence(...)
async def _plan_supplement(...)
async def _synthesize_report(...)
```

但覆盖评估和条件路由仍是同步函数：

```python
def _assess_coverage(...)
def _route_after_assessment(...)
```

因此实际运行模型是“异步图 + 异步节点 + 同步节点/路由 + 条件回边”。LangGraph 需要把同步 callable 调度到线程执行，再将结果送回异步事件循环。

## 4. 实际症状

### 4.1 工作流测试

执行：

```bash
python -m pytest tests/test_workflow.py -vv -s
```

测试收集正常，但停在第一个完整流程用例：

```text
tests/test_workflow.py::test_demo_runs_total_divide_total_flow
```

等待 45 秒仍不返回，外部 `timeout` 最终给出：

```text
exit=124
```

### 4.2 API 测试

全量测试最初停在：

```text
tests/test_api.py::test_novelty_health_and_run_lifecycle
```

API 服务最终调用同一个 `NoveltyWorkflow.arun()`，所以它表现为 API 请求一直不结束。

### 4.3 没有业务异常

这个问题没有产生 Pydantic 校验错误、模型错误或 LangGraph recursion limit 错误。主线程堆栈显示事件循环处于等待状态，另有线程池工作线程存在。

节点级事件跟踪得到：

```text
EVENT ['extract_points']
EVENT ['plan']
EVENT ['parallel_research']
EVENT ['validate_evidence']
EVENT ['assess_coverage']
EVENT ['synthesize_report']
```

也就是说，正常路径上的最后一个业务节点已经执行，但异步图调用没有完成收尾并把最终状态返回给调用方。

## 5. 排查和排除过程

### 5.1 API Key 缺失不是本次原因

最先阻塞的是使用 `DemoCoordinator`、`DemoPointExtractor` 和 `DemoResearchAgent` 的测试。Demo Agent 是本地确定性实现，不访问模型 API，因此 API Key 缺失不会导致该测试等待。

真实模型缺少 API Key 时，客户端也会立即抛出 `ModelClientError`，而不是无限等待。

### 5.2 arXiv 网络不是本次原因

默认配置为：

```json
{
  "tools": {
    "arxiv": {
      "enabled": false
    }
  }
}
```

Demo 工作流没有注入 arXiv 搜索、全文和元数据工具，因此不存在网络请求等待。

### 5.3 PDF 处理不是本次原因

`test_workflow.py` 直接在内存中构造 `PaperInput`，不读取 PDF。PDF 处理 CLI 也已单独成功生成结构化论文 JSON。

### 5.4 查新点提取与持久化已经完成

超时运行期间产生了：

```text
output/novelty_points/paper-test.points.json
```

这说明 `extract_points` 节点和本地持久化均已完成，阻塞并非发生在图启动前。

### 5.5 补检业务条件不是无限循环

第一个 Demo 测试会为每个查新点生成有效证据，`coverage_gaps` 应为空，因此路由直接进入 `synthesize_report`。事件跟踪也确认已经运行到 `synthesize_report`，不是 `rounds` 未递增造成的业务补检死循环。

## 6. 最小复现结论

排查时构造了一个只包含 `rounds` 字段的最小 LangGraph：

```text
START → start → assess
                   ├─ again → supplement → assess
                   └─ done → END
```

在受限执行环境中得到以下结果：

| 图的执行方式 | 结果 |
| --- | --- |
| `ainvoke()` + 条件回边 + 同步/异步 callable 混用 | 超时，不返回 |
| `ainvoke()` + 条件回边 + 全部 callable 异步 | 正常返回 |
| `invoke()` + 同步 callable | 正常返回 |

该最小复现不包含项目业务逻辑、模型、网络、PDF、持久化或 Pydantic 复杂结构，因此问题范围被缩小到异步图、回边和同步 callable 的组合及其线程调度/收尾过程。

## 7. 根因边界

能够确认的是：

1. 项目用 `ainvoke()` 运行一张含回边的异步图；
2. 图中混入同步节点和同步路由时，当前受限运行环境里异步执行器无法完成收尾；
3. 把这些 callable 全部改为异步后，工作流立即恢复；
4. 工作流专项测试和全量测试随后全部通过。

还需要谨慎说明：这不能仅凭现有证据断言为所有环境下的 LangGraph `1.2.10` 通用缺陷。排查同时发现，受限沙箱对线程/事件循环交互有明显影响：一个不包含项目代码的最小 FastAPI `TestClient` 在沙箱内也会卡在启动线程，而在正常运行权限下立即完成。

因此本问题的准确表述是：

> 当前 LangGraph 版本、异步循环图、同步 callable 线程调度和受限执行环境共同触发了结束阶段阻塞；项目通过消除图内不必要的同步/异步混用，规避该触发条件。

## 8. 评估过的解决方案

### 8.1 方案 A：把整个工作流改为同步 `invoke()`

优点：

- 最小同步图可以正常结束；
- 实现表面上简单。

缺点：

- Research Agent 已支持异步实现；
- 并发调研使用 `asyncio.gather()` 和 `Semaphore`；
- FastAPI 服务本身是异步应用；
- 强制同步会损失并发能力，并需要重新设计异步 Agent 的调用方式。

结论：不采用。

### 8.2 方案 B：降级或锁定 LangGraph 版本

优点：

- 如果旧版本不存在该触发条件，可能无需修改代码。

缺点：

- 项目没有记录开发时实际通过的精确版本；
- 仅降级不能解决执行模型混杂的问题；
- 可能引入其他兼容性变化；
- 依赖环境变化后问题可能再次出现。

结论：不作为首选修复。后续仍建议通过锁文件固定验证过的依赖组合。

### 8.3 方案 C：删除补检回边

优点：

- 把图变成单向 DAG，可能避开触发条件。

缺点：

- 自动补检是查新工作流的核心功能；
- 属于为了运行时问题删减业务能力。

结论：不采用。

### 8.4 方案 D：将剩余同步节点和路由改为异步

优点：

- 保留现有业务图和补检能力；
- 与 `ainvoke()`、FastAPI 和异步 Research Agent 的执行模型一致；
- 改动范围小；
- 覆盖度计算本身不变；
- 最小复现和正式工作流都验证有效。

缺点：

- 两个函数内部当前没有真正的 I/O，使用 `async def` 是为了调度一致性，而不是因为计算本身必须异步；
- 仍应通过依赖锁定和不同运行环境测试防止未来回归。

结论：采用。

## 9. 最终修改

修改前：

```python
def _assess_coverage(self, state: NoveltyState) -> dict[str, Any]:
    ...

def _route_after_assessment(self, state: NoveltyState) -> str:
    ...
```

修改后：

```python
async def _assess_coverage(self, state: NoveltyState) -> dict[str, Any]:
    ...

async def _route_after_assessment(self, state: NoveltyState) -> str:
    ...
```

业务逻辑没有改变：

- 覆盖度仍按每个查新点的有效证据数量计算；
- `coverage_gaps` 为空时仍进入报告汇总；
- 有缺口且未达到 `max_rounds` 时仍进入补检；
- 达到最大轮次后仍强制进入报告汇总。

## 10. 验证结果

### 10.1 工作流专项测试

```text
tests/test_workflow.py
8 passed
```

覆盖内容包括：

- 正常总—分—总流程；
- 缺少英文查新点的降级警告；
- Research Agent 并发执行；
- 无来源证据拒绝；
- 证据不足触发补检；
- 达到最大轮次后停止；
- 单个调研任务失败隔离；
- 单张畸形证据卡隔离。

### 10.2 全量测试

在正常运行权限下执行：

```text
127 passed, 6 skipped in 3.99s
```

6 个跳过项是需要真实网络或模型配额的 `live` 测试，不是失败。

### 10.3 真实模型验证

完成 API Key 安全配置后，SiliconFlow 冒烟测试通过：

```text
模型：deepseek-ai/DeepSeek-R1-0528-Qwen3-8B
测试：1 passed
```

这项测试用于确认模型凭据和模型客户端可用，与本 Issue 的 LangGraph 阻塞根因相互独立。

## 11. 后续建议

1. 为 LangGraph、Checkpoint、Prebuilt、FastAPI、Starlette、AnyIO 和 HTTPX 建立锁文件，保存已经验证的组合。
2. 增加工作流级超时，避免未来节点或第三方服务异常时无限等待。
3. 为节点增加结构化开始/结束日志，至少记录 `paper_id`、节点名、轮次和耗时。
4. 在 CI 中保留工作流闭环和补检回归测试。
5. 将外部网络 `live` 测试与离线测试分开运行，并为 live 测试设置明确超时。
6. 后续新增 LangGraph 节点时，在使用 `ainvoke()` 的图中优先保持 callable 全异步，尤其是包含回边时。
