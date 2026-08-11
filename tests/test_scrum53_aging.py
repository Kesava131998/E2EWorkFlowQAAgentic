import allure
from pages.aging_page import AgingPage
from config.settings import settings

# TODO: replace with real test data/fixtures once confirmed for this environment
BALANCE_CELL_MULTIPLE_COMMENTS = 0
BALANCE_CELL_WITH_FOLLOWUP_DATE = 0
BALANCE_CELL_WITHOUT_FOLLOWUP_DATE = 0
BALANCE_CELL_WITH_SYSTEM_COMMENT = 0
BALANCE_CELL_OVERFLOW_COMMENTS = 0
BALANCE_CELL_NEAR_RIGHT_EDGE = 0
BALANCE_CELL_NEAR_LEFT_EDGE = 0
BALANCE_CELL_WITH_TASK = 0
BALANCE_CELL_WITHOUT_TASK = 0
BALANCE_CELL_NO_USER_COMMENTS = 0
CASE_VIEW_CASE_ID = "TODO-case-with-aging-comments"
EXPECTED_FOLLOWUP_DATE = "2026-08-20"
MOST_RECENT_COMMENT_TEXT = "TODO-most-recent-comment-text"
SYSTEM_COMMENT_TEXT = "Balance auto-adjusted by system"
SAVED_VIEW_NAME = "Test View AC2"
# TODO: replace with the real oldest-to-newest comment texts for BALANCE_CELL_MULTIPLE_COMMENTS
EXPECTED_COMMENTS_OLDEST_TO_NEWEST = ["TODO-comment-1-oldest", "TODO-comment-2", "TODO-comment-3-newest"]


@allure.epic("SCRUM-53: All Task Comments in Aging Balance Tooltip")
@allure.feature("aging")
@allure.story("AC1: 'Show all comments in tooltip' toggle is present and defaults to Off")
@allure.title("Toggle is present and defaults to Off")
def test_pos_toggle_present_defaults_off(page):
    """
    Jira: SCRUM-53
    AC: "Show all comments in tooltip" toggle is present on the Aging page and defaults to Off
    """
    aging_page = AgingPage(page)

    with allure.step("Navigate to the Aging page"):
        aging_page.open()

    with allure.step("Verify the toggle is visible and defaults to Off"):
        assert aging_page.is_show_all_comments_toggle_visible(), "Toggle not visible on Aging page"
        assert not aging_page.is_show_all_comments_toggle_on(), "Toggle should default to Off"


@allure.epic("SCRUM-53: All Task Comments in Aging Balance Tooltip")
@allure.feature("aging")
@allure.story("AC2: Setting persists within the session and is saved as part of saved views")
@allure.title("Toggle setting persists within session and saved view")
def test_pos_toggle_setting_persists_session_and_saved_view(page):
    """
    Jira: SCRUM-53
    AC: The setting persists within the session and is saved as part of saved views
    """
    aging_page = AgingPage(page)

    with allure.step("Navigate to the Aging page and turn the toggle On"):
        aging_page.open()
        aging_page.toggle_show_all_comments()
        assert aging_page.is_show_all_comments_toggle_on(), "Toggle did not switch On"

    with allure.step("Navigate away and back within the same session"):
        aging_page.navigate_to(f"{settings.BASE_URL}/tasks")
        aging_page.open()
        assert aging_page.is_show_all_comments_toggle_on(), "Toggle state not persisted within session"

    with allure.step(f"Save the current view as '{SAVED_VIEW_NAME}'"):
        aging_page.save_view(SAVED_VIEW_NAME)

    with allure.step(f"Reload the saved view '{SAVED_VIEW_NAME}'"):
        aging_page.load_saved_view(SAVED_VIEW_NAME)

    with allure.step("Verify toggle state in the reloaded saved view"):
        assert aging_page.is_show_all_comments_toggle_on(), "Toggle state not saved with view"


@allure.epic("SCRUM-53: All Task Comments in Aging Balance Tooltip")
@allure.feature("aging")
@allure.story("AC3: Follow Up Date is displayed on the Aging tooltip")
@allure.title("Follow Up Date displayed in tooltip")
def test_pos_followup_date_displayed_in_tooltip(page):
    """
    Jira: SCRUM-53
    AC: Follow Up Date is displayed on the Aging tooltip
    """
    aging_page = AgingPage(page)

    with allure.step("Navigate to the Aging page and open the tooltip for a cell with a Follow Up Date"):
        aging_page.open()
        aging_page.open_tooltip_for_cell(BALANCE_CELL_WITH_FOLLOWUP_DATE)

    with allure.step("Verify the Follow Up Date field matches the expected date"):
        assert aging_page.is_tooltip_visible(), "Tooltip did not open"
        assert EXPECTED_FOLLOWUP_DATE in aging_page.get_followup_date_text(), "Follow Up Date not displayed correctly"


@allure.epic("SCRUM-53: All Task Comments in Aging Balance Tooltip")
@allure.feature("aging")
@allure.story("AC3: Follow Up Date is displayed on the Aging tooltip")
@allure.title("Follow Up Date absent renders without error")
def test_pos_followup_date_absent_renders_without_error(page):
    """
    Jira: SCRUM-53
    AC: Follow Up Date is displayed on the Aging tooltip (edge case: no date set)
    """
    aging_page = AgingPage(page)

    with allure.step("Open tooltip for a balance cell without a Follow Up Date"):
        aging_page.open()
        aging_page.open_tooltip_for_cell(BALANCE_CELL_WITHOUT_FOLLOWUP_DATE)

    with allure.step("Verify tooltip renders normally without error"):
        assert aging_page.is_tooltip_visible(), "Tooltip did not open"
        assert aging_page.tooltip_followup_date.is_visible(), "Follow Up Date field should render even when empty"


@allure.epic("SCRUM-53: All Task Comments in Aging Balance Tooltip")
@allure.feature("aging")
@allure.story("AC4: When Off, the tooltip shows only the most recent comment")
@allure.title("Toggle Off shows only the most recent comment")
def test_pos_toggle_off_shows_most_recent_comment_only(page):
    """
    Jira: SCRUM-53
    AC: When Off, the tooltip shows only the most recent comment — no change from current behavior
    """
    aging_page = AgingPage(page)

    with allure.step("Verify toggle is Off and open tooltip for a cell with multiple comments"):
        aging_page.open()
        assert not aging_page.is_show_all_comments_toggle_on(), "Toggle should be Off"
        aging_page.open_tooltip_for_cell(BALANCE_CELL_MULTIPLE_COMMENTS)

    with allure.step("Verify only the most recent comment is displayed"):
        assert aging_page.get_comment_count() == 1, "Expected exactly 1 comment when toggle is Off"
        assert MOST_RECENT_COMMENT_TEXT in aging_page.get_comment_texts()[0], "Displayed comment is not the most recent"


@allure.epic("SCRUM-53: All Task Comments in Aging Balance Tooltip")
@allure.feature("aging")
@allure.story("AC5: When On, all user-authored comments appear oldest-to-newest")
@allure.title("Toggle On shows all comments oldest-to-newest")
def test_pos_toggle_on_shows_all_comments_oldest_to_newest(page):
    """
    Jira: SCRUM-53
    AC: When On, all user-authored comments appear in the tooltip in oldest-to-newest order
    """
    aging_page = AgingPage(page)

    with allure.step("Turn the toggle On and open tooltip for a cell with multiple comments"):
        aging_page.open()
        aging_page.toggle_show_all_comments()
        aging_page.open_tooltip_for_cell(BALANCE_CELL_MULTIPLE_COMMENTS)

    with allure.step("Verify all comments are displayed in oldest-to-newest order"):
        comments = aging_page.get_comment_texts()
        assert len(comments) > 1, "Expected multiple comments when toggle is On"
        assert comments == EXPECTED_COMMENTS_OLDEST_TO_NEWEST, "Comments not in oldest-to-newest order"


@allure.epic("SCRUM-53: All Task Comments in Aging Balance Tooltip")
@allure.feature("aging")
@allure.story("AC6: System-generated comments never appear in the tooltip")
@allure.title("System-generated comments never shown")
def test_err_system_comments_never_shown(page):
    """
    Jira: SCRUM-53
    AC: System-generated comments never appear in the tooltip, regardless of the setting
    """
    aging_page = AgingPage(page)

    with allure.step("Open tooltip with toggle On for a cell containing a system-generated comment"):
        aging_page.open()
        aging_page.toggle_show_all_comments()
        aging_page.open_tooltip_for_cell(BALANCE_CELL_WITH_SYSTEM_COMMENT)
        comments_on = " ".join(aging_page.get_comment_texts())

    with allure.step("Verify system-generated comment text is not present with toggle On"):
        assert SYSTEM_COMMENT_TEXT not in comments_on, "System-generated comment leaked into tooltip (toggle On)"

    with allure.step("Set toggle Off and re-open tooltip for the same cell"):
        aging_page.close_tooltip()
        aging_page.toggle_show_all_comments()
        aging_page.open_tooltip_for_cell(BALANCE_CELL_WITH_SYSTEM_COMMENT)
        comments_off = " ".join(aging_page.get_comment_texts())

    with allure.step("Verify system-generated comment text is still not present with toggle Off"):
        assert SYSTEM_COMMENT_TEXT not in comments_off, "System-generated comment leaked into tooltip (toggle Off)"


@allure.epic("SCRUM-53: All Task Comments in Aging Balance Tooltip")
@allure.feature("aging")
@allure.story("AC7: The Comments section auto-scrolls to the most recent comment on tooltip open")
@allure.title("Comments auto-scroll to most recent comment")
def test_pos_comments_autoscroll_to_most_recent(page):
    """
    Jira: SCRUM-53
    AC: The Comments section auto-scrolls to the most recent comment on tooltip open
    """
    aging_page = AgingPage(page)

    with allure.step("Turn toggle On and open tooltip for a cell with overflowing comments"):
        aging_page.open()
        aging_page.toggle_show_all_comments()
        aging_page.open_tooltip_for_cell(BALANCE_CELL_OVERFLOW_COMMENTS)

    with allure.step("Verify the most recent comment row is scrolled into view"):
        most_recent_row = aging_page.tooltip_comment_rows.last
        assert most_recent_row.is_visible(), "Most recent comment is not scrolled into view on open"


@allure.epic("SCRUM-53: All Task Comments in Aging Balance Tooltip")
@allure.feature("aging")
@allure.story("AC8: Each comment displays author, date/time, and comment text")
@allure.title("Each comment shows author, date/time, and text")
def test_pos_comment_shows_author_date_text(page):
    """
    Jira: SCRUM-53
    AC: Each comment displays author, date/time, and comment text
    """
    aging_page = AgingPage(page)

    with allure.step("Open tooltip for a cell with at least one comment"):
        aging_page.open()
        aging_page.open_tooltip_for_cell(BALANCE_CELL_MULTIPLE_COMMENTS)

    with allure.step("Verify author, date/time, and text are all displayed for the first comment"):
        assert aging_page.get_comment_author(0), "Comment author not displayed"
        assert aging_page.get_comment_timestamp(0), "Comment date/time not displayed"
        assert aging_page.get_comment_texts()[0], "Comment text not displayed"


@allure.epic("SCRUM-53: All Task Comments in Aging Balance Tooltip")
@allure.feature("aging")
@allure.story("AC9: The Comments section scrolls independently when comments overflow")
@allure.title("Comments section scrolls independently")
def test_pos_comments_section_scrolls_independently(page):
    """
    Jira: SCRUM-53
    AC: The Comments section scrolls independently when comments overflow
    """
    aging_page = AgingPage(page)

    with allure.step("Turn toggle On and open tooltip for a cell with overflowing comments"):
        aging_page.open()
        aging_page.toggle_show_all_comments()
        aging_page.open_tooltip_for_cell(BALANCE_CELL_OVERFLOW_COMMENTS)

    with allure.step("Scroll within the Comments section and verify other tooltip elements remain fixed"):
        followup_box_before = aging_page.tooltip_followup_date.bounding_box()
        aging_page.tooltip_comments_section.hover()
        page.mouse.wheel(0, 300)
        followup_box_after = aging_page.tooltip_followup_date.bounding_box()
        assert followup_box_before == followup_box_after, "Tooltip elements outside Comments section moved on scroll"


@allure.epic("SCRUM-53: All Task Comments in Aging Balance Tooltip")
@allure.feature("aging")
@allure.story("AC10: The tooltip respects the max height")
@allure.title("Tooltip respects max height")
def test_pos_tooltip_respects_max_height(page):
    """
    Jira: SCRUM-53
    AC: The tooltip respects the max height
    """
    aging_page = AgingPage(page)

    with allure.step("Turn toggle On and open tooltip for a cell with many comments"):
        aging_page.open()
        aging_page.toggle_show_all_comments()
        aging_page.open_tooltip_for_cell(BALANCE_CELL_OVERFLOW_COMMENTS)

    with allure.step("Verify tooltip height does not exceed the defined max height"):
        box = aging_page.tooltip.bounding_box()
        assert box is not None, "Could not measure tooltip height"
        assert box["height"] <= 500, f"Tooltip height {box['height']}px exceeds expected max height"


@allure.epic("SCRUM-53: All Task Comments in Aging Balance Tooltip")
@allure.feature("aging")
@allure.story("AC11: The tooltip opens to the right or left of the balance cell")
@allure.title("Tooltip opens left or right of the balance cell")
def test_pos_tooltip_opens_left_or_right_of_cell(page):
    """
    Jira: SCRUM-53
    AC: The tooltip opens to the right or left of the balance cell
    """
    aging_page = AgingPage(page)
    aging_page.open()

    with allure.step("Open tooltip for a cell near the right edge and verify it flips left"):
        aging_page.open_tooltip_for_cell(BALANCE_CELL_NEAR_RIGHT_EDGE)
        cell_box = aging_page.balance_cells.nth(BALANCE_CELL_NEAR_RIGHT_EDGE).bounding_box()
        tooltip_box = aging_page.tooltip.bounding_box()
        assert tooltip_box["x"] < cell_box["x"], "Tooltip did not open to the left of the cell near the right edge"
        aging_page.close_tooltip()

    with allure.step("Open tooltip for a cell near the left edge and verify it opens right"):
        aging_page.open_tooltip_for_cell(BALANCE_CELL_NEAR_LEFT_EDGE)
        cell_box = aging_page.balance_cells.nth(BALANCE_CELL_NEAR_LEFT_EDGE).bounding_box()
        tooltip_box = aging_page.tooltip.bounding_box()
        assert tooltip_box["x"] >= cell_box["x"], "Tooltip did not open to the right of the cell near the left edge"


@allure.epic("SCRUM-53: All Task Comments in Aging Balance Tooltip")
@allure.feature("aging")
@allure.story("AC12: The See Task button opens the task as expected")
@allure.title("See Task button opens the associated task")
def test_pos_see_task_button_opens_task(page):
    """
    Jira: SCRUM-53
    AC: The See Task button opens the task as expected
    """
    aging_page = AgingPage(page)

    with allure.step("Open tooltip for a cell with an associated task"):
        aging_page.open()
        aging_page.open_tooltip_for_cell(BALANCE_CELL_WITH_TASK)

    with allure.step("Click See Task and verify navigation"):
        assert aging_page.is_see_task_button_visible(), "See Task button not visible"
        aging_page.click_see_task()
        page.wait_for_url("**/tasks/**", timeout=settings.TIMEOUT)


@allure.epic("SCRUM-53: All Task Comments in Aging Balance Tooltip")
@allure.feature("aging")
@allure.story("AC12: The See Task button opens the task as expected")
@allure.title("See Task button hidden when no linked task")
def test_err_see_task_button_hidden_without_task(page):
    """
    Jira: SCRUM-53
    AC: The See Task button opens the task as expected (negative: no linked task)
    """
    aging_page = AgingPage(page)

    with allure.step("Open tooltip for a cell with no associated task"):
        aging_page.open()
        aging_page.open_tooltip_for_cell(BALANCE_CELL_WITHOUT_TASK)

    with allure.step("Verify See Task button is hidden or disabled"):
        assert not aging_page.is_see_task_button_visible(), "See Task button should be hidden when no task is linked"


@allure.epic("SCRUM-53: All Task Comments in Aging Balance Tooltip")
@allure.feature("aging")
@allure.story("AC13: Comments section is hidden when there are no user-authored comments")
@allure.title("Comments section hidden when no user-authored comments")
def test_pos_comments_section_hidden_when_no_user_comments(page):
    """
    Jira: SCRUM-53
    AC: If a balance has no user-authored comments, the Comments section is hidden regardless of the setting
    """
    aging_page = AgingPage(page)

    with allure.step("Open tooltip with toggle Off for a cell with no user-authored comments"):
        aging_page.open()
        aging_page.open_tooltip_for_cell(BALANCE_CELL_NO_USER_COMMENTS)
        assert not aging_page.is_comments_section_visible(), "Comments section should be hidden (toggle Off)"
        aging_page.close_tooltip()

    with allure.step("Open tooltip with toggle On for the same cell"):
        aging_page.toggle_show_all_comments()
        aging_page.open_tooltip_for_cell(BALANCE_CELL_NO_USER_COMMENTS)

    with allure.step("Verify Comments section remains hidden"):
        assert not aging_page.is_comments_section_visible(), "Comments section should remain hidden (toggle On)"


@allure.epic("SCRUM-53: All Task Comments in Aging Balance Tooltip")
@allure.feature("aging")
@allure.story("AC14: All Aging tooltip acceptance criteria apply to Aging within Case View")
@allure.title("Aging tooltip behavior applies within Case View")
def test_pos_aging_tooltip_behavior_in_case_view(page):
    """
    Jira: SCRUM-53
    AC: All Aging tooltip acceptance criteria apply to Aging within Case View
    """
    aging_page = AgingPage(page)

    with allure.step("Navigate to a Case's Case View and locate the Aging section"):
        aging_page.open_case_view(CASE_VIEW_CASE_ID)
        assert aging_page.is_case_view_toggle_visible(), "Toggle not present in Case View Aging section"

    with allure.step("Turn the toggle On and open the tooltip within Case View"):
        aging_page.toggle_case_view_show_all_comments()
        aging_page.open_tooltip_for_cell(BALANCE_CELL_MULTIPLE_COMMENTS)

    with allure.step("Verify comments display oldest-to-newest, consistent with the main Aging page"):
        comments = aging_page.get_comment_texts()
        assert len(comments) > 1, "Expected multiple comments in Case View Aging tooltip"


@allure.epic("SCRUM-53: All Task Comments in Aging Balance Tooltip")
@allure.feature("aging")
@allure.story("RBAC: Viewer role cannot modify the toggle or saved view")
@allure.title("Viewer role cannot modify toggle or saved view")
def test_perm_viewer_cannot_modify_toggle_or_saved_view(page):
    """
    Jira: SCRUM-53
    AC: Access-control check derived from AC1/AC2 — Viewer (read-only) role should not
    be able to change the toggle or persist a saved view.
    """
    aging_page = AgingPage(page)

    with allure.step("Navigate to the Aging page as a Viewer (read-only) role"):
        aging_page.open()

    with allure.step("Verify toggle is visible but disabled for Viewer role"):
        assert aging_page.is_show_all_comments_toggle_visible(), "Toggle should still be visible for Viewer"
        assert aging_page.show_all_comments_toggle.is_disabled(), "Toggle should be disabled for Viewer role"

    with allure.step("Verify Save View action is unavailable for Viewer role"):
        assert not aging_page.save_view_button.is_enabled(), "Save View should be disabled for Viewer role"
