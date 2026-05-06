# Manual Test Cases — JP-1: Pre Payment Booking Flow
**Generated**: 2025-05-02  
**Jira**: [JP-1](https://innocito.atlassian.net/browse/JP-1)  
**Module**: booking

---

## Acceptance Criteria Summary

| AC | Description |
|----|-------------|
| AC1 | Location Selection — pickup, drop-off, delivery option |
| AC2 | Date & Time Selection — pickup/drop-off dates, auto-calculated duration, defaults |
| AC3 | Vehicle Search — returns EVs based on filters, card shows all required fields, filter options available |
| AC4 | Vehicle Selection — detail page shows Range, Year, Seating, Color, Features, Pickup/Drop-off, Pricing |
| AC5 | Pricing Details — base rate, taxes, additional charges, grand total displayed |
| AC6 | Booking/Checkout — auth gate (Log in / Join Us), Pay Now button, auth required |

---

## Test Cases

| # | AC | Type | Scenario | Steps | Expected Result |
|---|----|------|----------|-------|-----------------|
| 1 | AC1 | Happy Path | Select a valid pickup location from autocomplete | 1. Go to homepage 2. Click pickup input 3. Type "New York" 4. Select first suggestion | Pickup input populated with selected location |
| 2 | AC1 | Happy Path | Set a different drop-off location | 1. Go to homepage 2. Select pickup location 3. Click drop-off input 4. Type and select different city | Drop-off input populated with a different location |
| 3 | AC1 | Edge Case | Leave drop-off as default "Same as Pick Up" | 1. Go to homepage 2. Select pickup only 3. Proceed to search | Drop-off placeholder remains "Same as Pick Up"; search succeeds |
| 4 | AC2 | Happy Path | Open date picker and verify calendar is displayed | 1. Go to homepage 2. Click Duration/date section | Calendar widget is visible |
| 5 | AC2 | Happy Path | Default duration value is pre-populated | 1. Go to homepage | Duration section shows a default value (not empty) |
| 6 | AC2 | Edge Case | Select pickup and drop-off dates and verify auto-calculated duration | 1. Go to homepage 2. Open date picker 3. Select a pickup date 4. Select a drop-off date 5 days later | Duration is auto-updated and reflects correct day count |
| 7 | AC3 | Happy Path | Search returns vehicle cards after location selection | 1. Go to homepage 2. Select pickup location 3. Click Search | Navigated to /cars-list; at least one vehicle card visible |
| 8 | AC3 | Happy Path | Each vehicle card displays required fields | 1. Go to homepage 2. Select pickup 3. Click Search | Each card shows: vehicle name, type, daily rate, trip rate, seating, range |
| 9 | AC3 | Happy Path | Filter buttons are available on search results page | 1. Navigate to /cars-list | At least one filter button (Vehicle Type/Brand/Model/Price) is visible |
| 10 | AC3 | Negative | Search without selecting a pickup location | 1. Go to homepage 2. Click Search without entering location | Search does not proceed, or no results returned |
| 11 | AC4 | Happy Path | Click a vehicle card and land on detail/booking page | 1. Navigate to /cars-list 2. Click first vehicle card | URL changes to /booking; car specs container is visible |
| 12 | AC4 | Happy Path | Vehicle detail page shows Range, Year, Seating, Color specs | 1. Click any vehicle card | Spec boxes for Range, Year, Seating, and Color are all visible |
| 13 | AC4 | Happy Path | Vehicle detail page shows Pickup and Drop-off details | 1. Click any vehicle card | Pickup and Drop-off detail sections are displayed |
| 14 | AC5 | Happy Path | Pricing section shows base rate on booking page | 1. Navigate to booking detail page | Base rate row visible with a non-empty value |
| 15 | AC5 | Happy Path | Pricing section shows taxes on booking page | 1. Navigate to booking detail page | Taxes row visible with a calculated value |
| 16 | AC5 | Happy Path | Grand total is prominently displayed | 1. Navigate to booking detail page | Grand total amount is visible and non-zero |
| 17 | AC6 | Happy Path | Pay Now button is visible on booking summary page | 1. Navigate to booking detail page | "Pay Now" button/div is visible |
| 18 | AC6 | Happy Path | Log in / Join Us auth gate appears before payment | 1. Navigate to booking page 2. Click Pay Now | Auth modal/gate with "Log in" or "Join Us" option appears |
| 19 | AC6 | Negative | User cannot complete booking without authentication | 1. Navigate to booking page without logging in | Pay Now is visible but auth gate is triggered; booking not completed |
