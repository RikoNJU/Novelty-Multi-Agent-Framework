import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './tests', fullyParallel: true, workers: 2, timeout: 30000,
  use: { baseURL: 'http://127.0.0.1:5187', launchOptions: { executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE }, trace: 'retain-on-failure' },
  webServer: { command: 'pnpm dev --port 5187 --strictPort', url: 'http://127.0.0.1:5187', reuseExistingServer: false, env: {VITE_FILE_API_ENABLED:'true'} },
});
