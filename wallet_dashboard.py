#!/usr/bin/env python3
"""
AstroKiran Dashboard - Wallet + Meta Ads Analytics
Press 'D' to switch views, 'L' to load CSV.
"""

from datetime import datetime
from typing import Optional
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Static, DataTable, ProgressBar
from textual.worker import Worker, WorkerState

from styles import DASHBOARD_CSS
from screens import ViewSelectorScreen, FilePickerScreen
from data_fetcher import fetch_all_dashboard_data
from utils import parse_meta_ads_csv, fetch_cac_data
from display_helpers import (
    format_db_stats_row,
    format_kpi_row,
    format_daily_recharge_rows,
    format_rds_metrics_row1,
    format_rds_metrics_row2,
    format_user_row,
    format_meta_kpi_row,
    format_meta_ad_row,
    format_pagination_text,
    format_meta_pagination_text,
)


class WalletDashboard(App):
    """Textual app to monitor wallet and Meta Ads data."""

    CSS = DASHBOARD_CSS
    REFRESH_SECONDS = 30
    TICK_RATE = 0.1

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh Now"),
        ("n", "next_page", "Next Page"),
        ("p", "prev_page", "Previous Page"),
        ("left", "prev_page", "Prev"),
        ("right", "next_page", "Next"),
        ("home", "first_page", "First Page"),
        ("end", "last_page", "Last Page"),
        ("d", "open_view_selector", "Switch View"),
        ("l", "load_csv", "Load CSV"),
    ]

    def __init__(self):
        super().__init__()
        self.data = {}  # All dashboard data
        self.current_page = 1
        self.items_per_page = 100
        self.total_users = 0
        self.timer_ticks = 0
        self.total_ticks = int(self.REFRESH_SECONDS / self.TICK_RATE)
        self.current_view = 'wallet'
        self.meta_ads_data = []
        self.meta_ads_summary = {}
        self.meta_csv_path = None
        self.cac_data = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Container(id="refresh-timer-container"):
            yield Static(f"Auto-refresh every {self.REFRESH_SECONDS}s", id="refresh-label")
            yield ProgressBar(total=self.total_ticks, show_eta=False, id="refresh-bar")

        with Container(id="wallet-view"):
            with Container(id="db-stats-container"):
                yield Static("DATABASE CONNECTION STATS", classes="section-header")
                yield DataTable(id="db-stats-table")
            with Container(id="kpi-container"):
                yield Static("TODAY'S WALLET METRICS", classes="section-header")
                yield DataTable(id="kpi-table")
            with Container(id="daily-recharge-container"):
                yield Static("DAILY RECHARGE COUNTS (Last 7 Days)", classes="section-header")
                yield DataTable(id="daily-recharge-table")
            with Container(id="rds-container-1"):
                yield Static("AWS RDS CLOUDWATCH METRICS - Performance", classes="section-header")
                yield DataTable(id="rds-table-1")
            with Container(id="rds-container-2"):
                yield Static("AWS RDS METRICS - Latency & Replication Status", classes="section-header")
                yield DataTable(id="rds-table-2")
            with Container(id="users-container"):
                yield Static("REAL USERS ONLY - Created or Recharged since Nov 13, 2025", classes="section-header")
                yield DataTable(id="all-users-table")
                yield Static("Page 1 of 1", id="pagination-info")

        with Container(id="meta-ads-view", classes="hidden"):
            with Container(id="meta-kpi-container"):
                yield Static("META ADS CAMPAIGN METRICS", classes="section-header")
                yield DataTable(id="meta-kpi-table")
            with Container(id="meta-ads-container"):
                yield Static("AD SET PERFORMANCE (Sorted by Spend)", classes="section-header")
                yield DataTable(id="meta-ads-table")
                yield Static("Press L to load CSV", id="meta-pagination-info")

        yield Static("Last updated: Never", id="last-update")
        yield Footer()

    def on_mount(self) -> None:
        # Setup tables
        self._setup_table("#db-stats-table", ["Connections", "Active Queries", "Idle", "Cache Hit %"])
        self._setup_table("#kpi-table", ["Today's Recharge", "Total Promo Cash", "Today's Revenue", "Today's Spend"])
        self._setup_table("#daily-recharge-table", ["Day", "Today", "Yesterday", "2 days ago", "3 days ago", "4 days ago", "5 days ago", "6 days ago"])
        self._setup_table("#rds-table-1", ["CPU %", "Memory Free (GB)", "Read IOPS", "Write IOPS"])
        self._setup_table("#rds-table-2", ["Read Latency (ms)", "Write Latency (ms)", "WAL Bytes Behind", "Time Since Last TX"])
        self._setup_table("#all-users-table", ["ID", "Name", "Phone", "Real", "Promo", "#", "Total", "Spent", "#", "Created", "Last Activity"], cursor=True)
        self._setup_table("#meta-kpi-table", ["Period", "Spend", "Reach", "Freq", "Installs", "CPI", "Customers", "Revenue", "CAC"])
        self._setup_table("#meta-ads-table", ["Ad Set Name", "Spend", "Installs", "CPI", "Impressions", "Clicks", "CTR %", "Status"], cursor=True)

        self.fetch_data()
        self.set_interval(self.TICK_RATE, self._tick_timer)

    def _setup_table(self, table_id: str, columns: list, cursor: bool = False):
        table = self.query_one(table_id, DataTable)
        table.add_columns(*columns)
        table.zebra_stripes = True
        if cursor:
            table.cursor_type = "row"

    def _tick_timer(self) -> None:
        self.timer_ticks += 1
        bar = self.query_one("#refresh-bar", ProgressBar)
        bar.progress = self.timer_ticks

        if self.timer_ticks % 10 == 0:
            seconds_left = self.REFRESH_SECONDS - (self.timer_ticks * self.TICK_RATE)
            self.query_one("#refresh-label", Static).update(f"Auto-refresh every {self.REFRESH_SECONDS}s | Next refresh in {int(seconds_left)}s")

        if self.timer_ticks >= self.total_ticks:
            self.timer_ticks = 0
            bar.progress = 0
            self.fetch_data()

    def fetch_data(self) -> None:
        self.run_worker(self._fetch_worker, thread=True, exclusive=True)

    def _fetch_worker(self) -> dict:
        return fetch_all_dashboard_data(self.current_page, self.items_per_page)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.state == WorkerState.SUCCESS:
            self.data = event.worker.result
            if self.data.get('error'):
                self.notify(f"DB Error: {self.data['error']}", severity="error")
            else:
                self.total_users = self.data.get('total_users', 0)
                self._update_display()
        elif event.state == WorkerState.ERROR:
            self.notify("Failed to fetch data", severity="error")

    def _update_display(self) -> None:
        # DB Stats
        table = self.query_one("#db-stats-table", DataTable)
        table.clear()
        table.add_row(*format_db_stats_row(self.data['db_stats']))

        # KPIs
        table = self.query_one("#kpi-table", DataTable)
        table.clear()
        table.add_row(*format_kpi_row(self.data['kpi_data']))

        # Daily Recharge
        table = self.query_one("#daily-recharge-table", DataTable)
        table.clear()
        counts, amounts = format_daily_recharge_rows(self.data['daily_recharge_data'])
        table.add_row(*counts)
        table.add_row(*amounts)

        # RDS Metrics
        if self.data.get('rds_metrics'):
            table = self.query_one("#rds-table-1", DataTable)
            table.clear()
            table.add_row(*format_rds_metrics_row1(self.data['rds_metrics']))

            table = self.query_one("#rds-table-2", DataTable)
            table.clear()
            table.add_row(*format_rds_metrics_row2(self.data['rds_metrics'], self.data['replication_status']))

        # Users Table
        table = self.query_one("#all-users-table", DataTable)
        table.clear()
        for row in self.data['all_users_data']:
            table.add_row(*format_user_row(row))

        # Pagination
        self.query_one("#pagination-info", Static).update(
            format_pagination_text(self.current_page, self.total_users, self.items_per_page)
        )

        # Timestamp
        self.query_one("#last-update", Static).update(
            f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Auto-refresh: ON"
        )

    def _update_meta_display(self) -> None:
        if not self.meta_ads_summary:
            return

        # KPI Table
        table = self.query_one("#meta-kpi-table", DataTable)
        table.clear()
        table.add_row(*format_meta_kpi_row(self.meta_ads_summary, self.cac_data))

        # Ads Table
        table = self.query_one("#meta-ads-table", DataTable)
        table.clear()
        for ad in self.meta_ads_data:
            table.add_row(*format_meta_ad_row(ad))

        # Pagination
        self.query_one("#meta-pagination-info", Static).update(
            format_meta_pagination_text(self.meta_csv_path, len(self.meta_ads_data))
        )

    # --- Actions ---

    def action_refresh(self) -> None:
        self.timer_ticks = 0
        self.query_one("#refresh-bar", ProgressBar).progress = 0
        self.notify("Refreshing...", severity="information")
        self.fetch_data()

    def action_next_page(self) -> None:
        total_pages = max(1, (self.total_users + self.items_per_page - 1) // self.items_per_page)
        if self.current_page < total_pages:
            self.current_page += 1
            self.fetch_data()

    def action_prev_page(self) -> None:
        if self.current_page > 1:
            self.current_page -= 1
            self.fetch_data()

    def action_first_page(self) -> None:
        if self.current_page != 1:
            self.current_page = 1
            self.fetch_data()

    def action_last_page(self) -> None:
        total_pages = max(1, (self.total_users + self.items_per_page - 1) // self.items_per_page)
        if self.current_page != total_pages:
            self.current_page = total_pages
            self.fetch_data()

    def action_open_view_selector(self) -> None:
        def handle_result(view: Optional[str]) -> None:
            if view == "wallet":
                self.current_view = 'wallet'
                self.query_one("#wallet-view").remove_class("hidden")
                self.query_one("#meta-ads-view").add_class("hidden")
            elif view == "meta":
                self.current_view = 'meta'
                self.query_one("#wallet-view").add_class("hidden")
                self.query_one("#meta-ads-view").remove_class("hidden")
                if not self.meta_ads_data:
                    self.notify("No CSV loaded. Press L to load.", severity="warning")

        self.push_screen(ViewSelectorScreen(), handle_result)

    def action_load_csv(self) -> None:
        def handle_result(path: Optional[str]) -> None:
            if path:
                try:
                    self.meta_ads_data, self.meta_ads_summary = parse_meta_ads_csv(path)
                    self.meta_csv_path = path

                    date_start = self.meta_ads_summary.get('date_start')
                    date_end = self.meta_ads_summary.get('date_end')
                    if date_start and date_end:
                        self.cac_data = fetch_cac_data(date_start, date_end)

                    self._update_meta_display()
                    self.current_view = 'meta'
                    self.query_one("#wallet-view").add_class("hidden")
                    self.query_one("#meta-ads-view").remove_class("hidden")
                    self.notify(f"Loaded {len(self.meta_ads_data)} ad sets", severity="information")
                except Exception as e:
                    self.notify(f"Error: {e}", severity="error")

        self.push_screen(FilePickerScreen(), handle_result)


if __name__ == "__main__":
    WalletDashboard().run()
