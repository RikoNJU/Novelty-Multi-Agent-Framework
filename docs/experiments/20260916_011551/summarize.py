"""Audit persisted full-run results without making network requests."""
import json
from pathlib import Path
from collections import Counter,defaultdict
b=Path(__file__).resolve().parent;d=b/'run';w=d/'MF2033k6lC'
def read(p,default=None):
 return json.loads(p.read_text()) if p.exists() else default
r=read(d/'result.json',{});refs=read(w/'references/list.json',{});cards=read(w/'evidence-cards.json',{})
tasks=[read(p,{}) for p in w.glob('research-runs/*/*/attempt-*.json')]
if not tasks:
 tasks=[read(p,{}) for p in w.glob('runtime/*/stages/*run_research_task/output.json')]
http=[json.loads(s) for s in (d/'http_events.jsonl').read_text().splitlines()] if (d/'http_events.jsonl').exists() else []
rows=read(w/'candidate-audit.json',{}).get('tasks',[])
models=read(d/'model_calls.json',[])
evidence=[e for t in tasks for e in t.get('evidence',[])]
recovery=[{'task':t.get('task_id'),'warnings':[x for x in t.get('warnings',[]) if 'finalization' in x or 'correction' in x]} for t in tasks]
report=next(w.glob('report/*-report.md'),None)
tools=[read(p,{}) for p in w.glob('runtime/*/tools/*.json')]
reader_tools=[t for t in tools if t.get('tool_name')=='reader']
batch_tools=[t for t in reader_tools if t.get('agent_arguments',{}).get('reads')]
raw_reads=[]
for t in reader_tools:
 payload=(t.get('raw_result') or {}).get('payload',{})
 raw_reads.extend(payload.get('read_results',[payload['read_result']] if 'read_result' in payload else []))
subject=read(w/'subject_references/list.json',{})
subject_ids={a['artifact_id'] for a in subject.get('artifacts',[])}
point_metrics={}
for t in tasks:
 point=t.get('novelty_point_id')
 row=point_metrics.setdefault(point,{'tasks':0,'reads':0,'cards':0,'executions':[]})
 row['tasks']+=1; row['reads']+=len(t.get('read_results',[])); row['cards']+=len(t.get('evidence_cards',[]))
 row['executions'].extend(t.get('search_executions',[]))
for point,row in point_metrics.items():
 ex=row.pop('executions'); row['search_executions']=len(ex)
 row['search_statuses']=dict(Counter(e.get('status') for e in ex))
 row['unique_queries']=len({(e.get('source_id'),e.get('query')) for e in ex})
 row['final_cards']=sum(c.get('novelty_point_id')==point for c in r.get('evidence_cards',[]))
review_calls=[m for m in models if m.get('stage') in {'Reviewer card','Reviewer summary'}]
from datetime import datetime
review_starts=sorted(datetime.fromisoformat(m['started_at'].replace('Z','+00:00')) for m in review_calls)
first_wave=sum((start-review_starts[0]).total_seconds()<0.01 for start in review_starts) if review_starts else 0
metrics={
 'run':read(d/'run.json',{}),'rounds':r.get('rounds'),
 'points':r.get('brief',{}).get('novelty_points',[]),
 'task_count':len(tasks),'task_statuses':dict(Counter(t.get('status') for t in tasks)),
 'task_warnings':[{'task':t.get('task_id'),'warnings':t.get('warnings')} for t in tasks if t.get('warnings')],
 'external_works':len(refs.get('works',[])),'source_records':len(refs.get('source_records',[])),
 'source_kinds':dict(Counter(s.get('source_kind') for s in refs.get('source_records',[]))),
 'artifacts':len(refs.get('artifacts',[])),
 'read_count':sum(len(t.get('read_results',[])) for t in tasks),
 'raw_cards':sum(len(t.get('evidence_cards',[])) for t in tasks),
 'final_cards':len(r.get('evidence_cards',[])),
 'evidence_types':dict(Counter(e.get('provenance',{}).get('evidence_type','missing') for e in evidence)),
 'candidate_states':dict(Counter(c.get('status') for t in rows for c in t.get('candidates',[]))),
 'recovery': [x for x in recovery if x['warnings']],
 'http_counts':dict(Counter(f"{e['host']}:{e['status']}" for e in http)),
 'model_calls':len(models),'reported_tokens':sum(x.get('total_tokens') or 0 for x in models),
 'report_exists':report is not None,'issues':r.get('issues',[]),
 'reviews':r.get('novelty_reviews',[]),
 'point_metrics':point_metrics,
 'cache':{'works':len(subject.get('works',[])),'artifacts':len(subject_ids),
          'cached_read_fragments':sum(v.get('artifact_id') in subject_ids for v in raw_reads),
          'unique_cached_artifacts_read':len({v.get('artifact_id') for v in raw_reads if v.get('artifact_id') in subject_ids})},
 'reader_calls':len(reader_tools),'batch_reader_calls':len(batch_tools),
 'batch_requested_fragments':sum(len(t['agent_arguments']['reads']) for t in batch_tools),
 'batch_read_errors':[e for t in batch_tools for e in (t.get('raw_result') or {}).get('payload',{}).get('read_errors',[])],
 'database_reused_calls':sum(bool((t.get('normalized_result') or {}).get('reused_result')) for t in tools if t.get('tool_name')=='database_search'),
 'reviewer_model_calls':dict(Counter(m.get('stage') for m in review_calls)),
 'reviewer_first_wave_calls_within_10ms':first_wave,
 'stage_timings':read(d/'stage_timings.json',{}),
 'stage_durations':[{k:v.get(k) for k in ['stage_name','duration','status','error']} for p in w.glob('runtime/*/stages/*/meta.json') if (v:=read(p,{}))],
}
(b/'metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in metrics.items() if k not in {'points','task_warnings','recovery','reviews','run'}},ensure_ascii=False))
