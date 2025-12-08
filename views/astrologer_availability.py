"""
Astrologer Availability Metrics View (BD-9.0)
Subtasks: BD-9.1 to BD-9.2
- Astrologer vs Online Time
- Live Astrologers count
All support hourly/date range filtering.
"""

from typing import List
from views.base import BaseView, TableConfig, ContainerConfig
from db import execute_query, execute_single
from fmt import colorize, fmt_number, pad, GREEN


# --- Placeholder Queries ---

LIVE_COUNT_QUERY = """SELECT NULL;"""  # Current live astrologers
ONLINE_TIME_QUERY = """SELECT NULL;"""  # Per-astrologer online time


# --- Data Fetching (stateless) ---

def fetch_live_count() -> int:
    """Fetch current live astrologers count."""
    # TODO: Implement
    return 0


def fetch_online_time(start_date=None, end_date=None) -> list:
    """Fetch astrologer online time."""
    # TODO: Implement with date filtering
    # Returns: [(name, online_hours, online_minutes), ...]
    return []


# --- Row Formatting (stateless) ---

def format_summary(live_count: int) -> tuple:
    """Format availability summary row."""
    return (pad(colorize(fmt_number(live_count), GREEN)),)


def format_online_time_row(row: tuple) -> tuple:
    """Format astrologer online time row."""
    name, hours, minutes = row
    time_str = f"{int(hours)}h {int(minutes)}m"
    return (name, time_str)


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
                    "Online Time"  # BD-9.1
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
