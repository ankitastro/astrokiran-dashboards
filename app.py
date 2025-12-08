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


# --- Register Views ---
ViewRegistry.register(WalletView())
ViewRegistry.register(MetaView())


# --- Modal Screens ---

class ViewSelectorScreen(ModalScreen):
    """Modal for selecting views."""

    CSS = """
    ViewSelectorScreen { align: center middle; }
    #dialog { width: 35; height: auto; border: thick #32416a; background: #0f1525; padding: 1 2; }
    #title { text-align: center; text-style: bold; color: #8fb0ee; margin-bottom: 1; }
    .btn { width: 100%; margin-bottom: 1; }
    """

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Static("Select View", id="title")
            for view in ViewRegistry.all():
                yield Button(f"{view.icon} {view.name}", id=f"btn-{view.view_id}", classes="btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        view_id = event.button.id.replace("btn-", "")
        self.dismiss(view_id)


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


def update_table(table: DataTable, rows: list) -> None:
    """Update table with new rows."""
    table.clear()
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

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
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
        self.query_one("#timer-bar", ProgressBar).progress = self.timer_ticks
        if self.timer_ticks % 10 == 0:
            secs = self.REFRESH_SECONDS - int(self.timer_ticks * 0.1)
            self.query_one("#timer-label", Static).update(f"Auto-refresh: {secs}s")
        if self.timer_ticks >= self.total_ticks:
            self.timer_ticks = 0
            self.fetch_data()

    def fetch_data(self) -> None:
        self.run_worker(self._fetch_worker, thread=True, exclusive=True)

    def _fetch_worker(self) -> dict:
        view = ViewRegistry.get(self.current_view_id)
        if self.current_view_id == "wallet":
            return view.fetch_data(page=self.page, per_page=self.per_page)
        return view.fetch_data(csv_path=self.csv_path)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.state == WorkerState.SUCCESS:
            self.view_data = event.worker.result
            self._update_display()

    def _update_display(self) -> None:
        view = ViewRegistry.get(self.current_view_id)
        rows = view.format_rows(self.view_data)
        for table_id, table_rows in rows.items():
            table = self.query_one(f"#{table_id}", DataTable)
            update_table(table, table_rows)
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
        self.timer_ticks = 0
        self.fetch_data()

    def action_switch_view(self) -> None:
        def handle(view_id: Optional[str]) -> None:
            if view_id:
                self._switch_to_view(view_id)
        self.push_screen(ViewSelectorScreen(), handle)

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
