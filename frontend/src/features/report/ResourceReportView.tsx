import { useEffect, useState } from 'react';
import { api, normalizeError, reportFile } from '../../api/client';
import type { ReportResource } from '../../api/contracts';
import { FilePreview } from './FilePreview';

export function ResourceReportView({ id, onClose }: { id: string; onClose: () => void }) {
  const [resource, setResource] = useState<ReportResource | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState('');
  useEffect(() => {
    const controller = new AbortController();
    setResource(null); setFile(null); setError('');
    api.getReportResource(id, controller.signal)
      .then(async item => {
        const content = await reportFile(`/api/novelty/report-artifacts/${encodeURIComponent(id)}/content`, controller.signal);
        if (!controller.signal.aborted) { setResource(item); setFile(content); }
      })
      .catch(cause => { if (!controller.signal.aborted) setError(normalizeError(cause).message); });
    return () => controller.abort();
  }, [id]);
  return <section aria-label="只读恢复报告资源">
    <div className="panel report-recovery-notice">
      <h1>历史运行的恢复报告</h1>
      <p>基于既有证据与真实模型响应重组。原完整运行失败；本次未重跑解析、检索或核验。自动结论保留原有局限，尚未获得独立正确性认证。</p>
      <p>资源编号：{id}</p>
      {resource && <>
        <p>来源运行：{resource.source_run_id}（{resource.source_run_status}）；恢复身份：{resource.live_recovery_id}；组装身份：{resource.assembly_id}</p>
        <p>资源完整性：{resource.artifact_integrity}；语义状态：继承原审查，未重新评定。</p>
        <ul>{resource.source_issues.map(point => <li key={point.point_id}>{point.point_id}：{point.review_status}{point.incomplete_reason ? `，未完成原因 ${point.incomplete_reason}` : ''}</li>)}</ul>
        <a href={`/api/novelty/report-artifacts/${encodeURIComponent(id)}/provenance`} download="provenance.json">下载来源说明</a>
      </>}
    </div>
    {error ? <div className="panel"><p role="alert">{error}</p><button onClick={onClose}>返回</button></div>
      : file ? <FilePreview file={file} onClose={onClose}/>
      : <div className="panel"><p role="status">正在读取已登记报告…</p></div>}
  </section>;
}
