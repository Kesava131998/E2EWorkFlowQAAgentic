# Manual Test Cases — SCRUM-65: BillerActivity Report — Split "Overdue Tasks" into Two Columns

Source: Jira SCRUM-65 description (no formal AC1/AC2 labels in ticket — three bullet requirements treated as AC1–AC3 below).

- **AC1**: The "Overdue Tasks" column no longer appears on the Biller Activity Report (split into two columns instead).
- **AC2**: A biller with no overdue tasks of a given type shows `0` in that column.
- **AC3**: `0` shows in green, all other numbers in red.

| # | AC | Type | Priority | Scenario | Pre-conditions | Test Data | Steps | Expected Result |
|---|----|------|----------|----------|-----------------|-----------|-------|------------------|
| 1 | AC1 | Happy Path | High | Legacy combined "Overdue Tasks" column is removed from the report | User is logged in and navigated to `/tasks` Biller Activity Report | None | 1. Navigate to Biller Activity Report page.
2. Verify the report grid header row is visible.
3. Read all grid column header names. | 1. Biller Activity Report page loads.
2. Grid header row is visible.
3. The header list does NOT contain a column named "Overdue Tasks". |
| 2 | AC1 | Happy Path | High | Two new split columns are present in the grid headers | User is logged in and navigated to Biller Activity Report | None | 1. Navigate to Biller Activity Report page.
2. Verify the report grid header row is visible.
3. Read all grid column header names.
4. Check header list for "Overdue Open Balance Tasks".
5. Check header list for "Overdue Overpayment Tasks". | 1. Biller Activity Report page loads.
2. Grid header row is visible.
3. Header names are read successfully.
4. "Overdue Open Balance Tasks" column header is present.
5. "Overdue Overpayment Tasks" column header is present. |
| 3 | AC2 | Happy Path | High | Biller with zero overdue open-balance tasks shows 0 | User is logged in, report loaded, a biller with no overdue open-balance tasks exists in the grid | Biller name with 0 overdue open-balance tasks | 1. Navigate to Biller Activity Report page.
2. Locate the grid row for the test biller.
3. Read the value of the `overdueOpenBalanceTaskCount` cell for that biller. | 1. Report page loads.
2. Row for the biller is found in the grid.
3. Cell value reads `0`. |
| 4 | AC2 | Happy Path | High | Biller with zero overdue overpayment tasks shows 0 | User is logged in, report loaded, a biller with no overdue overpayment tasks exists in the grid | Biller name with 0 overdue overpayment tasks | 1. Navigate to Biller Activity Report page.
2. Locate the grid row for the test biller.
3. Read the value of the `overdueOverpaymentTaskCount` cell for that biller. | 1. Report page loads.
2. Row for the biller is found in the grid.
3. Cell value reads `0`. |
| 5 | AC2 | Edge Case | Medium | Biller with non-zero counts in both split columns shows independent values | User is logged in, report loaded, a biller with overdue tasks of both types exists | Biller name with e.g. 3 overdue open-balance and 5 overdue overpayment tasks | 1. Navigate to Biller Activity Report page.
2. Locate the grid row for the test biller.
3. Read the value of the `overdueOpenBalanceTaskCount` cell.
4. Read the value of the `overdueOverpaymentTaskCount` cell. | 1. Report page loads.
2. Row for the biller is found.
3. Open-balance cell shows its own independent count (not merged with overpayment count).
4. Overpayment cell shows its own independent count (not merged with open-balance count). |
| 6 | AC3 | Happy Path | High | Zero value in overdue open-balance column renders in green | User is logged in, report loaded, biller with 0 overdue open-balance tasks exists | Biller name with 0 overdue open-balance tasks | 1. Navigate to Biller Activity Report page.
2. Locate the grid row for the test biller.
3. Read the computed text color of the `overdueOpenBalanceTaskCount` cell. | 1. Report page loads.
2. Row is found.
3. Computed color corresponds to the green color token (not red). |
| 7 | AC3 | Happy Path | High | Non-zero value in overdue open-balance column renders in red | User is logged in, report loaded, biller with >0 overdue open-balance tasks exists | Biller name with 2 overdue open-balance tasks | 1. Navigate to Biller Activity Report page.
2. Locate the grid row for the test biller.
3. Read the computed text color of the `overdueOpenBalanceTaskCount` cell. | 1. Report page loads.
2. Row is found.
3. Computed color corresponds to the red color token (not green). |
| 8 | AC3 | Negative | Medium | Color coding rule applies independently to the overpayment column too | User is logged in, report loaded, biller with 0 overdue overpayment tasks and biller with >0 overdue overpayment tasks both exist | Biller A: 0 overpayment tasks; Biller B: 4 overpayment tasks | 1. Navigate to Biller Activity Report page.
2. Locate the grid row for Biller A.
3. Read the computed text color of Biller A's `overdueOverpaymentTaskCount` cell.
4. Locate the grid row for Biller B.
5. Read the computed text color of Biller B's `overdueOverpaymentTaskCount` cell. | 1. Report page loads.
2. Row for Biller A found.
3. Biller A's cell color is green (value is 0).
4. Row for Biller B found.
5. Biller B's cell color is red (value is non-zero), confirming the 0=green/non-zero=red rule applies to the overpayment column independently of the open-balance column. |
