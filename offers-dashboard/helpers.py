"""
Helper functions for the dashboard.
"""

from textual.widgets import DataTable


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
