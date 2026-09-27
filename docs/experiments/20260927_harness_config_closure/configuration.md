# 配置入口、能力与启动快照闭环

记录日期：2026-09-28。此项修改和验证不调用论文 Provider、模型或 tokenizer 服务；只读取一次公开 SiliconFlow 官方能力文档。旧 live run 及其 manifest 未改写，本轮测试不能追溯证明旧 full live 的源码可精确重建，也不是新配置的在线 E2E。

## 修前证据与修复

`configuration_before.json` 是用虚构环境值离线复现的原行为：`load_application_config(environ={})` 后设置 `NOVELTY_TIMEOUT_SECONDS=123`，真实 registry 仍读到 123，但冻结模型配置没有 timeout；预检漏查 processing OCR 凭据；profile 没有 tools/JSON 能力声明；源码只有 fingerprint，没有内容。

| 项目 | 当前行为 | 验证范围 |
| --- | --- | --- |
| 有效超时及来源 | profile timeout 默认为 60 秒，环境超时在 loader 的统一优先级层处理；显式 override 最后；typed registry 不再次读取环境超时 | 虚构 123/456 环境值验证隔离、覆盖顺序、registry 与 manifest 一致 |
| 角色调用参数 | typed 与 legacy projection 的 Coordinator、PointExtractor 保留 max_tokens、timeout、thinking 等选项；legacy timeout/alias 实际来源进入 configuration_resolution | 对比实际 Agent 的 ModelCallOptions；旧低层构造接口保留 |
| 模型能力 | 每个 deployment 明确声明 tool_calling、json_object、vision 为 true/false/null，tool_choices 单独列出；unknown/unsupported 必需能力和不兼容 tool_choice 在正式启动前报错 | 未从 provider 名称或本地接口形状推断兼容性 |
| processing | PDF 入口检查实际可进入的标题模型和 OCR 回退；ocr_fallback_enabled 默认为 true，false 时既不预检 OCR，也不实例化 OCR client | MinerU 失败/质量不足后确会进入 textify，文本层不足可调用 OCR；不把这个可能路径误认为从来不会使用 |
| Provider 回退 | recovery_provider_order 默认空；仅允许已注册、已开启且非 testing_only 的来源，不允许重复 | 不自动开启、不追加未经授权的 Provider |
| 其他新开关 | conservative_dedup、runtime_state_projection、reuse_reader_results、enable_evidence_checkpoint 同时进入 typed/legacy 实际构造 | 保守去重默认开启；projection/reuse/checkpoint 默认关闭；行为实现由其他分项验证 |
| 源码快照 | 外部请求前写运行隔离目录；保存执行源码、提示词、模板、技能、依赖声明、价格表、脱敏有效配置、已知输入；逐文件 SHA-256 与整体校验；不保存 .env | 可在独立进程从归档源码重建配置/registry/workflow，见 configuration_rebuild.log |

统一预检检查凭据是否存在，不把凭据存在、文档声明或历史成功当成当前服务授权/可用性验证。上下文预算仅声明 window 仍不足以保证安全：原有 exact counter/enforce 检查和警告继续保留。环境记录包含 Python、平台、已安装包版本、tokenizers/transformers/tiktoken/vllm 版本；远端模型服务器/tokenizer 版本显式 `not_probed`，不借客户端版本冒充服务器版本。

## 能力声明依据

- 本地 `qwen2.5-7b-instruct`：历史真实成功请求/响应证明 tools、auto/none、json_object。原始路径保存在 `model_capability_evidence.json` 及 models.example.json 的 evidence 字段。
- SiliconFlow `deepseek-ai/DeepSeek-V4-Flash`：2026-09-17 归档同样有 tools、auto/none、JSON 成功证据；本轮未调用。
- SiliconFlow DeepSeek-OCR 的 vision：2026-09-28 读取[官方多模态输入文档](https://docs.siliconflow.cn/docs/userguide/capabilities/multimodal-vision)，其模型表及请求说明明确支持 DeepSeek-OCR 图像/base64 输入。配置标记为官方 deployment 声明、非 live 验证；未发送论文图片或云模型请求。
- GLM-4.7、官方 DeepSeek flash、R1-Qwen3 以及其余未证实能力保持 null。将这些 profile 切到需要 tools/JSON 的角色时，会得到具体角色/能力路径的预检错误，需先提供该部署的明确能力声明与验证证据。

## 正式入口覆盖

| 入口 | 预检及快照位置 |
| --- | --- |
| build_standard_full_workflow | Reviewer 原异常契约先检查，再统一预检；默认在 output_root/.startup/<uuid> 留内容快照；已准备的同配置快照可复用 |
| run_full_workflow_live.py | 保存 preflight/有效配置；实际运行在编号目录 startup 中冻结源码和 PaperInput，再构造 workflow、再 reference bootstrap；check-config 不执行工作流 |
| run_single_research_task.py | 仅 researcher 角色，不要求未用角色或 processing；在 output_root/.startup/<run_id> 保存实际 TaskResearchRequest 和消费的 point/plan 源文件字节 |
| web.runner.execute | PDF 处理/模型 client 构造之前检查完整角色及 processing，并保存 PDF 与源码；使用配置 parser，OCR 禁用开关实际生效 |
| build_real_workflow_service / execute_file | 建服务时统一完整预检；每个 run 在处理 PDF 前构造/冻结工作流。服务建成后源码若改变，拒绝启动新 run，要求重启，避免共享 processor 与新源码混合 |
| inspect_config.py | 复用同一预检；single_task 仅 researcher；full_workflow/web_pdf 包含 processing；纯离线，不触发工作流 |

历史独立实验脚本和通用 `build_workflow(mapping)` 仍可作为低层/离线组合工具使用；它们不是新的正式完整启动门禁。legacy 映射来源已补超时与 invocation 一致性，但未重写所有历史脚本。

## 快照边界与重建

`prepare_startup` 创建新目录，禁止覆盖已有快照；捕获期间源码变动会拒绝启动，复用快照时配置、输入、源文件变化也会拒绝。`verify_startup_snapshot` 可不依赖当前工作树验证文件内容，篡改/额外文件/缺失文件均报错。运行 PromptLibrary 使用快照中的模板，后续仓库提示词变动不影响已构造客户端。

source 中的 Python/提示词/模板/技能/价格表/依赖声明是启动时字节。为了从快照运行正常 loader，split 配置文件由有效配置重建，不拷原始 profile 的潜在内嵌凭据；manifest 单独列出这些生成文件。完整有效配置也可直接交给 `ApplicationConfig.model_validate`。重建需要单独提供凭据环境；不会保存、复制或打印凭据值。

归档保证本仓库启动内容和配置可重建，不冻结远端模型权重/tokenizer/Provider 返回结果、外部 MinerU 环境，也不保证随机模型输出再次一致。默认 MinerU worker 在 scripts 中随源码保存；若用户配置仓库外 worker、私有包或其他外部资源，仍须独立提供相同资源。主进程从归档内容导入的离线重建已验证；正在运行中热修改执行代码不被视为受支持的复现实验方式。

## 验证产物

- `configuration_before.json` / `configuration_after.json`：修前后同类离线观测。
- `configuration_tests.log`：84 项定向回归通过（1 条既有 Starlette 弃用警告）；涵盖超时优先级/隔离、未知能力阻断、processing 与 OCR 开关、Provider 顺序、单任务范围、源码内容/脱敏/完整性、拒绝覆盖、客户端选项一致和入口时序。
- `configuration_rebuild.log`：独立 Python 进程，从归档源码导入，重建 typed config、registry 和完整 workflow；零网络/模型请求。
- `startup_snapshot/`：第一轮离线重建实例；`startup_snapshot_loader/`：随后验证普通 split loader 也可从有效配置重建的实例。其 captured_at 和逐文件 hash 是该实例的边界；不代表随后其他分项编辑的最终代码，更不能替代旧 live 的缺失 start patch。
