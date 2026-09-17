import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { expect, test } from '@playwright/test';

const cases = [
  { label: 'L1', id: process.env.REPORT_RESOURCE_L1, source: process.env.REPORT_MARKDOWN_L1 },
  { label: 'L2', id: process.env.REPORT_RESOURCE_L2, source: process.env.REPORT_MARKDOWN_L2 },
];

for (const item of cases) test(`${item.label} 真实后端只读报告预览和下载`, async ({ page, request }) => {
  test.skip(!item.id || !item.source, 'local registered resource was not supplied');
  const id = item.id!;
  const original = readFileSync(item.source!);
  const hash = createHash('sha256').update(original).digest('hex');
  const requests: { method: string; url: string }[] = [];
  page.on('request', req => { if (req.url().includes('/api/')) requests.push({ method: req.method(), url: req.url() }); });
  await page.goto(`/?report_resource_id=${id}`);
  await expect(page.getByRole('heading', { name: '历史运行的恢复报告' })).toBeVisible();
  await expect(page.getByText('原完整运行失败', { exact: false })).toBeVisible();
  await expect(page.getByText('资源完整性：passed', { exact: false })).toBeVisible();
  await expect(page.getByRole('heading', { name: `recovery-report-${id}.md` })).toBeVisible();
  for (const pointId of ['NP-1', 'NP-2', 'NP-3']) {
    await expect(page.getByText(`${pointId}：`, { exact: false }).first()).toBeVisible();
  }
  if (item.label === 'L1') await expect(page.getByText('technical_error', { exact: false }).first()).toBeVisible();
  const metadata = await request.get(`http://127.0.0.1:5187/api/novelty/report-artifacts/${id}`);
  expect(metadata.status()).toBe(200);
  expect((await metadata.json()).files['report.md'].sha256).toBe(hash);
  const provenance = await request.get(`http://127.0.0.1:5187/api/novelty/report-artifacts/${id}/provenance`);
  expect(provenance.status()).toBe(200);
  expect((await provenance.json()).source_run_status).toBe('FAILED');
  const direct = await request.get(`http://127.0.0.1:5187/api/novelty/report-artifacts/${id}/download`);
  expect(direct.status()).toBe(200);
  expect(direct.headers()['content-type']).toContain('text/markdown');
  expect(createHash('sha256').update(await direct.body()).digest('hex')).toBe(hash);
  const downloaded = page.waitForEvent('download');
  await page.getByRole('button', { name: '下载', exact: true }).click();
  const download = await downloaded;
  expect(createHash('sha256').update(readFileSync(await download.path())).digest('hex')).toBe(hash);
  await page.reload();
  await expect(page.getByRole('heading', { name: `recovery-report-${id}.md` })).toBeVisible();
  await page.goto(`/?report_resource_id=${id}`);
  await expect(page.getByRole('heading', { name: `recovery-report-${id}.md` })).toBeVisible();
  expect(requests.some(req => req.method !== 'GET')).toBe(false);
  expect(requests.some(req => req.url.includes(`/report-artifacts/${id}/content`))).toBe(true);
  await page.screenshot({ path: test.info().outputPath(`${item.label}-real-api.png`), fullPage: true });
});
