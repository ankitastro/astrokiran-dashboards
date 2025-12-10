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

from datetime import date
from typing import List
from views.base import BaseView, TableConfig, ContainerConfig
from db import execute_single
from queries import REVENUE_SUMMARY_QUERY
from fmt import colorize, fmt_currency, fmt_number, pad, GREEN


# --- Data Fetching (stateless) ---

def fetch_revenue_summary(start_date=None, end_date=None) -> tuple:
    """Fetch revenue summary metrics."""
    if start_date is None:
        start_date = date.today()
    if end_date is None:
        end_date = date.today()
    # Query needs: start, end repeated 8 times (for each subquery)
    params = (start_date, end_date) * 8
    return execute_single(REVENUE_SUMMARY_QUERY, params) or (0, 0, 0, 0, 0, 0, 0, 0)


# --- Row Formatting (stateless) ---

def format_amount_row(data: tuple) -> tuple:
    """Format amounts row."""
    add_cash_amt, add_cash_cnt, promo_amt, promo_cnt, consult_amt, consult_cnt, astro_share, company_share = data
    return (
        "Amount",
        pad(fmt_currency(float(add_cash_amt))),
        pad(fmt_currency(float(promo_amt))),
        pad(fmt_currency(float(consult_amt))),
        pad(fmt_currency(float(astro_share))),
        pad(colorize(fmt_currency(float(company_share)), GREEN))
    )


def format_count_row(data: tuple) -> tuple:
    """Format counts row."""
    add_cash_amt, add_cash_cnt, promo_amt, promo_cnt, consult_amt, consult_cnt, astro_share, company_share = data
    return (
        "Count",
        pad(fmt_number(int(add_cash_cnt))),
        pad(fmt_number(int(promo_cnt))),
        pad(fmt_number(int(consult_cnt))),
        pad("-"),
        pad("-")
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
                    "",                # Row label
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
            'revenue-table': [
                format_amount_row(data['summary']),
                format_count_row(data['summary'])
            ]
        }
