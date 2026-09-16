import { useEffect, useState } from 'react';
import { api, normalizeError, ApiError } from '../../api/client';
import type { RunSnapshot } from '../../api/contracts';
export const retryDelay = (errors: number, hidden = false) => Math.max(hidden ? 15000 : 1500, Math.min(30000, 1500 * 2 ** errors));
export function useRun(id: string | null) {
  const [snapshot, setSnapshot] = useState<RunSnapshot | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [reconnecting, setReconnecting] = useState(false);
  const [attempt, retry] = useState(0);
  useEffect(() => {
    setSnapshot(null); setError(null); setReconnecting(false);
    if (!id) return;
    const controller = new AbortController(); let timer: ReturnType<typeof setTimeout>; let failures = 0;
    const poll = async () => {
      try {
        const next = await api.getRun(id, controller.signal);
        if (controller.signal.aborted) return;
        if (next.task_id !== id) throw new ApiError('contract', '服务返回的任务编号不匹配，请联系服务管理员。');
        setSnapshot(next); setError(null); setReconnecting(false); failures = 0;
        if (next.status === 'succeeded' || next.status === 'failed') return;
      } catch (cause) {
        if (controller.signal.aborted) return;
        const failure = normalizeError(cause);
        if (failure.code === 'contract' || (failure.status && failure.status < 500 && failure.status !== 429)) { setError(failure); return; }
        setReconnecting(true); failures++;
      }
      timer = setTimeout(poll, retryDelay(failures, document.hidden));
    };
    void poll();
    return () => { controller.abort(); clearTimeout(timer); };
  }, [id, attempt]);
  return { snapshot, error, reconnecting, retry: () => retry(n => n + 1) };
}
