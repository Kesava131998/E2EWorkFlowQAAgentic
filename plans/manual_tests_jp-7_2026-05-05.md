# Manual Test Cases — JP-7: Jourez check Pickup location enhanced with search
**Date**: 2026-05-05
**Jira**: https://innocito.atlassian.net/browse/JP-7
**Module**: booking
**Platform**: http://drivejoulez.com

---

## Acceptance Criteria

**AC1: Pickup Location** — User should be able to select the pickup location from the auto dropdown **and search**.

Interpretation: this AC extends JP-5's pickup-selection behaviour by asserting that, once a pickup is chosen, clicking the **Search** control navigates to the vehicle list (`/cars-list`) and returns at least one result. JP-5 covered the autocomplete dropdown alone; JP-7 wires *pickup → search → results* end-to-end.

---

## Test Cases

| # | AC | Type | Scenario | Steps | Expected Result |
|---|----|------|----------|-------|-----------------|
| 1 | AC1 | Happy Path | Pickup selection + Search button → results page | 1. Navigate to drivejoulez.com<br>2. Select pickup "New York" via autocomplete<br>3. Click the Search button | URL changes to `**/cars-list`; page loads `domcontentloaded` |
| 2 | AC1 | Happy Path | Search returns at least one vehicle card | 1. From homepage, select pickup "New York"<br>2. Click Search | `/cars-list` shows ≥1 visible `.card.cursorPointer` vehicle card |
| 3 | AC1 | Edge Case | Default "Same as Pick Up" dropoff carries through to search | 1. Navigate to homepage<br>2. Select pickup "New York" only — leave drop-off untouched<br>3. Click Search | Navigation succeeds to `/cars-list`; results render (default drop-off mirrors pickup) |

---

## Coverage Summary

- **Total cases**: 3
- **Happy Path**: 2 (TC1, TC2)
- **Edge Case**: 1 (TC3)
- **AC coverage**: AC1 (1/1)

## Notes

- `BookingPage.click_search()` already exists; tests reuse it directly. No new POM helper needed.
- `vehicle_cards` locator (`.card.cursorPointer`) and `get_vehicle_card_count()` already exist and are reused for TC2.
- All timeouts use `settings.TIMEOUT` / `settings.PAGE_LOAD_TIMEOUT` — no raw integers introduced.
- Tests run against `settings.BASE_URL` (drivejoulez.com via `.env`).
- No negative case: AC1 is positive enablement; the platform's behaviour for "search without pickup" is not specified, and a speculative negative would be flake-prone without server-side validation rules to anchor against.
