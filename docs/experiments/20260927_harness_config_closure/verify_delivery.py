"""Offline final delivery checks; never reruns models or providers."""
import hashlib,json,re,subprocess,sys,xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
sys.path[:0]=[str(ROOT),str(ROOT/'backend/src')]
from novelty_agent_framework.config.experiment import verify_startup_snapshot
inventory=json.loads((OUT/'source_inventory.json').read_text())
for name,sha in inventory['files'].items(): assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name
manifest=json.loads((OUT/'final_configuration_manifest.json').read_text())
assert verify_startup_snapshot(OUT/'final_startup_v2')
for name,sha in manifest['code']['source_snapshot']['source_files'].items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name
assert verify_startup_snapshot(OUT/'reader_local_repeated/startup')
for command in (['git','apply','--reverse','--check',str(OUT/'implementation.patch')],['git','diff','--check']):
    result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    assert result.returncode==0,result.stderr+result.stdout
checked=[];broken=[]
for p in OUT.glob('*.md'):
    for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',p.read_text()):
        if re.match(r'^[A-Za-z]+://',target) or target.startswith('#'):continue
        target=unquote(target.split('#')[0]).strip('<>')
        if not target:continue
        resolved=(p.parent/target).resolve();checked.append((p.name,target))
        if not resolved.exists() and resolved!=OUT/'validation_summary.json':broken.append({'file':p.name,'target':target})
assert not broken,broken
suites=ET.parse(OUT/'full-tests.xml').getroot().findall('testsuite')
tests={key:sum(int(s.attrib.get(key,0)) for s in suites) for key in ('tests','failures','errors','skipped')}
match=re.search(r'(\d+) passed, (\d+) deselected, (\d+) warning in ([\d.]+)s',(OUT/'full-tests.log').read_text())
assert match and tests['failures']==tests['errors']==0
payload={'full_suite':{**tests,'passed':int(match[1]),'deselected':int(match[2]),'warnings':int(match[3]),'seconds':float(match[4]),
    'command':"PYTHONPATH=backend/src:.:tests /home/lya3106643285/miniconda3/envs/Novelty-web/bin/python -m pytest -o addopts='' -q -m 'not live'"},
    'source_inventory_matches_worktree':True,'changed_files':len(inventory['files']),
    'patch_reverse_apply_check':True,'git_diff_check':True,'final_source_snapshot_matches_worktree':True,
    'final_snapshot_verified':True,'reader_experiment_snapshot_verified':True,'markdown_local_links_checked':len(checked),
    'broken_links':broken,'scientific_performance_acceptance':'not_passed','exploratory_review_and_selected_engineering_closure':'partial_delivery_not_task_completion',
    'overall_task_status':'incomplete','task_acceptance':'not_accepted'}
(OUT/'validation_summary.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(payload,ensure_ascii=False))
