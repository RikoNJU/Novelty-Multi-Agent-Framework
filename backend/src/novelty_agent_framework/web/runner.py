"""Adapt the production workflow and publish only completed node outputs."""
import logging
from pathlib import Path

from ..config import build_model_registry, build_standard_full_workflow, load_application_config
from ..processing import DefaultPaperProcessor, prepare_paper_input_references
from ..processing.mineru_parser import MineruSettings
from ..persistence import paper_workspace

STAGES = {
    'extract_points': 'novelty_points', 'plan': 'research',
    'dispatch_planning_tasks': 'research', 'plan_research_task': 'research',
    'dispatch_research_tasks': 'research', 'run_research_task': 'research',
    'validate_evidence': 'research', 'review_evidence': 'review',
    'validate_synthesis_input': 'review', 'check_final_evidence_sufficiency': 'review',
    'plan_supplement': 'research', 'synthesize_report': 'render',
    'validate_report_integrity': 'render', 'persist_report': 'render', 'render_report': 'render',
}


def execute(directory: Path, update, publish) -> Path:
    config = load_application_config()
    processing = config.project.processing
    registry = build_model_registry(config)
    processor = DefaultPaperProcessor(
        parser='mineru',
        ocr_client=registry.client_for(processing['ocr_model']) if processing.get('ocr_model') else None,
        llm_client=registry.client_for(processing['llm_model']) if processing.get('llm_model') else None,
        dpi=int(processing.get('dpi', 200)),
        min_chars_per_page=int(processing.get('quality_min_chars_per_page', 200)),
        mineru_settings=MineruSettings(
            python_path=processing.get('mineru_python'),
            env_name=processing.get('mineru_env', 'mineru'),
            worker_path=processing.get('mineru_worker', 'scripts/mineru_worker.py'),
            backend=processing.get('mineru_backend', 'pipeline'),
            method=processing.get('mineru_method', 'auto'),
            lang=processing.get('mineru_lang', 'ch'),
            effort=processing.get('mineru_effort', 'medium'),
            timeout_seconds=int(processing.get('mineru_timeout_seconds', 1800)),
            work_root=str(directory / 'parser'),
            model_source=processing.get('mineru_model_source'),
        ),
    )
    update(stage='parse')
    import hashlib
    paper_id = 'paper-' + hashlib.sha256((directory / 'input.pdf').read_bytes()).hexdigest()[:24]
    paper = processor.to_paper_input(processor.process(directory / 'input.pdf', paper_id=paper_id))
    if not paper.full_text.strip():
        raise ValueError('PDF 未解析出可用文本')
    update(done='parse', stage='research')
    output = directory / 'outputs'
    prepare_paper_input_references(paper, stable_output_root=directory / 'references', run_output_root=output)
    workflow = build_standard_full_workflow(config, output_root=output)
    workspace = paper_workspace(paper, output_root=output)
    # Observe existing node entry/return without duplicating graph orchestration.
    def publish_optional(kind, path):
        try:
            publish(kind, path)
        except (OSError, ValueError, KeyError):
            logging.getLogger(__name__).exception('Could not publish stage artifact: %s', kind)

    original = workflow._record_stage

    def observe(name, function):
        recorded = original(name, function)
        async def wrapped(state):
            stage = STAGES.get(name, name)
            update(stage=stage)
            result = await recorded(state)
            if name == 'extract_points':
                publish_optional('novelty_points', workspace / 'novelty-points.json')
                update(done='novelty_points')
            elif name == 'review_evidence':
                publish_optional('search_results', workspace / 'evidence-cards.json')
                publish_optional('review', workspace / 'novelty-reviews.json')
                update(done='research')
                update(done='review')
            elif name == 'render_report':
                update(done='render')
            return result
        return wrapped

    workflow._record_stage = observe
    workflow.graph = workflow._build_graph()
    workflow.run(paper, run_identity={'entrypoint': 'web_pdf', 'web_run_id': directory.name})
    if not workflow.last_rendered_report_path:
        raise RuntimeError('工作流没有生成 Markdown 报告')
    return Path(workflow.last_rendered_report_path)
