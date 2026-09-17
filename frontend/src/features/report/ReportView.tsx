import { useEffect, useState } from 'react';
import { ArrowLeft } from 'lucide-react';
import { normalizeError, reportFile } from '../../api/client';
import type { RunSnapshot } from '../../api/contracts';
import { FilePreview } from './FilePreview';
export function ReportView({ run, onClose }: { run: RunSnapshot; onClose: () => void }) {
  const [file, setFile] = useState<File | null>(null); const [error, setError] = useState(''); const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    if (!run.report) return;
    const controller = new AbortController(); setError(''); setFile(null);
    reportFile(run.report.preview_url, controller.signal).then(value => { if (!controller.signal.aborted) setFile(value); }).catch(cause => { if (!controller.signal.aborted) setError(normalizeError(cause).message); });
    return () => controller.abort();
  }, [run, attempt]);
  if (file) return <FilePreview file={file} onClose={onClose}/>;
  const structured = run.result?.report;
  return <section className="reader panel" aria-label="查新报告">
    <div className="reader-toolbar"><button onClick={onClose}><ArrowLeft size={18}/>返回</button><h1>查新报告</h1></div>
    {run.report ? error ? <div className="report-error"><p role="alert">{error}</p><button className="primary" onClick={() => setAttempt(n => n + 1)}>重新加载报告</button></div> : <p role="status">正在加载报告…</p> : structured ? <article className="structured-report">
      <p className="notice">当前展示结构化报告。服务尚未提供报告文件，暂不支持下载。</p>
      <h2>{structured.paper_id} · 查新报告</h2>
      {structured.conclusions.map((c, i) => <section key={i}><h3>{c.novelty_point_id} · {c.incomplete_reason === 'budget_exhausted' ? '核验超时或预算耗尽，尚未完成' : c.incomplete_reason && c.incomplete_reason !== 'semantic_evidence' ? '核验未完成，无法裁定' : c.review_status === 'insufficient_evidence' ? '现有证据不足，无法裁定' : ({ novel: '新颖', partially_novel: '部分新颖', not_novel: '不新颖' }[c.verdict ?? ''] ?? '未裁定')}</h3><p>{c.summary}</p>{c.verdict_reason && <p>裁定理由：{c.verdict_reason}</p>}</section>)}
      {([['研究局限', structured.limitations], ['缺失参考文献', structured.missing_references], ['缺失基线', structured.missing_baselines], ['引用问题', structured.citation_issues]] as [string, string[]][]).map(([title, values]) => <section key={title}><h3>{title}</h3>{values.length ? <ul>{values.map((v, i) => <li key={i}>{v}</li>)}</ul> : <p>无。</p>}</section>)}
    </article> : <p role="alert">报告内容尚不可用，请返回后稍后重试。</p>}
  </section>;
}
