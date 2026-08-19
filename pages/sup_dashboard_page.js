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
    this.dashboardPage = page.locator("//arw-dashboard[@class='arw-page ng-star-inserted']");
    this.loadSpinner = page.locator("//mat-spinner[@role='progressbar']");

    // ── Tasks Worked / Task Updates widgets ──────────────────────────────
    this.tasksWorkedNoData = page.locator("//arw-tasks-worked-widget//div[normalize-space(text())='No Data']");
    this.taskUpdatesNoData = page.locator("//arw-task-updates-widget//div[normalize-space(text())='No Data']");
    this.taskUpdateAvatarToolpits = page.locator("//arw-task-updates-widget//arw-avatar");
    this.taskWorkedAvatarToolpits = page.locator("//arw-tasks-worked-widget//arw-avatar");
    this.taskUpdateWidget = page.locator('//arw-task-updates-widget');
    this.taskUpdateCanvas = page.locator("//arw-task-updates-widget//canvas");
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
    this.arStatusValues = page.locator(
      "//arw-ar-status-widget//div[contains(@class,'font-bold') and contains(@class,'justify-end')]"
    );
    this.arStatusTotal = page.locator(
      "//arw-ar-status-widget//div[contains(@class,'flex justify')]//span[contains(@class,'font-bold')]"
    );
    this.payerCategoryDropdown = page.locator("//arw-ar-status-widget//arw-select-tree[@mode='dropdown']//button");
    this.balanceStatusPayerCategoryDropdown = page.locator(
      "//arw-balance-status-widget//arw-select-tree[@mode='dropdown']//button"
    );

    // ── Payer category dropdown / options ─────────────────────────────────
    this.payerCategoriesDropDownOptions = page.locator("//div[@class='cdk-virtual-scroll-content-wrapper ng-scroll-content']//span");
    this.applyBtn = page.locator("//span[normalize-space()='Apply']");
    this.payerCategoryCheckboxes = page.locator(
      "//div[contains(@class,'cdk-virtual-scroll-content-wrapper')]//mat-checkbox"
    );
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
    this.filterIcons = page.locator("//arw-icon[@name='filterFunnel01']");
    this.balanceStatusWidgetOptions = (optionName) => page.locator(
      `//button[@role='radio'][.//span[normalize-space()='${optionName}']]`
    );
    this.balanceStatusOptions = page.locator(
      "//div[contains(@class,'flex') and contains(@class,'justify-center') and contains(@class,'ng-star-inserted')]//button"
    );
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
      const checkbox = this.payerCategoryCheckboxes.filter({ hasText: categoryName }).first();
      await expect(checkbox).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await checkbox.click();
    });
  }

  async isPayerCategorySelected(categoryName) {
    return test.step(`Verify Payer Category "${categoryName}" checkbox is checked`, async () => {
      const checkbox = this.payerCategoryCheckboxes.filter({ hasText: categoryName }).first();
      return checkbox.locator('input.mdc-checkbox__native-control').isChecked();
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
}

module.exports = { SupDashboardPage };
