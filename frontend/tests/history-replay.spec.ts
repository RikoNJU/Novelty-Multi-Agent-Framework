import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { resolve } from 'node:path';
import { expect, test } from '@playwright/test';

const source = resolve(process.cwd(), '../docs/experiments/20260917_005448/runs/full/0002/MG19333vrw-debug-full-20260907/report/MG19333vrw-debug-full-20260907-report.md');
const reportBytes = readFileSync(source);
const expectedHash = createHash('sha256').update(reportBytes).digest('hex');

test('历史正式 Markdown 只读回放，无业务创建请求', async ({ page }) => {
  let creates = 0;
  await page.route('**/api/novelty/runs/files', route => { creates++; return route.abort(); });
  await page.route('**/api/novelty/runs/historical-replay', route => route.fulfill({ json: {
    task_id: 'historical-replay', status: 'succeeded', created_at: '2026-09-17',
    updated_at: '2026-09-17', result: null, error: null,
    report: { available_formats: ['md'],
      preview_url: '/api/novelty/runs/historical-replay/report?disposition=inline',
      downloads: { md: '/api/novelty/runs/historical-replay/report?disposition=attachment' } },
  } }));
  await page.route('**/api/novelty/runs/historical-replay/report?*', route => route.fulfill({
    body: reportBytes, headers: { 'content-type': 'text/markdown; charset=utf-8',
      'content-disposition': 'inline; filename="historical-report.md"' },
  }));
  await page.goto('/?run=historical-replay&view=report');
  await expect(page.getByRole('heading', { name: 'historical-report.md' })).toBeVisible();
  await expect(page.locator('.markdown h1').first()).toBeVisible();
  await page.evaluate(() => {
    const label = document.createElement('aside');
    label.textContent = '历史运行回放：只读归档，未重新执行业务流程';
    label.style.cssText = 'position:fixed;top:0;right:0;z-index:9999;background:#fff;color:#111;padding:8px;border:2px solid #111';
    document.body.append(label);
  });
  await page.screenshot({ path: test.info().outputPath('historical-replay.png'), fullPage: true });
  const downloaded = page.waitForEvent('download');
  await page.getByRole('button', { name: '下载', exact: true }).click();
  const file = await downloaded;
  const actual = readFileSync(await file.path());
  expect(createHash('sha256').update(actual).digest('hex')).toBe(expectedHash);
  expect(creates).toBe(0);
});
