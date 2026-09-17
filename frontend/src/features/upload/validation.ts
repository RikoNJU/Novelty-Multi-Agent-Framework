function positive(value: string | undefined, fallback: number) { const n = Number(value); return Number.isInteger(n) && n > 0 ? n : fallback; }
export const limits = {
  fileBytes: positive(import.meta.env.VITE_MAX_FILE_MB, 30) * 1024 * 1024,
  totalBytes: positive(import.meta.env.VITE_MAX_TOTAL_MB, 100) * 1024 * 1024,
  references: positive(import.meta.env.VITE_MAX_REFERENCES, 20),
};
export const accepts = { paper: '.pdf,application/pdf', references: '.pdf,.md,.markdown,.txt,application/pdf,text/markdown,text/plain' };
export function validateFiles(files: File[], kind: 'paper' | 'references', other: File[] = []): string | null {
  if (kind === 'paper' && files.length !== 1) return '请只选择一篇论文 PDF';
  if (kind === 'references' && files.length > limits.references) return `参考文献最多 ${limits.references} 个`;
  for (const file of files) {
    const ext = file.name.split('.').pop()?.toLowerCase();
    const allowed = kind === 'paper' ? ['pdf'] : ['pdf', 'md', 'markdown', 'txt'];
    if (!ext || !allowed.includes(ext)) return kind === 'paper' ? '论文原文仅支持 PDF' : '参考文献仅支持 PDF、Markdown 和纯文本';
    const mime = ext === 'pdf' ? ['application/pdf'] : ['text/plain', 'text/markdown', 'text/x-markdown'];
    if (file.type && file.type !== 'application/octet-stream' && !mime.includes(file.type)) return '文件类型与扩展名不符，请重新选择';
    if (!file.size) return '不能上传空文件';
    if (file.size > limits.fileBytes) return `单个文件不能超过 ${size(limits.fileBytes)}`;
  }
  if ([...files, ...other].reduce((sum, f) => sum + f.size, 0) > limits.totalBytes) return `文件总大小不能超过 ${size(limits.totalBytes)}`;
  return null;
}
export function size(bytes: number) { return bytes < 1024 * 1024 ? `${Math.max(1, Math.ceil(bytes / 1024))} KB` : `${+(bytes / 1024 / 1024).toFixed(1)} MB`; }
