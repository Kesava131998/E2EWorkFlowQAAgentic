const { test, expect } = require('@playwright/test');
const { epic, feature, story } = require('allure-js-commons');
const { SupDashboardPage } = require('../pages/sup_dashboard_page');
const { LoginPage } = require('../pages/login_page');

// playwright.config.js sets a global storageState ('.auth/state.json') populated by
// global-setup.js, so every test here already starts authenticated — no per-test login.
test.describe('ARW-2: Dashboard – Add Payer Category Filter Functionality', () => {
  test.beforeEach(async () => {
    await epic('ARW-2: Dashboard – Add Payer Category Filter Functionality');
    await feature('sup_dashboard');
  });

  test('pos: open payer category filter dropdown', async ({ page }) => {
    await story('AC1: User can click the Payer Category filter on the Dashboard to open the dropdown');
    // Jira: ARW-2
    // AC: User can click the Payer Category filter on the Dashboard to open the dropdown
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Navigate to the Dashboard', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
    });

    await test.step('Verify the Payer Category filter control is visible', async () => {
      expect(
        await dashboardPage.isPayerCategoryFilterVisible(),
        'Payer Category filter control is not visible'
      ).toBeTruthy();
    });

    await test.step('Click the Payer Category filter and verify the dropdown opens', async () => {
      await dashboardPage.openPayerCategoryFilter();
      expect(
        await dashboardPage.isPayerCategoryDropdownOpen(),
        'Payer Category dropdown panel did not open'
      ).toBeTruthy();
    });
  });

  test('pos: close payer category dropdown by clicking outside', async ({ page }) => {
    await story('AC1: Clicking outside the open Payer Category dropdown closes it without applying changes');
    // Jira: ARW-2
    // AC: User can click the Payer Category filter on the Dashboard to open the dropdown
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Navigate to the Dashboard and open the Payer Category dropdown', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
      await dashboardPage.openPayerCategoryFilter();
    });

    await test.step('Verify the dropdown panel is visible', async () => {
      expect(
        await dashboardPage.isPayerCategoryDropdownOpen(),
        'Payer Category dropdown panel is not visible'
      ).toBeTruthy();
    });

    await test.step('Click outside the dropdown and verify it closes', async () => {
      await dashboardPage.closePayerCategoryDropdownByClickingOutside();
      expect(
        await dashboardPage.isPayerCategoryDropdownOpen(),
        'Payer Category dropdown panel is still visible after clicking outside'
      ).toBeFalsy();
    });
  });

  test('pos: search HMO in payer category filter shows matching result', async ({ page }) => {
    await story('AC2: User can search for HMO in the Payer Category search field and view the matching result');
    // Jira: ARW-2
    // AC: User can search for HMO in the Payer Category search field and view the matching HMO result
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Navigate to the Dashboard and open the Payer Category dropdown', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
      await dashboardPage.openPayerCategoryFilter();
    });

    await test.step('Verify the search box field is visible', async () => {
      expect(
        await dashboardPage.isPayerCategorySearchFieldVisible(),
        'Payer Category search box field is not visible'
      ).toBeTruthy();
    });

    await test.step('Search for "HMO" and verify the matching option is visible', async () => {
      await dashboardPage.searchPayerCategory('HMO');
      expect(
        await dashboardPage.isPayerCategoryOptionVisible('HMO'),
        'HMO option is not visible in the filtered Payer Category list'
      ).toBeTruthy();
    });
  });

  test('err: searching non-existent payer category shows no results', async ({ page }) => {
    await story('AC2: Searching for a non-existent Payer Category shows no matching results');
    // Jira: ARW-2
    // AC: User can search for HMO in the Payer Category search field and view the matching HMO result
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Navigate to the Dashboard and open the Payer Category dropdown', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
      await dashboardPage.openPayerCategoryFilter();
    });

    await test.step('Search for a non-existent Payer Category and verify no results are shown', async () => {
      await dashboardPage.searchPayerCategory('ZZZNONEXISTENT');
      expect(
        await dashboardPage.getPayerCategoryOptionsCount(),
        'Payer Category options list should be empty for a non-existent search term'
      ).toBe(0);
    });
  });

  test('pos: clearing search restores full payer category list', async ({ page }) => {
    await story('AC2: Clearing the search field after searching restores the full Payer Category list');
    // Jira: ARW-2
    // AC: User can search for HMO in the Payer Category search field and view the matching HMO result
    const dashboardPage = new SupDashboardPage(page);
    let optionsCountBefore;

    await test.step('Navigate to the Dashboard and open the Payer Category dropdown', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
      await dashboardPage.openPayerCategoryFilter();
      optionsCountBefore = await dashboardPage.getPayerCategoryOptionsCount();
    });

    await test.step('Search for "HMO" and verify only the matching option remains', async () => {
      await dashboardPage.searchPayerCategory('HMO');
      expect(
        await dashboardPage.getPayerCategoryOptionsCount(),
        'Payer Category list should be narrowed down to the HMO search term'
      ).toBe(1);
    });

    await test.step('Clear the search field and verify the full list is restored', async () => {
      await dashboardPage.clearPayerCategorySearch();
      expect(
        await dashboardPage.getPayerCategoryOptionsCount(),
        'Payer Category list was not restored after clearing the search field'
      ).toBe(optionsCountBefore);
    });
  });

  test('pos: select HMO and apply filters dashboard data', async ({ page }) => {
    await story('AC3: User can select HMO and click Apply; Dashboard data is filtered based on the selected HMO payer category');
    // Jira: ARW-2
    // AC: User can select HMO and click Apply; the Dashboard data should be filtered based on the selected HMO payer category
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Navigate to the Dashboard and open the Payer Category dropdown', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
      await dashboardPage.openPayerCategoryFilter();
    });

    await test.step('Search for and select the HMO checkbox', async () => {
      await dashboardPage.searchPayerCategory('HMO');
      await dashboardPage.selectPayerCategory('HMO');
      expect(
        await dashboardPage.isPayerCategorySelected('HMO'),
        'HMO checkbox did not become checked'
      ).toBeTruthy();
    });

    await test.step('Verify Apply is enabled and click it', async () => {
      expect(await dashboardPage.isApplyButtonEnabled(), 'Apply button is not enabled').toBeTruthy();
      await dashboardPage.clickApplyPayerCategoryFilter();
    });

    await test.step('Verify the Dashboard reloads with the filter applied', async () => {
      await dashboardPage.waitForDashboardLoad();
      expect(
        await dashboardPage.getAppliedPayerCategoryFilterValue(),
        'Dashboard filter value does not reflect the applied HMO category'
      ).toContain('HMO');
    });
  });

  test('err: apply with no payer category selected does not change filter', async ({ page }) => {
    await story('AC3: Clicking Apply with no Payer Category selected does not change the Dashboard filter');
    // Jira: ARW-2
    // AC: User can select HMO and click Apply; the Dashboard data should be filtered based on the selected HMO payer category
    const dashboardPage = new SupDashboardPage(page);
    let filterValueBefore;

    await test.step('Navigate to the Dashboard and open the Payer Category dropdown', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
      filterValueBefore = await dashboardPage.getAppliedPayerCategoryFilterValue();
      await dashboardPage.openPayerCategoryFilter();
    });

    await test.step('Verify no Payer Category is selected, then attempt to apply', async () => {
      expect(
        await dashboardPage.isPayerCategorySelected('HMO'),
        'No Payer Category should be selected by default'
      ).toBeFalsy();

      if (await dashboardPage.isApplyButtonEnabled()) {
        await dashboardPage.clickApplyPayerCategoryFilter();
      }
    });

    await test.step('Verify the Dashboard filter is unchanged', async () => {
      expect(
        await dashboardPage.getAppliedPayerCategoryFilterValue(),
        'Dashboard filter value changed despite no Payer Category being selected'
      ).toBe(filterValueBefore);
    });
  });

  test('pos: select multiple payer categories and apply', async ({ page }) => {
    await story('AC3: Selecting multiple Payer Categories and applying filters the Dashboard by all selected categories');
    // Jira: ARW-2
    // AC: User can select HMO and click Apply; the Dashboard data should be filtered based on the selected HMO payer category
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Navigate to the Dashboard and open the Payer Category dropdown', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
      await dashboardPage.openPayerCategoryFilter();
    });

    await test.step('Select the HMO and PPO checkboxes', async () => {
      await dashboardPage.selectPayerCategory('HMO');
      await dashboardPage.selectPayerCategory('PPO');
      expect(await dashboardPage.isPayerCategorySelected('HMO'), 'HMO checkbox was not checked').toBeTruthy();
      expect(await dashboardPage.isPayerCategorySelected('PPO'), 'PPO checkbox was not checked').toBeTruthy();
    });

    await test.step('Click Apply and verify the Dashboard reloads', async () => {
      await dashboardPage.clickApplyPayerCategoryFilter();
      await dashboardPage.waitForDashboardLoad();
      const appliedValue = await dashboardPage.getAppliedPayerCategoryFilterValue();
      expect(appliedValue, 'Applied filter value missing HMO').toContain('HMO');
      expect(appliedValue, 'Applied filter value missing PPO').toContain('PPO');
    });
  });

  test('pos: HMO displayed as selected value after applying filter', async ({ page }) => {
    await story('AC4: After applying the filter, HMO should be displayed as the selected value in the Payer Category filter');
    // Jira: ARW-2
    // AC: After applying the filter, HMO should be displayed as the selected value in the Payer Category filter
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Navigate to the Dashboard and apply the HMO Payer Category filter', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
      await dashboardPage.openPayerCategoryFilter();
      await dashboardPage.searchPayerCategory('HMO');
      await dashboardPage.selectPayerCategory('HMO');
      await dashboardPage.clickApplyPayerCategoryFilter();
      await dashboardPage.waitForDashboardLoad();
    });

    await test.step('Verify the Payer Category filter control is visible', async () => {
      expect(
        await dashboardPage.isPayerCategoryFilterVisible(),
        'Payer Category filter control is not visible'
      ).toBeTruthy();
    });

    await test.step('Verify HMO is displayed as the applied filter value', async () => {
      expect(
        await dashboardPage.getAppliedPayerCategoryFilterValue(),
        'HMO is not displayed as the selected value on the Payer Category filter'
      ).toContain('HMO');
    });
  });

  test('pos: applied HMO filter persists after reopening dropdown', async ({ page }) => {
    await story('AC4: The applied HMO filter value persists after reopening the Payer Category dropdown');
    // Jira: ARW-2
    // AC: After applying the filter, HMO should be displayed as the selected value in the Payer Category filter
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Navigate to the Dashboard and apply the HMO Payer Category filter', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
      await dashboardPage.openPayerCategoryFilter();
      await dashboardPage.searchPayerCategory('HMO');
      await dashboardPage.selectPayerCategory('HMO');
      await dashboardPage.clickApplyPayerCategoryFilter();
      await dashboardPage.waitForDashboardLoad();
    });

    await test.step('Reopen the Payer Category dropdown', async () => {
      await dashboardPage.openPayerCategoryFilter();
    });

    await test.step('Verify the HMO checkbox is still shown as checked', async () => {
      expect(
        await dashboardPage.isPayerCategorySelected('HMO'),
        'HMO checkbox should remain checked after reopening the dropdown'
      ).toBeTruthy();
    });
  });

  test.describe('unauthenticated', () => {
    // Overrides the global storageState so this test starts with no session,
    // unlike every other test in this file which reuses the authenticated state.
    test.use({ storageState: { cookies: [], origins: [] } });

    test('perm: payer category filter inaccessible without authentication', async ({ page }) => {
      await story('AC1: Payer Category filter is accessible only to an authenticated Dashboard user');
      // Jira: ARW-2
      // AC (RBAC): Only an authenticated user can access the Dashboard's Payer Category filter
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

      await test.step('Verify the Payer Category filter is not accessible', async () => {
        expect(
          await dashboardPage.isPayerCategoryFilterVisible(),
          'Payer Category filter should not be visible without authentication'
        ).toBeFalsy();
      });
    });
  });
});
