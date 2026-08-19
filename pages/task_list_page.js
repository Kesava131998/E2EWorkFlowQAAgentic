const { test } = require('@playwright/test');
const { BasePage } = require('./base_page');
const { settings } = require('../config/settings');

/**
 * Page object for the Task List page (converted from taskList.js / pageObjects/UI_Pages/taskList.js).
 * Only locators and simple actions are ported here — the original file's complex validation/
 * business-logic methods (filter/sort/column-reorder verification loops, Excel/API diffing,
 * payment-schedule CRUD flows, comment-thread lifecycle checks, calendar/date-math validation,
 * drag-and-drop reordering, activity-log assertions, etc.) belong in spec files as assertions
 * built on top of these locators, not in the page object.
 *
 * A handful of source methods referenced locators that were never defined in the source file's
 * constructor (`deleteDueDateFilterIcon`, `deleteBalanceFilterIcon`) — those dead-code methods
 * were not ported since there is no real selector to copy verbatim.
 *
 * Where the source defined the exact same selector string under two different property names
 * (e.g. `residentNameBox` / `residentNameLink`, `customSortBtn` / `sortBtn`, `calendar` /
 * `calendarView`, `downArrow` / `downArrowBtn`, `closeBtn` / `clearCaseSearchBtn`, the two
 * checkbox-by-index locators, the three `input[placeholder='Search']` locators, and
 * `shareLinkToast` / `toastMessage`), only one property was kept and reused.
 */
class TaskListPage extends BasePage {
  constructor(page) {
    super(page);

    // ── Filters ──────────────────────────────────────────────────────────
    this.filterBtn = page.locator("//span[normalize-space(text())='Filters']");
    this.selectedFilter = page.locator(
      "//div[@class='flex gap-8 overflow-hidden grow ng-untouched ng-pristine ng-valid ng-star-inserted']"
    );
    this.dueDateDropDown = page.locator("(//mat-select[@role='combobox' ])[1]");
    this.taskStatusDropDown = page.locator("(//mat-select[@role='combobox' ])[2]");
    this.assignedToDropDown = page.locator(
      "//arw-task-details//arw-select[@formcontrolname='assigneeId']//arw-label"
    );
    this.defaultOptionInDueDate = page.locator("//arw-select-tree[@formcontrolname='operator']");
    this.overdueCheckBox = page.locator("(//input[@type='checkbox'])[1]");
    this.todayCheckBox = page.locator("(//input[@type='checkbox'])[2]");
    this.defaultOptionInTaskStatus = page.locator("//arw-select-tree[@formcontrolname='value']");
    this.clearFilter = page.locator("//span[text()=' Clear Filter ']");
    this.disableModeClearbtn = page.locator(
      "//div[text()='Filter by']/following-sibling::arw-button[@category='tertiary']//button"
    );
    this.selectResidentDropDown = page.locator("//span[contains(text(),'Select Resident')]");
    this.applyFilterBtn = page.locator("//span[contains(text(),'Apply Filter')]");
    this.clearAssignedToFilter = page.locator("(//arw-icon[@name='x'])[3]");
    this.deleteSortIcon = page.locator(
      "(//arw-button[@icon='trash03']//button[contains(@class,'arw-button--small arw-button--tertiary')])[1]"
    );
    this.deleteBalanceInSort = page.locator(
      "(//button[@class='arw-button arw-button--neutral arw-button--small arw-button--tertiary arw-button--icon-only'])[2]"
    );
    this.applySortButton = page.locator("//span[text()=' Apply Sort ']/ancestor::arw-button");
    this.residentHeader = page.locator("//div[normalize-space(text()) = 'Resident']");
    this.gridFilterIcon = page.locator(
      "(//div[normalize-space(text()) = 'Resident']//../../..//*[name()='svg'])[1]"
    );
    this.searchInputBox = page.locator("//input[@placeholder='Search']");
    this.applyButton = page.locator("//span[normalize-space(text())='Apply']");
    this.facilityNameBox = page.locator("((//div[@data-column-definition-name='facility'])[2]//span)[2]");
    this.residentNameLink = page.locator("(//div[@data-column-definition-name='caseDetails'])[2]//a");
    this.viewAgingButton = page.locator("//arw-button[@category='secondary']");
    this.viewTaskListButton = page.locator(
      "//arw-button[@category='secondary']/following-sibling::arw-button"
    );
    this.appliedFilter1 = page.locator(
      "(//div[contains(@class,'web-body-1 text-foreground-high grow overflow-hidden')])[1]"
    );
    this.appliedFilter2 = page.locator(
      "(//div[contains(@class,'web-body-1 text-foreground-high grow overflow-hidden')])[2]"
    );
    this.downArrow = page.locator("//arw-icon[@name='arrowNarrowDown']");
    this.firstGroup = page.locator("//span[text()='Achieve']");
    this.filtersDropDown = page.locator("//span[text()=' Filters ']/ancestor::arw-grid-header-filters");
    this.firstFilter = page.locator("//div[@class='mat-mdc-select-value']");
    this.firstFilterInput = page.locator(
      "//arw-select-tree//button[@aria-haspopup='menu']//div[contains(@class,'arw-select-tree__value')]"
    );
    this.hoverOut = page.locator("//div[contains(@class,'cdk-overlay-backdrop')]");
    this.caseSearchInput = page.locator("//input[@placeholder='Search for a Case']");

    // ── Case search / Case view ─────────────────────────────────────────
    this.residentDob = page.locator("(//span[text()='DOB'])[1]/following-sibling::span");
    this.residentSSNNumber = page.locator("(//span[text()='SSN'])[1]/following-sibling::span");
    this.billingSystemId = page.locator("(//span[text()='Billing System ID'])[1]/following-sibling::span");
    this.billingSystemType = page.locator("(//span[text()='Billing System ID'])[1]/following-sibling::div");
    this.residentFacilityName = page.locator("//span[contains(@class,'flex items-center gap-2')]//span");
    this.caseViewResidentName = page.locator("//span[contains(@class, 'web-title-2')]");
    this.caseViewResidentFacility = page.locator("//div[contains(@class, 'web-title-2')]");
    this.caseViewBillingSystemId = page.locator(
      "//span[normalize-space(text())='Billing System ID']/ancestor::div[contains(@class,'arw-control')]"
    );
    this.caseViewDob = page.locator(
      "//span[normalize-space(text())='DOB']/ancestor::div[contains(@class,'arw-control')]"
    );
    this.caseViewSSNNumber = page.locator(
      "//span[normalize-space(text())='SSN']/ancestor::div[contains(@class,'arw-control')]"
    );
    this.caseViewBillingSystemType = page.locator("(//div[contains(@class, 'text-foreground-medium')])[2]");
    this.residentNameInSearchList = page.locator("//span[contains(@class,'web-subtitle-1')]//span");
    this.closeIconBtn = page.locator("//arw-icon[@name='x']");
    this.residentOptionList = page.locator(
      "(//div[@role='link']//span[contains(@class,'text-foreground-blue')])[1]"
    );

    // ── Global facility filter ───────────────────────────────────────────
    this.globalFacilityDropdown = page.locator("//button[contains(text(),'Selected Facilities')]");
    this.globalFacilityCheckboxes = page.locator("cdk-virtual-scroll-viewport mat-checkbox:not(:has-text('All'))");
    this.globalFacilityClearBtn = page.locator("//div[contains(@class,'flex items-baseline')]//button");
    this.selectAllBtn = page.locator("//label[contains(text(),'All')]");

    // ── Add Filter flow ───────────────────────────────────────────────────
    this.addFilterBtn = page.locator("//span[normalize-space(text())='Add Filter']");
    this.addFilterDropdown = page.locator("//span[text()='Select']");
    this.selectFiltersOptions = (txt) =>
      page.locator(`//div[@class='py-12']//div[normalize-space(text())='${txt}']`);
    this.taskNameSearchInput = page.locator("(//input)[2]");
    this.filterDropdownSearch = page.locator(
      "//div[contains(@class,'cdk-overlay-pane')]//input[@placeholder='Search']"
    );
    this.taskNameGridRow = page.locator(
      "(//div[@class='arw-grid-table__row-wrapper ng-star-inserted']//div[@data-column-definition-name='taskId'])[1]"
    );
    this.noTaskFound = page.locator("//div[text()='No tasks found']");
    this.customSortBtn = page.locator("//arw-grid-custom-sort//button");
    this.clearFilterOnNoTaskFoundScreen = page.locator("//span[text()='Clear filters']");
    this.editFilterOnNoTaskFoundScreen = page.locator("//span[text()='Edit Filters']");
    this.selectFacilityFilterSubOptionsDropdown = (txt) => page.locator(`//span[normalize-space(text())='${txt}']`);
    this.optionsLocator = page.locator(
      "//div[@class='cdk-virtual-scroll-content-wrapper ng-scroll-content']//span"
    );
    this.facilitydropdownOptions = page.locator(
      "//div[@class='px-12 flex items-center grow gap-8 overflow-hidden text-ellipsis whitespace-nowrap ng-star-inserted']//span"
    );

    // ── Sort flow ─────────────────────────────────────────────────────────
    this.addSortBtn = page.locator("//span[normalize-space(text())='Add Sort']");
    this.selectSortingFilterName = page.locator("(//span[text()='Select'])[1]");
    this.sortingOptionDropdown = page.locator("(//span[text()='Select'])[2]");
    this.selectSortingOption = (txt) => page.locator(`//div[normalize-space(text())='${txt}']`);

    // ── Grid columns ──────────────────────────────────────────────────────
    this.facilityGridColumns = page.locator("//div[@data-column-definition-name='facility']//span");
    this.residentGridColumns = page.locator("//div[@data-column-definition-name='caseDetails']//a");
    this.payerGridColumns = page.locator(
      "//div[@data-column-definition-name='payer']//span[contains(@class,'block overflow-hidden')]"
    );
    this.balanceGridColumn = page.locator(
      "//div[@data-column-definition-name='balance']//span[contains(@class,'block overflow-hidden')]"
    );
    this.balanceStatusGridColumn = page.locator(
      "//div[@data-column-definition-name='balanceStatusId']//span[contains(@class,'grow overflow-ellipsis')]"
    );
    this.taskStatusGridColumn = page.locator(
      "//div[@data-column-definition-name='taskStatusId']//span[contains(@class,'grow overflow-ellipsis')]"
    );
    this.assignedToGridColumns = page.locator(
      "//div[@data-column-definition-name='assignedToUser']//span[contains(@class,'overflow-hidden')]"
    );
    this.rootIssuesGridColumns = page.locator(
      "//div[@data-column-definition-name='issue']//span[contains(@class,'block overflow-hidden')]"
    );
    this.rootIssuesGridColumnsFirst = page.locator(
      "(//div[@data-column-definition-name='issue']//span[contains(@class,'block overflow-hidden')])[1]"
    );
    this.dueDateGridColumns = page.locator(
      "//div[@data-column-definition-name='dueDate']//span[contains(@class,'block overflow-hidden')]"
    );
    this.serviceDatesGridColumns = page.locator(
      "//div[@class='arw-grid-table__cell ng-star-inserted'][@data-column-definition-name='serviceDates']//span[contains(@class,'block overflow-hidden')]"
    );
    this.facilityOptionCheckbox = (txt) =>
      page.locator(`(//div[@class='overflow-hidden text-ellipsis whitespace-nowrap']//span[text()='${txt}'])[1]`);
    this.taskListGridColumns = (txt) =>
      page.locator(`//div[@data-column-definition-name='${txt}']//span[contains(@class,'block overflow-hidden')]`);
    this.noMatchesFoundLabel = page.locator("//label[normalize-space(text())='All (0 Matches)']");
    this.dropdownOptionList = page.locator(
      "//div[@class='overflow-hidden text-ellipsis whitespace-nowrap']//span[contains(@class,'bg-complementary-blue')]"
    );

    // ── Balance filter ────────────────────────────────────────────────────
    this.balanceOptions = (txt) => page.locator(`//div[normalize-space(text())='${txt}']`);
    this.betweenInputOne = page.locator("(//input[@type='number'])[1]");
    this.betweenInputTwo = page.locator("(//input[@type='number'])[2]");
    this.dueDateOptions = (txt) =>
      page.locator(
        `//div[contains(@class,'cdk-virtual-scroll-content-wrapper')
          and contains(@class,'ng-scroll-content')]
     //div[contains(@class,'overflow-hidden')
          and contains(@class,'text-ellipsis')
          and contains(@class,'whitespace-nowrap')]
     //span[normalize-space()='${txt}']`
      );
    this.dueDateDefaultValuePath = page.locator(
      "(//div[@class='mat-mdc-menu-content']/descendant::div[contains(@class,'whitespace-nowrap')])[2]"
    );
    this.defaultBalanceAndTaskStatusValuePath = page.locator(
      "(//div[@class='mat-mdc-menu-content']/descendant::div[contains(@class,'whitespace-nowrap')])[4]"
    );

    // ── Task row / Task details ──────────────────────────────────────────
    this.selectFirstTask = page
      .locator("//div[@data-column-definition-name='taskId']//span[contains(@class,'block overflow-hidden')]")
      .first();
    this.taskNameInput = page.locator("//div[@class='relative flex h-full']//input");
    this.taskViewFacilityName = page.locator("arw-icon[name='building01'] + span");
    this.taskNameInputField = page.locator("//arw-input[@formcontrolname='name']//input");
    this.taskViewResidentName = page.locator("//arw-task-details//a[contains(@href,'/cases/details/')]");
    this.taskViewPayerName = page.locator(
      "//span[normalize-space(text())='Payer']/ancestor::div[contains(@class,'items-center')]//span[contains(@class,'mr-auto')]"
    );
    this.taskViewBalance = page.locator("//span[normalize-space()='Balance']/following-sibling::span");
    this.taskCloseBtn = page.locator("//arw-task-details//arw-button[@icon='x']");
    this.rootIssueSelectDropdown = page.locator("//span[normalize-space()='Root Issue']");
    this.balanceStatusDropdownOptions = page.locator("//mat-option[@aria-selected='false']");
    this.selectRootOption = page.locator("(//mat-option[@role='option'])[1]");
    this.customRangeStartDateInput = page.locator("(//div[@class='mat-date-range-input-container']//input)[1]");
    this.customRangeEndDateInput = page.locator("(//div[@class='mat-date-range-input-container']//input)[2]");
    this.taskStatusDropdownOptions = (txt) =>
      page.locator(`//div[@class='overflow-hidden text-ellipsis whitespace-nowrap']//span[normalize-space(text())='${txt}']`);
    this.pickPayerName = (txt) =>
      page.locator(
        `(//div[contains(@class,'overflow-hidden text-ellipsis whitespace-nowrap')]/descendant::span[normalize-space(text())='${txt}'])[1]`
      );
    this.filtersDropdownListCount = page.locator("(//label[@class='mdc-label'])[1]");
    this.activityTab = page.locator("//span[normalize-space(text())='Activity']");
    this.dueDateInput = page.locator("//input[@placeholder='mm/dd/yyyy']");
    this.daysBtn = (txt) => page.locator(`(//span[normalize-space(text())='${txt}']/ancestor::button)[1]`);
    this.pickDuedate = (txt) => page.locator(`(//span[normalize-space(text())='${txt}'])[1]`);
    this.filterCountLabel = page.locator("//span[normalize-space(text())='Filters']//span");
    this.firstTaskName = page.locator("(//div[@class='arw-grid-table__row-wrapper ng-star-inserted']//div//div)[1]");
    this.residentNameInTaskList = page.locator("(//div[@class='arw-control arw-control--inline items-center'])[2]//a");

    // ── Calendar / dates ──────────────────────────────────────────────────
    this.currentYear = page.locator("//input[contains(@class,'cur-year')]");
    this.calendar = page.locator(".flatpickr-calendar");
    this.prevArrow = page.locator("//span[@class='flatpickr-prev-month']");
    this.monthButtons = page.locator("//div[@class='flatpickr-monthSelect-months']//span");
    this.chargersLabel = page.locator("(//span[@class='mdc-tab__text-label'])[2]");
    this.chargersServiceDates = page.locator(
      "//div[normalize-space()='Linked Charges'] /following::arw-grid[1] //div[contains(@class,'arw-grid-table__cell') and @data-column-definition-name='serviceDates']"
    );
    this.loadSpinner = page.locator("//mat-spinner[@role='progressbar']");
    this.taskListRows = page.locator("//div[@role='link']");
    this.chargesTab = page.locator("//arw-task-details//mat-tab-header//span[normalize-space(text())='Charges']");
    this.coverageInChargesTab = page.locator("(//arw-template-renderer[@class='text-sm ng-star-inserted'])[2]/span");
    this.facilityFilterOption = (option) => page.locator(`//mat-option//div[normalize-space(text())='${option}']`);
    this.highestBalancesLabel = page.locator("//div[normalize-space(text())='Highest Balances']");
    this.seeMoreBtn = page.locator("//span[normalize-space(text())='See more']/parent::button");
    this.unworkedTasksLabel = page.locator("//div[normalize-space(text())='Unworked Tasks']");
    this.unworkedTasksResidentNameLinks = page.locator("(//div[normalize-space(text())='Resident'])[2]/following::a");
    this.balanceLabels = page.locator(
      "(//div[normalize-space(text())='Balance'])[1]/following::a[contains(@class,'font-bold')]"
    );
    this.highestBalancesResidentNameLinks = page.locator(
      "//arw-highest-balances-widget//ng-scrollbar//div[contains(@class,'flex py-4')]/div[2]//a"
    );
    this.addCommentInputBox = page.locator("//div[contains(@data-placeholder,'Add comment')]");
    this.serviceInChargesTab = page.locator("(//arw-template-renderer[@class='text-sm ng-star-inserted'])[3]/span");
    this.taskListDueDateInput = page.locator(
      "arw-input[formcontrolname='followUpDate'] input.mat-datepicker-input"
    );
    this.dueDateCustomRangeBtn = page.locator("//span[@class='w-full text-left block']");
    this.applyFilterButton = page.locator(
      "//div[@class='flex justify-between px-20']//span[normalize-space(text())='Apply Filter']"
    );
    this.dayButton = (day) =>
      this.page.locator(`//button[contains(@class,'mat-calendar-body-cell')]
         [.//span[normalize-space(text())='${day}']]`);

    // ── Settings / navigation ─────────────────────────────────────────────
    this.settingsButton = page.locator("//span[normalize-space()='Settings']");
    this.userManagementOption = page.locator("//span[text()=' User Management ']");
    this.facilityPayersOption = page.locator("//arw-side-nav-node//span[normalize-space()='Facility Payers']");
    this.facilityAndRoleViewButton = page.locator("(//div[@class='flex justify-center']//mat-button-toggle)[2]");
    this.facilityFilterDropdown = page.locator("//span[text()='Select Facility']");
    this.firstNameColumnCell = this.page.locator(
      "//div[contains(@class,'arw-grid-table__cell') and @data-column-definition-name='firstName']//span[contains(@class,'block overflow-hidden text-ellipsis')]"
    );
    this.taskListBtn = page.locator("//arw-side-nav-node//span[text()=' Task List ']");
    this.commentEditor = page.locator("//arw-text-editor[@mode='comment']//div[contains(@class,'ql-editor')]");

    // ── Calendar overlay (due date extension) ────────────────────────────
    this.calendarContainer = this.page.locator('mat-datepicker-content');
    this.calendarHeader = this.page.locator('mat-calendar mat-calendar-header .mat-calendar-period-button');
    this.calendarNextBtn = this.page.locator('mat-calendar button[aria-label="Next month"]');
    this.calendarPrevBtn = this.page.locator('mat-calendar button[aria-label="Previous month"]');

    // ── Overdue tasks widget ──────────────────────────────────────────────
    this.overdueTasksUserIcons = page.locator("//arw-overdue-tasks-widget//arw-avatar");
    this.tooltip = page.locator("//div[contains(@id,'cdk-overlay')]/arw-tooltip-overlay");
    this.overdueTasksChart = page.locator("//arw-overdue-tasks-widget//canvas[@basechart]");
    this.overdueTasksNoData = page.locator("//arw-overdue-tasks-widget//div[normalize-space(text())='No Data']");
    this.overdueTasksSpinner = page.locator("//arw-overdue-tasks-widget//mat-spinner");

    // ── Column chooser ────────────────────────────────────────────────────
    // Button label now includes a live column count (e.g. "Columns (13)"), so match by role + partial text.
    this.columnsFilter = page.getByRole('button', { name: /Columns/ });
    this.clearButton = page.locator("//button[normalize-space(text())='Clear']");
    this.columnFiltersDropList = page.locator(
      "//div[@class='ng-scroll-content']/div[contains(@class,'cdk-drop-list')]/div"
    );
    this.columnFiltersDropListCheckboxes = this.columnFiltersDropList.locator("//input");
    this.columnFilterHeaders = page.locator("//div[contains(@class,'cdk-drag arw-grid-table__header')]");
    this.columnsGrid = (columnName) =>
      page.locator(
        `//div[contains(@class,'cdk-drag arw-grid-table__header-cell')]//div[normalize-space(text())='${columnName}']`
      );
    this.filterFunnel = (filter) =>
      page.locator(`//div[normalize-space()='${filter}']//arw-icon[contains(@name,'filterFunnel')]`);
    this.filterByCheckbox = (filterBy) =>
      page.locator(`//div[normalize-space()='${filterBy}']/preceding-sibling::mat-checkbox`);
    this.taskNameInputBox = page.locator("//arw-input[@formcontrolname='value']//input");
    this.chargeMonthButton = page.locator("//arw-label[normalize-space()='Balance']/following-sibling::span//arw-button");
    this.extendDueDateBtn = page.locator("//arw-button[@icon='clockFastForward']//button");
    this.dueDateCalendar = page.locator("//mat-calendar[@class='mat-calendar']");
    this.dueDateExtensionMessageBox = page.locator(
      "//div[contains(text(),'Can extend up to') and contains(text(),'from today')]"
    );
    this.reasonForExtensionInputBox = page.locator(
      "//div[contains(@data-placeholder,'reason for extending the due date')]"
    );
    this.dueDateExtensionSuccessfulMessage = page.locator(
      "//span[contains(text(),'Due date has been successfully extended')]"
    );
    this.dueDateExtendedTag = page.locator("//arw-tag[normalize-space()='Due Date Extended']");
    this.columnCountLocator = page.locator("//arw-grid-columns-toolbar//button//span[contains(@class,'font-bold')]");
    this.columnsToolbarDropdown = page.locator("//arw-grid-columns-toolbar-dropdown");
    this.columnsChooserFilterOptions = page.locator(
      "//arw-grid-columns-toolbar-dropdown//div[contains(@class,'overflow-hidden text-ellipsis whitespace-nowrap grow')]"
    );
    this.columnChooserCheckboxes = page.locator("//arw-grid-columns-toolbar-dropdown//input[@type='checkbox']");
    this.resetToDefault = page.locator("//arw-grid-header//arw-button[@iconright='refreshCw01']");

    // ── Case / facility payers ────────────────────────────────────────────
    this.residentLinkOnTaskDetails = page.locator("arw-task-details a[href*='/cases/details/']");
    this.residentNameOnTaskList = page.locator(
      "//div[contains(@class,'arw-grid-table__cell') and @data-column-definition-name='caseDetails']"
    );
    this.facilityPayersRows = page.locator("div.arw-grid-table__row");
    this.payerNameColumn = "[data-column-definition-name='payerName']";
    this.payerCategoryColumn = "[data-column-definition-name='overridePayerCategoryName']";
    this.facilityCheckbox = (facilityName) =>
      this.page.locator(`//span[normalize-space()='${facilityName}']/ancestor::div[1]/preceding-sibling::mat-checkbox`);
    this.payersFilterDropdown = page.locator("//arw-grid-inline-filters//span[normalize-space()='Select Payers']");
    this.payerCheckbox = (payerName) =>
      this.page.locator(`//span[normalize-space()='${payerName}']/ancestor::div[1]/preceding-sibling::mat-checkbox`);
    this.taskDetails = page.locator("//arw-task-details");
    this.facilityNamesOnTaskList = page.locator(
      "//div[contains(@class,'arw-grid-table__cell ng-star-inserted')][@data-column-definition-name='facility']"
    );

    // ── Saved views ───────────────────────────────────────────────────────
    this.defaultViewBtn = page.locator("//arw-grid-saved-views//button");
    this.saveAsNewViewBtn = page.locator("//button[@arw-dropdown-item and @icon='save01']");
    this.viewNameInput = page.locator("//input[@placeholder='View name']");
    this.saveNewViewBtn = page.locator(
      "//arw-button[contains(@class,'self-end')]//button//span[normalize-space()='Save new view']"
    );
    this.defaultViewToastMessage = page.locator("//arw-toast//span[contains(@class,'web-body-1 text')]");
    this.defaultViewToastCloseBtn = page.locator("//arw-toast//arw-button[@icon='x']");
    this.appliedFilterNames = page.locator(
      "//arw-grid-header-filters-dropdown//arw-select[@formcontrolname='name']//div[@class='mat-mdc-select-value']"
    );
    this.threeDotsBtn = (viewName) =>
      page.locator(
        `//div[contains(@class,'justify-between')][.//text()[contains(.,'${viewName}')]]//arw-button[@icon='dotsVerticalDefault']`
      );
    this.viewLocator = (viewName) =>
      page.locator(`//button[@icon="layoutAlt01"]//div[contains(@class,'justify-between') and contains(normalize-space(),'${viewName}')]`);
    this.deleteOption = page.locator("//button[@icon='trash03']");
    this.editOption = page.locator("//button[@icon='edit01']");
    this.confirmDeleteBtn = page.locator("//mat-dialog-container//span[normalize-space()='Delete']");
    this.savedViews = page.locator("//button[@icon='layoutAlt01']//div[contains(@class,'justify-between')]");
    this.deleteDialogTitle = page.locator("text=Are you sure you want to delete this saved view?");
    this.dialogCancelBtn = page.locator("//mat-dialog-container//span[normalize-space()='Cancel']");
    this.dialogCloseBtn = page.locator("//mat-dialog-container//arw-button[@icon='x']");
    this.deleteDialog = page.locator("//mat-dialog-container");
    this.deleteDialogContent = page.locator("//mat-dialog-container//div[contains(@class,'flex flex-col')]");
    this.viewEditRenameInput = page.locator("//arw-input[@formcontrolname='name']//input");
    this.viewEditRenameSubmitBtn = page.locator("//div[@role='menu']//arw-button[contains(@class,'self-end')]");
    this.renamePanel = page.locator("//div[@role='menu']");

    // ── Bulk update / comments ────────────────────────────────────────────
    this.bulkUpdateGridColumn = (headerName) =>
      page.locator(`//div[contains(@class,'cdk-drag arw-grid-table__header-cell') and @data-column-definition-name='${headerName}']`);
    this.bulkUpdateCommentInput = page.locator("//input[@placeholder='Write a comment']");
    this.commentSendBtn = page.locator("//arw-button[@icon='send03']//button");

    // ── Share functionality ───────────────────────────────────────────────
    this.shareButton = page.locator('arw-button[icon="share07"] button');
    this.toastMessage = page.locator('arw-toast span.web-body-1.text-foreground-high');

    // ── Selector strings — reusable across any page instance (e.g. popup tabs) ──
    this.selectors = {
      shareButton: "arw-button[icon='share07'] button",
      shareLinkToast: "arw-toast span.web-body-1.text-foreground-high",
      loadSpinner: "mat-spinner",
      viewTaskListBtn: "//arw-button[@category='secondary']/following-sibling::arw-button",
      viewAgingBtn: "//arw-button[@category='secondary']",
      filterBtn: "(//arw-grid-header-filters[@class='ng-star-inserted']//span)[1]",
      appliedFilter1: "(//div[contains(@class,'web-body-1 text-foreground-high grow overflow-hidden')])[1]",
      appliedFilter2: "(//div[contains(@class,'web-body-1 text-foreground-high grow overflow-hidden')])[2]",
      columnsFilter: "//span[normalize-space(text())='Columns']",
      columnsChosserFilterOptions:
        "//arw-grid-columns-toolbar-dropdown//div[contains(@class,'overflow-hidden text-ellipsis whitespace-nowrap grow')]",
      columnChosserCheckboxes: "//arw-grid-columns-toolbar-dropdown//input[@type='checkbox']",
    };

    // ── Facility Payers grid ──────────────────────────────────────────────
    this.virtualScrollViewport = page.locator("ng-scrollbar.cdk-virtual-scrollable").first();
    this.gridRowWrapper = this.page.locator("div.arw-grid-table__row-wrapper.ng-star-inserted");
    this.taskDetailsTitle = page.locator("//arw-task-details//span[@class='web-title-2']");
    this.copyTaskLinkBtn = page.locator("//arw-button[@icon='link01']");
    this.tooltipOverlay = page.locator("div.arw-tooltip-overlay.arw-tooltip-overlay--default");

    // ── Comments (Task Details) ──────────────────────────────────────────
    this.commentField = page.locator("arw-text-editor[mode='comment'] div.ql-editor[contenteditable='true']");
    this.existingComments = page.locator("quill-view .ql-editor p");
    this.commentAddedTime = page.locator("div.web-body-2.text-foreground-light");
    this.commentMenuBtn = page.locator("arw-button[icon='dotsVerticalDefault']");
    this.deleteCommentBtn = page.locator('button[arw-dropdown-item]').filter({ hasText: 'Delete' });
    this.editCommentBtn = page.locator('button[arw-dropdown-item] span.grow.text-left').filter({ hasText: 'Edit' });
    this.saveComment = page.locator('arw-button[category="primary"][size="small"]').filter({ hasText: 'Save' });
    this.commentConfirmDeleteBtn = page.getByRole('button', { name: 'Delete' });
    this.commentThread = page.locator('quill-view');
    this.replyBlock = page.locator('div.flex.flex-col.grow.overflow-hidden');
    this.replyBtn = page.getByRole('button', { name: 'Reply' });
    this.editor = page.locator('div.ql-editor[contenteditable="true"]');
    this.activityExpandBtn = page.locator(
      "//div[contains(@class,'shadow-m arw-grid-table__row')]//button[contains(@class,'arw-button arw-button--neutral')]"
    );
    this.balancesListBtn = page.locator("//arw-side-nav-node//span[normalize-space()='Balances List']");
    this.mostRecentComment = page.locator("//div[@data-column-definition-name='comment']//span[contains(@class,'overflow-hidden text')]");
    this.mostRecentCommentTableCell = page.locator(
      "//div[contains(@class,'arw-grid-table__cell ng-star-inserted')][@data-column-definition-name='comment']"
    );

    // ── Aging ─────────────────────────────────────────────────────────────
    this.agingTaskCreatedBtn = page.locator("//arw-ar-aging-cell//div[@role='button']");
    this.agingTaskTooltip = page.locator("//arw-tooltip-overlay//div[contains(@class,'web-body-1 ng')]");
    this.agingCommentOnTooltip = page.locator("//div[@class='ql-editor']");
    this.agingBtn = page.locator("//arw-side-nav-node//span[normalize-space(text())='AR Aging']");
    this.selectMonthPlaceholder = page.locator(
      "//arw-month-range-picker//span[starts-with(normalize-space(),'Select Month')]"
    );
    this.assignedUserName = page.locator(
      "//arw-task-details//arw-select[@formcontrolname='assigneeId']//span[contains(@class,'grow overflow-ellipsis')]"
    );

    // ── Last Updated On / Last Updated By columns (SCRUM-26) ──────────────
    this.columnChooserCheckboxByLabel = (columnName) =>
      page.locator(
        `//arw-grid-columns-toolbar-dropdown//div[normalize-space()='${columnName}']/preceding-sibling::input[@type='checkbox']`
      );
  }

  // ── getLocators — rebuild the shared selector map against another page/tab (popup, new tab) ──
  getLocators(page) {
    return {
      shareButton: page.locator(this.selectors.shareButton),
      shareLinkToast: page.locator(this.selectors.shareLinkToast),
      loadSpinner: page.locator(this.selectors.loadSpinner),
      viewTaskListBtn: page.locator(this.selectors.viewTaskListBtn),
      viewAgingBtn: page.locator(this.selectors.viewAgingBtn),
      filterBtn: page.locator(this.selectors.filterBtn),
      appliedFilter1: page.locator(this.selectors.appliedFilter1),
      appliedFilter2: page.locator(this.selectors.appliedFilter2),
    };
  }

  // ── Simple actions ──────────────────────────────────────────────────────

  async clickOnResidentLinkOnTaskDetails() {
    await test.step('Click on Resident Link on Task Details', async () => {
      await this.residentLinkOnTaskDetails.click();
    });
  }

  async fillReasonForDueDateExtension(reason) {
    await test.step('Enter reason for Due Date Extension', async () => {
      await this.reasonForExtensionInputBox.fill(reason);
    });
  }

  async clickOnExtendButton() {
    await test.step('Click on Extend button', async () => {
      await this.extendDueDateBtn.click();
    });
  }

  async fillTaskName(taskName) {
    await test.step('Enter Task Name', async () => {
      await this.taskNameInputBox.fill(taskName);
    });
  }

  async clickOnClearButton() {
    await test.step('Click on Clear button in Columns Filter in Task List', async () => {
      await this.clearButton.click();
    });
  }

  async clickOnColumnsFilter() {
    await test.step('Click on Columns Filter in Task List', async () => {
      await this.columnsFilter.click();
    });
  }

  async clickOnTaskList() {
    await test.step('Click on the Task List button', async () => {
      await this.taskListBtn.click();
    });
  }

  async searchTextInSearchBox(text) {
    await test.step('Enter user email in search box', async () => {
      await this.searchInputBox.fill(text);
    });
  }

  async clickOnFacilityFilterDropdown() {
    await test.step('Click on the facility dropdown', async () => {
      await this.facilityFilterDropdown.click();
    });
  }

  async clickFacilityAndRoleViewButton() {
    await test.step('Click on Facility & Role View button', async () => {
      await this.facilityAndRoleViewButton.click();
    });
  }

  async clickUserManagementOption() {
    await test.step('Click on User Management option in Settings', async () => {
      await this.userManagementOption.click();
    });
  }

  async clickOnSettingsButton() {
    await test.step('Click Settings button in HomePage/Dashboard', async () => {
      await this.settingsButton.click();
    });
  }

  async clickOnApplyBtn() {
    await test.step('Click on the Apply filter button', async () => {
      await this.applyButton.click();
    });
  }

  async clickOnSeeMoreBtn() {
    await test.step('Click on See More button', async () => {
      await this.seeMoreBtn.click();
    });
  }

  async fillCommentBox(message) {
    await test.step('Enter comment in add comment input box', async () => {
      await this.addCommentInputBox.fill(message);
    });
  }

  async clickOnAddCommentInputBox() {
    await test.step('Click on add comment input box', async () => {
      await this.addCommentInputBox.click();
    });
  }

  async selectFacilityFilterOption(filter) {
    await test.step('Select facility filter from dropdown', async () => {
      await this.facilityFilterOption(filter).click();
    });
  }

  async clickOnChargesTab() {
    await test.step('Click on Charges tab in task list', async () => {
      await this.chargesTab.click();
    });
  }

  async clickOnResidentNameInTaskList() {
    await test.step('Click on Resident Name in Task List', async () => {
      await this.firstTaskName.click();
    });
  }

  async clickOnFirstTaskOnTaskList() {
    await test.step('Click on first Task in Task List', async () => {
      await this.firstTaskName.click();
    });
  }

  async clickOnFilterBtn() {
    await test.step('Click on Filters icon in Task List', async () => {
      await this.filterBtn.click();
    });
  }

  async clickOnSelectedFilterBtn() {
    await test.step('Click on selectedFilter field in Task List', async () => {
      await this.selectedFilter.click();
    });
  }

  async selectDuedate(txt) {
    await test.step('Select the due date from the calendar', async () => {
      await this.pickDuedate(txt).click();
    });
  }

  async clickOnDueDateField() {
    await test.step('Click on due date input', async () => {
      await this.dueDateInput.click();
    });
  }

  async clickOnCloseBtn() {
    await test.step('Click on close icon', async () => {
      await this.closeIconBtn.click();
    });
  }

  async clickOnActivityTab() {
    await test.step('Navigate to Activity section', async () => {
      await this.activityTab.click();
    });
  }

  async clickOnTaskCloseBtn() {
    await test.step('Click close button', async () => {
      await this.taskCloseBtn.click();
    });
  }

  async selectTaskStatusOption(txt) {
    await test.step('Select task status dropdown option', async () => {
      await this.taskStatusDropdownOptions(txt).click();
    });
  }

  async enterCustomStartDate(txt) {
    await test.step('Enter the start date for the custom date range', async () => {
      await this.customRangeStartDateInput.fill(txt);
    });
  }

  async enterCustomEndDate(txt) {
    await test.step('Enter the end date for the custom date range', async () => {
      await this.customRangeEndDateInput.fill(txt);
    });
  }

  async clickOnRootIssueDropdown() {
    await test.step('Click on root issue dropdown', async () => {
      await this.rootIssueSelectDropdown.click();
    });
  }

  async selectRootIssueOptionFromDropdown() {
    await test.step('Select root issue option from the dropdown', async () => {
      await this.selectRootOption.click();
    });
  }

  async clickOnTaskName() {
    await test.step('Navigate to task view', async () => {
      await this.selectFirstTask.click();
    });
  }

  async clickOnClearFilterIcon() {
    await test.step('Click on Clear Filter icon to clear all default filters', async () => {
      await this.clearFilter.click();
    });
  }

  async clickOnClearAssignedToFilterIcon() {
    await test.step("Click on clear filter 'X' icon on assignedTo filter", async () => {
      await this.clearAssignedToFilter.click();
    });
  }

  async clickOnDeleteDueDateInSortIcon() {
    await test.step('Clear all sorting filters', async () => {
      await this.deleteSortIcon.click();
    });
  }

  async clickOnDeleteBalanceInSortIcon() {
    await test.step('Click on trash/delete icon beside Balance option in Sort dropdown', async () => {
      await this.deleteBalanceInSort.click();
    });
  }

  async clickOnApplySortButtonIcon() {
    await test.step('Click on Apply Sort button', async () => {
      await this.applySortButton.click();
    });
  }

  async hoverOverResidentHeaderIcon() {
    await test.step('Hover over Resident filter icon', async () => {
      await this.residentHeader.hover();
    });
  }

  async clickOnGridFilterIcon() {
    await test.step('Click on filter icon beside Resident', async () => {
      await this.gridFilterIcon.click();
    });
  }

  async clickOnSelectResidentDropDownIcon() {
    await test.step('Click on Select Resident dropdown', async () => {
      await this.selectResidentDropDown.click();
    });
  }

  async clickOnApplyFilterButton() {
    await test.step('Click on Apply Filter', async () => {
      await this.applyFilterBtn.click();
    });
  }

  async fillSearchBoxInResidentFilterIcon(name) {
    await test.step(`Enter/fill Resident Name ${name}`, async () => {
      await this.searchInputBox.fill(name);
    });
  }

  async clickOnAllCheckboxIcon() {
    await test.step('Select All checkbox', async () => {
      await this.overdueCheckBox.click();
    });
  }

  async clickOnApplyButton() {
    await test.step('Click on Apply button', async () => {
      await this.applyButton.click();
    });
  }

  async clickOnResidentNameLink() {
    await test.step('Click on Resident Name link in Resident column', async () => {
      await this.residentNameLink.click();
    });
  }

  async clickOnViewTaskListButton() {
    await test.step('Click on View Task List button on the top right', async () => {
      await this.viewTaskListButton.click();
    });
  }

  async clickOnResetDefaultBtn() {
    await test.step('Click on reset default button', async () => {
      await this.resetToDefault.click();
    });
  }

  async clickOnViewAgingButton() {
    await test.step('Click on View Aging button', async () => {
      await this.viewAgingButton.click();
    });
  }

  async clickOnDownArrow() {
    await test.step('Click on Down Arrow in AR Aging', async () => {
      await this.downArrow.click();
    });
  }

  async clickOnFiltersDropDownInArAging() {
    await test.step('Click on Filters dropdown in AR Aging', async () => {
      await this.filtersDropDown.click();
    });
  }

  async searchCaseName(txt) {
    await test.step("Search for a resident's name in case search input", async () => {
      await this.caseSearchInput.fill(txt);
    });
  }

  async clickOnClearCaseSearchBtn() {
    await test.step('Click on the Clear button to clear the search field', async () => {
      await this.closeIconBtn.click();
    });
  }

  async clickOnResidentOption() {
    await test.step('Navigate to case view details', async () => {
      await this.residentOptionList.click();
    });
  }

  async clickOnGlobalSearchDropdown() {
    await test.step('Click on global facility dropdown', async () => {
      await this.globalFacilityDropdown.click();
    });
  }

  async deselectAllFacilities() {
    await test.step('Deselect all facilities in the global facility dropdown', async () => {
      await this.selectAllBtn.click();
    });
  }

  async selectAllFacilities() {
    await test.step('Select all facilities in the global facility dropdown', async () => {
      await this.selectAllBtn.click();
    });
  }

  async searchGlobalFacility(txt) {
    await test.step('Search for a facility name in the search input field', async () => {
      await this.searchInputBox.fill(txt);
    });
  }

  async clickOnCustomSortBtn() {
    await test.step('Click on the custom sort button', async () => {
      await this.customSortBtn.click();
    });
  }

  async selectSearchFacilityInDropdown() {
    await test.step('Select a facility from the global facility dropdown', async () => {
      await this.todayCheckBox.click();
    });
  }

  async clickOnGlobalFacilityApplyBtn() {
    await test.step('Click on Apply button', async () => {
      await this.applyButton.click();
    });
  }

  async clickOnAddFilterBtn() {
    await test.step('Click on the Add Filter button', async () => {
      await this.addFilterBtn.click();
    });
  }

  async clickOnAddFilterDropdown() {
    await test.step('Click Add Filter dropdown', async () => {
      await this.addFilterDropdown.click();
    });
  }

  async searchTaskName(txt) {
    await test.step('Enter the filter name in the search input', async () => {
      await this.taskNameSearchInput.fill(txt);
    });
  }

  async searchFilterNames(txt) {
    await test.step('Enter the filter name in the search input', async () => {
      await this.searchInputBox.fill(txt);
    });
  }

  async selectFilterOptionsFromDropdown(txt) {
    await test.step('Select the desired filter from the dropdown list', async () => {
      await this.selectFiltersOptions(txt).click();
    });
  }

  async selectFacilitySubOptions(txt) {
    await test.step('Click on the dropdown to select a facility filter sub-option', async () => {
      await this.selectFacilityFilterSubOptionsDropdown(txt).click();
    });
  }

  async searchSortName(txt) {
    await test.step('Enter the sorting filter name in the search input', async () => {
      await this.searchInputBox.fill(txt);
    });
  }

  async clickOnAddSortBtn() {
    await test.step('Click on the Add Sort button', async () => {
      await this.addSortBtn.click();
    });
  }

  async clickOnSelectSortingFilterName() {
    await test.step('Click on the sorting filter name dropdown', async () => {
      await this.selectSortingFilterName.click();
    });
  }

  async clickOnSortingOptionDropdown() {
    await test.step('Click on the sorting option dropdown', async () => {
      await this.sortingOptionDropdown.click();
    });
  }

  async selectSortingOptionFromDropdown(txt) {
    await test.step('Select the desired sorting option from the dropdown', async () => {
      await this.selectSortingOption(txt).click();
    });
  }

  async clickOnSortBtn() {
    await test.step('Click on the sort button', async () => {
      await this.customSortBtn.click();
    });
  }

  async clickOnBalanceOptions(txt) {
    await test.step('Select required option from the dropdown', async () => {
      await this.balanceOptions(txt).click();
    });
  }

  async fillBetweenBalanceInputOne(txt) {
    await test.step('Enter data in input field', async () => {
      await this.betweenInputOne.fill(txt);
    });
  }

  async fillBetweenBalanceInputTwo(txt) {
    await test.step('Enter data in input field', async () => {
      await this.betweenInputTwo.fill(txt);
    });
  }

  async clickOnDueDateOptions(txt) {
    await test.step('Select due date option from the dropdown', async () => {
      await this.dueDateOptions(txt).click();
    });
  }

  // ── Last Updated On / Last Updated By columns (SCRUM-26) ─────────────────

  async isColumnChooserCheckboxChecked(columnName) {
    return test.step(`Check whether "${columnName}" checkbox is checked in the column chooser`, async () => {
      return this.columnChooserCheckboxByLabel(columnName).isChecked();
    });
  }

  async isColumnChooserCheckboxVisible(columnName) {
    return test.step(`Verify "${columnName}" checkbox is visible in the column chooser`, async () => {
      return this.columnChooserCheckboxByLabel(columnName).isVisible();
    });
  }

  async isColumnChooserCheckboxEnabled(columnName) {
    return test.step(`Verify "${columnName}" checkbox is enabled in the column chooser`, async () => {
      return this.columnChooserCheckboxByLabel(columnName).isEnabled();
    });
  }

  async toggleColumnChooserCheckbox(columnName) {
    await test.step(`Toggle "${columnName}" checkbox in the column chooser`, async () => {
      await this.columnChooserCheckboxByLabel(columnName).click();
    });
  }

  async closeColumnChooserDropdown() {
    await test.step('Close the column chooser dropdown', async () => {
      await this.hoverOut.click();
    });
  }

  async isColumnHeaderVisible(columnName) {
    return test.step(`Verify "${columnName}" column header is visible in the grid`, async () => {
      return this.columnsGrid(columnName).isVisible();
    });
  }

  async getGridColumnHeaderNames() {
    return test.step('Get the ordered list of grid column header names', async () => {
      const headerTexts = await this.columnFilterHeaders.allTextContents();
      return headerTexts.map((text) => text.trim()).filter(Boolean);
    });
  }

  async waitForGridToLoad() {
    await test.step('Wait for the Task List grid to load', async () => {
      // The Task List page keeps background polling/websocket traffic alive, so
      // page.waitForLoadState('networkidle') (BasePage.waitForLoad) never resolves here.
      // Wait on a concrete grid element instead.
      await this.columnsFilter.waitFor({ state: 'visible', timeout: settings.PAGE_LOAD_TIMEOUT });
    });
  }

  async clickOnFilterFunnelIcon(columnName) {
    await test.step(`Click filter funnel icon for "${columnName}" column`, async () => {
      await this.filterFunnel(columnName).click();
    });
  }

  async selectFirstDropdownOption() {
    await test.step('Select the first option from the open dropdown list', async () => {
      await this.dropdownOptionList.first().click();
    });
  }
}

module.exports = { TaskListPage };
