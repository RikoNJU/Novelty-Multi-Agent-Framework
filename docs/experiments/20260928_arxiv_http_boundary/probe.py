"""One-shot, rate-limited public endpoint diagnostics; no model calls or credentials."""
import argparse,hashlib,json,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
import httpx
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
UA='NoveltyFramework-Audit/1.0'
QUERY='https://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=1'
CASES=[
 ('canonical_example',QUERY,{}),
 ('project_identified_ua',QUERY,{'user-agent':UA+' (+https://github.com/RikoNJU/Novelty-Multi-Agent-Framework)'}),
 ('httpx_identified_ua',QUERY,{'user-agent':'python-httpx/'+httpx.__version__}),
 ('no_user_agent',QUERY,{'user-agent':None}),
 ('identity_encoding',QUERY,{'accept-encoding':'identity'}),
 ('documented_http','http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=1',{}),
 ('minimal_query','https://export.arxiv.org/api/query?search_query=all:electron',{}),
 ('malformed_id','https://export.arxiv.org/api/query?id_list=1234.12345',{}),
 ('export_abstract','https://export.arxiv.org/abs/1706.03762',{'accept':'text/html'}),
 ('main_abstract','https://arxiv.org/abs/1706.03762',{'accept':'text/html'}),
 ('main_web_search','https://arxiv.org/search/?query=electron&searchtype=all&abstracts=show&order=-announced_date_first&size=25',{'accept':'text/html'}),
 ('official_status','https://status.arxiv.org/',{'accept':'text/html'}),
]
KEEP={'date','server','content-type','content-length','location','via','cache-control','retry-after','x-cache','x-served-by','x-squid-error','x-webcache-source','x-webcache-request-guid'}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');a=parser.parse_args()
 if not a.execute:print(json.dumps({'requests':len(CASES),'model_calls':0,'automatic_retries':0}));return
 target=OUT/'results.json'
 if target.exists():raise SystemExit('Existing experiment is immutable; no silent rerun.')
 payload={'started_at':datetime.now(timezone.utc).isoformat(),'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'request_limit':len(CASES),'new_model_calls':0,'retries':0,'follow_redirects':False,'trust_env':True,'results':[]}
 target.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n');last=None
 for name,url,changes in CASES:
  if last is not None:time.sleep(max(0,4-(time.monotonic()-last)))
  last=time.monotonic();body=b''
  with httpx.Client(timeout=httpx.Timeout(12,connect=6),follow_redirects=False,trust_env=True,http2=False) as client:
   headers={'accept':'application/atom+xml','user-agent':UA}
   headers.update(changes)
   for key,value in headers.items():
    if value is None:client.headers.pop(key,None)
    else:client.headers[key]=value
   row={'case':name,'url':url,'requested_at':datetime.now(timezone.utc).isoformat(),'request_headers':dict(client.headers),'status_code':None}
   try:
    response=client.get(url);body=response.content
    row.update(status_code=response.status_code,http_version=response.http_version,response_headers={k:v for k,v in response.headers.items() if k.lower() in KEEP})
   except Exception as exc:row.update(exception_type=type(exc).__name__,exception_sha256=hashlib.sha256(str(exc).encode()).hexdigest())
  row.update(duration_seconds=round(time.monotonic()-last,3),body_bytes=len(body),body_sha256=hashlib.sha256(body).hexdigest(),saved_bytes=min(len(body),262144),truncated=len(body)>262144)
  (OUT/(name+'.body')).write_bytes(body[:262144]);payload['results'].append(row);target.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:row.get(k) for k in ('case','status_code','exception_type','body_bytes')}),flush=True)
 payload['finished_at']=datetime.now(timezone.utc).isoformat();payload['requests_attempted']=len(payload['results']);target.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
