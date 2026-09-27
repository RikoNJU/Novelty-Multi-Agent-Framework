"""Bounded production web-channel probe using queries from the new live run."""
import hashlib,json,sys,time
from pathlib import Path
from datetime import datetime,timezone
import httpx
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'backend/src')]
from novelty_agent_framework.tools.database_search.providers.arxiv_web import ArxivWebSession,ArxivWebSearchTool
if (OUT/'web_probe_results.json').exists():raise SystemExit('Refusing to overwrite prior run')
rt=next((OUT/'runs/0001/MF2033k6lC/runtime').iterdir())
queries=[]
for f in sorted((rt/'stages').glob('*run_research_task/output.json')):
 for row in json.loads(f.read_text())['task_research_results']:
  for e in row['search_executions']:
   if e['status']=='failed' and e['query'] not in queries:queries.append(e['query'])
queries=queries[:2]+['all:"graph neural network"']
responses=[]
def record(response):
 response.read();body=response.content
 name=f'web_response_{len(responses)+1:02d}.body';(OUT/name).write_bytes(body)
 responses.append({'url':str(response.request.url),'status_code':response.status_code,'at':datetime.now(timezone.utc).isoformat(),'body_file':name,'body_bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()})
client=httpx.Client(timeout=25,follow_redirects=False,event_hooks={'response':[record]})
session=ArxivWebSession(client=client,min_interval=8,max_retries=0,timeout=25,max_consecutive_failures=4)
tool=ArxivWebSearchTool(session=session)
results=[]
for query in queries:
 row={'query':query}
 try:
  hits=tool.search(query,limit=3)
  row['hits']=[{'document_id':h.document_id,'title':h.title,'url':h.url,'abstract':h.abstract} for h in hits]
 except Exception as exc:row.update(exception_type=type(exc).__name__,message=str(exc))
 results.append(row)
 (OUT/'web_probe_results.json').write_text(json.dumps({'model_calls':0,'results':results,'responses':responses,'stats':tool.stats()},ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'query':query,'hits':len(row.get('hits',[])),'error':row.get('exception_type')}),flush=True)
client.close()
