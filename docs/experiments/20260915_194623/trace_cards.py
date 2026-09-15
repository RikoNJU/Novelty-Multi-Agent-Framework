"""Offline per-work candidate -> read -> evidence card audit."""
import json,collections
from pathlib import Path
BASE=Path(__file__).resolve().parent;SOURCE=BASE.parent/'20260915_184612'
all_runs={}
for run in ['01_arxiv','02_arxiv_springer','03_arxiv_springer_web']:
 w=SOURCE/run/'MF2033k6lC';manifest=json.loads((w/'references/list.json').read_text());subject=json.loads((w/'subject_references/list.json').read_text());result=json.loads((SOURCE/run/'result.json').read_text());evidence=json.loads((w/'evidence-cards.json').read_text())
 tasks=[]
 for path in sorted(w.glob('research-runs/*/*/attempt-*.json')):
  t=json.loads(path.read_text());t['log']=str(path.relative_to(SOURCE));tasks.append(t)
 final_ids={c['card_id'] for c in result['evidence_cards']};works=[]
 for namespace,m in [('research_reference',manifest),('subject_reference',subject)]:
  for work in m['works']:
   wid=work['work_id'];reads=[];cards=[]
   for t in tasks:
    for r in t['read_results']:
     if r['work_id']==wid and r['namespace']==namespace:
      reads.append({'point':t['novelty_point_id'],'task':t['task_id'],'task_status':t['status'],'role':r['role'],'read_id':r['read_id'],'char_start':r['char_start'],'char_end':r['char_end'],'warnings':t['warnings'],'log':t['log']})
    ids={e['evidence_id'] for e in t['evidence'] if e['work_id']==wid and e.get('provenance',{}).get('artifact_namespace')==namespace}
    for c in t['evidence_cards']:
     if ids.intersection(c['evidence_ids']):cards.append({'card_id':c['card_id'],'point':c['novelty_point_id'],'task':c['task_id'],'final_accepted':c['card_id'] in final_ids})
   if cards:reason='card_produced'
   elif not reads:reason='not_read'
   elif all(r['task_status']=='partial' for r in reads):reason='only_read_in_aborted_tasks_no_builder'
   elif work['title'].startswith('HGP-IC:') and any('ungrounded quote' in warning for r in reads for warning in r['warnings']):reason='builder_rejected_modified_quote'
   else:reason='read_but_not_selected_no_per_work_reason'
   works.append({'namespace':namespace,'work_id':wid,'title':work['title'],'fulltext_acquired':any(a['work_id']==wid and a['role']=='extracted_text' for a in m['artifacts']),'reads':reads,'cards':cards,'reason':reason})
 web=[]
 for r in manifest['source_records']:
  if r['source_id']=='baidu':web.append({'source_record_id':r['source_record_id'],'title':r['title'],'url':r.get('landing_url'),'work_id':r.get('work_id'),'artifacts':[a['artifact_id'] for a in manifest['artifacts'] if a.get('source_record_id')==r['source_record_id']],'reason':'discovery_without_browser_acquisition'})
 research=[x for x in works if x['namespace']=='research_reference'];summary={'database_candidates':len(research),'database_read':sum(bool(x['reads']) for x in research),'database_fulltext_acquired':sum(x['fulltext_acquired'] for x in research),'database_fulltext_read':sum(any(r['role']=='extracted_text' for r in x['reads']) for x in research),'database_reason_counts':dict(collections.Counter(x['reason'] for x in research)),'partial_tasks':sum(t['status']=='partial' for t in tasks),'reads_in_partial_tasks':sum(len(t['read_results']) for t in tasks if t['status']=='partial'),'raw_cards':len(evidence['raw_evidence_cards']),'validator_rejected':len(evidence['rejected_evidence']),'final_cards':len(final_ids),'final_database_cards':sum(len(x['cards']) for x in research),'final_subject_reference_cards':sum(len(x['cards']) for x in works if x['namespace']=='subject_reference'),'web_sources':len(web),'web_artifacts':sum(len(x['artifacts']) for x in web)}
 all_runs[run]={'summary':summary,'works':works,'web_sources':web,'tasks':[{'point':t['novelty_point_id'],'task':t['task_id'],'status':t['status'],'reads':len(t['read_results']),'cards':len(t['evidence_cards']),'warnings':t['warnings'],'log':t['log']} for t in tasks]}
(BASE/'card_trace.json').write_text(json.dumps(all_runs,ensure_ascii=False,indent=2))
labels={'card_produced':'已产卡','not_read':'未读取；无逐篇排除理由','only_read_in_aborted_tasks_no_builder':'读取后任务中断；未调用Builder','builder_rejected_modified_quote':'引文被模型改写；Builder拒绝','read_but_not_selected_no_per_work_reason':'读取后未选入卡片；未记录逐篇理由'}
lines=['# 逐篇候选→读取→证据卡追踪','','本附件仅回放已有产物，无模型/API请求。未读取不等于不相关；没有逐篇理由的地方明确标记未知。','']
for run,data in all_runs.items():
 lines+=['## '+run,'','```json',json.dumps(data['summary'],ensure_ascii=False,indent=2),'```','','### 数据库文献逐篇记录','','| 文献 | 有全文 | 读取次数 | 卡片数 | 原因 |','|---|---|---:|---:|---|']
 for x in data['works']:
  if x['namespace']!='research_reference':continue
  link='../20260915_184612/'+x['reads'][0]['log'] if x['reads'] else '../20260915_184612/'+run+'/MF2033k6lC/references/list.json'
  title=x['title'].replace('|','\\|')
  lines.append(f"| [{title}]({link}) | {'是' if x['fulltext_acquired'] else '否'} | {len(x['reads'])} | {len(x['cards'])} | {labels[x['reason']]} |")
 lines+=['','### 任务记录','','| 查新点 / 任务 | 状态 | 读取 | 卡片 | 原因 |','|---|---|---:|---:|---|']
 for t in data['tasks']:
  reason='；'.join(t['warnings']).replace('|','\\|').replace('\n',' ') or '正常产卡'
  lines.append(f"| [{t['point']} / {t['task']}](../20260915_184612/{t['log']}) | {t['status']} | {t['reads']} | {t['cards']} | {reason} |")
 lines+=['']
(BASE/'card_trace.md').write_text('\n'.join(lines))
for k,v in all_runs.items():print(k,v['summary'])
