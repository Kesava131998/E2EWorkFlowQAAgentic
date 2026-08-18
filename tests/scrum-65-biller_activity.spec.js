const { test, expect } = require('@playwright/test');
const { epic, feature, story } = require('allure-js-commons');
const { BillerActivityPage } = require('../pages/biller_activity_page');
const { settings } = require('../config/settings');

// TODO: replace with real biller fixtures once test data is confirmed for this environment
const BILLER_WITH_ZERO_OPEN_BALANCE = 'TODO-biller-zero-open-balance';
const BILLER_WITH_ZERO_OVERPAYMENT = 'TODO-biller-zero-overpayment';
const BILLER_WITH_BOTH_TYPES = 'TODO-biller-both-overdue-types';
const BILLER_WITH_NONZERO_OPEN_BALANCE = 'TODO-biller-nonzero-open-balance';
const BILLER_A_ZERO_OVERPAYMENT = 'TODO-biller-a-zero-overpayment';
const BILLER_B_NONZERO_OVERPAYMENT = 'TODO-biller-b-nonzero-overpayment';

const OPEN_BALANCE_COLUMN = 'overdueOpenBalanceTaskCount';
const OVERPAYMENT_COLUMN = 'overdueOverpaymentTaskCount';
const LEGACY_COLUMN_HEADER = 'Overdue Tasks';
const OPEN_BALANCE_HEADER = 'Overdue Open Balance Tasks';
const OVERPAYMENT_HEADER = 'Overdue Overpayment Tasks';

function isGreen(rgbColor) {
  const [r, g, b] = rgbColor.match(/\d+/g).map(Number);
  return g > r && g > b;
}

function isRed(rgbColor) {
  const [r, g, b] = rgbColor.match(/\d+/g).map(Number);
  return r > g && r > b;
}

test.describe('SCRUM-65: BillerActivity Report — Split Overdue Tasks into Two Columns', () => {
  test.beforeEach(async () => {
    await epic('SCRUM-65: BillerActivity Report — Split Overdue Tasks into Two Columns');
    await feature('biller_activity');
  });

  test('pos: verify legacy Overdue Tasks column is removed from Biller Activity Report', async ({ page }) => {
    await story('AC1: The Overdue Tasks column no longer appears on the Biller Activity Report');
    // Jira: SCRUM-65
    // AC: The Overdue Tasks column no longer appears on the Biller Activity Report
    const billerActivityPage = new BillerActivityPage(page);

    await test.step('Navigate to Biller Activity Report page', async () => {
      await billerActivityPage.navigateTo(`${settings.BASE_URL}/tasks`);
      await expect(billerActivityPage.billerActivityReportBtn).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await billerActivityPage.clickBillerActivityReport();
    });

    await test.step('Verify the report grid header row is visible', async () => {
      await billerActivityPage.waitForReportGridVisible();
    });

    await test.step('Verify legacy "Overdue Tasks" column header is not present', async () => {
      const headers = await billerActivityPage.getColumnHeaderNames();
      expect(headers, 'Legacy "Overdue Tasks" column should no longer be present').not.toContain(LEGACY_COLUMN_HEADER);
    });
  });

  test('pos: verify Overdue Open Balance Tasks and Overdue Overpayment Tasks columns are present', async ({ page }) => {
    await story('AC1: The Overdue Tasks column is split into two independent columns');
    // Jira: SCRUM-65
    // AC: The Overdue Tasks column no longer appears on the Biller Activity Report
    const billerActivityPage = new BillerActivityPage(page);

    await test.step('Navigate to Biller Activity Report page', async () => {
      await billerActivityPage.navigateTo(`${settings.BASE_URL}/tasks`);
      await expect(billerActivityPage.billerActivityReportBtn).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await billerActivityPage.clickBillerActivityReport();
    });

    await test.step('Verify the report grid header row is visible', async () => {
      await billerActivityPage.waitForReportGridVisible();
    });

    await test.step('Verify both split columns are present in the grid headers', async () => {
      const headers = await billerActivityPage.getColumnHeaderNames();
      expect(headers, `"${OPEN_BALANCE_HEADER}" column header missing`).toContain(OPEN_BALANCE_HEADER);
      expect(headers, `"${OVERPAYMENT_HEADER}" column header missing`).toContain(OVERPAYMENT_HEADER);
    });
  });

  test('pos: verify overdue open balance task count shows zero for biller with no overdue tasks', async ({ page }) => {
    await story('AC2: A biller with no overdue tasks of a given type shows 0 in that column');
    // Jira: SCRUM-65
    // AC: A biller with no overdue tasks of a given type shows 0 in that column
    const billerActivityPage = new BillerActivityPage(page);

    await test.step('Navigate to Biller Activity Report page', async () => {
      await billerActivityPage.navigateTo(`${settings.BASE_URL}/tasks`);
      await expect(billerActivityPage.billerActivityReportBtn).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await billerActivityPage.clickBillerActivityReport();
      await billerActivityPage.waitForReportGridVisible();
    });

    await test.step('Verify the open balance task count is 0 for the test biller', async () => {
      const count = await billerActivityPage.getColumnValueForUser(BILLER_WITH_ZERO_OPEN_BALANCE, OPEN_BALANCE_COLUMN);
      expect(count).toBe(0);
    });
  });

  test('pos: verify overdue overpayment task count shows zero for biller with no overdue tasks', async ({ page }) => {
    await story('AC2: A biller with no overdue tasks of a given type shows 0 in that column');
    // Jira: SCRUM-65
    // AC: A biller with no overdue tasks of a given type shows 0 in that column
    const billerActivityPage = new BillerActivityPage(page);

    await test.step('Navigate to Biller Activity Report page', async () => {
      await billerActivityPage.navigateTo(`${settings.BASE_URL}/tasks`);
      await expect(billerActivityPage.billerActivityReportBtn).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await billerActivityPage.clickBillerActivityReport();
      await billerActivityPage.waitForReportGridVisible();
    });

    await test.step('Verify the overpayment task count is 0 for the test biller', async () => {
      const count = await billerActivityPage.getColumnValueForUser(BILLER_WITH_ZERO_OVERPAYMENT, OVERPAYMENT_COLUMN);
      expect(count).toBe(0);
    });
  });

  test('pos: verify overdue open balance and overpayment counts are independent for a biller with both types', async ({ page }) => {
    await story('AC2: Split columns show independent counts, not a merged total');
    // Jira: SCRUM-65
    // AC: A biller with no overdue tasks of a given type shows 0 in that column
    const billerActivityPage = new BillerActivityPage(page);

    await test.step('Navigate to Biller Activity Report page', async () => {
      await billerActivityPage.navigateTo(`${settings.BASE_URL}/tasks`);
      await expect(billerActivityPage.billerActivityReportBtn).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await billerActivityPage.clickBillerActivityReport();
      await billerActivityPage.waitForReportGridVisible();
    });

    await test.step('Verify both columns show their own independent counts for the test biller', async () => {
      const openBalanceCount = await billerActivityPage.getColumnValueForUser(BILLER_WITH_BOTH_TYPES, OPEN_BALANCE_COLUMN);
      const overpaymentCount = await billerActivityPage.getColumnValueForUser(BILLER_WITH_BOTH_TYPES, OVERPAYMENT_COLUMN);
      expect(openBalanceCount).toBeGreaterThan(0);
      expect(overpaymentCount).toBeGreaterThan(0);
      expect(openBalanceCount, 'Split columns should not report the same merged total').not.toBe(overpaymentCount);
    });
  });

  test('pos: verify zero overdue open balance count renders in green', async ({ page }) => {
    await story('AC3: 0 shows in green, all other numbers in red');
    // Jira: SCRUM-65
    // AC: 0 shows in green, all other numbers in red
    const billerActivityPage = new BillerActivityPage(page);

    await test.step('Navigate to Biller Activity Report page', async () => {
      await billerActivityPage.navigateTo(`${settings.BASE_URL}/tasks`);
      await expect(billerActivityPage.billerActivityReportBtn).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await billerActivityPage.clickBillerActivityReport();
      await billerActivityPage.waitForReportGridVisible();
    });

    await test.step('Verify the zero-value open balance cell renders in green', async () => {
      const color = await billerActivityPage.getColumnCellColorForUser(BILLER_WITH_ZERO_OPEN_BALANCE, OPEN_BALANCE_COLUMN);
      expect(isGreen(color), `Expected green text color for a 0 value, got ${color}`).toBeTruthy();
    });
  });

  test('pos: verify non-zero overdue open balance count renders in red', async ({ page }) => {
    await story('AC3: 0 shows in green, all other numbers in red');
    // Jira: SCRUM-65
    // AC: 0 shows in green, all other numbers in red
    const billerActivityPage = new BillerActivityPage(page);

    await test.step('Navigate to Biller Activity Report page', async () => {
      await billerActivityPage.navigateTo(`${settings.BASE_URL}/tasks`);
      await expect(billerActivityPage.billerActivityReportBtn).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await billerActivityPage.clickBillerActivityReport();
      await billerActivityPage.waitForReportGridVisible();
    });

    await test.step('Verify the non-zero open balance cell renders in red', async () => {
      const color = await billerActivityPage.getColumnCellColorForUser(BILLER_WITH_NONZERO_OPEN_BALANCE, OPEN_BALANCE_COLUMN);
      expect(isRed(color), `Expected red text color for a non-zero value, got ${color}`).toBeTruthy();
    });
  });

  test('err: verify overdue overpayment column follows the green/red color rule independently of the open balance column', async ({ page }) => {
    await story('AC3: 0 shows in green, all other numbers in red — applies to both split columns independently');
    // Jira: SCRUM-65
    // AC: 0 shows in green, all other numbers in red
    const billerActivityPage = new BillerActivityPage(page);

    await test.step('Navigate to Biller Activity Report page', async () => {
      await billerActivityPage.navigateTo(`${settings.BASE_URL}/tasks`);
      await expect(billerActivityPage.billerActivityReportBtn).toBeVisible({ timeout: settings.PAGE_LOAD_TIMEOUT });
      await billerActivityPage.clickBillerActivityReport();
      await billerActivityPage.waitForReportGridVisible();
    });

    await test.step('Verify the zero-value overpayment cell renders in green', async () => {
      const color = await billerActivityPage.getColumnCellColorForUser(BILLER_A_ZERO_OVERPAYMENT, OVERPAYMENT_COLUMN);
      expect(isGreen(color), `Expected green text color for a 0 value, got ${color}`).toBeTruthy();
    });

    await test.step('Verify the non-zero overpayment cell renders in red', async () => {
      const color = await billerActivityPage.getColumnCellColorForUser(BILLER_B_NONZERO_OVERPAYMENT, OVERPAYMENT_COLUMN);
      expect(isRed(color), `Expected red text color for a non-zero value, got ${color}`).toBeTruthy();
    });
  });
});
