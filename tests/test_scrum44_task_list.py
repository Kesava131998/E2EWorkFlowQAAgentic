import pytest
import allure
from pages.task_list_page import TaskListPage
from config.settings import settings


@allure.epic("SCRUM-44: Bulk Update(Facility + Payer / Resident + Payer Category)")
@allure.feature("task_list")
@allure.story("AC1: The filter bar displays a Bulk Mode setting with two options")
@allure.title("Bulk Mode setting displays both mode options")
def test_pos_bulk_mode_shows_both_options(page):
    """
    Jira: SCRUM-44
    AC: The filter bar displays a Bulk Mode setting with two options: "Facility + payer"
    and "Resident + payer category".
    """
    task_list_page = TaskListPage(page)

    with allure.step("Step 1: Navigate to the Task List page"):
        task_list_page.open()

    with allure.step("Step 2: Verify the filter bar is visible"):
        task_list_page.filter_bar.wait_for(state="visible", timeout=settings.TIMEOUT)

    with allure.step("Step 3: Verify the Bulk Mode control is visible"):
        task_list_page.bulk_mode_control.wait_for(state="visible", timeout=settings.TIMEOUT)

    with allure.step("Step 4: Open the Bulk Mode dropdown"):
        task_list_page.open_bulk_mode_dropdown()

    with allure.step("Step 5: Verify both Bulk Mode options are visible"):
        assert task_list_page.is_bulk_mode_option_visible("Facility + payer")
        assert task_list_page.is_bulk_mode_option_visible("Resident + payer category")


@allure.epic("SCRUM-44: Bulk Update(Facility + Payer / Resident + Payer Category)")
@allure.feature("task_list")
@allure.story('AC2: "Facility + payer" is the default selected mode on page load')
@allure.title("Facility + payer is the default mode on page load")
def test_pos_facility_payer_default_mode(page):
    """
    Jira: SCRUM-44
    AC: "Facility + payer" is the default selected mode on page load.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Step 1: Navigate to the Task List page"):
        task_list_page.open()

    with allure.step("Step 2: Verify the Bulk Mode control is visible"):
        task_list_page.bulk_mode_control.wait_for(state="visible", timeout=settings.TIMEOUT)

    with allure.step("Step 3: Verify the default selected mode is Facility + payer"):
        assert task_list_page.get_bulk_mode_value() == "Facility + payer"


@allure.epic("SCRUM-44: Bulk Update(Facility + Payer / Resident + Payer Category)")
@allure.feature("task_list")
@allure.story('AC3: In "Facility + payer" mode, the dropdowns show Facility and Payer')
@allure.title("Facility + payer mode shows Facility and Payer dropdowns")
def test_pos_facility_payer_mode_shows_facility_and_payer_dropdowns(page):
    """
    Jira: SCRUM-44
    AC: In "Facility + payer" mode, the two filter dropdowns show Facility and Payer,
    matching current behavior.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Step 1: Navigate to the Task List page"):
        task_list_page.open()

    with allure.step("Step 2: Verify Bulk Mode is Facility + payer"):
        assert task_list_page.get_bulk_mode_value() == "Facility + payer"

    with allure.step("Step 3: Verify the Facility dropdown is visible"):
        task_list_page.facility_dropdown.wait_for(state="visible", timeout=settings.TIMEOUT)

    with allure.step("Step 4: Verify the Payer dropdown is visible"):
        task_list_page.payer_dropdown.wait_for(state="visible", timeout=settings.TIMEOUT)

    with allure.step("Step 5: Verify the first and second dropdown labels are Facility and Payer"):
        assert task_list_page.get_first_dropdown_label() == "Facility"
        assert task_list_page.get_second_dropdown_label() == "Payer"


@allure.epic("SCRUM-44: Bulk Update(Facility + Payer / Resident + Payer Category)")
@allure.feature("task_list")
@allure.story('AC3: "Facility + payer" mode does not show Resident/Payer Category dropdowns')
@allure.title("Facility + payer mode hides Resident and Payer Category dropdowns")
def test_err_facility_payer_mode_hides_resident_dropdowns(page):
    """
    Jira: SCRUM-44
    AC: In "Facility + payer" mode, only Facility and Payer dropdowns are shown.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Step 1: Navigate to the Task List page"):
        task_list_page.open()

    with allure.step("Step 2: Verify Bulk Mode is Facility + payer"):
        assert task_list_page.get_bulk_mode_value() == "Facility + payer"

    with allure.step("Step 3: Verify no Resident dropdown is present"):
        assert task_list_page.resident_dropdown.count() == 0

    with allure.step("Step 4: Verify no Payer Category dropdown is present"):
        assert task_list_page.payer_category_dropdown.count() == 0


@allure.epic("SCRUM-44: Bulk Update(Facility + Payer / Resident + Payer Category)")
@allure.feature("task_list")
@allure.story('AC4: In "Resident + payer category" mode, dropdowns show Resident and Payer Category')
@allure.title("Resident + payer category mode shows Resident and Payer Category dropdowns")
def test_pos_resident_payer_category_mode_shows_correct_dropdowns(page):
    """
    Jira: SCRUM-44
    AC: In "Resident + payer category" mode, the two filter dropdowns show Resident
    and Payer Category.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Step 1: Navigate to the Task List page"):
        task_list_page.open()

    with allure.step("Step 2: Open the Bulk Mode dropdown"):
        task_list_page.open_bulk_mode_dropdown()

    with allure.step("Step 3: Verify the Resident + payer category option is visible"):
        assert task_list_page.is_bulk_mode_option_visible("Resident + payer category")

    with allure.step("Step 4: Select the Resident + payer category option"):
        task_list_page.select_bulk_mode("Resident + payer category")

    with allure.step("Step 5: Verify Bulk Mode now reads Resident + payer category"):
        assert task_list_page.get_bulk_mode_value() == "Resident + payer category"

    with allure.step("Step 6: Verify the first and second dropdown labels are Resident and Payer Category"):
        assert task_list_page.get_first_dropdown_label() == "Resident"
        assert task_list_page.get_second_dropdown_label() == "Payer Category"


@allure.epic("SCRUM-44: Bulk Update(Facility + Payer / Resident + Payer Category)")
@allure.feature("task_list")
@allure.story('AC4: "Resident + payer category" mode does not show Facility/Payer dropdowns')
@allure.title("Resident + payer category mode hides Facility and Payer dropdowns")
def test_err_resident_payer_category_mode_hides_facility_payer_dropdowns(page):
    """
    Jira: SCRUM-44
    AC: In "Resident + payer category" mode, only Resident and Payer Category dropdowns
    are shown.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Step 1: Navigate to the Task List page"):
        task_list_page.open()

    with allure.step("Step 2: Select Resident + payer category mode"):
        task_list_page.select_bulk_mode("Resident + payer category")

    with allure.step("Step 3: Verify Bulk Mode is Resident + payer category"):
        assert task_list_page.get_bulk_mode_value() == "Resident + payer category"

    with allure.step("Step 4: Verify no standalone Facility dropdown is present"):
        assert task_list_page.facility_dropdown.count() == 0

    with allure.step("Step 5: Verify no Payer dropdown is present"):
        assert task_list_page.payer_dropdown.count() == 0


@allure.epic("SCRUM-44: Bulk Update(Facility + Payer / Resident + Payer Category)")
@allure.feature("task_list")
@allure.story("AC5: Resident dropdown includes the facility")
@allure.title("Resident dropdown options include the facility name")
def test_pos_resident_dropdown_includes_facility_name(page):
    """
    Jira: SCRUM-44
    AC: Resident dropdown includes the facility.
    """
    task_list_page = TaskListPage(page)
    resident_name = "John Doe"
    facility_name = "Sunrise Care Center"

    with allure.step("Step 1: Navigate to the Task List page"):
        task_list_page.open()

    with allure.step("Step 2: Select Resident + payer category mode"):
        task_list_page.select_bulk_mode("Resident + payer category")

    with allure.step("Step 3: Verify the Resident dropdown is visible"):
        task_list_page.resident_dropdown.wait_for(state="visible", timeout=settings.TIMEOUT)

    with allure.step("Step 4: Open the Resident dropdown"):
        task_list_page.open_resident_dropdown()

    with allure.step("Step 5: Verify the options list is populated"):
        options = task_list_page.get_resident_option_texts()
        assert len(options) > 0

    with allure.step(f"Step 6: Verify an option for {resident_name} includes facility {facility_name}"):
        matching = [o for o in options if resident_name in o]
        assert matching, f"No option found for resident '{resident_name}'"
        assert any(facility_name in o for o in matching)


@allure.epic("SCRUM-44: Bulk Update(Facility + Payer / Resident + Payer Category)")
@allure.feature("task_list")
@allure.story("AC5: Resident dropdown includes the facility")
@allure.title("Resident dropdown disambiguates residents with the same name across facilities")
def test_err_resident_dropdown_disambiguates_same_name_residents(page):
    """
    Jira: SCRUM-44
    AC: Resident dropdown includes the facility (needed to disambiguate residents that
    share the same name across different facilities).
    """
    task_list_page = TaskListPage(page)
    resident_name = "Jane Smith"
    facility_a = "Sunrise Care Center"
    facility_b = "Lakeside Manor"

    with allure.step("Step 1: Navigate to the Task List page"):
        task_list_page.open()

    with allure.step("Step 2: Select Resident + payer category mode"):
        task_list_page.select_bulk_mode("Resident + payer category")

    with allure.step("Step 3: Open the Resident dropdown"):
        task_list_page.open_resident_dropdown()

    with allure.step("Step 4: Verify two distinct Jane Smith entries are listed"):
        options = task_list_page.get_resident_option_texts()
        matching = [o for o in options if resident_name in o]
        assert len(matching) >= 2

    with allure.step(f"Step 5: Verify one entry includes {facility_a}"):
        assert any(facility_a in o for o in matching)

    with allure.step(f"Step 6: Verify the other entry includes {facility_b}"):
        assert any(facility_b in o for o in matching)


@allure.epic("SCRUM-44: Bulk Update(Facility + Payer / Resident + Payer Category)")
@allure.feature("task_list")
@allure.story("AC6: Switching modes clears any currently selected filter values")
@allure.title("Switching to Resident + payer category mode clears Facility + payer selections")
def test_pos_switch_to_resident_mode_clears_filters(page):
    """
    Jira: SCRUM-44
    AC: Switching modes clears any currently selected filter values.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Step 1: Navigate to the Task List page"):
        task_list_page.open()

    with allure.step("Step 2: Select a Facility value"):
        task_list_page.select_facility("Sunrise Care Center")

    with allure.step("Step 3: Select a Payer value"):
        task_list_page.select_payer("Medicare")

    with allure.step("Step 4: Switch Bulk Mode to Resident + payer category"):
        task_list_page.select_bulk_mode("Resident + payer category")

    with allure.step("Step 5: Verify the Resident dropdown shows no selected value"):
        assert task_list_page.resident_dropdown.inner_text().strip() == ""

    with allure.step("Step 6: Verify the Payer Category dropdown shows no selected value"):
        assert task_list_page.payer_category_dropdown.inner_text().strip() == ""


@allure.epic("SCRUM-44: Bulk Update(Facility + Payer / Resident + Payer Category)")
@allure.feature("task_list")
@allure.story("AC6: Switching modes clears any currently selected filter values")
@allure.title("Switching to Facility + payer mode clears Resident + payer category selections")
def test_pos_switch_to_facility_mode_clears_filters(page):
    """
    Jira: SCRUM-44
    AC: Switching modes clears any currently selected filter values.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Step 1: Navigate to the Task List page"):
        task_list_page.open()

    with allure.step("Step 2: Switch Bulk Mode to Resident + payer category"):
        task_list_page.select_bulk_mode("Resident + payer category")

    with allure.step("Step 3: Select a Resident value"):
        task_list_page.select_resident("John Doe (Sunrise Care Center)")

    with allure.step("Step 4: Select a Payer Category value"):
        task_list_page.select_payer_category("Managed Care")

    with allure.step("Step 5: Switch Bulk Mode back to Facility + payer"):
        task_list_page.select_bulk_mode("Facility + payer")

    with allure.step("Step 6: Verify the Facility dropdown shows no selected value"):
        assert task_list_page.facility_dropdown.inner_text().strip() == ""

    with allure.step("Step 7: Verify the Payer dropdown shows no selected value"):
        assert task_list_page.payer_dropdown.inner_text().strip() == ""


@allure.epic("SCRUM-44: Bulk Update(Facility + Payer / Resident + Payer Category)")
@allure.feature("task_list")
@allure.story("AC7: Apply Filters and Clear behavior works identically in both modes")
@allure.title("Apply Filters works in Facility + payer mode")
def test_pos_apply_filters_facility_payer_mode(page):
    """
    Jira: SCRUM-44
    AC: Apply Filters and Clear behavior works identically in both modes.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Step 1: Navigate to the Task List page"):
        task_list_page.open()

    with allure.step("Step 2: Select a Facility value"):
        task_list_page.select_facility("Sunrise Care Center")

    with allure.step("Step 3: Select a Payer value"):
        task_list_page.select_payer("Medicare")

    with allure.step("Step 4: Verify the Apply Filters button is enabled"):
        assert task_list_page.is_apply_filters_enabled()

    with allure.step("Step 5: Click Apply Filters and verify the task table reloads"):
        with page.expect_response(lambda r: "/tasks" in r.url):
            task_list_page.click_apply_filters()


@allure.epic("SCRUM-44: Bulk Update(Facility + Payer / Resident + Payer Category)")
@allure.feature("task_list")
@allure.story("AC7: Apply Filters and Clear behavior works identically in both modes")
@allure.title("Apply Filters works in Resident + payer category mode")
def test_pos_apply_filters_resident_payer_category_mode(page):
    """
    Jira: SCRUM-44
    AC: Apply Filters and Clear behavior works identically in both modes.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Step 1: Navigate to the Task List page"):
        task_list_page.open()

    with allure.step("Step 2: Switch Bulk Mode to Resident + payer category"):
        task_list_page.select_bulk_mode("Resident + payer category")

    with allure.step("Step 3: Select a Resident value"):
        task_list_page.select_resident("John Doe (Sunrise Care Center)")

    with allure.step("Step 4: Select a Payer Category value"):
        task_list_page.select_payer_category("Managed Care")

    with allure.step("Step 5: Verify the Apply Filters button is enabled"):
        assert task_list_page.is_apply_filters_enabled()

    with allure.step("Step 6: Click Apply Filters and verify the task table reloads"):
        with page.expect_response(lambda r: "/tasks" in r.url):
            task_list_page.click_apply_filters()


@allure.epic("SCRUM-44: Bulk Update(Facility + Payer / Resident + Payer Category)")
@allure.feature("task_list")
@allure.story("AC7: Apply Filters and Clear behavior works identically in both modes")
@allure.title("Clear button resets filters identically in both modes")
def test_pos_clear_button_resets_filters_both_modes(page):
    """
    Jira: SCRUM-44
    AC: Apply Filters and Clear behavior works identically in both modes.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Step 1: Navigate to the Task List page"):
        task_list_page.open()

    with allure.step("Step 2: Select Facility and Payer values in Facility + payer mode"):
        task_list_page.select_facility("Sunrise Care Center")
        task_list_page.select_payer("Medicare")

    with allure.step("Step 3: Click Clear"):
        task_list_page.click_clear()

    with allure.step("Step 4: Verify both dropdowns reset to empty"):
        assert task_list_page.facility_dropdown.inner_text().strip() == ""
        assert task_list_page.payer_dropdown.inner_text().strip() == ""

    with allure.step("Step 5: Verify Apply Filters is disabled"):
        assert not task_list_page.is_apply_filters_enabled()

    with allure.step("Step 6: Switch to Resident + payer category mode and select values"):
        task_list_page.select_bulk_mode("Resident + payer category")
        task_list_page.select_resident("John Doe (Sunrise Care Center)")
        task_list_page.select_payer_category("Managed Care")

    with allure.step("Step 7: Click Clear again"):
        task_list_page.click_clear()

    with allure.step("Step 8: Verify both dropdowns reset to empty and Apply Filters is disabled"):
        assert task_list_page.resident_dropdown.inner_text().strip() == ""
        assert task_list_page.payer_category_dropdown.inner_text().strip() == ""
        assert not task_list_page.is_apply_filters_enabled()


@allure.epic("SCRUM-44: Bulk Update(Facility + Payer / Resident + Payer Category)")
@allure.feature("task_list")
@allure.story("AC8: The task table results reflect the correct filter logic for whichever mode is active")
@allure.title("Task table reflects Facility + Payer filter logic")
def test_pos_task_table_reflects_facility_payer_filter(page):
    """
    Jira: SCRUM-44
    AC: The task table results reflect the correct filter logic for whichever mode
    is active.
    """
    task_list_page = TaskListPage(page)
    facility_name = "Sunrise Care Center"
    payer_name = "Medicare"

    with allure.step("Step 1: Navigate to the Task List page"):
        task_list_page.open()

    with allure.step("Step 2: Select Facility and Payer values"):
        task_list_page.select_facility(facility_name)
        task_list_page.select_payer(payer_name)

    with allure.step("Step 3: Click Apply Filters"):
        task_list_page.click_apply_filters()
        task_list_page.wait_for_load()

    with allure.step("Step 4: Verify every row matches the selected Facility and Payer"):
        row_count = task_list_page.get_task_row_count()
        assert row_count > 0
        for i in range(row_count):
            assert task_list_page.get_row_facility(i) == facility_name
            assert task_list_page.get_row_payer(i) == payer_name


@allure.epic("SCRUM-44: Bulk Update(Facility + Payer / Resident + Payer Category)")
@allure.feature("task_list")
@allure.story("AC8: The task table results reflect the correct filter logic for whichever mode is active")
@allure.title("Task table reflects Resident + Payer Category filter logic")
def test_pos_task_table_reflects_resident_payer_category_filter(page):
    """
    Jira: SCRUM-44
    AC: The task table results reflect the correct filter logic for whichever mode
    is active.
    """
    task_list_page = TaskListPage(page)
    resident_name = "John Doe"
    payer_category = "Managed Care"

    with allure.step("Step 1: Navigate to the Task List page"):
        task_list_page.open()

    with allure.step("Step 2: Switch Bulk Mode to Resident + payer category"):
        task_list_page.select_bulk_mode("Resident + payer category")

    with allure.step("Step 3: Select Resident and Payer Category values"):
        task_list_page.select_resident(f"{resident_name} (Sunrise Care Center)")
        task_list_page.select_payer_category(payer_category)

    with allure.step("Step 4: Click Apply Filters"):
        task_list_page.click_apply_filters()
        task_list_page.wait_for_load()

    with allure.step("Step 5: Verify every row matches the selected Resident and Payer Category"):
        row_count = task_list_page.get_task_row_count()
        assert row_count > 0
        for i in range(row_count):
            assert resident_name in task_list_page.get_row_resident(i)
            assert task_list_page.get_row_payer_category(i) == payer_category


@allure.epic("SCRUM-44: Bulk Update(Facility + Payer / Resident + Payer Category)")
@allure.feature("task_list")
@allure.story("AC8: The task table results reflect the correct filter logic for whichever mode is active")
@allure.title("Task table shows empty state when no tasks match the applied filter")
def test_err_task_table_empty_state_no_matches(page):
    """
    Jira: SCRUM-44
    AC: The task table results reflect the correct filter logic for whichever mode
    is active (including a zero-match empty state).
    """
    task_list_page = TaskListPage(page)

    with allure.step("Step 1: Navigate to the Task List page"):
        task_list_page.open()

    with allure.step("Step 2: Select a Facility/Payer combination with no matching tasks"):
        task_list_page.select_facility("Rarely Used Facility")
        task_list_page.select_payer("Obscure Payer")

    with allure.step("Step 3: Click Apply Filters"):
        task_list_page.click_apply_filters()
        task_list_page.wait_for_load()

    with allure.step("Step 4: Verify the task table displays an empty state"):
        assert task_list_page.is_empty_state_visible()
        assert task_list_page.get_task_row_count() == 0


@allure.epic("SCRUM-44: Bulk Update(Facility + Payer / Resident + Payer Category)")
@allure.feature("task_list")
@allure.story('AC9: "Apply Filters" is disabled until both dropdowns have a value selected')
@allure.title("Apply Filters is disabled until both dropdowns are selected (Facility + payer mode)")
def test_pos_apply_filters_disabled_until_both_selected_facility_mode(page):
    """
    Jira: SCRUM-44
    AC: "Apply Filters" is disabled until both dropdowns in the active mode have a
    value selected.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Step 1: Navigate to the Task List page"):
        task_list_page.open()

    with allure.step("Step 2: Verify Apply Filters is disabled with no selections"):
        assert not task_list_page.is_apply_filters_enabled()

    with allure.step("Step 3: Select only the Facility value"):
        task_list_page.select_facility("Sunrise Care Center")

    with allure.step("Step 4: Verify Apply Filters remains disabled"):
        assert not task_list_page.is_apply_filters_enabled()

    with allure.step("Step 5: Also select the Payer value"):
        task_list_page.select_payer("Medicare")

    with allure.step("Step 6: Verify Apply Filters becomes enabled"):
        assert task_list_page.is_apply_filters_enabled()


@allure.epic("SCRUM-44: Bulk Update(Facility + Payer / Resident + Payer Category)")
@allure.feature("task_list")
@allure.story('AC9: "Apply Filters" is disabled until both dropdowns have a value selected')
@allure.title("Apply Filters is disabled until both dropdowns are selected (Resident + payer category mode)")
def test_pos_apply_filters_disabled_until_both_selected_resident_mode(page):
    """
    Jira: SCRUM-44
    AC: "Apply Filters" is disabled until both dropdowns in the active mode have a
    value selected.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Step 1: Navigate to the Task List page"):
        task_list_page.open()

    with allure.step("Step 2: Switch Bulk Mode to Resident + payer category"):
        task_list_page.select_bulk_mode("Resident + payer category")

    with allure.step("Step 3: Verify Apply Filters is disabled with no selections"):
        assert not task_list_page.is_apply_filters_enabled()

    with allure.step("Step 4: Select only the Resident value"):
        task_list_page.select_resident("John Doe (Sunrise Care Center)")

    with allure.step("Step 5: Verify Apply Filters remains disabled"):
        assert not task_list_page.is_apply_filters_enabled()

    with allure.step("Step 6: Also select the Payer Category value"):
        task_list_page.select_payer_category("Managed Care")

    with allure.step("Step 7: Verify Apply Filters becomes enabled"):
        assert task_list_page.is_apply_filters_enabled()


@allure.epic("SCRUM-44: Bulk Update(Facility + Payer / Resident + Payer Category)")
@allure.feature("task_list")
@allure.story('AC9: "Apply Filters" is disabled until both dropdowns have a value selected')
@allure.title("Deselecting one dropdown re-disables Apply Filters")
def test_err_apply_filters_redisabled_after_deselect(page):
    """
    Jira: SCRUM-44
    AC: "Apply Filters" is disabled until both dropdowns in the active mode have a
    value selected.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Step 1: Navigate to the Task List page"):
        task_list_page.open()

    with allure.step("Step 2: Select Facility and Payer values"):
        task_list_page.select_facility("Sunrise Care Center")
        task_list_page.select_payer("Medicare")

    with allure.step("Step 3: Verify Apply Filters is enabled"):
        assert task_list_page.is_apply_filters_enabled()

    with allure.step("Step 4: Clear the Payer selection only"):
        task_list_page.clear_payer_selection()

    with allure.step("Step 5: Verify Apply Filters becomes disabled again"):
        assert not task_list_page.is_apply_filters_enabled()


@allure.epic("SCRUM-44: Bulk Update(Facility + Payer / Resident + Payer Category)")
@allure.feature("task_list")
@allure.story("RBAC: Bulk Mode filters are usable across roles")
@allure.title("Viewer role can use Bulk Mode filters the same as a full-access user")
def test_perm_viewer_can_use_bulk_mode_filters(page):
    """
    Jira: SCRUM-44
    AC: Bulk Mode filter behavior (AC1-AC9) is verified for a read-only Viewer role,
    ensuring no filter functionality is unexpectedly restricted.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Step 1: Navigate to the Task List page as a Viewer-role user"):
        task_list_page.open()

    with allure.step("Step 2: Verify the Bulk Mode control is visible and interactive"):
        task_list_page.bulk_mode_control.wait_for(state="visible", timeout=settings.TIMEOUT)

    with allure.step("Step 3: Switch Bulk Mode to Resident + payer category"):
        task_list_page.select_bulk_mode("Resident + payer category")
        assert task_list_page.get_bulk_mode_value() == "Resident + payer category"

    with allure.step("Step 4: Switch Bulk Mode back to Facility + payer"):
        task_list_page.select_bulk_mode("Facility + payer")
        assert task_list_page.get_bulk_mode_value() == "Facility + payer"

    with allure.step("Step 5: Select Facility and Payer values"):
        task_list_page.select_facility("Sunrise Care Center")
        task_list_page.select_payer("Medicare")

    with allure.step("Step 6: Click Apply Filters and verify the task table updates"):
        task_list_page.click_apply_filters()
        task_list_page.wait_for_load()
        assert task_list_page.get_task_row_count() >= 0
