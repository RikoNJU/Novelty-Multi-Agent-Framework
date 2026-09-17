# Reviewer 输出契约与预算收尾实施记录

基线为 `dd74c039cc5de0065327a573f170e2be23f4386a`，实施范围限于 Reviewer、共享 Harness 的可配置收尾及固定 NP-3 脚本。未修改正文权限、检索、原 Card/Evidence 或旧否定词影子策略。

- 新增严格的 `ReviewerCardDraft`、`ReviewerSummaryDraft`。单卡提示、解析和一次格式修复使用前者；汇总提示、解析和一次格式修复使用后者。`review_evidence`、`incomplete_reason`、`read_citations`（汇总）不再出现在模型输出 schema；系统仍使用 `NoveltyPointReview` 落盘。非法系统字段记录原始响应，不静默删除。
- Reviewer 单卡使用显式的 4 次探索模型轮次加 1 次预留无工具收尾；保留 4 次 Reader、8,000 返回字符的原始对照边界。Harness 在超额读取前拒绝，返回申请量和余额，允许一次缩小；再次超额或探索上限触发 Reviewer 专用无工具收尾。旧 Researcher 默认收尾指令保持原样。
- 单卡使用同一个本地 deadline 执行探索与格式修复；预算异常按类型及异常链分类。只有合法 Draft 所引用的真实 read_id 才登记 ReviewEvidence。模型与系统输出、schema、有效预算、读取覆盖和错误轨迹进入现有 Runtime Debug。全部单卡因技术或预算原因无效时，确定性跳过付费汇总。
- 固定 NP-3 脚本默认只执行本地预检；`--live` 才可能发送模型请求。新的预检核对两张卡各自摘要、正文、Manifest 哈希、渲染提示哈希及输出 schema。Live 脚本按卡成对顺序运行；第一对出现技术／协议错误即停止第二对。调用数和费用在派发前保守检查，不重用已存在 trial 目录。

测试命令见 `tests/commands.txt`，实际输出见 `tests/pytest.log`。最终 **218项相关测试通过**，包含针对真实复验发现的汇总摘录遗漏和 Debug 空读误分类的回归。预检产物位于 `trials/preflight_v2/`；离线测试没有外部调用。

用户随后独立授权本轮 L0′/L1′；真实试验位于 `trials/np3_postrepair_pair_20260918/`。16次模型调用、Runtime估算¥0.3695712，四张单卡和两组汇总均结构合法。复核发现已登记的正文证据未进入**实际付费汇总输入**：单卡模型没有把新证据ID放在特征或相关文献引用中，旧装配器因而只发送原摘要。对此补充了离线修复和回归测试：明确选择的 ReviewEvidence 现在进入 `key_quotes`，并可被汇总引用；本次付费结果不据此追溯改写。详情见 `report.md`，语义收益仍未证实。
另修正 Runtime 对附带空 `material_catalog` 的单次非空 Reader 结果误标 `EMPTY` 的计数优先级；旧付费事件保留原样，读取字符以原始范围核对。
