# Manual Test Cases — JP-5: Jourez check Pickup location enhanced
**Date**: 2026-05-05
**Jira**: https://innocito.atlassian.net/browse/JP-5
**Module**: booking
**Platform**: http://drivejoulez.com

---

## Acceptance Criteria

**AC1: Pickup Location** — User should be able to select the pickup location from the auto dropdown.

---

## Test Cases

| # | AC | Type | Scenario | Steps | Expected Result |
|---|----|------|----------|-------|-----------------|
| 1 | AC1 | Happy Path | Select a valid pickup location from the autocomplete dropdown | 1. Navigate to drivejoulez.com<br>2. Click the pickup location input<br>3. Type a valid location query (e.g. "New York")<br>4. Click the first `.pac-item` suggestion | Pickup input shows the selected location; suggestion list closes |
| 2 | AC1 | Happy Path | Autocomplete dropdown appears as the user types | 1. Navigate to homepage<br>2. Click pickup input<br>3. Type "Manhat" | At least one `.pac-item` suggestion is rendered and visible |
| 3 | AC1 | Edge Case | Suggestion list disappears after a selection is made | 1. Navigate to homepage<br>2. Type a partial query into pickup input<br>3. Click any suggestion in the dropdown | After selection, no `.pac-item` elements remain visible |
| 4 | AC1 | Negative | Typing a nonsense query yields no suggestions | 1. Navigate to homepage<br>2. Click pickup input<br>3. Type random gibberish (e.g. "zzzzqxyqxq") | No `.pac-item` suggestions appear / the suggestion list is empty |

---

## Coverage Summary

- **Total cases**: 4
- **Happy Path**: 2 (TC1, TC2)
- **Edge Case**: 1 (TC3)
- **Negative**: 1 (TC4)
- **AC coverage**: AC1 (1/1)

## Notes

- The existing `BookingPage` POM already exposes `select_pickup_location()`, `pickup_location_input`, and `location_suggestions`. TC1 reuses these directly. TC2-TC4 need a small helper to type without auto-picking the first suggestion — to be added to `BookingPage` during script generation.
- All timeouts will use `settings.TIMEOUT` / `settings.PAGE_LOAD_TIMEOUT`; no raw integers per project rules.
- Tests will run against `settings.BASE_URL` (expected to be `http://drivejoulez.com`).
