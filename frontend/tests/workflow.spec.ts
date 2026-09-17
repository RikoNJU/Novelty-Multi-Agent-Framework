import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
const snapshot = (status: string) => ({task_id:'test-run', status, created_at:'2026-09-16', updated_at:'2026-09-16', result:null, error:null});
const report = { available_formats:['md'], preview_url:'/api/novelty/runs/test-run/report?disposition=inline', downloads:{md:'/api/novelty/runs/test-run/report?disposition=attachment'} };
test.beforeEach(async ({page}) => { await page.route('https://box.nju.edu.cn/**', route => route.abort()); });
test('上传页仅显示论文上传框，并可返回首页', async ({page}) => {
  await page.goto('/'); await page.getByRole('button',{name:'开始',exact:true}).click();
  await expect(page.getByRole('button',{name:'选择论文 PDF'})).toBeVisible();
  await expect(page.getByText('上传参考文献')).toHaveCount(0);
  await page.getByRole('button',{name:'返回首页',exact:true}).click();
  await expect(page.getByRole('button',{name:'开始',exact:true})).toBeVisible();
});
test('上传 → 真实契约轮询 → 完成 → Markdown 预览与下载，并刷新恢复', async ({page}) => {
  let posts = 0; let polls = 0;
  await page.route('**/api/novelty/runs/files', async route => { posts++; expect(route.request().postDataBuffer()?.toString()).toContain('论文.pdf'); await route.fulfill({status:202,json:snapshot('queued')}); });
  await page.route('**/api/novelty/runs/test-run', route => { polls++; return route.fulfill({json: polls < 2 ? snapshot('running') : {...snapshot('succeeded'), report}}); });
  await page.route('**/api/novelty/runs/test-run/report?*', route => route.fulfill({body:'# 查新报告\n\n证据不足，无法裁定。\n\n| 查新点 | 状态 |\n|---|---|\n| A | 待核验 |', headers:{'content-type':'text/markdown; charset=utf-8','content-disposition':"inline; filename*=UTF-8''%E6%9F%A5%E6%96%B0.md"}}));
  await page.goto('/'); await page.getByRole('button',{name:'开始',exact:true}).click();
  await page.getByLabel('论文文件', {exact:true}).setInputFiles({name:'论文.pdf',mimeType:'application/pdf',buffer:Buffer.from('%PDF-1.4 test')});
  await page.getByRole('button',{name:'开始查新'}).click();
  await expect(page).toHaveURL(/run=test-run/); await expect(page.getByRole('heading',{name:'查新完成',exact:true})).toBeVisible(); expect(posts).toBe(1);
  await page.getByRole('button',{name:'查看查新报告'}).click(); await expect(page.getByRole('table')).toBeVisible();
  const download = page.waitForEvent('download'); await page.getByRole('button',{name:'下载',exact:true}).click(); expect((await download).suggestedFilename()).toBe('查新.md');
  await page.reload(); await expect(page.getByRole('table')).toBeVisible(); expect(posts).toBe(1);
  expect((await new AxeBuilder({page}).analyze()).violations).toEqual([]);
});
for (const status of [404,422,500]) test(`任务查询 HTTP ${status}`,async ({page}) => {
  await page.route('**/api/novelty/runs/test-run',route => route.fulfill({status,json:{detail:'secret key /private/path'}}));
  await page.goto('/?run=test-run');
  await expect(page.getByText(status===404 ? '任务已失效' : status===422 ? '暂时遇到问题' : '连接中断，正在重连',{exact:true})).toBeVisible();
  await expect(page.getByText('secret key',{exact:false})).toHaveCount(0);
});
test('断网重连不会把任务变成失败',async ({page}) => {
  let offline=true; await page.route('**/api/novelty/runs/test-run',route => offline ? route.abort() : route.fulfill({json:snapshot('running')}));
  await page.goto('/?run=test-run'); await expect(page.getByText('连接中断，正在重连')).toBeVisible(); offline=false; await expect(page.getByRole('heading',{name:'正在查新',exact:true})).toBeVisible({timeout:10000});
});
test('报告加载失败可重试且保留任务',async ({page}) => {
  await page.route('**/api/novelty/runs/test-run',route => route.fulfill({json:{...snapshot('succeeded'),report}}));
  await page.route('**/api/novelty/runs/test-run/report?*',route => route.fulfill({status:500}));
  await page.goto('/?run=test-run&view=report'); await expect(page.getByRole('button',{name:'重新加载报告'})).toBeVisible();
  await page.getByRole('button',{name:'返回',exact:true}).click(); await expect(page.getByRole('heading',{name:'查新完成',exact:true})).toBeVisible();
});
for (const width of [390,768,1440]) test(`布局、背景失败、无障碍 ${width}`, async ({page}) => {
  await page.setViewportSize({width,height:900}); await page.emulateMedia({reducedMotion:'reduce'}); await page.goto('/');
  await expect(page.getByRole('heading',{name:'睿文查新'})).toBeVisible(); await page.screenshot({path:`test-results/landing-${width}.png`});
  expect((await new AxeBuilder({page}).analyze()).violations).toEqual([]);
  await page.getByRole('button',{name:'开始',exact:true}).click(); await page.getByRole('button',{name:'开始查新'}).click(); await expect(page.getByRole('button',{name:'选择论文 PDF'})).toBeFocused();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
  expect((await new AxeBuilder({page}).analyze()).violations).toEqual([]); await page.screenshot({path:`test-results/upload-${width}.png`,fullPage:true});
});
test('提交 422 后保留文件，允许修改重试', async ({page}) => {
  await page.route('**/api/novelty/runs/files', route => route.fulfill({status:422,json:{detail:'/private/secret'}}));
  await page.goto('/'); await page.getByRole('button',{name:'开始',exact:true}).click();
  await page.getByLabel('论文文件',{exact:true}).setInputFiles({name:'论文.pdf',mimeType:'application/pdf',buffer:Buffer.from('%PDF')});
  await page.getByRole('button',{name:'开始查新'}).click(); await expect(page.getByText('文件或请求未通过校验，请检查后重新提交。')).toBeVisible(); await expect(page.getByRole('button',{name:'删除 论文.pdf'})).toBeEnabled();
});
test('服务端阶段驱动进度，失败异常不暴露原文', async ({page}) => {
  let failed = false;
  await page.route('**/api/novelty/runs/test-run', route => route.fulfill({json:failed ? {...snapshot('failed'),error:'API_KEY=secret'} : {...snapshot('running'),progress:{stage:'validate_evidence',round:2}}}));
  await page.goto('/?run=test-run'); await expect(page.getByText('第 5 / 6 阶段 · 正在补充检索 · 第 2 轮')).toBeVisible();
  failed=true; await expect(page.getByRole('heading',{name:'暂时遇到问题'})).toBeVisible(); await expect(page.getByText('API_KEY=secret')).toHaveCount(0);
});
test('原有结构化结果可预览，不显示不存在的下载',async ({page}) => {
  await page.route('**/api/novelty/runs/test-run',route=>route.fulfill({json:{...snapshot('succeeded'),result:{report:{paper_id:'P-001',conclusions:[{novelty_point_id:'NP-1',review_status:'insufficient_evidence',summary:'证据不足，无法裁定。'}],limitations:['检索范围有限']}}}}));
  await page.goto('/?run=test-run&view=report'); await expect(page.getByText('检索范围有限')).toBeVisible(); await expect(page.getByRole('button',{name:'下载',exact:true})).toHaveCount(0);
});
function smallPdf() {
  const objects = ['<< /Type /Catalog /Pages 2 0 R >>','<< /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 >>','<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 400] /Resources << >> >>','<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 400] /Resources << >> >>'];
  let pdf='%PDF-1.4\n'; const offsets=[0]; objects.forEach((obj,i)=>{offsets.push(pdf.length);pdf+=`${i+1} 0 obj\n${obj}\nendobj\n`;});
  const start=pdf.length;pdf+=`xref\n0 5\n0000000000 65535 f \n${offsets.slice(1).map(n=>String(n).padStart(10,'0')+' 00000 n \n').join('')}trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n${start}\n%%EOF`;return Buffer.from(pdf);
}
test('PDF 本地预览、翻页、缩放、返回保留文件，无运行异常',async ({page}) => {
  const errors:string[]=[];page.on('pageerror',error=>errors.push(error.message));
  await page.goto('/');await page.getByRole('button',{name:'开始',exact:true}).click();
  await page.getByLabel('论文文件',{exact:true}).setInputFiles({name:'论文.pdf',mimeType:'application/pdf',buffer:smallPdf()});
  await page.getByRole('button',{name:'预览 论文.pdf'}).click();await expect(page.locator('canvas')).toBeVisible();await expect(page.getByText('1 / 2',{exact:true})).toBeVisible();
  await page.getByRole('button',{name:'下一页'}).click();await expect(page.getByText('2 / 2',{exact:true})).toBeVisible();await page.getByRole('button',{name:'放大',exact:true}).click();await expect(page.getByText('125%',{exact:true})).toBeVisible();
  await page.getByRole('button',{name:'返回',exact:true}).click();await expect(page.getByRole('button',{name:'预览 论文.pdf'})).toBeVisible();expect(errors).toEqual([]);
});
