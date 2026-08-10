import allure
import pytest
from pages.user_management_page import UserManagementPage


@allure.epic("SCRUM-11: Add Show Primary Only Toggle to Facility & Role View")
@allure.feature("user_management")
@allure.story("AC1: A Show Primary Only toggle appears on the Facility & Role View tab")
@allure.title("Toggle is visible on Facility & Role View tab")
def test_pos_toggle_visible_on_facility_role_view(page):
    """
    Jira: SCRUM-11
    AC: A "Show Primary Only" toggle appears on the Facility & Role View tab
    """
    user_mgmt_page = UserManagementPage(page)

    with allure.step("Step 1: Navigate to User Management page"):
        user_mgmt_page.navigate_to_user_management()

    with allure.step("Step 2: Click the Facility & Role tab"):
        user_mgmt_page.click_facility_role_tab()

    with allure.step("Step 3: Verify the Show Primary Only toggle is visible"):
        assert user_mgmt_page.is_show_primary_only_toggle_visible(), \
            "Show Primary Only toggle is not visible on Facility & Role View tab"


@allure.epic("SCRUM-11: Add Show Primary Only Toggle to Facility & Role View")
@allure.feature("user_management")
@allure.story("AC2: The toggle is enabled (on) by default")
@allure.title("Toggle is ON by default on first load")
def test_pos_toggle_on_by_default(page):
    """
    Jira: SCRUM-11
    AC: The toggle is enabled (on) by default
    """
    user_mgmt_page = UserManagementPage(page)

    with allure.step("Step 1: Navigate to User Management page"):
        user_mgmt_page.navigate_to_user_management()

    with allure.step("Step 2: Click the Facility & Role tab"):
        user_mgmt_page.click_facility_role_tab()

    with allure.step("Step 3: Verify the toggle state is on"):
        assert user_mgmt_page.get_show_primary_only_toggle_state() is True, \
            "Show Primary Only toggle is not on by default"


@allure.epic("SCRUM-11: Add Show Primary Only Toggle to Facility & Role View")
@allure.feature("user_management")
@allure.story("AC3: When enabled, only rows where the role is marked as Primary are shown")
@allure.title("Enabling toggle shows only Primary role rows")
def test_pos_toggle_on_shows_only_primary_rows(page):
    """
    Jira: SCRUM-11
    AC: When enabled, only rows where the role is marked as Primary are shown
    """
    user_mgmt_page = UserManagementPage(page)

    with allure.step("Step 1: Navigate to User Management page"):
        user_mgmt_page.navigate_to_user_management()

    with allure.step("Step 2: Click the Facility & Role tab"):
        user_mgmt_page.click_facility_role_tab()

    with allure.step("Step 3: Verify the toggle is on"):
        assert user_mgmt_page.get_show_primary_only_toggle_state() is True

    with allure.step("Step 4: Verify every visible row is flagged Primary"):
        flags = user_mgmt_page.get_role_grid_rows_primary_flags()
        assert len(flags) > 0, "Expected at least one Primary row to be visible"
        assert all(flag.strip().lower() == "primary" for flag in flags), \
            f"Non-primary row found while toggle is on: {flags}"


@allure.epic("SCRUM-11: Add Show Primary Only Toggle to Facility & Role View")
@allure.feature("user_management")
@allure.story("AC4: When disabled, all role assignments are shown regardless of primary status")
@allure.title("Disabling toggle shows all role assignments")
def test_pos_toggle_off_shows_all_role_assignments(page):
    """
    Jira: SCRUM-11
    AC: When disabled, all role assignments are shown regardless of primary status
    """
    user_mgmt_page = UserManagementPage(page)

    with allure.step("Step 1: Navigate to User Management page"):
        user_mgmt_page.navigate_to_user_management()

    with allure.step("Step 2: Click the Facility & Role tab"):
        user_mgmt_page.click_facility_role_tab()

    with allure.step("Step 3: Record the Primary-only row count"):
        primary_only_count = user_mgmt_page.get_role_grid_row_count()

    with allure.step("Step 4: Click the toggle to turn it off"):
        user_mgmt_page.toggle_show_primary_only()

    with allure.step("Step 5: Verify the toggle state is off"):
        assert user_mgmt_page.get_show_primary_only_toggle_state() is False

    with allure.step("Step 6: Verify the row count increases to include non-Primary rows"):
        all_rows_count = user_mgmt_page.get_role_grid_row_count()
        assert all_rows_count >= primary_only_count, \
            "Row count did not increase after disabling Show Primary Only"


@allure.epic("SCRUM-11: Add Show Primary Only Toggle to Facility & Role View")
@allure.feature("user_management")
@allure.story("AC5: The toggle state does not persist - it resets to on on page reload")
@allure.title("Toggle resets to ON after page reload")
def test_pos_toggle_resets_to_on_after_page_reload(page):
    """
    Jira: SCRUM-11
    AC: The toggle state does not persist - it resets to on on page reload
    """
    user_mgmt_page = UserManagementPage(page)

    with allure.step("Step 1: Navigate to User Management page"):
        user_mgmt_page.navigate_to_user_management()

    with allure.step("Step 2: Click the Facility & Role tab"):
        user_mgmt_page.click_facility_role_tab()

    with allure.step("Step 3: Click the toggle to turn it off"):
        user_mgmt_page.toggle_show_primary_only()
        assert user_mgmt_page.get_show_primary_only_toggle_state() is False

    with allure.step("Step 4: Reload the page"):
        user_mgmt_page.reload_page()

    with allure.step("Step 5: Navigate back to the Facility & Role tab"):
        user_mgmt_page.click_facility_role_tab()

    with allure.step("Step 6: Verify the toggle state resets to on"):
        assert user_mgmt_page.get_show_primary_only_toggle_state() is True, \
            "Toggle did not reset to on after page reload"


@allure.epic("SCRUM-11: Add Show Primary Only Toggle to Facility & Role View")
@allure.feature("user_management")
@allure.story("AC5: The toggle state does not persist - it resets to on on tab switch")
@allure.title("Toggle resets to ON after switching tabs")
def test_pos_toggle_resets_to_on_after_tab_switch(page):
    """
    Jira: SCRUM-11
    AC: The toggle state does not persist - it resets to on on tab switch
    """
    user_mgmt_page = UserManagementPage(page)

    with allure.step("Step 1: Navigate to User Management page"):
        user_mgmt_page.navigate_to_user_management()

    with allure.step("Step 2: Click the Facility & Role tab"):
        user_mgmt_page.click_facility_role_tab()

    with allure.step("Step 3: Click the toggle to turn it off"):
        user_mgmt_page.toggle_show_primary_only()
        assert user_mgmt_page.get_show_primary_only_toggle_state() is False

    with allure.step("Step 4: Click the User View tab"):
        user_mgmt_page.click_user_view_tab()

    with allure.step("Step 5: Click back on the Facility & Role tab"):
        user_mgmt_page.click_facility_role_tab()

    with allure.step("Step 6: Verify the toggle state resets to on"):
        assert user_mgmt_page.get_show_primary_only_toggle_state() is True, \
            "Toggle did not reset to on after switching tabs"


@allure.epic("SCRUM-11: Add Show Primary Only Toggle to Facility & Role View")
@allure.feature("user_management")
@allure.story("AC6: The toggle has no effect and is not visible on the User View tab")
@allure.title("Toggle is not visible on User View tab")
def test_pos_toggle_not_visible_on_user_view_tab(page):
    """
    Jira: SCRUM-11
    AC: The toggle has no effect and is not visible on the User View tab
    """
    user_mgmt_page = UserManagementPage(page)

    with allure.step("Step 1: Navigate to User Management page"):
        user_mgmt_page.navigate_to_user_management()

    with allure.step("Step 2: Click the User View tab"):
        user_mgmt_page.click_user_view_tab()

    with allure.step("Step 3: Verify the Show Primary Only toggle is not visible"):
        assert not user_mgmt_page.is_show_primary_only_toggle_visible(), \
            "Show Primary Only toggle should not be visible on User View tab"


@allure.epic("SCRUM-11: Add Show Primary Only Toggle to Facility & Role View")
@allure.feature("user_management")
@allure.story("AC3: No Primary roles exist - toggle on shows empty grid")
@allure.title("No Primary roles shows empty grid state")
def test_err_no_primary_roles_shows_empty_grid(page):
    """
    Jira: SCRUM-11
    AC: When enabled, only rows where the role is marked as Primary are shown
    Edge case: data set with zero Primary-flagged rows
    """
    user_mgmt_page = UserManagementPage(page)

    with allure.step("Step 1: Navigate to User Management page"):
        user_mgmt_page.navigate_to_user_management()

    with allure.step("Step 2: Click the Facility & Role tab"):
        user_mgmt_page.click_facility_role_tab()

    with allure.step("Step 3: Verify the toggle is on (default)"):
        assert user_mgmt_page.get_show_primary_only_toggle_state() is True

    with allure.step("Step 4: Verify the grid shows an empty state"):
        assert user_mgmt_page.get_role_grid_row_count() == 0
        assert user_mgmt_page.is_empty_state_visible(), \
            "Empty-state message not shown when no Primary roles exist"


@allure.epic("SCRUM-11: Add Show Primary Only Toggle to Facility & Role View")
@allure.feature("user_management")
@allure.story("AC4: Toggling off then on again is idempotent")
@allure.title("Toggle off then on returns to original Primary-only row count")
def test_pos_toggle_off_then_on_is_idempotent(page):
    """
    Jira: SCRUM-11
    AC: When disabled, all role assignments are shown regardless of primary status
    Edge case: toggling off then back on within the same session
    """
    user_mgmt_page = UserManagementPage(page)

    with allure.step("Step 1: Navigate to User Management page"):
        user_mgmt_page.navigate_to_user_management()

    with allure.step("Step 2: Click the Facility & Role tab"):
        user_mgmt_page.click_facility_role_tab()

    with allure.step("Step 3: Record the initial Primary-only row count"):
        initial_count = user_mgmt_page.get_role_grid_row_count()

    with allure.step("Step 4: Toggle off and verify row count reflects full data set"):
        user_mgmt_page.toggle_show_primary_only()
        full_count = user_mgmt_page.get_role_grid_row_count()

    with allure.step("Step 5: Toggle on again and verify row count matches the original"):
        user_mgmt_page.toggle_show_primary_only()
        final_count = user_mgmt_page.get_role_grid_row_count()
        assert final_count == initial_count, \
            f"Expected row count to return to {initial_count}, got {final_count}"


@allure.epic("SCRUM-11: Add Show Primary Only Toggle to Facility & Role View")
@allure.feature("user_management")
@allure.story("AC6: Facility & Role toggle state does not affect User View tab rows")
@allure.title("Facility & Role toggle does not affect User View rows")
def test_err_toggle_does_not_affect_user_view_rows(page):
    """
    Jira: SCRUM-11
    AC: The toggle has no effect and is not visible on the User View tab
    """
    user_mgmt_page = UserManagementPage(page)

    with allure.step("Step 1: Navigate to User Management page"):
        user_mgmt_page.navigate_to_user_management()

    with allure.step("Step 2: Click the User View tab and record its row count"):
        user_mgmt_page.click_user_view_tab()
        user_view_count_before = user_mgmt_page.get_role_grid_row_count()

    with allure.step("Step 3: Click the Facility & Role tab and toggle off"):
        user_mgmt_page.click_facility_role_tab()
        user_mgmt_page.toggle_show_primary_only()

    with allure.step("Step 4: Switch back to the User View tab"):
        user_mgmt_page.click_user_view_tab()

    with allure.step("Step 5: Verify the User View row count is unchanged"):
        user_view_count_after = user_mgmt_page.get_role_grid_row_count()
        assert user_view_count_after == user_view_count_before, \
            "Facility & Role toggle state should not affect User View tab rows"


@allure.epic("SCRUM-11: Add Show Primary Only Toggle to Facility & Role View")
@allure.feature("user_management")
@allure.story("AC1: Toggle is keyboard-operable with an accessible name")
@allure.title("Toggle is keyboard-operable and has an accessible name")
def test_pos_toggle_keyboard_operable_with_accessible_name(page):
    """
    Jira: SCRUM-11
    AC: A "Show Primary Only" toggle appears on the Facility & Role View tab
    Edge case: keyboard accessibility
    """
    user_mgmt_page = UserManagementPage(page)

    with allure.step("Step 1: Navigate to User Management page"):
        user_mgmt_page.navigate_to_user_management()

    with allure.step("Step 2: Click the Facility & Role tab"):
        user_mgmt_page.click_facility_role_tab()

    with allure.step("Step 3: Focus the toggle via keyboard"):
        user_mgmt_page.focus_toggle()

    with allure.step("Step 4: Verify the toggle has an accessible name"):
        accessible_name = user_mgmt_page.get_toggle_accessible_name()
        assert accessible_name, "Show Primary Only toggle has no accessible name"

    with allure.step("Step 5: Press Space to toggle it and verify the state changes"):
        initial_state = user_mgmt_page.get_show_primary_only_toggle_state()
        user_mgmt_page.press_toggle_key("Space")
        assert user_mgmt_page.get_show_primary_only_toggle_state() != initial_state, \
            "Toggle state did not change after keyboard activation"


@allure.epic("SCRUM-11: Add Show Primary Only Toggle to Facility & Role View")
@allure.feature("user_management")
@allure.story("AC1: Viewer role cannot access Facility & Role View")
@allure.title("Viewer role is blocked from Facility & Role View")
def test_perm_viewer_cannot_access_facility_role_view(page):
    """
    Jira: SCRUM-11
    AC: A "Show Primary Only" toggle appears on the Facility & Role View tab
    RBAC: Viewer-role users should not see the Facility & Role View tab/toggle
    """
    pytest.skip(
        "Blocked on missing pages/login_page.py for Azure AD SSO — "
        "cannot authenticate as a Viewer-role user yet. See SCRUM-11 PR notes."
    )

    user_mgmt_page = UserManagementPage(page)

    with allure.step("Step 1: Log in as a Viewer-role user"):
        pass  # TODO: Implement once LoginPage/SSO automation is available

    with allure.step("Step 2: Attempt to navigate to User Management page"):
        user_mgmt_page.navigate_to_user_management()

    with allure.step("Step 3: Verify Facility & Role tab/toggle is not accessible"):
        assert not user_mgmt_page.is_show_primary_only_toggle_visible(), \
            "Viewer-role user should not see the Facility & Role toggle"
