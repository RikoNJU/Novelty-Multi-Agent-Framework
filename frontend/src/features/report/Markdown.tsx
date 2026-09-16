import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
export function Markdown({ text }: { text: string }) {
  return <div className="markdown"><ReactMarkdown remarkPlugins={[remarkGfm]} skipHtml components={{
    a: ({ href, children }) => <a href={href} target="_blank" rel="noopener noreferrer">{children}</a>,
    img: ({ alt }) => <span>[图片：{alt || '未加载外部图片'}]</span>,
    table: ({ children }) => <div className="table-scroll"><table>{children}</table></div>,
  }}>{text}</ReactMarkdown></div>;
}
