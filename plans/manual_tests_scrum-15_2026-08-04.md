# Manual Test Cases — SCRUM-15: [FE] - Month Over Month (MOM) Report

| Field | Value |
|-------|-------|
| Ticket | [SCRUM-15](https://vwiki281-1785763863770.atlassian.net/browse/SCRUM-15) |
| Summary | [FE] - Month Over Month (MOM) Report |
| Module | `mom_report` (AR Reports) |
| Status | To Do |
| Priority | Medium |
| Date derived | 2026-08-04 |
| Application | RevFlow — https://revflow-dev.axgsolutions.com/ |
| Swagger / OpenAPI | Not configured for this project — test cases derived from ticket context only |
| Total cases | 26 |

## Acceptance Criteria Index

| AC | Text |
|----|------|
| AC1 | "MOM Report" appears in the AR Reports left nav below "Percent Collected Trend." |
| AC2 | Rows represent service months; columns represent posting months (chronological, oldest → most recent). |
| AC3 | Cells are only populated where posting month is strictly after the service month; all other cells are blank. |
| AC4 | Each cell applies a "Transactions Within" filter scoped to the number of months between that row's service month and that column's posting month. |
| AC5 | Posting date columns begin 1 month after the selected service date range start and end 1 month after the service date range end. |
| AC6 | Time range toggle (6 / 12 / 18 / Custom) controls the service date range, which determines the posting date columns shown. |
| AC7 | 12 months is the selected default. |
| AC8 | Custom time range allows selecting up to 24 months of service dates. |
| AC9 | Future service dates cannot be selected. |
| AC10 | Write-offs and Overpayments controls behave identically to Percent Collected Trend. |
| AC11 | No "Transactions Within" filter is present on this report. |
| AC12 | No grouping selector is present on this report. |
| AC13 | Global Facility Filter affects the report. |
| AC14 | Report can be exported in the pivot layout with service months as rows and posting months as columns. |
| AC15 | A new card is on the reports landing page which navigates to the MOM report. |

## Coverage Matrix

| Type | Count |
|------|-------|
| Happy Path | 15 |
| Negative | 5 |
| Edge Case | 4 |
| RBAC / Permission | 2 |
| **Total** | **26** |

---

## Test Cases

### TC-01 — MOM Report entry is present in AR Reports left nav below Percent Collected Trend

| Field | Value |
|-------|-------|
| **AC** | AC1 |
| **Type** | Happy Path |
| **Priority** | High |
| **Pre-conditions** | 1. Navigate to `https://revflow-dev.axgsolutions.com/`. 2. Signed in via "Sign in with Microsoft" as a user with the AR Reports permission. |
| **Test Data** | Nav label: `MOM Report`; sibling label: `Percent Collected Trend` |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Verify the primary left navigation container is visible | 1. Left navigation container is rendered and visible |
| 2 | Verify the "AR Reports" nav section is visible and enabled | 2. "AR Reports" section entry is visible and enabled |
| 3 | Click the "AR Reports" nav section | 3. Section expands and its child report links become visible |
| 4 | Verify the "Percent Collected Trend" child link is visible | 4. "Percent Collected Trend" link is visible within AR Reports |
| 5 | Verify the "MOM Report" child link is visible | 5. "MOM Report" link is visible within AR Reports |
| 6 | Read the ordered list of AR Reports child link labels and locate the index of both links | 6. Index of "MOM Report" is exactly one greater than the index of "Percent Collected Trend" (MOM Report sits directly below it) |

---

### TC-02 — Clicking the MOM Report nav entry loads the MOM Report page

| Field | Value |
|-------|-------|
| **AC** | AC1 |
| **Type** | Happy Path |
| **Priority** | High |
| **Pre-conditions** | 1. Signed in with AR Reports permission. 2. AR Reports nav section is expanded. |
| **Test Data** | Nav label: `MOM Report` |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Verify the "MOM Report" nav link is visible and enabled | 1. Link is visible and enabled |
| 2 | Click the "MOM Report" nav link | 2. Navigation is triggered and the page begins loading |
| 3 | Wait for the network to become idle | 3. All report data requests complete |
| 4 | Verify the page heading text | 4. Page heading reads "MOM Report" |
| 5 | Verify the "MOM Report" nav link carries the active/selected state | 5. "MOM Report" nav link is highlighted as the active route |
| 6 | Verify the pivot report grid is visible | 6. Pivot report grid is rendered and visible |

---

### TC-03 — Reports landing page shows a MOM Report card that navigates to the report

| Field | Value |
|-------|-------|
| **AC** | AC15 |
| **Type** | Happy Path |
| **Priority** | High |
| **Pre-conditions** | 1. Signed in with AR Reports permission. 2. On the Reports landing page. |
| **Test Data** | Card title: `MOM Report` |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Navigate to the Reports landing page | 1. Reports landing page loads and the report card grid is visible |
| 2 | Verify a card titled "MOM Report" is visible | 2. "MOM Report" card is visible in the card grid |
| 3 | Verify the "MOM Report" card is enabled/clickable | 3. Card is enabled and exposes a clickable affordance |
| 4 | Click the "MOM Report" card | 4. Navigation is triggered to the MOM Report route |
| 5 | Wait for the network to become idle | 5. Report page data requests complete |
| 6 | Verify the page heading | 6. Page heading reads "MOM Report" and the pivot grid is visible |

---

### TC-04 — Pivot grid renders service months as rows and posting months as columns

| Field | Value |
|-------|-------|
| **AC** | AC2 |
| **Type** | Happy Path |
| **Priority** | High |
| **Pre-conditions** | 1. Signed in with AR Reports permission. 2. On the MOM Report page with the default 12-month range applied. |
| **Test Data** | Default range: 12 months |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Verify the pivot grid is visible | 1. Pivot grid container is visible |
| 2 | Verify the row header column is visible | 2. Row header column is visible and labelled for Service Date / Service Month |
| 3 | Read all row header cell values | 3. Every row header value is a service month label in `MMM YYYY` form |
| 4 | Verify the column header row is visible | 4. Column header row is visible and labelled for Posting Date / Posting Month |
| 5 | Read all data column header values | 5. Every data column header is a posting month label in `MMM YYYY` form |
| 6 | Count the row headers and the data column headers | 6. Row count equals the selected service-range width (12) and data column count equals 12 |

---

### TC-05 — Posting date columns are ordered chronologically oldest to most recent

| Field | Value |
|-------|-------|
| **AC** | AC2 |
| **Type** | Edge Case |
| **Priority** | Medium |
| **Pre-conditions** | 1. On the MOM Report page. 2. Default 12-month range applied. |
| **Test Data** | Default range: 12 months |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Verify the column header row is visible | 1. Column header row is visible |
| 2 | Read all data column header labels left to right | 2. A non-empty ordered list of posting month labels is returned |
| 3 | Parse each label into a comparable year-month value | 3. Every label parses successfully into a `YYYY-MM` value |
| 4 | Compare each parsed value with the one to its right | 4. Each value is strictly earlier than the value to its right (oldest leftmost, most recent rightmost) |
| 5 | Verify no duplicate posting month appears in the header row | 5. All posting month headers are unique |

---

### TC-06 — Cells where posting month is after the service month are populated

| Field | Value |
|-------|-------|
| **AC** | AC3 |
| **Type** | Happy Path |
| **Priority** | High |
| **Pre-conditions** | 1. On the MOM Report page. 2. A service date range with known posted transaction data is applied. |
| **Test Data** | Service range spanning 12 months of historical data |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Verify the pivot grid is visible and has at least one data row | 1. Pivot grid is visible with one or more data rows |
| 2 | Pick the first (oldest) service month row and read its row header | 2. Row header returns a parseable service month |
| 3 | Identify every data column whose posting month is strictly after that service month | 3. A non-empty set of eligible columns is identified |
| 4 | Read the cell value at each eligible column for that row | 4. Every eligible cell is non-blank |
| 5 | Verify each non-blank cell value format | 5. Each value renders as a percent collected figure (numeric with a `%` suffix) |
| 6 | Verify each percent value is within a valid range | 6. Each value is greater than or equal to 0% |

---

### TC-07 — Cells where posting month is on or before the service month are blank

| Field | Value |
|-------|-------|
| **AC** | AC3 |
| **Type** | Negative |
| **Priority** | High |
| **Pre-conditions** | 1. On the MOM Report page. 2. Default 12-month range applied. |
| **Test Data** | Default range: 12 months |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Verify the pivot grid is visible | 1. Pivot grid is visible |
| 2 | Read every row header service month and every data column posting month | 2. Both ordered lists are returned and parseable |
| 3 | For each row, identify every column where posting month is earlier than the service month | 3. The set of earlier-posting-month cells is identified |
| 4 | Read the value of each cell identified in step 3 | 4. Every such cell is blank (empty string or a blank placeholder) |
| 5 | For each row, identify the column where posting month equals the service month, if present | 5. Equal-month cells are identified where they exist |
| 6 | Read the value of each equal-month cell | 6. Every equal-month cell is blank — population requires posting month strictly after service month |

---

### TC-08 — Each cell matches the Percent Collected Trend value for the equivalent Transactions Within scope

| Field | Value |
|-------|-------|
| **AC** | AC4 |
| **Type** | Happy Path |
| **Priority** | High |
| **Pre-conditions** | 1. Signed in with AR Reports permission. 2. Same Global Facility Filter, Write-offs and Overpayments settings applied on both reports. |
| **Test Data** | Service month row: oldest month in range; posting column: 1 month after that service month → equivalent "Transactions Within" = 1 month |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Open the MOM Report and verify the pivot grid is visible | 1. Pivot grid is visible |
| 2 | Read the row header of the oldest service month row | 2. Service month is captured (e.g. `Apr 2025`) |
| 3 | Read the cell value in the column exactly 1 month after that service month | 3. A percent collected value is captured for the 1-month interval |
| 4 | Read the cell value in the column exactly 2 months after that service month | 4. A percent collected value is captured for the 2-month interval |
| 5 | Navigate to the Percent Collected Trend report and verify its filter bar is visible | 5. Percent Collected Trend report loads with its filter bar visible |
| 6 | Set the same service date range and set "Transactions Within" to 1 month | 6. Report refreshes with the 1-month scope applied |
| 7 | Read the Percent Collected Trend value for the same service month | 7. Value equals the MOM Report value captured in step 3 |
| 8 | Change "Transactions Within" to 2 months and read the same service month value | 8. Value equals the MOM Report value captured in step 4 |
| 9 | Verify the cell values increase or stay level as the interval widens | 9. The 2-month value is greater than or equal to the 1-month value (collection matures over time) |

---

### TC-09 — Posting columns begin 1 month after the service range start and end 1 month after the range end

| Field | Value |
|-------|-------|
| **AC** | AC5 |
| **Type** | Happy Path |
| **Priority** | High |
| **Pre-conditions** | 1. On the MOM Report page. 2. Time range toggle is visible. |
| **Test Data** | Custom service date range: `Jan 2025` – `Mar 2025` → expected posting columns `Feb 2025` – `Apr 2025` |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Verify the time range toggle is visible and enabled | 1. Toggle is visible with 6 / 12 / 18 / Custom options |
| 2 | Click the "Custom" option | 2. Custom date range picker opens |
| 3 | Set the service date range start to `Jan 2025` | 3. Range start displays `Jan 2025` |
| 4 | Set the service date range end to `Mar 2025` | 4. Range end displays `Mar 2025` |
| 5 | Apply the custom range and wait for the network to become idle | 5. Report refreshes with the custom range applied |
| 6 | Read all row header service months | 6. Rows are exactly `Jan 2025`, `Feb 2025`, `Mar 2025` |
| 7 | Read the first data column header | 7. First posting column is `Feb 2025` — 1 month after the range start |
| 8 | Read the last data column header | 8. Last posting column is `Apr 2025` — 1 month after the range end |
| 9 | Count the data columns | 9. Exactly 3 posting date columns are rendered, matching the 3-month service range |

---

### TC-10 — Selecting the 6-month toggle renders a 6-month service range and 6 posting columns

| Field | Value |
|-------|-------|
| **AC** | AC6 |
| **Type** | Happy Path |
| **Priority** | High |
| **Pre-conditions** | 1. On the MOM Report page with the default 12-month range applied. |
| **Test Data** | Toggle option: `6` |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Verify the "6" toggle option is visible and enabled | 1. "6" option is visible and enabled |
| 2 | Click the "6" toggle option | 2. "6" becomes the selected option and the report begins refreshing |
| 3 | Wait for the network to become idle | 3. Report data request completes |
| 4 | Verify the selected state of the toggle | 4. "6" is selected; 12, 18 and Custom are not selected |
| 5 | Count the row headers | 5. Exactly 6 service month rows are rendered |
| 6 | Count the data column headers | 6. Exactly 6 posting month columns are rendered |
| 7 | Verify the first posting column against the first service row | 7. First posting column is exactly 1 month after the first service month row |

---

### TC-11 — Selecting the 18-month toggle renders an 18-month service range and 18 posting columns

| Field | Value |
|-------|-------|
| **AC** | AC6 |
| **Type** | Happy Path |
| **Priority** | High |
| **Pre-conditions** | 1. On the MOM Report page with the default 12-month range applied. |
| **Test Data** | Toggle option: `18` |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Verify the "18" toggle option is visible and enabled | 1. "18" option is visible and enabled |
| 2 | Click the "18" toggle option | 2. "18" becomes the selected option and the report begins refreshing |
| 3 | Wait for the network to become idle | 3. Report data request completes |
| 4 | Verify the selected state of the toggle | 4. "18" is selected; 6, 12 and Custom are not selected |
| 5 | Count the row headers | 5. Exactly 18 service month rows are rendered |
| 6 | Count the data column headers | 6. Exactly 18 posting month columns are rendered |
| 7 | Verify the last posting column against the last service row | 7. Last posting column is exactly 1 month after the last service month row |

---

### TC-12 — 12 months is the selected default on first load

| Field | Value |
|-------|-------|
| **AC** | AC7 |
| **Type** | Happy Path |
| **Priority** | High |
| **Pre-conditions** | 1. Signed in with AR Reports permission. 2. No prior report preference persisted for this user (fresh session / cleared state). |
| **Test Data** | Expected default toggle option: `12` |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Navigate to the MOM Report for the first time in the session | 1. MOM Report page loads |
| 2 | Wait for the network to become idle | 2. Initial report data request completes |
| 3 | Verify the time range toggle is visible | 3. Toggle is visible with 6 / 12 / 18 / Custom options |
| 4 | Read the selected toggle option | 4. "12" is the selected option without any user interaction |
| 5 | Verify 6, 18 and Custom are not selected | 5. None of 6, 18 or Custom carry the selected state |
| 6 | Count the row headers | 6. Exactly 12 service month rows are rendered |
| 7 | Count the data column headers | 7. Exactly 12 posting month columns are rendered |

---

### TC-13 — Custom range accepts exactly 24 months of service dates

| Field | Value |
|-------|-------|
| **AC** | AC8 |
| **Type** | Happy Path |
| **Priority** | Medium |
| **Pre-conditions** | 1. On the MOM Report page. 2. Time range toggle is visible. |
| **Test Data** | Custom service range spanning exactly 24 months, ending in the current month |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Verify the "Custom" toggle option is visible and enabled | 1. "Custom" option is visible and enabled |
| 2 | Click the "Custom" toggle option | 2. Custom date range picker opens |
| 3 | Set the range start to 23 months before the current month | 3. Range start reflects the selected month |
| 4 | Set the range end to the current month | 4. Range end reflects the current month, giving a 24-month span |
| 5 | Apply the custom range | 5. Range is accepted without a validation error |
| 6 | Wait for the network to become idle | 6. Report data request completes |
| 7 | Count the row headers | 7. Exactly 24 service month rows are rendered |
| 8 | Count the data column headers | 8. Exactly 24 posting month columns are rendered |

---

### TC-14 — Custom range rejects a span greater than 24 months

| Field | Value |
|-------|-------|
| **AC** | AC8 |
| **Type** | Negative |
| **Priority** | High |
| **Pre-conditions** | 1. On the MOM Report page. 2. Custom date range picker is open. |
| **Test Data** | Custom service range spanning 25 months (start = 24 months before current month, end = current month) |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Click the "Custom" toggle option | 1. Custom date range picker opens |
| 2 | Set the range end to the current month | 2. Range end reflects the current month |
| 3 | Attempt to set the range start to 24 months before the current month (25-month span) | 3. Either the month is not selectable, or it is selected but flagged as invalid |
| 4 | Attempt to apply the range | 4. The range is not applied — the apply action is blocked or rejected |
| 5 | Verify the validation feedback | 5. A validation message states the maximum selectable range is 24 months |
| 6 | Verify the rendered report | 6. The grid still reflects the previously applied valid range — no 25-month grid is rendered |

---

### TC-15 — Future service dates cannot be selected

| Field | Value |
|-------|-------|
| **AC** | AC9 |
| **Type** | Negative |
| **Priority** | High |
| **Pre-conditions** | 1. On the MOM Report page. 2. Custom date range picker is open. |
| **Test Data** | Target month: the month after the current month |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Click the "Custom" toggle option | 1. Custom date range picker opens |
| 2 | Verify the current month is selectable | 2. Current month is enabled in the picker |
| 3 | Locate the month immediately after the current month in the picker | 3. The next month is present in the picker view |
| 4 | Verify the interactive state of that future month | 4. The future month is disabled / not selectable |
| 5 | Attempt to click the future month | 5. The click does not change the selected range |
| 6 | Verify all months beyond the current month in the picker | 6. Every month after the current month is disabled |
| 7 | Apply the default valid range and read the last posting date column | 7. Last posting column extends at most 1 month past the current month |

---

### TC-16 — Write-offs toggle applies to the pivot values

| Field | Value |
|-------|-------|
| **AC** | AC10 |
| **Type** | Happy Path |
| **Priority** | Medium |
| **Pre-conditions** | 1. On the MOM Report page. 2. Default 12-month range applied with populated data. |
| **Test Data** | Write-offs toggle: default state, then toggled |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Verify the Write-offs toggle is visible and enabled | 1. Write-offs toggle is visible and enabled on the MOM Report |
| 2 | Read the current Write-offs toggle state | 2. Initial toggle state is captured |
| 3 | Read a populated cell value from the pivot grid | 3. A baseline percent collected value is captured |
| 4 | Click the Write-offs toggle to flip its state | 4. Toggle state flips and the report begins refreshing |
| 5 | Wait for the network to become idle | 5. Report data request completes |
| 6 | Read the same cell value again | 6. Cell value reflects the new Write-offs setting and differs from the baseline where write-off data exists |
| 7 | Click the Write-offs toggle again to restore the original state | 7. Toggle returns to its original state and the cell value returns to the baseline |

---

### TC-17 — Overpayments configuration control is present and applies to the report

| Field | Value |
|-------|-------|
| **AC** | AC10 |
| **Type** | Happy Path |
| **Priority** | Medium |
| **Pre-conditions** | 1. On the MOM Report page. 2. Default 12-month range applied with populated data. |
| **Test Data** | Overpayments configuration options as offered on Percent Collected Trend |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Verify the Overpayments configuration control is visible | 1. Overpayments control is visible on the MOM Report filter bar |
| 2 | Verify the control is enabled | 2. Overpayments control is enabled |
| 3 | Open the Overpayments control | 3. Available options are displayed |
| 4 | Compare the option list with the Percent Collected Trend report's Overpayments options | 4. The option sets are identical |
| 5 | Read a populated cell value from the pivot grid | 5. A baseline percent collected value is captured |
| 6 | Select a different Overpayments option and wait for the network to become idle | 6. Report refreshes with the new Overpayments configuration applied |
| 7 | Read the same cell value again | 7. Cell value reflects the new Overpayments configuration |

---

### TC-18 — No "Transactions Within" filter is present on the MOM Report

| Field | Value |
|-------|-------|
| **AC** | AC11 |
| **Type** | Negative |
| **Priority** | High |
| **Pre-conditions** | 1. On the MOM Report page with the report fully loaded. |
| **Test Data** | Control label: `Transactions Within` |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Verify the report filter bar is visible | 1. Filter bar is visible and fully rendered |
| 2 | Search the filter bar for a control labelled "Transactions Within" | 2. No such control exists in the filter bar |
| 3 | Open any collapsed / overflow filter panel on the report | 3. Overflow filter panel opens and its controls are visible |
| 4 | Search the overflow panel for a "Transactions Within" control | 4. No "Transactions Within" control exists in the overflow panel |
| 5 | Search the whole page for the text "Transactions Within" | 5. The text "Transactions Within" is absent from the MOM Report page |
| 6 | Confirm the same control does exist on Percent Collected Trend | 6. "Transactions Within" is present on Percent Collected Trend — confirming the locator is valid and its absence on MOM Report is intentional |

---

### TC-19 — No grouping selector is present on the MOM Report

| Field | Value |
|-------|-------|
| **AC** | AC12 |
| **Type** | Negative |
| **Priority** | High |
| **Pre-conditions** | 1. On the MOM Report page with the report fully loaded. |
| **Test Data** | Control label: `Group By` / `Grouping` |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Verify the report filter bar is visible | 1. Filter bar is visible and fully rendered |
| 2 | Search the filter bar for a "Group By" / "Grouping" selector | 2. No grouping selector exists in the filter bar |
| 3 | Open any collapsed / overflow filter panel | 3. Overflow filter panel opens and its controls are visible |
| 4 | Search the overflow panel for a grouping selector | 4. No grouping selector exists in the overflow panel |
| 5 | Verify the pivot grid row headers | 5. Row headers show service months only — no group header or expandable group rows are present |
| 6 | Confirm the grouping selector does exist on Percent Collected Trend | 6. Grouping selector is present on Percent Collected Trend — confirming its absence on MOM Report is intentional |

---

### TC-20 — Global Facility Filter affects the MOM Report data

| Field | Value |
|-------|-------|
| **AC** | AC13 |
| **Type** | Happy Path |
| **Priority** | High |
| **Pre-conditions** | 1. On the MOM Report page. 2. User has access to at least two facilities with differing collection data. |
| **Test Data** | Facility A and Facility B from the Global Facility Filter |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Verify the Global Facility Filter control is visible | 1. Global Facility Filter is visible on the MOM Report page |
| 2 | Verify the control is enabled | 2. Global Facility Filter is enabled |
| 3 | Select Facility A and wait for the network to become idle | 3. Report refreshes with Facility A applied |
| 4 | Read a populated cell value from the pivot grid | 4. Facility A percent collected value is captured |
| 5 | Open the Global Facility Filter and select Facility B | 5. Filter selection updates to Facility B and the report begins refreshing |
| 6 | Wait for the network to become idle | 6. Report data request completes |
| 7 | Read the same cell position again | 7. Cell value differs from the Facility A value — the report is scoped to the selected facility |
| 8 | Verify the report data request carried the facility scope | 8. The report data request includes the selected facility in its parameters |

---

### TC-21 — Export produces a file mirroring the pivot layout

| Field | Value |
|-------|-------|
| **AC** | AC14 |
| **Type** | Happy Path |
| **Priority** | High |
| **Pre-conditions** | 1. On the MOM Report page. 2. Default 12-month range applied with populated data. 3. User has export permission. |
| **Test Data** | Export format as offered by the report (CSV / Excel) |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Verify the Export control is visible | 1. Export control is visible on the MOM Report |
| 2 | Verify the Export control is enabled | 2. Export control is enabled |
| 3 | Capture the on-screen row headers and column headers | 3. On-screen service months and posting months are captured for comparison |
| 4 | Click the Export control | 4. Export is triggered and a file download begins |
| 5 | Wait for the download to complete and read the suggested filename | 5. A file is downloaded with a non-empty filename and the expected extension |
| 6 | Open the exported file and read its header row | 6. Header row lists the posting months in the same chronological order as the on-screen columns |
| 7 | Read the first cell of each exported data row | 7. Row labels are the service months in the same order as the on-screen rows |
| 8 | Compare exported cell values against the on-screen grid | 8. Values match the on-screen pivot, with blanks preserved where posting month is not strictly after the service month |

---

### TC-22 — Export with an empty result set still produces a well-formed file

| Field | Value |
|-------|-------|
| **AC** | AC14 |
| **Type** | Edge Case |
| **Priority** | Medium |
| **Pre-conditions** | 1. On the MOM Report page. 2. Filters applied that yield no matching transactions (e.g. a facility with no posted activity in the selected range). |
| **Test Data** | Facility / date range combination with zero results |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Apply a filter combination that returns no data and wait for the network to become idle | 1. Report refreshes and returns no data |
| 2 | Verify the grid empty state | 2. Grid shows an empty state message or renders rows with all cells blank — no error is displayed |
| 3 | Verify the Export control state | 3. Export control remains visible and its state is deterministic (enabled, or disabled with a clear reason) |
| 4 | Click Export if it is enabled | 4. Export is triggered and a file download begins |
| 5 | Open the exported file and read its header row | 5. Header row is present with the posting month columns intact |
| 6 | Read the file body | 6. Body contains only blank / zero cells — no malformed rows and no unhandled error content |

---

### TC-23 — Edge case: single-month custom range renders exactly one row and one posting column

| Field | Value |
|-------|-------|
| **AC** | AC5, AC8 |
| **Type** | Edge Case |
| **Priority** | Medium |
| **Pre-conditions** | 1. On the MOM Report page. 2. Custom date range picker available. |
| **Test Data** | Custom service range: start = end = the month before the current month |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Click the "Custom" toggle option | 1. Custom date range picker opens |
| 2 | Set the range start and range end to the same month (previous month) | 2. Both start and end display the same month |
| 3 | Apply the range and wait for the network to become idle | 3. Range is accepted and the report refreshes |
| 4 | Count the row headers | 4. Exactly 1 service month row is rendered |
| 5 | Count the data column headers | 5. Exactly 1 posting month column is rendered |
| 6 | Verify the posting column against the service row | 6. The single posting column is exactly 1 month after the single service month row |
| 7 | Read the single cell value | 7. Cell is populated — posting month is strictly after the service month |

---

### TC-24 — Edge case: toggling range width from 18 to 6 shrinks rows and columns consistently

| Field | Value |
|-------|-------|
| **AC** | AC6 |
| **Type** | Edge Case |
| **Priority** | Medium |
| **Pre-conditions** | 1. On the MOM Report page. 2. The 18-month toggle is currently applied. |
| **Test Data** | Toggle sequence: `18` → `6` |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Apply the "18" toggle and wait for the network to become idle | 1. 18 service rows and 18 posting columns are rendered |
| 2 | Capture the row and column counts | 2. Baseline counts of 18 and 18 are captured |
| 3 | Click the "6" toggle option | 3. "6" becomes the selected option and the report begins refreshing |
| 4 | Wait for the network to become idle | 4. Report data request completes |
| 5 | Count the row headers and data column headers | 5. Exactly 6 rows and 6 columns are rendered — no stale rows or columns remain from the 18-month view |
| 6 | Verify the newest service month row | 6. The newest service month row is unchanged — only the range start moved forward |
| 7 | Verify the blank-cell rule still holds | 7. Cells with posting month on or before the service month remain blank in the narrowed view |

---

### TC-25 — RBAC: user without AR Reports permission cannot reach the MOM Report

| Field | Value |
|-------|-------|
| **AC** | AC1, AC15 |
| **Type** | RBAC / Permission |
| **Priority** | High |
| **Pre-conditions** | 1. Signed in as a user whose role does not grant the AR Reports permission. |
| **Test Data** | Restricted role user; direct MOM Report route URL |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Verify the left navigation container is visible | 1. Left navigation is rendered for the restricted user |
| 2 | Search the left nav for the "AR Reports" section | 2. "AR Reports" section is either absent or present without report links |
| 3 | Search the left nav for a "MOM Report" link | 3. No "MOM Report" link is available to this user |
| 4 | Navigate to the Reports landing page | 4. Landing page loads or access is denied per the role's configuration |
| 5 | Search the landing page for a "MOM Report" card | 5. No "MOM Report" card is rendered for this user |
| 6 | Navigate directly to the MOM Report route URL | 6. Access is denied — an unauthorised / not-found view is shown and no pivot data is rendered |
| 7 | Verify no report data request succeeded | 7. No successful MOM Report data response is returned for this user |

---

### TC-26 — RBAC: user without export permission cannot export the MOM Report

| Field | Value |
|-------|-------|
| **AC** | AC14 |
| **Type** | RBAC / Permission |
| **Priority** | Medium |
| **Pre-conditions** | 1. Signed in as a user with AR Reports read access but no export permission. 2. On the MOM Report page. |
| **Test Data** | Read-only role user |

| # | Step | Expected Result |
|---|------|-----------------|
| 1 | Verify the MOM Report page loads for the read-only user | 1. MOM Report page loads and the pivot grid is visible |
| 2 | Verify the pivot grid contains data | 2. Report data renders normally — read access is unaffected |
| 3 | Locate the Export control | 3. Export control is either hidden or rendered in a disabled state |
| 4 | If the Export control is visible, verify its enabled state | 4. Export control is disabled and not clickable |
| 5 | Attempt to click the Export control | 5. No download is initiated |
| 6 | Verify no export network request was issued | 6. No export request is sent for this user |

---

## Notes

- **No Swagger/OpenAPI spec** is configured for RevFlow, so no API test cases are derived from a spec. If API coverage is wanted, network interception during the UI run is the available route.
- **Percent Collected Trend parity** is the reference for AC4, AC10 and AC13 — several cases cross-check against that existing report rather than asserting absolute figures, which keeps them stable across data refreshes.
