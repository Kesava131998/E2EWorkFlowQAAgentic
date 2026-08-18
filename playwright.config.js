require('dotenv').config();
const { defineConfig, devices } = require('@playwright/test');

/**
 * Replaces the old pyproject.toml [tool.pytest.ini_options] block.
 * Tag-based filtering (was pytest markers slow/smoke/regression) — tag test titles
 * with @slow / @smoke / @regression and filter via `--grep @smoke`.
 */
module.exports = defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.js',
  timeout: 60_000,
  fullyParallel: false,
  workers: process.env.WORKERS ? Number(process.env.WORKERS) : 1,
  retries: 0,
  reporter: [
    ['html', { outputFolder: 'reports/html', open: 'never' }],
    ['allure-playwright', { outputFolder: 'reports/allure-results' }],
    ['list'],
  ],
  use: {
    baseURL: process.env.BASE_URL || 'https://revflow-dev.axgsolutions.com',
    headless: (process.env.HEADLESS || 'true').toLowerCase() === 'true',
    viewport: { width: 1280, height: 720 },
    video: 'retain-on-failure',
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
    actionTimeout: process.env.TIMEOUT ? Number(process.env.TIMEOUT) : 30_000,
    navigationTimeout: process.env.PAGE_LOAD_TIMEOUT ? Number(process.env.PAGE_LOAD_TIMEOUT) : 60_000,
  },
  outputDir: 'test-results',
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
});
