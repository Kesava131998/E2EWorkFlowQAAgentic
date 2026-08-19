const { test } = require('@playwright/test');
const { BasePage } = require('./base_page');
const { settings } = require('../config/settings');

/**
 * Page object for the RevFlow Dashboard (converted from dashborad.js /
 * pages/dashboard_page.py). Only locators and simple actions are ported here — the
 * original file's complex validation/business-logic methods (widget tooltip
 * validation loops, AR-status/highest-balance total math, cross-tab navigation +
 * comparison flows, API status checks per payer category, filter-tooltip
 * verification, shared-link validation, etc.) belong in spec files as assertions
 * built on top of these locators, not in the page object.
 */
class DashboardPage extends BasePage {
  constructor(page) {
    super(page);

    this.taskListModuleCard = page.locator("(//div[@class='module-card'])[1]");
    this.agingModuleCard = page.locator("(//div[@class='module-card'])[2]");
    this.dashboardContainer = page.locator("//arw-dashboard[@class='arw-page ng-star-inserted']");
    this.tasksWorkedNoData = page.locator("//arw-tasks-worked-widget//div[normalize-space(text())='No Data']");
    this.taskUpdatesNoData = page.locator("//arw-task-updates-widget//div[normalize-space(text())='No Data']");
    this.taskUpdateAvatarTooltips = page.locator("//arw-task-updates-widget//arw-avatar");
    this.taskWorkedAvatarTooltips = page.locator("//arw-tasks-worked-widget//arw-avatar");
    this.taskUpdateWidget = page.locator('//arw-task-updates-widget');
    this.taskUpdateCanvas = page.locator("//arw-task-updates-widget//canvas");
    this.timePeriod = page.locator("(//div[@class='mat-mdc-select-trigger'])[1]");
    this.allTaskWorkedMartins = page.locator("//div[@class='flex gap-20 mt-8']");
    this.taskWorkedMartins = page.locator("//div[@class='flex gap-20 mt-8']//div//div");
    this.highestBalancesLabel = page.locator("//div[normalize-space(text())='Highest Balances']");
    this.balanceLabels = page.locator(
      "//arw-highest-balances-widget//ng-scrollbar//div[contains(@class,'flex py-4')]/div[4]"
    );
    this.unworkedTasksLabel = page.locator("//div[normalize-space(text())='Unworked Tasks']");
    this.unworkedTasksResidentNameLinks = page.locator(
      "(//div[normalize-space(text())='Resident'])[2]/following::a"
    );
    this.viewAgingButton = page.locator("//arw-button[@category='secondary']");
    this.loadSpinner = page.locator("//mat-spinner[@role='progressbar']");
    this.arStatusValues = page.locator(
      "//arw-ar-status-widget//div[contains(@class,'font-bold') and contains(@class,'justify-end')]"
    );
    this.dropdownOptions = page.locator(
      "//div[@class='cdk-virtual-scroll-content-wrapper ng-scroll-content']//span"
    );
    this.applyBtn = page.locator("//span[normalize-space()='Apply']");
    this.payerCategoryDropdown = page.locator(
      "//arw-ar-status-widget//arw-select-tree[@mode='dropdown']//button"
    );
    this.balanceStatusPayerCategoryDropdown = page.locator(
      "//arw-balance-status-widget//arw-select-tree[@mode='dropdown']//button"
    );
    this.payerCategoryCheckboxes = page.locator(
      "//div[contains(@class,'cdk-virtual-scroll-content-wrapper')]//mat-checkbox"
    );
    this.facilityName = page.locator("(((//div[@class='flex flex-col px-8'])[2]//div)[1]//div)[1]");
    this.residentName = page.locator("(((//div[@class='flex flex-col px-8'])[2]//div)[1]//div)[2]");
    this.payerName = page.locator("(((//div[@class='flex flex-col px-8'])[2]//div)[1]//div)[3]");
    this.dueDate = page.locator("(((//div[@class='flex flex-col px-8'])[2]//div)[1]//div)[4]");
    this.balance = page.locator("(((//div[@class='flex flex-col px-8'])[2]//div)[1]//div)[5]");
    this.assigneeName = page.locator("(((//div[@class='flex flex-col px-8'])[2]//div)[1]//div)[6]");
    this.serviceDate = page.locator("(((//div[@class='flex flex-col px-8'])[2]//div)[1]//div)[7]");
    this.viewTaskBtn = page.locator("(((//div[@class='flex flex-col px-8'])[2]//div)[1]//div)[8]//button");
    this.facilityLocator = page.locator(
      "//span[normalize-space(text())='Facility']/ancestor::div[contains(@class,'items-center')]"
    );
    this.residentLocator = page.locator(
      "//span[normalize-space(text())='Resident']/ancestor::div[contains(@class,'items-center')]"
    );
    this.payerLocator = page.locator(
      "//span[normalize-space(text())='Payer']/ancestor::div[contains(@class,'items-center')]"
    );
    this.balanceLocator = page.locator('span.font-bold.mr-4');
    this.taskListDueDateInput = page.locator("arw-input[formcontrolname='dueDate'] input.mat-datepicker-input");
    this.taskListAssignedTo = page.locator(
      "(//span[@class='grow overflow-ellipsis overflow-hidden text-center whitespace-nowrap'])[1]"
    );
    this.taskCloseBtn = page.locator("//div[@class='flex gap-8 items-center shrink-0']//arw-button[@icon='x']");
    this.chargesServiceDates = page.locator(
      "(//ng-scrollbar[@class='arw-grid-table__body ng-scroll-viewport ng-scrollbar ng-star-inserted'])[1]//div[@data-column-definition-name='serviceDates']"
    );
    this.chargesLabel = page.locator("(//span[@class='mdc-tab__text-label'])[2]");
    this.payerCategoriesDropdown = page.locator(
      "//arw-dashboard-header//arw-select-tree[@mode='dropdown']//button"
    );
    this.arStatusTotal = page.locator(
      "//arw-ar-status-widget//div[contains(@class,'flex justify')]//span[contains(@class,'font-bold')]"
    );
    this.billerActivityReportBtn = page.locator("//arw-side-nav-node//span[normalize-space()='Activity Report']");
    this.dashboardNavButton = page.locator("//arw-side-nav-node//span[normalize-space()='Dashboard']");

    // ── balancesList locators ──
    this.balancesListHighestBalancesRows = page.locator(
      "//arw-highest-balances-widget//ng-scrollbar//div[contains(@class,'ng-star-inserted')]"
    );
    this.balancesListFilterValueText = page.locator('div.arw-control-btn__value');
    this.taskAssignedToMeBtn = page.locator("//a[contains(@href,'/tasks?assignedTo') and contains(@href,'statusIds')]");
    this.taskAssignedToMeCount = this.taskAssignedToMeBtn.locator("//span[contains(@class,'web-subtitle')]");
    this.taskCountInTaskList = page.locator("//arw-grid-table//span[contains(@class,'web-body')]");
    this.taskListPageTitle = page.locator('h2.web-title-1');
    this.taskListFilterValueText = page.locator('div.arw-control-btn__value');
    this.balancesListTotalBalanceAmount = page.locator(
      "//span[normalize-space(text())='Total Balance Amount:']/following-sibling::b"
    );
    this.shareButton = page.locator('arw-button[icon="share07"] button');
    this.shareLinkToast = page.locator('arw-toast span.web-body-1.text-foreground-high');
    this.filterIcons = page.locator("//arw-icon[@name='filterFunnel01']");
    this.balanceStatusOptions = page.locator(
      "//div[contains(@class,'flex') and contains(@class,'justify-center') and contains(@class,'ng-star-inserted')]//button"
    );

    // Column metadata used by tooltip validations (kept as data, not a locator)
    this.dashboardTooltipWidgets = [
      'AR Status',
      'Balance Status Breakdown',
      'Overdue Tasks',
      'Task Updates',
      'Tasks Worked',
      'Highest Balances',
      'Unworked Tasks',
    ];
  }

  // ── Parameterized locators ──────────────────────────────────────────────

  timePeriodOption(days) {
    return this.page.locator(`//div[normalize-space(text())='${days}']`);
  }

  dashboardTooltip(txt) {
    return this.page.locator(
      `//div[contains(@class,'web-title-3') and contains(normalize-space(.),'${txt}')]//arw-icon`
    );
  }

  balancesListArStatusWidget(statusName) {
    return this.page.locator(
      `//arw-ar-status-widget//div[contains(@class,'flex items-center')][.//button[normalize-space()='${statusName}']]`
    );
  }

  balancesListArStatusWidgetDot(statusName) {
    return this.page.locator(
      `//arw-ar-status-widget//div[contains(@class,'flex items-center')][.//button[normalize-space()='${statusName}']]//div[contains(@class,'rounded-full')]`
    );
  }

  balancesListMatSpinner(tab) {
    return tab.locator('mat-spinner');
  }

  balancesListFiltersBtn(tab) {
    return tab.locator("//span[normalize-space(text())='Filters']");
  }

  balancesListStatusDropdown(tab) {
    return tab
      .locator("//arw-select-tree[contains(@formcontrolname,'value')] | //button[contains(@class,'arw-control-btn')]")
      .first();
  }

  balancesListCdkOverlay(tab) {
    return tab.locator('.cdk-overlay-pane');
  }

  balancesListStatusCheckbox(tab, statusName) {
    return tab.locator(`//div[normalize-space()='${statusName}']/preceding-sibling::mat-checkbox`);
  }

  balancesListBlankNoTaskCheckbox(tab) {
    return tab.locator("//div[normalize-space()='Blank (No Task)']/preceding-sibling::mat-checkbox");
  }

  balancesListHighestBalancesFacility(row) {
    return row.locator('div').nth(0);
  }

  balancesListHighestBalancesResident(row) {
    return row.locator("a[href*='/cases/details']").first();
  }

  balancesListHighestBalancesPayer(row) {
    return row.locator('div').nth(2);
  }

  balancesListHighestBalancesBalanceLink(row) {
    return row.locator("a[href*='/balances']").first();
  }

  balancesListFilterPanel(tab) {
    return tab.locator("//div[normalize-space(text())='Filter by']");
  }

  appliedPayerCategoryValue(tab) {
    return tab.locator(
      "//arw-dashboard-header//arw-select-tree[@mode='dropdown']//button//div[contains(@class,'arw-control-btn__value')]"
    );
  }

  balanceStatusWidgetOptions(optionName) {
    return this.page.locator(`//button[@role='radio'][.//span[normalize-space()='${optionName}']]`);
  }

  balancesListFilterValue(p) {
    return p.locator('div.arw-control-btn__value');
  }

  balancesListSubOptionsList(p) {
    return p.locator('mat-option, .mat-mdc-option, div.mdc-checkbox');
  }

  balancesListSubOptionRow(p, optionName) {
    return p
      .locator(
        `//mat-option[.//span[normalize-space()='${optionName}']] | //div[contains(@class,'ng-star-inserted')][.//span[normalize-space()='${optionName}']]`
      )
      .first();
  }

  balancesListSubOptionCheckbox(p, optionName) {
    return this.balancesListSubOptionRow(p, optionName).locator("input.mdc-checkbox__native-control").first();
  }

  // ── Simple actions ──────────────────────────────────────────────────────

  async hoverOnDashboardTooltip(txt) {
    await test.step(`Hover over dashboard tooltip icon for ${txt}`, async () => {
      await this.dashboardTooltip(txt).hover();
    });
  }

  async clickOnTaskCloseBtn() {
    await test.step('Click task slide-out close button', async () => {
      await this.taskCloseBtn.click();
    });
  }

  async clickOnTimePeriodDropdown() {
    await test.step('Click on Time Period dropdown', async () => {
      await this.timePeriod.click();
    });
  }

  async navigateToDashboard(timeout = settings.PAGE_LOAD_TIMEOUT) {
    await test.step('Navigate to Dashboard via side nav and wait for it to load', async () => {
      await this.dashboardNavButton.click();
      await this.dashboardContainer.waitFor({ state: 'visible', timeout });
      await this.loadSpinner.waitFor({ state: 'hidden', timeout }).catch(() => {});
    });
  }
}

module.exports = { DashboardPage };
