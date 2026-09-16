import { afterEach, expect, it, vi } from 'vitest';
import { poll } from './polling';
import { renderReport } from './report';
afterEach(() => vi.useRealTimers());
it('does not overlap and stops on terminal status', async () => {
  vi.useFakeTimers();
  let finish!: (value:boolean)=>void;
  const task = vi.fn().mockImplementationOnce(() => new Promise<boolean>(resolve => {finish=resolve;})).mockResolvedValue(false);
  const stop = poll(task);
  await vi.advanceTimersByTimeAsync(10000);
  expect(task).toHaveBeenCalledTimes(1);
  finish(true); await vi.advanceTimersByTimeAsync(2500);
  expect(task).toHaveBeenCalledTimes(2);
  await vi.advanceTimersByTimeAsync(10000); expect(task).toHaveBeenCalledTimes(2); stop();
});
it('aborts obsolete observation and never schedules another request', async () => {
  vi.useFakeTimers(); let signal!:AbortSignal;
  const task = vi.fn(async (value:AbortSignal) => {signal=value; return true;});
  const stop = poll(task); stop(); await vi.advanceTimersByTimeAsync(10000);
  expect(signal.aborted).toBe(true); expect(task).toHaveBeenCalledTimes(1);
});
it('renders tables and quotes but blocks raw HTML and dangerous links', () => {
  const html=renderReport('# 报告\n\n|证据|结论|\n|---|---|\n|不足|未知|\n\n> 引用\n\n<script>alert(1)</script>\n\n[x](javascript:alert(1))\n\n![x](https://remote/image.png)');
  expect(html).toContain('<table>'); expect(html).toContain('<blockquote>');
  expect(html).not.toContain('<script>'); expect(html).not.toContain('href="javascript:'); expect(html).not.toContain('<img');
});
