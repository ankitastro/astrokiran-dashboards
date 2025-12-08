"""
Modal Screen Classes for AstroKiran Dashboard
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Static, DataTable, Button
from textual.screen import ModalScreen

from styles import VIEW_SELECTOR_CSS, FILE_PICKER_CSS
from utils import scan_for_csv_files


class ViewSelectorScreen(ModalScreen):
    """Modal screen for selecting dashboard view."""

    CSS = VIEW_SELECTOR_CSS

    def compose(self) -> ComposeResult:
        with Container(id="view-dialog"):
            yield Static("Select View", id="view-dialog-title")
            yield Button("Wallet Dashboard", id="view-wallet-btn", classes="view-option")
            yield Button("Meta Ads Analytics", id="view-meta-btn", classes="view-option")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "view-wallet-btn":
            self.dismiss("wallet")
        elif event.button.id == "view-meta-btn":
            self.dismiss("meta")


class FilePickerScreen(ModalScreen):
    """Modal screen for selecting CSV files from common folders."""

    CSS = FILE_PICKER_CSS

    def __init__(self):
        super().__init__()
        self.csv_files = scan_for_csv_files()

    def compose(self) -> ComposeResult:
        with Container(id="file-dialog"):
            yield Static("Select Meta Ads CSV File", id="file-dialog-title")
            with Container(id="file-list-container"):
                yield DataTable(id="file-list")
            with Horizontal(id="file-buttons"):
                yield Button("Load Selected", variant="primary", id="load-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")
            yield Static("Scanning: ~/Downloads, ~/Desktop, ~/Documents", id="file-hint")

    def on_mount(self) -> None:
        table = self.query_one("#file-list", DataTable)
        table.add_columns("File Name", "Folder", "Size", "Modified")
        table.cursor_type = "row"
        table.zebra_stripes = True

        if not self.csv_files:
            table.add_row("No CSV files found", "-", "-", "-")
        else:
            for f in self.csv_files:
                size_str = f"{f['size'] / 1024:.1f} KB" if f['size'] < 1024*1024 else f"{f['size'] / (1024*1024):.1f} MB"
                mod_str = f['modified'].strftime("%Y-%m-%d %H:%M")
                table.add_row(f['name'], f['folder'], size_str, mod_str)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel-btn":
            self.dismiss(None)
        elif event.button.id == "load-btn":
            self._load_selected()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Double-click to load."""
        self._load_selected()

    def _load_selected(self) -> None:
        if not self.csv_files:
            return

        table = self.query_one("#file-list", DataTable)
        row_idx = table.cursor_row

        if row_idx is not None and row_idx < len(self.csv_files):
            selected_file = self.csv_files[row_idx]
            self.dismiss(str(selected_file['path']))
