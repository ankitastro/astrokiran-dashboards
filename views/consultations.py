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


def fmt_duration(minutes: float) -> str:
    """Format duration in minutes to Xm Ys format."""
    if minutes == 0:
        return "-"
    mins = int(minutes)
    secs = int((minutes - mins) * 60)
    if mins > 0 and secs > 0:
        return f"{mins}m{secs}s"
    elif mins > 0:
        return f"{mins}m"
    return f"{secs}s"


def format_astrologer_row(row: tuple) -> tuple:
    """Format astrologer row."""
    (guide_id, name,
     chat_count, chat_amount, chat_avg_earn, chat_total, chat_mean,
     call_count, call_amount, call_avg_earn, call_total, call_mean) = row
    return (
        str(guide_id),
        name,
        pad(fmt_number(int(chat_count))),
        pad(fmt_currency(float(chat_amount))),
        pad(fmt_currency(float(chat_avg_earn))),
        pad(fmt_duration(float(chat_total))),
        pad(fmt_duration(float(chat_mean))),
        pad(fmt_number(int(call_count))),
        pad(fmt_currency(float(call_amount))),
        pad(fmt_currency(float(call_avg_earn))),
        pad(fmt_duration(float(call_total))),
        pad(fmt_duration(float(call_mean)))
    )


def format_totals_row(data: list) -> tuple:
    """Format totals row from all astrologer data."""
    if not data:
        return tuple()
    # Sum up totals
    chat_count = sum(int(r[2]) for r in data)
    chat_amount = sum(float(r[3]) for r in data)
    chat_total_dur = sum(float(r[5]) for r in data)
    call_count = sum(int(r[7]) for r in data)
    call_amount = sum(float(r[8]) for r in data)
    call_total_dur = sum(float(r[10]) for r in data)
    # Calculate averages
    chat_avg = chat_amount / chat_count if chat_count > 0 else 0
    chat_mean_dur = chat_total_dur / chat_count if chat_count > 0 else 0
    call_avg = call_amount / call_count if call_count > 0 else 0
    call_mean_dur = call_total_dur / call_count if call_count > 0 else 0
    return (
        "",
        colorize("TOTAL", GREEN),
        pad(colorize(fmt_number(chat_count), GREEN)),
        pad(colorize(fmt_currency(chat_amount), GREEN)),
        pad(colorize(fmt_currency(chat_avg), GREEN)),
        pad(colorize(fmt_duration(chat_total_dur), GREEN)),
        pad(colorize(fmt_duration(chat_mean_dur), GREEN)),
        pad(colorize(fmt_number(call_count), GREEN)),
        pad(colorize(fmt_currency(call_amount), GREEN)),
        pad(colorize(fmt_currency(call_avg), GREEN)),
        pad(colorize(fmt_duration(call_total_dur), GREEN)),
        pad(colorize(fmt_duration(call_mean_dur), GREEN))
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
                    "ID",
                    "Astrologer",
                    "Chat#",
                    "Chat₹",
                    "ChatAvg₹",
                    "ChatTot",
                    "ChatAvg",
                    "Call#",
                    "Call₹",
                    "CallAvg₹",
                    "CallTot",
                    "CallAvg"
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
        astro_rows = [format_astrologer_row(r) for r in data['by_astrologer']]
        if data['by_astrologer']:
            astro_rows.append(format_totals_row(data['by_astrologer']))
        return {
            'consult-summary-table': format_summary_rows(data['summary']),
            'consult-astrologer-table': astro_rows
        }
