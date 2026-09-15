"""Run one real, isolated PaperInput provider trial; no production patches."""
import sys, os, json, time, threading, traceback, hashlib, shutil
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path.cwd(); sys.path[:0]=[str(ROOT),str(ROOT/'backend/src'),str(ROOT/'scripts')]
from backend.env.model_client import _load_dev_env
from novelty_agent_framework.config import load_application_config, effective_safe_config, build_standard_full_workflow
from novelty_agent_framework.schemas import PaperInput
from novelty_agent_framework.processing import prepare_paper_input_references
from novelty_agent_framework.core.run_identity import file_run_identity
from novelty_agent_framework.tools.database_search.providers import arxiv_scheduler
from run_full_pipeline_experiment import Recorder, _wrap_workflow
import httpx
BASE=Path(__file__).resolve().parent; number=int(sys.argv[1]); out=BASE/f'{number:02d}_{["arxiv","arxiv_springer","arxiv_springer_web"][number-1]}'
out.mkdir(exist_ok=True)
def now(): return datetime.now(timezone.utc).isoformat()
def write(name,data):
    p=out/name; tmp=p.with_suffix(p.suffix+'.tmp'); tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2,default=str)); tmp.replace(p)
_load_dev_env()
secrets=[v for k,v in os.environ.items() if any(s in k.upper() for s in ['API_KEY','TOKEN','SECRET']) and len(v)>6]
def clean(s):
    for v in secrets:s=s.replace(v,'<redacted>')
    return s
http_events=[]; lock=threading.Lock()
def event(request,response=None,error=None):
    row={'at':now(),'host':request.url.host,'path':request.url.path,'status':response.status_code if response is not None else None,'error':clean(str(error)) if error else None}
    with lock:
        http_events.append(row)
        with (out/'http_events.jsonl').open('a') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
orig_send=httpx.Client.send
async_send=httpx.AsyncClient.send
def send(self,request,*a,**k):
    try:r=orig_send(self,request,*a,**k)
    except Exception as e:event(request,error=e);raise
    event(request,r);return r
async def asend(self,request,*a,**k):
    try:r=await async_send(self,request,*a,**k)
    except Exception as e:event(request,error=e);raise
    event(request,r);return r
httpx.Client.send=send;httpx.AsyncClient.send=asend
rec=Recorder();rec.install_model_hook()
manifest={'trial':number,'started_at':now(),'status':'RUNNING','entrypoint':'paper_input','source_pdf':'examples/MF2033k6lC.pdf','pdf_sha256':hashlib.sha256((ROOT/'examples/MF2033k6lC.pdf').read_bytes()).hexdigest()}
write('run.json',manifest)
stop=threading.Event()
def snapshot():
    s=arxiv_scheduler._SHARED_SCHEDULER
    if s:write('arxiv_metrics.json',s.snapshot_metrics(include_events=True))
    write('model_calls.json',rec.model_calls);write('tool_events.json',dict(rec.tool_events))
def monitor():
    while not stop.wait(20):snapshot()
threading.Thread(target=monitor,daemon=True).start()
start=time.monotonic();workflow=None
try:
    config=load_application_config()
    for key,value in config.researcher.tools.database_search.providers.items():value['enabled']=key=='arxiv' or (number>=2 and key=='springer')
    config.researcher.tools.web_search.enabled=number==3
    config.project.runtime_debug.output_root=str(out)
    config.project.runtime_debug.archive_root=str(out/'runtime_archive')
    write('effective_config.json',effective_safe_config(config))
    paper_path=BASE/'input'/'MF2033k6lC'/'paper-input'/'others'/'paper.json'
    paper=PaperInput.model_validate_json(paper_path.read_text())
    manifest['paper_json_sha256']=hashlib.sha256(paper_path.read_bytes()).hexdigest()
    print(f'{now()} build workflow trial {number}',flush=True)
    workflow=build_standard_full_workflow(config,output_root=out)
    _wrap_workflow(workflow,rec)
    print(f'{now()} prepare references',flush=True)
    b=prepare_paper_input_references(paper,stable_output_root=BASE/'input',run_output_root=out,max_concurrency=config.project.workflow.max_concurrency)
    write('reference_bootstrap.json',b.model_dump(mode='json'))
    print(f'{now()} workflow start',flush=True)
    result=workflow.run(paper,run_identity=file_run_identity('paper_input',paper_path,project_root=ROOT))
    write('result.json',result.model_dump(mode='json'))
    manifest['status']='SUCCESS'
except BaseException as e:
    manifest['status']='FAILED';manifest['error']=clean(f'{type(e).__name__}: {e}')
    (out/'exception.txt').write_text(clean(traceback.format_exc()))
finally:
    stop.set();snapshot()
    manifest.update(finished_at=now(),duration_seconds=time.monotonic()-start,rendered_report_path=getattr(workflow,'last_rendered_report_path',None),runtime_run_id=getattr(workflow,'last_runtime_run_id',None))
    write('run.json',manifest)
    print(json.dumps(manifest,ensure_ascii=False),flush=True)
