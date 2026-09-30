"""Build in a temporary source tree; probe wheel imports outside repository."""
import json,os,shutil,subprocess,sys,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='novelty-audit-wheel-') as d:
 base=Path(d);src=base/'source';src.mkdir()
 for filename in ['pyproject.toml','README.md']:shutil.copy2(ROOT/filename,src/filename)
 shutil.copytree(ROOT/'backend/src',src/'backend/src',ignore=shutil.ignore_patterns('__pycache__','*.egg-info'))
 built=subprocess.run([sys.executable,'-m','pip','wheel','--no-deps','--no-build-isolation','--wheel-dir',str(base/'wheels'),str(src)],cwd=base,text=True,capture_output=True)
 (OUT/'wheel-build.log').write_text(built.stdout+built.stderr)
 result={'build_returncode':built.returncode}
 if built.returncode==0:
  wheel=next((base/'wheels').glob('*.whl'));target=base/'installed';target.mkdir()
  with zipfile.ZipFile(wheel) as z:
   names=z.namelist();z.extractall(target)
   result.update(wheel=wheel.name,contains_backend_env=any(n.startswith('backend/env/') for n in names),contains_scripts=any(n.startswith('scripts/') for n in names),json_configs=[n for n in names if '/config/' in n and n.endswith('.json')],metadata=z.read(next(n for n in names if n.endswith('.dist-info/METADATA'))).decode().split('\n\n')[0])
  checks=[]
  for module in ['novelty_agent_framework','novelty_agent_framework.cli','novelty_agent_framework.config']:
   probe=subprocess.run([sys.executable,'-I','-c',f'import sys;sys.path.insert(0,{str(target)!r});import importlib;importlib.import_module({module!r})'],cwd=base,text=True,capture_output=True)
   checks.append({'module':module,'returncode':probe.returncode,'stdout':probe.stdout,'stderr':probe.stderr})
  result['isolated_imports']=checks
 (OUT/'packaging-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result,ensure_ascii=False,indent=2))
