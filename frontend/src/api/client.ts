export type Snapshot = {run_id: string; status: 'pending'|'running'|'completed'|'failed'; stage: string; completed: string[]; started_at: string|null; updated_at: string; error: {code: string; message: string}|null};
export type Artifact = {type: string; available: boolean; revision?: number};
export class ApiError extends Error { constructor(message: string, public status: number) {super(message);} }
export async function request<T>(path: string, options: RequestInit = {}, signal?: AbortSignal): Promise<T> {
  const timeout = AbortSignal.timeout(60000);
  const response = await fetch(path, {...options, signal: signal ? AbortSignal.any([signal, timeout]) : timeout, cache: 'no-store'});
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(body?.detail?.message || (typeof body?.detail === 'string' ? body.detail : `请求失败（${response.status}）`), response.status);
  }
  return response.json() as Promise<T>;
}
export const runPath = (id: string) => `/api/runs/${encodeURIComponent(id)}`;
