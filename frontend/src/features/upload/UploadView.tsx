import { useRef, useState } from 'react';
import { ArrowRight, FileText, Upload, X, Eye } from 'lucide-react';
import { accepts, limits, size, validateFiles } from './validation';
import { FilePreview } from '../report/FilePreview';
interface Props { paper: File | null; references: File[]; onFiles: (paper: File | null, references: File[]) => void; onSubmit: () => void; busy: boolean; submitBlocked?: boolean; error: string | null }
export function UploadView({ paper, references, onFiles, onSubmit, busy, submitBlocked = false, error }: Props) {
  const [validation, setValidation] = useState<{kind: 'paper' | 'references'; text: string} | null>(null);
  const [preview, setPreview] = useState<File | null>(null);
  const paperButton = useRef<HTMLButtonElement>(null);
  const select = (incoming: File[], kind: 'paper' | 'references') => {
    if (busy) return;
    const files = kind === 'paper' ? incoming : [...references, ...incoming];
    const issue = validateFiles(files, kind, kind === 'paper' ? references : paper ? [paper] : []);
    if (issue) { setValidation({kind, text: issue}); return; }
    setValidation(null); onFiles(kind === 'paper' ? files[0] : paper, kind === 'references' ? files : references);
  };
  const submit = () => {
    if (!paper) { setValidation({ kind: 'paper', text: '请先上传论文 PDF' }); paperButton.current?.focus(); return; }
    setValidation(null); onSubmit();
  };
  if (preview) return <FilePreview file={preview} onClose={() => setPreview(null)}/>;
  return <section className="panel upload-view" aria-labelledby="upload-title" aria-busy={busy}>
    <p className="eyebrow">从一篇论文开始</p><h1 id="upload-title">让创新，有据可循。</h1>
    <p className="intro">添加论文原文，开启本次查新。</p>
    <div className="upload-grid">
      <div className="upload-column">
        <div className="field-label"><h2>上传论文原文</h2><span>必填 · 1 篇</span></div>
        <Dropzone kind="paper" disabled={busy} onSelect={files => select(files, 'paper')} buttonRef={paperButton} invalid={validation?.kind === 'paper'} replacing={!!paper}/>
        <ul className="file-list">{(paper ? [paper] : []).map((file, index) => <li key={`${file.name}-${index}`}>
          <FileText size={20}/><div className="file-meta"><span className="file-name" title={file.name}>{file.name}</span><small>{file.name.split('.').pop()?.toUpperCase()} · {size(file.size)} · {busy ? '上传中' : '待上传'}</small></div>
          <button className="icon-button" disabled={busy} onClick={() => setPreview(file)} aria-label={`预览 ${file.name}`}><Eye size={18}/></button>
          <button className="icon-button" disabled={busy} aria-label={`删除 ${file.name}`} onClick={() => { setValidation(null); onFiles(null, references); }}><X size={18}/></button>
        </li>)}</ul>
        <p className="field-error" id="paper-error" role="alert">{validation?.kind === 'paper' ? validation.text : ''}</p>
      </div>
    </div>
    <p className="limits">论文文件 ≤ {size(limits.fileBytes)} · 仅支持 PDF</p>
    {import.meta.env.VITE_FILE_API_ENABLED === 'false' && <p className="notice">当前服务尚未开放文件查新。可选择并预览文件，暂不能提交。</p>}
    {error && <p className="error" role="alert">{error}</p>}
    <div className="upload-footer"><p>文件仅在点击“开始查新”后发送至服务端。</p><button className="primary" onClick={submit} disabled={busy || submitBlocked}>{busy ? '正在提交…' : submitBlocked ? '提交状态待确认' : '开始查新'}<ArrowRight size={18}/></button></div>
  </section>;
}
function Dropzone({ kind, disabled, onSelect, buttonRef, invalid, replacing }: {kind: 'paper' | 'references'; disabled: boolean; onSelect: (files: File[]) => void; buttonRef?: React.Ref<HTMLButtonElement>; invalid: boolean; replacing: boolean}) {
  const input = useRef<HTMLInputElement>(null); const [drag, setDrag] = useState(false);
  return <><input ref={input} type="file" hidden accept={accepts[kind]} multiple={kind === 'references'} disabled={disabled} aria-label={kind === 'paper' ? '论文文件' : '参考文献文件'} onChange={e => { if (e.target.files?.length) onSelect([...e.target.files]); e.target.value = ''; }}/>
    <button type="button" ref={buttonRef} className={`dropzone ${drag ? 'dragging' : ''}`} disabled={disabled} aria-invalid={invalid} aria-describedby={`${kind}-error`} aria-label={kind === 'paper' ? '选择论文 PDF' : '选择参考文献'}
      onClick={() => input.current?.click()} onDragOver={e => { e.preventDefault(); if (!disabled) setDrag(true); }} onDragLeave={() => setDrag(false)} onDrop={e => { e.preventDefault(); setDrag(false); if (!disabled && e.dataTransfer.files.length) onSelect([...e.dataTransfer.files]); }}>
      <span className="upload-symbol"><Upload size={25} strokeWidth={1.5}/></span><strong>{kind === 'references' ? '参考文献功能尚未开放' : replacing ? '选择新文件，替换当前论文' : '点击选择，或拖拽文件至此'}</strong><span>{kind === 'paper' ? 'PDF 格式' : '后续版本支持'}</span>
    </button></>;
}
