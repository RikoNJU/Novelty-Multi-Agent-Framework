import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { limits, validateFiles } from '../features/upload/validation';
import { ApiError, downloadFilename, normalizeError, safeApiUrl } from '../api/client';
import { snapshotSchema, stageIndex } from '../api/contracts';
import { retryDelay } from '../features/run-progress/useRun';
import { UploadView } from '../features/upload/UploadView';
import { Markdown } from '../features/report/Markdown';
const pdf = () => new File(['%PDF-1.4'], '论文.pdf', { type: 'application/pdf' });
describe('文件校验', () => {
  it('校验类型、空文件、数量、MIME 和大小', () => {
    expect(validateFiles([pdf()], 'paper')).toBeNull();
    expect(validateFiles([pdf(), pdf()], 'paper')).toContain('一篇');
    expect(validateFiles([new File(['x'], 'a.docx')], 'references')).toContain('仅支持');
    expect(validateFiles([new File([], 'a.pdf')], 'paper')).toContain('空');
    expect(validateFiles([new File(['x'], 'a.pdf', { type: 'text/html' })], 'paper')).toContain('不符');
    expect(validateFiles(Array(limits.references + 1).fill(pdf()), 'references')).toContain('最多');
    const large = pdf(); Object.defineProperty(large, 'size', {value: limits.fileBytes + 1});
    expect(validateFiles([large], 'paper')).toContain('单个');
    expect(validateFiles([pdf()], 'paper', [{size: limits.totalBytes} as File])).toContain('总大小');
  });
});
it('下载文件名支持中文并清理路径、控制字符', () => {
  expect(downloadFilename("attachment; filename*=UTF-8''%E6%9F%A5%E6%96%B0.md")).toBe('查新.md');
  expect(downloadFilename('attachment; filename="../../report.md"')).toBe('report.md');
  expect(() => downloadFilename(null)).toThrow(ApiError);
});
it('归一化错误不暴露服务端异常', () => {
  expect(normalizeError(new Error('secret key')).message).not.toContain('secret');
  expect(normalizeError(new DOMException('', 'TimeoutError')).code).toBe('timeout');
  expect(() => safeApiUrl('https://attacker.example/report')).toThrow();
});
it('兼容当前后端，阶段映射与重连退避', () => {
  expect(snapshotSchema.parse({task_id:'a', status:'running', created_at:'x', updated_at:'x', error:null, result:null}).progress).toBeUndefined();
  expect(stageIndex('validate_evidence')).toBe(4);
  expect(retryDelay(0)).toBe(1500); expect(retryDelay(10)).toBe(30000); expect(retryDelay(0, true)).toBe(15000);
});
it('缺失论文时阻止提交，播报错误并聚焦上传框', async () => {
  const submit = vi.fn();
  render(<UploadView paper={null} references={[]} onFiles={vi.fn()} onSubmit={submit} busy={false} error={null}/>);
  await userEvent.click(screen.getByRole('button', { name:'开始查新' }));
  expect(screen.getByText('请先上传论文 PDF')).toBeVisible();
  expect(screen.getByRole('button', {name:'选择论文 PDF'})).toHaveFocus(); expect(submit).not.toHaveBeenCalled();
});
it('键盘文件入口和拖放均可选择文件', async () => {
  const onFiles = vi.fn(); render(<UploadView paper={null} references={[]} onFiles={onFiles} onSubmit={vi.fn()} busy={false} error={null}/>);
  const button = screen.getByRole('button', {name:'选择论文 PDF'}); button.focus();
  const input = screen.getByLabelText('论文文件'); const click = vi.spyOn(input, 'click');
  await userEvent.keyboard('{Enter}'); expect(click).toHaveBeenCalled();
  fireEvent.drop(button, {dataTransfer:{files:[pdf()]}}); expect(onFiles).toHaveBeenCalled();
});
it('Markdown 支持表格、禁止原始 HTML、危险链接和外部图片', () => {
  const {container} = render(<Markdown text={'# 报告\n\n| A | B |\n|---|---|\n| 1 | 2 |\n\n<script>alert(1)</script>\n\n[x](javascript:alert(1))\n\n![tracking](https://example.com/pixel)'}/>);
  expect(screen.getByRole('table')).toBeVisible(); expect(container.querySelector('script')).toBeNull(); expect(container.querySelector('img')).toBeNull(); expect(container.querySelector('a')?.getAttribute('href')).not.toContain('javascript:');
});
