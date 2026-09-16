"""Bound multipart traffic before the multipart parser spools it to disk."""
from starlette.responses import JSONResponse
from .routes import MAX_PDF_BYTES


class UploadLimitMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http' or scope['path'] != '/api/runs' or scope['method'] != 'POST':
            return await self.app(scope, receive, send)
        chunks, size = [], 0
        while True:
            message = await receive()
            if message['type'] == 'http.disconnect':
                return
            size += len(message.get('body', b''))
            if size > MAX_PDF_BYTES + 1024 * 1024:
                response = JSONResponse({'detail': {'code': 'file_too_large', 'message': '上传请求超过大小限制'}}, status_code=413)
                return await response(scope, receive, send)
            chunks.append(message)
            if not message.get('more_body', False):
                break
        iterator = iter(chunks)
        async def replay():
            try:
                return next(iterator)
            except StopIteration:
                return {'type': 'http.disconnect'}
        await self.app(scope, replay, send)
