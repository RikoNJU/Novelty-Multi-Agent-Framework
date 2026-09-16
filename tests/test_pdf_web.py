import json
import threading
import time
from pathlib import Path

import fitz
import pytest
from fastapi.testclient import TestClient

from novelty_agent_framework.main import create_app
from novelty_agent_framework.web.store import RunStore
from novelty_agent_framework.web.routes import MAX_PDF_BYTES


@pytest.fixture
def pdf():
    with fitz.open() as doc:
        page = doc.new_page()
        page.insert_text((72, 72), 'Novelty test paper')
        return doc.tobytes()


def successful_runner(directory, update, publish):
    update(stage='parse', done='parse')
    path = directory / 'outputs' / 'paper'
    path.mkdir(parents=True)
    source = path / 'novelty-points.json'
    source.write_text(json.dumps({'novelty_points': [{'id': 'N1', 'description': 'test'}]}))
    publish('novelty_points', source)
    report = path / 'actual.md'
    report.write_bytes('# 查新报告\r\n\r\n|证据|结论|\r\n|---|---|\r\n|不足|无法确认|\r\n'.encode())
    return report


def wait_terminal(client, run_id):
    for _ in range(200):
        state = client.get('/api/runs/' + run_id).json()
        if state['status'] in ('completed', 'failed'):
            return state
        time.sleep(.01)
    pytest.fail('worker did not finish')


def test_report_isolation_and_restore(tmp_path, pdf):
    app = create_app(runs_root=tmp_path, runner=successful_runner)
    with TestClient(app) as client:
        runs = [client.post('/api/runs', files={'file': ('../../same.pdf', pdf)}).json()['run_id'] for _ in range(2)]
        assert runs[0] != runs[1]
        for run_id in runs:
            terminal = wait_terminal(client, run_id)
            assert terminal['status'] == 'completed'
            assert terminal['stage'] == 'render'
            preview = client.get(f'/api/runs/{run_id}/report')
            download = client.get(f'/api/runs/{run_id}/report.md')
            assert preview.json()['content'].encode() == download.content
            assert download.content == (tmp_path / run_id / 'outputs/paper/actual.md').read_bytes()
            assert download.headers['cache-control'] == 'no-store'
            assert 'attachment' in download.headers['content-disposition']
            assert client.get(f'/api/runs/{run_id}/artifacts/novelty_points').json()['novelty_points']
            assert client.get(f'/api/runs/{run_id}/artifacts/review').status_code == 409
            assert (tmp_path / run_id / 'input.pdf').read_bytes() == pdf
        (tmp_path / runs[0] / 'report.md').unlink()
        assert client.get(f'/api/runs/{runs[0]}/report').json()['detail']['code'] == 'report_read_failed'
    with TestClient(create_app(runs_root=tmp_path, runner=successful_runner)) as client:
        assert client.get(f'/api/runs/{runs[1]}').json()['status'] == 'completed'
        assert client.get('/api/runs/not-a-run').status_code == 404


def test_input_contract(tmp_path, pdf):
    with TestClient(create_app(runs_root=tmp_path, runner=successful_runner)) as client:
        assert client.post('/api/runs').status_code == 415
        assert client.post('/api/runs', files=[('file', ('a.pdf', pdf)), ('file', ('b.pdf', pdf))]).status_code == 422
        assert client.post('/api/runs', files={'other': ('a.pdf', pdf)}).status_code == 422
        assert client.post('/api/runs', files={'file': ('a.zip', pdf)}).status_code == 415
        for value in (b'', b'%PDF-invalid', b'not pdf'):
            assert client.post('/api/runs', files={'file': ('a.pdf', value)}).status_code == 422
        assert client.post('/api/runs', files={'file': ('a.pdf', b'x'*(MAX_PDF_BYTES+1))}).status_code == 413
        assert client.post('/api/runs', content=b'x'*(MAX_PDF_BYTES+1024*1024+1), headers={'content-type':'multipart/form-data'}).status_code == 413
        with fitz.open(stream=pdf, filetype='pdf') as doc:
            encrypted = doc.tobytes(encryption=fitz.PDF_ENCRYPT_AES_256, owner_pw='owner', user_pw='secret')
        assert client.post('/api/runs', files={'file': ('a.pdf', encrypted)}).status_code == 422
        assert not list(tmp_path.glob('run-*'))


def test_pending_failure_and_path_constraint(tmp_path, pdf):
    release = threading.Event()
    def failing(directory, update, publish):
        release.wait(3)
        raise RuntimeError('secret credential must not be exposed')
    with TestClient(create_app(runs_root=tmp_path, runner=failing)) as client:
        run_id = client.post('/api/runs', files={'file': ('paper.pdf', pdf)}).json()['run_id']
        assert client.get(f'/api/runs/{run_id}/report').json()['detail']['code'] == 'report_not_ready'
        release.set()
        state = wait_terminal(client, run_id)
        assert state['status'] == 'failed'
        assert 'secret' not in json.dumps(state)
        assert client.get(f'/api/runs/{run_id}/report').json()['detail']['code'] == 'run_failed'
        assert client.get(f'/api/runs/{run_id}/artifacts/input.pdf').status_code == 404


def test_restart_marks_orphan_failed(tmp_path):
    run_id = 'run-' + 'a'*32
    directory = tmp_path / run_id
    directory.mkdir()
    (directory/'run.json').write_text(json.dumps(dict(run_id=run_id, status='running', completed=[])))
    store = RunStore(tmp_path)
    try:
        assert store.get(run_id)['error']['code'] == 'interrupted'
    finally:
        store.close()


def test_production_static_mount(tmp_path):
    dist = tmp_path / 'dist'
    dist.mkdir()
    (dist/'index.html').write_text('<h1>Novelty</h1>')
    with TestClient(create_app(runs_root=tmp_path/'runs', static_root=dist)) as client:
        assert 'Novelty' in client.get('/').text
        assert client.get('/api/health').json()['max_pdf_bytes'] == MAX_PDF_BYTES
        assert client.get('/api/runs/unknown').status_code == 404


def test_pdf_adapter_runs_existing_graph_offline(tmp_path, monkeypatch):
    """Exercise real text parsing, graph observation and Renderer with demo agents.

    External model and reference services are explicitly replaced in this test.
    This is not a live research acceptance test.
    """
    from types import SimpleNamespace
    from novelty_agent_framework.web import runner
    from novelty_agent_framework.processing import DefaultPaperProcessor
    from novelty_agent_framework.workflows import NoveltyWorkflow
    monkeypatch.setattr(runner, 'load_application_config', lambda: SimpleNamespace(project=SimpleNamespace(processing={})))
    monkeypatch.setattr(runner, 'build_model_registry', lambda config: None)
    monkeypatch.setattr(runner, 'DefaultPaperProcessor', lambda **kw: DefaultPaperProcessor(parser='text', min_chars_per_page=1))
    monkeypatch.setattr(runner, 'prepare_paper_input_references', lambda *a, **kw: None)
    def build(config, output_root):
        workflow = NoveltyWorkflow.default()
        return NoveltyWorkflow(workflow.services, output_root=output_root)
    monkeypatch.setattr(runner, 'build_standard_full_workflow', build)
    with TestClient(create_app(runs_root=tmp_path)) as client:
        sample = Path('examples/MF2033k6lC.pdf').read_bytes()
        response = client.post('/api/runs', files={'file': ('sample.pdf', sample)})
        run_id = response.json()['run_id']
        state = wait_terminal(client, run_id)
        assert state['status'] == 'completed', state
        assert set(state['completed']) == {'input','parse','novelty_points','research','review','render'}
        assert all(item['available'] for item in client.get(f'/api/runs/{run_id}/artifacts').json()['artifacts'])
        assert client.get(f'/api/runs/{run_id}/report').json()['content']
