"""Write the final report after all three workflows have returned."""
import json,collections,runpy,hashlib
from pathlib import Path
from datetime import datetime,timezone,timedelta
BASE=Path(__file__).resolve().parent
runpy.run_path(str(BASE/'summarize.py'))
rows=json.loads((BASE/'summary.json').read_text())
assert all(r['run'].get('status')=='SUCCESS' and r['report_exists'] for r in rows)
Z=timezone(timedelta(hours=8));now=datetime.now(Z)
def j(path):return json.loads(path.read_text())
def rel(n):return ['01_arxiv','02_arxiv_springer','03_arxiv_springer_web'][n-1]
for r in rows:
 m=j(BASE/rel(r['trial'])/'MF2033k6lC/references/list.json')
 r['artifact_roles']=dict(collections.Counter(a['role'] for a in m['artifacts']))
 r['source_access']=dict(collections.Counter((a['source_id']+':'+a['access_status']) for a in m['source_records']))
(BASE/'summary.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
batch=j(BASE/'supplementary/batch/result.json');compare=j(BASE/'supplementary/compare/result.json')
web_events=[j(p) for p in (BASE/'03_arxiv_springer_web').glob('*/runtime/*/tools/*web_search.json')]
web_counts=collections.Counter(e['execution_status'] for e in web_events)
web_results=sum(e.get('result_count') or 0 for e in web_events if e['execution_status']=='SUCCESS')
web_errors=collections.Counter(e['error']['message'] for e in web_events if e.get('error'))
web={'tool_statuses':dict(web_counts),'returned_results_including_duplicates':web_results,'unique_source_records':rows[2]['source_counts'].get('baidu',0),'errors':dict(web_errors),'browser_enabled':False}
(BASE/'web_summary.json').write_text(json.dumps(web,ensure_ascii=False,indent=2))
header='| 指标 | 1：arXiv | 2：arXiv + Springer | 3：再开 web_search |\n|---|---:|---:|---:|\n'
metrics=[('流程返回 / 报告生成',['成功 / 是']*3),('耗时（秒）',[round(r['run']['duration_seconds'],2) for r in rows]),('轮次',[r['rounds'] for r in rows]),('查新点',[r['novelty_points'] for r in rows]),('任务 completed / partial / failed',[f"{r['task_statuses'].get('completed',0)} / {r['task_statuses'].get('partial',0)} / {r['task_statuses'].get('failed',0)}" for r in rows]),('arXiv 物理请求',[r['arxiv']['physical_api_requests'] for r in rows]),('arXiv HTTP 200',[r['arxiv']['http_200_count'] for r in rows]),('arXiv HTTP 429',[r['arxiv']['http_429_count'] for r in rows]),('arXiv ReadTimeout',[r['arxiv']['read_timeout_count'] for r in rows]),('arXiv metadata 逻辑调用',[r['arxiv']['metadata_logical_requests'] for r in rows]),('arXiv 间隔违规',[r['arxiv']['interval_violation_count'] for r in rows]),('外部数据库独立作品',[r['external_works'] for r in rows]),('Springer source records',[r['source_counts'].get('springer',0) for r in rows]),('Web source records（去重）',[r['source_counts'].get('baidu',0) for r in rows]),('全文文本制品',[r['artifact_roles'].get('extracted_text',0) for r in rows]),('raw / validator / final证据卡',[f"{r['raw_cards']} / {r['validator_accepted']} / {r['final_cards']}" for r in rows]),('证据不足查新点',[', '.join(i['novelty_point_id'] for i in r['insufficient_points']) or '无' for r in rows]),('模型调用',[r['model_calls'] for r in rows]),('API报告的total tokens',[r['reported_total_tokens'] for r in rows])]
table=header+'\n'.join('| '+k+' | '+' | '.join(map(str,v))+' |' for k,v in metrics)
reports='\n'.join(f"- 第{r['trial']}组：[正式报告]({rel(r['trial'])}/MF2033k6lC/report/MF2033k6lC-report.md) · [结果]({rel(r['trial'])}/result.json) · [配置]({rel(r['trial'])}/effective_config.json) · [arXiv统计]({rel(r['trial'])}/arxiv_metrics.json) · [HTTP记录]({rel(r['trial'])}/http_events.jsonl)" for r in rows)
text=f'''# MF2033k6lC：PaperInput 后三组真实实验与解决方案

## 1. 结论

**三组完整工作流均已完成并生成报告；流程完成不等于证据充分。**

1. **batch 合并有效，但当前 arXiv 限流仍存在。** 第一组10次物理API请求中6次429、4次超时，没有200。生产流程没有触发metadata调用；独立探测确认6调用/4不同ID合并为同一个id_list，首次请求后重试一次，仍收到超时和429。不能宣称补丁已经解决429。
2. **Springer Nature 确实扩张检索。** 第二组新增16篇数据库作品、4份全文文本。固定同一英文计划补充对照得到24条结果、去重22篇；这些补充文献不混入主流程统计。元数据404中的“No data”被误当故障，会阻断自动放宽链。
3. **web_search 工具真实可用。** 第三组成功调用{web_counts.get('SUCCESS',0)}次，返回{web_results}条结果（含重复），保存{web['unique_source_records']}个独立Web来源。browser关闭意味着本轮仅验证Web发现能力，未完成网页获取→reader→证据闭环。长度校验错误及预算耗尽也真实发生。

开始：{rows[0]['run']['started_at']}；第三组结束：{rows[2]['run']['finished_at']}。整理时间：{now.isoformat(timespec='seconds')}（Asia/Shanghai）。目录名最终按归档结束时间精确到秒。

## 2. 实验设计与复现条件

- PDF：[MF2033k6lC.pdf](input/MF2033k6lC.pdf)，原路径 `examples/MF2033k6lC.pdf`，90页。标题为“面向大规模动态图的图神经网络优化机制研究”。
- PDF SHA-256：`{rows[0]['run']['pdf_sha256']}`。
- PaperInput SHA-256：`{rows[0]['run']['paper_json_sha256']}`，三组完全一致。复用既有text_layer解析输入、91条参考文献；本任务从PaperInput后执行，没有重跑MinerU。
- 生产 `build_standard_full_workflow`，默认max_rounds=2、max_concurrency=4；保留生产Reviewer、Validator和报告完整性检查。未抽样任务，未修改生产代码。
- 仅切换provider及web_search开关；第一组仅arxiv，第二组加springer，第三组再开启百度千帆web_search。其他provider（含null_catalog）禁用；browser三组均关闭。
- 模型为项目配置的deepseek-flash，通过SiliconFlow调用；所有真实联网操作已获用户明确授权。配置、版本和完整产物均随目录保存。
- arXiv参数：共享scheduler、4秒间隔、200ms批窗口、最大32 ID、20秒请求超时、max_retries=1、45秒重试预算。
- 查新点原文对照见 [novelty_point_comparison.json](novelty_point_comparison.json)，实际配置差异见 [config_diff.json](config_diff.json)。第二、三组NP-3是边分割图流划分，第一组NP-3是注意力融合，不能按NP编号直接比较覆盖。
- 每组重新执行查新点提取、计划及两轮上限研究；模型随机性导致计划/任务数量不完全相同。三组不是严格的固定计划A/B因果实验，固定计划补充对照用于单独验证provider扩张。
- 第一组自动刷新历史bootstrap；该轮90条failed、1条not_found，之后两组复用同一已刷新的快照。历史manifest仍含9篇缓存文献的问题见第5节。原始输入工作区未改写。

## 3. 三组主流程结果

{table}

说明：数据库作品统计来自每组research references manifest，不含subject-reference池；Web source record尚未绑定work，不能与数据库作品数量混为同一指标。全文指已落盘extracted_text制品，不能用HTTP 200次数代替。第一组最终3张卡来自原参考文献缓存。arXiv统计包含该组bootstrap，第二、三组复用缓存不额外发起bootstrap请求。

{reports}

详细指标：[summary.json](summary.json)。每组目录同时包含模型调用、工具调用、runtime stages、LLM输入输出、研究任务结果、参考文献和报告。

## 4. 重点观察

### arXiv：429与batch效果

第一组所有429响应正文为 `Rate exceeded.`，调度事件未记录间隔违规。主流程metadata_logical_requests=0，因此不能从生产运行证明metadata合并是否发生。累计logical/physical比例还包含熔断拒绝，不能直接解释为batch压缩收益。

独立探测使用图学习相关4个arXiv ID，并让6个调用同步进入200ms窗口；两个ID重复。记录见 [batch/result.json](supplementary/batch/result.json)。两次物理尝试携带相同6个logical_request_ids及4个唯一ID，分别超时、429，6个等待者均正确收到失败。合并确实执行；没有无补丁同期对照，无法量化429发生率改善。

当前batch统计把重试当成新批次累加，故unique_metadata_ids=8、dedup_count=4、batch_count=2；真实逻辑值分别为4、2、1。需拆分逻辑批次与物理尝试，详见修复方案。

### Springer：结果扩张与错误分类

第二组Springer Meta API 3次200、11次404；Open Access 7次200，最终仅4份不同全文文本制品。检索命中、HTTP请求、独立文献与可读全文已分别统计。

[固定计划对照](supplementary/compare/result.json)复用第一组NP-1/T-2英文SearchPlan，以各provider自有QueryAdapter编译3个查询；全部变体均执行供对照，区别于生产命中后提前停止的路径。Springer每次8条，去重22篇；arXiv两项429失败、一项熔断拒绝。这证明当前运行条件下Springer带来可检索文献，不代表其对所有查询都比arXiv更好。

另复现第二组一个中文查询的Meta 404，正文明确为无匹配数据；见对照产物中的springer_404_diagnostic及http_events。当前程序将其标记ProviderRequestError并停止放宽链，是需要修复的真实语义错误。

### web_search：可用，但获取链缺口阻止证据转化

[web_summary.json](web_summary.json)记录成功/失败次数及原因。主流程已经真实调用工具并落盘来源，未另跑额外Web探测，也未使用助手自己的网页搜索工具代替项目工具。

```json
{json.dumps(web,ensure_ascii=False,indent=2)}
```

成功发现Web来源不等于证据获取成功。当前配置缺少browser，Web结果没有可交给reader的网页Artifact；模型仍有错误使用source_record_id读文档、连续搜索耗尽预算等行为。不能将这些后续失败描述为百度搜索API不可用。

## 5. 影响工作流和报告的bug及解决方案

下面问题均基于实际日志与本地复现。修复方案尚未应用到生产代码，以保留三组相同代码版本的可比性。

'''
text+=(BASE/'diagnosis_notes.md').read_text().split('\n',1)[1]
text+='''

## 6. 验证、局限和归档说明

- 现有离线测试27项通过：[offline_tests.log](offline_tests.log)。覆盖arXiv scheduler、Springer provider、web_search；这些测试未覆盖本次发现的所有集成缺口，不能替代真实实验。
- 三组报告均检查存在且流程返回SUCCESS；证据质量必须另看各点不足项及检索降级。报告中出现的无条件“新颖”不能在外部检索失败背景下直接采信。
- 初次沙箱网络权限失败与后续审批拒绝保存在sandbox_start_failure及早期记录中，不计作三组实验，也不计入真实429统计；用户确认后已正常完成联网实验。
- 使用 `run_trial.py 1/2/3` 从仓库根目录启动（Python解释器为 `/home/lya3106643285/miniconda3/envs/Novelty/bin/python`）；该脚本针对本次目录运行，会写对应组别目录。要复跑应先复制脚本与input到新的实验目录，避免覆盖本次档案。
- `probe_tools.py batch/compare` 是独立补充探测；web模式已准备但未执行，因第三组已充分验证真实工具调用。`summarize.py` 可重新汇总原始产物，`write_solution.py` 可生成正文；诊断原文见diagnosis_notes.md。
- 归档时目录以结束时间重命名。原始日志中的绝对路径保留运行时原值；用path_mapping.json映射到当前目录，以上报告链接均为当前相对路径。原始来源观测、请求时间与错误未改写。
- 全部文本产物检查已配置凭据是否泄漏，结果见credential_scan.json；实验脚本不保存请求授权头和Springer请求中的api_key。文件清单及SHA-256见artifact_inventory.json。
'''
(BASE/'solution.md').write_text(text)
print('solution.md written')
