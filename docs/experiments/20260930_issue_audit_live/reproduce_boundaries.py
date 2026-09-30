"""Read-only production audit: deterministic counterexamples using existing test fixtures."""
import asyncio, json, sys, tempfile, traceback
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'backend/src'),str(ROOT/'tests')]
OUT=Path(__file__).resolve().parent
from backend.env.model_client import ModelCallEvent, ModelResponse, ModelToolCall
from novelty_agent_framework.core.runtime_artifacts import RuntimeArtifactManager,RuntimeDebugConfig
from novelty_agent_framework.core.recovery_policy import plan_recovery
from novelty_agent_framework.schemas import NoveltyPoint, NoveltyPointReview, NoveltyPointReviewRequest
from novelty_agent_framework.schemas.failures import make_failure,FailureCode,FailureScope
from novelty_agent_framework.agents import NoveltyEvidenceReviewer
from novelty_agent_framework.core import ToolCallHarness,ToolCallHarnessConfig
from novelty_agent_framework.tools import ReaderTool,ReferenceArtifactReaderTool,ResearcherToolRegistry
from scripts.reference_namespace_diagnostics import inspect_workspace
results=json.loads((OUT/"boundary-results.json").read_text()) if len(sys.argv)>1 else {}
def case(name,fn):
 if len(sys.argv)>1 and name not in sys.argv[1:]:return
 try:results[name]=fn()
 except Exception as e:results[name]={'experiment_error':type(e).__name__,'detail':str(e),'traceback':traceback.format_exc()}
 (OUT/'boundary-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
 print(name, json.dumps(results[name],ensure_ascii=False),flush=True)

def budgets():
 rows=[]
 for enabled in [True,False]:
  with tempfile.TemporaryDirectory() as d:
   m=RuntimeArtifactManager('audit',config=RuntimeDebugConfig(enabled=enabled,output_root=Path(d),max_model_calls=1,max_physical_provider_requests=1),diagnostics=[])
   model=[];provider=[]
   for i in range(2):
    try:m.record_model_call(ModelCallEvent(alias='local',provider='local',model='qwen',started_at=datetime.now(timezone.utc),duration_ms=0,message_count=1,call_id=str(i),phase='START'));model.append('allowed')
    except Exception as e:model.append(type(e).__name__)
    try:provider.append(m.reserve_provider_request(provider='audit',operation='offline'))
    except Exception as e:provider.append(type(e).__name__)
   rows.append({'enabled':enabled,'model_attempts':model,'provider_reservations':provider})
 return rows
case('debug_budget_bypass',budgets)

def recovery():
 issue=make_failure(FailureCode.MODEL_TRANSPORT,scope=FailureScope(point_id='NP-1'),message='Injected transport failure')
 review=NoveltyPointReview(novelty_point_id='NP-1',status='insufficient_evidence',incomplete_reason='technical_error',execution_issues=[issue])
 from test_workflow import _final_evidence_sufficiency_state
 state=_final_evidence_sufficiency_state(1)
 from novelty_agent_framework.schemas import TaskResearchResult,InsufficientFinalEvidence
 row=TaskResearchResult(task_id='T-1',novelty_point_id='NP-1',status='partial',steps_used=1,evidence_cards=[c.model_copy(update={'evidence_ids':[]}) for c in state['evidence_cards']])
 rows=[]
 for deficient in [False,True]:
  decisions,failures=plan_recovery(paper_id='p',run_id='r',points=[NoveltyPoint(point_id='NP-1',claim='audit')],results=[row],reviews=[review],insufficient=[InsufficientFinalEvidence(novelty_point_id='NP-1',valid_card_count=1,required_card_count=2)] if deficient else [],round_number=1,max_rounds=2)
  rows.append({'deficient':deficient,'cards':len(row.evidence_cards),'decisions':[x.model_dump(mode='json') for x in decisions],'failure_codes':[f.code for f in failures]})
 return rows
case('reviewer_technical_recovery',recovery)

def summary():
 issue=make_failure(FailureCode.MODEL_TRANSPORT,scope=FailureScope(point_id='NP-1'),message='Injected transport failure')
 review=NoveltyPointReview(novelty_point_id='NP-1',status='insufficient_evidence',incomplete_reason='technical_error',execution_issues=[issue])
 request=NoveltyPointReviewRequest(subject_paper_id='p',novelty_point=NoveltyPoint(point_id='NP-1',claim='audit'))
 result=asyncio.run(NoveltyEvidenceReviewer(model_client=object()).summarize_reviews(request,[{'status':'completed','review':review.model_dump(mode='json')}]))
 return {'input_issues':[x.code for x in review.execution_issues],'output_issues':[x.code for x in result.execution_issues],'output_reason':result.incomplete_reason}
case('all_card_failures_lose_issues',summary)

def reader():
 import test_reader_tool_call_harness_integration as f
 rows=[]
 for variant,args2 in [('exact',{'artifact_id':f.ARTIFACT_ID,'max_chars':1000}),('same_actual_range',{'artifact_id':f.ARTIFACT_ID,'max_chars':2000})]:
  with tempfile.TemporaryDirectory() as d:
   low=ReferenceArtifactReaderTool(f.prepare_store(Path(d))); dispatched=[];original=low.ainvoke
   async def count(req):dispatched.append(req);return await original(req)
   low.ainvoke=count
   args={'artifact_id':f.ARTIFACT_ID,'max_chars':1000}
   model=f.ScriptedModelClient(f.tool_request(args,'r1'),f.tool_request(args2,'r2'),ModelResponse(content='done'))
   harness=ToolCallHarness(model,ResearcherToolRegistry([ReaderTool(low)]),config=ToolCallHarnessConfig(reuse_reader_results=True))
   result=asyncio.run(harness.run(system_prompt='test',initial_user_message='test',scope=f.research_scope()))
   payloads=[json.loads(e.message.content) for e in result.trace if e.kind=='tool_result']
   rows.append({'variant':variant,'physical_reads':len(dispatched),'replay':payloads[1].get('reused_result',False),'reader_body_preserved':payloads[0]['read_result']['text']==payloads[1]['read_result']['text'],'last_model_input_chars':sum(len(x.content or '') for x in model.calls[-1][0]),'full_body_occurrences_in_last_prompt':sum((x.content or '').count(f.TEXT.replace('\n','\\n')) for x in model.calls[-1][0])})
 return rows
case('reader_replay_and_range',reader)

def namespace():
 import test_reader_tool_call_harness_integration as f
 rows=[]
 for batch in [False,True]:
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);low=ReferenceArtifactReaderTool(f.prepare_store(root));tool=ReaderTool(low)
   args={'reads':[{'artifact_id':f.ARTIFACT_ID,'max_chars':100}]} if batch else {'artifact_id':f.ARTIFACT_ID,'max_chars':100}
   model=f.ScriptedModelClient(f.tool_request(args,'r1'),ModelResponse(content='done'))
   manager=RuntimeArtifactManager(f.PAPER_ID,run_id='audit',config=RuntimeDebugConfig(output_root=root,archive_root=root/'archive'),diagnostics=[])
   manager.activate()
   try:asyncio.run(ToolCallHarness(model,ResearcherToolRegistry([tool])).run(system_prompt='test',initial_user_message='test',scope=f.research_scope()))
   finally:manager.deactivate()
   diagnosis=inspect_workspace(root/f.PAPER_ID,run_id='audit')
   rows.append({'batch':batch,'errors':diagnosis.get('errors'),'reader_calls':diagnosis.get('reader_calls')})
 return rows
case('namespace_diagnostic_false_positive',namespace)

def finalization():
 import test_tool_call_harness as f
 rows=[]
 for reserve in [False,True]:
  tool=f.ExampleTool();model=f.ScriptedModelClient(*[ModelResponse(content=None,tool_calls=(ModelToolCall(id=str(i),name='example',arguments={'value':'test'}),)) for i in range(2 if not reserve else 1)],ModelResponse(content='done'))
  result=asyncio.run(ToolCallHarness(model,ResearcherToolRegistry([tool]),config=ToolCallHarnessConfig(max_turns=2,max_tool_calls=10,finalize_on_budget=True,reserve_final_turn=reserve)).run(system_prompt='test',initial_user_message='test',scope=f.scope()))
  rows.append({'reserve_final_turn':reserve,'configured_max_turns':2,'actual_calls':len(model.calls),'tools':len(tool.received),'reported_turns':getattr(result,'turns_used',None)})
 return rows
case('unreserved_finalization',finalization)

def config_transport():
 from novelty_agent_framework.config import load_application_config,build_workflow
 rows=[]
 for mode in ['api','web']:
  c=load_application_config(environ={},overrides={'researcher':{'tools':{'database_search':{'providers':{'arxiv':{'search_transport':mode,'min_interval_seconds':0.07,'web_min_interval_seconds':0.17,'timeout_seconds':4,'web_timeout_seconds':6,'max_retries':1,'web_max_retries':0}}}}}})
  source=build_workflow(c).services.task_researcher.tools.get('database_search').tools_by_source['arxiv'].source.search_tool
  obj=source if mode=='api' else source._session
  rows.append({'transport':mode,'class':type(source).__name__,'interval':getattr(obj,'_min_interval',None),'timeout':getattr(obj,'_timeout',None),'max_retries':getattr(obj,'_max_retries',None)})
 return rows
case('config_transport_injection',config_transport)

def web_usage():
 from dataclasses import replace
 from decimal import Decimal
 from novelty_agent_framework.services.model_budget import RunModelBudget
 with tempfile.TemporaryDirectory() as d:
  root=Path(d);budget=RunModelBudget(root/'ledger.json',cap_rmb=Decimal('1'),max_attempts=2)
  manager=RuntimeArtifactManager('audit',config=RuntimeDebugConfig(output_root=root/'runtime'),diagnostics=[])
  event=ModelCallEvent(alias='offline-priced-event',provider='offline',model='deepseek-ai/DeepSeek-V4-Flash',started_at=datetime.now(timezone.utc),duration_ms=0,message_count=1,call_id='injected-usage',phase='START',request_payload={'messages':[{'role':'user','content':'offline event; no transport'}],'max_tokens':8})
  for e in [event,replace(event,phase='RESPONSE_PARSED',provider_usage={'prompt_tokens':10,'completion_tokens':2,'total_tokens':12}),replace(event,phase='COMPLETE',error=ValueError('injected invalid choices after usage'))]:budget(e);manager.record_model_call(e)
  ledger=json.loads((root/'ledger.json').read_text())
  try:budget(replace(event,call_id='unpriced',model='qwen2.5-7b-instruct'));unpriced='allowed'
  except Exception as exc:unpriced=f'{type(exc).__name__}: {exc}'
  return {'network_requests':0,'runtime_usage':manager._llm_call_records[0].get('provider_usage'),'web_attempt':ledger['attempts'][0],'web_unpriced_model':unpriced}
case('web_usage_and_price_boundary',web_usage)
