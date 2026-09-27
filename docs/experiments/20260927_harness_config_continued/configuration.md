# 配置管理续查：实际 Prompt 选择与显式 Harness 能力

本轮在首轮 Profile/来源/快照机制上继续收敛实际执行入口。首轮报告和已完成实验的快照保留不动。

## 已实现

1. Coordinator 的 `prompt_names.supplement`、`prompt_names.synthesize`，PointExtractor 的 `prompt_names.generate`、`prompt_names.deduplicate`、`prompt_names.coverage` 直接绑定对应模型请求。默认名称沿用原先实际使用的模板，不改变提示语义。模板清单 `prompts` 保留兼容：已知旧清单给迁移警告；自定义旧名称给预检错误，避免写了自定义 Prompt 却静默执行默认版本。
2. `selected_prompts` 将每个角色/操作的模板名称、front matter version、文件 SHA-256 写入 manifest。原有整个 Prompt 目录 hash 保留；未使用的模板与本次真正选择的模板可分别解释。缺文件和越出 Prompt 根目录的选择在预检失败。
3. 模型 Profile 增加 `context_admission`，Researcher Harness 增加 `enable_evidence_checkpoint`。类型校验、factory、legacy 形状、安全快照及实际 TaskResearcher 均接通。默认均关闭，显式实验才能改变动作/网络测量空间。
4. `scripts/inspect_config.py --entrypoint single_task` 仅对实际 Researcher 角色预检模型/Prompt，不要求闲置角色的凭据；数据库工具本身的配置仍检查。

## 增强实验配置

[`config/profiles/local-harness-guarded.json`](../../../config/profiles/local-harness-guarded.json) 是可复用示例，使用本地 Qwen、1 轮、1 并发、40 次模型调用、12 次物理 Provider 请求、仅 arXiv，关闭 web/browser，开启 Reader 状态/复用及 Evidence 检查点。

模型配置如下：

```json
{"context_admission": {
  "mode": "enforce", "counter": "vllm", "on_unavailable": "reject",
  "vllm_tools_mode": "v0_8_5_kwargs", "timeout_seconds": 5.0,
  "tokenize_path": "/tokenize"
}}
```

`v0_8_5_kwargs` 是显式、版本受限的兼容模式。本机 vLLM 0.8.5.post1 的 `/tokenize` 请求 schema 没有 `tools` 字段，直接发送会被忽略；此模式通过 `chat_template_kwargs.tools` 使用同一模板路径，并检查服务版本和参数默认值。本轮已对 Reader 对照实验全部 16 次真实请求做输入计数与 usage 对账，逐条一致。默认 `native` 不会自动启用此兼容方式。服务更新或不支持某项提示模板参数时会拒绝声称精确计数，详见上下文报告。

每次真实调用在发送 chat 请求前测量完整序列化消息、工具 schema、历史和显式输出预留。超过有效窗口或无法精确测量时拒绝并记录；不截断输入、不用字符数冒充 token、不新增模型生成预算来“估算”。`observe` 仅记录不拦截；`on_unavailable=allow` 明确放行未知，两者不能称为严格保护。

`enable_evidence_checkpoint` 将 `submit_evidence` 加入该 invocation 的工具集，改变动作空间并消耗普通工具预算。模型决定提交什么语义草稿，Builder 决定是否满足原有引用来源契约。已保存草稿仍需下游 Validator/Reviewer，不等价于正式结论。默认关闭便于独立消融。

离线检查命令（不发起模型或检索请求）：

```bash
LOCAL_VLLM_API_KEY=local PYTHONPATH=backend/src:. \
  /home/lya3106643285/miniconda3/envs/Novelty-web/bin/python scripts/inspect_config.py \
  --profile config/profiles/local-harness-guarded.json --isolated-config \
  --paper-json outputs/local-llm-full-workflow/0002/paper-input.json \
  --output /tmp/novelty-guarded-config.json
```

[归档预检](guarded-config-manifest.json) 为 0 error / 0 warning。离线预检不能替代服务连通性/分词协议验证或 Provider 授权可用性验证。

## 验证与边界

`tests/test_operation_prompt_config.py` 通过真实 factory 构建角色，给每个操作替换带唯一标记的模板，检查生成、去重、补核、补检、综合各次真实消息构造，而非只检查配置对象字段。另覆盖所选文件哈希、遗留自定义清单、缺失模板、兼容字段接线、非法路径/超时/模式。

服务恢复后已经完成的 `full_live_profile.json` 和 Reader off/on 实验均未开启新 Context guard 或 Evidence checkpoint；不将其结果记作这些功能的完整流程验收。新配置的守卫探针和检查点探针分别归档，不能合并成“增强配置已端到端成功”。

本轮仍未统一全部 Web/历史脚本入口的 preflight，也未实现通用模型能力协商、任意服务 tokenizer 或完整部署配置迁移。显式 named Prompt 的五个操作解决已发现的绑定缺口，不代表所有历史兼容代码已经删除。
