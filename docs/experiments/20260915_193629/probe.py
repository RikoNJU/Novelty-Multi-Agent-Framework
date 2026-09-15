"""One arXiv metadata API request, no workflow, batching, or retries."""
import json,time,socket,os,sys
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urlsplit
import httpx
out=Path(__file__).resolve().parent
trust_env='--no-env-proxy' not in sys.argv
url='https://export.arxiv.org/api/query';params={'id_list':'1902.08730','max_results':1}
r={'started_at':datetime.now(timezone.utc).isoformat(),'url':url,'params':params,'http_requests_planned':1,'retries':0,'follow_redirects':False,'timeout_seconds':30,'trust_env':trust_env}
r['proxy_environment']={k: {'configured':bool(os.getenv(k)),'host':urlsplit(os.getenv(k,'')).hostname} for k in ['HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy']}
try:r['resolved_addresses']=sorted({x[4][0] for x in socket.getaddrinfo('export.arxiv.org',443,type=socket.SOCK_STREAM)})
except OSError as e:r['dns_error']=str(e)
start=time.monotonic()
try:
 with httpx.Client(timeout=30,follow_redirects=False,trust_env=trust_env) as client:
  response=client.get(url,params=params)
  r.update(status=response.status_code,http_version=response.http_version,headers=dict(response.headers),request_headers=dict(response.request.headers),body=response.text)
except Exception as e:r.update(error_type=type(e).__name__,error=str(e))
r.update(elapsed_seconds=time.monotonic()-start,finished_at=datetime.now(timezone.utc).isoformat())
(out/('result.json' if trust_env else 'no_env_proxy_result.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(r,ensure_ascii=False))
