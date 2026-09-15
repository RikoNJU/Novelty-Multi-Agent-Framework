"""Summarise persisted observations, without making live requests."""
import json,collections,re
from pathlib import Path
BASE=Path(__file__).resolve().parent
summary=[]
def read(p,default=None):return json.loads(p.read_text()) if p.exists() else default
for n,name in enumerate(['arxiv','arxiv_springer','arxiv_springer_web'],1):
 d=BASE/f'{n:02d}_{name}';w=d/'MF2033k6lC';run=read(d/'run.json',{});r=read(d/'result.json',{});refs=read(w/'references/list.json',{});calls=read(d/'model_calls.json',[]);tools=read(d/'tool_events.json',{})
 tasks=[read(p) for p in w.glob('research-runs/*/*/attempt-*.json')]
 http=[json.loads(s) for s in (d/'http_events.jsonl').read_text().splitlines()] if (d/'http_events.jsonl').exists() else []
 counts=collections.Counter((e['host'],str(e['status']),e.get('error')) for e in http)
 tcounts=collections.defaultdict(collections.Counter)
 for events in tools.values():
  for e in events:
   if e.get('tool'):tcounts[e['tool']]['success' if e.get('success') else 'failed']+=1
 sources=collections.Counter(x.get('provider',x.get('source_id',x.get('backend','unknown'))) for x in refs.get('source_records',[]))
 a=read(d/'arxiv_metrics.json',{});a.pop('events',None)
 cards=read(w/'evidence-cards.json',{})
 row={'trial':n,'run':run,'rounds':r.get('rounds'),'novelty_points':len(r.get('brief',{}).get('novelty_points',[])),'task_statuses':dict(collections.Counter(t.get('status') for t in tasks)),'task_warnings':[{'point':t.get('novelty_point_id'),'task':t.get('task_id'),'warnings':t.get('warnings')} for t in tasks if t.get('warnings')],'arxiv':a,'external_works':len(refs.get('works',[])),'source_records':len(refs.get('source_records',[])),'source_counts':dict(sources),'artifacts':len(refs.get('artifacts',[])),'raw_cards':len(cards.get('raw_evidence_cards',[])),'validator_accepted':len(cards.get('validator_accepted_cards',[])),'final_cards':len(r.get('evidence_cards',[])),'insufficient_points':r.get('insufficient_final_evidence_points',[]),'issues':r.get('issues',[]),'tool_calls':dict(tcounts),'http_counts':[{'host':k[0],'status':k[1],'error':k[2],'count':v} for k,v in counts.items()],'model_calls':len(calls),'reported_total_tokens':sum(c.get('total_tokens') or 0 for c in calls),'report_exists':(w/'report/MF2033k6lC-report.md').exists()}
 provider_calls=collections.defaultdict(collections.Counter)
 errors=collections.Counter()
 for tool_path in w.glob('runtime/*/tools/*.json'):
  event=read(tool_path,{})
  if event.get('tool_name')=='database_search':
   provider=event.get('agent_arguments',{}).get('source_id','unknown')
   provider_calls[provider][event.get('execution_status','unknown')]+=1
   for execution in (event.get('raw_result') or {}).get('payload',{}).get('search_executions',[]):
    if execution.get('error'):errors[execution['error']]+=1
 row['provider_tool_calls']=dict(provider_calls)
 row['search_errors']=dict(errors)
 summary.append(row)
(BASE/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
for r in summary:print(json.dumps({k:r[k] for k in ['trial','task_statuses','external_works','source_counts','final_cards','model_calls','report_exists']},ensure_ascii=False))
