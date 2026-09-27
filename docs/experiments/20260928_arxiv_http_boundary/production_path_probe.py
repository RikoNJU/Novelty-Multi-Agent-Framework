"""Capture production serialization and parse the actual successful response, without network."""
import hashlib,json,sys
from pathlib import Path
from urllib.parse import parse_qsl,urlsplit
import httpx
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'backend/src')]
from novelty_agent_framework.tools.database_search.providers.arxiv_scheduler import ArxivRequestScheduler
from novelty_agent_framework.tools.database_search.providers.arxiv import ArxivSearchTool
body=(OUT/'canonical_example.body').read_bytes()
rows=[]
for status in (200,406):
 captured=[]
 def handler(request):
  captured.append({'url':str(request.url),'wire_raw_path':request.url.raw_path.decode(),'parameters':dict(parse_qsl(request.url.query.decode(),keep_blank_values=True))})
  return httpx.Response(status,content=body if status==200 else b'',headers={'content-type':'application/atom+xml'} if status==200 else {},request=request)
 with httpx.Client(transport=httpx.MockTransport(handler)) as client:
  scheduler=ArxivRequestScheduler(client=client,min_interval=0,max_retries=0,metadata_batch_enabled=False)
  try:
   tool=ArxivSearchTool(scheduler=scheduler)
   row={'injected_http':status}
   try:
    hits=list(tool.search('all:electron',limit=1));row.update(hit_count=len(hits),document_ids=[h.document_id for h in hits],titles=[h.title for h in hits])
   except Exception as exc:row['exception_type']=type(exc).__name__
   row['requests']=captured;rows.append(row)
  finally:scheduler.shutdown()
assert rows[0]['hit_count']==1 and rows[1]['exception_type']=='HTTPStatusError'
wire=rows[0]['requests'][0]['url'];assert wire=='https://export.arxiv.org/api/query?search_query=all%3Aelectron&start=0&max_results=1'
equivalent=all(dict(parse_qsl(urlsplit(wire).query,keep_blank_values=True))==r['requests'][0]['parameters'] for r in rows)
payload={'network_calls':0,'model_calls':0,'successful_response_sha256':hashlib.sha256(body).hexdigest(),'production_url_matches_live_failing_case':True,'same_parameters_across_cases':equivalent,'results':rows}
(OUT/'production_path_results.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n');print(json.dumps(payload,ensure_ascii=False))
