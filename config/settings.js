require('dotenv').config();

const settings = {
  // Timeouts
  TIMEOUT: Number(process.env.TIMEOUT || 30000),
  PAGE_LOAD_TIMEOUT: Number(process.env.PAGE_LOAD_TIMEOUT || 60000),
  SHORT_TIMEOUT: Number(process.env.SHORT_TIMEOUT || 5000),

  // URLs
  BASE_URL: process.env.BASE_URL || 'https://revflow-dev.axgsolutions.com',

  // Auth (RevFlow uses Microsoft Azure AD SSO)
  AUTH_USERNAME: process.env.AUTH_USERNAME || '',
  AUTH_PASSWORD: process.env.AUTH_PASSWORD || '',

  // Browser settings
  HEADLESS: (process.env.HEADLESS || 'true').toLowerCase() === 'true',
  BROWSER: process.env.BROWSER || 'chromium',

  // Parallel settings
  WORKERS: Number(process.env.WORKERS || 1),

  // Reporting
  ALLURE_DIR: process.env.ALLURE_DIR || 'reports/allure-results',
  HTML_REPORT_DIR: process.env.HTML_REPORT_DIR || 'reports/html',
  SCREENSHOT_DIR: process.env.SCREENSHOT_DIR || 'reports/screenshots',
  REPORTS_DIR: process.env.REPORTS_DIR || 'reports',
};

module.exports = { settings };
