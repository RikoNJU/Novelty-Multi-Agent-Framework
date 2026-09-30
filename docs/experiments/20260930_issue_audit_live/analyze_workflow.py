"""Summarize canonical runtime only; archives are excluded from totals."""
import collections,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT),str(ROOT/'backend/src')]
OUT=Path(__file__).resolve().parent;run=OUT/'runs/0001';workspace=run/'MF2033k6lC';runtime=next((workspace/'runtime').iterdir())
from novelty_agent_framework.tools.renderer import render_report
res=json.loads((run/'result.json').read_text());summary=json.loads((runtime/'summary.json').read_text());trace=json.loads((runtime/'diagnostics/point_extraction_trace.json').read_text())
calls=[json.loads(p.read_text()) for p in sorted((runtime/'llm_calls').glob('*.json'))]
budgets=[json.loads(p.read_text()) for p in sorted((runtime/'provider_budget').glob('*.json'))]
providers=[json.loads(p.read_text()) for p in sorted((runtime/'provider_requests').glob('*.json'))]
original=workspace/'report/MF2033k6lC-report.md';rendered=render_report(paper_name='MF2033k6lC',output_root=run,save_path=OUT/'rerendered-report.md')
a=original.read_text().splitlines();b=rendered.read_text().splitlines()
points=res['brief']['novelty_points'];paper=json.loads((run/'paper-input.json').read_text());digest=trace['digest']
pointtext={p['point_id']:json.dumps(p,ensure_ascii=False) for p in points}
mechanisms=[('NP-1','图自编码器',['图自编码器','graph autoencoder']),('NP-1','重构误差',['重构误差','reconstruction']),('NP-1','循环神经网络',['RNN','循环神经网络','recurrent']),('NP-2','注意力层',['注意力','attention']),('NP-2','梯度同步',['梯度','gradient']),('NP-3','Count-Min Sketch',['Count-Min Sketch']),('NP-3','最小堆',['最小堆','minimum heap'])]
coverage=[]
for point,label,terms in mechanisms:
 coverage.append({'point':point,'mechanism':label,'in_input_abstract':any(t.lower() in (paper.get('abstract') or '').lower() for t in terms),'in_digest':any(t.lower() in json.dumps(digest,ensure_ascii=False).lower() for t in terms),'literal_in_output_point':any(t.lower() in pointtext.get(point,'').lower() for t in terms),'note':'Literal locator aid only; not an exhaustive semantic gold standard.'})
result={'runtime_id':runtime.name,'duration_seconds':json.loads((run/'run.json').read_text())['duration'],'rounds':res['rounds'],'model_calls':len(calls),'model_statuses':dict(collections.Counter(x['status'] for x in calls)),'usage':{k:sum((x.get('provider_usage') or {}).get(k,0) or 0 for x in calls) for k in ['prompt_tokens','completion_tokens','total_tokens']},'usage_missing':sum(not x.get('provider_usage') for x in calls),'chat_dispatches':sum(x.get('chat_transport_invoked') is True for x in calls),'provider_reservations_by_label':dict(collections.Counter(x['provider'] for x in budgets)),'physical_events_by_provider':dict(collections.Counter(x['provider'] for x in providers if x.get('event_type')=='physical_request')),'cards_by_point':dict(collections.Counter(x['novelty_point_id'] for x in res['evidence_cards'])),'reviews':[{'point':r['novelty_point_id'],'status':r['status'],'reason':r.get('incomplete_reason'),'issues':[x['code'] for x in r.get('execution_issues',[])]} for r in res['novelty_reviews']],'recovery_decisions':res['recovery_decisions'],'integrity_gates':summary['integrity_gates'],'diagnostics':summary['diagnostics'],'rerender':{'same_bytes':original.read_bytes()==rendered.read_bytes(),'original_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'new_sha256':hashlib.sha256(rendered.read_bytes()).hexdigest(),'line_count_equal':len(a)==len(b),'changed_lines':[{'line':i+1,'before':x,'after':y} for i,(x,y) in enumerate(zip(a,b)) if x!=y]},'feature_locator_checks':coverage}
(OUT/'workflow-analysis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['recovery_decisions','integrity_gates','diagnostics']},ensure_ascii=False,indent=2))
