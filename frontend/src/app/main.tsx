import { StrictMode, Component, type ReactNode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import '../styles/global.css';
class ErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() { return this.state.failed ? <main className="workspace"><section className="panel"><h1>页面暂时无法显示</h1><p>请刷新页面重试，已有任务会在服务端继续运行。</p><button className="primary" onClick={() => location.reload()}>刷新页面</button></section></main> : this.props.children; }
}
createRoot(document.getElementById('root')!).render(<StrictMode><ErrorBoundary><BrowserRouter><App/></BrowserRouter></ErrorBoundary></StrictMode>);
