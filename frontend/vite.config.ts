import { defineConfig, loadEnv } from 'vite';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

export default defineConfig(({ mode }) => ({
  server: { proxy: { '/api': loadEnv(mode, '.', '').NOVELTY_API_TARGET || 'http://localhost:8010' } },
  plugins: [{
    name: 'static-shell-service-worker', enforce: 'post',
    generateBundle(_, bundle) {
      const assets = Object.keys(bundle).filter(name => /\.(js|css)$/.test(name)).map(name => '/' + name);
      const revision = createHash('sha256').update(JSON.stringify(Object.values(bundle).map(entry => entry.type === 'asset' ? String(entry.source) : entry.code))).update(readFileSync('public/manifest.webmanifest')).update(readFileSync('public/icon-192.png')).update(readFileSync('public/icon-512.png')).digest('hex').slice(0, 16);
      this.emitFile({ type: 'asset', fileName: 'sw.js', source: `
const CACHE = 'novelty-${revision}';
const SHELL = ['/', '/index.html', '/manifest.webmanifest', '/icon-192.png', '/icon-512.png', ...${JSON.stringify(assets)}];
self.addEventListener('install', event => event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(SHELL))));
self.addEventListener('message', event => { if (event.data === 'ACTIVATE') self.skipWaiting(); });
self.addEventListener('activate', event => event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key.startsWith('novelty-') && key !== CACHE).map(key => caches.delete(key)))).then(() => self.clients.claim())));
self.addEventListener('fetch', event => {
 const url = new URL(event.request.url);
 if (event.request.method !== 'GET' || url.origin !== self.location.origin || url.pathname.startsWith('/api/')) return;
 if (event.request.mode === 'navigate' && (url.pathname === '/' || url.pathname === '/index.html')) {
  event.respondWith(fetch(event.request).catch(() => caches.match('/index.html'))); return;
 }
 if (SHELL.includes(url.pathname) && !url.search) event.respondWith(caches.match(event.request).then(hit => hit || fetch(event.request)));
});` });
    }
  }]
}));
