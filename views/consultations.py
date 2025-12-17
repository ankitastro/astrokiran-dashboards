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
from queries import (
    CONSULTATION_SUMMARY_QUERY, CONSULTATION_BY_ASTROLOGER_QUERY,
    CONSULTATION_REQUESTS_QUERY, CONSULTATION_PERFORMANCE_QUERY
)
from fmt import colorize, fmt_currency, fmt_number, fmt_percent, pick_color, pad, GREEN, RED, YELLOW


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


def fetch_requests(start_date=None, end_date=None) -> list:
    """Fetch consultation requests by astrologer."""
    if start_date is None:
        start_date = date.today()
    if end_date is None:
        end_date = date.today()
    return execute_query(CONSULTATION_REQUESTS_QUERY, (start_date, end_date))


def fetch_connection_performance(start_date=None, end_date=None) -> tuple:
    """Fetch connection performance metrics."""
    if start_date is None:
        start_date = date(2025, 12, 5)
    if end_date is None:
        end_date = date.today()
    return execute_single(CONSULTATION_PERFORMANCE_QUERY, (start_date, end_date)) or (0, 0, 0, 0, 0, 0, 0, 0)


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


def format_request_row(row: tuple) -> tuple:
    """Format consultation request row."""
    guide_id, name, total, accepted, rejected, timed_out, completed = row
    # Acceptance rate = accepted / total * 100
    accept_rate = (accepted / total * 100) if total > 0 else 0
    rate_color = pick_color(accept_rate, 50, 80)
    return (
        str(guide_id),
        name or "-",
        pad(fmt_number(total)),
        pad(colorize(fmt_number(accepted), GREEN)),
        pad(colorize(fmt_number(rejected), RED)),
        pad(fmt_number(timed_out)),
        pad(fmt_number(completed)),
        pad(colorize(fmt_percent(accept_rate), rate_color))
    )


def format_performance_rows(data: tuple) -> list:
    """Format connection performance metrics as rows."""
    (total_attempts, total_successes, success_rate, successful_sessions,
     avg_attempts, first_try_success, first_try_rate, avg_minutes) = data

    # Row 1: Overall stats
    success_color = pick_color(float(success_rate or 0), 40, 60)
    row1 = (
        "Overall",
        pad(fmt_number(int(total_attempts or 0))),
        pad(colorize(fmt_number(int(total_successes or 0)), GREEN)),
        pad(colorize(fmt_percent(float(success_rate or 0)), success_color)),
        "-",
        "-",
        "-"
    )

    # Row 2: Session stats
    first_try_color = pick_color(float(first_try_rate or 0), 50, 70)
    attempts_color = pick_color(float(avg_attempts or 0), 3, 2, reverse=True)
    row2 = (
        "Sessions",
        pad(fmt_number(int(successful_sessions or 0))),
        pad(colorize(fmt_number(int(first_try_success or 0)), GREEN)),
        pad(colorize(fmt_percent(float(first_try_rate or 0)), first_try_color)),
        pad(colorize(f"{float(avg_attempts or 0):.1f}", attempts_color)),
        pad(f"{float(avg_minutes or 0):.1f}m"),
        "-"
    )

    return [row1, row2]


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
            ContainerConfig("consult-perf-container", "CONNECTION PERFORMANCE (Since Dec 5)", [
                TableConfig("consult-perf-table", [
                    "Metric",
                    "Attempts",
                    "Success",
                    "Rate",
                    "Avg Tries",
                    "Avg Time",
                    "-"
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
            ]),
            ContainerConfig("consult-requests-container", "REQUEST ACCEPTANCE", [
                TableConfig("consult-requests-table", [
                    "ID",
                    "Astrologer",
                    "Requests",
                    "Accepted",
                    "Rejected",
                    "Timeout",
                    "Completed",
                    "Accept%"
                ], cursor=True)
            ])
        ]

    def fetch_data(self, **kwargs) -> dict:
        start = kwargs.get('start_date')
        end = kwargs.get('end_date')
        return {
            'summary': fetch_consultation_summary(start, end),
            'performance': fetch_connection_performance(start, end),
            'by_astrologer': fetch_by_astrologer(start, end),
            'requests': fetch_requests(start, end)
        }

    def format_rows(self, data: dict) -> dict:
        astro_rows = [format_astrologer_row(r) for r in data['by_astrologer']]
        if data['by_astrologer']:
            astro_rows.append(format_totals_row(data['by_astrologer']))
        return {
            'consult-summary-table': format_summary_rows(data['summary']),
            'consult-perf-table': format_performance_rows(data['performance']),
            'consult-astrologer-table': astro_rows,
            'consult-requests-table': [format_request_row(r) for r in data['requests']]
        }
