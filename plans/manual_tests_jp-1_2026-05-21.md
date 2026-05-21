# Manual Test Cases — JP-1: Pre Payment Booking Flow
**Date**: 2026-05-21  
**Ticket**: JP-1  
**Module**: booking  
**Total Cases**: 34 (28 UI · 6 API)

---

## Verified Location Data
- **Positive**: Bronx, NY (5 vehicles ⭐), Brooklyn, NY (4), Long Island City, NY (4), Elmhurst, NY (4), Los Angeles, CA (3), El Segundo, CA (3)
- **Negative**: Seattle, WA · Miami, FL · Phoenix, AZ (no vehicles / outside service area)

---

## AC1 — Location Selection

| # | AC | Type | Priority | Scenario | Pre-conditions | Test Data | Steps | Expected Result |
|---|---|------|----------|----------|----------------|-----------|-------|-----------------|
| TC1 | AC1 | Happy Path | High | Select serviceable pickup location | Navigate to https://drivejoulez.com | location = "Bronx" | 1. Open https://drivejoulez.com<br>2. Verify pickup input is visible<br>3. Click pickup location input<br>4. Type "Bronx"<br>5. Wait for suggestion list to appear<br>6. Click first suggestion | 1. Page loads, pickup input visible<br>2. Pickup input is focusable<br>3. Input receives focus<br>4. Dropdown suggestions appear<br>5. At least one suggestion contains "Bronx"<br>6. Input value matches "Bronx" (case-insensitive, partial match) |
| TC2 | AC1 | Happy Path | High | Select different drop-off location | Pickup location selected | dropoff = "Brooklyn" | 1. Navigate and select pickup "Bronx"<br>2. Verify drop-off input is visible<br>3. Click drop-off input<br>4. Type "Brooklyn"<br>5. Wait for suggestions<br>6. Click first suggestion | 1. Drop-off input is visible after pickup<br>2. Drop-off input is focusable<br>3. Input receives focus<br>4. Suggestions appear<br>5. At least one matches "Brooklyn"<br>6. Drop-off input value contains "Brooklyn" |
| TC3 | AC1 | Happy Path | Low | Delivery option element present (conditional) | Navigate to https://drivejoulez.com | None | 1. Navigate to https://drivejoulez.com<br>2. Search for delivery/metro option element<br>3. Observe presence or absence | 1. Page loads<br>2. Search executes<br>3. Element may or may not be visible (xfail:strict=False — delivery is conditional UI) |
| TC4 | AC1 | Negative | High | Unserviceable location returns no vehicles | Navigate to https://drivejoulez.com | location = "Seattle" | 1. Navigate to https://drivejoulez.com<br>2. Type "Seattle" in pickup input<br>3. Click search<br>4. Observe results page | 1. Page loads<br>2. Input accepts "Seattle"<br>3. Results page loads<br>4. Zero vehicle cards displayed OR "no vehicles available" message shown |
| TC5 | AC1 | Edge Case | Medium | Same location for pickup and drop-off | Navigate to https://drivejoulez.com | location = "Bronx" | 1. Navigate to https://drivejoulez.com<br>2. Select "Bronx" as pickup<br>3. Verify drop-off input shows same/default value<br>4. Confirm drop-off defaults to same as pickup | 1. Page loads<br>2. Pickup set to Bronx<br>3. Drop-off shows "Same as Pick Up" placeholder or identical value<br>4. Same-location booking flow proceeds normally |

---

## AC2 — Date & Time Selection

| # | AC | Type | Priority | Scenario | Pre-conditions | Test Data | Steps | Expected Result |
|---|---|------|----------|----------|----------------|-----------|-------|-----------------|
| TC6 | AC2 | Happy Path | High | Select pickup date from calendar | Navigate to https://drivejoulez.com | day = 15 (or first available) | 1. Navigate to https://drivejoulez.com<br>2. Verify duration section is visible<br>3. Click duration section to open calendar<br>4. Verify react-calendar opens<br>5. Click day tile for a future date | 1. Page loads<br>2. Duration section visible<br>3. Click registers<br>4. Calendar opens with month view<br>5. Selected date tile is highlighted |
| TC7 | AC2 | Happy Path | High | Rental duration auto-calculated | Homepage loaded, calendar accessible | pickup = today+1, dropoff = today+3 | 1. Navigate to homepage<br>2. Open date picker<br>3. Select pickup date (tomorrow)<br>4. Select drop-off date (3 days out)<br>5. Close/confirm dates<br>6. Read duration display text | 1. Page loads<br>2. Calendar opens<br>3. Pickup date selected<br>4. Drop-off date selected<br>5. Calendar closes or confirms<br>6. Duration text shows "2" or "2 day(s)" |
| TC8 | AC2 | Happy Path | Medium | Default date/duration values pre-populated | Navigate to https://drivejoulez.com | None | 1. Navigate to homepage<br>2. Read duration section text before any interaction | 1. Page loads<br>2. Duration section shows a pre-populated value (e.g., "1 Day" or current date range) |
| TC9 | AC2 | Negative | High | Past dates disabled in calendar | Calendar is open | Any past date in current month | 1. Navigate to homepage<br>2. Open date picker<br>3. Verify past date tiles are disabled<br>4. Attempt to identify a past day tile | 1. Page loads<br>2. Calendar opens<br>3. Past-date tiles have disabled attribute or cannot-pick CSS class<br>4. No past date tile responds to click with selection |
| TC10 | AC2 | Edge Case | Medium | Single-day rental shows 1 day duration | Homepage loaded | Same pickup and dropoff day | 1. Navigate to homepage<br>2. Open date picker<br>3. Select same day for pickup and drop-off<br>4. Observe duration display | 1. Page loads<br>2. Calendar opens<br>3. Same day selected for both<br>4. Duration shows "1 Day" or minimum rental unit |

---

## AC3 — Vehicle Search

| # | AC | Type | Priority | Scenario | Pre-conditions | Test Data | Steps | Expected Result |
|---|---|------|----------|----------|----------------|-----------|-------|-----------------|
| TC11 | AC3 | Happy Path | High | Vehicle search returns results for Bronx, NY | Homepage loaded | pickup = "Bronx", dates = default | 1. Navigate to homepage<br>2. Select pickup "Bronx"<br>3. Click search<br>4. Wait for /cars-list URL<br>5. Count vehicle cards | 1. Page loads<br>2. Pickup set<br>3. Search triggered<br>4. URL contains /cars-list<br>5. At least 1 vehicle card visible |
| TC12 | AC3 | Happy Path | High | Vehicle card displays all required fields | On /cars-list with results | pickup = "Bronx" | 1. Navigate and search with Bronx<br>2. Wait for vehicle cards<br>3. Check first card for: vehicle name, vehicle type, daily rate, total trip rate, seating capacity, range | 1–2. Results page loaded<br>3. First card has non-empty vehicle name<br>4. First card has vehicle type text<br>5. Daily rate has $ symbol<br>6. Total trip rate has $ symbol<br>7. Seating capacity shown (members icon)<br>8. Range shown (miles icon) |
| TC13 | AC3 | Happy Path | High | Filter buttons present on results page | On /cars-list with results | pickup = "Bronx" | 1. Navigate and search with Bronx<br>2. Wait for filter buttons to load<br>3. Count filter buttons | 1–2. Results page loaded<br>3. At least 1 filter button visible |
| TC14 | AC3 | Happy Path | Medium | Filter by vehicle type updates results | On /cars-list with results | pickup = "Bronx" | 1. Navigate and search with Bronx<br>2. Record initial vehicle card count<br>3. Click first filter button<br>4. Wait for results to update<br>5. Count filtered vehicle cards | 1–2. N cards visible<br>3. Filter button clicked<br>4. Page updates<br>5. Cards count is ≤ N (filtered subset) |
| TC15 | AC3 | Negative | High | No vehicles for unserviceable location (Seattle) | Homepage loaded | location = "Seattle" | 1. Navigate to homepage<br>2. Type "Seattle" in pickup<br>3. Click search<br>4. Check /cars-list for vehicle cards | 1. Page loads<br>2. Input accepts Seattle<br>3. Results URL loads<br>4. Zero vehicle cards visible OR empty-state message shown |
| TC16 | AC3 | Edge Case | Low | Re-clicking active filter restores results | On /cars-list with filter applied | pickup = "Bronx" | 1. Navigate and search with Bronx<br>2. Click a filter button to filter<br>3. Click same filter button again to deselect<br>4. Count cards | 1–2. Filter applied, reduced cards<br>3. Filter deactivated<br>4. Card count restored to original (or at least increased) |

---

## AC4 — Vehicle Selection

| # | AC | Type | Priority | Scenario | Pre-conditions | Test Data | Steps | Expected Result |
|---|---|------|----------|----------|----------------|-----------|-------|-----------------|
| TC17 | AC4 | Happy Path | High | Clicking vehicle card navigates to /booking | On /cars-list with results | pickup = "Bronx" | 1. Navigate and search with Bronx<br>2. Wait for vehicle cards<br>3. Click first vehicle card<br>4. Wait for URL change | 1–2. Results loaded<br>3. Click registers<br>4. URL contains /booking<br>5. Booking detail page loads |
| TC18 | AC4 | Happy Path | High | Vehicle detail shows Pickup and Drop-off sections | On /booking detail page | pickup = "Bronx" | 1. Navigate → search → click first vehicle<br>2. Verify "Pick Up" text visible<br>3. Verify "Drop Off" text visible | 1. Booking page loads<br>2. "Pick Up" heading/section visible<br>3. "Drop Off" heading/section visible |
| TC19 | AC4 | Happy Path | High | Vehicle spec details displayed (Range, Year, Seating, Color) | On /booking detail page | pickup = "Bronx" | 1. Navigate → search → click first vehicle<br>2. Check car specs container visible<br>3. Verify Range spec visible<br>4. Verify Year spec visible<br>5. Verify Seating spec visible<br>6. Verify Color spec visible | 1. Booking page loads<br>2. Car specs container present<br>3. Range spec displayed<br>4. Year spec displayed<br>5. Seating spec displayed<br>6. Color spec displayed |
| TC20 | AC4 | Edge Case | Medium | Vehicle spec values are non-empty | On /booking detail page | pickup = "Bronx" | 1. Navigate → search → click first vehicle<br>2. Read Range spec inner text<br>3. Read Year spec inner text<br>4. Read Seating spec inner text | 1. Booking page loads<br>2. Range text is non-empty<br>3. Year text is non-empty<br>4. Seating text is non-empty |

---

## AC5 — Pricing Details

| # | AC | Type | Priority | Scenario | Pre-conditions | Test Data | Steps | Expected Result |
|---|---|------|----------|----------|----------------|-----------|-------|-----------------|
| TC21 | AC5 | Happy Path | High | Pricing breakdown (base rate + taxes) displayed | On /booking detail page | pickup = "Bronx" | 1. Navigate → search → click first vehicle<br>2. Scroll to Pricing Details section<br>3. Verify "Pricing Details" heading visible<br>4. Verify base rate row visible<br>5. Verify taxes row visible | 1. Booking page loads<br>2. Scroll to pricing<br>3. "Pricing Details" heading visible<br>4. Base rate row is present<br>5. Taxes row is present |
| TC22 | AC5 | Happy Path | High | Grand total is prominently displayed with dollar value | On /booking detail page | pickup = "Bronx" | 1. Navigate → search → click first vehicle<br>2. Read grand total display text | 1. Booking page loads<br>2. Grand total text contains "$" symbol and a numeric value |
| TC23 | AC5 | Happy Path | High | Base rate contains dollar value | On /booking detail page | pickup = "Bronx" | 1. Navigate → search → click first vehicle<br>2. Read base rate row text | 1. Booking page loads<br>2. Base rate text contains "$" symbol |
| TC24 | AC5 | Happy Path | Medium | Taxes row is visible on booking page | On /booking detail page | pickup = "Bronx" | 1. Navigate → search → click first vehicle<br>2. Check for taxes row visibility | 1. Booking page loads<br>2. Taxes row is visible (may read $0 for serviceable locations) |

---

## AC6 — Booking / Checkout (Auth Gate)

| # | AC | Type | Priority | Scenario | Pre-conditions | Test Data | Steps | Expected Result |
|---|---|------|----------|----------|----------------|-----------|-------|-----------------|
| TC25 | AC6 | RBAC | High | Guest user sees auth gate (Join Us / Log In) | On /booking detail page, not logged in | pickup = "Bronx" | 1. Navigate → search → click first vehicle<br>2. Check for Join Us button<br>3. Check for Log in button | 1. Booking page loads<br>2. "Join Us" button is visible OR<br>3. "Log in" button is visible |
| TC26 | AC6 | RBAC | High | Guest can click Join Us to initiate signup | On /booking detail page, not logged in | pickup = "Bronx" | 1. Navigate → search → click first vehicle<br>2. Wait for Join Us button<br>3. Verify it is enabled<br>4. Click Join Us | 1. Booking page loads<br>2. Join Us button visible<br>3. Button is not disabled<br>4. Signup modal/page opens |
| TC27 | AC6 | Negative | High | Guest cannot see Pay Now button | On /booking detail page, not logged in | pickup = "Bronx" | 1. Navigate → search → click first vehicle<br>2. Check for Pay Now element | 1. Booking page loads<br>2. Pay Now button/div is NOT visible for unauthenticated guest |
| TC28 | AC6 | Edge Case | Medium | Auth heading visible on booking page for guest | On /booking detail page, not logged in | pickup = "Bronx" | 1. Navigate → search → click first vehicle<br>2. Check for auth heading text | 1. Booking page loads<br>2. "Let's Get You on the Road!" heading is visible |

---

## API Tests

| # | AC | Type | Priority | Scenario | Pre-conditions | Test Data | Steps | Expected Result |
|---|---|------|----------|----------|----------------|-----------|-------|-----------------|
| TC29 | AC1 | Happy Path | High | GET available locations returns Bronx | None (open endpoint) | None | 1. GET /location/available-locations/open<br>2. Parse response<br>3. Search for Bronx in list | 1. HTTP 200<br>2. Response is a list or has list field<br>3. At least one location contains "Bronx" |
| TC30 | AC3 | Happy Path | High | POST available cars returns results for Bronx | Bronx location ID from TC29 | locationId from available-locations | 1. Get Bronx location from /available-locations<br>2. POST /car/availableCarsV4/open with Bronx locationId, valid dates<br>3. Parse response | 1. Location fetched<br>2. HTTP 200<br>3. Response contains at least 1 car |
| TC31 | AC5 | Happy Path | High | POST estimated price returns pricing fields | Car ID from TC30 | carId, locationId, dates | 1. Get Bronx location and first car ID<br>2. POST /booking/estimatedPrice/open with carId, locationId, dates<br>3. Verify pricing fields | 1–2. Setup done<br>3. HTTP 200<br>4. Response contains baseRate, taxes, and totalPrice fields |
| TC32 | AC3 | Negative | High | POST available cars with no location returns error | None | Empty/null locationId | 1. POST /car/availableCarsV4/open with empty payload<br>2. Check status code | 1. HTTP 400 or 422 or error body returned (not 200) |
| TC33 | AC4 | Happy Path | High | GET car by ID returns spec fields | Car ID from TC30 | carId | 1. Get first car ID from available cars<br>2. GET /car/getById/{carId}/open<br>3. Check response fields | 1. Car ID obtained<br>2. HTTP 200<br>3. Response contains range, year, seating, and color fields |
| TC34 | AC6 | Happy Path | High | POST authenticate with valid credentials returns token | Valid test credentials in .env | TEST_USERNAME, TEST_PASSWORD | 1. POST /authenticate with valid credentials<br>2. Check response | 1. HTTP 200<br>2. Response contains auth token (JWT or similar) |

---

## Coverage Summary

| AC | UI Cases | API Cases | Total |
|----|----------|-----------|-------|
| AC1 — Location Selection | 5 | 1 | 6 |
| AC2 — Date & Time | 5 | 0 | 5 |
| AC3 — Vehicle Search | 6 | 2 | 8 |
| AC4 — Vehicle Selection | 4 | 1 | 5 |
| AC5 — Pricing Details | 4 | 1 | 5 |
| AC6 — Booking/Auth Gate | 4 | 1 | 5 |
| **Total** | **28** | **6** | **34** |
