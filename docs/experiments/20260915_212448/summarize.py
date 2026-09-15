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
metrics={
 'run':read(d/'run.json',{}),'rounds':r.get('rounds'),
 'points':r.get('brief',{}).get('novelty_points',[]),
 'task_count':len(tasks),'task_statuses':dict(Counter(t.get('status') for t in tasks)),
 'task_warnings':[{'task':t.get('task_id'),'warnings':t.get('warnings')} for t in tasks if t.get('warnings')],
 'external_works':len(refs.get('works',[])),'source_records':len(refs.get('source_records',[])),
 'source_kinds':dict(Counter(s.get('source_kind') for s in refs.get('source_records',[]))),
 'artifacts':len(refs.get('artifacts',[])),
 'read_count':sum(len(t.get('read_results',[])) for t in tasks),
 'raw_cards':len(cards.get('raw_evidence_cards',[])),
 'final_cards':len(r.get('evidence_cards',[])),
 'evidence_types':dict(Counter(e.get('provenance',{}).get('evidence_type','missing') for e in evidence)),
 'candidate_states':dict(Counter(c.get('status') for t in rows for c in t.get('candidates',[]))),
 'recovery': [x for x in recovery if x['warnings']],
 'http_counts':dict(Counter(f"{e['host']}:{e['status']}" for e in http)),
 'model_calls':len(models),'reported_tokens':sum(x.get('total_tokens') or 0 for x in models),
 'report_exists':report is not None,'issues':r.get('issues',[]),
 'reviews':r.get('novelty_reviews',[]),
}
(b/'metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in metrics.items() if k not in {'points','task_warnings','recovery','reviews','run'}},ensure_ascii=False))
