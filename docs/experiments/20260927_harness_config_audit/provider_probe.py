"""Bounded, read-only provider diagnostics. No LLM or paid endpoints."""
from __future__ import annotations
import json, os, sys, time
from pathlib import Path
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'backend/src')]
from dotenv import load_dotenv
import httpx
from novelty_agent_framework.config.loader import load_application_config
from novelty_agent_framework.tools.database_search.factory import build_source_registry
from novelty_agent_framework.tools.database_search.providers.arxiv import reset_shared_arxiv_scheduler
load_dotenv(ROOT / 'backend/.env', override=False)
base = Path(__file__).resolve().parent
out = {'started_at': datetime.now(timezone.utc).isoformat(), 'scope': 'read_only_provider_probe_no_llm', 'http': [], 'probes': []}
secret_names = ['ELSEVIER_API_KEY','ELSEVIER_INST_TOKEN','SPRINGER_NATURE_META_API_KEY','SPRINGER_NATURE_OPEN_ACCESS_API_KEY','SPRINGER_NATURE_TDM_API_METRIC','IEEE_XPLORE_API_KEY','BAIDU_QIANFAN_API_KEY']
secrets = [os.environ[n] for n in secret_names if os.environ.get(n)]
out['credentials_present'] = {n: bool(os.getenv(n)) for n in secret_names}
cfg = load_application_config()
out['effective_enabled_sources'] = [k for k,v in cfg.researcher.tools.database_search.providers.items() if v.get('enabled') and not v.get('testing_only')]
out['configured_optional_tools'] = {'web_search': cfg.researcher.tools.web_search.enabled, 'browser': cfg.researcher.tools.browser.enabled}
original_send = httpx.Client.send
def observed_send(self, request, *args, **kwargs):
    start = time.monotonic()
    item = {'host':request.url.host, 'path':request.url.path, 'method':request.method}
    try:
        response = original_send(self, request, *args, **kwargs)
        item.update(status=response.status_code, elapsed_seconds=round(time.monotonic()-start,3), content_type=response.headers.get('content-type'))
        if request.url.host == 'api.springernature.com' and response.status_code >= 400:
            try:
                payload = response.json()
                item['response_message'] = payload.get('message')
                item['response_error'] = payload.get('error')
            except Exception:
                item['response_kind'] = 'non_json'
        return response
    except Exception as exc:
        item.update(exception_type=type(exc).__name__,elapsed_seconds=round(time.monotonic()-start,3))
        raise
    finally:
        out['http'].append(item)
httpx.Client.send = observed_send

def probe(label, function):
    row={'probe':label}; start=time.monotonic()
    try: row.update(function()); row['status']='completed'
    except Exception as exc:
        row.update(status='failed', exception_type=type(exc).__name__, error=str(exc))
    row['elapsed_seconds']=round(time.monotonic()-start,3)
    out['probes'].append(row)

def summarize_hits(source, query):
    hits=list(source.search_tool.search(query,limit=1))
    return {'query':query, 'hits':len(hits), 'items':[{'document_id':h.document_id,'abstract_chars':len(h.abstract or '')} for h in hits]}

def summarize_text(source, doc_id):
    full=source.full_text_tool.fetch(doc_id)
    return {'document_id':doc_id,'has_full_text':full is not None,'text_chars':len(full.text) if full else 0,'content_extent':full.content_extent if full else None}
try:
    registry=build_source_registry()
    if '--springer-only' not in sys.argv:
        arxiv_cfg=dict(cfg.researcher.tools.database_search.providers['arxiv'])
        arxiv_cfg.update(timeout_seconds=12,max_retries=0,retry_budget_seconds=15)
        arxiv=registry.build('arxiv',arxiv_cfg)
        probe('arxiv_search',lambda:summarize_hits(arxiv,'all:"graph neural network"'))
        probe('arxiv_known_id',lambda:{'known_id':'1706.03762','resolved':arxiv.metadata_tool.resolve('1706.03762') is not None})
    springer_cfg=dict(cfg.researcher.tools.database_search.providers['springer'])
    springer_cfg.update(enabled=True,timeout_seconds=12,max_retries=0)
    springer=registry.build('springer',springer_cfg)
    probe('springer_search',lambda:summarize_hits(springer,'"graph neural network"'))
    old=json.loads((ROOT/'docs/experiments/20260915_184612/supplementary/compare/result.json').read_text())
    query=old['springer_404_diagnostic']['query']
    probe('springer_historical_404_query',lambda:summarize_hits(springer,query))
    probe('springer_known_oa_fulltext',lambda:summarize_text(springer,'doi:10.1038/s41586-021-03819-2'))
finally:
    reset_shared_arxiv_scheduler()
    httpx.Client.send=original_send
    out['finished_at']=datetime.now(timezone.utc).isoformat()
    serialized=json.dumps(out,ensure_ascii=False,indent=2)
    for value in secrets:serialized=serialized.replace(value,'<redacted>')
    (base/('provider_probe_after.json' if '--springer-only' in sys.argv else 'provider_probe.json')).write_text(serialized)
    print(serialized)
