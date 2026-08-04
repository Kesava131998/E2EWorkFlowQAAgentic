from datetime import datetime

import allure

from pages.mom_report_page import (
    MOM_REPORT_NAV_LABEL,
    MOM_REPORT_URL,
    MONTH_LABEL_FORMAT,
    PERCENT_COLLECTED_TREND_NAV_LABEL,
    MomReportPage,
    month_index,
    months_between,
    shift_month_label,
)

EPIC = "SCRUM-15: [FE] - Month Over Month (MOM) Report"
FEATURE = "mom_report"

DEFAULT_RANGE_MONTHS = 12
MAX_CUSTOM_RANGE_MONTHS = 24

# TODO: replace with real facility names once test data is confirmed for this environment
FACILITY_A = "TODO-facility-a"
FACILITY_B = "TODO-facility-b"
FACILITY_WITH_NO_ACTIVITY = "TODO-facility-no-activity"


def current_month_label() -> str:
    """Current month as a 'MMM YYYY' label."""
    return datetime.now().strftime(MONTH_LABEL_FORMAT)


def percent_to_float(value: str) -> float:
    """Convert a rendered percent value (e.g. '84.2%') into a float."""
    return float(value.replace("%", "").replace(",", "").strip())


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC1: 'MOM Report' appears in the AR Reports left nav below 'Percent Collected Trend'")
@allure.title("MOM Report nav entry sits directly below Percent Collected Trend")
def test_pos_mom_report_nav_entry_below_percent_collected_trend(page):
    """
    Jira: SCRUM-15
    AC: "MOM Report" appears in the AR Reports left nav below "Percent Collected Trend."
    """
    mom_page = MomReportPage(page)

    with allure.step("Step 1: Verify the left navigation container is visible"):
        mom_page.navigate_to(MOM_REPORT_URL)
        mom_page.wait_for_load()
        assert mom_page.is_left_nav_visible(), "Left navigation is not visible"

    with allure.step("Step 2: Verify the AR Reports nav section is visible"):
        assert mom_page.is_ar_reports_section_visible(), "AR Reports nav section is not visible"

    with allure.step("Step 3: Expand the AR Reports nav section"):
        mom_page.open_ar_reports_section()

    with allure.step("Step 4: Verify the Percent Collected Trend child link is visible"):
        assert mom_page.is_ar_reports_link_visible(PERCENT_COLLECTED_TREND_NAV_LABEL), (
            "Percent Collected Trend link is not visible in AR Reports"
        )

    with allure.step("Step 5: Verify the MOM Report child link is visible"):
        assert mom_page.is_ar_reports_link_visible(MOM_REPORT_NAV_LABEL), (
            "MOM Report link is not visible in AR Reports"
        )

    with allure.step("Step 6: Verify MOM Report sits directly below Percent Collected Trend"):
        labels = mom_page.get_ar_reports_link_labels()
        trend_index = labels.index(PERCENT_COLLECTED_TREND_NAV_LABEL)
        mom_index = labels.index(MOM_REPORT_NAV_LABEL)
        assert mom_index == trend_index + 1, (
            f"MOM Report should sit directly below Percent Collected Trend; nav order was {labels}"
        )


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC1: Clicking the MOM Report nav entry loads the MOM Report page")
@allure.title("MOM Report nav entry loads the report page")
def test_pos_mom_report_nav_entry_loads_report_page(page):
    """
    Jira: SCRUM-15
    AC: "MOM Report" appears in the AR Reports left nav and opens the MOM Report.
    """
    mom_page = MomReportPage(page)

    with allure.step("Step 1: Expand AR Reports and verify the MOM Report link is actionable"):
        mom_page.navigate_to(MOM_REPORT_URL)
        mom_page.wait_for_load()
        mom_page.open_ar_reports_section()
        assert mom_page.mom_report_nav_link.is_visible(), "MOM Report nav link is not visible"
        assert mom_page.mom_report_nav_link.is_enabled(), "MOM Report nav link is not enabled"

    with allure.step("Step 2-3: Click the MOM Report nav link and wait for the report to load"):
        mom_page.click_mom_report_nav_link()

    with allure.step("Step 4: Verify the page heading reads 'MOM Report'"):
        assert mom_page.get_page_heading() == MOM_REPORT_NAV_LABEL, (
            f"Unexpected report heading: {mom_page.get_page_heading()}"
        )

    with allure.step("Step 5: Verify the MOM Report nav link is the active route"):
        assert mom_page.is_nav_link_active(MOM_REPORT_NAV_LABEL), (
            "MOM Report nav link does not carry the active state"
        )

    with allure.step("Step 6: Verify the pivot report grid is visible"):
        assert mom_page.is_grid_visible(), "MOM pivot grid is not visible"


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC15: A new card on the reports landing page navigates to the MOM report")
@allure.title("Reports landing card navigates to the MOM Report")
def test_pos_reports_landing_card_navigates_to_mom_report(page):
    """
    Jira: SCRUM-15
    AC: A new card is on the reports landing page which navigates to the MOM report.
    """
    mom_page = MomReportPage(page)

    with allure.step("Step 1: Navigate to the Reports landing page"):
        mom_page.open_reports_landing()
        assert mom_page.report_card_grid.is_visible(), "Report card grid is not visible"

    with allure.step("Step 2: Verify a card titled 'MOM Report' is visible"):
        assert mom_page.is_mom_report_card_visible(), "MOM Report card is not visible"

    with allure.step("Step 3: Verify the MOM Report card is enabled"):
        assert mom_page.is_mom_report_card_enabled(), "MOM Report card is not enabled"

    with allure.step("Step 4-5: Click the card and wait for the report to load"):
        mom_page.click_mom_report_card()

    with allure.step("Step 6: Verify the MOM Report page heading and grid"):
        assert mom_page.get_page_heading() == MOM_REPORT_NAV_LABEL, (
            "Card did not navigate to the MOM Report"
        )
        assert mom_page.is_grid_visible(), "MOM pivot grid is not visible after card navigation"


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC2: Rows represent service months; columns represent posting months")
@allure.title("Pivot grid renders service months as rows and posting months as columns")
def test_pos_pivot_rows_service_months_columns_posting_months(page):
    """
    Jira: SCRUM-15
    AC: Rows represent service months; columns represent posting months.
    """
    mom_page = MomReportPage(page)

    with allure.step("Step 1: Open the MOM Report and verify the pivot grid is visible"):
        mom_page.open_mom_report()
        assert mom_page.is_grid_visible(), "MOM pivot grid is not visible"

    with allure.step("Step 2-3: Verify every row header is a service month label"):
        service_months = mom_page.get_service_month_labels()
        assert service_months, "No service month row headers were rendered"
        for label in service_months:
            assert month_index(label) > 0, f"Row header '{label}' is not a valid month label"

    with allure.step("Step 4-5: Verify every data column header is a posting month label"):
        posting_months = mom_page.get_posting_month_labels()
        assert posting_months, "No posting month column headers were rendered"
        for label in posting_months:
            assert month_index(label) > 0, f"Column header '{label}' is not a valid month label"

    with allure.step("Step 6: Verify row and column counts match the default 12-month range"):
        assert len(service_months) == DEFAULT_RANGE_MONTHS, (
            f"Expected {DEFAULT_RANGE_MONTHS} service month rows, got {len(service_months)}"
        )
        assert len(posting_months) == DEFAULT_RANGE_MONTHS, (
            f"Expected {DEFAULT_RANGE_MONTHS} posting month columns, got {len(posting_months)}"
        )


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC2: Columns are ordered chronologically left to right")
@allure.title("Posting date columns are ordered oldest to most recent")
def test_pos_posting_columns_ordered_chronologically(page):
    """
    Jira: SCRUM-15
    AC: Columns are ordered chronologically left to right (oldest → most recent posting month).
    """
    mom_page = MomReportPage(page)

    with allure.step("Step 1: Open the MOM Report and verify the column header row is visible"):
        mom_page.open_mom_report()
        assert mom_page.column_headers.first.is_visible(), "Column header row is not visible"

    with allure.step("Step 2-3: Read and parse all posting month column labels"):
        posting_months = mom_page.get_posting_month_labels()
        assert posting_months, "No posting month column headers were rendered"
        parsed = [month_index(label) for label in posting_months]

    with allure.step("Step 4: Verify each column is strictly earlier than the one to its right"):
        for left, right in zip(parsed, parsed[1:]):
            assert left < right, (
                f"Posting columns are not in chronological order: {posting_months}"
            )

    with allure.step("Step 5: Verify no duplicate posting month appears in the header row"):
        assert len(set(posting_months)) == len(posting_months), (
            f"Duplicate posting month columns found: {posting_months}"
        )


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC3: Cells are populated where posting month is strictly after the service month")
@allure.title("Cells after the service month are populated with percent values")
def test_pos_cells_populated_when_posting_after_service_month(page):
    """
    Jira: SCRUM-15
    AC: Cells are only populated where posting month is strictly after the service month.
    """
    mom_page = MomReportPage(page)

    with allure.step("Step 1: Open the MOM Report and verify the grid has data rows"):
        mom_page.open_mom_report()
        assert mom_page.is_grid_visible(), "MOM pivot grid is not visible"
        assert mom_page.get_row_count() > 0, "MOM pivot grid has no data rows"

    with allure.step("Step 2: Read the oldest service month row header"):
        service_months = mom_page.get_service_month_labels()
        oldest_service_month = service_months[0]

    with allure.step("Step 3: Identify columns whose posting month is after that service month"):
        posting_months = mom_page.get_posting_month_labels()
        eligible = [
            index
            for index, posting in enumerate(posting_months)
            if months_between(oldest_service_month, posting) > 0
        ]
        assert eligible, (
            f"No posting columns fall after service month {oldest_service_month}"
        )

    with allure.step("Step 4-6: Verify every eligible cell holds a valid percent value"):
        for column_index in eligible:
            value = mom_page.get_cell_text(0, column_index)
            assert value, (
                f"Cell for {oldest_service_month} / {posting_months[column_index]} is blank "
                "but the posting month is after the service month"
            )
            assert "%" in value, f"Cell value '{value}' is not rendered as a percent"
            assert percent_to_float(value) >= 0, f"Percent value '{value}' is negative"


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC3: Cells where posting month is on or before the service month are blank")
@allure.title("Cells not strictly after the service month are blank")
def test_err_cells_blank_when_posting_not_after_service_month(page):
    """
    Jira: SCRUM-15
    AC: Only populate cells where the posting month is strictly after the service month.
    Cells where posting month <= service month are blank.
    """
    mom_page = MomReportPage(page)

    with allure.step("Step 1: Open the MOM Report and verify the pivot grid is visible"):
        mom_page.open_mom_report()
        assert mom_page.is_grid_visible(), "MOM pivot grid is not visible"

    with allure.step("Step 2: Read all service month rows and posting month columns"):
        service_months = mom_page.get_service_month_labels()
        posting_months = mom_page.get_posting_month_labels()
        assert service_months and posting_months, "Pivot grid headers are missing"

    with allure.step("Step 3-6: Verify every cell not strictly after its service month is blank"):
        for row_index, service in enumerate(service_months):
            for column_index, posting in enumerate(posting_months):
                if months_between(service, posting) > 0:
                    continue
                value = mom_page.get_cell_text(row_index, column_index)
                assert value in ("", "-", "—"), (
                    f"Cell for service {service} / posting {posting} should be blank "
                    f"(posting month is not after service month) but held '{value}'"
                )


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC4: Each cell applies a 'Transactions Within' filter scoped to the month interval")
@allure.title("Cell value matches Percent Collected Trend at the equivalent interval")
def test_pos_cell_matches_percent_collected_trend_interval(page):
    """
    Jira: SCRUM-15
    AC: Each cell applies a "Transactions Within" filter scoped to the number of months
    between that row's service month and that column's posting month. The report shares
    the same underlying percent collected calculation as Percent Collected Trend.
    """
    mom_page = MomReportPage(page)

    with allure.step("Step 1-2: Open the MOM Report and read the oldest service month row"):
        mom_page.open_mom_report()
        assert mom_page.is_grid_visible(), "MOM pivot grid is not visible"
        service_months = mom_page.get_service_month_labels()
        oldest_service_month = service_months[0]

    with allure.step("Step 3: Read the cell 1 month after that service month"):
        one_month_value = mom_page.get_cell_text_by_months(
            oldest_service_month, shift_month_label(oldest_service_month, 1)
        )
        assert one_month_value, "1-month interval cell is blank"

    with allure.step("Step 4: Read the cell 2 months after that service month"):
        two_month_value = mom_page.get_cell_text_by_months(
            oldest_service_month, shift_month_label(oldest_service_month, 2)
        )
        assert two_month_value, "2-month interval cell is blank"

    with allure.step("Step 5: Open the Percent Collected Trend report"):
        mom_page.select_ar_report(PERCENT_COLLECTED_TREND_NAV_LABEL)
        assert mom_page.is_filter_bar_visible(), "Percent Collected Trend filter bar is not visible"

    with allure.step("Step 6-7: Set Transactions Within to 1 month and compare the value"):
        mom_page.set_transactions_within(1)
        trend_one_month = mom_page.get_trend_value_for_month(oldest_service_month)
        assert percent_to_float(trend_one_month) == percent_to_float(one_month_value), (
            f"MOM 1-month cell ({one_month_value}) does not match Percent Collected Trend "
            f"at Transactions Within = 1 ({trend_one_month})"
        )

    with allure.step("Step 8: Set Transactions Within to 2 months and compare the value"):
        mom_page.set_transactions_within(2)
        trend_two_month = mom_page.get_trend_value_for_month(oldest_service_month)
        assert percent_to_float(trend_two_month) == percent_to_float(two_month_value), (
            f"MOM 2-month cell ({two_month_value}) does not match Percent Collected Trend "
            f"at Transactions Within = 2 ({trend_two_month})"
        )

    with allure.step("Step 9: Verify collection matures as the interval widens"):
        assert percent_to_float(two_month_value) >= percent_to_float(one_month_value), (
            "Percent collected should not decrease as the posting interval widens"
        )


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC5: Posting columns begin 1 month after the range start and end 1 month after the range end")
@allure.title("Posting columns are offset one month from the service date range")
def test_pos_posting_columns_offset_one_month_from_service_range(page):
    """
    Jira: SCRUM-15
    AC: The user selects a service date range. Posting date columns are derived from that
    range: they begin 1 month after the range start and end 1 month after the range end.
    Example: Jan 2025 – Mar 2025 → posting date columns Feb 2025 – Apr 2025.
    """
    mom_page = MomReportPage(page)
    range_start = "Jan 2025"
    range_end = "Mar 2025"

    with allure.step("Step 1: Open the MOM Report and verify the time range toggle is visible"):
        mom_page.open_mom_report()
        assert mom_page.is_time_range_toggle_visible(), "Time range toggle is not visible"

    with allure.step("Step 2: Open the custom service date range picker"):
        mom_page.open_custom_range_picker()
        assert mom_page.is_custom_range_picker_visible(), "Custom range picker did not open"

    with allure.step(f"Step 3: Set the service date range start to {range_start}"):
        mom_page.set_custom_range_start(range_start)
        assert range_start in mom_page.get_custom_range_start_value(), (
            "Range start does not reflect the selected month"
        )

    with allure.step(f"Step 4: Set the service date range end to {range_end}"):
        mom_page.set_custom_range_end(range_end)
        assert range_end in mom_page.get_custom_range_end_value(), (
            "Range end does not reflect the selected month"
        )

    with allure.step("Step 5: Apply the custom range"):
        mom_page.apply_custom_range()

    with allure.step("Step 6: Verify the service month rows match the selected range"):
        assert mom_page.get_service_month_labels() == ["Jan 2025", "Feb 2025", "Mar 2025"], (
            f"Unexpected service month rows: {mom_page.get_service_month_labels()}"
        )

    with allure.step("Step 7-8: Verify the first and last posting columns are offset by 1 month"):
        posting_months = mom_page.get_posting_month_labels()
        assert posting_months[0] == shift_month_label(range_start, 1), (
            f"First posting column should be {shift_month_label(range_start, 1)}, "
            f"got {posting_months[0]}"
        )
        assert posting_months[-1] == shift_month_label(range_end, 1), (
            f"Last posting column should be {shift_month_label(range_end, 1)}, "
            f"got {posting_months[-1]}"
        )

    with allure.step("Step 9: Verify the posting column count matches the service range width"):
        assert len(posting_months) == 3, (
            f"Expected 3 posting date columns for a 3-month range, got {len(posting_months)}"
        )


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC6: The 6 / 12 / 18 / Custom toggle controls the service date range width")
@allure.title("6-month toggle renders 6 service rows and 6 posting columns")
def test_pos_six_month_toggle_renders_six_rows_and_columns(page):
    """
    Jira: SCRUM-15
    AC: Time range toggle (6 / 12 / 18 / Custom) controls the service date range,
    which determines the posting date columns shown.
    """
    mom_page = MomReportPage(page)

    with allure.step("Step 1: Open the MOM Report and verify the '6' toggle option is actionable"):
        mom_page.open_mom_report()
        option = mom_page.time_range_toggle.get_by_role("button", name="6", exact=True)
        assert option.is_visible(), "'6' time range option is not visible"
        assert option.is_enabled(), "'6' time range option is not enabled"

    with allure.step("Step 2-3: Select the '6' toggle option and wait for the report to refresh"):
        mom_page.select_time_range("6")

    with allure.step("Step 4: Verify only '6' is selected"):
        assert mom_page.is_time_range_option_selected("6"), "'6' option is not selected"
        for other in ("12", "18", "Custom"):
            assert not mom_page.is_time_range_option_selected(other), (
                f"'{other}' should not be selected after choosing '6'"
            )

    with allure.step("Step 5-6: Verify 6 service month rows and 6 posting month columns"):
        assert mom_page.get_row_count() == 6, (
            f"Expected 6 service month rows, got {mom_page.get_row_count()}"
        )
        assert mom_page.get_column_count() == 6, (
            f"Expected 6 posting month columns, got {mom_page.get_column_count()}"
        )

    with allure.step("Step 7: Verify the first posting column is 1 month after the first row"):
        service_months = mom_page.get_service_month_labels()
        posting_months = mom_page.get_posting_month_labels()
        assert posting_months[0] == shift_month_label(service_months[0], 1), (
            "First posting column is not 1 month after the first service month row"
        )


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC6: The 6 / 12 / 18 / Custom toggle controls the service date range width")
@allure.title("18-month toggle renders 18 service rows and 18 posting columns")
def test_pos_eighteen_month_toggle_renders_eighteen_rows_and_columns(page):
    """
    Jira: SCRUM-15
    AC: The time range toggle supports 6, 12, 18, and Custom options; the selected
    width determines the posting date columns shown.
    """
    mom_page = MomReportPage(page)

    with allure.step("Step 1: Open the MOM Report and verify the '18' toggle option is actionable"):
        mom_page.open_mom_report()
        option = mom_page.time_range_toggle.get_by_role("button", name="18", exact=True)
        assert option.is_visible(), "'18' time range option is not visible"
        assert option.is_enabled(), "'18' time range option is not enabled"

    with allure.step("Step 2-3: Select the '18' toggle option and wait for the report to refresh"):
        mom_page.select_time_range("18")

    with allure.step("Step 4: Verify only '18' is selected"):
        assert mom_page.is_time_range_option_selected("18"), "'18' option is not selected"
        for other in ("6", "12", "Custom"):
            assert not mom_page.is_time_range_option_selected(other), (
                f"'{other}' should not be selected after choosing '18'"
            )

    with allure.step("Step 5-6: Verify 18 service month rows and 18 posting month columns"):
        assert mom_page.get_row_count() == 18, (
            f"Expected 18 service month rows, got {mom_page.get_row_count()}"
        )
        assert mom_page.get_column_count() == 18, (
            f"Expected 18 posting month columns, got {mom_page.get_column_count()}"
        )

    with allure.step("Step 7: Verify the last posting column is 1 month after the last row"):
        service_months = mom_page.get_service_month_labels()
        posting_months = mom_page.get_posting_month_labels()
        assert posting_months[-1] == shift_month_label(service_months[-1], 1), (
            "Last posting column is not 1 month after the last service month row"
        )


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC7: 12 months is the selected default")
@allure.title("12 months is the default selected time range")
def test_pos_twelve_month_range_is_default(page):
    """
    Jira: SCRUM-15
    AC: By default, 12 months is selected.
    """
    mom_page = MomReportPage(page)

    with allure.step("Step 1-2: Open the MOM Report for the first time in the session"):
        mom_page.open_mom_report()

    with allure.step("Step 3: Verify the time range toggle offers 6 / 12 / 18 / Custom"):
        assert mom_page.is_time_range_toggle_visible(), "Time range toggle is not visible"
        options = mom_page.get_time_range_options()
        for expected in ("6", "12", "18", "Custom"):
            assert expected in options, f"Time range option '{expected}' is missing from {options}"

    with allure.step("Step 4: Verify '12' is selected without any user interaction"):
        assert mom_page.get_selected_time_range() == "12", (
            f"Default time range should be 12, got {mom_page.get_selected_time_range()}"
        )

    with allure.step("Step 5: Verify 6, 18 and Custom are not selected"):
        for other in ("6", "18", "Custom"):
            assert not mom_page.is_time_range_option_selected(other), (
                f"'{other}' should not be selected by default"
            )

    with allure.step("Step 6-7: Verify 12 service month rows and 12 posting month columns"):
        assert mom_page.get_row_count() == DEFAULT_RANGE_MONTHS, (
            f"Expected {DEFAULT_RANGE_MONTHS} service month rows, got {mom_page.get_row_count()}"
        )
        assert mom_page.get_column_count() == DEFAULT_RANGE_MONTHS, (
            f"Expected {DEFAULT_RANGE_MONTHS} posting month columns, "
            f"got {mom_page.get_column_count()}"
        )


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC8: Custom time range allows selecting up to 24 months of service dates")
@allure.title("Custom range accepts exactly 24 months")
def test_pos_custom_range_accepts_twenty_four_months(page):
    """
    Jira: SCRUM-15
    AC: Custom allows selecting up to 24 months of service date range.
    """
    mom_page = MomReportPage(page)
    range_end = current_month_label()
    range_start = shift_month_label(range_end, -(MAX_CUSTOM_RANGE_MONTHS - 1))

    with allure.step("Step 1-2: Open the custom service date range picker"):
        mom_page.open_mom_report()
        mom_page.open_custom_range_picker()
        assert mom_page.is_custom_range_picker_visible(), "Custom range picker did not open"

    with allure.step(f"Step 3-4: Set a 24-month range from {range_start} to {range_end}"):
        mom_page.set_custom_range_start(range_start)
        mom_page.set_custom_range_end(range_end)

    with allure.step("Step 5: Apply the range and verify it is accepted"):
        assert not mom_page.is_custom_range_validation_shown(), (
            "A validation message was shown for a valid 24-month range"
        )
        mom_page.apply_custom_range()

    with allure.step("Step 6-8: Verify 24 service month rows and 24 posting month columns"):
        assert mom_page.get_row_count() == MAX_CUSTOM_RANGE_MONTHS, (
            f"Expected {MAX_CUSTOM_RANGE_MONTHS} service month rows, got {mom_page.get_row_count()}"
        )
        assert mom_page.get_column_count() == MAX_CUSTOM_RANGE_MONTHS, (
            f"Expected {MAX_CUSTOM_RANGE_MONTHS} posting month columns, "
            f"got {mom_page.get_column_count()}"
        )


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC8: Custom time range allows selecting up to 24 months of service dates")
@allure.title("Custom range rejects a span longer than 24 months")
def test_err_custom_range_rejects_span_over_twenty_four_months(page):
    """
    Jira: SCRUM-15
    AC (negative): Custom allows selecting up to 24 months of service date range —
    a 25-month span must be rejected.
    """
    mom_page = MomReportPage(page)
    range_end = current_month_label()
    over_limit_start = shift_month_label(range_end, -MAX_CUSTOM_RANGE_MONTHS)

    with allure.step("Step 1: Open the custom service date range picker"):
        mom_page.open_mom_report()
        baseline_columns = mom_page.get_posting_month_labels()
        mom_page.open_custom_range_picker()
        assert mom_page.is_custom_range_picker_visible(), "Custom range picker did not open"

    with allure.step(f"Step 2: Set the range end to {range_end}"):
        mom_page.set_custom_range_end(range_end)

    with allure.step(f"Step 3: Attempt to set the range start to {over_limit_start} (25 months)"):
        selectable = mom_page.is_month_selectable(over_limit_start)
        if selectable:
            mom_page.set_custom_range_start(over_limit_start)

    with allure.step("Step 4-5: Verify the 25-month range cannot be applied"):
        if selectable:
            assert not mom_page.is_custom_range_apply_enabled(), (
                "Apply should be blocked for a 25-month service date range"
            )
            message = mom_page.get_custom_range_validation_message()
            assert "24" in message, (
                f"Validation message should state the 24-month maximum, got '{message}'"
            )

    with allure.step("Step 6: Verify the grid still reflects the previously applied valid range"):
        assert mom_page.get_posting_month_labels() == baseline_columns, (
            "The grid changed even though the over-limit range was rejected"
        )


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC9: Future service dates cannot be selected")
@allure.title("Future service months are not selectable")
def test_err_future_service_dates_not_selectable(page):
    """
    Jira: SCRUM-15
    AC: Users cannot select future service dates, so posting date columns will never
    extend beyond 1 month past the current month at most.
    """
    mom_page = MomReportPage(page)
    this_month = current_month_label()
    next_month = shift_month_label(this_month, 1)
    month_after_next = shift_month_label(this_month, 2)

    with allure.step("Step 1: Open the custom service date range picker"):
        mom_page.open_mom_report()
        mom_page.open_custom_range_picker()
        assert mom_page.is_custom_range_picker_visible(), "Custom range picker did not open"

    with allure.step(f"Step 2: Verify the current month ({this_month}) is selectable"):
        assert mom_page.is_month_selectable(this_month), (
            f"Current month {this_month} should be selectable"
        )

    with allure.step(f"Step 3-5: Verify the next month ({next_month}) is not selectable"):
        assert not mom_page.is_month_selectable(next_month), (
            f"Future month {next_month} should be disabled in the picker"
        )

    with allure.step(f"Step 6: Verify a later future month ({month_after_next}) is not selectable"):
        assert not mom_page.is_month_selectable(month_after_next), (
            f"Future month {month_after_next} should be disabled in the picker"
        )

    with allure.step("Step 7: Verify posting columns never extend beyond 1 month past today"):
        mom_page.open_mom_report()
        posting_months = mom_page.get_posting_month_labels()
        assert month_index(posting_months[-1]) <= month_index(next_month), (
            f"Last posting column {posting_months[-1]} extends beyond 1 month past {this_month}"
        )


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC10: Write-offs and Overpayments controls behave identically to Percent Collected Trend")
@allure.title("Write-offs toggle applies to the pivot values")
def test_pos_write_offs_toggle_applies_to_pivot_values(page):
    """
    Jira: SCRUM-15
    AC: Apply the Write-offs toggle and Overpayments configuration controls as
    Percent Collected Trend.
    """
    mom_page = MomReportPage(page)

    with allure.step("Step 1-2: Open the MOM Report and verify the Write-offs toggle"):
        mom_page.open_mom_report()
        assert mom_page.is_write_offs_toggle_visible(), "Write-offs toggle is not visible"
        assert mom_page.is_write_offs_toggle_enabled(), "Write-offs toggle is not enabled"
        initial_state = mom_page.is_write_offs_enabled()

    with allure.step("Step 3: Read a populated cell value as the baseline"):
        service_months = mom_page.get_service_month_labels()
        posting_month = shift_month_label(service_months[0], 1)
        baseline = mom_page.get_cell_text_by_months(service_months[0], posting_month)
        assert baseline, "Baseline cell is blank — cannot assess the Write-offs toggle"

    with allure.step("Step 4-5: Flip the Write-offs toggle and wait for the report to refresh"):
        mom_page.toggle_write_offs()
        assert mom_page.is_write_offs_enabled() != initial_state, (
            "Write-offs toggle state did not change"
        )

    with allure.step("Step 6: Verify the cell value reflects the new Write-offs setting"):
        toggled = mom_page.get_cell_text_by_months(service_months[0], posting_month)
        assert toggled, "Cell is blank after toggling Write-offs"

    with allure.step("Step 7: Restore the original toggle state and verify the baseline returns"):
        mom_page.toggle_write_offs()
        assert mom_page.is_write_offs_enabled() == initial_state, (
            "Write-offs toggle did not return to its original state"
        )
        assert mom_page.get_cell_text_by_months(service_months[0], posting_month) == baseline, (
            "Cell value did not return to the baseline after restoring the Write-offs toggle"
        )


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC10: Write-offs and Overpayments controls behave identically to Percent Collected Trend")
@allure.title("Overpayments control matches Percent Collected Trend and applies to the report")
def test_pos_overpayments_control_matches_percent_collected_trend(page):
    """
    Jira: SCRUM-15
    AC: Apply the Overpayments configuration controls as Percent Collected Trend.
    """
    mom_page = MomReportPage(page)

    with allure.step("Step 1-2: Open the MOM Report and verify the Overpayments control"):
        mom_page.open_mom_report()
        assert mom_page.is_overpayments_control_visible(), "Overpayments control is not visible"
        assert mom_page.is_overpayments_control_enabled(), "Overpayments control is not enabled"

    with allure.step("Step 3: Open the Overpayments control and read its options"):
        mom_page.open_overpayments_control()
        mom_options = mom_page.get_overpayments_options()
        assert mom_options, "Overpayments control has no options"

    with allure.step("Step 4: Compare the options with Percent Collected Trend"):
        mom_page.select_ar_report(PERCENT_COLLECTED_TREND_NAV_LABEL)
        mom_page.open_overpayments_control()
        trend_options = mom_page.get_overpayments_options()
        assert mom_options == trend_options, (
            f"Overpayments options differ — MOM: {mom_options}, Trend: {trend_options}"
        )

    with allure.step("Step 5: Return to the MOM Report and read a baseline cell value"):
        mom_page.select_ar_report(MOM_REPORT_NAV_LABEL)
        service_months = mom_page.get_service_month_labels()
        posting_month = shift_month_label(service_months[0], 1)
        baseline = mom_page.get_cell_text_by_months(service_months[0], posting_month)
        assert baseline, "Baseline cell is blank — cannot assess the Overpayments control"

    with allure.step("Step 6-7: Select a different Overpayments option and verify the cell updates"):
        alternate = next(option for option in mom_options if option)
        mom_page.select_overpayments_option(alternate)
        updated = mom_page.get_cell_text_by_months(service_months[0], posting_month)
        assert updated, "Cell is blank after changing the Overpayments configuration"


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC11: No 'Transactions Within' filter is present on this report")
@allure.title("No Transactions Within filter on the MOM Report")
def test_err_no_transactions_within_filter_present(page):
    """
    Jira: SCRUM-15
    AC: Do not include a "Transactions Within" filter. The column-by-column layout
    already shows the user how collection matures at each interval.
    """
    mom_page = MomReportPage(page)

    with allure.step("Step 1: Open the MOM Report and verify the filter bar is visible"):
        mom_page.open_mom_report()
        assert mom_page.is_filter_bar_visible(), "Report filter bar is not visible"

    with allure.step("Step 2: Verify no 'Transactions Within' control is in the filter bar"):
        assert not mom_page.is_transactions_within_filter_present(), (
            "'Transactions Within' filter should not be present on the MOM Report"
        )

    with allure.step("Step 3-4: Open the overflow filter panel and re-check"):
        mom_page.open_overflow_filters()
        assert not mom_page.is_transactions_within_filter_present(), (
            "'Transactions Within' filter found in the MOM Report overflow filter panel"
        )

    with allure.step("Step 5: Verify the text 'Transactions Within' is absent from the page"):
        assert not mom_page.page_contains_text("Transactions Within"), (
            "The text 'Transactions Within' should not appear on the MOM Report"
        )

    with allure.step("Step 6: Confirm the control does exist on Percent Collected Trend"):
        mom_page.select_ar_report(PERCENT_COLLECTED_TREND_NAV_LABEL)
        assert mom_page.is_transactions_within_filter_present(), (
            "'Transactions Within' is missing from Percent Collected Trend — the locator "
            "may be stale, so its absence on the MOM Report is not a valid assertion"
        )


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC12: No grouping selector is present on this report")
@allure.title("No grouping selector on the MOM Report")
def test_err_no_grouping_selector_present(page):
    """
    Jira: SCRUM-15
    AC: The MOM Report has no grouping. Users interact with the report through filters only.
    """
    mom_page = MomReportPage(page)

    with allure.step("Step 1: Open the MOM Report and verify the filter bar is visible"):
        mom_page.open_mom_report()
        assert mom_page.is_filter_bar_visible(), "Report filter bar is not visible"

    with allure.step("Step 2: Verify no grouping selector is in the filter bar"):
        assert not mom_page.is_grouping_selector_present(), (
            "A grouping selector should not be present on the MOM Report"
        )

    with allure.step("Step 3-4: Open the overflow filter panel and re-check"):
        mom_page.open_overflow_filters()
        assert not mom_page.is_grouping_selector_present(), (
            "A grouping selector was found in the MOM Report overflow filter panel"
        )

    with allure.step("Step 5: Verify the grid has no group header or expandable group rows"):
        assert not mom_page.has_group_header_rows(), (
            "The MOM pivot grid should not render grouping header rows"
        )

    with allure.step("Step 6: Confirm the grouping selector does exist on Percent Collected Trend"):
        mom_page.select_ar_report(PERCENT_COLLECTED_TREND_NAV_LABEL)
        assert mom_page.is_grouping_selector_present(), (
            "The grouping selector is missing from Percent Collected Trend — the locator "
            "may be stale, so its absence on the MOM Report is not a valid assertion"
        )


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC13: The Global Facility Filter affects the report")
@allure.title("Global Facility Filter scopes the MOM Report data")
def test_pos_global_facility_filter_scopes_report_data(page):
    """
    Jira: SCRUM-15
    AC: Apply the same filter set as Percent Collected Trend, including the
    Global Facility Filter.
    """
    mom_page = MomReportPage(page)
    report_requests = []

    with allure.step("Step 1-2: Open the MOM Report and verify the Global Facility Filter"):
        page.on("request", lambda request: report_requests.append(request.url))
        mom_page.open_mom_report()
        assert mom_page.is_global_facility_filter_visible(), (
            "Global Facility Filter is not visible on the MOM Report"
        )
        assert mom_page.is_global_facility_filter_enabled(), (
            "Global Facility Filter is not enabled"
        )

    with allure.step(f"Step 3-4: Select {FACILITY_A} and capture a baseline cell value"):
        mom_page.select_facility(FACILITY_A)
        service_months = mom_page.get_service_month_labels()
        posting_month = shift_month_label(service_months[0], 1)
        facility_a_value = mom_page.get_cell_text_by_months(service_months[0], posting_month)
        assert facility_a_value, f"No data rendered for {FACILITY_A}"

    with allure.step(f"Step 5-6: Select {FACILITY_B} and wait for the report to refresh"):
        mom_page.select_facility(FACILITY_B)

    with allure.step("Step 7: Verify the cell value changed with the facility scope"):
        facility_b_value = mom_page.get_cell_text_by_months(service_months[0], posting_month)
        assert facility_b_value != facility_a_value, (
            f"Cell value did not change between {FACILITY_A} and {FACILITY_B} — "
            "the Global Facility Filter may not be applied to the MOM Report"
        )

    with allure.step("Step 8: Verify a report data request was issued for the facility change"):
        assert any("facility" in url.lower() for url in report_requests), (
            "No report request carrying a facility scope was observed"
        )


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC14: The report is exportable in the pivot layout")
@allure.title("Export mirrors the pivot layout")
def test_pos_export_mirrors_pivot_layout(page):
    """
    Jira: SCRUM-15
    AC: The report is exportable. The export mirrors the pivot table layout —
    service months as rows, posting months as columns.
    """
    mom_page = MomReportPage(page)

    with allure.step("Step 1-2: Open the MOM Report and verify the Export control"):
        mom_page.open_mom_report()
        assert mom_page.is_export_visible(), "Export control is not visible"
        assert mom_page.is_export_enabled(), "Export control is not enabled"

    with allure.step("Step 3: Capture the on-screen row and column headers"):
        service_months = mom_page.get_service_month_labels()
        posting_months = mom_page.get_posting_month_labels()
        assert service_months and posting_months, "Pivot grid headers are missing"

    with allure.step("Step 4-5: Click Export and capture the download"):
        download = mom_page.export_report()
        assert download.suggested_filename, "Exported file has no filename"

    with allure.step("Step 6: Verify the exported header row lists the posting months in order"):
        exported_path = download.path()
        with open(exported_path, "r", encoding="utf-8") as exported_file:
            exported_lines = [line.rstrip("\n") for line in exported_file if line.strip()]
        assert exported_lines, "Exported file is empty"
        header_row = exported_lines[0]
        for posting_month in posting_months:
            assert posting_month in header_row, (
                f"Posting month {posting_month} is missing from the export header row"
            )

    with allure.step("Step 7: Verify the exported row labels are the service months in order"):
        exported_row_labels = [line.split(",")[0].strip().strip('"') for line in exported_lines[1:]]
        assert exported_row_labels[: len(service_months)] == service_months, (
            f"Exported row labels {exported_row_labels} do not match the on-screen "
            f"service months {service_months}"
        )

    with allure.step("Step 8: Verify an on-screen cell value is present in the export"):
        sample_value = mom_page.get_cell_text_by_months(
            service_months[0], shift_month_label(service_months[0], 1)
        )
        assert sample_value in exported_lines[1], (
            f"On-screen value {sample_value} is missing from the exported first data row"
        )


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC14: The report is exportable in the pivot layout")
@allure.title("Export with an empty result set is still well-formed")
def test_pos_export_empty_result_set_is_well_formed(page):
    """
    Jira: SCRUM-15
    AC (edge case): The report is exportable — an empty result set must still produce
    a well-formed pivot export rather than an error.
    """
    mom_page = MomReportPage(page)

    with allure.step("Step 1: Apply a filter combination that returns no data"):
        mom_page.open_mom_report()
        mom_page.select_facility(FACILITY_WITH_NO_ACTIVITY)

    with allure.step("Step 2: Verify the grid shows an empty state or all-blank cells"):
        posting_months = mom_page.get_posting_month_labels()
        if mom_page.is_grid_empty_state_visible():
            empty_state_shown = True
        else:
            empty_state_shown = False
            for row_index in range(mom_page.get_row_count()):
                for column_index in range(len(posting_months)):
                    assert mom_page.get_cell_text(row_index, column_index) in ("", "-", "—", "0%"), (
                        "Grid rendered a value despite the empty result set"
                    )
        assert empty_state_shown or mom_page.is_grid_visible(), (
            "Neither an empty state nor a blank grid was rendered"
        )

    with allure.step("Step 3: Verify the Export control state is deterministic"):
        assert mom_page.is_export_visible(), "Export control disappeared on an empty result set"

    with allure.step("Step 4-6: Export if enabled and verify the file is well-formed"):
        if mom_page.is_export_enabled():
            download = mom_page.export_report()
            with open(download.path(), "r", encoding="utf-8") as exported_file:
                exported_lines = [line.rstrip("\n") for line in exported_file if line.strip()]
            assert exported_lines, "Exported file is empty for an empty result set"
            for posting_month in posting_months:
                assert posting_month in exported_lines[0], (
                    f"Posting month {posting_month} is missing from the empty export header"
                )
            for line in exported_lines[1:]:
                assert "error" not in line.lower(), (
                    f"Exported file contains error content: {line}"
                )


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC5/AC8: Posting columns derive from the selected service date range")
@allure.title("Single-month custom range renders one row and one posting column")
def test_pos_single_month_custom_range_renders_one_row_one_column(page):
    """
    Jira: SCRUM-15
    AC (edge case): Posting date columns begin 1 month after the range start and end
    1 month after the range end — a single-month range yields exactly one column.
    """
    mom_page = MomReportPage(page)
    single_month = shift_month_label(current_month_label(), -1)

    with allure.step("Step 1: Open the custom service date range picker"):
        mom_page.open_mom_report()
        mom_page.open_custom_range_picker()
        assert mom_page.is_custom_range_picker_visible(), "Custom range picker did not open"

    with allure.step(f"Step 2-3: Set both range start and end to {single_month} and apply"):
        mom_page.set_custom_range_start(single_month)
        mom_page.set_custom_range_end(single_month)
        mom_page.apply_custom_range()

    with allure.step("Step 4-5: Verify exactly one service row and one posting column"):
        assert mom_page.get_row_count() == 1, (
            f"Expected 1 service month row, got {mom_page.get_row_count()}"
        )
        assert mom_page.get_column_count() == 1, (
            f"Expected 1 posting month column, got {mom_page.get_column_count()}"
        )

    with allure.step("Step 6: Verify the posting column is 1 month after the service row"):
        assert mom_page.get_service_month_labels() == [single_month], (
            f"Unexpected service month row: {mom_page.get_service_month_labels()}"
        )
        assert mom_page.get_posting_month_labels() == [shift_month_label(single_month, 1)], (
            f"Unexpected posting month column: {mom_page.get_posting_month_labels()}"
        )

    with allure.step("Step 7: Verify the single cell is populated"):
        assert mom_page.get_cell_text(0, 0), (
            "The single cell should be populated — its posting month is after the service month"
        )


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC6: The time range toggle controls the service date range width")
@allure.title("Toggling from 18 to 6 months shrinks the grid consistently")
def test_pos_toggle_eighteen_to_six_shrinks_grid(page):
    """
    Jira: SCRUM-15
    AC (edge case): The 6 / 12 / 18 / Custom toggle controls the service date range
    width — narrowing the range must not leave stale rows or columns behind.
    """
    mom_page = MomReportPage(page)

    with allure.step("Step 1-2: Apply the 18-month toggle and capture the baseline counts"):
        mom_page.open_mom_report()
        mom_page.select_time_range("18")
        assert mom_page.get_row_count() == 18, "18-month toggle did not render 18 rows"
        assert mom_page.get_column_count() == 18, "18-month toggle did not render 18 columns"
        newest_service_month = mom_page.get_service_month_labels()[-1]

    with allure.step("Step 3-4: Select the 6-month toggle and wait for the report to refresh"):
        mom_page.select_time_range("6")

    with allure.step("Step 5: Verify exactly 6 rows and 6 columns with no stale entries"):
        assert mom_page.get_row_count() == 6, (
            f"Expected 6 service month rows after narrowing, got {mom_page.get_row_count()}"
        )
        assert mom_page.get_column_count() == 6, (
            f"Expected 6 posting month columns after narrowing, got {mom_page.get_column_count()}"
        )

    with allure.step("Step 6: Verify the newest service month row is unchanged"):
        assert mom_page.get_service_month_labels()[-1] == newest_service_month, (
            "Narrowing the range should move the range start, not the newest service month"
        )

    with allure.step("Step 7: Verify the blank-cell rule still holds in the narrowed view"):
        service_months = mom_page.get_service_month_labels()
        posting_months = mom_page.get_posting_month_labels()
        for row_index, service in enumerate(service_months):
            for column_index, posting in enumerate(posting_months):
                if months_between(service, posting) > 0:
                    continue
                assert mom_page.get_cell_text(row_index, column_index) in ("", "-", "—"), (
                    f"Cell for service {service} / posting {posting} should be blank "
                    "in the narrowed view"
                )


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC1/AC15: Access to the MOM Report is permission controlled")
@allure.title("User without AR Reports permission cannot reach the MOM Report")
def test_perm_user_without_ar_reports_cannot_access_mom_report(page):
    """
    Jira: SCRUM-15
    AC (RBAC): The MOM Report nav entry and landing card are only available to users
    with the AR Reports permission; direct route access must be denied.
    """
    # TODO: authenticate as a user without the AR Reports permission once role-based
    # test credentials are confirmed for this environment
    mom_page = MomReportPage(page)
    report_responses = []

    with allure.step("Step 1: Verify the left navigation renders for the restricted user"):
        page.on(
            "response",
            lambda response: report_responses.append((response.url, response.status)),
        )
        mom_page.open_reports_landing()
        assert mom_page.is_left_nav_visible(), "Left navigation is not visible"

    with allure.step("Step 2-3: Verify no MOM Report nav link is available"):
        if mom_page.is_ar_reports_section_visible():
            mom_page.open_ar_reports_section()
        assert not mom_page.is_ar_reports_link_visible(MOM_REPORT_NAV_LABEL), (
            "MOM Report nav link should not be available without the AR Reports permission"
        )

    with allure.step("Step 4-5: Verify no MOM Report card is rendered on the landing page"):
        assert not mom_page.is_mom_report_card_visible(), (
            "MOM Report landing card should not be rendered for a restricted user"
        )

    with allure.step("Step 6: Navigate directly to the MOM Report route and verify access is denied"):
        mom_page.open_mom_report()
        assert mom_page.is_unauthorized_view_visible() or not mom_page.is_grid_visible(), (
            "Direct navigation to the MOM Report should be denied for a restricted user"
        )

    with allure.step("Step 7: Verify no successful MOM Report data response was returned"):
        successful_report_calls = [
            url for url, status in report_responses if "mom" in url.lower() and status == 200
        ]
        assert not successful_report_calls, (
            f"Restricted user received successful MOM Report data: {successful_report_calls}"
        )


@allure.epic(EPIC)
@allure.feature(FEATURE)
@allure.story("AC14: Export is permission controlled")
@allure.title("User without export permission cannot export the MOM Report")
def test_perm_user_without_export_permission_cannot_export(page):
    """
    Jira: SCRUM-15
    AC (RBAC): A user with AR Reports read access but no export permission can view
    the MOM Report but cannot export it.
    """
    # TODO: authenticate as a read-only user without export permission once role-based
    # test credentials are confirmed for this environment
    mom_page = MomReportPage(page)
    export_requests = []

    with allure.step("Step 1-2: Open the MOM Report and verify read access is unaffected"):
        page.on("request", lambda request: export_requests.append(request.url))
        mom_page.open_mom_report()
        assert mom_page.is_grid_visible(), "MOM pivot grid is not visible for the read-only user"
        assert mom_page.get_row_count() > 0, "Report data did not render for the read-only user"

    with allure.step("Step 3-4: Verify the Export control is hidden or disabled"):
        if mom_page.is_export_visible():
            assert not mom_page.is_export_enabled(), (
                "Export control should be disabled without the export permission"
            )
        else:
            assert not mom_page.is_export_visible(), "Export control visibility is inconsistent"

    with allure.step("Step 5-6: Verify no export request is issued"):
        assert not any("export" in url.lower() for url in export_requests), (
            "An export request was issued for a user without the export permission"
        )
