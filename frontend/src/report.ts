import MarkdownIt from 'markdown-it';
const markdown = new MarkdownIt({html: false, linkify: false, breaks: false});
// Reports do not require remote images; avoid third-party requests and local path guesses.
markdown.renderer.rules.image = () => '<span>[图片未加载]</span>';
export const renderReport = (content: string): string => markdown.render(content);
