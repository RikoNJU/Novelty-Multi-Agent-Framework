"""Reconcile observed model responses; do not count archive copies or reserves as dispatches."""
import collections,json
from pathlib import Path
OUT=Path(__file__).resolve().parent
roots={'full_workflow':OUT/'runs/0001/MF2033k6lC/runtime','semantic_initial':OUT/'semantic-controls/public-attention-control/runtime','semantic_corrected':OUT/'semantic-controls-v2/public-attention-control/runtime','context_probes':OUT/'local-context/local-context/runtime'}
rows=[];allids=[]
for label,root in roots.items():
 calls=[json.loads(p.read_text()) for p in root.glob('*/llm_calls/*.json')]
 allids.extend(x.get('client_call_id') for x in calls)
 rows.append({'experiment':label,'records':len(calls),'statuses':dict(collections.Counter(x['status'] for x in calls)),'chat_dispatches':sum(x.get('chat_transport_invoked') is True for x in calls),'usage':{k:sum((x.get('provider_usage') or {}).get(k,0) or 0 for x in calls) for k in ['prompt_tokens','completion_tokens','total_tokens']},'missing_usage':sum(not x.get('provider_usage') for x in calls)})
manual=json.loads((OUT/'local-context-results.json').read_text())[-1]
rows.append({'experiment':'debug_disabled_direct_responses','records':0,'chat_dispatches':2,'usage':{k:manual['first']['usage'][k]+manual['second']['usage'][k] for k in ['prompt_tokens','completion_tokens','total_tokens']},'missing_usage':0})
result={'experiments':rows,'total_chat_dispatches':sum(x['chat_dispatches'] for x in rows),'total_observed_usage':{k:sum(x['usage'][k] for x in rows) for k in ['prompt_tokens','completion_tokens','total_tokens']},'duplicate_nonempty_client_call_ids':[k for k,v in collections.Counter(x for x in allids if x).items() if v>1],'notes':['Admission denial has a runtime record but no chat dispatch.','The real HTTP 400 has no provider usage; totals are observed usage, not total server cost.','Debug-disabled calls are counted from retained actual response objects, not Runtime.','Context measurement requests and health probes are not chat requests.','No cloud model inference calls were made.']}
(OUT/'usage-summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
