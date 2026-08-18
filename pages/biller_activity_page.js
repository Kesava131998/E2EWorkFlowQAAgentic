const { test } = require('@playwright/test');
const { BasePage } = require('./base_page');
const { settings } = require('../config/settings');

/**
 * Page object for the Biller Activity Report (converted from billerActivityReport.js /
 * pages/biller_activity_page.py). Only locators and simple actions are ported here — the
 * original file's complex validation/business-logic methods (Excel diffing, sort-order
 * math, API-response checks, drag-and-drop column reorder, etc.) belong in spec files as
 * assertions built on top of these locators, not in the page object.
 */
class BillerActivityPage extends BasePage {
  constructor(page) {
    super(page);

    this.billerActivityReportBtn = page.locator(
      "//arw-side-nav-node//span[normalize-space(text())='Activity Report']"
    );
    this.settingsButton = page.locator("//span[normalize-space()='Settings']");
    this.userManagementOption = page.locator("//span[text()=' User Management ']");
    this.selectUserDropdown = page.locator("//span[normalize-space(text())='Select Users']");
    this.selectRolesDropdown = page.locator("//span[normalize-space(text())='Select Roles']");
    this.allUsers = page.locator('//mat-checkbox//label');
    this.overdueColumn = page.locator(
      "//div[contains(@class,'arw-grid-table__cell ng-star-inserted')]" +
        "[@data-column-definition-name='overdueOpenBalanceTaskCount']//span//a"
    );
    this.taskHeader = page.locator("//h2[normalize-space(text())='Tasks']");
    this.userNames = page.locator(
      "//div[contains(@class,'overflow-hidden text-ellipsis')]//span[contains(@class,'overflow-ellipsis')]"
    );
    this.searchUser = page.locator("//input[@placeholder='Search']");
    this.applyButton = page.locator("//span[normalize-space(text())='Apply']");
    this.userNameInGrid = page.locator("[data-column-definition-name='user'] span.web-body-2");
    this.filterButton = page.locator("//span[normalize-space(text())='Filters']");
    this.filterByText = page.locator("//div[normalize-space(text())='Filter by']");
    this.selectedFilters = page.locator(
      "//arw-grid-filter[@class='flex overflow-hidden grow w-full ng-untouched ng-pristine ng-valid ng-star-inserted']//button"
    );
    this.clearSelectedRoles = page.locator("//arw-icon[@name='x']");
    this.workedLastXDaysValues = page.locator(
      "//div[@data-column-definition-name='workedLastXDays']//span//span"
    );
    this.updatedLastXDaysValues = page.locator(
      "//div[@data-column-definition-name='updatedLastXDays']//span//span"
    );
    this.timePeriodDropdown = page.locator("//div[@class='mat-mdc-select-trigger']");
    this.billerActivityGridNames = page.locator(
      "//div[contains(@class,'cdk-drag') and contains(@class,'arw-grid-table__header-cell')]"
    );
    this.loadSpinner = page.locator("//mat-spinner[@role='progressbar']");
    this.excelDownloadButton = page.locator("//button[.//arw-icon[@name='download01']]");
    this.uiColumnHeaders = page.locator(
      "//div[contains(@class,'arw-grid-table__header')]//div[contains(@class,'text-ellipsis')]"
    );
    this.excelDownloadIconButton = page.locator("//arw-icon[contains(@name,'download')]/parent::button");
    this.gridRows = page.locator('div.arw-grid-table__row');
    this.userNameCell = page.locator("//arw-grid-table//span[contains(@class,'web-body-2 ng-star')]");
    this.userMailCell = page.locator("//arw-grid-table//div[contains(@class,'web-body-3 ng-star-inserted')]");
    this.userNameAndEmailCell = page.locator(
      "//arw-grid-table//div[contains(@class,'arw-grid-table__cell ng-star')][@data-column-definition-name='user']"
    );
    this.facilityCountsCell = page.locator(
      "//div[contains(@class,'arw-grid-table__cell')][@data-column-definition-name='facilities']"
    );
    this.facilityNamesCell = page.locator(
      "//div[contains(@class,'arw-grid-table__cell')][@data-column-definition-name='facilityHierarchyId']"
    );
    this.facilityAndRoleViewButton = page.locator("//div[text()=' FACILITY & ROLE VIEW ']");
    this.selectUsersDropdown = page.locator('arw-select-tree').filter({ hasText: 'Users' }).locator('button').first();
    this.clearButton = page.locator("//div[contains(@class,'flex items-baseline')]/button");
    this.searchInputBox = page.locator("//input[@placeholder='Search']");
    this.crossButton = page.locator("//arw-grid-filter//button//arw-icon[@name='x']");
    this.refreshDataButton = page.locator("//arw-button[@iconright='refreshCw01']");
    this.reportCards = page.locator("//arw-activity-report-cards//div[contains(@class,'grow overflow-hidden text')]");
    this.tooltipText = page.locator("//arw-tooltip-overlay//div[contains(@class,'web-body-1')]");
    this.shareButton = page.locator('arw-button[icon="share07"] button');
    this.shareLinkToast = page.locator('arw-toast span.web-body-1.text-foreground-high');
    this.userManagementFirstRow = page.locator(
      "//div[contains(@class,'shadow-m arw-grid-table__row--clickable arw-grid-table__row')]"
    );
    this.userRoleNameCells = page.locator(
      "//div[contains(@class,'arw-grid-table__cell')][@data-column-definition-name='roleName']" +
        "//div[@class='flex flex-col overflow-hidden']"
    );
    this.backButton = page.locator("//arw-button[@icon='chevronLeft']");
    this.userDropdownItems = page.locator(
      "//cdk-virtual-scroll-viewport//div[contains(@class,'overflow-hidden')]//arw-chip//span"
    );
    this.noUsersFoundMessage = page.getByText('No users found');
    this.virtualScrollViewport = page.locator('ng-scrollbar.cdk-virtual-scrollable').first();
    this.gridRowWrapper = page.locator('div.arw-grid-table__row-wrapper.ng-star-inserted');
    this.firstRowUserName = page
      .locator('div.arw-grid-table__row')
      .first()
      .locator("[data-column-definition-name='user'] span.web-body-2.ng-star-inserted");
    this.firstRowUserRole = page
      .locator('div.arw-grid-table__row')
      .first()
      .locator("[data-column-definition-name='user'] div.text-foreground-medium");
    this.firstRowTasksWorkedCell = page
      .locator('div.arw-grid-table__row')
      .locator("[data-column-definition-name='tasksWorkedTodayPercent'] button");
    this.taskCompletionDialog = page.locator('mat-dialog-container');
    this.taskCompletionDialogTitle = page.locator('mat-dialog-container div.web-title-3.\\!font-bold');
    this.taskCompletionDialogSubtitle = page.locator('mat-dialog-container div.web-body-1.text-foreground-medium');
    this.userGridRow = page.locator(
      "//div[contains(@class,'arw-grid-table__cell ng-star-inserted')][@data-column-definition-name='lastName']"
    );
    this.userManagementBackButton = page.locator("//arw-button[@icon='chevronLeft']");
    this.facilityUsersGrid = page.locator("//div[contains(@class,'cdk-drag arw-grid-table__header-cell')]");
    this.facilityRolesGridColumns = page.locator(
      "//div[@data-column-definition-name='roleId']//div[@class='overflow-hidden text-ellipsis']"
    );

    // Column metadata used by sort/export validations (kept as data, not a locator)
    this.billerActivityColumns = [
      { key: 'facilities', label: 'Facilities', type: 'number' },
      { key: 'overdueOpenBalanceTaskCount', label: 'Overdue Open Balance Tasks', type: 'number' },
      { key: 'overdueOverpaymentTaskCount', label: 'Overdue Overpayment Tasks', type: 'number' },
      { key: 'dueTodayCount', label: 'Due Today', type: 'number' },
      { key: 'lastActivity', label: 'Last Activity', type: 'activity' },
    ];
  }

  // ── Parameterized locators ──────────────────────────────────────────────

  randomUserName(user) {
    return this.page.locator(
      `//div[@class='cdk-virtual-scroll-content-wrapper ng-scroll-content']//span[normalize-space(text())='${user}']`
    );
  }

  gridColumnValues(columnName) {
    return this.page.locator(`//div[@data-column-definition-name='${columnName}']//span//a`);
  }

  roleOption(role) {
    return this.page.locator(`//span[normalize-space(text())='${role}']`);
  }

  metricValue(label) {
    return this.page.locator(
      `//div[normalize-space()='${label}']/following::div[contains(@class,'web-title-1')][1]`
    );
  }

  timePeriodOption(days) {
    return this.page.locator(`//div[normalize-space(text())='${days}']`);
  }

  gridHeader(sortName) {
    return this.page.locator(
      `//div[contains(@class,'cdk-drag arw-grid-table__header-cell') and @data-column-definition-name='${sortName}']`
    );
  }

  userSortButton(column) {
    return this.page.locator(`((//div[@data-column-definition-name='${column}'])[1]//arw-header-cell//div)[5]`);
  }

  sortButton(column) {
    return this.page.locator(`(//div[@data-column-definition-name='${column}'])[1]//button//*[name()='svg']`);
  }

  columnValues(column) {
    return this.page.locator(`//div[@data-column-definition-name='${column}']//arw-template-renderer`);
  }

  reportColumnCells(column) {
    return this.page.locator(`//div[@data-column-definition-name='${column}']/arw-template-renderer`);
  }

  columnPercentageValues(columnName) {
    return this.page.locator(
      `//div[@data-column-definition-name='${columnName}']//span[contains(@class,'web-body-2')]`
    );
  }

  taskWorkedTodayContainer() {
    return this.page.locator(
      "//div[@data-column-definition-name='tasksWorkedTodayPercent']//div[contains(@class,'flex flex-col gap-4')]"
    );
  }

  taskWorkedPercentage(row) {
    return row.locator("[data-column-definition-name='tasksWorkedTodayPercent'] span.web-body-2");
  }

  taskWorkedPercent(row) {
    return row.locator("[data-column-definition-name='tasksWorkedTodayPercent'] span.web-body-2");
  }

  taskWorkedRatio(row) {
    return row.locator("[data-column-definition-name='tasksWorkedTodayPercent'] span.web-body-3");
  }

  reportCardInfoButton(cardName) {
    return this.page.locator(
      `arw-activity-report-cards//div[normalize-space()='${cardName}']//arw-icon[@name='infoCircle']`
    );
  }

  clearSelectedFilterButton(filterName) {
    return this.page.locator(
      `//button[.//div[contains(normalize-space(),'${filterName}')]]//button[contains(@class,'arw-select__clear')]`
    );
  }

  // ── Simple actions ──────────────────────────────────────────────────────

  async clickBillerActivityReport() {
    await test.step('Click on Biller Activity Report nav link', async () => {
      await this.billerActivityReportBtn.click();
    });
  }

  async clickSettingsButton() {
    await test.step('Click on Settings button', async () => {
      await this.settingsButton.click();
    });
  }

  async clickUserManagementOption() {
    await test.step('Click on User Management option', async () => {
      await this.userManagementOption.click();
    });
  }

  async clickSelectUserDropdown() {
    await test.step('Click on Select Users dropdown (report filter)', async () => {
      await this.selectUserDropdown.click();
    });
  }

  async clickSelectUsersDropdown() {
    await test.step('Click on Select Users dropdown (user management)', async () => {
      await this.selectUsersDropdown.click();
    });
  }

  async clickSelectRolesDropdown() {
    await test.step('Click on Select Roles dropdown', async () => {
      await this.selectRolesDropdown.click();
    });
  }

  async clickApplyButton() {
    await test.step('Click on Apply button', async () => {
      await this.applyButton.click();
    });
  }

  async clickFilterButton() {
    await test.step('Click on Filters button', async () => {
      await this.filterButton.click();
    });
  }

  async clickOverdueColumn() {
    await test.step('Click on Overdue column in grid', async () => {
      await this.overdueColumn.click();
    });
  }

  async clickClearRolesDropdown() {
    await test.step('Click on X button to clear selected roles', async () => {
      await this.clearSelectedRoles.click();
    });
  }

  async clickTimePeriodDropdown() {
    await test.step('Click on Time Period dropdown', async () => {
      await this.timePeriodDropdown.click();
    });
  }

  async clickFacilityAndRoleViewButton() {
    await test.step('Click on Facility & Role View button', async () => {
      await this.facilityAndRoleViewButton.click();
    });
  }

  async clickUserSortButton(column) {
    await test.step(`Click on user sort button for ${column}`, async () => {
      await this.userSortButton(column).click();
    });
  }

  async clickSortButton(column) {
    await test.step(`Click on sort button for ${column}`, async () => {
      await this.sortButton(column).click();
    });
  }

  async hoverGridHeader(sortName) {
    await test.step(`Hover over grid header for ${sortName}`, async () => {
      await this.gridHeader(sortName).hover();
    });
  }

  async selectUserName(user) {
    await test.step(`Select user ${user} from dropdown`, async () => {
      await this.randomUserName(user).click();
    });
  }

  async waitForReportLoaded(timeout = settings.PAGE_LOAD_TIMEOUT) {
    await this.reportColumnCells('user').first().waitFor({ state: 'visible', timeout });
  }

  async clearSelectedFilter(clearButton, timeout = settings.PAGE_LOAD_TIMEOUT) {
    await test.step('Clear selected filter if visible', async () => {
      if (await clearButton.isVisible()) {
        await clearButton.click();
        await this.loadSpinner.waitFor({ state: 'hidden', timeout });
      }
    });
  }
}

module.exports = { BillerActivityPage };
