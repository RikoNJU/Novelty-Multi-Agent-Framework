import { lazy, Suspense, useEffect, useState } from 'react';
import { ArrowLeft, Download } from 'lucide-react';
import { saveFile } from '../../api/client';
import { Markdown } from './Markdown';
const PdfReader = lazy(() => import('./PdfReader'));
export function FilePreview({ file, onClose }: { file: File; onClose: () => void }) {
  const [text, setText] = useState(''); const [error, setError] = useState(false);
  const pdf = file.type === 'application/pdf' || /\.pdf$/i.test(file.name);
  const markdown = /\.(md|markdown)$/i.test(file.name) || file.type === 'text/markdown';
  const plain = file.type === 'text/plain' || /\.txt$/i.test(file.name);
  useEffect(() => { let active = true; if (!pdf && (markdown || plain)) file.text().then(value => { if (active) setText(value); }).catch(() => { if (active) setError(true); }); return () => { active = false; }; }, [file, pdf, markdown, plain]);
  return <section className="reader panel" aria-label="文件预览">
    <div className="reader-toolbar"><button onClick={onClose}><ArrowLeft size={18}/>返回</button><h1>{file.name}</h1><button onClick={() => saveFile(file)}><Download size={18}/>下载</button></div>
    {error ? <p role="alert">文件读取失败，请关闭预览后重试。</p> : pdf ? <Suspense fallback={<p role="status">正在加载阅读器…</p>}><PdfReader file={file}/></Suspense> : markdown ? <Markdown text={text}/> : plain ? <pre className="plain-text">{text}</pre> : <p>暂不支持此格式的预览，可下载查看。</p>}
  </section>;
}
