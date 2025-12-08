"""
User Metrics View (BD-2.0)
Subtasks: BD-2.1 to BD-2.3
- ARPU (Average Revenue Per User)
- Number of Registrations
- Number of Conversions
All support hourly/date range filtering.
"""

from typing import List
from views.base import BaseView, TableConfig, ContainerConfig
from db import execute_query, execute_single
from fmt import colorize, fmt_currency, fmt_number, pad, GREEN


# --- Placeholder Queries ---

USER_METRICS_QUERY = """SELECT NULL;"""  # TODO: ARPU, Registrations, Conversions


# --- Data Fetching (stateless) ---

def fetch_user_metrics(start_date=None, end_date=None) -> tuple:
    """Fetch user metrics."""
    # TODO: Implement with date filtering
    return (0, 0, 0)


# --- Row Formatting (stateless) ---

def format_metrics(data: tuple) -> tuple:
    """Format user metrics row."""
    arpu, registrations, conversions = data
    return (
        pad(fmt_currency(float(arpu))),
        pad(fmt_number(int(registrations))),
        pad(colorize(fmt_number(int(conversions)), GREEN))
    )


# --- View Class ---

class UsersView(BaseView):
    """User Metrics Dashboard (BD-2.0)"""

    name = "Users"
    view_id = "users"
    icon = "U"

    def get_containers(self) -> List[ContainerConfig]:
        return [
            ContainerConfig("users-container", "USER METRICS", [
                TableConfig("users-table", [
                    "ARPU",          # BD-2.1
                    "Registrations", # BD-2.2
                    "Conversions"    # BD-2.3
                ])
            ])
        ]

    def fetch_data(self, **kwargs) -> dict:
        return {
            'metrics': fetch_user_metrics(
                kwargs.get('start_date'),
                kwargs.get('end_date')
            )
        }

    def format_rows(self, data: dict) -> dict:
        return {
            'users-table': [format_metrics(data['metrics'])]
        }
