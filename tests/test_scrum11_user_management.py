import allure
from pages.user_management_page import UserManagementPage
from config.settings import settings

# TODO: replace with real fixtures once test data is confirmed for this environment
USER_WITH_MIXED_ROLES_URL = f"{settings.BASE_URL}/user-management/TODO-user-mixed-roles"
USER_WITH_NO_PRIMARY_ROLES_URL = f"{settings.BASE_URL}/user-management/TODO-user-no-primary-roles"
VIEWER_ROLE_USERNAME = "TODO-viewer-role-username"
VIEWER_ROLE_PASSWORD = "TODO-viewer-role-password"


@allure.epic('SCRUM-11: Add "Show Primary Only" Toggle to Facility & Role View')
@allure.feature("user_management")
@allure.story("AC1: A Show Primary Only toggle appears on the Facility & Role View tab")
@allure.title("Toggle is visible on Facility & Role View tab")
def test_pos_toggle_visible_on_facility_role_view(page):
    """
    Jira: SCRUM-11
    AC: A "Show Primary Only" toggle appears on the Facility & Role View tab
    """
    um_page = UserManagementPage(page)

    with allure.step("Navigate to the User Management page"):
        um_page.navigate_to_user_management()
        um_page.wait_for_load()

    with allure.step("Verify the Facility & Role View tab is visible"):
        assert um_page.is_facility_role_view_tab_visible(), "Facility & Role View tab not visible"

    with allure.step("Click the Facility & Role View tab"):
        um_page.open_facility_role_view_tab()

    with allure.step("Verify the Show Primary Only toggle is visible"):
        assert um_page.is_show_primary_only_toggle_visible(), "Show Primary Only toggle not visible"


@allure.epic('SCRUM-11: Add "Show Primary Only" Toggle to Facility & Role View')
@allure.feature("user_management")
@allure.story("AC2: The toggle is enabled (on) by default")
@allure.title("Toggle is on by default")
def test_pos_toggle_on_by_default(page):
    """
    Jira: SCRUM-11
    AC: The toggle is enabled (on) by default
    """
    um_page = UserManagementPage(page)

    with allure.step("Navigate to the Facility & Role View tab"):
        um_page.navigate_to_user_management()
        um_page.wait_for_load()
        um_page.open_facility_role_view_tab()

    with allure.step("Verify the toggle is checked (on)"):
        assert um_page.is_show_primary_only_toggle_checked(), "Toggle is not on by default"


@allure.epic('SCRUM-11: Add "Show Primary Only" Toggle to Facility & Role View')
@allure.feature("user_management")
@allure.story("AC3: When enabled, only rows where the role is marked as Primary are shown")
@allure.title("Toggle on shows only primary rows")
def test_pos_toggle_on_shows_only_primary_rows(page):
    """
    Jira: SCRUM-11
    AC: When enabled, only rows where the role is marked as Primary are shown
    """
    um_page = UserManagementPage(page)

    with allure.step("Navigate to the Facility & Role View tab for a user with mixed roles"):
        um_page.navigate_to_user_management()
        um_page.navigate_to(USER_WITH_MIXED_ROLES_URL)
        um_page.wait_for_load()
        um_page.open_facility_role_view_tab()

    with allure.step("Verify the toggle is on"):
        assert um_page.is_show_primary_only_toggle_checked(), "Toggle expected to be on"

    with allure.step("Verify every visible row is marked Primary"):
        assert um_page.all_rows_marked_primary(), "Non-primary row visible while toggle is on"


@allure.epic('SCRUM-11: Add "Show Primary Only" Toggle to Facility & Role View')
@allure.feature("user_management")
@allure.story("AC4: When disabled, all role assignments are shown regardless of primary status")
@allure.title("Toggle off shows all role assignments")
def test_pos_toggle_off_shows_all_role_assignments(page):
    """
    Jira: SCRUM-11
    AC: When disabled, all role assignments are shown regardless of primary status
    """
    um_page = UserManagementPage(page)

    with allure.step("Navigate to the Facility & Role View tab for a user with mixed roles"):
        um_page.navigate_to_user_management()
        um_page.navigate_to(USER_WITH_MIXED_ROLES_URL)
        um_page.wait_for_load()
        um_page.open_facility_role_view_tab()

    with allure.step("Record the row count with the toggle on"):
        primary_only_count = um_page.get_grid_row_count()

    with allure.step("Click the toggle to switch it off"):
        um_page.click_show_primary_only_toggle()

    with allure.step("Verify the row count increases and includes non-primary rows"):
        assert um_page.get_grid_row_count() > primary_only_count, "Row count did not increase when toggle switched off"
        assert um_page.any_row_not_primary(), "No non-primary row visible with toggle off"


@allure.epic('SCRUM-11: Add "Show Primary Only" Toggle to Facility & Role View')
@allure.feature("user_management")
@allure.story("AC5: The toggle state does not persist across page reload")
@allure.title("Toggle resets to on after page reload")
def test_pos_toggle_resets_to_on_after_page_reload(page):
    """
    Jira: SCRUM-11
    AC: The toggle state does not persist — it resets to on on page reload
    """
    um_page = UserManagementPage(page)

    with allure.step("Navigate to the Facility & Role View tab and switch the toggle off"):
        um_page.navigate_to_user_management()
        um_page.wait_for_load()
        um_page.open_facility_role_view_tab()
        um_page.click_show_primary_only_toggle()
        assert not um_page.is_show_primary_only_toggle_checked(), "Toggle did not switch off"

    with allure.step("Reload the page"):
        um_page.reload_page()
        um_page.open_facility_role_view_tab()

    with allure.step("Verify the toggle is on again"):
        assert um_page.is_show_primary_only_toggle_checked(), "Toggle did not reset to on after reload"


@allure.epic('SCRUM-11: Add "Show Primary Only" Toggle to Facility & Role View')
@allure.feature("user_management")
@allure.story("AC5: The toggle state does not persist across tab switch")
@allure.title("Toggle resets to on after tab switch")
def test_pos_toggle_resets_to_on_after_tab_switch(page):
    """
    Jira: SCRUM-11
    AC: The toggle state does not persist — it resets to on on tab switch
    """
    um_page = UserManagementPage(page)

    with allure.step("Navigate to the Facility & Role View tab and switch the toggle off"):
        um_page.navigate_to_user_management()
        um_page.wait_for_load()
        um_page.open_facility_role_view_tab()
        um_page.click_show_primary_only_toggle()
        assert not um_page.is_show_primary_only_toggle_checked(), "Toggle did not switch off"

    with allure.step("Switch to the User View tab and back"):
        um_page.open_user_view_tab()
        um_page.open_facility_role_view_tab()

    with allure.step("Verify the toggle is on again"):
        assert um_page.is_show_primary_only_toggle_checked(), "Toggle did not reset to on after tab switch"


@allure.epic('SCRUM-11: Add "Show Primary Only" Toggle to Facility & Role View')
@allure.feature("user_management")
@allure.story("AC6: The toggle is not visible on the User View tab")
@allure.title("Toggle not visible on User View tab")
def test_pos_toggle_not_visible_on_user_view_tab(page):
    """
    Jira: SCRUM-11
    AC: The toggle has no effect and is not visible on the User View tab
    """
    um_page = UserManagementPage(page)

    with allure.step("Navigate to the User Management page (User View tab active by default)"):
        um_page.navigate_to_user_management()
        um_page.wait_for_load()

    with allure.step("Verify the Show Primary Only toggle is not visible"):
        assert not um_page.is_show_primary_only_toggle_visible(), "Toggle unexpectedly visible on User View tab"


@allure.epic('SCRUM-11: Add "Show Primary Only" Toggle to Facility & Role View')
@allure.feature("user_management")
@allure.story("AC3: Toggle on with zero primary roles shows an empty grid")
@allure.title("No primary roles shows empty grid when toggled on")
def test_err_no_primary_roles_shows_empty_grid(page):
    """
    Jira: SCRUM-11
    AC: When enabled, only rows where the role is marked as Primary are shown
    Edge case: a user with zero Primary-marked role assignments
    """
    um_page = UserManagementPage(page)

    with allure.step("Navigate to the Facility & Role View tab for a user with no primary roles"):
        um_page.navigate_to_user_management()
        um_page.navigate_to(USER_WITH_NO_PRIMARY_ROLES_URL)
        um_page.wait_for_load()
        um_page.open_facility_role_view_tab()

    with allure.step("Verify the toggle is on and the grid is empty"):
        assert um_page.is_show_primary_only_toggle_checked(), "Toggle expected to be on"
        assert um_page.is_grid_empty_state_visible(), "Empty state not shown for user with no primary roles"

    with allure.step("Switch the toggle off and verify rows appear"):
        um_page.click_show_primary_only_toggle()
        assert um_page.get_grid_row_count() > 0, "No rows shown after switching toggle off"


@allure.epic('SCRUM-11: Add "Show Primary Only" Toggle to Facility & Role View')
@allure.feature("user_management")
@allure.story("AC4: Toggling off then on returns to the original filtered state")
@allure.title("Toggle off then on is idempotent")
def test_pos_toggle_off_then_on_is_idempotent(page):
    """
    Jira: SCRUM-11
    AC: When disabled, all role assignments are shown; when re-enabled, only Primary rows show again
    """
    um_page = UserManagementPage(page)

    with allure.step("Navigate to the Facility & Role View tab for a user with mixed roles"):
        um_page.navigate_to_user_management()
        um_page.navigate_to(USER_WITH_MIXED_ROLES_URL)
        um_page.wait_for_load()
        um_page.open_facility_role_view_tab()

    with allure.step("Record the row count with the toggle on"):
        primary_only_count = um_page.get_grid_row_count()

    with allure.step("Switch the toggle off"):
        um_page.click_show_primary_only_toggle()
        assert um_page.get_grid_row_count() > primary_only_count, "Row count did not increase when toggle switched off"

    with allure.step("Switch the toggle back on"):
        um_page.click_show_primary_only_toggle()

    with allure.step("Verify the row count matches the original primary-only count"):
        assert um_page.get_grid_row_count() == primary_only_count, "Row count did not return to primary-only count"


@allure.epic('SCRUM-11: Add "Show Primary Only" Toggle to Facility & Role View')
@allure.feature("user_management")
@allure.story("AC6: Toggling on Facility & Role View does not affect User View rows")
@allure.title("Toggle does not affect User View rows")
def test_err_toggle_does_not_affect_user_view_rows(page):
    """
    Jira: SCRUM-11
    AC: The toggle has no effect and is not visible on the User View tab
    """
    um_page = UserManagementPage(page)

    with allure.step("Navigate to the User View tab and record the row count"):
        um_page.navigate_to_user_management()
        um_page.wait_for_load()
        user_view_row_count = um_page.get_grid_row_count()

    with allure.step("Switch to the Facility & Role View tab and toggle off"):
        um_page.open_facility_role_view_tab()
        um_page.click_show_primary_only_toggle()

    with allure.step("Switch back to the User View tab and verify the row count is unchanged"):
        um_page.open_user_view_tab()
        assert um_page.get_grid_row_count() == user_view_row_count, "User View row count changed unexpectedly"


@allure.epic('SCRUM-11: Add "Show Primary Only" Toggle to Facility & Role View')
@allure.feature("user_management")
@allure.story("AC1: The toggle is keyboard-operable and has an accessible name")
@allure.title("Toggle is keyboard operable with accessible name")
def test_pos_toggle_keyboard_operable_with_accessible_name(page):
    """
    Jira: SCRUM-11
    AC: A "Show Primary Only" toggle appears on the Facility & Role View tab
    """
    um_page = UserManagementPage(page)

    with allure.step("Navigate to the Facility & Role View tab"):
        um_page.navigate_to_user_management()
        um_page.wait_for_load()
        um_page.open_facility_role_view_tab()

    with allure.step("Focus the toggle via keyboard and verify its accessible name"):
        um_page.focus_show_primary_only_toggle()
        accessible_name = um_page.get_show_primary_only_toggle_accessible_name()
        assert "Show Primary Only" in accessible_name, "Toggle accessible name missing or incorrect"

    with allure.step("Press Space to activate the toggle and verify state changes"):
        was_checked = um_page.is_show_primary_only_toggle_checked()
        um_page.press_key("Space")
        assert um_page.is_show_primary_only_toggle_checked() != was_checked, "Toggle state did not change on Space key"


@allure.epic('SCRUM-11: Add "Show Primary Only" Toggle to Facility & Role View')
@allure.feature("user_management")
@allure.story("AC1: RBAC - Viewer role cannot access the Facility & Role View tab")
@allure.title("Viewer cannot access Facility & Role View tab")
def test_perm_viewer_cannot_access_facility_role_view(page):
    """
    Jira: SCRUM-11
    AC: A "Show Primary Only" toggle appears on the Facility & Role View tab
    RBAC: verifies the tab/toggle is restricted for the Viewer role
    """
    um_page = UserManagementPage(page)

    with allure.step("Navigate to the User Management page as a Viewer-role user"):
        um_page.navigate_to_user_management()
        um_page.wait_for_load()

    with allure.step("Verify the Facility & Role View tab is not accessible to the Viewer role"):
        assert not um_page.is_facility_role_view_tab_visible(), "Facility & Role View tab unexpectedly accessible to Viewer role"
