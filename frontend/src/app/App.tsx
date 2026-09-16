import { useEffect, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { ArrowRight, Check, RotateCcw } from 'lucide-react';
import { api, normalizeError } from '../api/client';
import type { Phase } from '../api/contracts';
import { UploadView } from '../features/upload/UploadView';
import { useRun } from '../features/run-progress/useRun';
import { ProgressView } from '../features/run-progress/ProgressView';
import { ReportView } from '../features/report/ReportView';
export default function App() {
  const [params, setParams] = useSearchParams(); const id = params.get('run');
  const [localPhase, setPhase] = useState<Phase>('landing');
  const [paper, setPaper] = useState<File | null>(null); const [references, setReferences] = useState<File[]>([]);
  const [submitError, setSubmitError] = useState<string | null>(null); const submitting = useRef(false);
  const controller = useRef<AbortController | null>(null);
  const { snapshot, error, reconnecting, retry } = useRun(id);
  const phase: Phase = id ? error ? 'failed' : snapshot?.status === 'succeeded' && params.get('view') === 'report' ? 'previewing' : snapshot?.status ?? 'running' : localPhase;
  const main = useRef<HTMLElement>(null);
  const celebrated = useRef(new Set<string>());
  const animateSuccess = !!id && !celebrated.current.has(id);
  useEffect(() => { if (phase === 'succeeded' && id) celebrated.current.add(id); }, [phase, id]);
  useEffect(() => { main.current?.focus(); }, [phase]);
  useEffect(() => () => controller.current?.abort(), []);
  const restart = () => { setParams({}); setPhase('editing'); setSubmitError(null); };
  const submit = async () => {
    if (!paper || submitting.current) return;
    submitting.current = true; setPhase('submitting'); setSubmitError(null); controller.current = new AbortController();
    try {
      const next = await api.createRun(paper, references, controller.current.signal);
      if (controller.current.signal.aborted) return;
      setParams({ run: next.task_id }); setPhase('editing'); setPaper(null); setReferences([]);
    } catch (cause) {
      if (!controller.current.signal.aborted) {
        const failure = normalizeError(cause);
        setSubmitError(failure.code === 'timeout' || failure.code === 'network' ? '未能确认提交结果。任务可能已创建，请联系服务管理员确认后再提交，以免重复。' : failure.message); setPhase('editing');
      }
    } finally { submitting.current = false; }
  };
  return <div className="app-shell" onDragOver={e => e.preventDefault()} onDrop={e => e.preventDefault()}>
    {phase !== 'landing' && <header className="brand">睿文查新</header>}
    <main ref={main} tabIndex={-1} className={phase === 'landing' ? 'landing-main' : 'workspace'}>
      {phase === 'landing' && <section className="landing"><h1>睿文查新</h1><p>上传论文与参考文献，自动完成查新点提取、文献检索和证据核验，<br className="desktop-break"/>生成可追溯的查新报告。</p><button className="primary start" onClick={() => setPhase('editing')}>开始<ArrowRight size={21}/></button></section>}
      {(phase === 'editing' || phase === 'submitting') && <UploadView paper={paper} references={references} onFiles={(p, r) => { setPaper(p); setReferences(r); setSubmitError(null); }} onSubmit={() => void submit()} busy={phase === 'submitting'} error={submitError}/>}
      {(phase === 'queued' || phase === 'running') && <ProgressView snapshot={snapshot} reconnecting={reconnecting}/>}
      {phase === 'succeeded' && <section className="panel completion"><div className={`success-mark ${animateSuccess ? 'animate-success' : ''}`}><Check size={40}/></div><p className="eyebrow">本次查新已结束</p><h1>查新完成</h1><button className="primary" onClick={() => setParams({ run: id!, view: 'report' })}>查看查新报告<ArrowRight size={18}/></button><button className="text-button" onClick={restart}>开始新的查新</button></section>}
      {phase === 'previewing' && snapshot && <ReportView run={snapshot} onClose={() => setParams({ run: id! })}/>}
      {phase === 'failed' && <section className="panel failure"><p className="eyebrow">本次查新未能完成</p><h1>{error?.status === 404 ? '任务已失效' : '暂时遇到问题'}</h1><p role="alert">{error?.message ?? '查新运行失败。请检查文件后重新开始，或联系服务管理员。'}</p><p className="task-id">任务编号 {id}</p><button className="primary" onClick={restart}>重新开始<RotateCcw size={18}/></button>{error && error.status !== 404 && <button className="text-button" onClick={retry}>重新查询任务</button>}</section>}
    </main>
  </div>;
}
