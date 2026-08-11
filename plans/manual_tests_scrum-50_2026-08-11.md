# Manual Test Cases — SCRUM-50: Add "Show Primary Only" Toggle to Facility & Role View

**Jira**: https://vwiki281-1785763863770.atlassian.net/browse/SCRUM-50
**Module**: facility_role
**Date**: 2026-08-11

## Acceptance Criteria

- AC1: A "Show Primary Only" toggle appears on the Facility & Role View tab
- AC2: The toggle is enabled (on) by default
- AC3: When enabled, only rows where the role is marked as Primary are shown
- AC4: When disabled, all role assignments are shown regardless of primary status
- AC5: The toggle state does not persist — it resets to on on page reload or tab switch
- AC6: The toggle has no effect and is not visible on the User View tab

## Test Cases

| # | AC | Type | Priority | Scenario | Pre-conditions | Test Data | Steps | Expected Result |
|---|----|------|----------|----------|-----------------|-----------|-------|------------------|
| 1 | AC1 | Happy Path | High | Toggle is present on Facility & Role View tab | User is logged into RevFlow and has opened a case with facility/role assignments | N/A | 1. Navigate to the case detail page.
2. Verify the "Facility & Role View" tab is visible.
3. Click on the "Facility & Role View" tab.
4. Verify the "Show Primary Only" toggle control is visible on the tab. | 1. Case detail page loads successfully.
2. "Facility & Role View" tab is visible.
3. "Facility & Role View" tab becomes active.
4. "Show Primary Only" toggle is visible on the tab. |
| 2 | AC2 | Happy Path | High | Toggle is enabled (on) by default when tab is opened | User is logged into RevFlow and has opened a case with facility/role assignments | N/A | 1. Navigate to the case detail page.
2. Click on the "Facility & Role View" tab.
3. Verify the "Show Primary Only" toggle control is visible.
4. Read the current state (checked/aria-pressed) of the toggle. | 1. Case detail page loads successfully.
2. "Facility & Role View" tab becomes active.
3. "Show Primary Only" toggle is visible.
4. Toggle state is "on"/checked by default. |
| 3 | AC3 | Happy Path | High | Enabling the toggle filters the grid to Primary rows only | User is on the "Facility & Role View" tab; case has a mix of Primary and non-Primary role rows | Case with at least 1 Primary row and 1 non-Primary row | 1. Navigate to the case detail page and open the "Facility & Role View" tab.
2. Verify the "Show Primary Only" toggle is on by default.
3. Note the total row count in the grid.
4. For each visible row, verify the "Primary" indicator/column value. | 1. Case detail page loads successfully.
2. Toggle is confirmed "on".
3. Row count is captured (baseline).
4. Every visible row has its Primary indicator set to true/"Primary". |
| 4 | AC4 | Happy Path | High | Disabling the toggle shows all role assignments regardless of Primary status | User is on the "Facility & Role View" tab; case has a mix of Primary and non-Primary role rows | Case with at least 1 Primary row and 1 non-Primary row | 1. Navigate to the case detail page and open the "Facility & Role View" tab.
2. Verify the "Show Primary Only" toggle is on by default.
3. Click the "Show Primary Only" toggle to turn it off.
4. Verify the toggle state is now "off"/unchecked.
5. Verify the grid row count. | 1. Case detail page loads successfully.
2. Toggle is confirmed "on".
3. Toggle click is registered.
4. Toggle state changes to "off"/unchecked.
5. Grid displays all role assignment rows, including non-Primary rows. |
| 5 | AC3, AC4 | Edge Case | Medium | Toggle behavior when case has no Primary role assignments | User is on the "Facility & Role View" tab; case has only non-Primary role rows | Case with 0 Primary rows, at least 1 non-Primary row | 1. Navigate to the case detail page and open the "Facility & Role View" tab.
2. Verify the "Show Primary Only" toggle is on by default.
3. Verify the grid content/empty state with the toggle on.
4. Click the toggle to turn it off.
5. Verify the grid content with the toggle off. | 1. Case detail page loads successfully.
2. Toggle is confirmed "on".
3. Grid shows an empty state (no rows) since no row is Primary.
4. Toggle state changes to "off".
5. Grid now displays all non-Primary role rows. |
| 6 | AC3, AC4 | Edge Case | Medium | Toggle behavior when every role assignment is Primary | User is on the "Facility & Role View" tab; case has only Primary role rows | Case where all rows are marked Primary | 1. Navigate to the case detail page and open the "Facility & Role View" tab.
2. Verify the "Show Primary Only" toggle is on by default.
3. Note the row count with toggle on.
4. Click the toggle to turn it off.
5. Note the row count with toggle off. | 1. Case detail page loads successfully.
2. Toggle is confirmed "on".
3. Row count equals the total number of Primary rows.
4. Toggle state changes to "off".
5. Row count is unchanged (identical set), since all rows are already Primary. |
| 7 | AC5 | Happy Path | Medium | Toggle resets to on after a page reload | User is on the "Facility & Role View" tab | N/A | 1. Navigate to the case detail page and open the "Facility & Role View" tab.
2. Click the toggle to turn it off.
3. Verify the toggle state is "off".
4. Reload the page.
5. Navigate back to the "Facility & Role View" tab.
6. Verify the toggle state. | 1. Case detail page loads successfully.
2. Toggle click is registered.
3. Toggle state is confirmed "off".
4. Page reload completes.
5. "Facility & Role View" tab becomes active.
6. Toggle state is reset to "on". |
| 8 | AC5 | Happy Path | Medium | Toggle resets to on after switching away from and back to the tab | User is on the "Facility & Role View" tab; case detail page has at least one other tab (e.g. "User View") | N/A | 1. Navigate to the case detail page and open the "Facility & Role View" tab.
2. Click the toggle to turn it off.
3. Verify the toggle state is "off".
4. Click on the "User View" tab.
5. Click back on the "Facility & Role View" tab.
6. Verify the toggle state. | 1. Case detail page loads successfully.
2. Toggle click is registered.
3. Toggle state is confirmed "off".
4. "User View" tab becomes active.
5. "Facility & Role View" tab becomes active again.
6. Toggle state is reset to "on". |
| 9 | AC6 | Negative | High | "Show Primary Only" toggle is not visible on the User View tab | User is logged into RevFlow and has opened a case | N/A | 1. Navigate to the case detail page.
2. Click on the "User View" tab.
3. Verify the "User View" tab is active.
4. Search the tab content for the "Show Primary Only" toggle control. | 1. Case detail page loads successfully.
2. Tab click is registered.
3. "User View" tab is active.
4. "Show Primary Only" toggle is not present/not visible on the "User View" tab. |
| 10 | AC6 | Negative | Medium | Toggling "Show Primary Only" on the Facility & Role View tab has no effect on User View tab data | User is on the "Facility & Role View" tab; case has a mix of Primary and non-Primary role rows | Case with at least 1 Primary row and 1 non-Primary row | 1. Navigate to the case detail page and open the "Facility & Role View" tab.
2. Note the row count on the "User View" tab before toggling (switch tabs to capture baseline, then return).
3. On the "Facility & Role View" tab, click the toggle to turn it off (all rows shown).
4. Click on the "User View" tab.
5. Verify the row count on the "User View" tab. | 1. Case detail page loads successfully.
2. Baseline "User View" row count is captured.
3. Toggle state changes to "off" on "Facility & Role View" tab.
4. "User View" tab becomes active.
5. "User View" row count is unchanged from the baseline — unaffected by the Facility & Role View toggle. |
