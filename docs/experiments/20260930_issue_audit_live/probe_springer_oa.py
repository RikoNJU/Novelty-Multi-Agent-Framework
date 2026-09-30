"""Explicit OA configuration: default provider profile disables full-text."""
import json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT),str(ROOT/'backend/src')]
OUT=Path(__file__).resolve().parent
from novelty_agent_framework.config import load_application_config
from novelty_agent_framework.config.experiment import redact_config
from novelty_agent_framework.tools.database_search.providers.springer import build_springer_source
from novelty_agent_framework.core.runtime_artifacts import RuntimeArtifactManager,RuntimeDebugConfig
config=load_application_config(environ={});options=dict(config.researcher.tools.database_search.providers['springer'])
options.update(enabled=True,full_text_mode='openaccess',max_retries=0,timeout_seconds=20)
source=build_springer_source(options)
m=RuntimeArtifactManager('springer-oa',run_id='live',config=RuntimeDebugConfig(output_root=OUT/'probes',archive_root=OUT/'probes-archive',max_model_calls=1,max_physical_provider_requests=6),diagnostics=[]);m.activate()
result={'full_text_mode':'openaccess'}
try:
 hits=source.search_tool.search('keyword:"graph neural network" openaccess:true',limit=2)
 result['hits']=[{'id':x.document_id,'title':x.title} for x in hits]
 result['fulltext']=[]
 for hit in hits[:1]:
  text=source.full_text_tool.fetch(hit.document_id)
  result['fulltext'].append({'id':hit.document_id,'acquired':text is not None,'chars':len(text.text) if text else 0})
  if text:(OUT/'springer-openaccess-text.txt').write_text(text.text)
 m.finish_run('SUCCESS')
except Exception as exc:result.update(error_type=type(exc).__name__,detail=redact_config(str(exc)));m.finish_run('FAILED',error=exc)
finally:
 m.deactivate();result['budget_reservations']=m._provider_dispatch_count
 (OUT/'springer-oa-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
