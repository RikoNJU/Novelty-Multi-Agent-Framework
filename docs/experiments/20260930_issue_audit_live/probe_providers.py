"""Bounded real provider probes; count HTTP transports independently of budget reservations."""
import dataclasses,json,sys,time,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT),str(ROOT/'backend/src')]
OUT=Path(__file__).resolve().parent
import httpx
from backend.env.model_client import _load_dev_env
from novelty_agent_framework.config import load_application_config
from novelty_agent_framework.config.experiment import redact_config
from novelty_agent_framework.core.runtime_artifacts import RuntimeArtifactManager,RuntimeDebugConfig
from novelty_agent_framework.tools.database_search.providers.arxiv import build_arxiv_source
from novelty_agent_framework.tools.database_search.providers.springer import build_springer_source
_load_dev_env()
http_rows=[];rows=[]
original=httpx.Client._send_single_request
def tracked(self,request):
 row={'method':request.method,'host':request.url.host,'path':request.url.path}
 http_rows.append(row)
 try:
  response=original(self,request);row['status']=response.status_code;return response
 except Exception as exc:row['error_type']=type(exc).__name__;raise
httpx.Client._send_single_request=tracked
config=load_application_config(environ={})
manager=RuntimeArtifactManager('provider-probes',run_id='live',config=RuntimeDebugConfig(output_root=OUT/'probes',archive_root=OUT/'probes-archive',max_model_calls=1,max_physical_provider_requests=20),diagnostics=[])
manager.activate()
def save():
 (OUT/'provider-results.json').write_text(json.dumps({'cases':rows,'http_transports':http_rows},ensure_ascii=False,indent=2)+'\n')
def probe(name,fn):
 start=time.monotonic();a=len(http_rows);b=manager._provider_dispatch_count
 row={'case':name};rows.append(row)
 try:
  value=fn()
  if isinstance(value,(list,tuple)):
   row.update(status='success',hits=[{'document_id':x.document_id,'title':x.title,'abstract_chars':len(x.abstract or ''),'full_text_url':getattr(x,'full_text_url',None)} for x in value])
  elif value is None:row.update(status='no_material')
  else:
   row.update(status='success',chars=len(value.text),sha256=hashlib.sha256(value.text.encode()).hexdigest(),content_extent=str(value.content_extent))
   (OUT/(name+'-text.txt')).write_text(value.text)
  return value
 except Exception as e:row.update(status='error',error_type=type(e).__name__,detail=redact_config(str(e)));return None
 finally:
  row.update(elapsed_seconds=round(time.monotonic()-start,3),http_transports=len(http_rows)-a,budget_reservations=manager._provider_dispatch_count-b);save();print(json.dumps(row,ensure_ascii=False),flush=True)
try:
 arxiv=dict(config.researcher.tools.database_search.providers['arxiv'])
 api=build_arxiv_source({**arxiv,'enabled':True,'search_transport':'api','max_retries':0,'timeout_seconds':15})
 probe('arxiv-api-search',lambda:api.search_tool.search('abs:"graph neural network"',limit=2))
 web=build_arxiv_source({**arxiv,'enabled':True,'search_transport':'web','web_max_retries':0,'web_timeout_seconds':25})
 probe('arxiv-web-search',lambda:web.search_tool.search('abs:"graph neural network"',limit=2))
 # Public exact paper gives a fixed retrievable source for semantic controls.
 probe('arxiv-web-fulltext',lambda:web.full_text_tool.fetch('1706.03762'))
 springer=dict(config.researcher.tools.database_search.providers['springer'])
 source=build_springer_source({**springer,'enabled':True,'max_retries':0,'timeout_seconds':20})
 hits=probe('springer-search',lambda:source.search_tool.search('keyword:"graph neural network"',limit=2))
 if hits:probe('springer-fulltext',lambda:source.full_text_tool.fetch(hits[0].document_id))
 # An open-access public known DOI isolates OA access from the arbitrary search hit.
 probe('springer-openaccess-known',lambda:source.full_text_tool.fetch('10.1038/s41598-023-43383-4'))
finally:
 manager.finish_run('SUCCESS');manager.deactivate();httpx.Client._send_single_request=original;save()
