"""Cold adapter identifier probe: raw DOI versus DOI-prefixed identifier."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT),str(ROOT/'backend/src')]
OUT=Path(__file__).resolve().parent
import httpx
from novelty_agent_framework.config import load_application_config
from novelty_agent_framework.tools.database_search.providers.springer import build_springer_source
from novelty_agent_framework.config.experiment import redact_config
from novelty_agent_framework.core.runtime_artifacts import RuntimeArtifactManager,RuntimeDebugConfig
c=load_application_config(environ={});opts=dict(c.researcher.tools.database_search.providers['springer']);opts.update(enabled=True,full_text_mode='openaccess',max_retries=0,timeout_seconds=20)
s=build_springer_source(opts);m=RuntimeArtifactManager('springer-identifiers',run_id='live',config=RuntimeDebugConfig(output_root=OUT/'probes',archive_root=OUT/'probes-archive',max_physical_provider_requests=3),diagnostics=[])
http_rows=[];orig=httpx.Client._send_single_request
def tracked(self,req):
 r=orig(self,req);http_rows.append({'host':req.url.host,'path':req.url.path,'status':r.status_code});return r
httpx.Client._send_single_request=tracked;m.activate();rows=[]
try:
 for identifier in ['10.1038/s41598-023-43383-4','doi:10.1038/s41598-023-43383-4']:
  count=len(http_rows);row={'identifier':identifier}
  try:
   t=s.full_text_tool.fetch(identifier);row.update(acquired=t is not None,chars=len(t.text) if t else 0)
   if t:(OUT/'springer-oa-identifier-text.txt').write_text(t.text)
  except Exception as e:row.update(error_type=type(e).__name__,detail=redact_config(str(e)))
  row['http_transports']=len(http_rows)-count;rows.append(row)
 m.finish_run('SUCCESS')
finally:
 m.deactivate();httpx.Client._send_single_request=orig
 result={'cases':rows,'http_transports':http_rows,'budget_reservations':m._provider_dispatch_count};(OUT/'springer-identifier-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
