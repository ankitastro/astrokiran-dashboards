"""
Consultation Metrics View (BD-3.0)
Subtasks: BD-3.1 to BD-3.5
- All consultations (number + amount)
- Astrology consultations (number + amount)
- Palmist consultations (number + amount)
- Chat consultations (number + amount)
- Call consultations (number + amount)
All support hourly/date range filtering.
"""

from typing import List
from views.base import BaseView, TableConfig, ContainerConfig
from db import execute_query, execute_single
from fmt import colorize, fmt_currency, fmt_number, pad, GREEN


# --- Placeholder Queries ---

CONSULTATION_BY_TYPE_QUERY = """SELECT NULL;"""  # All, Astrology, Palmist
CONSULTATION_BY_CHANNEL_QUERY = """SELECT NULL;"""  # Chat, Call


# --- Data Fetching (stateless) ---

def fetch_by_type(start_date=None, end_date=None) -> list:
    """Fetch consultations by type (All/Astrology/Palmist)."""
    # TODO: Implement with date filtering
    # Returns: [(type, count, amount), ...]
    return []


def fetch_by_channel(start_date=None, end_date=None) -> list:
    """Fetch consultations by channel (Chat/Call)."""
    # TODO: Implement with date filtering
    # Returns: [(channel, count, amount), ...]
    return []


# --- Row Formatting (stateless) ---

def format_type_row(row: tuple) -> tuple:
    """Format consultation by type row."""
    ctype, count, amount = row
    return (ctype, fmt_number(int(count)), fmt_currency(float(amount)))


def format_channel_row(row: tuple) -> tuple:
    """Format consultation by channel row."""
    channel, count, amount = row
    return (channel, fmt_number(int(count)), fmt_currency(float(amount)))


# --- View Class ---

class ConsultationsView(BaseView):
    """Consultation Metrics Dashboard (BD-3.0)"""

    name = "Consultations"
    view_id = "consultations"
    icon = "C"

    def get_containers(self) -> List[ContainerConfig]:
        return [
            ContainerConfig("consult-type-container", "BY TYPE", [
                TableConfig("consult-type-table", [
                    "Type",   # All / Astrology / Palmist
                    "Count",  # BD-3.1, BD-3.2, BD-3.3
                    "Amount"
                ])
            ]),
            ContainerConfig("consult-channel-container", "BY CHANNEL", [
                TableConfig("consult-channel-table", [
                    "Channel",  # Chat / Call
                    "Count",    # BD-3.4, BD-3.5
                    "Amount"
                ])
            ])
        ]

    def fetch_data(self, **kwargs) -> dict:
        start = kwargs.get('start_date')
        end = kwargs.get('end_date')
        return {
            'by_type': fetch_by_type(start, end),
            'by_channel': fetch_by_channel(start, end)
        }

    def format_rows(self, data: dict) -> dict:
        return {
            'consult-type-table': [format_type_row(r) for r in data['by_type']],
            'consult-channel-table': [format_channel_row(r) for r in data['by_channel']]
        }
