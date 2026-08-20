const { test, expect } = require('@playwright/test');
const { epic, feature, story } = require('allure-js-commons');
const { settings } = require('../config/settings');
const { SupDashboardPage } = require('../pages/sup_dashboard_page');
const { LoginPage } = require('../pages/login_page');

// playwright.config.js sets a global storageState ('.auth/state.json') populated by
// global-setup.js, so every test here already starts authenticated — no per-test login.
test.describe('ARW-13: Tasks Worked Widget – Verify Martin Legend Tooltips', () => {
  test.beforeEach(async () => {
    await epic('ARW-13: Tasks Worked Widget – Verify Martin Legend Tooltips');
    await feature('sup_dashboard');
  });

  test('pos: display exactly 3 martin legend items when data available', async ({ page }) => {
    await story('AC1: The Tasks Worked widget should display exactly 3 Martin legend items when data is available');
    // Jira: ARW-13
    // AC: The Tasks Worked widget should display exactly 3 Martin legend items when data is available.
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Navigate to the Dashboard and wait for it to load', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
    });

    await test.step('Verify the Tasks Worked widget has data', async () => {
      expect(
        await dashboardPage.tasksWorkedNoData.isVisible().catch(() => false),
        'Tasks Worked widget should have data for this scenario'
      ).toBeFalsy();
    });

    await test.step('Verify exactly 3 Martin legend items are displayed', async () => {
      await dashboardPage.allTaskWorkedMartins.waitFor({ state: 'visible', timeout: settings.PAGE_LOAD_TIMEOUT });
      await dashboardPage.taskWorkedMartins.first().scrollIntoViewIfNeeded();
      expect(await dashboardPage.taskWorkedMartins.count()).toBe(3);
    });
  });

  test('err: no martin legend items shown when tasks worked widget has no data', async ({ page }) => {
    await story('AC1: No Martin legend items are shown when the Tasks Worked widget has no data');
    // Jira: ARW-13
    // AC: The Tasks Worked widget should display Martin legend items only when data is available.
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Navigate to the Dashboard and wait for it to load', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
    });

    await test.step('Verify behavior for the current Tasks Worked widget data state', async () => {
      const hasNoData = await dashboardPage.tasksWorkedNoData.isVisible().catch(() => false);
      test.skip(!hasNoData, 'Tasks Worked widget currently has data — "No Data" state is not reproducible in this run');

      expect(
        await dashboardPage.taskWorkedMartins.count(),
        'No Martin legend items should be present when the widget shows "No Data"'
      ).toBe(0);
    });
  });

  test('pos: verify tooltip text for first martin legend item within 2 days', async ({ page }) => {
    await story('AC2: Hovering over the first Martin legend item shows the "within 2 days" tooltip');
    // Jira: ARW-13
    // AC: Hovering over each Martin legend item should display a tooltip with the corresponding text — "Balance status updated within 2 days of due date".
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Navigate to the Dashboard and wait for it to load', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
    });

    await test.step('Hover over the first Martin legend item and verify its tooltip text', async () => {
      await dashboardPage.allTaskWorkedMartins.waitFor({ state: 'visible', timeout: settings.PAGE_LOAD_TIMEOUT });
      const martin = dashboardPage.taskWorkedMartins.nth(0);
      await martin.scrollIntoViewIfNeeded();
      await martin.hover();

      await expect(dashboardPage.widgetTooltip).toBeVisible({ timeout: settings.SHORT_TIMEOUT });
      expect((await dashboardPage.widgetTooltip.innerText()).trim())
        .toBe('Balance status updated within 2 days of due date');

      await page.mouse.move(0, 0);
    });
  });

  test('pos: verify tooltip text for second martin legend item within 3 to 7 days', async ({ page }) => {
    await story('AC2: Hovering over the second Martin legend item shows the "within 3 - 7 days" tooltip');
    // Jira: ARW-13
    // AC: Hovering over each Martin legend item should display a tooltip with the corresponding text — "Balance status updated within 3 - 7 days of due date".
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Navigate to the Dashboard and wait for it to load', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
    });

    await test.step('Hover over the second Martin legend item and verify its tooltip text', async () => {
      await dashboardPage.allTaskWorkedMartins.waitFor({ state: 'visible', timeout: settings.PAGE_LOAD_TIMEOUT });
      const martin = dashboardPage.taskWorkedMartins.nth(1);
      await martin.scrollIntoViewIfNeeded();
      await martin.hover();

      await expect(dashboardPage.widgetTooltip).toBeVisible({ timeout: settings.SHORT_TIMEOUT });
      expect((await dashboardPage.widgetTooltip.innerText()).trim())
        .toBe('Balance status updated within 3 - 7 days of due date');

      await page.mouse.move(0, 0);
    });
  });

  test('pos: verify tooltip text for third martin legend item over 8 days', async ({ page }) => {
    await story('AC2: Hovering over the third Martin legend item shows the "> 8 days" tooltip');
    // Jira: ARW-13
    // AC: Hovering over each Martin legend item should display a tooltip with the corresponding text — "Balance status updated > 8 days of due date".
    // NOTE: pages/sup_dashboard_page.js's verifyTaskWorkedMartinTooltips() currently expects "> 7 days" —
    // this test asserts the AC's literal wording ("> 8 days") so any mismatch surfaces as a real failure.
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Navigate to the Dashboard and wait for it to load', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
    });

    await test.step('Hover over the third Martin legend item and verify its tooltip text', async () => {
      await dashboardPage.allTaskWorkedMartins.waitFor({ state: 'visible', timeout: settings.PAGE_LOAD_TIMEOUT });
      const martin = dashboardPage.taskWorkedMartins.nth(2);
      await martin.scrollIntoViewIfNeeded();
      await martin.hover();

      await expect(dashboardPage.widgetTooltip).toBeVisible({ timeout: settings.SHORT_TIMEOUT });
      expect((await dashboardPage.widgetTooltip.innerText()).trim())
        .toBe('Balance status updated > 8 days of due date');

      await page.mouse.move(0, 0);
    });
  });

  test('err: no tooltip shown when no martin legend item is hovered', async ({ page }) => {
    await story('AC2: No Martin legend tooltip is shown when no legend item is hovered');
    // Jira: ARW-13
    // AC: Tooltips should only appear on hover of a Martin legend item, not otherwise.
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Navigate to the Dashboard and wait for it to load', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
    });

    await test.step('Move the mouse away from all Martin legend items', async () => {
      await dashboardPage.allTaskWorkedMartins.waitFor({ state: 'visible', timeout: settings.PAGE_LOAD_TIMEOUT });
      await page.mouse.move(0, 0);
    });

    await test.step('Verify no Martin legend tooltip is visible', async () => {
      expect(
        await dashboardPage.widgetTooltip.isVisible().catch(() => false),
        'No tooltip should be visible when no Martin legend item is hovered'
      ).toBeFalsy();
    });
  });

  test.describe('unauthenticated', () => {
    // Overrides the global storageState so this test starts with no session,
    // unlike every other test in this file which reuses the authenticated state.
    test.use({ storageState: { cookies: [], origins: [] } });

    test('perm: unauthenticated user cannot view tasks worked widget', async ({ page }) => {
      await story('AC2 (RBAC): The Tasks Worked widget and its Martin legend tooltips require an authenticated Dashboard session');
      // Jira: ARW-13
      // AC (RBAC): The Tasks Worked widget's Martin legend tooltips must not be accessible without authentication.
      const dashboardPage = new SupDashboardPage(page);
      const loginPage = new LoginPage(page);

      await test.step('Attempt to navigate directly to the Dashboard page without logging in', async () => {
        await dashboardPage.navigateToDashboard();
      });

      await test.step('Verify the user is redirected to the login page', async () => {
        expect(
          await loginPage.microsoftSignInButton.isVisible(),
          'User was not redirected to the login page when unauthenticated'
        ).toBeTruthy();
      });

      await test.step('Verify the Tasks Worked widget Martin legend items are not accessible', async () => {
        expect(
          await dashboardPage.taskWorkedMartins.count(),
          'Tasks Worked widget Martin legend items should not be visible without authentication'
        ).toBe(0);
      });
    });
  });
});
