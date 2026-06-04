# Manual Test Cases — JP-1: Pre Payment Booking Flow
**Date**: 2026-06-04  
**Ticket**: [JP-1](https://innocito.atlassian.net/browse/JP-1)  
**Module**: booking  
**Total Cases**: 23

---

## Verified Test Data
- **Positive location**: Bronx, NY (5 vehicles — highest inventory)
- **Positive locations**: Los Angeles CA, El Segundo CA, Brooklyn NY, Long Island City NY, Elmhurst NY
- **Negative locations**: Seattle WA, Miami FL, Phoenix AZ (outside service area)

---

## AC1 — Location Selection

| TC# | AC | Type | Priority | Scenario | Pre-conditions | Test Data | Steps | Expected Result |
|-----|-----|------|----------|----------|----------------|-----------|-------|-----------------|
| TC1 | AC1 | Happy Path | High | Select a serviceable pickup location | 1. Navigate to https://drivejoulez.com | `Bronx` (type into pickup) | 1. Verify pickup location input is visible and enabled<br>2. Click the pickup location input<br>3. Type "Bronx" into the input<br>4. Wait for location suggestions to appear<br>5. Click the first suggestion in the dropdown | 1. Pickup input is visible and enabled<br>2. Input is focused<br>3. Characters appear in the field<br>4. Suggestions dropdown appears with at least one item<br>5. Input is populated with the selected location text (contains "Bronx") |
| TC2 | AC1 | Happy Path | High | Select a different drop-off location | 1. Navigate to https://drivejoulez.com<br>2. Pickup location already set to "Bronx, NY" | `Brooklyn` (type into dropoff) | 1. Verify drop-off input is visible<br>2. Click the drop-off location input<br>3. Type "Brooklyn" into the input<br>4. Wait for suggestions to appear<br>5. Click the first suggestion | 1. Drop-off input is visible<br>2. Drop-off input is focused<br>3. Characters appear in the field<br>4. Suggestions dropdown appears<br>5. Drop-off input is populated with selected location (contains "Brooklyn") |
| TC3 | AC1 | Happy Path | Medium | Delivery option is available for metro area | 1. Navigate to https://drivejoulez.com | N/A | 1. Verify the homepage loads<br>2. Look for a "Delivery" toggle, checkbox, or link on the booking form<br>3. Check if delivery option element is present in the DOM | 1. Homepage loads<br>2. Delivery option element is found in the page (xfail if not visible — optional UI) |
| TC4 | AC1 | Negative | High | Unserviceable location yields no search results | 1. Navigate to https://drivejoulez.com | `Seattle` (unserviceable) | 1. Verify pickup input is visible<br>2. Click the pickup input<br>3. Type "Seattle"<br>4. Wait for suggestions<br>5. Select the first suggestion or press Enter<br>6. Click Search | 1. Input is visible<br>2. Input is focused<br>3. Text appears<br>4. Dropdown appears or no suggestions shown<br>5. Location selected or text typed<br>6. Search results page shows no vehicle cards or an error/empty state message |
| TC5 | AC1 | Edge Case | Medium | Same location for pickup and drop-off is accepted | 1. Navigate to https://drivejoulez.com | `Bronx` for both fields | 1. Select pickup location as "Bronx, NY"<br>2. Verify drop-off input is visible<br>3. Leave drop-off as same (default placeholder "Same as Pick Up") or type same location<br>4. Click Search | 1. Pickup set to Bronx<br>2. Drop-off input shows "Same as Pick Up" placeholder<br>3. Drop-off is same as pickup<br>4. Search proceeds without validation error |

---

## AC2 — Date & Time Selection

| TC# | AC | Type | Priority | Scenario | Pre-conditions | Test Data | Steps | Expected Result |
|-----|-----|------|----------|----------|----------------|-----------|-------|-----------------|
| TC6 | AC2 | Happy Path | High | Select a pickup date from the calendar | 1. Navigate to https://drivejoulez.com<br>2. Pickup location set to "Bronx, NY" | Day = 15 (next available future date) | 1. Verify duration section is visible<br>2. Click the duration section to open calendar<br>3. Verify react-calendar is visible<br>4. Click on day 15 tile<br>5. Verify calendar closes or date updates | 1. Duration section is visible<br>2. Calendar opens<br>3. React-calendar is visible<br>4. Day 15 tile is clicked<br>5. Calendar closes or pickup date is updated in the UI |
| TC7 | AC2 | Happy Path | High | Rental duration is auto-calculated | 1. Navigate to https://drivejoulez.com<br>2. Pickup set to "Bronx, NY" | Pickup day 15, dropoff day 16 | 1. Open the duration picker<br>2. Select day 15 as pickup<br>3. Select day 16 as drop-off<br>4. Read the duration display text | 1. Duration picker opens<br>2. Day 15 is selected<br>3. Day 16 is selected<br>4. Duration text shows "1 Day" or "1 day" |
| TC8 | AC2 | Happy Path | High | Default values are pre-populated | 1. Navigate to https://drivejoulez.com | N/A | 1. Verify duration section is visible<br>2. Read the text content of the duration section<br>3. Verify it contains a date (not empty) | 1. Duration section is visible<br>2. Duration text is readable<br>3. Duration section shows a non-empty default value (today's date or 1-day duration) |
| TC9 | AC2 | Negative | High | Past dates are disabled in the calendar | 1. Navigate to https://drivejoulez.com<br>2. Pickup set to "Bronx, NY" | Day 1 (should be past/disabled for current month) | 1. Open the duration picker<br>2. Verify calendar is visible<br>3. Locate day 1 tile<br>4. Check if it has disabled attribute or class | 1. Calendar opens<br>2. Calendar is visible<br>3. Day 1 tile found<br>4. Day 1 tile has disabled state or is a neighboring month tile (past date not selectable) |

---

## AC3 — Vehicle Search

| TC# | AC | Type | Priority | Scenario | Pre-conditions | Test Data | Steps | Expected Result |
|-----|-----|------|----------|----------|----------------|-----------|-------|-----------------|
| TC10 | AC3 | Happy Path | High | Search returns vehicle cards | 1. Navigate to https://drivejoulez.com<br>2. Pickup: Bronx, NY; default dates | `Bronx, NY` | 1. Select pickup location "Bronx"<br>2. Verify location is set<br>3. Click Search<br>4. Wait for /cars-list URL<br>5. Count vehicle cards | 1. Bronx selected<br>2. Location confirmed in input<br>3. Search button clicked<br>4. URL changes to /cars-list<br>5. At least 1 vehicle card is visible |
| TC11 | AC3 | Happy Path | High | Vehicle card displays required fields | 1. On /cars-list page with Bronx results | N/A (use TC10 setup) | 1. Wait for first vehicle card to be visible<br>2. Verify vehicle name element is visible<br>3. Verify vehicle type element is visible<br>4. Verify daily rate element is visible<br>5. Verify trip rate element is visible<br>6. Verify seating capacity element is visible<br>7. Verify driving range element is visible | 1. First card is visible<br>2. Vehicle name text is non-empty<br>3. Vehicle type text is visible<br>4. Daily rate shows currency value<br>5. Trip rate shows currency value<br>6. Seating capacity is visible<br>7. Driving range is visible |
| TC12 | AC3 | Happy Path | High | Filter buttons are available | 1. On /cars-list page with Bronx results | N/A | 1. Wait for filter buttons to appear<br>2. Count the filter buttons<br>3. Verify at least 4 filter buttons exist | 1. Filter buttons are visible<br>2. At least 4 filter options shown<br>3. Filter buttons are clickable |
| TC13 | AC3 | Negative | High | Unserviceable location yields no vehicles | 1. Navigate to https://drivejoulez.com<br>2. Pickup: Seattle, WA | `Seattle` | 1. Type "Seattle" in pickup<br>2. Select or type location<br>3. Click Search<br>4. Check result count | 1. Seattle typed<br>2. Location entered<br>3. Search executed<br>4. Zero vehicle cards shown or empty state / error message displayed |

---

## AC4 — Vehicle Selection

| TC# | AC | Type | Priority | Scenario | Pre-conditions | Test Data | Steps | Expected Result |
|-----|-----|------|----------|----------|----------------|-----------|-------|-----------------|
| TC14 | AC4 | Happy Path | High | Click vehicle card navigates to detail page | 1. On /cars-list with Bronx results<br>2. At least 1 vehicle visible | N/A | 1. Verify first vehicle card is visible<br>2. Click the first vehicle card<br>3. Wait for /booking URL<br>4. Verify car specs container is visible | 1. Card is visible<br>2. Card is clicked<br>3. URL changes to /booking<br>4. Car specs box is rendered on the page |
| TC15 | AC4 | Happy Path | High | Vehicle detail page shows pickup/drop-off details | 1. On /booking detail page (from TC14) | N/A | 1. Verify "Pick Up" text is visible<br>2. Verify "Drop Off" text is visible | 1. "Pick Up" section is present<br>2. "Drop Off" section is present |
| TC16 | AC4 | Happy Path | High | Car specs display Range, Year, Seating, Color | 1. On /booking detail page | N/A | 1. Verify Range spec is visible<br>2. Verify Year spec is visible<br>3. Verify Seating spec is visible<br>4. Verify Color spec is visible | 1. Range spec displayed<br>2. Year spec displayed<br>3. Seating spec displayed<br>4. Color spec displayed |

---

## AC5 — Pricing Details

| TC# | AC | Type | Priority | Scenario | Pre-conditions | Test Data | Steps | Expected Result |
|-----|-----|------|----------|----------|----------------|-----------|-------|-----------------|
| TC17 | AC5 | Happy Path | High | Pricing breakdown is displayed | 1. On /booking detail page | N/A | 1. Verify "Pricing Details" heading is visible<br>2. Verify base rate row is visible<br>3. Verify taxes row is visible | 1. "Pricing Details" heading is present<br>2. Base rate row is visible with a value<br>3. Taxes row is visible |
| TC18 | AC5 | Happy Path | High | Grand total is prominently displayed | 1. On /booking detail page | N/A | 1. Locate the grand total display element<br>2. Verify it contains a $ amount | 1. Grand total element found<br>2. Grand total text is non-empty and contains a numeric value |
| TC19 | AC5 | Happy Path | High | Base rate per day is visible | 1. On /booking detail page | N/A | 1. Verify base rate row is visible<br>2. Read base rate text<br>3. Verify it contains a dollar sign or numeric value | 1. Base rate is visible<br>2. Base rate text is readable<br>3. Base rate contains "$" or a number |
| TC20 | AC5 | Edge Case | Medium | Taxes are included in pricing | 1. On /booking detail page | N/A | 1. Verify taxes row is visible<br>2. Read taxes text<br>3. Confirm it is non-zero or shows calculated amount | 1. Taxes row visible<br>2. Taxes text readable<br>3. Taxes value is present (not zero or empty) |

---

## AC6 — Booking/Checkout

| TC# | AC | Type | Priority | Scenario | Pre-conditions | Test Data | Steps | Expected Result |
|-----|-----|------|----------|----------|----------------|-----------|-------|-----------------|
| TC21 | AC6 | RBAC | High | Guest user sees authentication gate | 1. On /booking detail page (not logged in) | N/A | 1. Verify "Join Us" button is visible<br>2. Verify "Log in" button is visible | 1. "Join Us" button is present and visible<br>2. "Log in" button is present and visible |
| TC22 | AC6 | RBAC | High | Guest can initiate signup via Join Us | 1. On /booking detail page (not logged in) | N/A | 1. Verify "Join Us" button is visible<br>2. Verify it is enabled and clickable | 1. "Join Us" button is visible<br>2. Button is enabled (not disabled) |
| TC23 | AC6 | Negative | High | Guest cannot see Pay Now button | 1. On /booking detail page (not logged in) | N/A | 1. Check if "Pay Now" text is visible on the page | 1. "Pay Now" text is NOT visible for unauthenticated users (auth gate shown instead) |
