import { existsSync, readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { resolve } from 'node:path';
import { expect, test } from '@playwright/test';

const source = resolve(process.cwd(), '../outputs/report-node-recovery-20260918/L1-offline-final/99703e948fce4f1eb12c37de318f764d/report/99703e948fce4f1eb12c37de318f764d-report.md');

test('报告节点离线替身产物只读展示和同字节下载', async ({ page }) => {
  test.skip(!existsSync(source), 'local controlled recovery artifact is unavailable');
  const bytes = readFileSync(source);
  const expectedHash = createHash('sha256').update(bytes).digest('hex');
  let creates = 0;
  await page.route('**/api/novelty/runs/files', route => { creates++; return route.abort(); });
  await page.route('**/api/novelty/runs/recovery-offline', route => route.fulfill({ json: {
    task_id: 'recovery-offline', status: 'succeeded', created_at: '2026-09-18',
    updated_at: '2026-09-18', result: null, error: null,
    report: { available_formats: ['md'],
      preview_url: '/api/novelty/runs/recovery-offline/report?disposition=inline',
      downloads: { md: '/api/novelty/runs/recovery-offline/report?disposition=attachment' } },
  } }));
  await page.route('**/api/novelty/runs/recovery-offline/report?*', route => route.fulfill({
    body: bytes, headers: { 'content-type': 'text/markdown; charset=utf-8',
      'content-disposition': 'inline; filename="report-node-offline.md"' },
  }));
  await page.goto('/?run=recovery-offline&view=report');
  await expect(page.getByRole('heading', { name: 'report-node-offline.md' })).toBeVisible();
  await expect(page.getByText('Reviewer 核验未完成，尚不能作出新颖性裁定。')).toBeVisible();
  await page.evaluate(() => {
    const label = document.createElement('aside');
    label.textContent = '基于历史失败 run 的报告节点离线替身恢复；非完整查新成功';
    label.style.cssText = 'position:fixed;top:0;right:0;z-index:9999;background:#fff;color:#111;padding:8px;border:2px solid #111';
    document.body.append(label);
  });
  await page.screenshot({ path: test.info().outputPath('report-recovery-offline.png'), fullPage: true });
  const downloaded = page.waitForEvent('download');
  await page.getByRole('button', { name: '下载', exact: true }).click();
  const file = await downloaded;
  expect(createHash('sha256').update(readFileSync(await file.path())).digest('hex')).toBe(expectedHash);
  await page.reload();
  expect(creates).toBe(0);
});
