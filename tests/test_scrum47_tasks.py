import allure
from pages.task_list_page import TaskListPage
from config.settings import settings

# TODO: replace with real facility/resident/payer/staff fixtures once test data is confirmed for this environment
FACILITY_A = "TODO-Facility-A"
FACILITY_B = "TODO-Facility-B"
FACILITY_C = "TODO-Facility-C"
RESIDENT_X_FACILITY_A = "TODO-Resident-X"
RESIDENT_Y_FACILITY_B_ONLY = "TODO-Resident-Y"
PAYER_P_FACILITY_A = "TODO-Payer-P"
PAYER_Q_MULTI_FACILITY = "TODO-Payer-Q"
STAFF_M_FACILITY_A = "TODO-Staff-M"
STAFF_N_FACILITY_B = "TODO-Staff-N"
SEARCH_TEXT = "INV-1001"


@allure.epic("SCRUM-47: Preserve Task List and Aging Filter Selections when Global Facility Filter Changes")
@allure.feature("tasks")
@allure.story("AC1: Changing the global facility filter refreshes available filter values")
@allure.title("Refresh filter options on facility change")
def test_pos_refresh_filter_options_on_facility_change(page):
    """
    Jira: SCRUM-47
    AC: Changing the global facility filter refreshes available values for Resident,
    Facility, Payer, and Assigned To filters.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Navigate to the Task List with global facility filter set to Facility A"):
        task_list_page.navigate_to(task_list_page.url)
        task_list_page.wait_for_load()

    with allure.step("Add Facility B to the global facility filter and apply"):
        task_list_page.open_global_facility_filter()
        task_list_page.select_global_facility(FACILITY_B)
        task_list_page.apply_global_facility_filter()

    with allure.step("Verify Resident filter options now include values from both facilities"):
        task_list_page.open_filter("resident")
        options = task_list_page.get_filter_option_texts("resident")
        assert options, "Resident filter option list did not refresh"


@allure.epic("SCRUM-47: Preserve Task List and Aging Filter Selections when Global Facility Filter Changes")
@allure.feature("tasks")
@allure.story("AC1: Payer and Assigned To filters refresh alongside Resident/Facility")
@allure.title("Refresh Payer and Assigned To filters")
def test_pos_refresh_payer_assigned_to_filters(page):
    """
    Jira: SCRUM-47
    AC: Changing the global facility filter refreshes available values for Payer and
    Assigned To filters.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Navigate to the Task List with global facility filter set to Facility A"):
        task_list_page.navigate_to(task_list_page.url)
        task_list_page.wait_for_load()

    with allure.step("Add Facility B to the global facility filter and apply"):
        task_list_page.open_global_facility_filter()
        task_list_page.select_global_facility(FACILITY_B)
        task_list_page.apply_global_facility_filter()

    with allure.step("Verify Payer and Assigned To filter options refreshed"):
        task_list_page.open_filter("payer")
        payer_options = task_list_page.get_filter_option_texts("payer")
        task_list_page.open_filter("assigned_to")
        assigned_to_options = task_list_page.get_filter_option_texts("assigned_to")
        assert payer_options, "Payer filter option list did not refresh"
        assert assigned_to_options, "Assigned To filter option list did not refresh"


@allure.epic("SCRUM-47: Preserve Task List and Aging Filter Selections when Global Facility Filter Changes")
@allure.feature("tasks")
@allure.story("AC2: Selected values remain selected when still matching a remaining global facility")
@allure.title("Preserve Resident filter when facility still matches")
def test_pos_preserve_resident_filter_when_facility_still_matches(page):
    """
    Jira: SCRUM-47
    AC: Existing selected values remain selected when they still match at least one
    selected global facility.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Navigate with global facility filter set to Facility A + Facility B and Resident X selected"):
        task_list_page.navigate_to(task_list_page.url)
        task_list_page.wait_for_load()
        task_list_page.open_filter("resident")
        assert RESIDENT_X_FACILITY_A in task_list_page.get_filter_selected_texts("resident")

    with allure.step("Remove Facility B from the global facility filter"):
        task_list_page.open_global_facility_filter()
        task_list_page.deselect_global_facility(FACILITY_B)
        task_list_page.apply_global_facility_filter()

    with allure.step("Verify Resident X remains selected"):
        task_list_page.open_filter("resident")
        assert RESIDENT_X_FACILITY_A in task_list_page.get_filter_selected_texts("resident"), \
            "Resident selection was incorrectly cleared"


@allure.epic("SCRUM-47: Preserve Task List and Aging Filter Selections when Global Facility Filter Changes")
@allure.feature("tasks")
@allure.story("AC3: Selected values are removed when no longer matching any remaining global facility")
@allure.title("Remove Resident filter when facility no longer matches")
def test_pos_remove_resident_filter_when_facility_no_longer_matches(page):
    """
    Jira: SCRUM-47
    AC: Existing selected values are removed when they no longer match any selected
    global facility.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Navigate with global facility filter set to Facility A + Facility B and Resident Y selected"):
        task_list_page.navigate_to(task_list_page.url)
        task_list_page.wait_for_load()
        task_list_page.open_filter("resident")
        assert RESIDENT_Y_FACILITY_B_ONLY in task_list_page.get_filter_selected_texts("resident")

    with allure.step("Remove Facility B from the global facility filter"):
        task_list_page.open_global_facility_filter()
        task_list_page.deselect_global_facility(FACILITY_B)
        task_list_page.apply_global_facility_filter()

    with allure.step("Verify Resident Y is no longer selected"):
        task_list_page.open_filter("resident")
        assert RESIDENT_Y_FACILITY_B_ONLY not in task_list_page.get_filter_selected_texts("resident"), \
            "Resident selection should have been invalidated"


@allure.epic("SCRUM-47: Preserve Task List and Aging Filter Selections when Global Facility Filter Changes")
@allure.feature("tasks")
@allure.story("AC4: Adding facilities to the global filter does not clear existing valid selections")
@allure.title("Retain filters when facility added")
def test_pos_retain_filters_when_facility_added(page):
    """
    Jira: SCRUM-47
    AC: Adding facilities to the global filter does not clear existing valid Task List
    filter selections.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Navigate with global facility filter set to Facility A, Resident X and Payer P selected"):
        task_list_page.navigate_to(task_list_page.url)
        task_list_page.wait_for_load()

    with allure.step("Add Facility B to the global facility filter"):
        task_list_page.open_global_facility_filter()
        task_list_page.select_global_facility(FACILITY_B)
        task_list_page.apply_global_facility_filter()

    with allure.step("Verify Resident X and Payer P remain selected"):
        task_list_page.open_filter("resident")
        assert RESIDENT_X_FACILITY_A in task_list_page.get_filter_selected_texts("resident")
        task_list_page.open_filter("payer")
        assert PAYER_P_FACILITY_A in task_list_page.get_filter_selected_texts("payer")


@allure.epic("SCRUM-47: Preserve Task List and Aging Filter Selections when Global Facility Filter Changes")
@allure.feature("tasks")
@allure.story("AC5: Removing facilities only removes selections that are no longer valid")
@allure.title("Retain valid filters when facility removed")
def test_pos_retain_valid_filters_when_facility_removed(page):
    """
    Jira: SCRUM-47
    AC: Removing facilities from the global filter only removes Task List filter
    selections that are no longer valid.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Navigate with global facility filter set to Facility A + Facility B, Staff M and Staff N assigned"):
        task_list_page.navigate_to(task_list_page.url)
        task_list_page.wait_for_load()
        task_list_page.open_filter("assigned_to")
        selected = task_list_page.get_filter_selected_texts("assigned_to")
        assert STAFF_M_FACILITY_A in selected and STAFF_N_FACILITY_B in selected

    with allure.step("Remove Facility B from the global facility filter"):
        task_list_page.open_global_facility_filter()
        task_list_page.deselect_global_facility(FACILITY_B)
        task_list_page.apply_global_facility_filter()

    with allure.step("Verify Staff M remains selected and Staff N is removed"):
        task_list_page.open_filter("assigned_to")
        selected = task_list_page.get_filter_selected_texts("assigned_to")
        assert STAFF_M_FACILITY_A in selected, "Valid selection was incorrectly removed"
        assert STAFF_N_FACILITY_B not in selected, "Invalid selection was not removed"


@allure.epic("SCRUM-47: Preserve Task List and Aging Filter Selections when Global Facility Filter Changes")
@allure.feature("tasks")
@allure.story("AC6: The Task List reloads using the preserved valid filters")
@allure.title("Task List reloads with preserved filters")
def test_pos_task_list_reloads_with_preserved_filters(page):
    """
    Jira: SCRUM-47
    AC: The Task List reloads using the preserved valid filters after the global
    facility filter changes.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Navigate with global facility filter set to Facility A + Facility B and Resident X selected"):
        task_list_page.navigate_to(task_list_page.url)
        task_list_page.wait_for_load()
        assert task_list_page.get_grid_row_count() > 0

    with allure.step("Remove Facility B from the global facility filter and apply"):
        task_list_page.open_global_facility_filter()
        task_list_page.deselect_global_facility(FACILITY_B)
        task_list_page.apply_global_facility_filter()

    with allure.step("Verify the Task List grid reloaded and still shows Resident X rows"):
        task_list_page.wait_for_load()
        assert task_list_page.is_grid_visible(), "Task List grid did not reload"
        assert task_list_page.get_grid_row_count() > 0, "Task List grid is empty after reload"


@allure.epic("SCRUM-47: Preserve Task List and Aging Filter Selections when Global Facility Filter Changes")
@allure.feature("tasks")
@allure.story("AC7: A filter is cleared entirely when every selected value is invalidated")
@allure.title("Clear filter when all values invalidated")
def test_pos_clear_filter_when_all_values_invalidated(page):
    """
    Jira: SCRUM-47
    AC: If every selected value in a filter is invalidated by the global facility
    filter change, the filter is cleared.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Navigate with global facility filter set to Facility A + Facility B, only Resident Y selected"):
        task_list_page.navigate_to(task_list_page.url)
        task_list_page.wait_for_load()
        task_list_page.open_filter("resident")
        assert task_list_page.get_filter_selected_texts("resident") == [RESIDENT_Y_FACILITY_B_ONLY]

    with allure.step("Remove Facility B from the global facility filter"):
        task_list_page.open_global_facility_filter()
        task_list_page.deselect_global_facility(FACILITY_B)
        task_list_page.apply_global_facility_filter()

    with allure.step("Verify the Resident filter is fully cleared"):
        task_list_page.open_filter("resident")
        assert task_list_page.is_filter_cleared("resident"), "Resident filter was not cleared"


@allure.epic("SCRUM-47: Preserve Task List and Aging Filter Selections when Global Facility Filter Changes")
@allure.feature("tasks")
@allure.story("AC3, AC7: All filters are cleared when switched to a disjoint facility set")
@allure.title("Clear all filters on disjoint facility change")
def test_err_clear_all_filters_on_disjoint_facility_change(page):
    """
    Jira: SCRUM-47
    AC: Existing selected values are removed when they no longer match any selected
    global facility; a filter is cleared entirely once all its values are invalidated.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Navigate with global facility filter set to Facility A and all filters populated"):
        task_list_page.navigate_to(task_list_page.url)
        task_list_page.wait_for_load()

    with allure.step("Switch the global facility filter to the disjoint Facility C"):
        task_list_page.open_global_facility_filter()
        task_list_page.deselect_global_facility(FACILITY_A)
        task_list_page.select_global_facility(FACILITY_C)
        task_list_page.apply_global_facility_filter()

    with allure.step("Verify Resident, Facility, Payer, and Assigned To filters are all cleared"):
        for filter_name in ("resident", "facility", "payer", "assigned_to"):
            task_list_page.open_filter(filter_name)
            assert task_list_page.is_filter_cleared(filter_name), f"{filter_name} filter was not cleared"


@allure.epic("SCRUM-47: Preserve Task List and Aging Filter Selections when Global Facility Filter Changes")
@allure.feature("tasks")
@allure.story("AC2: A value matching multiple remaining facilities is preserved")
@allure.title("Preserve filter matching multiple facilities")
def test_pos_preserve_filter_matching_multiple_facilities(page):
    """
    Jira: SCRUM-47
    AC: Existing selected values remain selected when they still match at least one
    selected global facility.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Navigate with global facility filter set to Facility A + B + C and Payer Q selected"):
        task_list_page.navigate_to(task_list_page.url)
        task_list_page.wait_for_load()
        task_list_page.open_filter("payer")
        assert PAYER_Q_MULTI_FACILITY in task_list_page.get_filter_selected_texts("payer")

    with allure.step("Remove only Facility C from the global facility filter"):
        task_list_page.open_global_facility_filter()
        task_list_page.deselect_global_facility(FACILITY_C)
        task_list_page.apply_global_facility_filter()

    with allure.step("Verify Payer Q remains selected"):
        task_list_page.open_filter("payer")
        assert PAYER_Q_MULTI_FACILITY in task_list_page.get_filter_selected_texts("payer"), \
            "Payer selection was incorrectly cleared while still matching a remaining facility"


@allure.epic("SCRUM-47: Preserve Task List and Aging Filter Selections when Global Facility Filter Changes")
@allure.feature("tasks")
@allure.story("AC5: Removing all facilities clears all Task List filter selections")
@allure.title("Clear all filters when no facility selected")
def test_err_clear_all_filters_when_no_facility_selected(page):
    """
    Jira: SCRUM-47
    AC: Removing facilities from the global filter only removes Task List filter
    selections that are no longer valid — with zero facilities selected, nothing
    remains valid.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Navigate with global facility filter set to Facility A, Resident and Payer filters populated"):
        task_list_page.navigate_to(task_list_page.url)
        task_list_page.wait_for_load()

    with allure.step("Remove Facility A from the global facility filter, leaving zero facilities selected"):
        task_list_page.open_global_facility_filter()
        task_list_page.deselect_global_facility(FACILITY_A)
        task_list_page.apply_global_facility_filter()

    with allure.step("Verify Resident and Payer filters are cleared"):
        task_list_page.open_filter("resident")
        assert task_list_page.is_filter_cleared("resident")
        task_list_page.open_filter("payer")
        assert task_list_page.is_filter_cleared("payer")


@allure.epic("SCRUM-47: Preserve Task List and Aging Filter Selections when Global Facility Filter Changes")
@allure.feature("tasks")
@allure.story("AC1, AC6: A global facility change with an active search does not error")
@allure.title("Facility change with active search causes no error")
def test_pos_facility_change_with_active_search_no_error(page):
    """
    Jira: SCRUM-47
    AC: The Task List reloads using the preserved valid filters, and continues to
    apply any active row-level search, after the global facility filter changes.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Navigate and apply a free-text search on the Task List"):
        task_list_page.navigate_to(task_list_page.url)
        task_list_page.wait_for_load()
        task_list_page.search(SEARCH_TEXT)

    with allure.step("Add Facility B to the global facility filter and apply"):
        task_list_page.open_global_facility_filter()
        task_list_page.select_global_facility(FACILITY_B)
        task_list_page.apply_global_facility_filter()

    with allure.step("Verify the grid reloaded without an unhandled error state"):
        assert not task_list_page.is_error_state_visible(), "Task List grid surfaced an unexpected error"
        assert task_list_page.is_grid_visible()


@allure.epic("SCRUM-47: Preserve Task List and Aging Filter Selections when Global Facility Filter Changes")
@allure.feature("tasks")
@allure.story("AC1: Filter dropdowns do not show stale options during refresh")
@allure.title("No stale filter options during refresh")
def test_err_no_stale_filter_options_during_refresh(page):
    """
    Jira: SCRUM-47
    AC: Changing the global facility filter refreshes available values for the
    Resident filter without leaving stale, pre-change options behind.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Navigate and capture the Resident filter options before the change"):
        task_list_page.navigate_to(task_list_page.url)
        task_list_page.wait_for_load()
        task_list_page.open_filter("resident")
        options_before = set(task_list_page.get_filter_option_texts("resident"))

    with allure.step("Add Facility B to the global facility filter and apply"):
        task_list_page.open_global_facility_filter()
        task_list_page.select_global_facility(FACILITY_B)
        task_list_page.apply_global_facility_filter()

    with allure.step("Verify the Resident filter options refreshed and are not merely appended stale entries"):
        task_list_page.open_filter("resident")
        options_after = set(task_list_page.get_filter_option_texts("resident"))
        assert options_after != options_before, "Resident filter options did not refresh"
        assert len(options_after) == len(set(options_after)), "Resident filter options contain duplicates"


@allure.epic("SCRUM-47: Preserve Task List and Aging Filter Selections when Global Facility Filter Changes")
@allure.feature("tasks")
@allure.story("AC6: Task List surfaces an error state if the reload request fails")
@allure.title("Task List shows error state on reload failure")
def test_err_task_list_shows_error_on_reload_failure(page):
    """
    Jira: SCRUM-47
    AC: The Task List reloads using the preserved valid filters after the global
    facility filter changes; if that reload fails, the grid must surface a clear
    error state rather than a blank or stale grid.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Navigate to the Task List"):
        task_list_page.navigate_to(task_list_page.url)
        task_list_page.wait_for_load()

    with allure.step("Simulate a failed reload response and change the global facility filter"):
        page.route(
            "**/api/tasks**",
            lambda route: route.fulfill(status=500, body='{"error": "Internal Server Error"}'),
        )
        task_list_page.open_global_facility_filter()
        task_list_page.select_global_facility(FACILITY_B)
        task_list_page.apply_global_facility_filter()

    with allure.step("Verify the Task List grid surfaces an error state"):
        assert task_list_page.is_error_state_visible(), "Task List grid did not surface an error state on failure"


@allure.epic("SCRUM-47: Preserve Task List and Aging Filter Selections when Global Facility Filter Changes")
@allure.feature("tasks")
@allure.story("AC2, AC4: A facility-restricted role only sees permitted facilities, valid selections persist")
@allure.title("Facility-restricted role sees only permitted facilities")
def test_perm_facility_restricted_role_sees_permitted_facilities_only(page):
    """
    Jira: SCRUM-47
    AC: Existing selected values remain selected when they still match at least one
    selected global facility; adding/removing facilities the user cannot access must
    not be possible for a facility-restricted role.
    """
    task_list_page = TaskListPage(page)

    with allure.step("Navigate as a facility-restricted user scoped to Facility A only"):
        task_list_page.navigate_to(task_list_page.url)
        task_list_page.wait_for_load()

    with allure.step("Verify the global facility filter only lists the permitted facility"):
        task_list_page.open_global_facility_filter()
        options = task_list_page.global_facility_filter_options.all_inner_texts()
        assert options == [FACILITY_A], \
            "Global facility filter exposed a facility outside the user's permitted scope"

    with allure.step("Verify Resident X remains selected after re-applying the permitted facility"):
        task_list_page.apply_global_facility_filter()
        task_list_page.open_filter("resident")
        assert RESIDENT_X_FACILITY_A in task_list_page.get_filter_selected_texts("resident")
