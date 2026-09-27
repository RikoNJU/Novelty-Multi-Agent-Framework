"""Validate IDs against actual received Atom IDs; no network or production changes."""
import hashlib,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'backend/src')]
from novelty_agent_framework.tools.database_search.providers.arxiv import parse_entry,strip_version
NS='{http://www.w3.org/2005/Atom}'
files=[OUT/'canonical_example.body',OUT/'minimal_query.body',OUT/'url_equivalence/minimal_known_id.body']
rows=[]
for file in files:
 tree=ET.fromstring(file.read_bytes())
 for entry in tree.findall(NS+'entry'):
  original=entry.findtext(NS+'id');path=urlsplit(original).path;assert path.startswith('/abs/')
  expected_external=path[len('/abs/'):];expected_document=strip_version(expected_external);hit=parse_entry(entry)
  rows.append({'response_file':file.relative_to(OUT).as_posix(),'original_atom_id':original,'expected_external_id':expected_external,'actual_external_id':hit.external_id,'expected_document_id':expected_document,'actual_document_id':hit.document_id,'expected_url':'https://arxiv.org/abs/'+expected_document,'actual_url':hit.url,'actual_fulltext_url':hit.full_text_url,'mismatch':hit.external_id!=expected_external or hit.document_id!=expected_document})
payload={'new_network_calls':0,'new_model_calls':0,'input_sha256':{p.relative_to(OUT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'rows':rows,'mismatched_rows':sum(r['mismatch'] for r in rows),'distinct_mismatched_atom_ids':len({r['original_atom_id'] for r in rows if r['mismatch']}),'note':'Read-only reproduction of an existing parser defect. Not the cause of HTTP 406; occurs after successful Atom receipt.'}
(OUT/'identifier_audit.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'rows':len(rows),'mismatched_rows':payload['mismatched_rows'],'distinct_mismatched_atom_ids':payload['distinct_mismatched_atom_ids']}))
