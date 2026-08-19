const { test, expect } = require('@playwright/test');
const { epic, feature, story } = require('allure-js-commons');
const { SupDashboardPage } = require('../pages/sup_dashboard_page');
const { LoginPage } = require('../pages/login_page');

// playwright.config.js sets a global storageState ('.auth/state.json') populated by
// global-setup.js, so every test here already starts authenticated — no per-test login.
test.describe('ARW-5: AR Status Widget – Display Applied Payer Category Filter', () => {
  test.beforeEach(async () => {
    await epic('ARW-5: AR Status Widget – Display Applied Payer Category Filter');
    await feature('sup_dashboard');
  });

  test('pos: display filter icon when payer category applied', async ({ page }) => {
    await story('AC1: AR Status widget displays the filter icon/indicator when a Payer Category filter such as HMO is applied');
    // Jira: ARW-5
    // AC: When a Payer Category filter such as HMO is applied, the AR Status widget should display the filter icon/indicator
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Navigate to the Dashboard and wait for it to load', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
    });

    await test.step('Apply the Payer Category filter with HMO selected', async () => {
      await dashboardPage.openPayerCategoryFilter();
      await dashboardPage.searchPayerCategory('HMO');
      await dashboardPage.selectPayerCategory('HMO');
      await dashboardPage.clickApplyPayerCategoryFilter();
    });

    await test.step('Verify the AR Status widget filter icon is visible', async () => {
      expect(
        await dashboardPage.isArStatusFilterIconVisible(),
        'AR Status widget filter icon should be visible when a Payer Category filter is applied'
      ).toBeTruthy();
    });
  });

  test('err: hide filter icon when no payer category filter applied', async ({ page }) => {
    await story('AC1: AR Status widget does not display the filter icon when no Payer Category filter is applied');
    // Jira: ARW-5
    // AC: When no Payer Category filter is applied, the filter indicator should not display an applied filter
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Navigate to the Dashboard and wait for it to load', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
    });

    await test.step('Verify the AR Status widget filter icon is not visible', async () => {
      expect(
        await dashboardPage.isArStatusFilterIconVisible(),
        'AR Status widget filter icon should not be visible when no Payer Category filter is applied'
      ).toBeFalsy();
    });
  });

  test('pos: show tooltip on hover with applied payer category', async ({ page }) => {
    await story('AC2: Hovering over the AR Status widget filter indicator shows a tooltip with the applied Payer Category');
    // Jira: ARW-5
    // AC: When the user hovers over the filter indicator on the AR Status widget, a tooltip should be displayed
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Navigate to the Dashboard and apply the Payer Category filter with HMO selected', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
      await dashboardPage.openPayerCategoryFilter();
      await dashboardPage.searchPayerCategory('HMO');
      await dashboardPage.selectPayerCategory('HMO');
      await dashboardPage.clickApplyPayerCategoryFilter();
    });

    await test.step('Hover over the AR Status widget filter icon and verify the tooltip is visible', async () => {
      await dashboardPage.hoverArStatusFilterIcon();
      expect(
        await dashboardPage.tooltip.isVisible(),
        'AR Status widget filter tooltip should be visible on hover'
      ).toBeTruthy();
    });
  });

  test('err: no tooltip shown when no filter indicator present', async ({ page }) => {
    await story('AC2: No tooltip is shown when hovering over the AR Status widget if no filter indicator is present');
    // Jira: ARW-5
    // AC: The tooltip should only show the applied Payer Category when a filter indicator is present
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Navigate to the Dashboard and wait for it to load', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
    });

    await test.step('Verify the AR Status widget filter icon is not present', async () => {
      expect(
        await dashboardPage.isArStatusFilterIconVisible(),
        'AR Status widget filter icon should be absent when no Payer Category filter is applied'
      ).toBeFalsy();
    });

    await test.step('Hover over the AR Status widget header area and verify no filter tooltip appears', async () => {
      await dashboardPage.arStatusWidget.hover();
      expect(
        await dashboardPage.tooltip.isVisible(),
        'No Payer Category filter tooltip should appear when there is no filter indicator'
      ).toBeFalsy();
    });
  });

  test('pos: update filter indicator and tooltip when payer category changed', async ({ page }) => {
    await story('AC3: AR Status widget filter indicator and tooltip update when the applied Payer Category filter is changed');
    // Jira: ARW-5
    // AC: When the user changes the Payer Category filter, the AR Status widget's filter indicator and tooltip should reflect the current applied filter
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Navigate to the Dashboard and apply the Payer Category filter with HMO selected', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
      await dashboardPage.openPayerCategoryFilter();
      await dashboardPage.searchPayerCategory('HMO');
      await dashboardPage.selectPayerCategory('HMO');
      await dashboardPage.clickApplyPayerCategoryFilter();
    });

    await test.step('Verify the tooltip shows the HMO filter applied', async () => {
      await dashboardPage.hoverArStatusFilterIcon();
      expect(
        await dashboardPage.getArStatusFilterTooltipText(),
        'Tooltip should show the HMO Payer Category filter before the change'
      ).toContain('HMO');
    });

    await test.step('Change the Payer Category filter from HMO to PPO', async () => {
      await dashboardPage.openPayerCategoryFilter();
      await dashboardPage.searchPayerCategory('HMO');
      await dashboardPage.selectPayerCategory('HMO');
      await dashboardPage.clearPayerCategorySearch();
      await dashboardPage.searchPayerCategory('PPO');
      await dashboardPage.selectPayerCategory('PPO');
      await dashboardPage.clickApplyPayerCategoryFilter();
    });

    await test.step('Verify the tooltip now shows the PPO filter applied', async () => {
      await dashboardPage.hoverArStatusFilterIcon();
      expect(
        await dashboardPage.getArStatusFilterTooltipText(),
        'Tooltip should update to show the PPO Payer Category filter after the change'
      ).toContain('PPO');
    });
  });

  test('pos: remove filter indicator when payer category filter cleared', async ({ page }) => {
    await story('AC3: AR Status widget filter indicator is removed when the applied Payer Category filter is removed');
    // Jira: ARW-5
    // AC: When the user removes the Payer Category filter, the AR Status widget's filter indicator should reflect the current applied filter
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Navigate to the Dashboard and apply the Payer Category filter with HMO selected', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
      await dashboardPage.openPayerCategoryFilter();
      await dashboardPage.searchPayerCategory('HMO');
      await dashboardPage.selectPayerCategory('HMO');
      await dashboardPage.clickApplyPayerCategoryFilter();
    });

    await test.step('Verify the AR Status widget filter icon is visible', async () => {
      expect(
        await dashboardPage.isArStatusFilterIconVisible(),
        'AR Status widget filter icon should be visible while HMO filter is applied'
      ).toBeTruthy();
    });

    await test.step('Remove the applied Payer Category filter', async () => {
      await dashboardPage.openPayerCategoryFilter();
      await dashboardPage.searchPayerCategory('HMO');
      await dashboardPage.selectPayerCategory('HMO');
      await dashboardPage.clickApplyPayerCategoryFilter();
    });

    await test.step('Verify the AR Status widget filter icon is no longer visible', async () => {
      expect(
        await dashboardPage.isArStatusFilterIconVisible(),
        'AR Status widget filter icon should not be visible after the Payer Category filter is removed'
      ).toBeFalsy();
    });
  });

  test('pos: tooltip lists multiple applied payer categories', async ({ page }) => {
    await story('AC3: AR Status widget tooltip lists all applied Payer Categories when multiple categories are selected');
    // Jira: ARW-5
    // AC: The AR Status widget's filter indicator and tooltip should reflect the current applied filter
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Navigate to the Dashboard and apply the Payer Category filter with HMO and PPO selected', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
      await dashboardPage.openPayerCategoryFilter();
      await dashboardPage.searchPayerCategory('HMO');
      await dashboardPage.selectPayerCategory('HMO');
      await dashboardPage.clearPayerCategorySearch();
      await dashboardPage.searchPayerCategory('PPO');
      await dashboardPage.selectPayerCategory('PPO');
      await dashboardPage.clickApplyPayerCategoryFilter();
    });

    await test.step('Hover over the AR Status widget filter icon and verify the tooltip lists both categories', async () => {
      await dashboardPage.hoverArStatusFilterIcon();
      const tooltipText = await dashboardPage.getArStatusFilterTooltipText();
      expect(tooltipText, 'Tooltip should list the HMO Payer Category').toContain('HMO');
      expect(tooltipText, 'Tooltip should list the PPO Payer Category').toContain('PPO');
    });
  });

  test('pos: tooltip text matches exact payer category filter format', async ({ page }) => {
    await story('AC2: AR Status widget tooltip text exactly matches the acceptance-criteria format for the applied Payer Category');
    // Jira: ARW-5
    // AC: The tooltip should show the applied Payer Category, for example "Payer Category Filters (HMO)"
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Navigate to the Dashboard and apply the Payer Category filter with HMO selected', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
      await dashboardPage.openPayerCategoryFilter();
      await dashboardPage.searchPayerCategory('HMO');
      await dashboardPage.selectPayerCategory('HMO');
      await dashboardPage.clickApplyPayerCategoryFilter();
    });

    await test.step('Hover over the AR Status widget filter icon and verify the exact tooltip text', async () => {
      await dashboardPage.hoverArStatusFilterIcon();
      expect(
        await dashboardPage.getArStatusFilterTooltipText(),
        'Tooltip text should exactly match the AC-specified format'
      ).toBe('Payer Category Filters (HMO)');
    });
  });

  test.describe('unauthenticated', () => {
    // Overrides the global storageState so this test starts with no session,
    // unlike every other test in this file which reuses the authenticated state.
    test.use({ storageState: { cookies: [], origins: [] } });

    test('perm: ar status widget filter indicator requires authentication', async ({ page }) => {
      await story('AC1: AR Status widget filter indicator is accessible only to an authenticated Dashboard user');
      // Jira: ARW-5
      // AC (RBAC): The AR Status widget and its filter indicator require an authenticated Dashboard session
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

      await test.step('Verify the AR Status widget filter indicator is not accessible', async () => {
        expect(
          await dashboardPage.isArStatusFilterIconVisible(),
          'AR Status widget filter indicator should not be visible without authentication'
        ).toBeFalsy();
      });
    });
  });
});
