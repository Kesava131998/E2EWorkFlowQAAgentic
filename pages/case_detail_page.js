const { test } = require('@playwright/test');
const { BasePage } = require('./base_page');
const { settings } = require('../config/settings');

/** Page object for the Case Detail view, including the Payment Schedule modal (ARW-2579). */
class CaseDetailPage extends BasePage {
  constructor(page) {
    super(page);
    this.emptyStateCta = page.getByRole('button', { name: 'Add Payment Schedule' });
    this.populatedViewButton = page.getByRole('button', { name: 'Add Payment Schedule' });
    this.scheduleTable = page.locator("[data-testid='payment-schedule-table']");
    this.scheduleTableRows = this.scheduleTable.locator('tbody tr');

    this.modal = page.locator("[data-testid='add-payment-schedule-modal']");
    this.modalTitle = this.modal.getByText('Add Payment Schedule', { exact: false });
    this.modalSubtitle = this.modal.getByText(
      'Define the expected payment timing and method for a payer.',
      { exact: false }
    );
    this.modalCloseButton = this.modal.getByRole('button', { name: 'Close' });

    this.payerDropdown = this.modal.locator("[data-testid='payer-select']");
    this.payerOptions = this.modal.locator("[data-testid='payer-select'] [role='option']");

    this.scheduleTypeDropdown = this.modal.locator("[data-testid='schedule-type-select']");
    this.daySelector = this.modal.locator("[data-testid='schedule-day-selector']");
    this.weekdaySelector = this.modal.locator("[data-testid='schedule-weekday-selector']");

    this.paymentMethodDropdown = this.modal.locator("[data-testid='payment-method-select']");
    this.paymentMethodOptions = this.modal.locator(
      "[data-testid='payment-method-select'] [role='option']"
    );

    this.autopayCheckbox = this.modal.locator("[data-testid='autopay-checkbox']");
    this.autopayHelperText = this.modal.getByText(
      'Indicates whether this payer is set up for auto-pay.',
      { exact: false }
    );

    this.saveButton = this.modal.getByRole('button', { name: 'Save' });
    this.successToast = page.getByText('Payment schedule added successfully.');
  }

  async openModalFromEmptyState() {
    await test.step('Open Add Payment Schedule modal from empty-state CTA', async () => {
      await this.emptyStateCta.click();
    });
  }

  async openModalFromButton() {
    await test.step('Open Add Payment Schedule modal from populated-view button', async () => {
      await this.populatedViewButton.click();
    });
  }

  async isModalVisible() {
    return this.modal.isVisible();
  }

  async closeModal() {
    await test.step('Close Add Payment Schedule modal', async () => {
      await this.modalCloseButton.click();
    });
  }

  async getScheduleRowCount() {
    return this.scheduleTableRows.count();
  }

  async selectPayer(payerName) {
    await test.step(`Select payer ${payerName}`, async () => {
      await this.payerDropdown.click();
      await this.modal.getByRole('option', { name: payerName }).click();
    });
  }

  async openPayerDropdown() {
    await test.step('Open payer dropdown', async () => {
      await this.payerDropdown.click();
    });
  }

  async isPayerOptionVisible(payerName) {
    return this.modal.getByRole('option', { name: payerName }).isVisible();
  }

  async isPayerOptionDisabled(payerName) {
    return this.modal.getByRole('option', { name: payerName }).isDisabled();
  }

  async getPayerTooltipText(payerName) {
    return test.step(`Get tooltip text for disabled payer ${payerName}`, async () => {
      const option = this.modal.getByRole('option', { name: payerName });
      await option.hover();
      const tooltip = this.page.locator("[role='tooltip']");
      await tooltip.waitFor({ state: 'visible', timeout: settings.SHORT_TIMEOUT });
      return tooltip.innerText();
    });
  }

  async selectScheduleType(scheduleType) {
    await test.step(`Select schedule type ${scheduleType}`, async () => {
      await this.scheduleTypeDropdown.click();
      await this.modal.getByRole('option', { name: scheduleType }).click();
    });
  }

  async isDaySelectorVisible() {
    return this.daySelector.isVisible();
  }

  async isWeekdaySelectorVisible() {
    return this.weekdaySelector.isVisible();
  }

  async selectDay(day) {
    await test.step(`Select day ${day}`, async () => {
      await this.daySelector.selectOption({ label: day });
    });
  }

  async selectWeekdayPattern(pattern) {
    await test.step(`Select weekday pattern ${pattern}`, async () => {
      await this.weekdaySelector.selectOption({ label: pattern });
    });
  }

  async selectPaymentMethod(method) {
    await test.step(`Select payment method ${method}`, async () => {
      await this.paymentMethodDropdown.click();
      await this.modal.getByRole('option', { name: method }).click();
    });
  }

  async getPaymentMethodOptions() {
    return this.paymentMethodOptions.allInnerTexts();
  }

  async toggleAutopay() {
    await test.step('Toggle Auto-Pay checkbox', async () => {
      await this.autopayCheckbox.click();
    });
  }

  async isAutopayChecked() {
    return this.autopayCheckbox.isChecked();
  }

  async isAutopayHelperTextVisible() {
    return this.autopayHelperText.isVisible();
  }

  async isSaveButtonEnabled() {
    return this.saveButton.isEnabled();
  }

  async clickSave() {
    await test.step('Click Save', async () => {
      await this.saveButton.click();
    });
  }

  async isSuccessToastVisible() {
    return this.successToast.isVisible();
  }
}

module.exports = { CaseDetailPage };
