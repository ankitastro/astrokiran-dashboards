"""
Astrologer Availability Metrics View (BD-9.0)
Subtasks: BD-9.1 to BD-9.2
- Astrologer vs Online Time
- Live Astrologers count
All support hourly/date range filtering.
"""

from datetime import date
from typing import List
from views.base import BaseView, TableConfig, ContainerConfig
from db import execute_query, execute_scalar
from queries import ASTROLOGER_AVAILABILITY_QUERY, LIVE_ASTROLOGERS_QUERY
from fmt import colorize, fmt_number, pad, GREEN


# --- Data Fetching (stateless) ---

def fetch_live_count() -> int:
    """Fetch current live astrologers count."""
    result = execute_scalar(LIVE_ASTROLOGERS_QUERY, ())
    return result or 0


def fetch_online_time(start_date=None, end_date=None) -> list:
    """Fetch astrologer online time from audit logs."""
    if start_date is None:
        start_date = date.today()
    if end_date is None:
        end_date = date.today()
    return execute_query(ASTROLOGER_AVAILABILITY_QUERY, (start_date, end_date))


# --- Row Formatting (stateless) ---

def format_summary(live_count: int) -> tuple:
    """Format availability summary row."""
    return (pad(colorize(fmt_number(live_count), GREEN)),)


def format_date_range(first_date, last_date) -> str:
    """Format date range as string."""
    if first_date == last_date:
        return first_date.strftime('%b %d')
    return f"{first_date.strftime('%b %d')} - {last_date.strftime('%b %d')}"


def format_online_time_row(row: tuple) -> tuple:
    """Format astrologer online time row."""
    name, first_online, last_online, total_minutes = row
    hours = int(total_minutes) // 60
    minutes = int(total_minutes) % 60
    time_str = f"{hours}h {minutes}m"
    return (
        name,
        pad(format_date_range(first_online, last_online)),
        pad(time_str)
    )


# --- View Class ---

class AstrologerAvailabilityView(BaseView):
    """Astrologer Availability Metrics Dashboard (BD-9.0)"""

    name = "Astrologer Availability"
    view_id = "astro-avail"
    icon = "V"

    def get_containers(self) -> List[ContainerConfig]:
        return [
            ContainerConfig("avail-summary-container", "LIVE NOW", [
                TableConfig("avail-summary-table", [
                    "Live Astrologers"  # BD-9.2
                ])
            ]),
            ContainerConfig("avail-online-container", "ONLINE TIME", [
                TableConfig("avail-online-table", [
                    "Astrologer",
                    "Period",       # Date range
                    "Online Time"   # BD-9.1
                ], cursor=True)
            ])
        ]

    def fetch_data(self, **kwargs) -> dict:
        return {
            'live_count': fetch_live_count(),
            'online_time': fetch_online_time(
                kwargs.get('start_date'),
                kwargs.get('end_date')
            )
        }

    def format_rows(self, data: dict) -> dict:
        return {
            'avail-summary-table': [format_summary(data['live_count'])],
            'avail-online-table': [format_online_time_row(r) for r in data['online_time']]
        }
