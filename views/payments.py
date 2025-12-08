"""
Payment Metrics View (BD-4.0)
Subtasks: BD-4.1 to BD-4.4
- Number of Payments
- Amount of Payments
- Success Rate of Payments
- Success Rate by Payment Mode (UPI, Debit, Credit, Net Banking, Wallet)
All support hourly/date range filtering.
"""

from typing import List
from views.base import BaseView, TableConfig, ContainerConfig
from db import execute_query, execute_single
from fmt import colorize, pick_color, fmt_currency, fmt_percent, fmt_number, pad, GREEN, RED


# --- Placeholder Queries ---

PAYMENT_SUMMARY_QUERY = """SELECT NULL;"""  # Count, Amount, Success Rate
PAYMENT_BY_MODE_QUERY = """SELECT NULL;"""  # UPI, Debit, Credit, Net Banking, Wallet


# --- Data Fetching (stateless) ---

def fetch_payment_summary(start_date=None, end_date=None) -> tuple:
    """Fetch payment summary metrics."""
    # TODO: Implement with date filtering
    # Returns: (count, amount, success_rate)
    return (0, 0, 0)


def fetch_by_mode(start_date=None, end_date=None) -> list:
    """Fetch success rate by payment mode."""
    # TODO: Implement with date filtering
    # Returns: [(mode, count, amount, success_rate), ...]
    return []


# --- Row Formatting (stateless) ---

def format_summary(data: tuple) -> tuple:
    """Format payment summary row."""
    count, amount, success_rate = data
    rate_color = pick_color(float(success_rate), 90, 95)
    return (
        pad(fmt_number(int(count))),
        pad(fmt_currency(float(amount))),
        pad(colorize(fmt_percent(float(success_rate)), rate_color))
    )


def format_mode_row(row: tuple) -> tuple:
    """Format payment by mode row."""
    mode, count, amount, success_rate = row
    rate_color = pick_color(float(success_rate), 90, 95)
    return (
        mode,
        fmt_number(int(count)),
        fmt_currency(float(amount)),
        colorize(fmt_percent(float(success_rate)), rate_color)
    )


# --- View Class ---

class PaymentsView(BaseView):
    """Payment Metrics Dashboard (BD-4.0)"""

    name = "Payments"
    view_id = "payments"
    icon = "P"

    def get_containers(self) -> List[ContainerConfig]:
        return [
            ContainerConfig("payment-summary-container", "PAYMENT SUMMARY", [
                TableConfig("payment-summary-table", [
                    "Count",        # BD-4.1
                    "Amount",       # BD-4.2
                    "Success Rate"  # BD-4.3
                ])
            ]),
            ContainerConfig("payment-mode-container", "BY PAYMENT MODE", [
                TableConfig("payment-mode-table", [
                    "Mode",         # UPI, Debit, Credit, Net Banking, Wallet
                    "Count",
                    "Amount",
                    "Success Rate"  # BD-4.4
                ], cursor=True)
            ])
        ]

    def fetch_data(self, **kwargs) -> dict:
        start = kwargs.get('start_date')
        end = kwargs.get('end_date')
        return {
            'summary': fetch_payment_summary(start, end),
            'by_mode': fetch_by_mode(start, end)
        }

    def format_rows(self, data: dict) -> dict:
        return {
            'payment-summary-table': [format_summary(data['summary'])],
            'payment-mode-table': [format_mode_row(r) for r in data['by_mode']]
        }
