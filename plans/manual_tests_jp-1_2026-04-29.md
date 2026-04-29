# Manual Test Cases — JP-1: Pre Payment Booking Flow
**Date**: 2026-04-29  
**Jira**: https://innocito.atlassian.net/browse/JP-1  
**Module**: booking  
**Platform**: http://drivejoulez.com

---

## Test Cases

| # | AC | Type | Scenario | Steps | Expected Result |
|---|----|------|----------|-------|-----------------|
| 1 | AC1: Location Selection | Happy Path | Select pickup and drop-off at same location | 1. Navigate to drivejoulez.com 2. Click pickup location dropdown 3. Select an available service location 4. Set drop-off to same location | Selected location saved; drop-off mirrors pickup |
| 2 | AC1: Location Selection | Happy Path | Select different pickup and drop-off locations | 1. Navigate to site 2. Select pickup location 3. Select a different drop-off location | Both locations saved and displayed correctly |
| 3 | AC1: Location Selection | Happy Path | Select delivery option in a supported metro area | 1. Navigate to site 2. Choose "Delivery" option 3. Enter a supported metro address | Delivery option accepted; address confirmed |
| 4 | AC1: Location Selection | Negative | Attempt to search without selecting a pickup location | 1. Navigate to site 2. Skip location selection 3. Click Search/Next | Validation error shown; user cannot proceed |
| 5 | AC2: Date & Time Selection | Happy Path | Select valid pickup and drop-off date/time | 1. Select a future pickup date and time 2. Select drop-off date/time at least 1 day later | Rental duration auto-calculated and displayed |
| 6 | AC2: Date & Time Selection | Happy Path | Verify default values are pre-populated | 1. Navigate to site without changing any fields | Current date pre-filled; morning pickup time pre-filled; 1-day duration shown |
| 7 | AC2: Date & Time Selection | Negative | Set drop-off date earlier than pickup date | 1. Set pickup date to tomorrow 2. Set drop-off date to today | Error shown; invalid date range rejected |
| 8 | AC2: Date & Time Selection | Edge Case | Select same-day pickup and drop-off (minimum rental) | 1. Set pickup and drop-off to same calendar day | Minimum duration enforced or warning displayed |
| 9 | AC3: Vehicle Search | Happy Path | Search returns available EVs for valid inputs | 1. Select valid location, pickup and drop-off dates 2. Click Search | List of EV cards displayed |
| 10 | AC3: Vehicle Search | Happy Path | Each result card displays all required fields | 1. Perform a valid search 2. Inspect each result card | Card shows: vehicle name, type, daily rate, total trip rate, seating capacity, driving range |
| 11 | AC3: Vehicle Search | Happy Path | Filter results by Vehicle Type | 1. Perform search 2. Apply "Vehicle Type" filter | Results narrowed to matching type only |
| 12 | AC3: Vehicle Search | Happy Path | Filter results by Brand | 1. Perform search 2. Apply "Brand" filter | Results narrowed to matching brand only |
| 13 | AC3: Vehicle Search | Happy Path | Filter results by Price range | 1. Perform search 2. Set price range slider/filter | Results show only vehicles within that price range |
| 14 | AC3: Vehicle Search | Negative | Search with no available vehicles for selected criteria | 1. Select location/dates with no inventory | "No vehicles available" or equivalent empty-state message shown |
| 15 | AC4: Vehicle Selection | Happy Path | Click vehicle card opens detail page | 1. Perform valid search 2. Click any vehicle card | Vehicle detail page opens |
| 16 | AC4: Vehicle Selection | Happy Path | Vehicle detail page displays all required fields | 1. Open vehicle detail page | Page shows: Range, Year, Seating capacity, Color, Features, Pickup/Drop-off details, full Pricing breakdown |
| 17 | AC5: Pricing Details | Happy Path | Base rate, taxes and grand total are visible | 1. Select a vehicle 2. Review pricing section | Base rate per day, taxes, any itemised additional charges, and grand total all visible |
| 18 | AC5: Pricing Details | Edge Case | Verify grand total equals base + taxes + charges | 1. Select a vehicle 2. Note base rate, taxes, extras 3. Compute expected total | Displayed grand total matches manual calculation |
| 19 | AC6: Booking/Checkout | Happy Path | Unauthenticated user sees login/signup prompt at checkout | 1. Complete vehicle selection without logging in 2. Click "Pay Now" | Login or "Join Us" prompt displayed; user not sent to payment gateway |
| 20 | AC6: Booking/Checkout | Happy Path | "Pay Now" button is present on booking summary page | 1. Navigate to booking summary page | "Pay Now" button visible and enabled |
| 21 | AC6: Booking/Checkout | Negative | Unauthenticated user cannot complete booking | 1. Attempt to reach payment step without authenticating | User redirected to login/signup; booking not confirmed |
