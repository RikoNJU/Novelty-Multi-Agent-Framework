"""Durable snapshots and a single local background worker (one server process)."""
import copy
import json
import logging
import re
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from .runner import execute

ARTIFACTS = ('novelty_points', 'search_results', 'review')


def now():
    return datetime.now(timezone.utc).isoformat()


class RunStore:
    def __init__(self, root: Path, executor=execute):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.executor = executor
        self.lock = threading.RLock()
        self.pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='novelty-web')
        self.records = {}
        for path in self.root.glob('run-*/run.json'):
            value = json.loads(path.read_text('utf-8'))
            self.records[value['run_id']] = value
            if value['status'] in ('pending', 'running'):
                self.update(value['run_id'], status='failed', error={'code': 'interrupted', 'message': '服务已重启，本次运行中断，请重新提交。'})

    def directory(self, run_id):
        if not re.fullmatch(r'run-[0-9a-f]{32}', run_id):
            raise KeyError(run_id)
        return self.root / run_id

    def get(self, run_id):
        with self.lock:
            self.directory(run_id)
            return copy.deepcopy(self.records[run_id])

    def update(self, run_id, done=None, **values):
        with self.lock:
            item = self.records[run_id]
            item.update(values, updated_at=now())
            if done and done not in item['completed']:
                item['completed'].append(done)
            path = self.directory(run_id) / 'run.json'
            temporary = path.with_suffix('.tmp')
            temporary.write_text(json.dumps(item, ensure_ascii=False), 'utf-8')
            temporary.replace(path)

    def create(self, content):
        run_id = 'run-' + uuid.uuid4().hex
        directory = self.directory(run_id)
        directory.mkdir()
        (directory / 'input.pdf').write_bytes(content)
        with self.lock:
            self.records[run_id] = dict(run_id=run_id, status='pending', stage='input', completed=['input'], started_at=None, updated_at=now(), error=None)
            self.update(run_id)
        self.pool.submit(self._execute, run_id)
        return self.get(run_id)

    def publish(self, run_id, kind, source):
        # Called only after the producer node has returned. API reads immutable copies.
        payload = json.loads(source.read_text('utf-8'))
        if kind == 'search_results':
            payload = {key: len(payload.get(key, [])) for key in ('raw_evidence_cards', 'accepted_evidence_cards', 'rejected_evidence')}
        elif kind == 'novelty_points':
            payload = {'novelty_points': payload['novelty_points']}
        elif kind == 'review':
            payload = {'reviews': payload['reviews'], 'phase': payload.get('phase', 'complete')}
        path = self.directory(run_id) / f'{kind}.json'
        with self.lock:
            temporary = path.with_suffix('.tmp')
            temporary.write_text(json.dumps(payload, ensure_ascii=False), 'utf-8')
            temporary.replace(path)

    def _execute(self, run_id):
        directory = self.directory(run_id)
        try:
            self.update(run_id, status='running', started_at=now())
            report = self.executor(directory, lambda **kw: self.update(run_id, **kw), lambda kind, path: self.publish(run_id, kind, path))
            report = report.resolve()
            if not report.is_relative_to(directory) or not report.read_text('utf-8').strip():
                raise ValueError('报告路径或内容无效')
            # Preserve the exact rendered bytes for both preview and download.
            (directory / 'report.md').write_bytes(report.read_bytes())
            self.update(run_id, status='completed', stage='render', done='render')
        except Exception as exc:
            logging.getLogger(__name__).exception('Web run failed: %s', run_id)
            stage = self.get(run_id)['stage']
            labels = {'input': '输入与配置初始化', 'parse': '论文解析', 'novelty_points': '查新点生成', 'research': '文献检索', 'review': '结果审查', 'render': '报告生成'}
            message = f"{labels.get(stage, '工作流')}失败（{type(exc).__name__}），请联系部署者按运行编号检查服务日志。"
            self.update(run_id, status='failed', error={'code': 'execution_failed', 'message': message})

    def close(self):
        self.pool.shutdown(wait=True)
