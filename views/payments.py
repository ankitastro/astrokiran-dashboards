"""
Payment Metrics View (BD-4.0)
Subtasks: BD-4.1 to BD-4.4
- Number of Payments
- Amount of Payments
- Success Rate of Payments
- Success Rate by Payment Mode (UPI, Debit, Credit, Net Banking, Wallet)
All support hourly/date range filtering.
"""

from datetime import date
from typing import List
from views.base import BaseView, TableConfig, ContainerConfig
from db import execute_query, execute_single
from queries import PAYMENT_SUMMARY_QUERY, PAYMENT_BY_METHOD_QUERY
from fmt import colorize, pick_color, fmt_currency, fmt_percent, fmt_number, pad, GREEN, RED


# --- Data Fetching (stateless) ---

def fetch_payment_summary(start_date=None, end_date=None) -> tuple:
    """Fetch payment summary metrics."""
    if start_date is None:
        start_date = date.today()
    if end_date is None:
        end_date = date.today()
    # Query needs: start, end repeated 5 times (for each subquery)
    params = (start_date, end_date) * 5
    return execute_single(PAYMENT_SUMMARY_QUERY, params) or (0, 0, 0, 0, 0)


def fetch_by_method(start_date=None, end_date=None) -> list:
    """Fetch success rate by payment method."""
    if start_date is None:
        start_date = date.today()
    if end_date is None:
        end_date = date.today()
    return execute_query(PAYMENT_BY_METHOD_QUERY, (start_date, end_date))


# --- Row Formatting (stateless) ---

def format_summary(data: tuple) -> tuple:
    """Format payment summary row."""
    total, amount, successful, failed, pending = data
    # Calculate success rate: successful / (successful + failed)
    completed = int(successful) + int(failed)
    success_rate = (float(successful) / completed * 100) if completed > 0 else 0
    rate_color = pick_color(success_rate, 80, 95)
    return (
        pad(fmt_number(int(total))),
        pad(fmt_currency(float(amount))),
        pad(fmt_number(int(successful))),
        pad(fmt_number(int(failed))),
        pad(fmt_number(int(pending))),
        pad(colorize(fmt_percent(success_rate), rate_color))
    )


def format_method_row(row: tuple) -> tuple:
    """Format payment by method row."""
    method, total, successful, failed, amount = row
    # Calculate success rate: successful / (successful + failed)
    completed = int(successful) + int(failed)
    success_rate = (float(successful) / completed * 100) if completed > 0 else 0
    rate_color = pick_color(success_rate, 80, 95)
    return (
        method,
        pad(fmt_number(int(total))),
        pad(fmt_currency(float(amount))),
        pad(colorize(fmt_percent(success_rate), rate_color))
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
                    "Total",        # BD-4.1
                    "Amount",       # BD-4.2
                    "Success",
                    "Failed",
                    "Pending",
                    "Success %"     # BD-4.3
                ])
            ]),
            ContainerConfig("payment-method-container", "BY PAYMENT METHOD", [
                TableConfig("payment-method-table", [
                    "Method",       # UPI, Debit, Credit, Net Banking, Wallet
                    "Count",
                    "Amount",
                    "Success %"     # BD-4.4
                ], cursor=True)
            ])
        ]

    def fetch_data(self, **kwargs) -> dict:
        start = kwargs.get('start_date')
        end = kwargs.get('end_date')
        return {
            'summary': fetch_payment_summary(start, end),
            'by_method': fetch_by_method(start, end)
        }

    def format_rows(self, data: dict) -> dict:
        return {
            'payment-summary-table': [format_summary(data['summary'])],
            'payment-method-table': [format_method_row(r) for r in data['by_method']]
        }
