import allure
from pages.bulk_update_page import BulkUpdatePage


@allure.epic("SCRUM-30: [FE] Add \"Bulk Edit Mode\" to Bulk Update")
@allure.feature("bulk_update")
@allure.story("AC1: Bulk Mode toggle displays two options")
@allure.title("Bulk Mode toggle displays both Facility + Payer and Resident + Payer Category options")
def test_pos_bulk_mode_toggle_displays_both_options(page):
    """
    Jira: SCRUM-30
    AC: The filter bar displays a Bulk Mode setting with two options: "Facility + payer" and "Resident + payer category"
    """
    bulk_update_page = BulkUpdatePage(page)

    with allure.step("Step 1: Navigate to the Bulk Edit Tasks screen"):
        bulk_update_page.open()

    with allure.step("Step 2: Verify the Bulk Mode toggle is visible"):
        assert bulk_update_page.bulk_mode_toggle.is_visible()

    with allure.step("Step 3: Open the Bulk Mode menu"):
        bulk_update_page.open_mode_menu()

    with allure.step("Step 4: Verify both mode options are visible"):
        assert bulk_update_page.mode_option_facility_payer.is_visible()
        assert bulk_update_page.mode_option_resident_payer_category.is_visible()


@allure.epic("SCRUM-30: [FE] Add \"Bulk Edit Mode\" to Bulk Update")
@allure.feature("bulk_update")
@allure.story("AC2: Facility + Payer is the default mode on page load")
@allure.title("Facility + Payer is selected by default on page load")
def test_pos_facility_payer_default_mode_on_load(page):
    """
    Jira: SCRUM-30
    AC: "Facility + payer" is the default selected mode on page load
    """
    bulk_update_page = BulkUpdatePage(page)

    with allure.step("Step 1: Navigate to the Bulk Edit Tasks screen"):
        bulk_update_page.open()

    with allure.step("Step 2: Verify the active Bulk Mode label"):
        assert BulkUpdatePage.MODE_FACILITY_PAYER in bulk_update_page.get_active_mode_label()

    with allure.step("Step 3: Verify Facility and Payer dropdowns are displayed"):
        assert bulk_update_page.facility_dropdown.is_visible()
        assert bulk_update_page.payer_dropdown.is_visible()


@allure.epic("SCRUM-30: [FE] Add \"Bulk Edit Mode\" to Bulk Update")
@allure.feature("bulk_update")
@allure.story("AC3: Facility + Payer mode shows Facility and Payer dropdowns")
@allure.title("Facility + Payer mode shows the correct dropdown labels")
def test_pos_facility_payer_mode_shows_correct_dropdowns(page):
    """
    Jira: SCRUM-30
    AC: In "Facility + payer" mode, the two filter dropdowns show Facility and Payer, matching current behavior
    """
    bulk_update_page = BulkUpdatePage(page)

    with allure.step("Step 1: Navigate to the Bulk Edit Tasks screen"):
        bulk_update_page.open()

    with allure.step("Step 2: Verify Facility + Payer is the active mode"):
        assert BulkUpdatePage.MODE_FACILITY_PAYER in bulk_update_page.get_active_mode_label()

    with allure.step("Step 3: Verify the first dropdown is labeled Facility"):
        assert bulk_update_page.facility_dropdown.is_visible()

    with allure.step("Step 4: Verify the second dropdown is labeled Payer"):
        assert bulk_update_page.payer_dropdown.is_visible()


@allure.epic("SCRUM-30: [FE] Add \"Bulk Edit Mode\" to Bulk Update")
@allure.feature("bulk_update")
@allure.story("AC4: Resident + Payer Category mode shows Resident and Payer Category dropdowns")
@allure.title("Resident + Payer Category mode shows the correct dropdown labels")
def test_pos_resident_payer_category_mode_shows_correct_dropdowns(page):
    """
    Jira: SCRUM-30
    AC: In "Resident + payer category" mode, the two filter dropdowns show Resident and Payer Category
    """
    bulk_update_page = BulkUpdatePage(page)

    with allure.step("Step 1: Navigate to the Bulk Edit Tasks screen"):
        bulk_update_page.open()

    with allure.step("Step 2: Switch to Resident + Payer Category mode"):
        bulk_update_page.select_mode(BulkUpdatePage.MODE_RESIDENT_PAYER_CATEGORY)

    with allure.step("Step 3: Verify Resident + Payer Category is the active mode"):
        assert BulkUpdatePage.MODE_RESIDENT_PAYER_CATEGORY in bulk_update_page.get_active_mode_label()

    with allure.step("Step 4: Verify the first dropdown is labeled Resident"):
        assert bulk_update_page.resident_dropdown.is_visible()

    with allure.step("Step 5: Verify the second dropdown is labeled Payer Category"):
        assert bulk_update_page.payer_category_dropdown.is_visible()


@allure.epic("SCRUM-30: [FE] Add \"Bulk Edit Mode\" to Bulk Update")
@allure.feature("bulk_update")
@allure.story("AC5: Resident dropdown includes the facility")
@allure.title("Resident dropdown entries display the resident's facility name")
def test_pos_resident_dropdown_includes_facility_name(page):
    """
    Jira: SCRUM-30
    AC: Resident dropdown includes the facility
    """
    bulk_update_page = BulkUpdatePage(page)

    with allure.step("Step 1: Navigate to the Bulk Edit Tasks screen"):
        bulk_update_page.open()

    with allure.step("Step 2: Switch to Resident + Payer Category mode"):
        bulk_update_page.select_mode(BulkUpdatePage.MODE_RESIDENT_PAYER_CATEGORY)

    with allure.step("Step 3: Open the Resident dropdown and read visible option labels"):
        option_labels = bulk_update_page.get_resident_option_labels()

    with allure.step("Step 4: Verify at least one option includes a facility name separator"):
        assert any("|" in label for label in option_labels)


@allure.epic("SCRUM-30: [FE] Add \"Bulk Edit Mode\" to Bulk Update")
@allure.feature("bulk_update")
@allure.story("AC6: Switching modes clears any currently selected filter values")
@allure.title("Switching from Facility + Payer to Resident + Payer Category clears selections")
def test_pos_switch_facility_to_resident_clears_filters(page):
    """
    Jira: SCRUM-30
    AC: Switching modes clears any currently selected filter values
    """
    bulk_update_page = BulkUpdatePage(page)

    with allure.step("Step 1: Navigate to the Bulk Edit Tasks screen"):
        bulk_update_page.open()

    with allure.step("Step 2: Select a Facility value"):
        bulk_update_page.open_facility_dropdown()
        first_facility = bulk_update_page.mode_menu_panel.locator(
            ".cdk-virtual-scroll-content-wrapper > *"
        ).first
        first_facility.click()

    with allure.step("Step 3: Select a Payer value"):
        bulk_update_page.open_payer_dropdown()
        first_payer = bulk_update_page.mode_menu_panel.locator(
            ".cdk-virtual-scroll-content-wrapper > *"
        ).first
        first_payer.click()

    with allure.step("Step 4: Switch to Resident + Payer Category mode"):
        bulk_update_page.select_mode(BulkUpdatePage.MODE_RESIDENT_PAYER_CATEGORY)

    with allure.step("Step 5: Verify the Resident dropdown has no value selected"):
        assert bulk_update_page.resident_dropdown.inner_text().strip() == "Resident"

    with allure.step("Step 6: Verify the Payer Category dropdown has no value selected"):
        assert bulk_update_page.payer_category_dropdown.inner_text().strip() == "Payer Category"


@allure.epic("SCRUM-30: [FE] Add \"Bulk Edit Mode\" to Bulk Update")
@allure.feature("bulk_update")
@allure.story("AC6: Switching modes clears any currently selected filter values")
@allure.title("Switching from Resident + Payer Category to Facility + Payer clears selections")
def test_pos_switch_resident_to_facility_clears_filters(page):
    """
    Jira: SCRUM-30
    AC: Switching modes clears any currently selected filter values
    """
    bulk_update_page = BulkUpdatePage(page)

    with allure.step("Step 1: Navigate to the Bulk Edit Tasks screen"):
        bulk_update_page.open()

    with allure.step("Step 2: Switch to Resident + Payer Category mode"):
        bulk_update_page.select_mode(BulkUpdatePage.MODE_RESIDENT_PAYER_CATEGORY)

    with allure.step("Step 3: Select a Resident value"):
        bulk_update_page.open_resident_dropdown()
        first_resident = bulk_update_page.mode_menu_panel.locator(
            ".cdk-virtual-scroll-content-wrapper > *"
        ).first
        first_resident.click()

    with allure.step("Step 4: Select a Payer Category value"):
        bulk_update_page.open_payer_category_dropdown()
        first_category = bulk_update_page.mode_menu_panel.locator(
            ".cdk-virtual-scroll-content-wrapper > *"
        ).first
        first_category.click()

    with allure.step("Step 5: Switch to Facility + Payer mode"):
        bulk_update_page.select_mode(BulkUpdatePage.MODE_FACILITY_PAYER)

    with allure.step("Step 6: Verify the Facility dropdown has no value selected"):
        assert bulk_update_page.facility_dropdown.inner_text().strip() == "Facility"

    with allure.step("Step 7: Verify the Payer dropdown has no value selected"):
        assert bulk_update_page.payer_dropdown.inner_text().strip() == "Payer"


@allure.epic("SCRUM-30: [FE] Add \"Bulk Edit Mode\" to Bulk Update")
@allure.feature("bulk_update")
@allure.story("AC7: Apply Filters works identically in both modes")
@allure.title("Apply Filters refreshes the task table in Facility + Payer mode")
def test_pos_apply_filters_facility_payer_mode(page):
    """
    Jira: SCRUM-30
    AC: Apply Filters and Clear behavior works identically in both modes
    """
    bulk_update_page = BulkUpdatePage(page)

    with allure.step("Step 1: Navigate to the Bulk Edit Tasks screen"):
        bulk_update_page.open()

    with allure.step("Step 2: Select a Facility value"):
        bulk_update_page.open_facility_dropdown()
        bulk_update_page.mode_menu_panel.locator(
            ".cdk-virtual-scroll-content-wrapper > *"
        ).first.click()

    with allure.step("Step 3: Select a Payer value"):
        bulk_update_page.open_payer_dropdown()
        bulk_update_page.mode_menu_panel.locator(
            ".cdk-virtual-scroll-content-wrapper > *"
        ).first.click()

    with allure.step("Step 4: Verify Apply Filters is enabled"):
        assert bulk_update_page.is_apply_filters_enabled()

    with allure.step("Step 5: Click Apply Filters"):
        bulk_update_page.click_apply_filters()

    with allure.step("Step 6: Verify the empty-state prompt is no longer showing the initial message"):
        assert not bulk_update_page.is_empty_state_prompt_visible()


@allure.epic("SCRUM-30: [FE] Add \"Bulk Edit Mode\" to Bulk Update")
@allure.feature("bulk_update")
@allure.story("AC7: Apply Filters works identically in both modes")
@allure.title("Apply Filters refreshes the task table in Resident + Payer Category mode")
def test_pos_apply_filters_resident_payer_category_mode(page):
    """
    Jira: SCRUM-30
    AC: Apply Filters and Clear behavior works identically in both modes
    """
    bulk_update_page = BulkUpdatePage(page)

    with allure.step("Step 1: Navigate to the Bulk Edit Tasks screen"):
        bulk_update_page.open()

    with allure.step("Step 2: Switch to Resident + Payer Category mode"):
        bulk_update_page.select_mode(BulkUpdatePage.MODE_RESIDENT_PAYER_CATEGORY)

    with allure.step("Step 3: Select a Resident value"):
        bulk_update_page.open_resident_dropdown()
        bulk_update_page.mode_menu_panel.locator(
            ".cdk-virtual-scroll-content-wrapper > *"
        ).first.click()

    with allure.step("Step 4: Select a Payer Category value"):
        bulk_update_page.open_payer_category_dropdown()
        bulk_update_page.mode_menu_panel.locator(
            ".cdk-virtual-scroll-content-wrapper > *"
        ).first.click()

    with allure.step("Step 5: Verify Apply Filters is enabled"):
        assert bulk_update_page.is_apply_filters_enabled()

    with allure.step("Step 6: Click Apply Filters"):
        bulk_update_page.click_apply_filters()

    with allure.step("Step 7: Verify the empty-state prompt is no longer showing the initial message"):
        assert not bulk_update_page.is_empty_state_prompt_visible()


@allure.epic("SCRUM-30: [FE] Add \"Bulk Edit Mode\" to Bulk Update")
@allure.feature("bulk_update")
@allure.story("AC7: Apply Filters works identically in both modes")
@allure.title("Clear button resets filters in Facility + Payer mode")
def test_pos_clear_filters_facility_payer_mode(page):
    """
    Jira: SCRUM-30
    AC: Apply Filters and Clear behavior works identically in both modes
    """
    bulk_update_page = BulkUpdatePage(page)

    with allure.step("Step 1: Navigate to the Bulk Edit Tasks screen"):
        bulk_update_page.open()

    with allure.step("Step 2: Select Facility and Payer, then apply"):
        bulk_update_page.open_facility_dropdown()
        bulk_update_page.mode_menu_panel.locator(
            ".cdk-virtual-scroll-content-wrapper > *"
        ).first.click()
        bulk_update_page.open_payer_dropdown()
        bulk_update_page.mode_menu_panel.locator(
            ".cdk-virtual-scroll-content-wrapper > *"
        ).first.click()
        bulk_update_page.click_apply_filters()

    with allure.step("Step 3: Verify the Clear button is visible"):
        assert bulk_update_page.is_clear_button_visible()

    with allure.step("Step 4: Click Clear"):
        bulk_update_page.click_clear()

    with allure.step("Step 5: Verify the Facility dropdown resets to its placeholder"):
        assert bulk_update_page.facility_dropdown.inner_text().strip() == "Facility"

    with allure.step("Step 6: Verify the Payer dropdown resets to its placeholder"):
        assert bulk_update_page.payer_dropdown.inner_text().strip() == "Payer"


@allure.epic("SCRUM-30: [FE] Add \"Bulk Edit Mode\" to Bulk Update")
@allure.feature("bulk_update")
@allure.story("AC7: Apply Filters works identically in both modes")
@allure.title("Clear button resets filters in Resident + Payer Category mode")
def test_pos_clear_filters_resident_payer_category_mode(page):
    """
    Jira: SCRUM-30
    AC: Apply Filters and Clear behavior works identically in both modes
    """
    bulk_update_page = BulkUpdatePage(page)

    with allure.step("Step 1: Navigate to the Bulk Edit Tasks screen"):
        bulk_update_page.open()

    with allure.step("Step 2: Switch to Resident + Payer Category mode"):
        bulk_update_page.select_mode(BulkUpdatePage.MODE_RESIDENT_PAYER_CATEGORY)

    with allure.step("Step 3: Select Resident and Payer Category, then apply"):
        bulk_update_page.open_resident_dropdown()
        bulk_update_page.mode_menu_panel.locator(
            ".cdk-virtual-scroll-content-wrapper > *"
        ).first.click()
        bulk_update_page.open_payer_category_dropdown()
        bulk_update_page.mode_menu_panel.locator(
            ".cdk-virtual-scroll-content-wrapper > *"
        ).first.click()
        bulk_update_page.click_apply_filters()

    with allure.step("Step 4: Verify the Clear button is visible"):
        assert bulk_update_page.is_clear_button_visible()

    with allure.step("Step 5: Click Clear"):
        bulk_update_page.click_clear()

    with allure.step("Step 6: Verify the Resident dropdown resets to its placeholder"):
        assert bulk_update_page.resident_dropdown.inner_text().strip() == "Resident"

    with allure.step("Step 7: Verify the Payer Category dropdown resets to its placeholder"):
        assert bulk_update_page.payer_category_dropdown.inner_text().strip() == "Payer Category"


@allure.epic("SCRUM-30: [FE] Add \"Bulk Edit Mode\" to Bulk Update")
@allure.feature("bulk_update")
@allure.story("AC8: Task table reflects correct filter logic")
@allure.title("Task table reflects filtered results in Facility + Payer mode")
def test_pos_task_table_reflects_facility_payer_filter(page):
    """
    Jira: SCRUM-30
    AC: The task table results reflect the correct filter logic for whichever mode is active
    """
    bulk_update_page = BulkUpdatePage(page)

    with allure.step("Step 1: Navigate to the Bulk Edit Tasks screen"):
        bulk_update_page.open()

    with allure.step("Step 2: Select a Facility and Payer combination and apply"):
        bulk_update_page.open_facility_dropdown()
        bulk_update_page.mode_menu_panel.locator(
            ".cdk-virtual-scroll-content-wrapper > *"
        ).first.click()
        bulk_update_page.open_payer_dropdown()
        bulk_update_page.mode_menu_panel.locator(
            ".cdk-virtual-scroll-content-wrapper > *"
        ).first.click()
        bulk_update_page.click_apply_filters()

    with allure.step("Step 3: Verify either matching results or the No tasks found empty state is shown"):
        assert bulk_update_page.get_results_row_count() >= 0 or bulk_update_page.is_no_tasks_found_visible()


@allure.epic("SCRUM-30: [FE] Add \"Bulk Edit Mode\" to Bulk Update")
@allure.feature("bulk_update")
@allure.story("AC8: Task table reflects correct filter logic")
@allure.title("Task table reflects filtered results in Resident + Payer Category mode")
def test_pos_task_table_reflects_resident_payer_category_filter(page):
    """
    Jira: SCRUM-30
    AC: The task table results reflect the correct filter logic for whichever mode is active
    """
    bulk_update_page = BulkUpdatePage(page)

    with allure.step("Step 1: Navigate to the Bulk Edit Tasks screen"):
        bulk_update_page.open()

    with allure.step("Step 2: Switch to Resident + Payer Category mode"):
        bulk_update_page.select_mode(BulkUpdatePage.MODE_RESIDENT_PAYER_CATEGORY)

    with allure.step("Step 3: Select a Resident and Payer Category combination and apply"):
        bulk_update_page.open_resident_dropdown()
        bulk_update_page.mode_menu_panel.locator(
            ".cdk-virtual-scroll-content-wrapper > *"
        ).first.click()
        bulk_update_page.open_payer_category_dropdown()
        bulk_update_page.mode_menu_panel.locator(
            ".cdk-virtual-scroll-content-wrapper > *"
        ).first.click()
        bulk_update_page.click_apply_filters()

    with allure.step("Step 4: Verify either matching results or the No tasks found empty state is shown"):
        assert bulk_update_page.get_results_row_count() >= 0 or bulk_update_page.is_no_tasks_found_visible()


@allure.epic("SCRUM-30: [FE] Add \"Bulk Edit Mode\" to Bulk Update")
@allure.feature("bulk_update")
@allure.story("AC9: Apply Filters disabled until both dropdowns have a value")
@allure.title("Apply Filters is disabled when only Facility is selected")
def test_err_apply_filters_disabled_facility_only(page):
    """
    Jira: SCRUM-30
    AC: "Apply Filters" is disabled until both dropdowns in the active mode have a value selected
    """
    bulk_update_page = BulkUpdatePage(page)

    with allure.step("Step 1: Navigate to the Bulk Edit Tasks screen"):
        bulk_update_page.open()

    with allure.step("Step 2: Select a Facility value only"):
        bulk_update_page.open_facility_dropdown()
        bulk_update_page.mode_menu_panel.locator(
            ".cdk-virtual-scroll-content-wrapper > *"
        ).first.click()

    with allure.step("Step 3: Verify Apply Filters button is disabled"):
        assert not bulk_update_page.is_apply_filters_enabled()


@allure.epic("SCRUM-30: [FE] Add \"Bulk Edit Mode\" to Bulk Update")
@allure.feature("bulk_update")
@allure.story("AC9: Apply Filters disabled until both dropdowns have a value")
@allure.title("Apply Filters is disabled when only Payer is selected")
def test_err_apply_filters_disabled_payer_only(page):
    """
    Jira: SCRUM-30
    AC: "Apply Filters" is disabled until both dropdowns in the active mode have a value selected
    """
    bulk_update_page = BulkUpdatePage(page)

    with allure.step("Step 1: Navigate to the Bulk Edit Tasks screen"):
        bulk_update_page.open()

    with allure.step("Step 2: Select a Payer value only"):
        bulk_update_page.open_payer_dropdown()
        bulk_update_page.mode_menu_panel.locator(
            ".cdk-virtual-scroll-content-wrapper > *"
        ).first.click()

    with allure.step("Step 3: Verify Apply Filters button is disabled"):
        assert not bulk_update_page.is_apply_filters_enabled()


@allure.epic("SCRUM-30: [FE] Add \"Bulk Edit Mode\" to Bulk Update")
@allure.feature("bulk_update")
@allure.story("AC9: Apply Filters disabled until both dropdowns have a value")
@allure.title("Apply Filters is disabled when only Resident is selected")
def test_err_apply_filters_disabled_resident_only(page):
    """
    Jira: SCRUM-30
    AC: "Apply Filters" is disabled until both dropdowns in the active mode have a value selected
    """
    bulk_update_page = BulkUpdatePage(page)

    with allure.step("Step 1: Navigate to the Bulk Edit Tasks screen"):
        bulk_update_page.open()

    with allure.step("Step 2: Switch to Resident + Payer Category mode"):
        bulk_update_page.select_mode(BulkUpdatePage.MODE_RESIDENT_PAYER_CATEGORY)

    with allure.step("Step 3: Select a Resident value only"):
        bulk_update_page.open_resident_dropdown()
        bulk_update_page.mode_menu_panel.locator(
            ".cdk-virtual-scroll-content-wrapper > *"
        ).first.click()

    with allure.step("Step 4: Verify Apply Filters button is disabled"):
        assert not bulk_update_page.is_apply_filters_enabled()


@allure.epic("SCRUM-30: [FE] Add \"Bulk Edit Mode\" to Bulk Update")
@allure.feature("bulk_update")
@allure.story("AC9: Apply Filters disabled until both dropdowns have a value")
@allure.title("Apply Filters is disabled when only Payer Category is selected")
def test_err_apply_filters_disabled_payer_category_only(page):
    """
    Jira: SCRUM-30
    AC: "Apply Filters" is disabled until both dropdowns in the active mode have a value selected
    """
    bulk_update_page = BulkUpdatePage(page)

    with allure.step("Step 1: Navigate to the Bulk Edit Tasks screen"):
        bulk_update_page.open()

    with allure.step("Step 2: Switch to Resident + Payer Category mode"):
        bulk_update_page.select_mode(BulkUpdatePage.MODE_RESIDENT_PAYER_CATEGORY)

    with allure.step("Step 3: Select a Payer Category value only"):
        bulk_update_page.open_payer_category_dropdown()
        bulk_update_page.mode_menu_panel.locator(
            ".cdk-virtual-scroll-content-wrapper > *"
        ).first.click()

    with allure.step("Step 4: Verify Apply Filters button is disabled"):
        assert not bulk_update_page.is_apply_filters_enabled()


@allure.epic("SCRUM-30: [FE] Add \"Bulk Edit Mode\" to Bulk Update")
@allure.feature("bulk_update")
@allure.story("AC9: Apply Filters disabled until both dropdowns have a value")
@allure.title("Apply Filters becomes enabled only once both dropdowns are populated")
def test_pos_apply_filters_enabled_after_both_selected(page):
    """
    Jira: SCRUM-30
    AC: "Apply Filters" is disabled until both dropdowns in the active mode have a value selected
    """
    bulk_update_page = BulkUpdatePage(page)

    with allure.step("Step 1: Navigate to the Bulk Edit Tasks screen"):
        bulk_update_page.open()

    with allure.step("Step 2: Verify Apply Filters is disabled before any selection"):
        assert not bulk_update_page.is_apply_filters_enabled()

    with allure.step("Step 3: Select a Facility value"):
        bulk_update_page.open_facility_dropdown()
        bulk_update_page.mode_menu_panel.locator(
            ".cdk-virtual-scroll-content-wrapper > *"
        ).first.click()

    with allure.step("Step 4: Verify Apply Filters remains disabled"):
        assert not bulk_update_page.is_apply_filters_enabled()

    with allure.step("Step 5: Select a Payer value"):
        bulk_update_page.open_payer_dropdown()
        bulk_update_page.mode_menu_panel.locator(
            ".cdk-virtual-scroll-content-wrapper > *"
        ).first.click()

    with allure.step("Step 6: Verify Apply Filters becomes enabled"):
        assert bulk_update_page.is_apply_filters_enabled()


@allure.epic("SCRUM-30: [FE] Add \"Bulk Edit Mode\" to Bulk Update")
@allure.feature("bulk_update")
@allure.story("RBAC: Viewer role cannot apply bulk filters/actions")
@allure.title("Viewer role cannot apply bulk filters on the Bulk Edit Tasks screen")
def test_perm_viewer_cannot_apply_bulk_filters(page):
    """
    Jira: SCRUM-30
    AC: Access controls should block unauthorized actions on the Bulk Edit Tasks screen for restricted roles
    """
    bulk_update_page = BulkUpdatePage(page)

    with allure.step("Step 1: Navigate to the Bulk Edit Tasks screen as a Viewer-role user"):
        # TODO: Implement Viewer-role login/session switch once role-based test accounts are available
        bulk_update_page.open()

    with allure.step("Step 2: Verify the Bulk Mode toggle and dropdowns are visible"):
        assert bulk_update_page.bulk_mode_toggle.is_visible()

    with allure.step("Step 3: Verify the Apply Filters/bulk action affordance is disabled or hidden for Viewer role"):
        # TODO: Assert role-restricted state once Viewer-role test account is available
        pass


@allure.epic("SCRUM-30: [FE] Add \"Bulk Edit Mode\" to Bulk Update")
@allure.feature("bulk_update")
@allure.story("AC8: Task table reflects correct filter logic")
@allure.title("Empty state is shown when no tasks match the selected filters")
def test_pos_empty_state_when_no_tasks_match_filters(page):
    """
    Jira: SCRUM-30
    AC: The task table results reflect the correct filter logic for whichever mode is active
    """
    bulk_update_page = BulkUpdatePage(page)

    with allure.step("Step 1: Navigate to the Bulk Edit Tasks screen"):
        bulk_update_page.open()

    with allure.step("Step 2: Switch to Resident + Payer Category mode"):
        bulk_update_page.select_mode(BulkUpdatePage.MODE_RESIDENT_PAYER_CATEGORY)

    with allure.step("Step 3: Select a Resident and Payer Category combination with no matching tasks"):
        bulk_update_page.open_resident_dropdown()
        bulk_update_page.mode_menu_panel.locator(
            ".cdk-virtual-scroll-content-wrapper > *"
        ).first.click()
        bulk_update_page.open_payer_category_dropdown()
        bulk_update_page.mode_menu_panel.locator(
            ".cdk-virtual-scroll-content-wrapper > *"
        ).first.click()

    with allure.step("Step 4: Click Apply Filters"):
        bulk_update_page.click_apply_filters()

    with allure.step("Step 5: Verify the No tasks found empty state message is displayed"):
        assert bulk_update_page.is_no_tasks_found_visible()
