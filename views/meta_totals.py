"""
Meta Marketing Totals View (BD-7.0)
Subtasks: BD-7.1 to BD-7.6
Aggregated metrics across all campaigns:
- Total Marketing Budget
- Total Budget Per Day
- Total Marketing Spends
- Total Registered Users
- Total Converted Users
- Overall CAC
"""

from typing import List
from views.base import BaseView, TableConfig, ContainerConfig
from db import execute_single
from fmt import colorize, pick_color, fmt_currency, fmt_number, pad, GREEN


# --- Placeholder Queries ---

META_TOTALS_QUERY = """SELECT NULL;"""  # Aggregated campaign totals


# --- Data Fetching (stateless) ---

def fetch_totals() -> tuple:
    """Fetch aggregated Meta marketing totals."""
    # TODO: Implement - aggregate from campaigns or Meta API
    # Returns: (total_budget, daily_budget, spends, registered, converted, cac)
    return (0, 0, 0, 0, 0, 0)


# --- Row Formatting (stateless) ---

def format_totals(data: tuple) -> tuple:
    """Format totals row."""
    total_budget, daily_budget, spends, registered, converted, cac = data

    cac_color = pick_color(float(cac), 50, 100, True) if cac > 0 else None
    cac_str = colorize(fmt_currency(float(cac)), cac_color) if cac_color else fmt_currency(float(cac))

    return (
        pad(fmt_currency(float(total_budget))),  # BD-7.1
        pad(fmt_currency(float(daily_budget))),  # BD-7.2
        pad(fmt_currency(float(spends))),        # BD-7.3
        pad(fmt_number(int(registered))),        # BD-7.4
        pad(colorize(fmt_number(int(converted)), GREEN)),  # BD-7.5
        pad(cac_str)                             # BD-7.6
    )


# --- View Class ---

class MetaTotalsView(BaseView):
    """Meta Marketing Totals Dashboard (BD-7.0)"""

    name = "Meta Totals"
    view_id = "meta-totals"
    icon = "T"

    def get_containers(self) -> List[ContainerConfig]:
        return [
            ContainerConfig("meta-totals-container", "META MARKETING TOTALS", [
                TableConfig("meta-totals-table", [
                    "Total Budget",    # BD-7.1
                    "Budget/Day",      # BD-7.2
                    "Total Spends",    # BD-7.3
                    "Registered",      # BD-7.4
                    "Converted",       # BD-7.5
                    "Overall CAC"      # BD-7.6
                ])
            ])
        ]

    def fetch_data(self, **kwargs) -> dict:
        return {
            'totals': fetch_totals()
        }

    def format_rows(self, data: dict) -> dict:
        return {
            'meta-totals-table': [format_totals(data['totals'])]
        }
