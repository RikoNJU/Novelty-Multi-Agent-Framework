import './styles/main.css';
import { ApiError, request, runPath, type Snapshot, type Artifact } from './api/client';
import { poll } from './polling';
import { renderReport } from './report';

const el = <T extends HTMLElement = HTMLElement>(id: string) => document.getElementById(id) as T;
const names: Record<string,string> = {input:'输入处理',parse:'论文解析',novelty_points:'查新点生成',research:'文献检索与阅读',review:'结果审查',render:'报告生成'};
const artifactNames: Record<string,string> = {novelty_points:'查新点',search_results:'检索证据摘要',review:'审查结果与告警'};
let selected: File|null = null, submitting = false, active = false, current: string|null = null, stop = () => {}, generation = 0;
function notice(id: string, message = '') {el(id).textContent = message; el(id).hidden = !message;}
function buttons() {el<HTMLButtonElement>('start').disabled = !selected || submitting || active; el<HTMLInputElement>('file').disabled = submitting; el<HTMLButtonElement>('remove').disabled = submitting;}
function select(files: FileList|null) {
  if (submitting) return;
  selected = null;
  notice('upload-error');
  if (!files || files.length !== 1) notice('upload-error', '请选择一个 PDF 文件。');
  else if (!files[0].name.toLowerCase().endsWith('.pdf')) notice('upload-error', '仅支持 PDF 文件。');
  else if (files[0].size === 0 || files[0].size > 25 * 1024 * 1024) notice('upload-error', '请选择非空且不超过 25 MiB 的 PDF。');
  else selected = files[0];
  el('selection').hidden = !selected;
  el('filename').textContent = selected ? `${selected.name} · ${(selected.size / 1024 / 1024).toFixed(2)} MiB` : '';
  buttons();
}
el<HTMLInputElement>('file').onchange = event => select((event.target as HTMLInputElement).files);
el('remove').onclick = () => {select(null); notice('upload-error'); el<HTMLInputElement>('file').value = '';};
for (const event of ['dragover','drop']) el('drop').addEventListener(event, e => e.preventDefault());
el('drop').addEventListener('drop', event => select(event.dataTransfer?.files || null));
el('start').onclick = async () => {
  if (!selected || submitting || active) return;
  submitting = true; buttons(); notice('upload-error');
  el('start').textContent = '正在上传…';
  try {
    const body = new FormData(); body.append('file', selected);
    const run = await request<{run_id: string}>('/api/runs', {method: 'POST', body});
    const url = new URL(location.href); url.searchParams.set('run', run.run_id); history.replaceState(null, '', url);
    observe(run.run_id);
  } catch (error) {
    notice('upload-error', error instanceof ApiError ? `上传失败：${error.message}` : '上传连接中断，未能确认是否创建运行。请检查服务，避免连续重复提交。');
  } finally {submitting = false; el('start').textContent = '开始查新 →'; buttons();}
};
function display(state: Snapshot) {
  el('status').textContent = {pending:'等待执行',running:'正在查新',completed:'查新完成',failed:'运行失败'}[state.status];
  el('stage').textContent = `当前阶段：${names[state.stage] || state.stage}`;
  el('steps').replaceChildren(...Object.entries(names).map(([key, name]) => {
    const item = document.createElement('li'); item.textContent = `${state.completed.includes(key) ? '✓' : '○'} ${name}`;
    if (key === state.stage && state.status === 'running') item.className = 'current';
    return item;
  }));
  const elapsed = state.started_at ? Math.max(0, Math.floor(((active ? Date.now() : Date.parse(state.updated_at)) - Date.parse(state.started_at))/1000)) : 0;
  el('elapsed').textContent = state.started_at ? `已用时 ${Math.floor(elapsed/60)} 分 ${elapsed%60} 秒` : '等待后端开始执行';
  notice('task-error', state.error?.message || '');
}
async function loadReport(id: string, token: number) {
  notice('report-error'); el('retry-report').hidden = true;
  try {
    const result = await request<{content:string}>(runPath(id)+'/report');
    if (token !== generation) return;
    el('report').innerHTML = renderReport(result.content);
    el('report-placeholder').hidden = true;
    const link = el<HTMLAnchorElement>('download'); link.href = runPath(id)+'/report.md'; link.hidden = false;
  } catch (error) {
    if (token !== generation) return;
    notice('report-error', `报告获取失败：${error instanceof Error ? error.message : '连接错误'}`);
    el('retry-report').hidden = false;
  }
}
async function loadArtifacts(id: string, token: number, signal: AbortSignal) {
  try {
    const result = await request<{artifacts: Artifact[]}>(runPath(id)+'/artifacts', {}, signal);
    if (token !== generation || signal.aborted) return;
    el('artifacts-panel').hidden = false; notice('artifact-error');
    for (const entry of result.artifacts) {
      const key = `artifact-${entry.type}`;
      let details = document.getElementById(key) as HTMLDetailsElement|null;
      if (details && details.dataset.available === `${entry.available}:${entry.revision}`) continue;
      const replacement = document.createElement('details'); replacement.id = key; replacement.dataset.available = `${entry.available}:${entry.revision}`;
      const summary = document.createElement('summary'); summary.textContent = `${artifactNames[entry.type] || entry.type} · ${entry.available ? '可查看' : '等待生成'}`;
      replacement.append(summary);
      replacement.ontoggle = async () => {
        if (!replacement.open || !entry.available || replacement.querySelector('pre')) return;
        try {
          const content = await request<unknown>(runPath(id)+'/artifacts/'+encodeURIComponent(entry.type));
          if (token !== generation || !replacement.isConnected) return;
          const pre = document.createElement('pre'); pre.textContent = JSON.stringify(content, null, 2); replacement.append(pre);
        } catch {notice('artifact-error', '阶段成果获取失败，可收起后重新展开。');}
      };
      if (details) details.replaceWith(replacement); else el('artifacts').append(replacement);
    }
  } catch {if (token === generation && !signal.aborted) notice('artifact-error', '暂时无法获取阶段成果，不影响查新执行。');}
}
function observe(id: string) {
  stop(); const token = ++generation; current = id; active = true; buttons();
  el('run-id').textContent = `运行编号 ${id}`;
  el('report').replaceChildren(); el('artifacts').replaceChildren();
  el('download').hidden = true; el('report-placeholder').hidden = false; el('retry-report').hidden = true;
  for (const area of ['task-error','report-error','connection-error','artifact-error']) notice(area);
  stop = poll(async signal => {
    try {
      const state = await request<Snapshot>(runPath(id), {}, signal);
      if (token !== generation || signal.aborted) return false;
      active = state.status === 'running' || state.status === 'pending';
      display(state); buttons(); notice('connection-error');
      if (!active) {
        void loadArtifacts(id, token, signal);
        if (state.status === 'completed') void loadReport(id, token);
        return false;
      }
      await loadArtifacts(id, token, signal);
      return true;
    } catch (error) {
      if (token !== generation || signal.aborted) return false;
      if (error instanceof ApiError && error.status === 404) {
        active = false; buttons(); el('status').textContent = '运行不存在'; notice('connection-error', '未找到该运行，请确认链接或重新提交。'); return false;
      }
      notice('connection-error', '暂时无法获取状态，正在重试。连接中断不代表任务失败。'); return true;
    }
  });
}
el('retry-report').onclick = () => {if (current) void loadReport(current, generation);};
window.addEventListener('pagehide', () => stop());
window.addEventListener('pageshow', event => {if (event.persisted && current) observe(current);});
const restored = new URL(location.href).searchParams.get('run'); if (restored) observe(restored);
const stopHealth = poll(async signal => {
  try {await request('/api/health', {}, signal); notice('service');} catch {if (!signal.aborted) notice('service', '后端服务暂时不可用。请检查 Python 服务与网络连接。');}
  return true;
}, 15000);
window.addEventListener('pagehide', () => stopHealth());
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  void navigator.serviceWorker.register('/sw.js').then(registration => {
    function updateReady() {
      if (!registration.waiting || !navigator.serviceWorker.controller) return;
      el('update').hidden = false;
      el('refresh').onclick = () => {
        if (submitting) {notice('service', '请等待上传完成后更新页面。'); return;}
        navigator.serviceWorker.addEventListener('controllerchange', () => location.reload(), {once:true});
        registration.waiting?.postMessage('ACTIVATE');
      };
    }
    updateReady();
    registration.addEventListener('updatefound', () => registration.installing?.addEventListener('statechange', updateReady));
  }).catch(() => {/* ordinary web access remains available */});
}
