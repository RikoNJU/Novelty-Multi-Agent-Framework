"""Recover query audit from recorded tool observations without rerunning APIs."""
import json,collections
from pathlib import Path
BASE=Path(__file__).resolve().parent
result={};lines=['# 检索式遗漏审计与实际查询恢复','', '以下来自原始运行日志，未重新调用模型或检索API。失败记录表示已进入数据库检索执行层，不表示请求一定发送上网（熔断可能本地拒绝）。Web调用另列，不伪装为数据库检索式。原始三份报告保持不变。','']
for d in ['01_arxiv','02_arxiv_springer','03_arxiv_springer_web']:
 w=BASE/d/'MF2033k6lC';plans=json.loads((w/'retrieval-plans.json').read_text())['novelty_point_plans'];points={p['novelty_point_id']:{'search_plan_count':len(p['search_plans']),'persisted_execution_count':len(p['executed_queries']),'report_query_count':len(p['query_plan']['queries']),'database_executions':[],'web_calls':[]} for p in plans}
 task_context={}
 for p in w.glob('runtime/*/stages/*run_research_task/input.json'):
  j=json.loads(p.read_text());task_context[j['current_task']['task_id']+':'+j['current_point']['point_id']]=j
 for p in sorted(w.glob('runtime/*/tools/*.json')):
  e=json.loads(p.read_text());raw=e.get('raw_result') or {};payload=raw.get('payload') or {}
  if e.get('tool_name')=='database_search':
   for x in payload.get('search_executions',[]):
    point=x['parameters'].get('novelty_point_id');row={'task':x['parameters'].get('task_id'),'provider':x['source_id'],'query':x['query'],'status':x['status'],'error':x.get('error'),'log':str(p.relative_to(BASE)),'execution_id':x['execution_id']}
    if point in points:points[point]['database_executions'].append(row)
  elif e.get('tool_name')=='web_search':
   # Tool logs do not consistently carry task bindings; retain them at run scope.
   points.setdefault('_web',{'web_calls':[]})['web_calls'].append({'query':(e.get('agent_arguments') or {}).get('query'),'status':e.get('execution_status'),'error':(e.get('error') or {}).get('message'),'log':str(p.relative_to(BASE))})
 result[d]=points;lines+=['## '+d,'','| 查新点 | 语义计划数 | 报告检索式数 | 日志数据库执行记录 | 其中失败 |','|---|---:|---:|---:|---:|']
 for point,r in points.items():
  if point=='_web':continue
  r['runtime_execution_count']=len(r['database_executions']);r['runtime_failed_count']=sum(x['status']=='failed' for x in r['database_executions'])
  lines.append(f"| {point} | {r['search_plan_count']} | {r['report_query_count']} | {r['runtime_execution_count']} | {r['runtime_failed_count']} |")
 for point,r in points.items():
  if point=='_web':continue
  lines+=['','### '+point,'']
  groups=collections.defaultdict(list)
  for x in r['database_executions']:groups[(x['provider'],x['query'],x['status'])].append(x)
  for (provider,query,status),xs in groups.items():
   lines += [f"- **{provider} / {status}**；日志出现 {len(xs)} 次；任务：{', '.join(sorted({x['task'] for x in xs}))}",f"  - 检索式：`{query}`",f"  - [原始记录]({xs[0]['log']})"]
   if xs[0].get('error'):lines += ['  - 错误：'+xs[0]['error'].replace('\n',' ')[:300]]
 if '_web' in points:
  lines+=['','### Web 查询（按调用记录，含本地拒绝）','']
  for x in points['_web']['web_calls']:lines+=[f"- {x['status']}：`{x['query']}`；[记录]({x['log']})"]
 lines+=['']
(BASE/'report_query_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
(BASE/'report_query_audit.md').write_text('\n'.join(lines))
for d,points in result.items():print(d,{p:{k:r[k] for k in ['search_plan_count','report_query_count','runtime_execution_count','runtime_failed_count']} for p,r in points.items() if p!='_web'})
