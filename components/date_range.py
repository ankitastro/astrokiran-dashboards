"""
Date Range Selector Component (BD-5.0)
Subtasks: BD-5.1, BD-5.2
- Toggle between preset ranges
- Custom date range selector
Reusable across all dashboard views.
"""

from datetime import datetime, date, timedelta
from dataclasses import dataclass
from typing import Optional, Tuple
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Static, DataTable, Input, Button
from textual.screen import ModalScreen


@dataclass
class DateRange:
    """Represents a date range with start and end dates."""
    start_date: date
    end_date: date
    label: str = "Custom"

    def __str__(self) -> str:
        if self.start_date == self.end_date:
            return f"{self.label}: {self.start_date}"
        return f"{self.label}: {self.start_date} to {self.end_date}"

    def as_tuple(self) -> Tuple[date, date]:
        return (self.start_date, self.end_date)


# --- Preset Date Ranges ---

def today() -> DateRange:
    d = date.today()
    return DateRange(d, d, "Today")


def yesterday() -> DateRange:
    d = date.today() - timedelta(days=1)
    return DateRange(d, d, "Yesterday")


def last_7_days() -> DateRange:
    end = date.today()
    start = end - timedelta(days=6)
    return DateRange(start, end, "Last 7 Days")


def last_30_days() -> DateRange:
    end = date.today()
    start = end - timedelta(days=29)
    return DateRange(start, end, "Last 30 Days")


def this_month() -> DateRange:
    end = date.today()
    start = end.replace(day=1)
    return DateRange(start, end, "This Month")


def last_month() -> DateRange:
    today_date = date.today()
    first_this_month = today_date.replace(day=1)
    end = first_this_month - timedelta(days=1)
    start = end.replace(day=1)
    return DateRange(start, end, "Last Month")


PRESETS = [
    ("today", "Today", today),
    ("yesterday", "Yesterday", yesterday),
    ("last_7", "Last 7 Days", last_7_days),
    ("last_30", "Last 30 Days", last_30_days),
    ("this_month", "This Month", this_month),
    ("last_month", "Last Month", last_month),
    ("custom", "Custom Range", None),
]


# --- Date Range Selector Modal ---

class DateRangeSelector(ModalScreen):
    """Modal for selecting date range with presets and custom option."""

    CSS = """
    DateRangeSelector { align: center middle; }
    #dialog {
        width: 50;
        height: auto;
        border: thick #32416a;
        background: #0f1525;
        padding: 1 2;
    }
    #title {
        text-align: center;
        text-style: bold;
        color: #8fb0ee;
        margin-bottom: 1;
    }
    #preset-table { height: auto; max-height: 12; }
    #custom-container {
        height: auto;
        margin-top: 1;
        padding: 1;
        border: solid #32416a;
        display: none;
    }
    #custom-container.visible { display: block; }
    .date-row { height: 3; margin-bottom: 1; }
    .date-label { width: 12; padding-top: 1; }
    .date-input { width: 1fr; }
    #buttons { margin-top: 1; height: auto; }
    #buttons Button { margin-right: 1; }
    #hint { text-align: center; color: #788bc9; text-style: italic; margin-top: 1; }
    #current { text-align: center; color: #54efae; margin-bottom: 1; }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("enter", "select", "Select"),
    ]

    def __init__(self, current: Optional[DateRange] = None):
        super().__init__()
        self.current = current or today()
        self.selected_preset = None
        self.custom_start = None
        self.custom_end = None

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Static("Select Date Range", id="title")
            yield Static(f"Current: {self.current}", id="current")
            yield DataTable(id="preset-table")
            with Container(id="custom-container"):
                with Horizontal(classes="date-row"):
                    yield Static("Start Date:", classes="date-label")
                    yield Input(
                        placeholder="YYYY-MM-DD",
                        id="start-input",
                        classes="date-input",
                        value=str(date.today() - timedelta(days=7))
                    )
                with Horizontal(classes="date-row"):
                    yield Static("End Date:", classes="date-label")
                    yield Input(
                        placeholder="YYYY-MM-DD",
                        id="end-input",
                        classes="date-input",
                        value=str(date.today())
                    )
                with Horizontal(id="buttons"):
                    yield Button("Apply", variant="primary", id="apply-btn")
                    yield Button("Cancel", id="cancel-custom-btn")
            yield Static("↑↓ Navigate  Enter Select  Esc Cancel", id="hint")

    def on_mount(self) -> None:
        table = self.query_one("#preset-table", DataTable)
        table.add_columns("", "Range")
        table.cursor_type = "row"
        table.zebra_stripes = True
        for preset_id, label, _ in PRESETS:
            icon = "📅" if preset_id != "custom" else "✏️"
            table.add_row(icon, label)
        table.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self._handle_selection()

    def action_select(self) -> None:
        self._handle_selection()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def _handle_selection(self) -> None:
        table = self.query_one("#preset-table", DataTable)
        idx = table.cursor_row
        if idx is None or idx >= len(PRESETS):
            return

        preset_id, label, factory = PRESETS[idx]
        if preset_id == "custom":
            self._show_custom()
        else:
            self.dismiss(factory())

    def _show_custom(self) -> None:
        container = self.query_one("#custom-container")
        container.add_class("visible")
        self.query_one("#start-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "apply-btn":
            self._apply_custom()
        elif event.button.id == "cancel-custom-btn":
            container = self.query_one("#custom-container")
            container.remove_class("visible")
            self.query_one("#preset-table", DataTable).focus()

    def _apply_custom(self) -> None:
        start_str = self.query_one("#start-input", Input).value
        end_str = self.query_one("#end-input", Input).value
        try:
            start = datetime.strptime(start_str, "%Y-%m-%d").date()
            end = datetime.strptime(end_str, "%Y-%m-%d").date()
            if start > end:
                start, end = end, start
            self.dismiss(DateRange(start, end, "Custom"))
        except ValueError:
            pass  # Invalid date format, ignore
