"""
View Selector Modal - Select dashboard view.
"""

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static, DataTable
from textual.screen import ModalScreen

from views.registry import ViewRegistry


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
            yield Static("Navigate  Enter Select  Esc Cancel", id="hint")

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
