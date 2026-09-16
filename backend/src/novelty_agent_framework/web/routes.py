"""Public PDF API. No user supplied filesystem paths are accepted."""
import json

import pymupdf
from fastapi import APIRouter, HTTPException, Request
from starlette.datastructures import UploadFile
from starlette.concurrency import run_in_threadpool
from starlette.responses import Response

from .store import ARTIFACTS

router = APIRouter(prefix='/api')
MAX_PDF_BYTES = 25 * 1024 * 1024


def error(status, code, message):
    return HTTPException(status, detail={'code': code, 'message': message})


def snapshot(request, run_id):
    try:
        return request.app.state.pdf_runs.get(run_id)
    except KeyError:
        raise error(404, 'run_not_found', '运行不存在')


def validate_pdf(content):
    try:
        if not content.startswith(b'%PDF-'):
            raise ValueError()
        with pymupdf.open(stream=content, filetype='pdf') as document:
            if document.needs_pass or document.page_count == 0 or document.is_repaired:
                raise ValueError()
    except Exception:
        raise error(422, 'invalid_pdf', 'PDF 已损坏、加密、为空或格式不受支持')


@router.get('/health')
def health():
    return {'status': 'ok', 'max_pdf_bytes': MAX_PDF_BYTES}


@router.post('/runs', status_code=202)
async def create(request: Request):
    if not request.headers.get('content-type', '').startswith('multipart/form-data'):
        raise error(415, 'invalid_type', '请上传一个 PDF 文件')
    async with request.form(max_files=2, max_fields=1) as form:
        items = list(form.multi_items())
        if len(items) != 1 or items[0][0] != 'file' or not isinstance(items[0][1], UploadFile):
            raise error(422, 'single_pdf_required', '必须且只能上传一个 file 字段的 PDF')
        upload = items[0][1]
        if not (upload.filename or '').lower().endswith('.pdf'):
            raise error(415, 'invalid_type', '仅支持 PDF')
        content = await upload.read(MAX_PDF_BYTES + 1)
        if len(content) > MAX_PDF_BYTES:
            raise error(413, 'file_too_large', 'PDF 不得超过 25 MiB')
        await run_in_threadpool(validate_pdf, content)
        result = await run_in_threadpool(request.app.state.pdf_runs.create, content)
        return {'run_id': result['run_id'], 'status': result['status']}


@router.get('/runs/{run_id}')
def get_run(run_id: str, request: Request):
    return snapshot(request, run_id)


def report_bytes(request, run_id):
    state = snapshot(request, run_id)
    if state['status'] == 'failed':
        raise error(409, 'run_failed', '本次运行失败，没有可发布报告')
    if state['status'] != 'completed':
        raise error(409, 'report_not_ready', '报告尚未生成')
    try:
        content = (request.app.state.pdf_runs.directory(run_id) / 'report.md').read_bytes()
        if not content.strip():
            raise ValueError()
        content.decode('utf-8')
        return content
    except (OSError, ValueError):
        raise error(500, 'report_read_failed', '报告获取失败')


@router.get('/runs/{run_id}/report')
def report(run_id: str, request: Request):
    return {'content': report_bytes(request, run_id).decode('utf-8')}


@router.get('/runs/{run_id}/report.md')
def download(run_id: str, request: Request):
    return Response(report_bytes(request, run_id), media_type='text/markdown; charset=utf-8', headers={'Content-Disposition': f'attachment; filename="{run_id}.md"'})


@router.get('/runs/{run_id}/artifacts')
def artifacts(run_id: str, request: Request):
    snapshot(request, run_id)
    directory = request.app.state.pdf_runs.directory(run_id)
    return {'run_id': run_id, 'artifacts': [{'type': kind, 'available': (directory / f'{kind}.json').is_file(), 'revision': (directory / f'{kind}.json').stat().st_mtime_ns if (directory / f'{kind}.json').is_file() else None} for kind in ARTIFACTS]}


@router.get('/runs/{run_id}/artifacts/{kind}')
def artifact(run_id: str, kind: str, request: Request):
    snapshot(request, run_id)
    if kind not in ARTIFACTS:
        raise error(404, 'artifact_unknown', '未知阶段成果')
    try:
        return json.loads((request.app.state.pdf_runs.directory(run_id) / f'{kind}.json').read_text('utf-8'))
    except FileNotFoundError:
        raise error(409, 'artifact_not_ready', '阶段成果尚未发布')
    except (OSError, ValueError):
        raise error(500, 'artifact_read_failed', '阶段成果获取失败')
