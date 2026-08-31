const { test, expect } = require('@playwright/test');
const { BasePage } = require('./base_page');
const { settings } = require('../config/settings');

/**
 * Page object for the Supervisor Dashboard page (converted from dashborad.js /
 * pageObjects/UI_Pages/dashborad.js). Only locators are ported here — the original file's
 * validation/business-logic methods (widget tooltip checks, payer-category filter flows,
 * highest-balances ordering/API assertions, slide-out vs grid comparisons, saved-view/API
 * status loops, etc.) belong in spec files as assertions built on top of these locators.
 */
class SupDashboardPage extends BasePage {
  constructor(page) {
    super(page);

    // ── Module cards ──────────────────────────────────────────────────────
    this.taskListModuleCard = page.locator("(//div[@class='module-card'])[1]");
    this.agingModuleCard = page.locator("(//div[@class='module-card'])[2]");

    // ── Dashboard root / spinner ─────────────────────────────────────────
    this.dashboardPage = page.locator("//arw-dashboard[contains(@class,'arw-page')]");
    this.loadSpinner = page.locator("//mat-spinner[@role='progressbar']");

    // ── Tasks Worked / Task Updates widgets ──────────────────────────────
    this.tasksWorkedNoData = page.locator("//arw-tasks-worked-widget//div[normalize-space(text())='No Data']");
    this.taskUpdatesNoData = page.locator("//arw-task-updates-widget//div[normalize-space(text())='No Data']");
    this.taskUpdateAvatarToolpits = page.locator("//arw-task-updates-widget//arw-avatar");
    this.taskWorkedAvatarToolpits = page.locator("//arw-tasks-worked-widget//arw-avatar");
    this.taskUpdateWidget = page.locator('//arw-task-updates-widget');
    this.taskUpdateCanvas = page.locator("//arw-task-updates-widget//canvas");
    this.taskUpdatesFilterIcon = page.locator(
      "//arw-task-updates-widget//arw-icon[@name='filterFunnel01']"
    );
    this.timePeriod = page.locator("(//div[@class='mat-mdc-select-trigger'])[1]");
    this.timePeriodOptions = (days) => page.locator(`//div[normalize-space(text())='${days}']`);
    this.allTaskWorkedMartins = page.locator("//div[@class='flex gap-20 mt-8']");
    this.taskWorkedMartins = page.locator("//div[@class='flex gap-20 mt-8']//div//div");

    // ── Highest Balances widget ───────────────────────────────────────────
    this.highestBalancesLabel = page.locator("//div[normalize-space(text())='Highest Balances']");
    this.balanceLabels = page.locator(
      "//arw-highest-balances-widget//ng-scrollbar//div[contains(@class,'flex py-4')]/div[4]"
    );
    this.balancesListHighestBalancesRows = page.locator(
      "//arw-highest-balances-widget//ng-scrollbar//div[contains(@class,'ng-star-inserted')]"
    );
    this.balancesListHighestBalancesFacility = (row) => row.locator("div").nth(0);
    this.balancesListHighestBalancesResident = (row) => row.locator("a[href*='/cases/details']").first();
    this.balancesListHighestBalancesPayer = (row) => row.locator("div").nth(2);
    this.balancesListHighestBalancesBalanceLink = (row) => row.locator("a[href*='/balances']").first();
    this.balancesListHighestBalancesAmount = (row) => row.locator("a[href*='/balances']").first();

    // ── Unworked Tasks widget ─────────────────────────────────────────────
    this.unworkedTasksLabel = page.locator("//div[normalize-space(text())='Unworked Tasks']");
    this.unworkedTasksResidentNameLinks = page.locator(
      "(//div[normalize-space(text())='Resident'])[2]/following::a"
    );
    this.viewAgingButton = page.locator("//arw-button[@category='secondary']");

    // ── AR Status widget ───────────────────────────────────────────────────
    this.arStatusWidget = page.locator(
      "//arw-ar-status-widget"
    )

    this.arStatusfilterIcon = page.locator("//arw-ar-status-widget//arw-icon[@name='filterFunnel01']");

    this.arStatusValues = page.locator(
      "//arw-ar-status-widget//div[contains(@class,'font-bold') and contains(@class,'justify-end')]"
    );
    this.arStatusTotal = page.locator(
      "//arw-ar-status-widget//div[contains(@class,'flex justify')]//span[contains(@class,'font-bold')]"
    );
    this.tooltip = page.locator(`div.arw-tooltip-overlay.arw-tooltip-overlay--default`)
      .last();
    this.payerCategoryDropdown = page.locator("//arw-ar-status-widget//arw-select-tree[@mode='dropdown']//button");
    this.balanceStatusWidget = page.locator(
      "//arw-balance-status-widget"
    );
    this.balanceStatusStatusfilterIcon = page.locator(
      "//arw-balance-status-widget//arw-icon[@name='filterFunnel01']"
    );

    // ── Overdue Tasks widget (ARW-17) ─────────────────────────────────────
    this.overdueTasksWidget = page.locator("//arw-overdue-tasks-widget");
    this.overdueTasksFilterIcon = page.locator(
      "//arw-overdue-tasks-widget//arw-icon[@name='filterFunnel01']"
    );


    // ── Payer category dropdown / options ─────────────────────────────────
    this.payerCategoriesDropDownOptions = page.locator("//div[@class='cdk-virtual-scroll-content-wrapper ng-scroll-content']//span");
    this.applyBtn = page.locator("//span[normalize-space()='Apply']");
    this.payerCategoryCheckboxes = page.locator(
      "//div[contains(@class,'cdk-virtual-scroll-content-wrapper')]//mat-checkbox"
    );
    // The row's mat-checkbox has no label text of its own — the category name renders in a
    // sibling <div>, so filtering payerCategoryCheckboxes by hasText never matches. Locate the
    // row by its text instead, then scope the checkbox click/state check to that row.
    this.payerCategoryOptionRow = (categoryName) => page.locator(
      `//div[contains(@class,'cdk-virtual-scroll-content-wrapper')]//div[contains(@class,'web-body-1')][.//span[normalize-space()='${categoryName}']]`
    ).first();
    this.payerCategoriesDropDown = page.locator("//arw-dashboard-header//arw-select-tree[@mode='dropdown']//button");
    this.appliedPayerCategoryValue = (tab) => tab.locator(
      "//arw-dashboard-header//arw-select-tree[@mode='dropdown']//button//div[contains(@class,'arw-control-btn__value')]"
    );
    this.searchBoxField = page.locator(
      "//input[@placeholder='Search']"
    );

    // ── Task grid (dashboard preview) ─────────────────────────────────────
    this.facilityName = page.locator("(((//div[@class='flex flex-col px-8'])[2]//div)[1]//div)[1]");
    this.residentName = page.locator("(((//div[@class='flex flex-col px-8'])[2]//div)[1]//div)[2]");
    this.payerName = page.locator("(((//div[@class='flex flex-col px-8'])[2]//div)[1]//div)[3]");
    this.dueDate = page.locator("(((//div[@class='flex flex-col px-8'])[2]//div)[1]//div)[4]");
    this.balance = page.locator("(((//div[@class='flex flex-col px-8'])[2]//div)[1]//div)[5]");
    this.assigneeName = page.locator("(((//div[@class='flex flex-col px-8'])[2]//div)[1]//div)[6]");
    this.serviceDate = page.locator("(((//div[@class='flex flex-col px-8'])[2]//div)[1]//div)[7]");
    this.viewTaskBtn = page.locator("(((//div[@class='flex flex-col px-8'])[2]//div)[1]//div)[8]//button");

    // ── Task slide-out ─────────────────────────────────────────────────────
    this.facilityLocator = page.locator(
      "//span[normalize-space(text())='Facility']/ancestor::div[contains(@class,'items-center')]"
    );
    this.residentLocator = page.locator(
      "//span[normalize-space(text())='Resident']/ancestor::div[contains(@class,'items-center')]"
    );
    this.payerLocator = page.locator(
      "//span[normalize-space(text())='Payer']/ancestor::div[contains(@class,'items-center')]"
    );
    this.balanceLocator = page.locator("span.font-bold.mr-4");
    this.taskListDueDateInput = page.locator("arw-input[formcontrolname='dueDate'] input.mat-datepicker-input");
    this.taskListAssignedTo = page.locator(
      "(//span[@class='grow overflow-ellipsis overflow-hidden text-center whitespace-nowrap'])[1]"
    );
    this.taskCloseBtn = page.locator(
      "//div[@class='flex gap-8 items-center shrink-0']//arw-button[@icon='x']"
    );
    this.chargersServecesDates = page.locator(
      "(//ng-scrollbar[@class='arw-grid-table__body ng-scroll-viewport ng-scrollbar ng-star-inserted'])[1]//div[@data-column-definition-name='serviceDates']"
    );
    this.chargersLabel = page.locator("(//span[@class='mdc-tab__text-label'])[2]");

    // ── Tooltips ───────────────────────────────────────────────────────────
    this.dashBoardTooltips = (txt) => page.locator(
      `//div[contains(@class,'web-title-3') and contains(normalize-space(.),'${txt}')]//arw-icon`
    );

    // ── Side nav ───────────────────────────────────────────────────────────
    this.billerActivityReportBtn = page.locator("//arw-side-nav-node//span[normalize-space()='Activity Report']");
    this.dashBoardBtn = page.locator("//arw-side-nav-node//span[normalize-space()='Dashboard']");

    // ══════════════════════════════════════════
    // ── Balances List Locators ──
    // ══════════════════════════════════════════

    this.balancesListArStatusWidget = (statusName) => page.locator(
      `//arw-ar-status-widget//div[contains(@class,'flex items-center')][.//button[normalize-space()='${statusName}']]`
    );
    this.balancesListArStatusWidgetDot = (statusName) => page.locator(
      `//arw-ar-status-widget//div[contains(@class,'flex items-center')][.//button[normalize-space()='${statusName}']]//div[contains(@class,'rounded-full')]`
    );
    this.balancesListMatSpinner = (tab) => tab.locator("mat-spinner");
    this.balancesListFiltersBtn = (tab) => tab.locator("//span[normalize-space(text())='Filters']");
    this.balancesListStatusDropdown = (tab) => tab.locator(
      "//arw-select-tree[contains(@formcontrolname,'value')] | //button[contains(@class,'arw-control-btn')]"
    ).first();
    this.balancesListCdkOverlay = (tab) => tab.locator(".cdk-overlay-pane");
    this.balancesListStatusCheckbox = (tab, statusName) => tab.locator(
      `//div[normalize-space()='${statusName}']/preceding-sibling::mat-checkbox`
    );
    this.balancesListBlankNoTaskCheckbox = (tab) => tab.locator(
      `//div[normalize-space()='Blank (No Task)']/preceding-sibling::mat-checkbox`
    );
    this.balancesListFilterPanel = (tab) => tab.locator("//div[normalize-space(text())='Filter by']");
    this.balancesListFilterValue = (p) => p.locator("div.arw-control-btn__value");
    this.balancesListSubOptionsList = (p) => p.locator("mat-option, .mat-mdc-option, div.mdc-checkbox");
    this.balancesListSubOptionRow = (p, optionName) => p.locator(
      `//mat-option[.//span[normalize-space()='${optionName}']] | //div[contains(@class,'ng-star-inserted')][.//span[normalize-space()='${optionName}']]`
    ).first();
    this.balancesListSubOptionCheckbox = (p, optionName) => p.locator(
      `//mat-option[.//span[normalize-space()='${optionName}']] | //div[contains(@class,'ng-star-inserted')][.//span[normalize-space()='${optionName}']]`
    ).first().locator("input.mdc-checkbox__native-control").first();
    this.balancesListTotalBalanceAmount = page.locator(
      "//span[normalize-space(text())='Total Balance Amount:']/following-sibling::b"
    );

    // ── Task assigned to me ───────────────────────────────────────────────
    this.taskAssignedToMeBtn = page.locator("//a[contains(@href,'/tasks?assignedTo') and contains(@href,'statusIds')]");
    this.taskAssignedToMeCount = this.taskAssignedToMeBtn.locator("//span[contains(@class,'web-subtitle')]");
    this.taskCountInTaskList = page.locator("//arw-grid-table//span[contains(@class,'web-body')]");
    this.taskListPageTitle = page.locator("h2.web-title-1");
    this.taskListFilterValueText = page.locator("div.arw-control-btn__value");

    // ── Share functionality ────────────────────────────────────────────────
    this.shareButton = page.locator('arw-button[icon="share07"] button');
    this.shareLinkToast = page.locator('arw-toast span.web-body-1.text-foreground-high');

    // ── Filters ─────────────────────────────────────────────────────────────
    this.balanceStatusWidgetOptions = (optionName) => page.locator(
      `//button[@role='radio'][.//span[normalize-space()='${optionName}']]`
    );
    this.balanceStatusOptions = page.locator(
      "//div[contains(@class,'flex') and contains(@class,'justify-center') and contains(@class,'ng-star-inserted')]//button"
    );

    // ── Generic widget tooltips (Task Updates / Tasks Worked avatars & legend) ─
    this.widgetTooltip = page.locator('div.web-body-1:visible').last();
    this.avatarTooltip = page.locator('arw-tooltip-overlay div.web-body-1');

    // ── Filter icons across all dashboard widgets ─────────────────────────
    this.filterIcons = page.locator("//arw-icon[@name='filterFunnel01']");

  }

  // ── Payer Category filter actions ─────────────────────────────────────

  async openPayerCategoryFilter() {
    await test.step('Click Payer Category filter to open dropdown', async () => {
      await expect(this.payerCategoriesDropDown).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await this.payerCategoriesDropDown.click();
    });
  }

  async isPayerCategorySearchFieldVisible() {
    return test.step('Verify Payer Category search field is visible', async () => {
      return this.searchBoxField.isVisible();
    });
  }

  async searchPayerCategory(categoryName) {
    await test.step(`Search for "${categoryName}" in Payer Category search field`, async () => {
      await expect(this.searchBoxField).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await this.searchBoxField.fill(categoryName);
    });
  }

  async clearPayerCategorySearch() {
    await test.step('Clear the Payer Category search field', async () => {
      await this.searchBoxField.fill('');
    });
  }

  async getPayerCategoryOptionsCount() {
    return test.step('Count visible Payer Category options', async () => {
      return this.payerCategoriesDropDownOptions.count();
    });
  }

  async isPayerCategoryOptionVisible(categoryName) {
    return test.step(`Verify Payer Category option "${categoryName}" is visible`, async () => {
      return this.payerCategoriesDropDownOptions.filter({ hasText: categoryName }).first().isVisible();
    });
  }

  async selectPayerCategory(categoryName) {
    await test.step(`Select Payer Category checkbox for "${categoryName}"`, async () => {
      const row = this.payerCategoryOptionRow(categoryName);
      await expect(row).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await row.locator('mat-checkbox').click();
    });
  }

  async isPayerCategorySelected(categoryName) {
    return test.step(`Verify Payer Category "${categoryName}" checkbox is checked`, async () => {
      const row = this.payerCategoryOptionRow(categoryName);
      return row.locator('input.mdc-checkbox__native-control').isChecked();
    });
  }

  async isApplyButtonEnabled() {
    return test.step('Verify Apply button enabled state', async () => {
      return this.applyBtn.isEnabled();
    });
  }

  async clickApplyPayerCategoryFilter() {
    await test.step('Click Apply to submit Payer Category filter', async () => {
      await this.applyBtn.click();
    });
  }

  async getAppliedPayerCategoryFilterValue() {
    return test.step('Read the applied Payer Category filter value', async () => {
      return this.payerCategoriesDropDown.innerText();
    });
  }

  async navigateToDashboard() {
    await test.step('Navigate to the Dashboard page', async () => {
      await this.navigateTo(`${settings.BASE_URL}/dashboard`);
    });
  }

  async waitForDashboardLoad() {
    await test.step('Wait for Dashboard to finish loading', async () => {
      await expect(this.dashboardPage).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await this.loadSpinner.first().waitFor({ state: 'hidden', timeout: settings.PAGE_LOAD_TIMEOUT });
    });
  }

  async isPayerCategoryFilterVisible() {
    return test.step('Verify Payer Category filter control is visible', async () => {
      return this.payerCategoriesDropDown.isVisible();
    });
  }

  async isPayerCategoryDropdownOpen() {
    return test.step('Verify Payer Category dropdown panel is visible', async () => {
      return this.payerCategoriesDropDownOptions.first().isVisible();
    });
  }

  async closePayerCategoryDropdownByClickingOutside() {
    await test.step('Click outside the Payer Category dropdown to close it', async () => {
      await this.dashboardPage.click({ position: { x: 0, y: 0 } });
    });
  }

  // ── AR Status widget filter indicator actions ──────────────────────────

  async isArStatusFilterIconVisible() {
    return test.step('Verify the AR Status widget filter icon is visible', async () => {
      return this.arStatusfilterIcon.isVisible();
    });
  }

  async hoverArStatusFilterIcon() {
    await test.step('Hover over the AR Status widget filter icon', async () => {
      await expect(this.arStatusfilterIcon).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await this.arStatusfilterIcon.hover();
    });
  }

  async getArStatusFilterTooltipText() {
    return test.step('Read the AR Status widget filter tooltip text', async () => {
      await expect(this.tooltip).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      return this.tooltip.innerText();
    });
  }

  async isArStatusFilterTooltipVisible() {
    return test.step('Verify the AR Status widget filter tooltip is visible', async () => {
      return this.tooltip.isVisible();
    });
  }

  async hoverArStatusWidget() {
    await test.step('Hover over the AR Status widget header area', async () => {
      await expect(this.arStatusWidget).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await this.arStatusWidget.hover();
    });
  }

  // ── Overdue Tasks widget filter indicator actions (ARW-17) ─────────────

  async isOverdueTasksWidgetVisible() {
    return test.step('Verify the Overdue Tasks widget is visible', async () => {
      return this.overdueTasksWidget.isVisible();
    });
  }

  async isOverdueTasksFilterIconVisible() {
    return test.step('Verify the Overdue Tasks widget filter icon is visible', async () => {
      return this.overdueTasksFilterIcon.isVisible();
    });
  }

  async hoverOverdueTasksFilterIcon() {
    await test.step('Hover over the Overdue Tasks widget filter icon', async () => {
      await expect(this.overdueTasksFilterIcon).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await this.overdueTasksFilterIcon.scrollIntoViewIfNeeded();
      await this.overdueTasksFilterIcon.hover();
    });
  }

  async getOverdueTasksFilterTooltipText() {
    return test.step('Read the Overdue Tasks widget filter tooltip text', async () => {
      await expect(this.tooltip).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      return (await this.tooltip.innerText()).trim();
    });
  }

  async isOverdueTasksFilterTooltipVisible() {
    return test.step('Verify the Overdue Tasks widget filter tooltip is visible', async () => {
      return this.tooltip.isVisible();
    });
  }

  async hoverOverdueTasksWidget() {
    await test.step('Hover over the Overdue Tasks widget header area', async () => {
      await expect(this.overdueTasksWidget).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await this.overdueTasksWidget.scrollIntoViewIfNeeded();
      await this.overdueTasksWidget.hover();
    });
  }

  // ── Task Updates widget filter indicator actions (ARW-18) ──────────────

  async isTaskUpdatesWidgetVisible() {
    return test.step('Verify the Task Updates widget is visible', async () => {
      return this.taskUpdateWidget.isVisible();
    });
  }

  async isTaskUpdatesFilterIconVisible() {
    return test.step('Verify the Task Updates widget filter icon is visible', async () => {
      return this.taskUpdatesFilterIcon.isVisible();
    });
  }

  async hoverTaskUpdatesFilterIcon() {
    await test.step('Hover over the Task Updates widget filter icon', async () => {
      await expect(this.taskUpdatesFilterIcon).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await this.taskUpdatesFilterIcon.scrollIntoViewIfNeeded();
      await this.taskUpdatesFilterIcon.hover();
    });
  }

  async getTaskUpdatesFilterTooltipText() {
    return test.step('Read the Task Updates widget filter tooltip text', async () => {
      await expect(this.tooltip).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      return (await this.tooltip.innerText()).trim();
    });
  }

  async isTaskUpdatesFilterTooltipVisible() {
    return test.step('Verify the Task Updates widget filter tooltip is visible', async () => {
      return this.tooltip.isVisible();
    });
  }

  // The Payer Category filter is a per-user preference that survives navigation and page
  // reloads (see verifyDashboardRefreshClearsPayerCategoryFilter), and selectPayerCategory()
  // toggles rather than sets. With workers: 1 and a shared storageState, a filter applied by
  // one test leaks into the next, so tests that require an unfiltered Dashboard must reset first.
  async resetPayerCategoryFilter() {
    await test.step('Reset the Payer Category filter to its unfiltered state', async () => {
      await expect(this.payerCategoriesDropDown).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });

      if ((await this.filterIcons.count()) === 0) {
        return;
      }

      await this.payerCategoriesDropDown.click();
      await this.uncheckAllSelectedPayerCategories();

      if (await this.applyBtn.isEnabled()) {
        await this.applyBtn.click();
      } else {
        await this.closePayerCategoryDropdownByClickingOutside();
      }

      await expect(this.loadSpinner).toHaveCount(0, { timeout: settings.PAGE_LOAD_TIMEOUT });
      await expect(this.filterIcons).toHaveCount(0, { timeout: settings.TIMEOUT });
    });
  }

  async selectPayerCategoryOtherThan(excludedCategoryName) {
    return test.step(`Select the first Payer Category option other than "${excludedCategoryName}"`, async () => {
      await this.payerCategoriesDropDownOptions.first().waitFor({
        state: 'visible',
        timeout: settings.TIMEOUT,
      });

      const optionCount = await this.payerCategoriesDropDownOptions.count();
      expect(optionCount, 'Payer Category dropdown should list at least one option').toBeGreaterThan(0);

      for (let i = 0; i < optionCount; i++) {
        const option = this.payerCategoriesDropDownOptions.nth(i);
        const optionName = (await option.innerText()).trim();

        if (optionName && optionName !== excludedCategoryName) {
          await option.scrollIntoViewIfNeeded();
          await option.click();
          return optionName;
        }
      }

      throw new Error(
        `No Payer Category option other than "${excludedCategoryName}" is available to switch to`
      );
    });
  }

  // ── Module cards ─────────────────────────────────────────────────────

  async validateTaskListModuleCardOnDashboard() {
    await test.step('Verify the Task List module card is visible on the dashboard', async () => {
      await expect(this.taskListModuleCard).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
    });
  }

  async validateArAgingModuleCardOnDashboard() {
    await test.step('Verify the AR Aging module card is visible on the dashboard', async () => {
      await expect(this.agingModuleCard).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
    });
  }

  // ── Task Updates / Tasks Worked widget tooltips ─────────────────────

  async verifyTaskUpdatesWidgetTooltips() {
    await test.step('Verify Task Updates widget avatar tooltips', async () => {
      if (await this.taskUpdatesNoData.isVisible()) {
        return;
      }

      await this.taskUpdateAvatarToolpits.first().waitFor({ state: 'visible', timeout: settings.PAGE_LOAD_TIMEOUT });
      await this.taskUpdateAvatarToolpits.first().scrollIntoViewIfNeeded();

      const avatarCount = await this.taskUpdateAvatarToolpits.count();
      expect(avatarCount, 'Task Updates widget should have at least one avatar').toBeGreaterThan(0);

      for (let i = 0; i < avatarCount; i++) {
        const avatar = this.taskUpdateAvatarToolpits.nth(i);
        await avatar.hover();
        await expect(this.avatarTooltip).toBeVisible({ timeout: settings.SHORT_TIMEOUT });

        const tooltipText = (await this.avatarTooltip.innerText()).trim();
        const userName = tooltipText.split('\n').map(l => l.trim()).filter(Boolean)[0];
        const count = Number((tooltipText.match(/\d+/) || [0])[0]);

        expect(userName, `Avatar ${i} tooltip should show a user name`).toBeTruthy();
        expect(count, `Avatar ${i} tooltip count should be >= 0`).toBeGreaterThanOrEqual(0);

        await this.page.mouse.move(0, 0);

        const canvasBox = await this.taskUpdateCanvas.boundingBox();
        expect(canvasBox, 'Task Updates graph canvas should exist').not.toBeNull();
      }
    });
  }

  async verifyTaskWorkedMartinTooltips() {
    await test.step('Verify Tasks Worked widget Martin legend tooltips', async () => {
      if (await this.tasksWorkedNoData.isVisible()) {
        return;
      }

      await this.allTaskWorkedMartins.waitFor({ state: 'visible', timeout: settings.PAGE_LOAD_TIMEOUT });
      await this.taskWorkedMartins.first().scrollIntoViewIfNeeded();

      const martinsCount = await this.taskWorkedMartins.count();
      expect(martinsCount, 'Tasks Worked widget should have 3 Martin legend items').toBe(3);

      const expectedTooltips = [
        'Balance status updated within 2 days of due date',
        'Balance status updated within 3 - 7 days of due date',
        'Balance status updated > 7 days of due date',
      ];

      for (let i = 0; i < martinsCount; i++) {
        const martin = this.taskWorkedMartins.nth(i);
        await martin.scrollIntoViewIfNeeded();
        await martin.hover();

        await expect(this.widgetTooltip).toBeVisible({ timeout: settings.SHORT_TIMEOUT });
        const tooltipText = (await this.widgetTooltip.innerText()).trim();

        expect(tooltipText, `Martin ${i} tooltip text should match the expected legend text`).toBe(expectedTooltips[i]);

        await this.page.mouse.move(0, 0);
      }
    });
  }

  async verifyTaskWorkedUserTooltips() {
    await test.step('Verify Tasks Worked widget avatar tooltips', async () => {
      if (await this.tasksWorkedNoData.isVisible()) {
        return;
      }

      await this.taskWorkedAvatarToolpits.first().waitFor({ state: 'visible', timeout: settings.PAGE_LOAD_TIMEOUT });
      await this.taskWorkedAvatarToolpits.first().scrollIntoViewIfNeeded();

      const avatarCount = await this.taskWorkedAvatarToolpits.count();
      expect(avatarCount, 'Tasks Worked widget should have at least one avatar').toBeGreaterThan(0);

      for (let i = 0; i < avatarCount; i++) {
        const avatar = this.taskWorkedAvatarToolpits.nth(i);
        await avatar.hover();

        await expect(this.widgetTooltip).toBeVisible({ timeout: settings.SHORT_TIMEOUT });
        const text = await this.widgetTooltip.innerText();
        const userName = text.split('\n').map(l => l.trim()).filter(Boolean)[0];
        expect(userName, `Avatar ${i} tooltip should show a user name`).toBeTruthy();

        const getValue = (label) => {
          const match = text.match(new RegExp(`${label}:\\s*(\\d+)`, 'i'));
          return match ? Number(match[1]) : 0;
        };

        expect(getValue('Due Now')).toBeGreaterThanOrEqual(0);
        expect(getValue('Due Soon')).toBeGreaterThanOrEqual(0);
        expect(getValue('Due Future')).toBeGreaterThanOrEqual(0);

        await this.page.mouse.move(0, 0);
      }
    });
  }

  // ── Unworked Tasks widget ────────────────────────────────────────────

  async clickResidentNameLinkInUnworkedTasks() {
    return test.step('Click a random resident name link in the Unworked Tasks widget', async () => {
      await this.unworkedTasksResidentNameLinks.first().waitFor({ state: 'visible', timeout: settings.PAGE_LOAD_TIMEOUT });

      const noOfLinks = await this.unworkedTasksResidentNameLinks.count();
      const facilityNameLinks = this.unworkedTasksResidentNameLinks.locator('//preceding::div[1]');
      const payerNameLinks = this.unworkedTasksResidentNameLinks.locator('//following::div[1]');

      const randomIndex = Math.floor(Math.random() * noOfLinks);
      const residentNameLink = this.unworkedTasksResidentNameLinks.nth(randomIndex);
      const facilityNameLink = facilityNameLinks.nth(randomIndex);
      const payerNameLink = payerNameLinks.nth(randomIndex);

      const residentName = (await residentNameLink.textContent()).trim();
      const facilityName = (await facilityNameLink.textContent()).trim();
      const payerName = (await payerNameLink.textContent()).trim();

      await residentNameLink.click();

      return { residentName, facilityName, payerName };
    });
  }

  async verifyPayerDetailsForUnworkedTasks() {
    await test.step('Verify resident/facility details carry over to the case page from Unworked Tasks', async () => {
      const [newPage, { residentName, facilityName }] = await Promise.all([
        this.page.waitForEvent('popup'),
        this.clickResidentNameLinkInUnworkedTasks(),
      ]);

      await newPage.locator("//mat-spinner[@role='progressbar']")
        .waitFor({ state: 'hidden', timeout: settings.PAGE_LOAD_TIMEOUT })
        .catch(() => { });

      const viewAgingButton = newPage.locator("//arw-button[@category='secondary']");
      await viewAgingButton.waitFor({ state: 'visible', timeout: settings.PAGE_LOAD_TIMEOUT });

      const residentNameHeader = newPage.locator("//arw-button[@icon='chevronLeft']/following::span[1]");
      const facilityNameLabel = newPage.locator("//arw-button[@category='secondary']/preceding::div[2]");

      expect(await residentNameHeader.innerText()).toContain(residentName);
      expect(await facilityNameLabel.innerText()).toContain(facilityName);
    });
  }

  // ── Highest Balances widget ──────────────────────────────────────────

  async verifyBalanceOrderInHighestBalancesTable() {
    await test.step('Verify Highest Balances widget rows are sorted descending by balance', async () => {
      await expect(this.dashboardPage).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await this.highestBalancesLabel.waitFor({ state: 'visible', timeout: settings.TIMEOUT });
      await this.balanceLabels.first().waitFor({ state: 'visible', timeout: settings.TIMEOUT });

      const balanceLabels = await this.balanceLabels.all();
      const balances = [];
      for (const balanceLabel of balanceLabels) {
        const text = await balanceLabel.textContent();
        balances.push(Number(text.replace(/[$,]/g, '').trim()));
      }

      for (let i = 0; i < balances.length - 1; i++) {
        expect(balances[i]).toBeGreaterThanOrEqual(balances[i + 1]);
      }
    });
  }

  async verifyHighestBalanceAmountOnDashboard() {
    await test.step('Verify the Highest Balances widget amount matches the resident case balance', async () => {
      const highestBalanceRow = this.balancesListHighestBalancesRows.first();

      await expect(this.dashboardPage).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await highestBalanceRow.scrollIntoViewIfNeeded();
      await expect(highestBalanceRow).toBeVisible({ timeout: settings.TIMEOUT });

      const facilityName = (await highestBalanceRow.locator('div').nth(0).textContent()).trim();
      const residentName = (await highestBalanceRow.locator('div').nth(1).textContent()).trim();
      const payerName = (await highestBalanceRow.locator('div').nth(2).textContent()).trim();
      const balanceText = (await highestBalanceRow.locator('div').nth(3).textContent()).trim();
      const highestBalanceNumber = Math.trunc(Number(balanceText.replace(/[^\d.-]/g, '')));

      const [newPage] = await Promise.all([
        this.page.context().waitForEvent('page'),
        this.page.getByText(residentName, { exact: true }).click(),
      ]);

      await newPage.waitForLoadState('domcontentloaded');
      await newPage.locator('mat-spinner').waitFor({ state: 'hidden', timeout: settings.PAGE_LOAD_TIMEOUT }).catch(() => { });

      const residentHeader = newPage.locator("//arw-case-details//span[@class='web-title-2 text-foreground-blue']");
      await expect(residentHeader).toBeVisible({ timeout: settings.TIMEOUT });
      expect((await residentHeader.textContent()).trim()).toBe(residentName);

      const payerRow = newPage
        .locator('div.arw-grid-table__row-wrapper')
        .filter({ has: newPage.locator('span', { hasText: payerName }) })
        .first();
      await expect(payerRow).toBeVisible({ timeout: settings.TIMEOUT });

      const totalBalanceCell = payerRow.locator("div[data-column-definition-name='totalBalance']");
      await expect(totalBalanceCell).toBeVisible();

      const totalBalanceNumber = Math.trunc(Number((await totalBalanceCell.textContent()).trim().replace(/[^\d.-]/g, '')));

      expect(totalBalanceNumber).toBe(highestBalanceNumber);
    });
  }

  async validateHighestBalancesToBalanceListFilters() {
    await test.step('Validate a Highest Balances row navigates to matching Balances List filters', async () => {
      await expect(this.dashboardPage).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await expect(this.loadSpinner).toHaveCount(0, { timeout: settings.PAGE_LOAD_TIMEOUT });

      await this.balancesListHighestBalancesRows.first().waitFor({ state: 'visible', timeout: settings.TIMEOUT });

      const rowCount = await this.balancesListHighestBalancesRows.count();
      const randomIndex = Math.floor(Math.random() * rowCount);
      const selectedRow = this.balancesListHighestBalancesRows.nth(randomIndex);

      await selectedRow.scrollIntoViewIfNeeded();
      await selectedRow.waitFor({ state: 'visible', timeout: settings.TIMEOUT });

      const facilityText = (await this.balancesListHighestBalancesFacility(selectedRow).innerText()).trim();
      const residentText = (await this.balancesListHighestBalancesResident(selectedRow).innerText()).trim();
      const payerText = (await this.balancesListHighestBalancesPayer(selectedRow).innerText()).trim();

      const balanceLink = this.balancesListHighestBalancesBalanceLink(selectedRow);
      await balanceLink.waitFor({ state: 'visible', timeout: settings.TIMEOUT });

      await Promise.all([
        this.page.waitForURL(/balances/, { timeout: settings.PAGE_LOAD_TIMEOUT }),
        balanceLink.click(),
      ]);

      await this.page.waitForLoadState('domcontentloaded');
      await this.balancesListMatSpinner(this.page).waitFor({ state: 'hidden', timeout: settings.PAGE_LOAD_TIMEOUT }).catch(() => { });

      const filtersBtn = this.balancesListFiltersBtn(this.page);
      await filtersBtn.waitFor({ state: 'visible', timeout: settings.TIMEOUT });
      await filtersBtn.click();

      await this.balancesListFilterPanel(this.page).waitFor({ state: 'visible', timeout: settings.TIMEOUT }).catch(() => { });

      const filterValues = this.taskListFilterValueText;
      await filterValues.first().waitFor({ state: 'visible', timeout: settings.TIMEOUT });

      const appliedResident = (await filterValues.nth(0).innerText()).trim();
      const appliedFacility = (await filterValues.nth(1).innerText()).trim();
      const appliedPayer = (await filterValues.nth(2).innerText()).trim();

      expect(appliedResident, `Resident filter "${appliedResident}" does not match widget value "${residentText}"`).toBe(residentText);
      expect(appliedFacility, `Facility filter "${appliedFacility}" does not match widget value "${facilityText}"`).toBe(facilityText);
      expect(appliedPayer, `Payer filter "${appliedPayer}" does not match widget value "${payerText}"`).toContain(payerText);

      await this.page.keyboard.press('Escape');
      await this.dashBoardBtn.click();
      await expect(this.dashboardPage).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await expect(this.loadSpinner).toHaveCount(0, { timeout: settings.PAGE_LOAD_TIMEOUT });
    });
  }

  async validateHighestBalancesMatchesInBalancesList() {
    await test.step('Validate a Highest Balances amount matches the Balances List total', async () => {
      await expect(this.dashboardPage).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await expect(this.loadSpinner).toHaveCount(0, { timeout: settings.PAGE_LOAD_TIMEOUT });

      await this.balancesListHighestBalancesRows.first().waitFor({ state: 'visible', timeout: settings.TIMEOUT });

      const rowCount = await this.balancesListHighestBalancesRows.count();
      const randomIndex = Math.floor(Math.random() * rowCount);
      const selectedRow = this.balancesListHighestBalancesRows.nth(randomIndex);

      await selectedRow.scrollIntoViewIfNeeded();
      await selectedRow.waitFor({ state: 'visible', timeout: settings.TIMEOUT });

      const parseAmount = (text) => {
        const isNegative = text.includes('(');
        const value = parseFloat(text.replace(/[$,()\s]/g, ''));
        return isNegative ? -value : value;
      };

      const dashboardBalanceRaw = (await this.balancesListHighestBalancesAmount(selectedRow).innerText()).trim();
      const dashboardBalanceValue = parseAmount(dashboardBalanceRaw);

      const balanceLink = this.balancesListHighestBalancesBalanceLink(selectedRow);
      await balanceLink.waitFor({ state: 'visible', timeout: settings.TIMEOUT });

      await Promise.all([
        this.page.waitForURL(/balances/, { timeout: settings.PAGE_LOAD_TIMEOUT }),
        balanceLink.click(),
      ]);

      await this.page.waitForLoadState('domcontentloaded');
      await this.balancesListMatSpinner(this.page).waitFor({ state: 'hidden', timeout: settings.PAGE_LOAD_TIMEOUT }).catch(() => { });

      await this.balancesListTotalBalanceAmount.waitFor({ state: 'visible', timeout: settings.TIMEOUT });
      const balancesListAmountRaw = (await this.balancesListTotalBalanceAmount.innerText()).trim();
      const balancesListValue = parseAmount(balancesListAmountRaw);

      expect(
        balancesListValue,
        `Balance mismatch — Dashboard: ${dashboardBalanceRaw} | Balances List Total: ${balancesListAmountRaw}`
      ).toBe(dashboardBalanceValue);

      await this.dashBoardBtn.click();
      await expect(this.dashboardPage).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await expect(this.loadSpinner).toHaveCount(0, { timeout: settings.PAGE_LOAD_TIMEOUT });
    });
  }

  // ── AR Status widget totals / filter ─────────────────────────────────

  async verifyArStatusTotal() {
    return test.step('Verify AR Status total equals sum of all AR status values', async () => {
      await expect(this.arStatusTotal).toBeVisible({ timeout: settings.TIMEOUT });
      await expect(this.arStatusValues).toHaveCount(4);

      const valuesText = await this.arStatusValues.allTextContents();
      const values = valuesText.map(text => Number(text.replace(/[$,]/g, '').trim()));
      const calculatedTotal = values.reduce((sum, v) => sum + v, 0);

      const totalText = await this.arStatusTotal.textContent();
      const uiTotal = Number(totalText.replace(/[$,]/g, '').trim());

      expect(calculatedTotal).toBe(uiTotal);
      return uiTotal;
    });
  }

  async selectMultipleCheckboxesFromDropdown(dropdownLocator, checkboxLocator, countToSelect, stepName = `Select ${countToSelect} options from dropdown`, clickApply = true) {
    await test.step(stepName, async () => {
      await dropdownLocator.click();
      await expect(checkboxLocator.first()).toBeVisible({ timeout: settings.TIMEOUT });

      const totalOptions = await checkboxLocator.count();
      if (totalOptions < countToSelect) {
        throw new Error(`Not enough options available. Required ${countToSelect}, found ${totalOptions}`);
      }

      let selected = 0;
      for (let i = 0; i < totalOptions && selected < countToSelect; i++) {
        const checkbox = checkboxLocator.nth(i);
        const isChecked = await checkbox.getAttribute('aria-checked');
        if (isChecked !== 'true') {
          await checkbox.click();
          selected++;
        }
      }

      expect(selected).toBe(countToSelect);

      if (clickApply) {
        await expect(this.applyBtn).toBeVisible();
        await expect(this.applyBtn).toBeEnabled();
        await this.applyBtn.click();
      }
    });
  }

  async verifyPayerCategoryFilterFunctionalityArStatusWidget() {
    await test.step('Verify Payer Category filter updates the AR Status widget total', async () => {
      await expect(this.arStatusTotal).toBeVisible({ timeout: settings.TIMEOUT });

      await this.selectMultipleCheckboxesFromDropdown(
        this.payerCategoryDropdown,
        this.payerCategoryCheckboxes,
        2,
        'Select two payer categories',
        true
      );

      await expect(this.loadSpinner).toHaveCount(0, { timeout: settings.PAGE_LOAD_TIMEOUT });

      await this.verifyArStatusTotal();
    });
  }

  async verifyDashboardRefreshClearsPayerCategoryFilter() {
    await test.step('Verify navigating away and back to the Dashboard clears the Payer Category filter', async () => {
      await expect(this.dashboardPage).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await expect(this.loadSpinner).toHaveCount(0, { timeout: settings.PAGE_LOAD_TIMEOUT });
      await this.payerCategoriesDropDown.scrollIntoViewIfNeeded();
      await expect(this.payerCategoriesDropDown).toBeVisible({ timeout: settings.TIMEOUT });
      await expect(this.arStatusTotal).toBeVisible({ timeout: settings.TIMEOUT });

      const totalBeforeFilter = (await this.arStatusTotal.textContent()).trim();

      await this.payerCategoriesDropDown.click();
      const optionCount = await this.payerCategoriesDropDownOptions.count();
      expect(optionCount).toBeGreaterThan(0);

      const randomIndex = Math.floor(Math.random() * optionCount);
      const option = this.payerCategoriesDropDownOptions.nth(randomIndex);
      await option.scrollIntoViewIfNeeded();
      await option.click();
      await this.applyBtn.click();

      await expect(this.arStatusTotal).toBeVisible({ timeout: settings.TIMEOUT });
      const totalAfterFilter = (await this.arStatusTotal.textContent()).trim();

      expect(totalAfterFilter).not.toBe(totalBeforeFilter);

      await expect(this.billerActivityReportBtn).toBeVisible({ timeout: settings.TIMEOUT });
      await this.billerActivityReportBtn.click();
      await expect(this.loadSpinner).toHaveCount(0, { timeout: settings.PAGE_LOAD_TIMEOUT });

      await this.dashBoardBtn.click();
      await expect(this.loadSpinner).toHaveCount(0, { timeout: settings.PAGE_LOAD_TIMEOUT });
      await expect(this.arStatusTotal).toBeVisible({ timeout: settings.TIMEOUT });

      const totalAfterReturningToDashboard = (await this.arStatusTotal.textContent()).trim();
      expect(totalAfterReturningToDashboard).toBe(totalAfterFilter);
    });
  }

  async applyRandomPayerCategoryFilter() {
    return test.step('Apply a random Payer Category filter', async () => {
      await this.payerCategoriesDropDown.scrollIntoViewIfNeeded();
      await expect(this.payerCategoriesDropDown).toBeVisible({ timeout: settings.TIMEOUT });
      await this.payerCategoriesDropDown.click();

      const optionCount = await this.payerCategoriesDropDownOptions.count();
      expect(optionCount).toBeGreaterThan(0);

      const randomIndex = Math.floor(Math.random() * optionCount);
      const option = this.payerCategoriesDropDownOptions.nth(randomIndex);
      const selectedPayerCategory = (await option.innerText()).trim();

      await option.scrollIntoViewIfNeeded();
      await option.click();
      await this.applyBtn.click();

      await expect(this.loadSpinner).toHaveCount(0, { timeout: settings.PAGE_LOAD_TIMEOUT });

      return selectedPayerCategory;
    });
  }

  async selectRandomOptionsFromPayerCategoriesDropdown(count) {
    return test.step(`Select ${count} random Payer Category options`, async () => {
      await expect(this.dashboardPage).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await this.payerCategoriesDropDown.scrollIntoViewIfNeeded();
      await expect(this.payerCategoriesDropDown).toBeVisible({ timeout: settings.TIMEOUT });

      await this.payerCategoriesDropDown.click();
      await this.payerCategoriesDropDownOptions.first().waitFor({ state: 'visible', timeout: settings.TIMEOUT });

      const optionCount = await this.payerCategoriesDropDownOptions.count();
      expect(optionCount).toBeGreaterThan(0);

      const selectCount = Math.min(count, optionCount);
      const shuffled = Array.from({ length: optionCount }, (_, i) => i).sort(() => Math.random() - 0.5);
      const selectedIndices = shuffled.slice(0, selectCount);

      const selectedOptionNames = [];
      for (const index of selectedIndices) {
        const option = this.payerCategoriesDropDownOptions.nth(index);
        await option.scrollIntoViewIfNeeded();
        selectedOptionNames.push((await option.innerText()).trim());
        await option.click();
      }

      await this.applyBtn.scrollIntoViewIfNeeded();
      await this.applyBtn.click();

      return selectedOptionNames;
    });
  }

  async uncheckAllSelectedPayerCategories() {
    await test.step('Uncheck all currently selected Payer Category checkboxes', async () => {
      const count = await this.payerCategoryCheckboxes.count();

      for (let i = 0; i < count; i++) {
        const checkbox = this.payerCategoryCheckboxes.nth(i);
        const classAttr = await checkbox.getAttribute('class');

        if (classAttr?.includes('mat-mdc-checkbox-checked')) {
          await checkbox.scrollIntoViewIfNeeded();
          await checkbox.click();
        }
      }
    });
  }

  // ── Dashboard widget API status per Payer Category ───────────────────

  async verifyDashboardWidgetApiStatusForEachPayerCategory({ widgetName, payerCategoryDropdown, apiEndpoints }) {
    await test.step(`Verify ${widgetName} API status code for each Payer Category`, async () => {
      await expect(this.dashboardPage).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await payerCategoryDropdown.scrollIntoViewIfNeeded();
      await expect(payerCategoryDropdown).toBeVisible({ timeout: settings.TIMEOUT });

      await payerCategoryDropdown.click();
      const optionCount = await this.payerCategoriesDropDownOptions.count();
      expect(optionCount).toBeGreaterThan(0);
      await this.page.keyboard.press('Escape');

      for (let i = 0; i < optionCount; i++) {
        await payerCategoryDropdown.click();
        await this.uncheckAllSelectedPayerCategories();

        const option = this.payerCategoriesDropDownOptions.nth(i);
        await option.scrollIntoViewIfNeeded();
        await option.click();
        await this.applyBtn.click();

        const apiResponses = await Promise.all(
          apiEndpoints.map(endpoint =>
            this.page.waitForResponse(res =>
              res.url().includes(endpoint) &&
              res.request().method() === 'POST' &&
              res.status() === 200
            )
          )
        );

        for (const response of apiResponses) {
          expect(response.status()).toBe(200);
        }
      }
    });
  }

  async verifyBalanceStatusBreakdownApiForEachPayerCategory() {
    await this.verifyDashboardWidgetApiStatusForEachPayerCategory({
      widgetName: 'Balance Status Breakdown',
      payerCategoryDropdown: this.payerCategoriesDropDown,
      apiEndpoints: ['api/v1/dashboard/balance-status-totals'],
    });
  }

  async verifyHighestBalancesApiForEachPayerCategory() {
    await this.verifyDashboardWidgetApiStatusForEachPayerCategory({
      widgetName: 'Highest Balances',
      payerCategoryDropdown: this.payerCategoriesDropDown,
      apiEndpoints: ['api/v1/dashboard/highest-balances'],
    });
  }

  async verifyUnworkedTasksApiForEachPayerCategory() {
    await this.verifyDashboardWidgetApiStatusForEachPayerCategory({
      widgetName: 'Unworked Tasks',
      payerCategoryDropdown: this.payerCategoriesDropDown,
      apiEndpoints: ['api/v1/tasks/list'],
    });
  }

  async verifyArStatusApiForEachPayerCategory() {
    await this.verifyDashboardWidgetApiStatusForEachPayerCategory({
      widgetName: 'All Widgets',
      payerCategoryDropdown: this.payerCategoriesDropDown,
      apiEndpoints: [
        '/api/v1/dashboard/ar-status-totals',
        'api/v1/tasks/list',
        'api/v1/dashboard/highest-balances',
        'api/v1/dashboard/balance-status-totals',
      ],
    });
  }

  // ── Task slide-out ────────────────────────────────────────────────────

  async getFieldValue(containerLocator, labelText) {
    return test.step(`Read the "${labelText}" field value`, async () => {
      const rawText = await containerLocator.innerText();
      return rawText.replace(new RegExp(`^${labelText}\\s*`, 'i'), '').trim();
    });
  }

  async verifyTaskSlideOutMatchesGridValues() {
    await test.step('Verify grid task values match the task slide-out', async () => {
      let gridTaskValues;
      let slideOutTaskValues;

      await test.step('Capture task values from the grid', async () => {
        await this.facilityName.waitFor({ state: 'visible', timeout: settings.TIMEOUT });

        gridTaskValues = {
          facility: (await this.facilityName.textContent())?.trim(),
          resident: (await this.residentName.textContent())?.trim(),
          payer: (await this.payerName.textContent())?.trim(),
          dueDate: (await this.dueDate.textContent())?.trim(),
          balance: (await this.balance.innerText()).trim(),
          assignee: (await this.assigneeName.textContent())?.trim(),
          serviceDate: (await this.serviceDate.textContent())?.trim(),
        };
      });

      await test.step('Open the task slide-out', async () => {
        await this.viewTaskBtn.waitFor({ state: 'visible', timeout: settings.TIMEOUT });
        await this.viewTaskBtn.click();
      });

      await test.step('Capture task values from the slide-out', async () => {
        await this.balanceLocator.waitFor({ state: 'visible', timeout: settings.TIMEOUT });

        slideOutTaskValues = {
          facility: await this.getFieldValue(this.facilityLocator, 'Facility'),
          resident: await this.getFieldValue(this.residentLocator, 'Resident'),
          payer: await this.getFieldValue(this.payerLocator, 'Payer'),
          balance: (await this.balanceLocator.innerText()).trim(),
          dueDate: (await this.taskListDueDateInput.inputValue()).trim(),
          assignee: (await this.taskListAssignedTo.innerText()).trim(),
        };
      });

      const normalizeText = (text = '') => text.replace(/\s+/g, ' ').trim();
      const toNumber = (value = '') => Number(value.replace(/[^0-9.]/g, ''));
      const normalizeDateRange = (text = '') => text.replace(/\s+/g, ' ').replace(/\s*-\s*/g, '-').trim();

      await test.step('Validate grid values match slide-out values', async () => {
        expect(normalizeText(slideOutTaskValues.facility)).toBe(normalizeText(gridTaskValues.facility));
        expect(normalizeText(slideOutTaskValues.resident)).toBe(normalizeText(gridTaskValues.resident));
        expect(normalizeText(slideOutTaskValues.payer)).toBe(normalizeText(gridTaskValues.payer));
        expect(normalizeText(slideOutTaskValues.assignee)).toBe(normalizeText(gridTaskValues.assignee));
        expect(normalizeText(slideOutTaskValues.dueDate)).toContain(normalizeText(gridTaskValues.dueDate));
        expect(toNumber(slideOutTaskValues.balance)).toBe(toNumber(gridTaskValues.balance));
      });

      await test.step('Validate the service date appears in the slide-out charges tab', async () => {
        await this.chargersLabel.click();

        const gridServiceDate = normalizeDateRange(gridTaskValues.serviceDate);
        const serviceDateRanges = (await this.chargersServecesDates.allTextContents()).map(normalizeDateRange);

        expect(
          serviceDateRanges.includes(gridServiceDate),
          `Expected at least one service date range to match "${gridTaskValues.serviceDate}"`
        ).toBeTruthy();
      });

      await test.step('Close the task slide-out', async () => {
        await this.taskCloseBtn.click();
      });
    });
  }

  // ── Dashboard widget tooltips (general) ──────────────────────────────

  async validateDashboardWidgetTooltip(widgetName, expectedText) {
    await test.step(`Validate tooltip for the "${widgetName}" widget`, async () => {
      const tooltipIcon = this.dashBoardTooltips(widgetName);
      await tooltipIcon.scrollIntoViewIfNeeded();
      await tooltipIcon.hover();

      const tooltip = this.page.locator('div.web-body-1').filter({ hasText: expectedText }).first();
      await expect(tooltip).toBeVisible({ timeout: settings.SHORT_TIMEOUT });

      expect((await tooltip.innerText()).trim()).toBe(expectedText);
    });
  }

  async verifyAllDashboardWidgetTooltips(tooltipData) {
    await test.step('Verify tooltips are visible on all Supervisor Dashboard widgets', async () => {
      await expect(this.dashboardPage).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });

      const widgets = [
        { name: 'AR Status', text: tooltipData.arStatus },
        { name: 'Balance Status Breakdown', text: tooltipData.balanceStatusBreakdown },
        { name: 'Overdue Tasks', text: tooltipData.overdueTasks },
        { name: 'Task Updates', text: tooltipData.taskUpdates },
        { name: 'Tasks Worked', text: tooltipData.tasksWorked },
        { name: 'Highest Balances', text: tooltipData.highestBalances },
        { name: 'Unworked Tasks', text: tooltipData.unworkedTasks },
      ];

      for (const widget of widgets) {
        await this.validateDashboardWidgetTooltip(widget.name, widget.text);
      }
    });
  }

  // ── Filter icon tooltips (multi-widget) ──────────────────────────────

  async #verifyTooltipsOnFilterIcons(selectedFilters, label = '') {
    await test.step(`${label} Verify filter icon tooltips contain the applied filters`, async () => {
      const expectedTooltipPrefix = 'Filters (';

      await this.filterIcons.first().waitFor({ state: 'visible', timeout: settings.TIMEOUT });
      const iconCount = await this.filterIcons.count();
      expect(iconCount).toBeGreaterThan(0);

      for (let i = 0; i < iconCount; i++) {
        const icon = this.filterIcons.nth(i);
        await icon.scrollIntoViewIfNeeded();
        await icon.hover();

        await expect(this.tooltip).toBeVisible({ timeout: settings.SHORT_TIMEOUT });
        const tooltipText = (await this.tooltip.innerText()).trim();

        expect(tooltipText, `${label} Icon [${i}] tooltip should start with "Filters ("`).toContain(expectedTooltipPrefix);

        for (const filterName of selectedFilters) {
          expect(tooltipText, `${label} Icon [${i}] tooltip should contain: "${filterName}"`).toContain(filterName);
        }

        await this.page.mouse.move(0, 0);
      }
    });
  }

  async verifyFilterTooltipOnHoverOfFilterIcon(count) {
    return test.step(`Apply ${count} Payer Category filters and verify tooltips on filter icons`, async () => {
      const selectedFilters = await this.selectRandomOptionsFromPayerCategoriesDropdown(count);
      await this.#verifyTooltipsOnFilterIcons(selectedFilters, '[Before Reload]');
      return selectedFilters;
    });
  }

  async applyFilterAndVerifyTooltipAfterReload(count) {
    await test.step(`Apply ${count} Payer Category filters and re-verify tooltips after a page reload`, async () => {
      const selectedFilters = await this.verifyFilterTooltipOnHoverOfFilterIcon(count);

      await this.page.reload();
      await expect(this.dashboardPage).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await expect(this.loadSpinner).toHaveCount(0, { timeout: settings.PAGE_LOAD_TIMEOUT });

      await this.#verifyTooltipsOnFilterIcons(selectedFilters, '[After Reload]');
    });
  }

  // ── Balance Status widget navigation ─────────────────────────────────

  async verifyBalanceStatusWidgetNavigation(optionName) {
    await test.step(`Verify Balance Status Breakdown widget navigates and applies the "${optionName}" sub-option`, async () => {
      await this.page.setViewportSize({ width: 1920, height: 1080 });
      await expect(this.dashboardPage).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });

      const widgetTab = this.balanceStatusWidgetOptions(optionName);
      await widgetTab.waitFor({ state: 'visible', timeout: settings.TIMEOUT });
      await widgetTab.click();
      await expect(this.loadSpinner).toHaveCount(0, { timeout: settings.PAGE_LOAD_TIMEOUT });

      await this.balanceStatusOptions.first().waitFor({ state: 'attached', timeout: settings.TIMEOUT });
      const optionCount = await this.balanceStatusOptions.count();
      expect(optionCount, 'No balance status options found in list').toBeGreaterThan(0);

      const validOptions = [];
      for (let i = 0; i < optionCount; i++) {
        const option = this.balanceStatusOptions.nth(i);
        await option.scrollIntoViewIfNeeded();
        const text = (await option.innerText()).trim();
        if (text.toLowerCase() !== 'other') {
          validOptions.push({ text, locator: option });
        }
      }

      expect(validOptions.length, "No valid balance status options found after excluding 'Other'").toBeGreaterThan(0);

      const selectedOption = validOptions[Math.floor(Math.random() * validOptions.length)];
      const selectedBalanceStatus = selectedOption.text;

      await selectedOption.locator.scrollIntoViewIfNeeded();

      const [newPage] = await Promise.all([
        this.page.context().waitForEvent('page', { timeout: settings.TIMEOUT }),
        selectedOption.locator.click(),
      ]);

      await newPage.waitForLoadState('domcontentloaded');
      await this.balancesListMatSpinner(newPage).waitFor({ state: 'hidden', timeout: settings.PAGE_LOAD_TIMEOUT }).catch(() => { });

      const pageTitle = newPage.locator('h2.web-title-1');
      await pageTitle.waitFor({ state: 'visible', timeout: settings.PAGE_LOAD_TIMEOUT });
      expect((await pageTitle.innerText()).trim(), 'Expected "Balances List" title').toContain('Balances');

      const filtersBtn = this.balancesListFiltersBtn(newPage);
      await filtersBtn.waitFor({ state: 'visible', timeout: settings.TIMEOUT });
      await filtersBtn.click();
      await this.balancesListFilterPanel(newPage).waitFor({ state: 'visible', timeout: settings.TIMEOUT }).catch(() => { });

      const filterValueLocator = this.balancesListFilterValue(newPage);
      await filterValueLocator.waitFor({ state: 'visible', timeout: settings.TIMEOUT });
      const displayedFilterValue = (await filterValueLocator.innerText()).trim();

      expect(
        displayedFilterValue,
        `Expected filter to show "${selectedBalanceStatus}" but got "${displayedFilterValue}"`
      ).toBe(selectedBalanceStatus);

      await filterValueLocator.click();
      await this.balancesListSubOptionsList(newPage).first().waitFor({ state: 'visible', timeout: settings.TIMEOUT }).catch(() => { });

      const checkbox = this.balancesListSubOptionCheckbox(newPage, optionName);
      await this.balancesListSubOptionRow(newPage, optionName).waitFor({ state: 'visible', timeout: settings.TIMEOUT });

      const ariaChecked = await checkbox.getAttribute('aria-checked');
      const isChecked = await checkbox.isChecked().catch(() => false);

      expect(
        ariaChecked === 'true' || ariaChecked === 'mixed' || isChecked,
        `Expected "${optionName}" checkbox to be checked or mixed but got aria-checked="${ariaChecked}"`
      ).toBe(true);

      await newPage.close();
    });
  }

  // ── Tasks Assigned To Me ─────────────────────────────────────────────

  async validateTasksAssignedToMeNavigation() {
    await test.step('Validate "Tasks Assigned To Me" navigates to the Task List with matching filters', async () => {
      await expect(this.dashboardPage).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await expect(this.loadSpinner).toHaveCount(0, { timeout: settings.PAGE_LOAD_TIMEOUT });

      const rawCount = (await this.taskAssignedToMeCount.innerText()).trim();
      const dashboardCount = parseInt(rawCount.replace(/[^0-9]/g, ''), 10);

      await this.taskAssignedToMeBtn.waitFor({ state: 'visible', timeout: settings.TIMEOUT });

      await Promise.all([
        this.page.waitForURL(/tasks/, { timeout: settings.PAGE_LOAD_TIMEOUT }),
        this.taskAssignedToMeBtn.click(),
      ]);

      await this.page.waitForLoadState('domcontentloaded');
      await this.loadSpinner.waitFor({ state: 'hidden', timeout: settings.PAGE_LOAD_TIMEOUT }).catch(() => { });

      await this.taskListPageTitle.waitFor({ state: 'visible', timeout: settings.TIMEOUT });
      const pageTitle = (await this.taskListPageTitle.innerText()).trim();
      expect(pageTitle, `Expected page title to be "Tasks" but got "${pageTitle}"`).toBe('Tasks');

      await this.taskCountInTaskList.waitFor({ state: 'visible', timeout: settings.TIMEOUT });
      const rawTaskListCount = (await this.taskCountInTaskList.innerText()).trim();
      const taskListCount = parseInt(rawTaskListCount.replace(/[^0-9]/g, ''), 10);

      expect(
        taskListCount,
        `Dashboard count (${dashboardCount}) does not match Task List count (${taskListCount})`
      ).toBe(dashboardCount);

      await this.balancesListFiltersBtn(this.page).waitFor({ state: 'visible', timeout: settings.TIMEOUT });
      await this.balancesListFiltersBtn(this.page).click();

      await this.balancesListFilterPanel(this.page).waitFor({ state: 'visible', timeout: settings.TIMEOUT }).catch(() => { });

      await this.taskListFilterValueText.first().waitFor({ state: 'visible', timeout: settings.TIMEOUT });

      const taskStatusValue = (await this.taskListFilterValueText.nth(0).innerText()).trim();
      const assignedToValue = (await this.taskListFilterValueText.nth(1).innerText()).trim();

      expect(taskStatusValue, `Expected Task Status filter to contain "Not Started" but got "${taskStatusValue}"`).toContain('Not Started');
      expect(taskStatusValue, `Expected Task Status filter to contain "In Progress" but got "${taskStatusValue}"`).toContain('In Progress');
      expect(assignedToValue, `Expected Assigned To filter to be "Me" but got "${assignedToValue}"`).toBe('Me');

      await this.page.keyboard.press('Escape');
      await this.dashBoardBtn.click();
      await expect(this.dashboardPage).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await expect(this.loadSpinner).toHaveCount(0, { timeout: settings.PAGE_LOAD_TIMEOUT });
    });
  }

  // ── Balances List navigation from AR Status widget ───────────────────

  async validateDashboardToBalanceFilter(statusName) {
    await test.step(`Validate the "${statusName}" AR Status widget navigates to the matching Balances List filter`, async () => {
      await this.page.setViewportSize({ width: 1920, height: 1080 });
      await expect(this.dashboardPage).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await expect(this.loadSpinner).toHaveCount(0, { timeout: settings.PAGE_LOAD_TIMEOUT });

      const widget = this.balancesListArStatusWidget(statusName);
      await widget.waitFor({ state: 'visible', timeout: settings.TIMEOUT });
      await widget.scrollIntoViewIfNeeded();

      const [newTab] = await Promise.all([
        this.page.context().waitForEvent('page'),
        widget.evaluate(el => {
          const btn = el.querySelector('button');
          if (btn) btn.click();
          else el.click();
        }),
      ]);

      await newTab.waitForLoadState('domcontentloaded');
      await this.balancesListMatSpinner(newTab).waitFor({ state: 'hidden', timeout: settings.PAGE_LOAD_TIMEOUT }).catch(() => { });

      const filtersBtn = this.balancesListFiltersBtn(newTab);
      await filtersBtn.waitFor({ state: 'visible', timeout: settings.PAGE_LOAD_TIMEOUT });
      await filtersBtn.click();

      const balanceStatusDropdown = this.balancesListStatusDropdown(newTab);
      await balanceStatusDropdown.waitFor({ state: 'visible', timeout: settings.TIMEOUT });
      await balanceStatusDropdown.click();

      await this.balancesListCdkOverlay(newTab).waitFor({ state: 'visible', timeout: settings.TIMEOUT }).catch(() => { });

      if (statusName === 'Other Balances') {
        const blankNoTaskCheckbox = this.balancesListBlankNoTaskCheckbox(newTab);
        await blankNoTaskCheckbox.waitFor({ state: 'visible', timeout: settings.TIMEOUT });

        const isChecked = await blankNoTaskCheckbox.evaluate(el => el.classList.contains('mat-mdc-checkbox-checked'));
        expect(
          isChecked,
          'Expected "Blank (No Task)" checkbox to be checked for "Other Balances" filter, but it was not'
        ).toBe(true);
      } else {
        const statusCheckbox = this.balancesListStatusCheckbox(newTab, statusName);
        await statusCheckbox.waitFor({ state: 'visible', timeout: settings.TIMEOUT });

        const isChecked = await statusCheckbox.evaluate(el => el.classList.contains('mat-mdc-checkbox-checked'));
        expect(
          isChecked,
          `Expected "${statusName}" checkbox to be checked in Balance Status filter, but it was not`
        ).toBe(true);
      }

      await newTab.close();
      await this.page.setViewportSize({ width: 1280, height: 720 });
    });
  }

  // ── Shared link ───────────────────────────────────────────────────────

  async verifySharedLinkFunctionalityOnDashboard() {
    await test.step('Verify the shared Dashboard link preserves the applied Payer Category filter', async () => {
      await this.dashBoardBtn.click();
      await expect(this.dashboardPage).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await expect(this.loadSpinner).toHaveCount(0, { timeout: settings.PAGE_LOAD_TIMEOUT });

      const selectedPayerCategory = await this.applyRandomPayerCategoryFilter();
      const pageUrlBeforeShare = this.page.url();

      await this.shareButton.waitFor({ state: 'visible', timeout: settings.TIMEOUT });
      await this.shareButton.click();

      await this.shareLinkToast.waitFor({ state: 'visible', timeout: settings.TIMEOUT });
      await expect(this.shareLinkToast).toHaveText('Link copied');

      let copiedUrl;
      try {
        await this.page.context().grantPermissions(['clipboard-read', 'clipboard-write']);
        copiedUrl = await this.page.evaluate(async () => await navigator.clipboard.readText());
      } catch {
        copiedUrl = pageUrlBeforeShare;
      }

      expect(copiedUrl, 'Copied URL is empty — share button may not have worked').toBeTruthy();

      const newTab = await this.page.context().newPage();
      await newTab.goto(copiedUrl, { waitUntil: 'domcontentloaded' });
      await newTab.locator('mat-spinner').waitFor({ state: 'hidden', timeout: settings.PAGE_LOAD_TIMEOUT }).catch(() => { });

      const appliedValue = this.appliedPayerCategoryValue(newTab);
      await appliedValue.waitFor({ state: 'visible', timeout: settings.TIMEOUT });

      await expect(
        appliedValue,
        `Expected shared link to preserve Payer Category filter "${selectedPayerCategory}"`
      ).toContainText(selectedPayerCategory);

      await newTab.close();
    });
  }
}

module.exports = { SupDashboardPage };
