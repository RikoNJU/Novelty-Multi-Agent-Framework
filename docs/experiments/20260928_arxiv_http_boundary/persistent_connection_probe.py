"""Four ABBA requests on one direct HTTP/1.1 client, capturing connection event names only."""
import hashlib,json,time,subprocess
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import parse_qsl,urlsplit
import httpx
OUT=Path(__file__).resolve().parent
DEST=OUT/'persistent_results.json'
URLS=[('A_raw','https://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=1'),('B_encoded','https://export.arxiv.org/api/query?search_query=all%3Aelectron&start=0&max_results=1'),('B_encoded_repeat','https://export.arxiv.org/api/query?search_query=all%3Aelectron&start=0&max_results=1'),('A_raw_repeat','https://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=1')]
KEEP={'date','server','content-type','content-length','via','cache-control','x-cache','x-served-by','age','vary'}
def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');args=p.parse_args()
 if not args.execute:print('4 direct requests; --execute required');return
 if DEST.exists():raise SystemExit('Refusing to overwrite or rerun existing probe')
 result={'started_at':datetime.now(timezone.utc).isoformat(),'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'trust_env':False,'http2':False,'request_count_limit':4,'new_model_calls':0,'results':[]};last=None
 with httpx.Client(trust_env=False,http2=False,follow_redirects=False,timeout=12,headers={'User-Agent':'NoveltyFramework-Audit/1.0','Accept':'application/atom+xml'},limits=httpx.Limits(max_connections=1,max_keepalive_connections=1,keepalive_expiry=60)) as client:
  for name,url in URLS:
   if last is not None:time.sleep(max(0,4-(time.monotonic()-last)))
   last=time.monotonic();events=[]
   def trace(event,info):events.append(event)
   row={'case':name,'url':url,'decoded_parameters':dict(parse_qsl(urlsplit(url).query,keep_blank_values=True)),'requested_at':datetime.now(timezone.utc).isoformat(),'status_code':None};body=b''
   try:
    response=client.get(url,extensions={'trace':trace});body=response.content
    row.update(status_code=response.status_code,wire_raw_path=response.request.url.raw_path.decode(),response_headers={k:v for k,v in response.headers.items() if k.lower() in KEEP})
    stream=response.extensions.get('network_stream');ssl=stream.get_extra_info('ssl_object') if stream else None
    if ssl:
     row['tls_leaf_sha256']=hashlib.sha256(ssl.getpeercert(binary_form=True)).hexdigest()
     row['tls_issuer']=ssl.getpeercert().get('issuer')
   except Exception as exc:row['exception_type']=type(exc).__name__
   row.update(body_bytes=len(body),body_sha256=hashlib.sha256(body).hexdigest(),transport_events=events,duration_seconds=round(time.monotonic()-last,3));(OUT/(name+'.body')).write_bytes(body);result['results'].append(row);DEST.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'case':name,'status':row['status_code'],'new_tcp_connections':events.count('connection.connect_tcp.started')}),flush=True)
 result['requests_attempted']=len(result['results']);result['tcp_connections_started']=sum(r['transport_events'].count('connection.connect_tcp.started') for r in result['results']);result['same_decoded_parameters']=len({json.dumps(r['decoded_parameters'],sort_keys=True) for r in result['results']})==1;result['finished_at']=datetime.now(timezone.utc).isoformat();DEST.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
