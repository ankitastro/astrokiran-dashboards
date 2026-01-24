#!/usr/bin/env python3
"""
AstroKiran Dashboard - View Framework Based
Press 'D' to switch views, 'L' to load CSV.
All functions are stateless and under 20 lines.
"""

from datetime import datetime
from typing import Optional
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Static, DataTable, ProgressBar, Button
from textual.worker import Worker, WorkerState
from textual.screen import ModalScreen

from styles import DASHBOARD_CSS
from views.registry import ViewRegistry
from views.wallet import WalletView
from views.meta import MetaView
from views.base import ContainerConfig
from components.date_range import DateRangeSelector, DateRange, today

# Business Dashboard Views (BD-1.0 to BD-9.0)
from views.revenue import RevenueView
from views.users import UsersView
from views.consultations import ConsultationsView
from views.payments import PaymentsView
from views.meta_campaigns import MetaCampaignsView
from views.meta_totals import MetaTotalsView
from views.astrologer_performance import AstrologerPerformanceView
from views.astrologer_availability import AstrologerAvailabilityView
from views.guides import GuidesView
from views.guide_performance import GuidePerformanceView


# --- Register Views ---
ViewRegistry.register(WalletView())
ViewRegistry.register(MetaView())

# Business Dashboard Views
ViewRegistry.register(RevenueView())           # BD-1.0
ViewRegistry.register(UsersView())             # BD-2.0
ViewRegistry.register(ConsultationsView())     # BD-3.0
ViewRegistry.register(PaymentsView())          # BD-4.0
ViewRegistry.register(MetaCampaignsView())     # BD-6.0
ViewRegistry.register(MetaTotalsView())        # BD-7.0
ViewRegistry.register(AstrologerPerformanceView())   # BD-8.0
ViewRegistry.register(AstrologerAvailabilityView())  # BD-9.0
ViewRegistry.register(GuidesView())                  # Guides Dashboard
ViewRegistry.register(GuidePerformanceView())        # Guide Performance (Repeat/Leakage)


# --- Modal Screens ---

class ViewSelectorScreen(ModalScreen):
    """Modal for selecting views with arrow key navigation."""

    CSS = """
    ViewSelectorScreen { align: center middle; }
    #dialog { width: 40; height: auto; border: thick #32416a; background: #0f1525; padding: 1 2; }
    #title { text-align: center; text-style: bold; color: #8fb0ee; margin-bottom: 1; }
    #hint { text-align: center; color: #788bc9; text-style: italic; }
    #view-table { height: auto; max-height: 20; }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("enter", "select", "Select"),
    ]

    def compose(self) -> ComposeResult:
        self.views = ViewRegistry.all()
        with Container(id="dialog"):
            yield Static("Select View", id="title")
            yield DataTable(id="view-table")
            yield Static("↑↓ Navigate  Enter Select  Esc Cancel", id="hint")

    def on_mount(self) -> None:
        table = self.query_one("#view-table", DataTable)
        table.add_columns("", "View")
        table.cursor_type = "row"
        table.zebra_stripes = True
        for view in self.views:
            table.add_row(view.icon, view.name)
        table.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self._select_current()

    def action_select(self) -> None:
        self._select_current()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def _select_current(self) -> None:
        table = self.query_one("#view-table", DataTable)
        idx = table.cursor_row
        if idx is not None and idx < len(self.views):
            self.dismiss(self.views[idx].view_id)


class FilePickerScreen(ModalScreen):
    """Modal for selecting CSV files."""

    CSS = """
    FilePickerScreen { align: center middle; }
    #dialog { width: 80; height: 20; border: thick #32416a; background: #0f1525; padding: 1 2; }
    #title { text-align: center; text-style: bold; color: #8fb0ee; margin-bottom: 1; }
    #file-table { height: 12; }
    #buttons { align: center middle; height: auto; margin-top: 1; }
    #buttons Button { margin: 0 1; }
    """

    def __init__(self):
        super().__init__()
        self.files = scan_csv_files()

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Static("Select CSV File", id="title")
            yield DataTable(id="file-table")
            with Container(id="buttons"):
                yield Button("Load", variant="primary", id="load-btn")
                yield Button("Cancel", id="cancel-btn")

    def on_mount(self) -> None:
        table = self.query_one("#file-table", DataTable)
        table.add_columns("File", "Folder", "Size", "Modified")
        table.cursor_type = "row"
        for f in self.files:
            table.add_row(f['name'], f['folder'], f['size_str'], f['mod_str'])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel-btn":
            self.dismiss(None)
        elif event.button.id == "load-btn":
            self._select_file()

    def on_data_table_row_selected(self, _) -> None:
        self._select_file()

    def _select_file(self) -> None:
        table = self.query_one("#file-table", DataTable)
        idx = table.cursor_row
        if idx is not None and idx < len(self.files):
            self.dismiss(str(self.files[idx]['path']))


# --- Helper Functions (stateless, <20 lines) ---

def scan_csv_files() -> list:
    """Scan common folders for CSV files."""
    from pathlib import Path
    folders = [Path.home() / d for d in ["Downloads", "Desktop", "Documents"]]
    files = []
    for folder in folders:
        if folder.exists():
            for f in folder.glob("*.csv"):
                stat = f.stat()
                size = f"{stat.st_size / 1024:.1f} KB"
                mod = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                files.append({'path': f, 'name': f.name, 'folder': folder.name, 'size_str': size, 'mod_str': mod})
    files.sort(key=lambda x: x['mod_str'], reverse=True)
    return files[:20]


def build_container(cfg: ContainerConfig) -> Container:
    """Build a container from config."""
    container = Container(id=cfg.id)
    return container


def setup_table(table: DataTable, columns: list, cursor: bool = False) -> None:
    """Setup a DataTable with columns."""
    table.add_columns(*columns)
    table.zebra_stripes = True
    if cursor:
        table.cursor_type = "row"


def update_table(table: DataTable, rows: list, columns: list = None) -> None:
    """Update table with new rows, optionally updating columns."""
    table.clear()
    if columns:
        # Clear existing columns - table.columns returns ColumnKey objects directly
        col_keys = list(table.columns)
        for key in col_keys:
            table.remove_column(key)
        table.add_columns(*columns)
    for row in rows:
        table.add_row(*row)


# --- Main App ---

class Dashboard(App):
    """Main dashboard app using view framework."""

    CSS = DASHBOARD_CSS
    REFRESH_SECONDS = 30

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("d", "switch_view", "Views"),
        ("f", "date_filter", "Date Filter"),
        ("l", "load_csv", "Load CSV"),
        ("n", "next_page", "Next"),
        ("p", "prev_page", "Prev"),
    ]

    def __init__(self):
        super().__init__()
        self.current_view_id = "wallet"
        self.view_data = {}
        self.page = 1
        self.per_page = 100
        self.csv_path = None
        self.timer_ticks = 0
        self.total_ticks = int(self.REFRESH_SECONDS / 0.1)
        self.date_range: DateRange = today()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="filter-container"):
            yield Static(f"📅 {self.date_range}", id="date-range-label")
        with Container(id="timer-container"):
            yield Static(f"Auto-refresh: {self.REFRESH_SECONDS}s", id="timer-label")
            yield ProgressBar(total=self.total_ticks, show_eta=False, id="timer-bar")
        for view in ViewRegistry.all():
            hidden = "hidden" if view.view_id != self.current_view_id else ""
            with Container(id=f"view-{view.view_id}", classes=hidden):
                for cfg in view.get_containers():
                    with Container(id=cfg.id):
                        yield Static(cfg.header, classes="section-header")
                        for tbl in cfg.tables:
                            yield DataTable(id=tbl.id)
        yield Static("Last updated: Never", id="last-update")
        yield Footer()

    def on_mount(self) -> None:
        for view in ViewRegistry.all():
            for cfg in view.get_containers():
                for tbl in cfg.tables:
                    table = self.query_one(f"#{tbl.id}", DataTable)
                    setup_table(table, tbl.columns, tbl.cursor)
        self.fetch_data()
        self.set_interval(0.1, self._tick)

    def _tick(self) -> None:
        self.timer_ticks += 1
        bar = self.query_one("#timer-bar", ProgressBar)
        bar.progress = self.timer_ticks
        if self.timer_ticks % 10 == 0:
            secs = self.REFRESH_SECONDS - int(self.timer_ticks * 0.1)
            self.query_one("#timer-label", Static).update(f"Auto-refresh: {secs}s")
        if self.timer_ticks >= self.total_ticks:
            self._reset_timer()
            self.fetch_data()

    def _reset_timer(self) -> None:
        self.timer_ticks = 0
        self.query_one("#timer-bar", ProgressBar).progress = 0
        self.query_one("#timer-label", Static).update(f"Auto-refresh: {self.REFRESH_SECONDS}s")

    def fetch_data(self) -> None:
        self.run_worker(self._fetch_worker, thread=True, exclusive=True)

    def _fetch_worker(self) -> dict:
        view = ViewRegistry.get(self.current_view_id)
        start, end = self.date_range.as_tuple()
        if self.current_view_id == "wallet":
            return view.fetch_data(page=self.page, per_page=self.per_page)
        elif self.current_view_id == "meta":
            return view.fetch_data(csv_path=self.csv_path)
        return view.fetch_data(start_date=start, end_date=end)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.state == WorkerState.SUCCESS:
            self.view_data = event.worker.result
            self._update_display()

    def _update_display(self) -> None:
        view = ViewRegistry.get(self.current_view_id)
        rows = view.format_rows(self.view_data)
        # Get dynamic columns if the view supports it
        dynamic_cols = {}
        if hasattr(view, 'get_dynamic_columns'):
            dynamic_cols = view.get_dynamic_columns(self.view_data)
        for table_id, table_rows in rows.items():
            table = self.query_one(f"#{table_id}", DataTable)
            columns = dynamic_cols.get(table_id)
            update_table(table, table_rows, columns)
        self.query_one("#last-update", Static).update(
            f"Last updated: {datetime.now().strftime('%H:%M:%S')}"
        )

    def _switch_to_view(self, view_id: str) -> None:
        if view_id == self.current_view_id:
            return
        self.query_one(f"#view-{self.current_view_id}").add_class("hidden")
        self.query_one(f"#view-{view_id}").remove_class("hidden")
        self.current_view_id = view_id
        self.fetch_data()

    def action_refresh(self) -> None:
        self._reset_timer()
        self.fetch_data()

    def action_switch_view(self) -> None:
        def handle(view_id: Optional[str]) -> None:
            if view_id:
                self._switch_to_view(view_id)
        self.push_screen(ViewSelectorScreen(), handle)

    def action_date_filter(self) -> None:
        def handle(result: Optional[DateRange]) -> None:
            if result:
                self.date_range = result
                self.query_one("#date-range-label", Static).update(f"📅 {self.date_range}")
                self._reset_timer()
                self.fetch_data()
        self.push_screen(DateRangeSelector(self.date_range), handle)

    def action_load_csv(self) -> None:
        def handle(path: Optional[str]) -> None:
            if path:
                self.csv_path = path
                self._switch_to_view("meta")
        self.push_screen(FilePickerScreen(), handle)

    def action_next_page(self) -> None:
        self.page += 1
        self.fetch_data()

    def action_prev_page(self) -> None:
        if self.page > 1:
            self.page -= 1
            self.fetch_data()


if __name__ == "__main__":
    Dashboard().run()
