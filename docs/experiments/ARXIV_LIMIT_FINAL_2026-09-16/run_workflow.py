"""Repeat existing single-task and PaperInput harnesses with Web arXiv, no MinerU."""
import argparse
import asyncio
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path.cwd()
sys.path[:0] = [str(ROOT), str(ROOT / 'backend/src'), str(ROOT / 'scripts')]
from backend.env.model_client import _load_dev_env
from novelty_agent_framework.config import build_standard_full_workflow, load_application_config, effective_safe_config
from novelty_agent_framework.core.runtime_artifacts import RuntimeArtifactManager, RuntimeDebugConfig
from novelty_agent_framework.core.run_identity import file_run_identity
from novelty_agent_framework.processing import prepare_paper_input_references
from novelty_agent_framework.schemas import PaperInput
from run_single_research_task import build_request
from run_full_pipeline_experiment import Recorder, _wrap_workflow, safe_error

BASE = Path(__file__).resolve().parent

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['single', 'parallel', 'full'])
    args = parser.parse_args()
    _load_dev_env()
    out = BASE / 'runtime' / args.mode
    out.mkdir(parents=True, exist_ok=False)
    paper_path = ROOT / 'outputs/MF2033k6lC/paper-input/others/paper.json'
    paper = PaperInput.model_validate_json(paper_path.read_text())
    config = load_application_config()
    config.project.workflow.max_concurrency = 4
    config.researcher.tools.database_search.max_concurrency = 4
    for key, provider in config.researcher.tools.database_search.providers.items():
        provider['enabled'] = key == 'arxiv'
    config.researcher.tools.database_search.providers['arxiv'].update(
        search_transport='web', web_min_interval_seconds=8, web_max_retries=1,
        web_max_consecutive_failures=2, web_circuit_cooldown_seconds=60,
        web_retry_budget_seconds=90)
    config.researcher.tools.web_search.enabled = False
    config.researcher.tools.browser.enabled = False
    config.project.runtime_debug.output_root = str(out)
    config.project.runtime_debug.archive_root = str(out / 'archive')
    write(out / 'effective-config.json', effective_safe_config(config))
    manifest = dict(mode=args.mode, paper_id=paper.paper_id,
        paper_sha256=hashlib.sha256(paper_path.read_bytes()).hexdigest(), mineru_invoked=False,
        max_concurrency=4, status='RUNNING')
    write(out / 'run.json', manifest)
    started = time.monotonic()
    rec = Recorder()
    rec.install_model_hook()
    workflow = None
    try:
        # The previously validated cache is read only; only this run's snapshot is written.
        cached = ROOT / 'docs/experiments/20260916_011551/input'
        bootstrap = prepare_paper_input_references(paper, stable_output_root=cached,
            run_output_root=out, force=False, max_concurrency=4)
        write(out / 'reference-bootstrap.json', bootstrap.model_dump(mode='json'))
        workflow = build_standard_full_workflow(config, output_root=out)
        _wrap_workflow(workflow, rec)
        if args.mode == 'full':
            result = workflow.run(paper, run_identity=file_run_identity('paper_input', paper_path, project_root=ROOT))
            write(out / 'result.json', result.model_dump(mode='json'))
            manifest['rendered_report_path'] = workflow.last_rendered_report_path
        else:
            plans_root = ROOT / 'outputs'
            task_ids = ['T-2'] if args.mode == 'single' else ['T-1', 'T-2']
            manager = RuntimeArtifactManager(paper.paper_id,
                config=RuntimeDebugConfig(output_root=out, archive_root=out / 'archive'),
                run_identity=file_run_identity(args.mode, paper_path, project_root=ROOT),
                runtime_config={'max_concurrency': 4, 'transport': 'web'},
                stage_names=['run_research_task'])
            requests = [build_request(plans_root, paper.paper_id, run_id=manager.run_id,
                point_id='NP-2', task_id=task_id) for task_id in task_ids]
            write(out / 'requests.json', [r.model_dump(mode='json') for r in requests])
            async def run_tasks():
                async def run_task(req):
                    stage = manager.start_stage('run_research_task', req)
                    try:
                        result = await workflow.services.task_researcher.ainvoke(req)
                    except BaseException as exc:
                        manager.fail_stage(stage, exc)
                        raise
                    manager.finish_stage(stage, result)
                    return result
                return await asyncio.gather(*(run_task(req) for req in requests))
            with manager:
                results = asyncio.run(run_tasks())
            manager.finish_run('SUCCESS')
            write(out / 'results.json', [r.model_dump(mode='json') for r in results])
        manifest['status'] = 'SUCCESS'
    except BaseException as exc:
        manifest.update(status='FAILED', error=safe_error(exc))
        raise
    finally:
        manifest['elapsed_seconds'] = time.monotonic() - started
        write(out / 'run.json', manifest)
        write(out / 'model-calls.json', rec.model_calls)
        write(out / 'tool-events.json', dict(rec.tool_events))
        write(out / 'stage-timings.json', dict(rec.stage_elapsed))
        print(json.dumps(manifest, ensure_ascii=False), flush=True)

if __name__ == '__main__':
    main()
