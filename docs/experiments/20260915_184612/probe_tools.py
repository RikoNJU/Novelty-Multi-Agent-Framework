"""Supplementary probes, kept separate from the three production workflows."""
import sys,json,os,time,asyncio,threading
from dataclasses import asdict
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
ROOT=Path.cwd();sys.path[:0]=[str(ROOT),str(ROOT/'backend/src')]
from backend.env.model_client import _load_dev_env
from novelty_agent_framework.config import load_application_config
from novelty_agent_framework.tools.database_search.factory import build_retrieval_source
from novelty_agent_framework.tools.database_search.providers.arxiv_scheduler import ArxivRequestScheduler
from novelty_agent_framework.tools.database_search.providers.arxiv import ArxivMetadataTool
from novelty_agent_framework.schemas import TaskResearchRequest,WebSearchArguments
from novelty_agent_framework.tools.web_search_backend import BaiduSearchBackend
from novelty_agent_framework.tools.web_search import WebSearchTool
from novelty_agent_framework.persistence import ReferenceStore
_load_dev_env();BASE=Path(__file__).resolve().parent; mode=sys.argv[1];out=BASE/'supplementary'/mode;out.mkdir(parents=True,exist_ok=True)
keys=[v for k,v in os.environ.items() if ('KEY' in k or 'TOKEN' in k) and len(v)>6]
def clean(s):
 for v in keys:s=s.replace(v,'<redacted>')
 return s
payload={'probe':mode,'started_at':datetime.now(timezone.utc).isoformat(),'supplementary':True};start=time.monotonic()
import httpx
_original_send=httpx.Client.send
def observed_send(self,request,*args,**kwargs):
 response=_original_send(self,request,*args,**kwargs)
 if request.url.host=='api.springernature.com':
  payload.setdefault('http_events',[]).append({'path':request.url.path,'query':request.url.params.get('q'),'status':response.status_code,'body':response.text[:4000] if response.status_code!=200 else None})
 return response
httpx.Client.send=observed_send
def dump():
 (out/'result.json').write_text(clean(json.dumps(payload,ensure_ascii=False,indent=2,default=str)))
def scope():
 p=next(p for p in sorted((BASE/'01_arxiv').glob('*/runtime/*/stages/*run_research_task/input.json')) if json.loads(p.read_text())['current_task'].get('language')=='en')
 j=json.loads(p.read_text());payload['scope_source']=str(p.relative_to(BASE))
 return TaskResearchRequest(subject_paper_id=j['subject_paper_id'],run_id='supplementary-'+mode,novelty_point=j['current_point'],research_task=j['current_task'],search_plan=j['current_search_plan'])
try:
 if mode=='batch':
  # Graph neural network metadata IDs; synchronise callers to exercise batching.
  ids=['1609.02907','1706.02216','1902.10197','2006.10637','1609.02907','1706.02216']
  scheduler=ArxivRequestScheduler(min_interval=4,timeout=20,max_retries=1,metadata_batch_window_ms=200,metadata_batch_max_size=32)
  tool=ArxivMetadataTool(scheduler=scheduler);barrier=threading.Barrier(len(ids))
  def resolve(i):
   barrier.wait()
   try:
    hit=tool.resolve(i);return {'id':i,'resolved':hit is not None,'hit':asdict(hit) if hit else None}
   except Exception as e:return {'id':i,'resolved':False,'error':clean(f'{type(e).__name__}: {e}')}
  try:
   with ThreadPoolExecutor(max_workers=len(ids)) as pool:payload['results']=list(pool.map(resolve,ids))
  finally:payload['metrics']=scheduler.snapshot_metrics(include_events=True);scheduler.shutdown()
 elif mode=='compare':
  request=scope();c=load_application_config();payload['search_plan']=request.search_plan.model_dump(mode='json');payload['providers']={}
  db=c.researcher.tools.database_search
  for provider in ['arxiv','springer']:
   db.providers[provider]['enabled']=True
   source=build_retrieval_source({'active_source':provider,'sources':db.providers})
   rows=[]
   for q in source.query_adapter.compile(request.search_plan):
    row={'query':q.query}
    try:row['hits']=[asdict(h) for h in source.search_tool.search(q.query,limit=8)]
    except Exception as e:row['error']=clean(f'{type(e).__name__}: {e}')
    rows.append(row);payload['providers'][provider]=rows;dump()
  source=build_retrieval_source({'active_source':'springer','sources':db.providers})
  failing_query=None
  for path in sorted((BASE/'02_arxiv_springer').glob('*/runtime/*/tools/*database_search.json')):
   event=json.loads(path.read_text())
   for execution in (event.get('raw_result') or {}).get('payload',{}).get('search_executions',[]):
    if '404' in str(execution.get('error','')) and execution.get('source_id')=='springer':
     failing_query=execution['query'];break
   if failing_query:break
  if failing_query:
   diagnostic={'query':failing_query,'purpose':'reproduce observed Meta API 404'}
   try:diagnostic['hits']=[asdict(h) for h in source.search_tool.search(failing_query,limit=8)]
   except Exception as e:diagnostic['error']=clean(f'{type(e).__name__}: {e}')
   payload['springer_404_diagnostic']=diagnostic
 elif mode=='web':
  request=scope();tool=WebSearchTool(BaiduSearchBackend(),ReferenceStore(out),default_max_results=5)
  args=WebSearchArguments(query='dynamic graph neural network distributed training',max_results=5)
  r=asyncio.run(tool.ainvoke(args,scope=request));payload['observation']=r.model_dump(mode='json');payload['backend_diagnostics']=tool.backend.last_diagnostics
 else:raise ValueError(mode)
except Exception as e:payload['error']=clean(f'{type(e).__name__}: {e}')
finally:
 payload['finished_at']=datetime.now(timezone.utc).isoformat();payload['duration_seconds']=time.monotonic()-start;dump();print(clean(json.dumps(payload,ensure_ascii=False,default=str)))
