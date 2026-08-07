# Manual Test Cases — SCRUM-11: Add "Show Primary Only" Toggle to Facility & Role View

Jira: https://vwiki281-1785763863770.atlassian.net/browse/SCRUM-11
Date: 2026-08-07

## Acceptance Criteria

- AC1: A "Show Primary Only" toggle appears on the Facility & Role View tab
- AC2: The toggle is enabled (on) by default
- AC3: When enabled, only rows where the role is marked as Primary are shown
- AC4: When disabled, all role assignments are shown regardless of primary status
- AC5: The toggle state does not persist — it resets to on on page reload or tab switch
- AC6: The toggle has no effect and is not visible on the User View tab

## Test Cases

### TC-01 | AC1 | Happy Path | High
**Scenario:** "Show Primary Only" toggle is visible on the Facility & Role View tab
**Pre-conditions:** User is logged in as an Org Admin; User Management page is loaded
**Test Data:** N/A

| Step | Action | Expected Result |
|---|---|---|
| 1 | Navigate to the User Management page | User Management page loads with User View tab active by default |
| 2 | Verify the "Facility & Role View" tab is visible and clickable | "Facility & Role View" tab is visible and clickable |
| 3 | Click the "Facility & Role View" tab | Facility & Role View grid loads |
| 4 | Verify the "Show Primary Only" toggle control is visible in the tab header area | "Show Primary Only" toggle is visible with a label |

### TC-02 | AC2 | Happy Path | High
**Scenario:** Toggle is on by default when the tab is first opened
**Pre-conditions:** User is logged in as an Org Admin; has not previously interacted with the toggle this session
**Test Data:** N/A

| Step | Action | Expected Result |
|---|---|---|
| 1 | Navigate to the User Management page | User Management page loads |
| 2 | Click the "Facility & Role View" tab | Facility & Role View grid loads |
| 3 | Verify the "Show Primary Only" toggle is visible | Toggle is visible |
| 4 | Inspect the toggle's checked/aria-checked state | Toggle state is "on" (checked = true) |

### TC-03 | AC3 | Happy Path | High
**Scenario:** Enabling the toggle filters the grid to only Primary-marked rows
**Pre-conditions:** User is logged in as an Org Admin; a user with both Primary and non-Primary role assignments exists across facilities
**Test Data:** Test user with 2 Primary rows and 3 non-Primary rows

| Step | Action | Expected Result |
|---|---|---|
| 1 | Navigate to the Facility & Role View tab | Grid loads with toggle on by default |
| 2 | Verify toggle is in the "on" state | Toggle shows "on" |
| 3 | Read the total row count displayed in the grid | Row count equals 2 (matches Primary rows only) |
| 4 | Verify each visible row's "Primary" column/badge | Every visible row is marked Primary |

### TC-04 | AC4 | Happy Path | High
**Scenario:** Disabling the toggle shows all role assignments regardless of primary status
**Pre-conditions:** Same as TC-03
**Test Data:** Same test user as TC-03 (2 Primary + 3 non-Primary rows)

| Step | Action | Expected Result |
|---|---|---|
| 1 | Navigate to the Facility & Role View tab with toggle on | Grid shows only the 2 Primary rows |
| 2 | Click the "Show Primary Only" toggle to switch it off | Toggle switches to "off" state |
| 3 | Read the total row count displayed in the grid | Row count equals 5 (all Primary + non-Primary rows) |
| 4 | Verify at least one visible row is marked non-Primary | A non-Primary row is present in the grid |

### TC-05 | AC5 | Happy Path | High
**Scenario:** Toggle resets to on after a full page reload
**Pre-conditions:** User is logged in as an Org Admin; on the Facility & Role View tab with toggle switched off
**Test Data:** N/A

| Step | Action | Expected Result |
|---|---|---|
| 1 | On the Facility & Role View tab, click the toggle to switch it off | Toggle shows "off"; all rows visible |
| 2 | Reload the page | Page reloads and User Management page loads again |
| 3 | Click the "Facility & Role View" tab | Grid loads |
| 4 | Inspect the toggle's checked/aria-checked state | Toggle state is "on" again |

### TC-06 | AC5 | Happy Path | High
**Scenario:** Toggle resets to on after switching away to another tab and back
**Pre-conditions:** User is logged in as an Org Admin; on the Facility & Role View tab with toggle switched off
**Test Data:** N/A

| Step | Action | Expected Result |
|---|---|---|
| 1 | On the Facility & Role View tab, click the toggle to switch it off | Toggle shows "off" |
| 2 | Click the "User View" tab | User View tab becomes active |
| 3 | Click the "Facility & Role View" tab again | Facility & Role View grid loads |
| 4 | Inspect the toggle's checked/aria-checked state | Toggle state is "on" again |

### TC-07 | AC6 | Happy Path | Medium
**Scenario:** Toggle is not visible on the User View tab
**Pre-conditions:** User is logged in as an Org Admin
**Test Data:** N/A

| Step | Action | Expected Result |
|---|---|---|
| 1 | Navigate to the User Management page | User View tab is active by default |
| 2 | Verify the tab header area for a "Show Primary Only" control | "Show Primary Only" toggle is not present in the DOM/not visible |

### TC-08 | AC3 | Edge Case | Medium
**Scenario:** Toggle on with a user who has zero Primary role assignments shows an empty grid
**Pre-conditions:** User is logged in as an Org Admin; a test user exists with only non-Primary role assignments
**Test Data:** Test user with 0 Primary rows, 2 non-Primary rows

| Step | Action | Expected Result |
|---|---|---|
| 1 | Navigate to the Facility & Role View tab for the test user | Grid loads with toggle on by default |
| 2 | Read the grid's row count / empty-state message | Grid shows 0 rows and displays an empty-state indicator |
| 3 | Click the toggle to switch it off | Toggle shows "off" |
| 4 | Read the grid's row count | Grid now shows 2 rows |

### TC-09 | AC4 | Edge Case | Low
**Scenario:** Toggling off then back on returns to the original filtered state (idempotency)
**Pre-conditions:** Same as TC-03
**Test Data:** Same test user as TC-03

| Step | Action | Expected Result |
|---|---|---|
| 1 | Navigate to the Facility & Role View tab (toggle on, 2 rows) | Grid shows 2 Primary rows |
| 2 | Click toggle off | Grid shows 5 rows |
| 3 | Click toggle on again | Toggle shows "on" |
| 4 | Read the grid's row count | Grid shows 2 Primary rows again |

### TC-10 | AC6 | Negative | Medium
**Scenario:** Toggling on the Facility & Role View tab does not affect the User View tab's rows
**Pre-conditions:** User is logged in as an Org Admin; toggle switched off on Facility & Role View tab
**Test Data:** N/A

| Step | Action | Expected Result |
|---|---|---|
| 1 | On the Facility & Role View tab, note the row count with toggle off | Row count recorded (e.g. 5) |
| 2 | Click the "User View" tab | User View grid loads |
| 3 | Read the User View tab's row count | Row count is unchanged from before visiting Facility & Role View |

### TC-11 | AC1 | Edge Case | Low
**Scenario:** Toggle is keyboard-operable and exposes an accessible name
**Pre-conditions:** User is logged in as an Org Admin; on the Facility & Role View tab
**Test Data:** N/A

| Step | Action | Expected Result |
|---|---|---|
| 1 | Navigate to the Facility & Role View tab | Grid and toggle load |
| 2 | Tab (keyboard) focus to the toggle control | Toggle receives visible focus |
| 3 | Press Space/Enter to activate the toggle | Toggle state switches (on → off) |
| 4 | Inspect the toggle's accessible name (aria-label/label text) | Accessible name is present and describes "Show Primary Only" |

### TC-12 | AC1 | RBAC | High
**Scenario:** A Viewer-role user cannot access the Facility & Role View tab (or its toggle)
**Pre-conditions:** User is logged in with a Viewer role account
**Test Data:** Viewer-role credentials

| Step | Action | Expected Result |
|---|---|---|
| 1 | Log in as a Viewer-role user | Login succeeds, User Management page loads (or is restricted per role policy) |
| 2 | Attempt to click the "Facility & Role View" tab | Tab is disabled, hidden, or access is denied per role policy |
| 3 | Verify the "Show Primary Only" toggle is not accessible | Toggle is not visible/interactable for this role |
