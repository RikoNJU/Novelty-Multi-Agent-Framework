"""Explicit, bounded arXiv investigation. Run only with --execute; never retries."""
from datetime import datetime, timezone
from pathlib import Path
import argparse, hashlib, json, os, subprocess, tempfile, time
from urllib.parse import urlencode, quote
import httpx

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SOURCE = ROOT / 'docs/experiments/runtime/MF2033k6lC_2026-09-27/run-d55196716d254641a84cf1b0c19f14e9/workspace/MF2033k6lC/retrieval-plans.json'
plans = json.loads(SOURCE.read_text())['novelty_point_plans']
model_query = next(x for x in plans if x['novelty_point_id'] == 'NP-4')['executed_queries'][0]['query']
human_query = 'all:"graph neural network"'
HEADERS = {'Accept': 'application/atom+xml', 'User-Agent': 'NoveltyFramework-Audit/1.0'}
SELECTED = {'date','server','content-type','content-length','location','via','cache-control','retry-after','x-cache','x-served-by'}
CASES = [
 ('httpx_env_human','httpx',True, human_query,None),
 ('httpx_env_model','httpx',True, model_query,None),
 ('httpx_direct_human','httpx',False,human_query,None),
 ('httpx_direct_model','httpx',False,model_query,None),
 ('curl_env_human','curl',True,human_query,None),
 ('curl_env_model','curl',True,model_query,None),
 ('httpx_env_known_id','httpx',True,None,'1706.03762'),
 ('httpx_env_human_repeat','httpx',True,human_query,None),
]

def url_for(query, known_id):
    params = {'id_list':known_id} if known_id else {'search_query':query}
    params.update(start=0,max_results=1)
    return 'https://export.arxiv.org/api/query?' + urlencode(params,quote_via=quote)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    if not args.execute:
        print(json.dumps({'requests':len(CASES),'destination':'https://export.arxiv.org/api/query','new_model_calls':0,'requires_explicit_execute':True}));return
    result_file=OUT/'network_results.json'
    if result_file.exists():raise SystemExit('Refusing to overwrite an existing probe or silently repeat network requests.')
    payload={'started_at':datetime.now(timezone.utc).isoformat(),'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'request_limit':8,'automatic_retries':0,'follow_redirects':False,'new_model_calls':0,'proxy_environment_names':[k for k in os.environ if k.lower() in {'http_proxy','https_proxy','all_proxy','no_proxy'}],'httpx_version':httpx.__version__,'curl_version':subprocess.check_output(['curl','--version'],text=True).splitlines()[0],'request_headers':HEADERS,'model_query_source':SOURCE.relative_to(ROOT).as_posix(),'model_query_source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'results':[]}
    result_file.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    last_start=None
    for name,client,trust_env,query,known_id in CASES:
        if last_start is not None:time.sleep(max(0,4-(time.monotonic()-last_start)))
        last_start=time.monotonic();url=url_for(query,known_id)
        row={'case':name,'client':client,'trust_env':trust_env,'requested_at':datetime.now(timezone.utc).isoformat(),'url':url,'query_kind':'known_id' if known_id else ('archived_model' if query==model_query else 'human_fixed'),'status_code':None}
        body=b''
        try:
            if client=='httpx':
                with httpx.Client(timeout=httpx.Timeout(10,connect=6),trust_env=trust_env,follow_redirects=False,http2=False) as c:
                    response=c.get(url,headers=HEADERS)
                row.update(status_code=response.status_code,http_version=response.http_version,response_headers={k:v for k,v in response.headers.items() if k.lower() in SELECTED});body=response.content
            else:
                with tempfile.TemporaryDirectory() as temp:
                    hp=Path(temp)/'headers';bp=Path(temp)/'body'
                    command=['curl','--silent','--show-error','--http1.1','--retry','0','--max-time','12','--connect-timeout','6','--dump-header',str(hp),'--output',str(bp),'--write-out','%{http_code}','--user-agent',HEADERS['User-Agent'],'--header','Accept: '+HEADERS['Accept'],url]
                    r=subprocess.run(command,capture_output=True,timeout=15)
                    row.update(curl_exit_code=r.returncode,stderr_sha256=hashlib.sha256(r.stderr).hexdigest())
                    code=r.stdout.decode().strip();row['status_code']=int(code) if code.isdigit() and code!='000' else None
                    headers={}
                    if hp.exists():
                        for line in hp.read_text(errors='replace').splitlines():
                            if ':' in line:
                                k,v=line.split(':',1)
                                if k.lower() in SELECTED:headers[k.lower()]=v.strip()
                    row['response_headers']=headers;body=bp.read_bytes() if bp.exists() else b''
        except Exception as exc:
            row['exception_type']=type(exc).__name__
            row['exception_text_sha256']=hashlib.sha256(str(exc).encode()).hexdigest()
        row.update(duration_seconds=round(time.monotonic()-last_start,3),body_bytes=len(body),body_sha256=hashlib.sha256(body).hexdigest(),body_saved_bytes=min(len(body),65536),body_truncated=len(body)>65536)
        (OUT/(name+'.body')).write_bytes(body[:65536]);payload['results'].append(row)
        result_file.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({k:row.get(k) for k in ('case','status_code','exception_type','curl_exit_code','body_bytes')},ensure_ascii=False),flush=True)
    payload['finished_at']=datetime.now(timezone.utc).isoformat();payload['requests_attempted']=len(payload['results']);result_file.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
