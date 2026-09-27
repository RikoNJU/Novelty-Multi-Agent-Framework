from datetime import UTC, datetime
from pathlib import Path
import hashlib,json,time
from urllib.parse import quote,quote_plus
import httpx
root=Path('docs/experiments/20260927_harness_config_closure')
query='all:"graph neural network"'
base='https://export.arxiv.org/api/query?search_query='
suffix='&start=0&max_results=1'
ua='NoveltyFramework-Audit/1.0'
variants=[
 ('export_percent20_atom',base+quote(query,safe='')+suffix,'application/atom+xml'),
 ('export_plus_atom',base+quote_plus(query,safe='')+suffix,'application/atom+xml'),
 ('export_percent20_any',base+quote(query,safe='')+suffix,'*/*'),
 ('arxiv_percent20_atom','https://arxiv.org/api/query?search_query='+quote(query,safe='')+suffix,'application/atom+xml'),
]
results=[]
for name,url,accept in variants:
 record={'name':name,'requested_at':datetime.now(UTC).isoformat(),'method':'GET','url':url,'request_headers':{'Accept':accept,'User-Agent':ua},'follow_redirects':False,'retries':0}
 start=time.monotonic()
 try:
  with httpx.Client(timeout=20,follow_redirects=False) as client:
   response=client.get(url,headers=record['request_headers'])
  content=response.content
  record.update(status_code=response.status_code,response_headers={name:value for name,value in response.headers.items() if name.lower() in {'date','server','content-type','content-length','location','cache-control','via','retry-after'}},body_first_200_bytes=content[:200].decode('utf-8',errors='replace'),response_body_sha256=hashlib.sha256(content).hexdigest(),response_body_bytes=len(content))
 except Exception as exc:
  record.update(status_code=None,exception_type=type(exc).__name__)
 record['duration_seconds']=round(time.monotonic()-start,3)
 results.append(record)
(root/'arxiv_public_probe.json').write_text(json.dumps({'performed_at':datetime.now(UTC).isoformat(),'authorization':'at most four public fixed-query GET requests; no paper-derived queries/model calls','query':query,'physical_get_attempts':len(results),'results':results},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2))
