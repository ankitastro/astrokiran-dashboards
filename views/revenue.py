"""
Revenue Metrics View (BD-1.0)
Subtasks: BD-1.1 to BD-1.5
- Total Add Cash amount
- Total Promotions Amount
- Total Consultations Amount
- Total Astrologer Share
- Total Company Share
All support hourly/date range filtering.
"""

from typing import List
from views.base import BaseView, TableConfig, ContainerConfig
from db import execute_query, execute_single
from fmt import colorize, fmt_currency, pad, GREEN


# --- Placeholder Queries ---

REVENUE_SUMMARY_QUERY = """SELECT NULL;"""  # TODO: Add Cash, Promotions, Consultations, Astrologer Share, Company Share


# --- Data Fetching (stateless) ---

def fetch_revenue_summary(start_date=None, end_date=None) -> tuple:
    """Fetch revenue summary metrics."""
    # TODO: Implement with date filtering
    return (0, 0, 0, 0, 0)


# --- Row Formatting (stateless) ---

def format_summary(data: tuple) -> tuple:
    """Format revenue summary row."""
    add_cash, promotions, consultations, astro_share, company_share = data
    return (
        pad(fmt_currency(float(add_cash))),
        pad(fmt_currency(float(promotions))),
        pad(fmt_currency(float(consultations))),
        pad(fmt_currency(float(astro_share))),
        pad(colorize(fmt_currency(float(company_share)), GREEN))
    )


# --- View Class ---

class RevenueView(BaseView):
    """Revenue Metrics Dashboard (BD-1.0)"""

    name = "Revenue"
    view_id = "revenue"
    icon = "₹"

    def get_containers(self) -> List[ContainerConfig]:
        return [
            ContainerConfig("revenue-container", "REVENUE METRICS", [
                TableConfig("revenue-table", [
                    "Add Cash",        # BD-1.1
                    "Promotions",      # BD-1.2
                    "Consultations",   # BD-1.3
                    "Astrologer Share", # BD-1.4
                    "Company Share"    # BD-1.5
                ])
            ])
        ]

    def fetch_data(self, **kwargs) -> dict:
        return {
            'summary': fetch_revenue_summary(
                kwargs.get('start_date'),
                kwargs.get('end_date')
            )
        }

    def format_rows(self, data: dict) -> dict:
        return {
            'revenue-table': [format_summary(data['summary'])]
        }
