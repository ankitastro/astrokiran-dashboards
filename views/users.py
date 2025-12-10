"""
User Metrics View (BD-2.0)
Subtasks: BD-2.1 to BD-2.3
- ARPU (Average Revenue Per User) - Lifetime
- Number of Registrations - Date range
- Number of Conversions - Date range (first payment)
"""

from datetime import date
from typing import List
from views.base import BaseView, TableConfig, ContainerConfig
from db import execute_single
from queries import USER_METRICS_QUERY
from fmt import colorize, fmt_currency, fmt_number, pad, GREEN


# --- Data Fetching (stateless) ---

def fetch_user_metrics(start_date=None, end_date=None) -> tuple:
    """Fetch user metrics."""
    if start_date is None:
        start_date = date.today()
    if end_date is None:
        end_date = date.today()
    # Query needs: start, end for registrations + start, end for conversions
    params = (start_date, end_date, start_date, end_date)
    return execute_single(USER_METRICS_QUERY, params) or (0, 0, 0)


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
            ContainerConfig("user-metrics-container", "USER METRICS", [
                TableConfig("user-metrics-table", [
                    "ARPU (Lifetime)", # BD-2.1
                    "Registrations",   # BD-2.2
                    "Conversions"      # BD-2.3
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
            'user-metrics-table': [format_metrics(data['metrics'])]
        }
