"""
Astrologer Performance Metrics View (BD-8.0)
Subtasks: BD-8.1 to BD-8.4
Per-astrologer metrics:
- Number of Consultations by Chat
- Amount of Consultations by Chat
- Number of Consultations by Call
- Amount of Consultations by Call
All support hourly/date range filtering.
"""

from datetime import date
from typing import List
from views.base import BaseView, TableConfig, ContainerConfig
from db import execute_query
from queries import ASTROLOGER_PERFORMANCE_QUERY
from fmt import colorize, fmt_currency, fmt_number, pad, GREEN


# --- Data Fetching (stateless) ---

def fetch_performance(start_date=None, end_date=None) -> list:
    """Fetch astrologer performance metrics."""
    if start_date is None:
        start_date = date.today()
    if end_date is None:
        end_date = date.today()
    return execute_query(ASTROLOGER_PERFORMANCE_QUERY, (start_date, end_date))


# --- Row Formatting (stateless) ---

def format_performance_row(row: tuple) -> tuple:
    """Format astrologer performance row."""
    name, chat_count, chat_amount, call_count, call_amount = row
    total_amount = float(chat_amount) + float(call_amount)
    return (
        name,
        pad(fmt_number(int(chat_count))),           # BD-8.1
        pad(fmt_currency(float(chat_amount))),      # BD-8.2
        pad(fmt_number(int(call_count))),           # BD-8.3
        pad(fmt_currency(float(call_amount))),      # BD-8.4
        pad(colorize(fmt_currency(total_amount), GREEN))
    )


# --- View Class ---

class AstrologerPerformanceView(BaseView):
    """Astrologer Performance Metrics Dashboard (BD-8.0)"""

    name = "Astrologer Performance"
    view_id = "astro-perf"
    icon = "A"

    def get_containers(self) -> List[ContainerConfig]:
        return [
            ContainerConfig("astro-perf-container", "ASTROLOGER PERFORMANCE", [
                TableConfig("astro-perf-table", [
                    "Astrologer",
                    "Chat #",      # BD-8.1
                    "Chat Rs.",    # BD-8.2
                    "Call #",      # BD-8.3
                    "Call Rs.",    # BD-8.4
                    "Total Rs."
                ], cursor=True)
            ])
        ]

    def fetch_data(self, **kwargs) -> dict:
        return {
            'performance': fetch_performance(
                kwargs.get('start_date'),
                kwargs.get('end_date')
            )
        }

    def format_rows(self, data: dict) -> dict:
        return {
            'astro-perf-table': [format_performance_row(r) for r in data['performance']]
        }
