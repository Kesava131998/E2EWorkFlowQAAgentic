from datetime import datetime

from playwright.sync_api import Page
import allure

from pages.base_page import BasePage
from config.settings import settings

# TODO: confirm the real AR Reports routes for this environment once SCRUM-15 is deployed
REPORTS_LANDING_URL = f"{settings.BASE_URL}/reports"
MOM_REPORT_URL = f"{settings.BASE_URL}/reports/mom"
PERCENT_COLLECTED_TREND_URL = f"{settings.BASE_URL}/reports/percent-collected-trend"

MOM_REPORT_NAV_LABEL = "MOM Report"
PERCENT_COLLECTED_TREND_NAV_LABEL = "Percent Collected Trend"

MONTH_LABEL_FORMAT = "%b %Y"


def parse_month_label(label: str) -> datetime:
    """Parse a 'MMM YYYY' month label (e.g. 'Apr 2025') into a datetime."""
    return datetime.strptime(label.strip(), MONTH_LABEL_FORMAT)


def month_index(label: str) -> int:
    """Convert a month label into a comparable absolute month index."""
    parsed = parse_month_label(label)
    return parsed.year * 12 + parsed.month


def months_between(service_label: str, posting_label: str) -> int:
    """Number of months from a service month to a posting month (may be negative)."""
    return month_index(posting_label) - month_index(service_label)


def shift_month_label(label: str, offset: int) -> str:
    """Return the month label `offset` months away from the given label."""
    parsed = parse_month_label(label)
    total = parsed.year * 12 + (parsed.month - 1) + offset
    return datetime(total // 12, total % 12 + 1, 1).strftime(MONTH_LABEL_FORMAT)


class MomReportPage(BasePage):
    """
    Page object for the AR Reports → Month Over Month (MOM) Report (SCRUM-15).

    The MOM Report is a pivot of Percent Collected Trend: service months as rows,
    posting months as columns. Several methods also target the Percent Collected
    Trend report, because the ACs are defined as parity with that report.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # --- Left navigation ---
        self.left_nav = page.locator("[data-testid='left-nav']")
        self.ar_reports_section = self.left_nav.get_by_role("button", name="AR Reports")
        self.ar_reports_links = self.left_nav.locator("[data-testid='ar-reports-nav-link']")
        self.mom_report_nav_link = self.left_nav.get_by_role("link", name=MOM_REPORT_NAV_LABEL)

        # --- Reports landing page ---
        self.report_card_grid = page.locator("[data-testid='report-card-grid']")
        self.mom_report_card = self.report_card_grid.locator(
            "[data-testid='report-card']", has_text=MOM_REPORT_NAV_LABEL
        )

        # --- Report shell ---
        self.page_heading = page.locator("[data-testid='report-heading']")
        self.filter_bar = page.locator("[data-testid='report-filter-bar']")
        self.overflow_filters_button = self.filter_bar.get_by_role("button", name="More filters")
        self.overflow_filter_panel = page.locator("[data-testid='report-filter-overflow']")
        self.unauthorized_view = page.locator("[data-testid='unauthorized-view']")

        # --- MOM pivot grid ---
        self.report_grid = page.locator("[data-testid='mom-report-grid']")
        self.grid_empty_state = self.report_grid.locator("[data-testid='grid-empty-state']")
        self.column_headers = self.report_grid.locator("[data-testid='mom-column-header']")
        self.data_rows = self.report_grid.locator("[data-testid='mom-data-row']")
        self.row_headers = self.report_grid.locator("[data-testid='mom-row-header']")
        self.group_headers = self.report_grid.locator("[data-testid='mom-group-header']")

        # --- Time range toggle ---
        self.time_range_toggle = self.filter_bar.locator("[data-testid='time-range-toggle']")
        self.time_range_options = self.time_range_toggle.locator("[data-testid='time-range-option']")

        # --- Custom date range picker ---
        self.custom_range_picker = page.locator("[data-testid='custom-range-picker']")
        self.custom_range_start = self.custom_range_picker.locator("[data-testid='range-start']")
        self.custom_range_end = self.custom_range_picker.locator("[data-testid='range-end']")
        self.custom_range_month_options = self.custom_range_picker.locator(
            "[data-testid='month-option']"
        )
        self.custom_range_apply_button = self.custom_range_picker.get_by_role(
            "button", name="Apply"
        )
        self.custom_range_validation_message = self.custom_range_picker.locator(
            "[data-testid='range-validation-message']"
        )

        # --- Shared AR Report controls ---
        self.write_offs_toggle = self.filter_bar.locator("[data-testid='write-offs-toggle']")
        self.overpayments_control = self.filter_bar.locator("[data-testid='overpayments-select']")
        self.overpayments_options = page.locator("[data-testid='overpayments-select'] [role='option']")
        self.global_facility_filter = page.locator("[data-testid='global-facility-filter']")
        self.transactions_within_filter = page.locator("[data-testid='transactions-within-select']")
        self.grouping_selector = page.locator("[data-testid='report-grouping-select']")
        self.export_button = self.filter_bar.get_by_role("button", name="Export")

        # --- Percent Collected Trend (reference report) ---
        self.trend_grid = page.locator("[data-testid='percent-collected-trend-grid']")
        self.trend_rows = self.trend_grid.locator("[data-testid='trend-data-row']")

    # ------------------------------------------------------------------ #
    # Navigation
    # ------------------------------------------------------------------ #

    @allure.step("Verify left navigation is visible")
    def is_left_nav_visible(self) -> bool:
        return self.left_nav.is_visible()

    @allure.step("Verify AR Reports nav section is visible")
    def is_ar_reports_section_visible(self) -> bool:
        return self.ar_reports_section.is_visible()

    @allure.step("Expand the AR Reports nav section")
    def open_ar_reports_section(self):
        self.ar_reports_section.click()
        self.ar_reports_links.first.wait_for(
            state="visible", timeout=settings.SHORT_TIMEOUT
        )

    @allure.step("Get the ordered list of AR Reports nav link labels")
    def get_ar_reports_link_labels(self) -> list:
        return [label.strip() for label in self.ar_reports_links.all_inner_texts()]

    @allure.step("Check if AR Reports nav link {label} is visible")
    def is_ar_reports_link_visible(self, label: str) -> bool:
        return self.left_nav.get_by_role("link", name=label).is_visible()

    @allure.step("Click the MOM Report nav link")
    def click_mom_report_nav_link(self):
        self.mom_report_nav_link.click()
        self.wait_for_load()

    @allure.step("Check if nav link {label} is the active route")
    def is_nav_link_active(self, label: str) -> bool:
        link = self.left_nav.get_by_role("link", name=label)
        return link.get_attribute("aria-current") is not None

    @allure.step("Open the AR Report {report_name}")
    def select_ar_report(self, report_name: str):
        self.open_ar_reports_section()
        self.left_nav.get_by_role("link", name=report_name).click()
        self.wait_for_load()

    @allure.step("Navigate to the Reports landing page")
    def open_reports_landing(self):
        self.navigate_to(REPORTS_LANDING_URL)
        self.wait_for_load()

    @allure.step("Navigate directly to the MOM Report")
    def open_mom_report(self):
        self.navigate_to(MOM_REPORT_URL)
        self.wait_for_load()

    @allure.step("Navigate directly to the Percent Collected Trend report")
    def open_percent_collected_trend(self):
        self.navigate_to(PERCENT_COLLECTED_TREND_URL)
        self.wait_for_load()

    @allure.step("Check if the MOM Report landing card is visible")
    def is_mom_report_card_visible(self) -> bool:
        return self.mom_report_card.is_visible()

    @allure.step("Check if the MOM Report landing card is enabled")
    def is_mom_report_card_enabled(self) -> bool:
        return self.mom_report_card.is_enabled()

    @allure.step("Click the MOM Report landing card")
    def click_mom_report_card(self):
        self.mom_report_card.click()
        self.wait_for_load()

    @allure.step("Get the report page heading text")
    def get_page_heading(self) -> str:
        return self.page_heading.inner_text().strip()

    @allure.step("Check if the unauthorized view is shown")
    def is_unauthorized_view_visible(self) -> bool:
        return self.unauthorized_view.is_visible()

    # ------------------------------------------------------------------ #
    # Pivot grid
    # ------------------------------------------------------------------ #

    @allure.step("Verify the MOM pivot grid is visible")
    def is_grid_visible(self) -> bool:
        return self.report_grid.is_visible()

    @allure.step("Verify the pivot grid empty state is visible")
    def is_grid_empty_state_visible(self) -> bool:
        return self.grid_empty_state.is_visible()

    @allure.step("Get the service month row labels")
    def get_service_month_labels(self) -> list:
        return [label.strip() for label in self.row_headers.all_inner_texts()]

    @allure.step("Get the posting month column labels")
    def get_posting_month_labels(self) -> list:
        return [label.strip() for label in self.column_headers.all_inner_texts()]

    @allure.step("Get the pivot grid row count")
    def get_row_count(self) -> int:
        return self.data_rows.count()

    @allure.step("Get the pivot grid data column count")
    def get_column_count(self) -> int:
        return self.column_headers.count()

    @allure.step("Get the cell text at row {row_index}, column {column_index}")
    def get_cell_text(self, row_index: int, column_index: int) -> str:
        cell = self.data_rows.nth(row_index).locator("[data-testid='mom-cell']").nth(column_index)
        return cell.inner_text().strip()

    @allure.step("Get the cell text for service month {service_label} / posting month {posting_label}")
    def get_cell_text_by_months(self, service_label: str, posting_label: str) -> str:
        row_index = self.get_service_month_labels().index(service_label)
        column_index = self.get_posting_month_labels().index(posting_label)
        return self.get_cell_text(row_index, column_index)

    @allure.step("Check if a grouping header row is present in the grid")
    def has_group_header_rows(self) -> bool:
        return self.group_headers.count() > 0

    # ------------------------------------------------------------------ #
    # Time range toggle
    # ------------------------------------------------------------------ #

    @allure.step("Verify the time range toggle is visible")
    def is_time_range_toggle_visible(self) -> bool:
        return self.time_range_toggle.is_visible()

    @allure.step("Get the available time range toggle options")
    def get_time_range_options(self) -> list:
        return [label.strip() for label in self.time_range_options.all_inner_texts()]

    @allure.step("Get the selected time range option")
    def get_selected_time_range(self) -> str:
        selected = self.time_range_toggle.locator(
            "[data-testid='time-range-option'][aria-pressed='true']"
        )
        return selected.inner_text().strip()

    @allure.step("Check if time range option {option} is selected")
    def is_time_range_option_selected(self, option: str) -> bool:
        target = self.time_range_toggle.get_by_role("button", name=option, exact=True)
        return target.get_attribute("aria-pressed") == "true"

    @allure.step("Select the {option} time range option")
    def select_time_range(self, option: str):
        self.time_range_toggle.get_by_role("button", name=option, exact=True).click()
        self.wait_for_load()

    # ------------------------------------------------------------------ #
    # Custom date range picker
    # ------------------------------------------------------------------ #

    @allure.step("Open the custom service date range picker")
    def open_custom_range_picker(self):
        self.select_time_range("Custom")
        self.custom_range_picker.wait_for(state="visible", timeout=settings.SHORT_TIMEOUT)

    @allure.step("Verify the custom range picker is visible")
    def is_custom_range_picker_visible(self) -> bool:
        return self.custom_range_picker.is_visible()

    @allure.step("Set the custom service date range start to {month_label}")
    def set_custom_range_start(self, month_label: str):
        self.custom_range_start.click()
        self.custom_range_picker.get_by_role("button", name=month_label, exact=True).click()

    @allure.step("Set the custom service date range end to {month_label}")
    def set_custom_range_end(self, month_label: str):
        self.custom_range_end.click()
        self.custom_range_picker.get_by_role("button", name=month_label, exact=True).click()

    @allure.step("Get the displayed custom range start value")
    def get_custom_range_start_value(self) -> str:
        return self.custom_range_start.inner_text().strip()

    @allure.step("Get the displayed custom range end value")
    def get_custom_range_end_value(self) -> str:
        return self.custom_range_end.inner_text().strip()

    @allure.step("Check if month {month_label} is selectable in the picker")
    def is_month_selectable(self, month_label: str) -> bool:
        option = self.custom_range_picker.get_by_role("button", name=month_label, exact=True)
        if not option.is_visible():
            return False
        return option.is_enabled()

    @allure.step("Check if the Apply button is enabled")
    def is_custom_range_apply_enabled(self) -> bool:
        return self.custom_range_apply_button.is_enabled()

    @allure.step("Apply the custom service date range")
    def apply_custom_range(self):
        self.custom_range_apply_button.click()
        self.wait_for_load()

    @allure.step("Get the custom range validation message")
    def get_custom_range_validation_message(self) -> str:
        self.custom_range_validation_message.wait_for(
            state="visible", timeout=settings.SHORT_TIMEOUT
        )
        return self.custom_range_validation_message.inner_text().strip()

    @allure.step("Check if a custom range validation message is shown")
    def is_custom_range_validation_shown(self) -> bool:
        return self.custom_range_validation_message.is_visible()

    @allure.step("Apply a custom service date range from {start_label} to {end_label}")
    def apply_service_date_range(self, start_label: str, end_label: str):
        self.open_custom_range_picker()
        self.set_custom_range_start(start_label)
        self.set_custom_range_end(end_label)
        self.apply_custom_range()

    # ------------------------------------------------------------------ #
    # Shared AR Report filters
    # ------------------------------------------------------------------ #

    @allure.step("Verify the report filter bar is visible")
    def is_filter_bar_visible(self) -> bool:
        return self.filter_bar.is_visible()

    @allure.step("Open the overflow filter panel")
    def open_overflow_filters(self):
        if self.overflow_filters_button.is_visible():
            self.overflow_filters_button.click()
            self.overflow_filter_panel.wait_for(
                state="visible", timeout=settings.SHORT_TIMEOUT
            )

    @allure.step("Check if a 'Transactions Within' filter is present")
    def is_transactions_within_filter_present(self) -> bool:
        return self.transactions_within_filter.count() > 0

    @allure.step("Set 'Transactions Within' to {months} months")
    def set_transactions_within(self, months: int):
        self.transactions_within_filter.click()
        self.page.get_by_role("option", name=f"{months}", exact=True).click()
        self.wait_for_load()

    @allure.step("Check if a grouping selector is present")
    def is_grouping_selector_present(self) -> bool:
        return self.grouping_selector.count() > 0

    @allure.step("Check if the page contains the text {text}")
    def page_contains_text(self, text: str) -> bool:
        return self.page.get_by_text(text, exact=False).count() > 0

    @allure.step("Verify the Write-offs toggle is visible")
    def is_write_offs_toggle_visible(self) -> bool:
        return self.write_offs_toggle.is_visible()

    @allure.step("Verify the Write-offs toggle is enabled")
    def is_write_offs_toggle_enabled(self) -> bool:
        return self.write_offs_toggle.is_enabled()

    @allure.step("Get the Write-offs toggle state")
    def is_write_offs_enabled(self) -> bool:
        return self.write_offs_toggle.is_checked()

    @allure.step("Toggle the Write-offs control")
    def toggle_write_offs(self):
        self.write_offs_toggle.click()
        self.wait_for_load()

    @allure.step("Verify the Overpayments control is visible")
    def is_overpayments_control_visible(self) -> bool:
        return self.overpayments_control.is_visible()

    @allure.step("Verify the Overpayments control is enabled")
    def is_overpayments_control_enabled(self) -> bool:
        return self.overpayments_control.is_enabled()

    @allure.step("Open the Overpayments control")
    def open_overpayments_control(self):
        self.overpayments_control.click()
        self.overpayments_options.first.wait_for(
            state="visible", timeout=settings.SHORT_TIMEOUT
        )

    @allure.step("Get the Overpayments options")
    def get_overpayments_options(self) -> list:
        return [label.strip() for label in self.overpayments_options.all_inner_texts()]

    @allure.step("Select Overpayments option {option}")
    def select_overpayments_option(self, option: str):
        self.overpayments_control.click()
        self.page.get_by_role("option", name=option, exact=True).click()
        self.wait_for_load()

    @allure.step("Verify the Global Facility Filter is visible")
    def is_global_facility_filter_visible(self) -> bool:
        return self.global_facility_filter.is_visible()

    @allure.step("Verify the Global Facility Filter is enabled")
    def is_global_facility_filter_enabled(self) -> bool:
        return self.global_facility_filter.is_enabled()

    @allure.step("Select facility {facility_name} in the Global Facility Filter")
    def select_facility(self, facility_name: str):
        self.global_facility_filter.click()
        self.page.get_by_role("option", name=facility_name, exact=True).click()
        self.wait_for_load()

    # ------------------------------------------------------------------ #
    # Export
    # ------------------------------------------------------------------ #

    @allure.step("Verify the Export control is visible")
    def is_export_visible(self) -> bool:
        return self.export_button.is_visible()

    @allure.step("Verify the Export control is enabled")
    def is_export_enabled(self) -> bool:
        return self.export_button.is_enabled()

    @allure.step("Click Export and capture the download")
    def export_report(self):
        with self.page.expect_download(timeout=settings.PAGE_LOAD_TIMEOUT) as download_info:
            self.export_button.click()
        return download_info.value

    # ------------------------------------------------------------------ #
    # Percent Collected Trend (reference report)
    # ------------------------------------------------------------------ #

    @allure.step("Verify the Percent Collected Trend grid is visible")
    def is_trend_grid_visible(self) -> bool:
        return self.trend_grid.is_visible()

    @allure.step("Get the Percent Collected Trend value for service month {month_label}")
    def get_trend_value_for_month(self, month_label: str) -> str:
        row = self.trend_rows.filter(has_text=month_label).first
        return row.locator("[data-testid='trend-percent-collected']").inner_text().strip()
