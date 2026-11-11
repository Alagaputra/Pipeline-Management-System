import { defineConfig } from '@playwright/test'
export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,
  workers: 1,
  use: {
    baseURL: 'http://127.0.0.1:5174',
    headless: true,
    reducedMotion: 'reduce',
    viewport: { width: 1440, height: 1080 },
    launchOptions: { channel: 'msedge' },
  },
  webServer: [
    {
      command: 'php.cmd artisan serve --host=127.0.0.1 --port=8001',
      cwd: '../backend',
      url: 'http://127.0.0.1:8001/up',
      reuseExistingServer: true,
      env: {
        DB_CONNECTION: 'pgsql',
        DB_DATABASE: 'pipeline_funding_test',
        PHP_CLI_SERVER_WORKERS: '1',
      },
    },
    {
      command: 'npm run dev -- --port 5174 --strictPort',
      url: 'http://127.0.0.1:5174',
      reuseExistingServer: false,
      env: { PIPELINE_API_TARGET: 'http://127.0.0.1:8001' },
    },
  ],
})
