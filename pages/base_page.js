const { test } = require('@playwright/test');

class BasePage {
  constructor(page) {
    this.page = page;
  }

  async navigateTo(url) {
    await test.step(`Navigate to ${url}`, async () => {
      await this.page.goto(url);
    });
  }

  async waitForLoad() {
    await test.step('Wait for page load', async () => {
      await this.page.waitForLoadState('networkidle');
    });
  }

  async takeScreenshot(name) {
    await test.step('Take screenshot', async () => {
      await this.page.screenshot({ path: `screenshots/${name}.png` });
    });
  }
}

module.exports = { BasePage };
