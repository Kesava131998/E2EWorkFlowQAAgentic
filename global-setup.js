require('dotenv').config();
const path = require('path');
const { chromium } = require('@playwright/test');
const { settings } = require('./config/settings');

const STORAGE_STATE_PATH = path.join(__dirname, '.auth', 'state.json');

/**
 * Logs in once via Azure AD SSO and persists the session so every test reuses it.
 * Repeating the live Microsoft login per test tripped Azure AD's sign-in throttling
 * on the shared service account after the first attempt, stranding later tests on
 * the password re-entry screen.
 *
 * Uses raw page calls rather than LoginPage's test.step-wrapped methods — test.step()
 * requires an active test context, which globalSetup does not have.
 */
module.exports = async function globalSetup() {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  await page.goto(settings.BASE_URL);
  await page.waitForURL(settings.BASE_URL, { timeout: settings.PAGE_LOAD_TIMEOUT });

  const microsoftSignInButton = page.locator('arw-login button').first();
  await microsoftSignInButton.waitFor({ state: 'visible', timeout: settings.PAGE_LOAD_TIMEOUT });
  await microsoftSignInButton.click();

  const emailInputField = page.locator("//input[@type='email']");
  const submitButton = page.locator("//input[@type='submit']");
  const passwordInputField = page.locator("//input[@type='password']");
  const searchForCase = page.locator("//input[@placeholder='Search for a Case']");

  await emailInputField.waitFor({ state: 'visible', timeout: settings.PAGE_LOAD_TIMEOUT });
  await emailInputField.fill(settings.AUTH_USERNAME);
  await submitButton.click();

  await passwordInputField.waitFor({ state: 'visible', timeout: settings.PAGE_LOAD_TIMEOUT });
  await passwordInputField.fill(settings.AUTH_PASSWORD);
  await submitButton.click();
  // Azure AD's "Stay signed in?" prompt requires a second submit.
  await submitButton.click();

  await searchForCase.waitFor({ state: 'visible', timeout: settings.PAGE_LOAD_TIMEOUT });

  await page.context().storageState({ path: STORAGE_STATE_PATH });
  await browser.close();
};

module.exports.STORAGE_STATE_PATH = STORAGE_STATE_PATH;
