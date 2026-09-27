"""Summarize canonical live runtime only; archive copies do not add calls."""
import collections,hashlib,json
from pathlib import Path
OUT=Path(__file__).resolve().parent
runs=[]
for root in sorted((OUT/'runs').iterdir()):
 manifest=json.loads((root/'run.json').read_text());assert manifest['status']!='RUNNING'
 rt=next((root/'MF2033k6lC/runtime').iterdir())
 summary=json.loads((rt/'summary.json').read_text())
 result=json.loads((root/'result.json').read_text()) if (root/'result.json').exists() else {}
 calls=[json.loads(f.read_text()) for f in sorted((rt/'llm_calls').glob('*.json'))]
 sums={k:sum(c['tokens'].get(k) or 0 for c in calls) for k in ('input_tokens','output_tokens','total_tokens')}
 assert len(calls)==summary['llm_usage']['totals']['calls']
 assert all(v==summary['llm_usage']['totals'][k] for k,v in sums.items())
 tasks=[]
 for f in sorted((rt/'stages').glob('*run_research_task/output.json')):
  tasks.extend(json.loads(f.read_text()).get('task_research_results',[]))
 executions=[e for task in tasks for e in task['search_executions']]
 links=[]
 for e in executions:
  params=e['parameters']
  if params.get('not_run_reason')=='provider_failed':
   matching=[x for x in executions if x['execution_id']==params['blocked_by_execution_id'] and x['failure']['event_id']==params['blocked_by_failure_event_id']]
   assert matching and matching[0]['failure']['code']==params['blocked_by_failure_code']
   links.append(e['execution_id'])
 anomalies=[]
 for call in calls:
  tools={t['function']['name']:t['function']['parameters'] for t in call['request_payload'].get('tools',[])}
  for tc in (call.get('response') or {}).get('tool_calls',[]):
   name=tc['name'];args=tc['arguments']
   if name not in tools:
    anomalies.append({'call_id':call['llm_call_id'],'type':'unadvertised_tool','name':name,'advertised_tools':list(tools)})
   elif isinstance(args,dict):
    extra=sorted(set(args)-set(tools[name].get('properties',{})))
    if extra:anomalies.append({'call_id':call['llm_call_id'],'type':'extra_arguments','name':name,'extra_names':extra})
 runs.append({'run_number':manifest['run_number'],'run_id':manifest['runtime_run_id'],'runner_status':manifest['status'],'duration_seconds':manifest['duration'],'model_call_records':len(calls),'model_calls':sum(bool(c.get('chat_transport_invoked')) for c in calls),'tokens':sums,'provider_requests':summary['provider_requests'],'search_execution_status_counts':dict(collections.Counter(e['status'] for e in executions)),'not_run_links_verified':len(links),'reader_calls':next((t['calls'] for t in summary['tool_calls'] if t['tool_name']=='reader'),0),'tool_calls':summary['tool_calls'],'model_action_anomalies':anomalies,'final_report_evidence_cards':len(result['evidence_cards']) if 'evidence_cards' in result else None,'task_cards_produced':sum(len(t.get('evidence_cards',[])) for t in tasks),'gate_a_accepted_cards':next((g['accepted_card_count'] for g in summary.get('integrity_gates',[]) if 'accepted_card_count' in g),None),'review_statuses':[r['status'] for r in result.get('novelty_reviews',[])],'recovery_decisions':result.get('recovery_decisions',[]),'task_outcomes':[{'point_id':t['novelty_point_id'],'task_id':t['task_id'],'status':t['status'],'steps_used':t['steps_used'],'read_count':len(t.get('read_results',[])),'card_count':len(t.get('evidence_cards',[])),'warnings':t.get('warnings',[]),'failure_codes':[e['code'] for e in t.get('execution_failures',[])]} for t in tasks],'failed_model_calls':[{'call_id':c['llm_call_id'],'status':c['status'],'error':c['error'],'chat_transport_invoked':c['chat_transport_invoked']} for c in calls if c['status']!='SUCCESS'],'outcome':summary.get('outcome')})
probe=json.loads((OUT/'web_probe_results.json').read_text())
for row in probe['responses']:
 assert hashlib.sha256((OUT/row['body_file']).read_bytes()).hexdigest()==row['sha256']
payload={'production_commit':'145723771fb615916f1fdd8199b21c603d31b59c','runs':runs,'total_model_calls':sum(r['model_calls'] for r in runs),'total_tokens':sum(r['tokens']['total_tokens'] for r in runs),'web_probe_requests':len(probe['responses']),'web_probe_hit_counts':[len(r.get('hits',[])) for r in probe['results']],'health_requests':1,'accounting_scope':'Canonical runs/* and review_followup runtime counted once; archive copies excluded; health and three diagnostic web requests listed separately','task_acceptance':'not_accepted'}
followups=[]
for rt in sorted((OUT/'review_followup/MF2033k6lC/runtime').iterdir()):
    summary=json.loads((rt/'summary.json').read_text())
    calls=[json.loads(f.read_text()) for f in (rt/'llm_calls').glob('*.json')]
    row={'run_id':rt.name,'runtime_status':summary['run']['status'],'model_calls':sum(bool(c.get('chat_transport_invoked')) for c in calls),'tokens':summary['llm_usage']['totals'],'provider_requests':summary['provider_requests']}
    followups.append(row)
payload['review_followups']=followups
payload['total_model_calls']+=sum(r['model_calls'] for r in followups)
payload['total_tokens']+=sum(r['tokens']['total_tokens'] for r in followups)
payload['arxiv_physical_requests']=sum(r['provider_requests']['physical_api_requests']+r['provider_requests']['physical_web_requests'] for r in runs)+len(probe['responses'])
payload['review_card']=json.loads((OUT/'review_followup/card_review.json').read_text())
payload['review_summary_attempt']=json.loads((OUT/'review_followup/summary_attempt.json').read_text())
(OUT/'analysis.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in payload.items() if k not in {'runs','review_followups','review_card','review_summary_attempt'}}))
