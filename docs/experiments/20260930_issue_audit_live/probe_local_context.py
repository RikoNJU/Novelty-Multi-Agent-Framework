"""Real local inference/context boundary probes; no external model service."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT),str(ROOT/'backend/src'),str(ROOT/'tests')]
OUT=Path(__file__).resolve().parent
from backend.env.model_client import ModelProfile,OpenAICompatibleChatClient,ChatMessage,ModelCallOptions
from backend.env.context_admission import ContextAdmissionConfig
from novelty_agent_framework.core.runtime_artifacts import RuntimeArtifactManager,RuntimeDebugConfig
from novelty_agent_framework.workflows.research_task import _execution_failure
from test_tool_call_harness import scope
rows=[]
def invoke(client,messages):
 try:
  r=client.complete(messages,options=ModelCallOptions(max_tokens=3,temperature=0,timeout_seconds=45,tool_choice='none'))
  return {'status':'success','usage':dict(r.usage),'finish_reason':r.raw.get('choices',[{}])[0].get('finish_reason'),'content':r.content}
 except Exception as e:return {'status':'failed','error_type':type(e).__name__,'detail':str(e),'research_failure_code':_execution_failure(scope(),e).code}
for mode,enabled in [('off',True),('enforce',True),('off',False)]:
 name=f'{mode}-debug-{enabled}';m=RuntimeArtifactManager('local-context',run_id=name,config=RuntimeDebugConfig(enabled=enabled,output_root=OUT/'local-context',archive_root=OUT/'local-context-archive',max_model_calls=1,max_physical_provider_requests=1),diagnostics=[])
 client=OpenAICompatibleChatClient(ModelProfile(alias='local-context',model='qwen2.5-7b-instruct',base_url='http://127.0.0.1:8000/v1',api_key='local',context_window=32768,context_admission=ContextAdmissionConfig(mode=mode,counter='vllm' if mode=='enforce' else 'none',vllm_tools_mode='v0_8_5_kwargs',on_unavailable='reject')))
 m.activate()
 try:
  first='audit '*34000 if enabled else 'Count aloud from one to ten.'
  row={'case':name,'configured_model_cap':1,'first':invoke(client,[ChatMessage(role='user',content=first)]),'second':invoke(client,[ChatMessage(role='user',content='Count aloud from one to ten.')])}
  row['runtime_counter']=m._llm_call_counter;rows.append(row);m.finish_run('SUCCESS')
 finally:m.deactivate()
 (OUT/'local-context-results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');print(json.dumps(row,ensure_ascii=False),flush=True)
