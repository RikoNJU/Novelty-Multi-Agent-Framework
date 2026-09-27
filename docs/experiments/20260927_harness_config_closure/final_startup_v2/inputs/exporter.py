"""Archive current reviewed code; deliberately separate from live experiment starts."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'backend/src')]
from novelty_agent_framework.config import load_application_config
from novelty_agent_framework.config.experiment import prepare_startup,verify_startup_snapshot
out=Path(__file__).parent
config=load_application_config(profile_path=ROOT/'config/profiles/local-harness-closure.json',environ={})
manifest=prepare_startup(config,output_root=Path('/tmp/novelty-closure-preview'),entrypoint='paper_input',
    snapshot_dir=out/'final_startup_v2',input_path=ROOT/'outputs/harness-config-audit-continued/0001/paper-input.json',
    input_contents={'profile.json':(ROOT/'config/profiles/local-harness-closure.json').read_bytes(),
                    'exporter.py':Path(__file__).read_bytes()},include_processing=False)
assert verify_startup_snapshot(out/'final_startup_v2')
for name in ('final_configuration_manifest.json','implementation.patch','source_inventory.json'):
    old=out/name
    if old.exists(): old.rename(out/(old.stem+'-before-tool-boundary'+old.suffix))
(out/'final_configuration_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
paths=['backend','scripts','tests','config']
patch=subprocess.check_output(['git','diff','--binary','--',*paths],cwd=ROOT)
untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard','--',*paths],cwd=ROOT,text=True).splitlines()
for name in untracked:
    result=subprocess.run(['git','diff','--no-index','--binary','--','/dev/null',name],cwd=ROOT,capture_output=True)
    if result.returncode not in (0,1): raise RuntimeError('diff failed for '+name)
    patch+=result.stdout
patch_path=out/'implementation.patch';patch_path.write_bytes(patch)
result=subprocess.run(['git','apply','--reverse','--check',str(patch_path)],cwd=ROOT,capture_output=True,text=True)
if result.returncode: raise RuntimeError(result.stderr)
changed=subprocess.check_output(['git','diff','--name-only','--',*paths],cwd=ROOT,text=True).splitlines()
files=sorted(set(changed+untracked))
base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
inventory={'base_commit':base,'patch_sha256':hashlib.sha256(patch).hexdigest(),'patch_bytes':len(patch),
    'reverse_apply_check_passed':True,'files':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in files if (ROOT/name).is_file()},
    'untracked_included':untracked,'excluded_user_file':'docs/Novelty_本地LLM使用手册.md',
    'final_startup_verified':True,'final_startup_path':'final_startup_v2',
    'snapshot_is_new_offline_archive_not_retroactive_live_start':True}
(out/'source_inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'source_files_changed':len(files),'patch_bytes':len(patch),'reverse_check':True,'snapshot_verified':True}))
