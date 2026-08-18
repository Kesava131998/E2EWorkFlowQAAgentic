const { test, expect } = require('@playwright/test');
const { BasePage } = require('./base_page');
const { settings } = require('../config/settings');

class LoginPage extends BasePage {
  constructor(page) {
    super(page);
    this.microsoftSignInButton = page.locator('arw-login button').first();
    this.emailInputField = page.locator("//input[@type='email']");
    this.submitButton = page.locator("//input[@type='submit']");
    this.passwordInputField = page.locator("//input[@type='password']");
    this.welcomeMessage = page.locator("//h2[contains(text(),'Hi')]");
    this.searchForCase = page.locator("//input[@placeholder='Search for a Case']");
  }

  async launchApplication(baseUrl = settings.BASE_URL) {
    await test.step('Launch the RevFlow application', async () => {
      await this.page.goto(baseUrl);
    });
  }

  async clickMicrosoftSignInButton() {
    await test.step('Click on the Microsoft Sign In button', async () => {
      await expect(this.microsoftSignInButton).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await this.microsoftSignInButton.click();
    });
  }

  async fillUserEmail(email) {
    await test.step('Fill username in the email field', async () => {
      await this.emailInputField.waitFor({ state: 'visible', timeout: settings.PAGE_LOAD_TIMEOUT });
      await this.emailInputField.fill(email);
    });
  }

  async fillUserPassword(password) {
    await test.step('Fill password in the password field', async () => {
      await this.passwordInputField.waitFor({ state: 'visible', timeout: settings.PAGE_LOAD_TIMEOUT });
      await this.passwordInputField.fill(password);
    });
  }

  async clickSubmitButton() {
    await test.step('Click on the Submit button', async () => {
      await this.submitButton.click();
    });
  }

  async loginWithValidCredentials(email, password) {
    await test.step('Log in with valid credentials', async () => {
      await this.page.waitForURL(settings.BASE_URL, { timeout: settings.PAGE_LOAD_TIMEOUT });

      await this.clickMicrosoftSignInButton();
      await this.fillUserEmail(email);
      await this.clickSubmitButton();

      await this.fillUserPassword(password);
      await this.clickSubmitButton();
      // Azure AD's "Stay signed in?" prompt requires a second submit.
      await this.clickSubmitButton();
    });
  }

  async isWelcomeMessageVisible() {
    return this.welcomeMessage.isVisible();
  }
}

module.exports = { LoginPage };
