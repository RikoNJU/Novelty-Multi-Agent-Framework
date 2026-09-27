"""Known-secret audit: never print or persist a credential value."""
import hashlib,json,os,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'backend/src')]
import backend.env  # Loads the same development credential environment as clients.
OUT=Path(__file__).parent
keys={key:value for key,value in os.environ.items() if re.search(r'(?:API_?KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)',key,re.I)
      and len(value)>=8 and value.strip() and value.lower() not in {'placeholder','not-configured','test-token','test-api-key'}}
roots=[OUT,ROOT/'docs/experiments/20260927_harness_config_audit',ROOT/'docs/experiments/20260927_harness_config_continued',
       ROOT/'docs/experiments/runtime/MF2033k6lC_2026-09-27',ROOT/'outputs/harness-config-audit-continued']
files={p for root in roots if root.exists() for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
findings=[];total=0
for p in sorted(files):
    data=p.read_bytes();total+=len(data)
    for key,value in keys.items():
        if value.encode() in data:
            findings.append({'file':p.relative_to(ROOT).as_posix(),'environment_key_name':key})
result={'known_secret_values_checked':len(set(keys.values())),'environment_names_checked':sorted(keys),
    'files_scanned':len(files),'bytes_scanned':total,'roots':[str(p.relative_to(ROOT)) for p in roots],
    'matches':findings,'secret_values_recorded':False,'limitation':'Exact known environment secret values only; not a proof that arbitrary unknown secrets are absent.'}
(OUT/'secret_scan.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'known_secret_values_checked':result['known_secret_values_checked'],'files_scanned':len(files),'match_count':len(findings)}))
if findings: raise SystemExit(1)
