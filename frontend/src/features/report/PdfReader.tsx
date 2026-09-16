import { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import workerUrl from 'pdfjs-dist/build/pdf.worker.min.mjs?url';
pdfjs.GlobalWorkerOptions.workerSrc = workerUrl;
const options = { isEvalSupported: false };
export default function PdfReader({ file }: { file: File }) {
  const [pages, setPages] = useState(0); const [page, setPage] = useState(1); const [scale, setScale] = useState(1);
  return <div className="pdf-reader">
    <div className="pdf-controls" aria-label="PDF 阅读控制">
      <button disabled={page <= 1} onClick={() => setPage(n => n - 1)}>上一页</button><span role="status">{page} / {pages || '—'}</span><button disabled={page >= pages} onClick={() => setPage(n => n + 1)}>下一页</button>
      <button aria-label="缩小" disabled={scale <= .5} onClick={() => setScale(n => n - .25)}>−</button><span>{Math.round(scale * 100)}%</span><button aria-label="放大" disabled={scale >= 2} onClick={() => setScale(n => n + .25)}>+</button>
    </div>
    <div className="pdf-canvas"><Document file={file} options={options} onLoadSuccess={({numPages}) => setPages(numPages)} loading={<p role="status">正在加载 PDF…</p>} error={<p role="alert">PDF 无法预览，文件可能损坏或已加密。请检查文件。</p>}><Page pageNumber={page} width={680 * scale} renderAnnotationLayer={false} renderTextLayer={false} loading={<p>正在绘制页面…</p>}/></Document></div>
  </div>;
}
