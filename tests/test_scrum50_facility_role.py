import allure
from pages.facility_role_page import FacilityRolePage
from config.settings import settings

# TODO: replace with a real case fixture once test data is confirmed for this environment
CASE_WITH_MIXED_ROLES_URL = f"{settings.BASE_URL}/cases/TODO-mixed-primary-roles-case"
CASE_WITH_NO_PRIMARY_ROLES_URL = f"{settings.BASE_URL}/cases/TODO-no-primary-roles-case"
CASE_WITH_ALL_PRIMARY_ROLES_URL = f"{settings.BASE_URL}/cases/TODO-all-primary-roles-case"


@allure.epic("SCRUM-50: Add \"Show Primary Only\" Toggle to Facility & Role View")
@allure.feature("facility_role")
@allure.story("AC1: A Show Primary Only toggle appears on the Facility & Role View tab")
@allure.title("Toggle is visible on Facility & Role View tab")
def test_pos_toggle_visible_on_facility_role_tab(page):
    """
    Jira: SCRUM-50
    AC: A "Show Primary Only" toggle appears on the Facility & Role View tab
    """
    facility_role_page = FacilityRolePage(page)

    with allure.step("Step 1: Navigate to the case detail page"):
        facility_role_page.navigate_to(CASE_WITH_MIXED_ROLES_URL)
        facility_role_page.wait_for_load()

    with allure.step("Step 2: Open the Facility & Role View tab"):
        facility_role_page.open_facility_role_tab()

    with allure.step("Step 3: Verify the Show Primary Only toggle is visible"):
        assert facility_role_page.is_toggle_visible(), "Show Primary Only toggle is not visible"


@allure.epic("SCRUM-50: Add \"Show Primary Only\" Toggle to Facility & Role View")
@allure.feature("facility_role")
@allure.story("AC2: The toggle is enabled (on) by default")
@allure.title("Toggle is on by default")
def test_pos_toggle_enabled_by_default(page):
    """
    Jira: SCRUM-50
    AC: The toggle is enabled (on) by default
    """
    facility_role_page = FacilityRolePage(page)

    with allure.step("Step 1: Navigate to the case detail page"):
        facility_role_page.navigate_to(CASE_WITH_MIXED_ROLES_URL)
        facility_role_page.wait_for_load()

    with allure.step("Step 2: Open the Facility & Role View tab"):
        facility_role_page.open_facility_role_tab()

    with allure.step("Step 3: Verify the toggle is on by default"):
        assert facility_role_page.is_toggle_on(), "Show Primary Only toggle is not on by default"


@allure.epic("SCRUM-50: Add \"Show Primary Only\" Toggle to Facility & Role View")
@allure.feature("facility_role")
@allure.story("AC3: When enabled, only rows where the role is marked as Primary are shown")
@allure.title("Enabling toggle filters grid to Primary rows only")
def test_pos_toggle_on_filters_primary_rows_only(page):
    """
    Jira: SCRUM-50
    AC: When enabled, only rows where the role is marked as Primary are shown
    """
    facility_role_page = FacilityRolePage(page)

    with allure.step("Step 1: Navigate to the case detail page"):
        facility_role_page.navigate_to(CASE_WITH_MIXED_ROLES_URL)
        facility_role_page.wait_for_load()

    with allure.step("Step 2: Open the Facility & Role View tab"):
        facility_role_page.open_facility_role_tab()

    with allure.step("Step 3: Verify the toggle is on by default"):
        assert facility_role_page.is_toggle_on(), "Show Primary Only toggle is not on by default"

    with allure.step("Step 4: Verify every visible row is marked Primary"):
        primary_values = facility_role_page.get_primary_indicator_values()
        assert primary_values, "No rows returned while toggle is on"
        assert all(value.strip().lower() == "primary" for value in primary_values), (
            f"Non-Primary row found while toggle is on: {primary_values}"
        )


@allure.epic("SCRUM-50: Add \"Show Primary Only\" Toggle to Facility & Role View")
@allure.feature("facility_role")
@allure.story("AC4: When disabled, all role assignments are shown regardless of primary status")
@allure.title("Disabling toggle shows all role assignments")
def test_pos_toggle_off_shows_all_role_assignments(page):
    """
    Jira: SCRUM-50
    AC: When disabled, all role assignments are shown regardless of primary status
    """
    facility_role_page = FacilityRolePage(page)

    with allure.step("Step 1: Navigate to the case detail page"):
        facility_role_page.navigate_to(CASE_WITH_MIXED_ROLES_URL)
        facility_role_page.wait_for_load()

    with allure.step("Step 2: Open the Facility & Role View tab"):
        facility_role_page.open_facility_role_tab()

    with allure.step("Step 3: Capture the row count with the toggle on"):
        primary_only_count = facility_role_page.get_role_grid_row_count()

    with allure.step("Step 4: Click the toggle to turn it off"):
        facility_role_page.click_toggle()

    with allure.step("Step 5: Verify the toggle state is off"):
        assert not facility_role_page.is_toggle_on(), "Toggle did not turn off"

    with allure.step("Step 6: Verify the grid now shows more (or equal) rows including non-Primary ones"):
        all_rows_count = facility_role_page.get_role_grid_row_count()
        assert all_rows_count >= primary_only_count, (
            "Row count did not increase after disabling Show Primary Only"
        )


@allure.epic("SCRUM-50: Add \"Show Primary Only\" Toggle to Facility & Role View")
@allure.feature("facility_role")
@allure.story("AC3/AC4: Toggle behavior when case has no Primary role assignments")
@allure.title("Toggle on with no Primary rows shows empty grid")
def test_pos_toggle_on_with_no_primary_rows_shows_empty_grid(page):
    """
    Jira: SCRUM-50
    AC: When enabled, only rows where the role is marked as Primary are shown
    (edge case: no Primary rows exist)
    """
    facility_role_page = FacilityRolePage(page)

    with allure.step("Step 1: Navigate to a case with only non-Primary role rows"):
        facility_role_page.navigate_to(CASE_WITH_NO_PRIMARY_ROLES_URL)
        facility_role_page.wait_for_load()

    with allure.step("Step 2: Open the Facility & Role View tab"):
        facility_role_page.open_facility_role_tab()

    with allure.step("Step 3: Verify the toggle is on by default"):
        assert facility_role_page.is_toggle_on(), "Show Primary Only toggle is not on by default"

    with allure.step("Step 4: Verify the grid shows no rows"):
        assert facility_role_page.get_role_grid_row_count() == 0, (
            "Grid shows rows even though no role is marked Primary"
        )

    with allure.step("Step 5: Click the toggle to turn it off"):
        facility_role_page.click_toggle()

    with allure.step("Step 6: Verify the grid now shows the non-Primary rows"):
        assert facility_role_page.get_role_grid_row_count() > 0, (
            "Grid still shows no rows after disabling Show Primary Only"
        )


@allure.epic("SCRUM-50: Add \"Show Primary Only\" Toggle to Facility & Role View")
@allure.feature("facility_role")
@allure.story("AC3/AC4: Toggle behavior when every role assignment is Primary")
@allure.title("Toggle off with all rows Primary leaves grid unchanged")
def test_pos_toggle_off_with_all_rows_primary_unchanged(page):
    """
    Jira: SCRUM-50
    AC: When disabled, all role assignments are shown regardless of primary status
    (edge case: every row is already Primary)
    """
    facility_role_page = FacilityRolePage(page)

    with allure.step("Step 1: Navigate to a case where every role row is Primary"):
        facility_role_page.navigate_to(CASE_WITH_ALL_PRIMARY_ROLES_URL)
        facility_role_page.wait_for_load()

    with allure.step("Step 2: Open the Facility & Role View tab"):
        facility_role_page.open_facility_role_tab()

    with allure.step("Step 3: Capture the row count with the toggle on"):
        primary_only_count = facility_role_page.get_role_grid_row_count()

    with allure.step("Step 4: Click the toggle to turn it off"):
        facility_role_page.click_toggle()

    with allure.step("Step 5: Verify the row count is unchanged"):
        all_rows_count = facility_role_page.get_role_grid_row_count()
        assert all_rows_count == primary_only_count, (
            "Row count changed even though all rows were already Primary"
        )


@allure.epic("SCRUM-50: Add \"Show Primary Only\" Toggle to Facility & Role View")
@allure.feature("facility_role")
@allure.story("AC5: The toggle state does not persist — it resets to on on page reload")
@allure.title("Toggle resets to on after page reload")
def test_pos_toggle_resets_on_after_page_reload(page):
    """
    Jira: SCRUM-50
    AC: The toggle state does not persist — it resets to on on page reload or tab switch
    """
    facility_role_page = FacilityRolePage(page)

    with allure.step("Step 1: Navigate to the case detail page"):
        facility_role_page.navigate_to(CASE_WITH_MIXED_ROLES_URL)
        facility_role_page.wait_for_load()

    with allure.step("Step 2: Open the Facility & Role View tab"):
        facility_role_page.open_facility_role_tab()

    with allure.step("Step 3: Click the toggle to turn it off"):
        facility_role_page.click_toggle()

    with allure.step("Step 4: Verify the toggle state is off"):
        assert not facility_role_page.is_toggle_on(), "Toggle did not turn off"

    with allure.step("Step 5: Reload the page"):
        facility_role_page.reload_page()

    with allure.step("Step 6: Re-open the Facility & Role View tab"):
        facility_role_page.open_facility_role_tab()

    with allure.step("Step 7: Verify the toggle has reset to on"):
        assert facility_role_page.is_toggle_on(), "Toggle did not reset to on after page reload"


@allure.epic("SCRUM-50: Add \"Show Primary Only\" Toggle to Facility & Role View")
@allure.feature("facility_role")
@allure.story("AC5: The toggle state does not persist — it resets to on on tab switch")
@allure.title("Toggle resets to on after switching tabs")
def test_pos_toggle_resets_on_after_tab_switch(page):
    """
    Jira: SCRUM-50
    AC: The toggle state does not persist — it resets to on on page reload or tab switch
    """
    facility_role_page = FacilityRolePage(page)

    with allure.step("Step 1: Navigate to the case detail page"):
        facility_role_page.navigate_to(CASE_WITH_MIXED_ROLES_URL)
        facility_role_page.wait_for_load()

    with allure.step("Step 2: Open the Facility & Role View tab"):
        facility_role_page.open_facility_role_tab()

    with allure.step("Step 3: Click the toggle to turn it off"):
        facility_role_page.click_toggle()

    with allure.step("Step 4: Verify the toggle state is off"):
        assert not facility_role_page.is_toggle_on(), "Toggle did not turn off"

    with allure.step("Step 5: Switch to the User View tab"):
        facility_role_page.open_user_view_tab()

    with allure.step("Step 6: Switch back to the Facility & Role View tab"):
        facility_role_page.open_facility_role_tab()

    with allure.step("Step 7: Verify the toggle has reset to on"):
        assert facility_role_page.is_toggle_on(), "Toggle did not reset to on after tab switch"


@allure.epic("SCRUM-50: Add \"Show Primary Only\" Toggle to Facility & Role View")
@allure.feature("facility_role")
@allure.story("AC6: The toggle has no effect and is not visible on the User View tab")
@allure.title("Toggle is not visible on User View tab")
def test_err_toggle_not_visible_on_user_view_tab(page):
    """
    Jira: SCRUM-50
    AC: The toggle has no effect and is not visible on the User View tab
    """
    facility_role_page = FacilityRolePage(page)

    with allure.step("Step 1: Navigate to the case detail page"):
        facility_role_page.navigate_to(CASE_WITH_MIXED_ROLES_URL)
        facility_role_page.wait_for_load()

    with allure.step("Step 2: Open the User View tab"):
        facility_role_page.open_user_view_tab()

    with allure.step("Step 3: Verify the Show Primary Only toggle is not present"):
        assert facility_role_page.is_toggle_absent_on_user_view(), (
            "Show Primary Only toggle is unexpectedly visible on the User View tab"
        )


@allure.epic("SCRUM-50: Add \"Show Primary Only\" Toggle to Facility & Role View")
@allure.feature("facility_role")
@allure.story("AC6: The toggle has no effect and is not visible on the User View tab")
@allure.title("Toggle has no effect on User View data")
def test_err_toggle_has_no_effect_on_user_view_data(page):
    """
    Jira: SCRUM-50
    AC: The toggle has no effect and is not visible on the User View tab
    """
    facility_role_page = FacilityRolePage(page)

    with allure.step("Step 1: Navigate to the case detail page"):
        facility_role_page.navigate_to(CASE_WITH_MIXED_ROLES_URL)
        facility_role_page.wait_for_load()

    with allure.step("Step 2: Capture the baseline User View row count"):
        facility_role_page.open_user_view_tab()
        baseline_count = facility_role_page.get_user_view_row_count()

    with allure.step("Step 3: Switch to the Facility & Role View tab and turn the toggle off"):
        facility_role_page.open_facility_role_tab()
        facility_role_page.click_toggle()
        assert not facility_role_page.is_toggle_on(), "Toggle did not turn off"

    with allure.step("Step 4: Switch back to the User View tab"):
        facility_role_page.open_user_view_tab()

    with allure.step("Step 5: Verify the User View row count is unchanged"):
        assert facility_role_page.get_user_view_row_count() == baseline_count, (
            "User View row count changed after toggling Show Primary Only on Facility & Role View tab"
        )
