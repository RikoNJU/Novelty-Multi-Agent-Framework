# Configuration Management 审查与首轮实现

日期：2026-09-27。范围：实际 typed loader/factory、模型客户端、Full/PaperInput/Single Task 入口与 Runtime。未修改用户已有的本地 LLM 手册。

## 证据与验证

| 现象 | 原因 | 验证与处理 |
|---|---|---|
| `effective_safe_config` 会输出嵌套 Provider `api_key` | 只白名单处理模型段，其余开放字典直接输出 | 用 `SYNTHETIC_AUDIT_SECRET` 复现，见 `config_before.json`；现在递归脱敏，覆盖 credential/header/URL userinfo/签名参数，测试不使用真实密钥 |
| 加载后将 `max_rounds` 设为 0 不报错 | Pydantic 默认不校验赋值，CLI加载后直接修改字段 | CLI改为加载时传入覆盖；snapshot与typed factory构建时重新校验，拒绝绕过 |
| 未知 Provider 在加载阶段被接受 | `providers` 是开放字典，只有运行构建时检查来源 | 新离线 preflight 检查 registry 名称、正式启用状态、必要凭据；不把“有凭据”解释成在线可用 |
| 实验没有统一单文件 Profile/来源解释 | 分片文件、env与入口常量并存 | `load_application_config(profile_path=..., overrides=...)`；逐字段来源、源文件hash、显式优先级 |
| CLI默认预算悄悄覆盖实验设置 | argparse固定默认值后再次赋值 | 未提供CLI值时沿用已解析配置；显式CLI值最后覆盖并校验 |
| 修改Prompt正文但版本字符串未变不易复现 | 旧快照只保存Prompt名 | Manifest保存整个实际Prompt目录的SHA-256（包含硬编码调用的Prompt），同时记录代码commit、dirty和Python源码内容指纹 |
| Single Task Runtime只保存少量模式字段 | 诊断入口没有注入完整typed config | 现在归档实际配置、Manifest与原始输入hash |
| 本地API可访问，但模型客户端仍要求非空key | 客户端认证约定与无鉴权vLLM不同 | `preflight-missing-local-credential.json`保留5角色缺失凭据证据；按手册设 `LOCAL_VLLM_API_KEY=local` 后预检通过；没有读取/输出真实secret |

## 优先级与可复现边界

`schema defaults < split files < profile < supported environment overrides < explicit overrides/CLI`。
对象递归合并，数组/标量整体替换；拼错typed字段立即失败。Profile中的Provider对象为合并语义，所以单Provider实验应显式禁用其他Provider。

`NOVELTY_EXPERIMENT_PROFILE` 为所有调用统一loader的入口提供Profile选择。PaperInput、Single Task另支持 `--profile`。`--isolated-config` 忽略配置环境覆盖，凭据仍由正常环境变量解析；它不关闭网络代理或修改Provider客户端实现。未传 `--isolated-config` 时，已有 `NOVELTY_SPRINGER_ENABLED=true` 会覆盖Profile中的false，此结果会记录为environment来源。

`effective-config.json`保持完整ApplicationConfig形状；`experiment-manifest.json`记录入口、输入hash、有效配置hash、每字段来源、Prompt文件hash、源码指纹。typed factory同时把Manifest注入Runtime配置；直接修改已加载配置会在快照标为runtime_override，实际输出目录标为runtime_output_root。API Key值不参与公开指纹，避免可推导凭据的实验归档；Credential变化仍可能影响授权条件，所以复现前必须重新预检/在线探测。

代码处于dirty状态时，commit本身不足以重建本次运行。本实验包另保存本轮实现patch；Python指纹用于检查代码一致性，不能替代依赖锁文件、外部服务版本、Provider数据时间或GPU推理确定性。

## 使用

仓库提供 `config/profiles/local-baseline.json`、`local-reader-reuse.json`、`remote-baseline.json`。前两者仅Reader缓存开关不同；远端Profile仅作为显式切换示例，本轮没有执行远端LLM。

```bash
export LOCAL_VLLM_API_KEY=local
python scripts/inspect_config.py \
  --profile config/profiles/local-reader-reuse.json --isolated-config \
  --output outputs/config-review.json

python scripts/run_full_workflow_live.py \
  --paper-json outputs/local-llm-full-workflow/0002/paper-input.json \
  --profile config/profiles/local-reader-reuse.json --isolated-config \
  --runs-root outputs/harness-config-audit --check-config
```

去掉 `--check-config` 执行；可显式追加 `--max-rounds`、`--max-concurrency`、`--max-model-calls`、`--max-physical-provider-requests`。未经指定的CLI预算现在采用配置值，原脚本的固定1轮/1并发默认不再覆盖项目2轮/4并发；本轮示例Profile显式冻结1轮/1并发。

`python scripts/run_single_research_task.py --paper-json ... --point-id NP-1 --task-id T-1 --profile ... --isolated-config`仍要求既有任务/计划产物，未把它伪装成任意输入的自动规划入口。

## 明确尚未完成

- Coordinator/PointExtractor的历史 `prompts` 列表仍不控制实际硬编码Prompt名；预检显式warning，不能宣称任意Prompt切换已完成。应后续迁移为按操作命名的字段，而不是依赖列表顺序。
- `supported_params`只表达厂商额外参数白名单，尚不足以表达工具调用、JSON格式、thinking组合和上下文Tokenizer能力。启用但将被静默过滤的thinking参数已在预检报错。
- Context预检仅证明输出额度小于窗口，未证明系统Prompt、工具schema、历史消息和输出预留总和可容纳；精确准入仍需运行时token计数。
- 新 preflight 覆盖 inspect/PaperInput/Single Task；其余入口共享loader和typed factory快照/再校验，但不声称全部Web/PDF/legacy入口已执行同一凭据与能力预检。
- Full PDF入口仍可能调用processing OCR角色（默认远端），本轮只跑PaperInput/固定任务，不触发OCR。模型角色切换不等于所有底层计算能力都已本地化。
- Provider内部配置仍为开放字典，认证状态/配额/全文授权仍需Capability Registry；回退顺序与策略消融还没有统一表达。
- 旧兼容factory仍读取部分环境变量，Web部署设置有独立env类；本轮不做无证据的大规模删除。`NOVELTY_TIMEOUT_SECONDS`及Provider transport环境来源需要下一步统一归集。
- 没有新增GPU成本估算；Token usage、API估价和本地计算成本保持不同概念。

结论：建立了可用的Profile与审计基础，未声称完整配置治理已终结。

## 交叉审阅补充

最终交叉审查另复现并修复：字符串 `enabled="false"` 被truthiness当启用（预检拒绝）；Springer OA/TDM凭据漏检及IEEE默认env名误报（按真实构造契约检查）；未调用角色阻断Single Task（按active_roles校验）；Single Task真实预算/工作目录与Manifest不一致（统一注入）；真实TaskResearchRequest和来源文件未冻结（补hash）；运行时新增字段未标来源（补runtime_override）；URL `sig`以及无效配置Pydantic异常带input_value泄漏（成功/失败路径均脱敏，配置异常隐藏输入）。这些回归使用虚构值，不含真实密钥。

Manifest也记录Python与关键包版本；仍不是完整依赖锁或远端服务镜像。错误类别、Provider内部所有数值字段及所有入口的统一预检仍需后续收敛。
