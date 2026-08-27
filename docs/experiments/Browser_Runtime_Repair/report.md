# Browser Runtime 修复实验报告

## 结论

Browser runtime 修复通过。当前宿主缺少 Chromium 所需的系统级 NSPR、NSS
和 ALSA 动态库，且 `playwright install-deps chromium` 因无 sudo 交互权限未能
安装；实现按三层策略自动选择了 Conda 环境库的子进程 fallback。未手工或全局
导出 `LD_LIBRARY_PATH`，Chromium 启动、本地 HTML、公网静态页和真实
Browser → Artifact → Reader 均通过。

原 Single-Pass Prompt Pretest 在门禁通过后以原 Prompt 重跑。获取层达到 PASS：
6 个任务中 4 个生成 Artifact 并完成 trusted Reader read；但整体并非完整跑通，
因此不继续全栈 demo，待接入 reviewer 后再执行完整 demo。

## 安装问题与三层策略

官方命令 `playwright install-deps chromium` 会调用系统包管理器并需要管理员权限。
本机尝试停在 sudo 密码要求，故没有改变系统包。诊断确认系统 loader 缺少
`libnspr4.so`、`libnss3.so`、`libnssutil3.so`、`libasound.so.2`，而当前 Novelty
Conda 环境的 `lib/` 中四者完整。

运行时现在采用以下决策：

1. 系统 loader 可解析全部库：正常路径，直接启动。
2. 系统缺库、当前 Python 环境库完整：兼容路径，仅给 Chromium 子进程设置库
   搜索路径；父进程和项目全局环境不变。
3. 两边均不完整：失败路径，在启动前抛出 `BrowserDependencyError`，明确提示
   部署时运行 `playwright install-deps chromium`。

Conda fallback 是开发环境兼容措施，不替代部署镜像中的官方系统依赖安装。

## 网络与安全

- `network_mode=inherit` 默认按 `HTTPS_PROXY`、`https_proxy`、`HTTP_PROXY`、
  `http_proxy` 优先级解析宿主出口，并把 `NO_PROXY/no_proxy` 转为 bypass。
- `network_mode=direct` 即使宿主存在代理变量，也不会向 Playwright launch options
  传入 proxy。
- 当前宿主检测到 HTTP 代理并成功显式传给 Playwright；报告和结构化结果只记录
  “已配置”、scheme 与脱敏 host，不含完整 URI、端口、用户名或密码。
- Browser 的 public URL/SSRF 校验保持原样；没有加入关闭 Chromium sandbox 的
  自定义参数，也没有把代理信息暴露给 LLM。

## 零模型验证

| 验证项 | 结果 |
|---|---|
| Playwright import / Chromium executable | PASS / PASS |
| Chromium launch / context / page | PASS / PASS / PASS |
| 本地 HTML render | PASS |
| `inherit` 宿主代理解析 | PASS（内容已脱敏） |
| 公网 `https://example.com/` | PASS，HTTP 200 |
| dependency mode | `environment_fallback` |
| Browser smoke | 3/3 success |
| SourceRecord → Browser → Artifact → Reader | PASS |
| 模型 API 调用 | 0 |

真实工具链成功读取静态页、JavaScript 渲染页和 WebSearch 候选页，均生成
`extracted_text` Artifact，Reader 使用对应 `artifact_id` 读取可信文本。

## Single-Pass Prompt Pretest 复跑

首次复跑完成模型和工具阶段后，在汇总阶段因实验脚本仍读取已迁移出
`docs/experiments` 的旧 JSON 路径而失败。修正对照输入为
`outputs/experiments` 后，以未修改的实验 Prompt 再次完整运行。

最终结果：

- acquisition：PASS；Browser success 4/6，Artifact 4/6，trusted read 4/6，
  共读取 22,865 字符。
- behavior path：FAIL；严格单次序列 2/6，存在重复 search/read 行为。
- NP-3/T-1：模型调用失败，未进入 Browser。
- NP-3/T-2：目标页面两次导航超时，未生成 Artifact。
- grounded card：0；唯一草稿卡包含非逐字 quote，被 EvidenceCardBuilder 正确拒绝。
- 本轮 Researcher token 总计 242,037。此前一次因末尾路径错误而失败的真实调用
  也实际发生，不计为成功实验，但不可视为零成本。

这证明 Browser 基础设施不再统一报 `TargetClosedError`，但 Prompt 遵循度、站点
可访问性和证据质量仍需后续 reviewer/full-demo 阶段处理。

## 回归与产物

相关回归测试 52 项全部通过，覆盖 WebSearch、BrowserTool、ReferenceStore、
Reader、EvidenceCardBuilder、Harness、Config loading 及新增 runtime resolver。

报告保存在 `docs/experiments/Browser_Runtime_Repair/report.md`。预检 JSON、实验
summary、trace、manifest、Artifact 与 Reader 输出均按目录策略保存在
`outputs/experiments`，不放入文档目录。
