"""
Consultation Metrics View (BD-3.0)
Subtasks: BD-3.1 to BD-3.5
- All consultations (number + amount)
- Chat consultations (number + amount)
- Call consultations (number + amount)
- Per-astrologer breakdown
All support hourly/date range filtering.
"""

from datetime import date
from typing import List
from views.base import BaseView, TableConfig, ContainerConfig
from db import execute_single, execute_query
from queries import CONSULTATION_SUMMARY_QUERY, CONSULTATION_BY_ASTROLOGER_QUERY
from fmt import colorize, fmt_currency, fmt_number, pad, GREEN


# --- Data Fetching (stateless) ---

def fetch_consultation_summary(start_date=None, end_date=None) -> tuple:
    """Fetch consultation summary metrics."""
    if start_date is None:
        start_date = date.today()
    if end_date is None:
        end_date = date.today()
    # Query needs: start, end repeated 6 times (for each subquery)
    params = (start_date, end_date) * 6
    return execute_single(CONSULTATION_SUMMARY_QUERY, params) or (0, 0, 0, 0, 0, 0)


def fetch_by_astrologer(start_date=None, end_date=None) -> list:
    """Fetch consultations by astrologer."""
    if start_date is None:
        start_date = date.today()
    if end_date is None:
        end_date = date.today()
    return execute_query(CONSULTATION_BY_ASTROLOGER_QUERY, (start_date, end_date))


# --- Row Formatting (stateless) ---

def format_summary_rows(data: tuple) -> list:
    """Format consultation summary rows."""
    all_cnt, all_amt, chat_cnt, chat_amt, call_cnt, call_amt = data
    return [
        ("All", pad(fmt_number(int(all_cnt))), pad(fmt_currency(float(all_amt)))),
        ("Chat", pad(fmt_number(int(chat_cnt))), pad(fmt_currency(float(chat_amt)))),
        ("Call", pad(fmt_number(int(call_cnt))), pad(fmt_currency(float(call_amt)))),
    ]


def format_astrologer_row(row: tuple) -> tuple:
    """Format astrologer row."""
    name, mode, count, amount = row
    mode_display = "Chat" if mode == "chat" else "Call"
    return (
        name,
        mode_display,
        pad(fmt_number(int(count))),
        pad(colorize(fmt_currency(float(amount)), GREEN))
    )


# --- View Class ---

class ConsultationsView(BaseView):
    """Consultation Metrics Dashboard (BD-3.0)"""

    name = "Consultations"
    view_id = "consultations"
    icon = "C"

    def get_containers(self) -> List[ContainerConfig]:
        return [
            ContainerConfig("consult-summary-container", "CONSULTATION SUMMARY", [
                TableConfig("consult-summary-table", [
                    "Type",
                    "Count",
                    "Amount"
                ])
            ]),
            ContainerConfig("consult-astrologer-container", "BY ASTROLOGER", [
                TableConfig("consult-astrologer-table", [
                    "Astrologer",
                    "Mode",
                    "Count",
                    "Amount"
                ], cursor=True)
            ])
        ]

    def fetch_data(self, **kwargs) -> dict:
        start = kwargs.get('start_date')
        end = kwargs.get('end_date')
        return {
            'summary': fetch_consultation_summary(start, end),
            'by_astrologer': fetch_by_astrologer(start, end)
        }

    def format_rows(self, data: dict) -> dict:
        return {
            'consult-summary-table': format_summary_rows(data['summary']),
            'consult-astrologer-table': [format_astrologer_row(r) for r in data['by_astrologer']]
        }
