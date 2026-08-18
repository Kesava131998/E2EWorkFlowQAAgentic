const { test, expect } = require('@playwright/test');
const { BasePage } = require('../pages/base_page');

test.describe('Basic Navigation', () => {
  test('homepage loads successfully', async ({ page }) => {
    const basePage = new BasePage(page);

    await test.step('Navigate to base URL', async () => {
      await basePage.navigateTo('https://example.com');
    });

    await test.step('Verify page title', async () => {
      expect(await page.title()).toContain('Example Domain');
    });

    await test.step('Take screenshot', async () => {
      await basePage.takeScreenshot('homepage');
    });
  });
});
