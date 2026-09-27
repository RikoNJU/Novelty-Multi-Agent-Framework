# Reader / Researcher 六样本本地重复验证

日期：2026-09-28。结论：在一个固定真实历史任务的更紧预算下，`reuse_reader_results` 开关两组均为每次 5 个模型请求、4 次实际读取、0 次缓存回放、0 张证据卡、partial。没有观察到模型调用或物理 I/O 次数减少。开启组减少了重复返回字符，但有一次改读了另一篇摘要，跨样本轨迹并非完全稳定；不能据此宣称通用效率或语义效果改善。

## 固定条件与边界

沿用 `continued/replay_reader_local.py` 的历史任务 `MF2033k6lC / NP-1 / T-1`、原 `0002_database_search` 候选和原 workspace 字节。真实候选包括 *A Survey of Link Prediction in Temporal Networks*、*Graph Neural Networks (GNNs)*、*Graph neural networks: Historical backgrounds, present revolutions, and conventionalization for the future* 等。原候选共 8 篇，全部 `metadata_only`，实际读取材料 role 均为 `abstract`。没有合成语义材料，没有把整个摘要读完称为论文全文覆盖。

模型 `qwen2.5-7b-instruct`，本地 `127.0.0.1:8000/v1`，temperature=0、max_tokens=2048、timeout=120、profile context_window=32768。只注册 Reader；无检索工具、无外网/云端模型调用。组间唯一区别是 `reuse_reader_results`，`runtime_state_projection=false`、checkpoint=false、ContextAdmission=off，保持原 Reader 探针开关边界。所有六次**实际设置去掉该 flag 后完全相同，首次发送 payload 也完全相同**，见 `reader_local_repeated/consistency.json`。

共同探索 max_steps=4、max_tool_calls=4、Reader 单次最多 16000 字符/总计64000、reader 次数上限4；每样本 Runtime 模型上限6，另有独立实际 HTTP 发送守卫：每样本6、整个实验36，只接受本地 chat endpoint。finalization/格式修复/quote correction 都算在该硬限内。实际只用了 30 次，30 次均有原始 provider usage。执行顺序 off_1、on_1、on_2、off_2、off_3、on_3。

该预算相对原 continued 探针的 max_steps=10 / max_tool_calls=8 降低，**这是新条件，不能直接比较原 10→6 的调用差异**。每组仅3次、一个任务，temperature=0也不保证服务器位级确定性，结果只作描述性重复观察。

## 可执行源码与实验偏差

启动前使用 `prepare_startup` 保存当前生产源码、prompts、有效配置、原历史输入、整个 workspace 和实验 runner 字节，并从 `reader_local_repeated/startup/source` 导入执行；没有从继续变化的工作树导入生产模块。source tree SHA256：`d75ed1c57522aa17c9f15d6348e70eaf0e5cc62d4de4339f61ce24a8dd13ce16`。运行前各样本及全部结束后验证 snapshot 均通过。

off_1 已完成5次推理并保存 stage output、5条 llm_calls 和4条工具记录后，**实验 runner** 错将业务 partial 传给只接受 SUCCESS/FAILED/INTERRUPTED 的 `finish_run`，继而错误地传入 dict 作为 error，导致收尾异常。未重复 off_1；从原始已保存记录重建其统计，既有5次仍计入总36硬限。原冻结 runner / 失败日志未改写。`runner_v2.py` 只改实验记录收尾及断点恢复，不改条件、消息、预算、fixture 或生产源码；两版边界和新 SHA 在 `resume_note.json`。原 off_1 缺独立 Harness trace sidecar/正常 run summary，完整模型 request/response、工具 observation 和研究 stage output 均保留，统计使用这些原记录。

该偏差记录在对照中，未以成功样本替换；不能将 runner 收尾异常当成模型推理失败，也不能掩盖研究本身因预算终止的 partial。

## 逐样本结果

| 样本 | 模型请求 | 物理读 / replay | 唯一摘要数 | 返回字符 / 唯一字符 | 重复或重叠字符 | 输入 / 输出 token | 卡 | 秒 |
| --- | ---: | --- | ---: | --- | ---: | --- | ---: | ---: |
| off_1 | 5 | 4 / 0 | 3 | 4530 / 3026 | 1504 | 32660 / 207 | 0 | 25.129 |
| off_2 | 5 | 4 / 0 | 3 | 4530 / 3026 | 1504 | 32660 / 207 | 0 | 12.051 |
| off_3 | 5 | 4 / 0 | 3 | 4530 / 3026 | 1504 | 32660 / 207 | 0 | 12.069 |
| on_1 | 5 | 4 / 0 | 4 | 4112 / 4112 | 0 | 32926 / 233 | 0 | 22.554 |
| on_2 | 5 | 4 / 0 | 3 | 3325 / 3026 | 299 | 32795 / 228 | 0 | 19.615 |
| on_3 | 5 | 4 / 0 | 3 | 3325 / 3026 | 299 | 32795 / 228 | 0 | 13.254 |

全部样本4次 Reader 返回成功，无参数非法/工具失败、无空 EOF 物理读取；这些成功调用中仍有重复内容。token 为 provider 实际 usage，字符数则为 Reader 原文字数，两者不混用。时间仅为研究 stage 墙钟，受服务状态/缓存等影响：均值 off 16.416 秒、on 18.474 秒，不支持加速结论。

- off 三次都重复完整读取 `art_8eb173b983f525f0fa01d20d [0,1504)`，第4次无新增覆盖。
- on_1 第4个不同 artifact 为 `art_1880aaf2419e313e395501ad [0,1086)`，多读一篇摘要。
- on_2/on_3 已读取 `[0,1504)` 后请求同 artifact `[1205,4205)`，实际返回 `[1205,1504)`，全部299字符已覆盖。它是合法重叠范围，现规则有意允许回读，不能为了“消除重复”无条件屏蔽。

本实验没有触发 exact-request replay 或已知尾部之外的 EOF replay；观察到的是 Reader 状态提示后的模型动作差异，不是缓存命中减少 I/O 的证明。离线回归覆盖的机械缓存收益与此处实测必须区分。

最终六次均保留预算终止失败事件及 no_evidence_reason。部分材料未读、均无全文、最终0cards，不能解释为“已验证无匹配文献”或“查新已完成”；也不能仅以0cards断言模型错误，因为允许无充分证据时保守不产卡。本实验没有进行 Validator/Reviewer 判定或全文语义金标准评价。

## 证据和离线复查

- `reader_local_repeated/{off_1,on_1,on_2,off_2,off_3,on_3}.json`：逐样本结果、warning、原读范围和完整研究输出。
- 各条件 `MF2033k6lC/runtime/<label>/{llm_calls,tools,stages}`：真实请求/响应/usage、原读文本和业务状态。
- `reader_local_repeated/{experiment_plan,validity,consistency,physical_dispatches,resume_note}.json`：预先预算、独立请求计数、只改一项验证、快照校验和 runner 偏差。
- `reader_local_repeated.log` / `reader_local_repeated_resume.log`：原失败与续跑日志。
- `reader_local_repeated/startup/manifest.json`：源码/输入/配置逐文件哈希；`startup/inputs/runner.py` 和 `runner_v2.py` 保存实际执行的实验脚本版本。

无需新模型调用的复查命令：

```bash
/home/lya3106643285/miniconda3/envs/Novelty-web/bin/python docs/experiments/20260927_harness_config_closure/analyze_reader_repetitions.py
```

新执行应使用新的输出目录和独立预算，不能覆盖或自动重跑本次数据。
