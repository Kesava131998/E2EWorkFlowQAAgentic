const { test, expect } = require('@playwright/test');
const { epic, feature, story } = require('allure-js-commons');
const { SupDashboardPage } = require('../pages/sup_dashboard_page');

// playwright.config.js sets a global storageState ('.auth/state.json') populated by
// global-setup.js, so every test here already starts authenticated — no per-test login.
test.describe('ARW-33: Highest Balances Widget – Display Applied Payer Category Filter', () => {
  const PAYER_CATEGORY = 'Medicaid';
  const EXPECTED_TOOLTIP = 'Payer Category Filters (Medicaid)';

  test.beforeEach(async () => {
    await epic('ARW-33: Highest Balances Widget – Display Applied Payer Category Filter');
    await feature('sup_dashboard');
  });

  test('pos: display filter indicator when payer category filter applied', async ({ page }) => {
    await story('AC1: The Highest Balances widget displays the filter icon/indicator when the Medicaid Payer Category filter is applied');
    // Jira: ARW-33
    // AC1: When the Medicaid Payer Category filter is applied, the Highest Balances widget should display the filter icon/indicator
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Step 1: Navigate to the Dashboard and wait for it to load', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
    });

    await test.step('Pre-condition: Reset any previously applied Payer Category filter', async () => {
      await dashboardPage.resetPayerCategoryFilter();
    });

    await test.step('Step 2: Verify the Payer Category filter control is visible', async () => {
      expect(
        await dashboardPage.isPayerCategoryFilterVisible(),
        'Payer Category filter control should be visible in the Dashboard header'
      ).toBeTruthy();
    });

    await test.step(`Step 3: Apply the Payer Category filter with ${PAYER_CATEGORY} selected`, async () => {
      await dashboardPage.openPayerCategoryFilter();
      await dashboardPage.searchPayerCategory(PAYER_CATEGORY);
      await dashboardPage.selectPayerCategory(PAYER_CATEGORY);
      await dashboardPage.clickApplyPayerCategoryFilter();
    });

    await test.step('Step 4: Verify the Highest Balances widget is visible', async () => {
      expect(
        await dashboardPage.isHighestBalancesWidgetVisible(),
        'Highest Balances widget should be visible on the Dashboard'
      ).toBeTruthy();
    });

    await test.step('Step 5: Verify the Highest Balances widget filter indicator is displayed', async () => {
      expect(
        await dashboardPage.isHighestBalancesFilterIconVisible(),
        `Highest Balances widget filter indicator should be displayed when the ${PAYER_CATEGORY} Payer Category filter is applied`
      ).toBeTruthy();
    });
  });

  test('err: no applied filter shown when no payer category applied', async ({ page }) => {
    await story('AC1: The Highest Balances widget filter indicator does not display an applied filter when no Payer Category filter is applied');
    // Jira: ARW-33
    // AC1: When no Payer Category filter is applied, the filter indicator should not display an applied filter
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Step 1: Navigate to the Dashboard and wait for it to load', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
    });

    await test.step('Pre-condition: Reset any previously applied Payer Category filter', async () => {
      await dashboardPage.resetPayerCategoryFilter();
    });

    await test.step('Step 2: Verify the Highest Balances widget is visible', async () => {
      expect(
        await dashboardPage.isHighestBalancesWidgetVisible(),
        'Highest Balances widget should be visible on the Dashboard'
      ).toBeTruthy();
    });

    await test.step('Step 3: Verify the Highest Balances widget shows no applied filter indicator', async () => {
      expect(
        await dashboardPage.isHighestBalancesFilterIconVisible(),
        'Highest Balances widget filter indicator should not display an applied filter when no Payer Category filter is applied'
      ).toBeFalsy();
    });
  });

  test('pos: tooltip shows applied payer category on hover', async ({ page }) => {
    await story('AC2: The Highest Balances widget tooltip shows "Payer Category Filters (Medicaid)" on hover of the filter indicator');
    // Jira: ARW-33
    // AC2: When the user hovers over the filter indicator, a tooltip should be displayed showing "Payer Category Filters (Medicaid)"
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Step 1: Navigate to the Dashboard and wait for it to load', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
    });

    await test.step('Pre-condition: Reset any previously applied Payer Category filter', async () => {
      await dashboardPage.resetPayerCategoryFilter();
    });

    await test.step(`Step 2: Apply the Payer Category filter with ${PAYER_CATEGORY} selected`, async () => {
      await dashboardPage.openPayerCategoryFilter();
      await dashboardPage.searchPayerCategory(PAYER_CATEGORY);
      await dashboardPage.selectPayerCategory(PAYER_CATEGORY);
      await dashboardPage.clickApplyPayerCategoryFilter();
    });

    await test.step('Step 3: Verify the Highest Balances widget filter indicator is displayed', async () => {
      expect(
        await dashboardPage.isHighestBalancesFilterIconVisible(),
        'Highest Balances widget filter indicator should be displayed before hovering'
      ).toBeTruthy();
    });

    await test.step(`Step 4: Hover over the filter indicator and verify the tooltip reads "${EXPECTED_TOOLTIP}"`, async () => {
      await dashboardPage.hoverHighestBalancesFilterIcon();
      expect(
        await dashboardPage.isHighestBalancesFilterTooltipVisible(),
        'A tooltip should be displayed when hovering over the Highest Balances widget filter indicator'
      ).toBeTruthy();
      expect(
        await dashboardPage.getHighestBalancesFilterTooltipText(),
        `Highest Balances widget tooltip should show "${EXPECTED_TOOLTIP}"`
      ).toBe(EXPECTED_TOOLTIP);
    });
  });

  test('pos: tooltip reflects multiple selected payer categories', async ({ page }) => {
    await story('AC2: The Highest Balances widget tooltip reflects all applied Payer Categories when multiple are selected');
    // Jira: ARW-33
    // AC2: The tooltip should show the applied Payer Category filter(s)
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Step 1: Navigate to the Dashboard and wait for it to load', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
    });

    await test.step('Pre-condition: Reset any previously applied Payer Category filter', async () => {
      await dashboardPage.resetPayerCategoryFilter();
    });

    let selectedCategories;
    await test.step('Step 2: Select two Payer Category options and apply the filter', async () => {
      selectedCategories = await dashboardPage.selectRandomOptionsFromPayerCategoriesDropdown(2);
      expect(selectedCategories, 'Two Payer Category options should have been selected').toHaveLength(2);
    });

    await test.step('Step 3: Hover over the Highest Balances widget filter indicator and verify the tooltip', async () => {
      await dashboardPage.hoverHighestBalancesFilterIcon();
      expect(
        await dashboardPage.isHighestBalancesFilterTooltipVisible(),
        'A tooltip should be displayed when hovering over the Highest Balances widget filter indicator'
      ).toBeTruthy();

      const tooltipText = await dashboardPage.getHighestBalancesFilterTooltipText();
      for (const categoryName of selectedCategories) {
        expect(
          tooltipText,
          `Tooltip should contain the selected Payer Category "${categoryName}"`
        ).toContain(categoryName);
      }
    });
  });

  test('pos: filter indicator and tooltip update when payer category changed', async ({ page }) => {
    await story('AC3: The Highest Balances widget filter indicator and tooltip reflect the current applied filter after the Payer Category filter is changed');
    // Jira: ARW-33
    // AC3: When the user changes the Payer Category filter, the Highest Balances widget's filter indicator and tooltip should reflect the current applied filter
    const dashboardPage = new SupDashboardPage(page);
    let changedCategory;

    await test.step('Step 1: Navigate to the Dashboard and wait for it to load', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
    });

    await test.step('Pre-condition: Reset any previously applied Payer Category filter', async () => {
      await dashboardPage.resetPayerCategoryFilter();
    });

    await test.step(`Step 2: Apply the Payer Category filter with ${PAYER_CATEGORY} selected`, async () => {
      await dashboardPage.openPayerCategoryFilter();
      await dashboardPage.searchPayerCategory(PAYER_CATEGORY);
      await dashboardPage.selectPayerCategory(PAYER_CATEGORY);
      await dashboardPage.clickApplyPayerCategoryFilter();
    });

    await test.step(`Step 3: Verify the tooltip reflects the applied ${PAYER_CATEGORY} filter`, async () => {
      await dashboardPage.hoverHighestBalancesFilterIcon();
      expect(
        await dashboardPage.getHighestBalancesFilterTooltipText(),
        `Tooltip should reflect the ${PAYER_CATEGORY} Payer Category filter before the change`
      ).toContain(PAYER_CATEGORY);
    });

    await test.step(`Step 4: Change the Payer Category filter away from ${PAYER_CATEGORY}`, async () => {
      await dashboardPage.openPayerCategoryFilter();
      await dashboardPage.searchPayerCategory(PAYER_CATEGORY);
      await dashboardPage.selectPayerCategory(PAYER_CATEGORY);
      await dashboardPage.clearPayerCategorySearch();
      changedCategory = await dashboardPage.selectPayerCategoryOtherThan(PAYER_CATEGORY);
      await dashboardPage.clickApplyPayerCategoryFilter();
    });

    await test.step('Step 5: Verify the Highest Balances widget filter indicator is still displayed', async () => {
      expect(
        await dashboardPage.isHighestBalancesFilterIconVisible(),
        'Highest Balances widget filter indicator should remain displayed after the Payer Category filter is changed'
      ).toBeTruthy();
    });

    await test.step('Step 6: Verify the tooltip reflects the newly applied Payer Category', async () => {
      await dashboardPage.hoverHighestBalancesFilterIcon();
      const tooltipText = await dashboardPage.getHighestBalancesFilterTooltipText();

      expect(
        tooltipText,
        `Tooltip should reflect the newly applied "${changedCategory}" Payer Category filter`
      ).toContain(changedCategory);
      expect(
        tooltipText,
        `Tooltip should no longer reference the removed "${PAYER_CATEGORY}" Payer Category filter`
      ).not.toContain(PAYER_CATEGORY);
    });
  });

  test('pos: filter indicator and tooltip cleared when payer category removed', async ({ page }) => {
    await story('AC3: The Highest Balances widget filter indicator and tooltip reflect no applied filter after the Payer Category filter is removed');
    // Jira: ARW-33
    // AC3: When the user removes the Payer Category filter, the Highest Balances widget's filter indicator and tooltip should reflect the current applied filter
    const dashboardPage = new SupDashboardPage(page);

    await test.step('Step 1: Navigate to the Dashboard and wait for it to load', async () => {
      await dashboardPage.navigateToDashboard();
      await dashboardPage.waitForDashboardLoad();
    });

    await test.step('Pre-condition: Reset any previously applied Payer Category filter', async () => {
      await dashboardPage.resetPayerCategoryFilter();
    });

    await test.step(`Step 2: Apply the Payer Category filter with ${PAYER_CATEGORY} selected`, async () => {
      await dashboardPage.openPayerCategoryFilter();
      await dashboardPage.searchPayerCategory(PAYER_CATEGORY);
      await dashboardPage.selectPayerCategory(PAYER_CATEGORY);
      await dashboardPage.clickApplyPayerCategoryFilter();
    });

    await test.step('Step 3: Verify the Highest Balances widget filter indicator is displayed', async () => {
      expect(
        await dashboardPage.isHighestBalancesFilterIconVisible(),
        `Highest Balances widget filter indicator should be displayed while the ${PAYER_CATEGORY} filter is applied`
      ).toBeTruthy();
    });

    await test.step(`Step 4: Remove the applied ${PAYER_CATEGORY} Payer Category filter`, async () => {
      await dashboardPage.resetPayerCategoryFilter();
    });

    await test.step('Step 5: Verify the Highest Balances widget filter indicator is no longer displayed', async () => {
      expect(
        await dashboardPage.isHighestBalancesFilterIconVisible(),
        'Highest Balances widget filter indicator should not be displayed after the Payer Category filter is removed'
      ).toBeFalsy();
    });

    await test.step('Step 6: Verify no filter tooltip is displayed on the Highest Balances widget', async () => {
      await dashboardPage.highestBalancesWidget.hover();
      expect(
        await dashboardPage.isHighestBalancesFilterTooltipVisible(),
        'No Payer Category filter tooltip should be displayed once the filter is removed'
      ).toBeFalsy();
    });
  });
});
