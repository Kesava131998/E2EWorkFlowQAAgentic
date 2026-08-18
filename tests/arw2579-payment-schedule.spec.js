const { test, expect } = require('@playwright/test');
const { epic, feature, story } = require('allure-js-commons');
const { CaseDetailPage } = require('../pages/case_detail_page');
const { settings } = require('../config/settings');

// TODO: replace with a real case/payer fixture once test data is confirmed for this environment
const CASE_WITH_NO_SCHEDULE_URL = `${settings.BASE_URL}/cases/TODO-empty-schedule-case`;
const CASE_WITH_SCHEDULE_URL = `${settings.BASE_URL}/cases/TODO-populated-schedule-case`;
const ELIGIBLE_PAYER = 'TODO-eligible-payer';
const INELIGIBLE_PAYER = 'TODO-ineligible-payer';
const PAYER_WITH_EXISTING_SCHEDULE = 'TODO-payer-with-existing-schedule';

test.describe('ARW-2579: FE - Add a Payment Schedule to a Case', () => {
  test.beforeEach(async () => {
    await epic('ARW-2579: FE - Add a Payment Schedule to a Case');
    await feature('payment_schedule');
  });

  test('pos: open modal from empty-state CTA', async ({ page }) => {
    await story("AC1: User can open the Add Payment Schedule modal from the empty-state CTA");
    // Jira: ARW-2579
    // AC: User can click "Add Payment Schedule" from the Empty state CTA; opens modal
    // titled "Add Payment Schedule" with subtitle "Define the expected payment timing
    // and method for a payer. Payments are not initiated from this schedule."
    const casePage = new CaseDetailPage(page);

    await test.step('Navigate to a case with zero payment schedules', async () => {
      await casePage.navigateTo(CASE_WITH_NO_SCHEDULE_URL);
      await casePage.waitForLoad();
    });

    await test.step("Click the empty-state 'Add Payment Schedule' CTA", async () => {
      await casePage.openModalFromEmptyState();
    });

    await test.step('Verify the modal opens with the correct title and subtitle', async () => {
      expect(await casePage.isModalVisible(), 'Add Payment Schedule modal did not open').toBeTruthy();
      await expect(casePage.modalTitle).toBeVisible();
      await expect(casePage.modalSubtitle).toBeVisible();
    });
  });

  test('pos: open modal from populated-view button', async ({ page }) => {
    await story('AC1: User can open the Add Payment Schedule modal from the populated-view button');
    // Jira: ARW-2579
    // AC: User can click "Add Payment Schedule" from the Button in populated view
    const casePage = new CaseDetailPage(page);

    await test.step('Navigate to a case with an existing payment schedule row', async () => {
      await casePage.navigateTo(CASE_WITH_SCHEDULE_URL);
      await casePage.waitForLoad();
    });

    await test.step("Click the 'Add Payment Schedule' button", async () => {
      await casePage.openModalFromButton();
    });

    await test.step('Verify the modal opens with the correct title and subtitle', async () => {
      expect(await casePage.isModalVisible(), 'Add Payment Schedule modal did not open').toBeTruthy();
      await expect(casePage.modalTitle).toBeVisible();
      await expect(casePage.modalSubtitle).toBeVisible();
    });
  });

  test('err: close modal discards no schedule', async ({ page }) => {
    await story('AC1: Closing the modal without saving discards no schedule');
    // Jira: ARW-2579
    // AC: Modal can be dismissed without creating a schedule
    const casePage = new CaseDetailPage(page);
    let rowCountBefore;

    await test.step('Navigate to a case and open the modal', async () => {
      await casePage.navigateTo(CASE_WITH_SCHEDULE_URL);
      await casePage.waitForLoad();
      rowCountBefore = await casePage.getScheduleRowCount();
      await casePage.openModalFromButton();
    });

    await test.step('Close the modal without saving', async () => {
      await casePage.closeModal();
    });

    await test.step('Verify modal is closed and no new row was added', async () => {
      expect(await casePage.isModalVisible(), 'Modal is still visible after close').toBeFalsy();
      expect(
        await casePage.getScheduleRowCount(),
        'Schedule table row count changed after closing without saving'
      ).toBe(rowCountBefore);
    });
  });

  test('pos: payer dropdown shows only eligible payers', async ({ page }) => {
    await story("AC2: Payer dropdown only includes payers flagged 'Allow Payment Schedule'");
    // Jira: ARW-2579
    // AC: Payer dropdown only includes payers whose payer category is flagged
    // "Allow Payment Schedule"
    const casePage = new CaseDetailPage(page);

    await test.step('Navigate to a case and open the modal', async () => {
      await casePage.navigateTo(CASE_WITH_SCHEDULE_URL);
      await casePage.waitForLoad();
      await casePage.openModalFromButton();
    });

    await test.step('Open the Payer dropdown', async () => {
      await casePage.openPayerDropdown();
    });

    await test.step('Verify only eligible payers are listed', async () => {
      expect(
        await casePage.isPayerOptionVisible(ELIGIBLE_PAYER),
        'Eligible payer missing from Payer dropdown'
      ).toBeTruthy();
      expect(
        await casePage.isPayerOptionVisible(INELIGIBLE_PAYER),
        'Ineligible payer unexpectedly present in Payer dropdown'
      ).toBeFalsy();
    });
  });

  test('err: existing-schedule payer disabled with tooltip', async ({ page }) => {
    await story('AC2: Payers with an existing schedule for this case are disabled');
    // Jira: ARW-2579
    // AC: Payers with an existing schedule for this case are disabled; tooltip
    // reads "A payment schedule already exists for this payer."
    const casePage = new CaseDetailPage(page);

    await test.step('Navigate to a case and open the modal', async () => {
      await casePage.navigateTo(CASE_WITH_SCHEDULE_URL);
      await casePage.waitForLoad();
      await casePage.openModalFromButton();
    });

    await test.step('Open the Payer dropdown', async () => {
      await casePage.openPayerDropdown();
    });

    await test.step('Verify the payer with an existing schedule is disabled', async () => {
      expect(
        await casePage.isPayerOptionDisabled(PAYER_WITH_EXISTING_SCHEDULE),
        'Payer with existing schedule is not disabled'
      ).toBeTruthy();
    });

    await test.step('Verify the tooltip text is shown on hover', async () => {
      const tooltipText = await casePage.getPayerTooltipText(PAYER_WITH_EXISTING_SCHEDULE);
      expect(tooltipText).toContain('A payment schedule already exists for this payer.');
    });
  });

  test('err: no eligible payers shows empty dropdown', async ({ page }) => {
    await story('AC2: No eligible payers results in an empty Payer dropdown');
    // Jira: ARW-2579
    // AC: Payer dropdown only includes payers flagged "Allow Payment Schedule";
    // if none exist, Save must remain disabled
    const casePage = new CaseDetailPage(page);

    await test.step('Navigate to a case with no eligible payers and open the modal', async () => {
      await casePage.navigateTo(CASE_WITH_NO_SCHEDULE_URL);
      await casePage.waitForLoad();
      await casePage.openModalFromEmptyState();
    });

    await test.step('Open the Payer dropdown', async () => {
      await casePage.openPayerDropdown();
    });

    await test.step('Verify the Save button remains disabled', async () => {
      expect(
        await casePage.isSaveButtonEnabled(),
        'Save button should remain disabled when no eligible payers exist'
      ).toBeFalsy();
    });
  });

  test('pos: specific day reveals day selector', async ({ page }) => {
    await story("AC3: Schedule Type 'Specific day of the month' shows a day selector");
    // Jira: ARW-2579
    // AC: Schedule Type "Specific day of the month" shows a Day selector
    const casePage = new CaseDetailPage(page);

    await test.step('Navigate to a case, open the modal, and select an eligible payer', async () => {
      await casePage.navigateTo(CASE_WITH_SCHEDULE_URL);
      await casePage.waitForLoad();
      await casePage.openModalFromButton();
      await casePage.selectPayer(ELIGIBLE_PAYER);
    });

    await test.step("Select 'Specific day of the month' as the schedule type", async () => {
      await casePage.selectScheduleType('Specific day of the month');
    });

    await test.step('Verify the day selector is visible', async () => {
      expect(await casePage.isDaySelectorVisible(), 'Day selector not shown').toBeTruthy();
      expect(
        await casePage.isWeekdaySelectorVisible(),
        "Weekday pattern selector should not be shown for 'Specific day' type"
      ).toBeFalsy();
    });
  });

  test('pos: relative weekday reveals weekday selector', async ({ page }) => {
    await story("AC3: Schedule Type 'Relative weekday' shows a weekday pattern selector");
    // Jira: ARW-2579
    // AC: Schedule Type "Relative weekday" (e.g. 3rd Thursday, last Wednesday)
    // shows a weekday pattern selector
    const casePage = new CaseDetailPage(page);

    await test.step('Navigate to a case, open the modal, and select an eligible payer', async () => {
      await casePage.navigateTo(CASE_WITH_SCHEDULE_URL);
      await casePage.waitForLoad();
      await casePage.openModalFromButton();
      await casePage.selectPayer(ELIGIBLE_PAYER);
    });

    await test.step("Select 'Relative weekday' as the schedule type", async () => {
      await casePage.selectScheduleType('Relative weekday');
    });

    await test.step('Verify the weekday pattern selector is visible', async () => {
      expect(await casePage.isWeekdaySelectorVisible(), 'Weekday pattern selector not shown').toBeTruthy();
      expect(
        await casePage.isDaySelectorVisible(),
        "Day selector should not be shown for 'Relative weekday' type"
      ).toBeFalsy();
    });
  });

  test('pos: all payment methods are selectable', async ({ page }) => {
    await story('AC3: Payment Method supports ACH, Credit Card, Direct Deposit, Personal Check, Other');
    // Jira: ARW-2579
    // AC: Payment Method: ACH, Credit Card, Direct Deposit, Personal Check, Other
    const casePage = new CaseDetailPage(page);
    const expectedMethods = ['ACH', 'Credit Card', 'Direct Deposit', 'Personal Check', 'Other'];

    await test.step('Navigate to a case, open the modal, and select an eligible payer', async () => {
      await casePage.navigateTo(CASE_WITH_SCHEDULE_URL);
      await casePage.waitForLoad();
      await casePage.openModalFromButton();
      await casePage.selectPayer(ELIGIBLE_PAYER);
    });

    await test.step('Open the Payment Method dropdown', async () => {
      await casePage.paymentMethodDropdown.click();
    });

    await test.step('Verify all expected payment methods are present', async () => {
      const availableMethods = await casePage.getPaymentMethodOptions();
      for (const method of expectedMethods) {
        expect(availableMethods, `Payment method '${method}' missing from dropdown`).toContain(method);
      }
    });
  });

  test('pos: auto-pay checkbox toggle and helper text', async ({ page }) => {
    await story('AC3: Auto-Pay Status checkbox toggles and shows helper text');
    // Jira: ARW-2579
    // AC: Auto-Pay Status checkbox with helper text "Indicates whether this payer
    // is set up for auto-pay."
    const casePage = new CaseDetailPage(page);

    await test.step('Navigate to a case, open the modal, and select an eligible payer', async () => {
      await casePage.navigateTo(CASE_WITH_SCHEDULE_URL);
      await casePage.waitForLoad();
      await casePage.openModalFromButton();
      await casePage.selectPayer(ELIGIBLE_PAYER);
    });

    await test.step('Verify the helper text is visible', async () => {
      expect(await casePage.isAutopayHelperTextVisible(), 'Auto-Pay helper text not visible').toBeTruthy();
    });

    await test.step('Toggle the Auto-Pay checkbox on', async () => {
      await casePage.toggleAutopay();
      expect(await casePage.isAutopayChecked(), 'Auto-Pay checkbox did not become checked').toBeTruthy();
    });

    await test.step('Toggle the Auto-Pay checkbox off', async () => {
      await casePage.toggleAutopay();
      expect(await casePage.isAutopayChecked(), 'Auto-Pay checkbox did not become unchecked').toBeFalsy();
    });
  });

  test('err: save disabled until required fields complete', async ({ page }) => {
    await story('AC3: Save button is disabled until all required fields are completed');
    // Jira: ARW-2579
    // AC: Save button disabled until all required fields are completed
    const casePage = new CaseDetailPage(page);

    await test.step('Navigate to a case and open the modal', async () => {
      await casePage.navigateTo(CASE_WITH_SCHEDULE_URL);
      await casePage.waitForLoad();
      await casePage.openModalFromButton();
    });

    await test.step('Verify Save is disabled with no fields filled', async () => {
      expect(await casePage.isSaveButtonEnabled(), 'Save should be disabled initially').toBeFalsy();
    });

    await test.step('Select a payer and verify Save is still disabled', async () => {
      await casePage.selectPayer(ELIGIBLE_PAYER);
      expect(await casePage.isSaveButtonEnabled(), 'Save should still be disabled').toBeFalsy();
    });

    await test.step('Select schedule type and day, verify Save is still disabled', async () => {
      await casePage.selectScheduleType('Specific day of the month');
      await casePage.selectDay('15');
      expect(await casePage.isSaveButtonEnabled(), 'Save should still be disabled').toBeFalsy();
    });

    await test.step('Select payment method and verify Save is still disabled', async () => {
      await casePage.selectPaymentMethod('ACH');
      expect(await casePage.isSaveButtonEnabled(), 'Save should still be disabled').toBeFalsy();
    });

    await test.step('Set Auto-Pay status and verify Save becomes enabled', async () => {
      await casePage.toggleAutopay();
      expect(
        await casePage.isSaveButtonEnabled(),
        'Save should become enabled once all required fields are set'
      ).toBeTruthy();
    });
  });

  test('pos: save schedule success toast and table update', async ({ page }) => {
    await story('AC4: Saving closes the modal, refreshes the table, and shows a success toast');
    // Jira: ARW-2579
    // AC: On save, modal closes, new schedule appears in table, success toast
    // "Payment schedule added successfully." is shown
    const casePage = new CaseDetailPage(page);
    let rowCountBefore;

    await test.step('Navigate to a case and note the current schedule row count', async () => {
      await casePage.navigateTo(CASE_WITH_SCHEDULE_URL);
      await casePage.waitForLoad();
      rowCountBefore = await casePage.getScheduleRowCount();
    });

    await test.step('Open the modal and fill in all required fields', async () => {
      await casePage.openModalFromButton();
      await casePage.selectPayer(ELIGIBLE_PAYER);
      await casePage.selectScheduleType('Specific day of the month');
      await casePage.selectDay('15');
      await casePage.selectPaymentMethod('ACH');
      await casePage.toggleAutopay();
    });

    await test.step('Click Save', async () => {
      expect(await casePage.isSaveButtonEnabled(), 'Save should be enabled with all fields set').toBeTruthy();
      await casePage.clickSave();
    });

    await test.step('Verify the modal closes, table refreshes, and success toast is shown', async () => {
      expect(await casePage.isModalVisible(), 'Modal did not close after save').toBeFalsy();
      expect(
        await casePage.getScheduleRowCount(),
        'New schedule row was not added to the table'
      ).toBe(rowCountBefore + 1);
      expect(await casePage.isSuccessToastVisible(), 'Success toast not shown').toBeTruthy();
    });
  });

  test('err: duplicate schedule prevented for same payer', async ({ page }) => {
    await story('AC4: System prevents saving more than one schedule per payer per case');
    // Jira: ARW-2579
    // AC: System prevents saving more than one payment schedule for the same
    // payer on a case
    const casePage = new CaseDetailPage(page);

    await test.step('Navigate to a case and open the modal', async () => {
      await casePage.navigateTo(CASE_WITH_SCHEDULE_URL);
      await casePage.waitForLoad();
      await casePage.openModalFromButton();
    });

    await test.step('Open the Payer dropdown', async () => {
      await casePage.openPayerDropdown();
    });

    await test.step('Verify the payer with an existing schedule cannot be selected', async () => {
      expect(
        await casePage.isPayerOptionDisabled(PAYER_WITH_EXISTING_SCHEDULE),
        'Payer with an existing schedule should be disabled to prevent duplicates'
      ).toBeTruthy();
    });
  });

  test('perm: viewer role cannot access Add Payment Schedule', async ({ page }) => {
    await story('AC1: Viewer role cannot access Add Payment Schedule');
    // Jira: ARW-2579
    // AC (RBAC): Only authorized roles can create payment schedules; a
    // read-only Viewer should not see or be able to use the entry points
    // TODO: authenticate as a Viewer-role user once role-based test
    // credentials are confirmed for this environment
    const casePage = new CaseDetailPage(page);

    await test.step('Navigate to a case as a Viewer-role user', async () => {
      await casePage.navigateTo(CASE_WITH_SCHEDULE_URL);
      await casePage.waitForLoad();
    });

    await test.step('Verify the Add Payment Schedule entry point is hidden or disabled', async () => {
      const visible = await casePage.populatedViewButton.isVisible();
      const enabled = visible ? await casePage.populatedViewButton.isEnabled() : false;
      expect(
        !visible || !enabled,
        'Viewer role should not be able to access Add Payment Schedule'
      ).toBeTruthy();
    });
  });
});
