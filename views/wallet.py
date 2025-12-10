"""
Wallet View - Database stats, KPIs, and user data.
All functions are stateless and under 20 lines.
"""

from typing import List
from views.base import BaseView, TableConfig, ContainerConfig
from db import execute_query, execute_single, execute_scalar
from queries import (
    DAILY_RECHARGE_QUERY, KPI_QUERY, DB_CONNECTIONS_QUERY,
    REPLICATION_STATUS_QUERY, WALLET_TRANSACTIONS_QUERY, WALLET_TRANSACTIONS_COUNT_QUERY
)
from fmt import (
    colorize, pick_color, fmt_currency, fmt_percent,
    fmt_number, fmt_bytes, fmt_duration, fmt_date, fmt_datetime, pad
)


# --- Data Fetching (stateless) ---

def fetch_db_stats() -> tuple:
    """Fetch database connection stats."""
    return execute_single(DB_CONNECTIONS_QUERY) or (0, 0, 0, 0, 0.0)


def fetch_kpis() -> tuple:
    """Fetch today's KPI metrics."""
    return execute_single(KPI_QUERY) or (0, 0, 0, 0)


def fetch_daily_recharges() -> list:
    """Fetch last 7 days of recharge data."""
    return execute_query(DAILY_RECHARGE_QUERY)


def fetch_replication() -> tuple:
    """Fetch replication status."""
    return execute_single(REPLICATION_STATUS_QUERY) or (False, 0, 0)


def fetch_transaction_count() -> int:
    """Fetch total transaction count."""
    return execute_scalar(WALLET_TRANSACTIONS_COUNT_QUERY) or 0


def fetch_transactions(limit: int, offset: int) -> list:
    """Fetch paginated wallet transactions."""
    return execute_query(WALLET_TRANSACTIONS_QUERY, (limit, offset))


# --- Row Formatting (stateless) ---

def format_db_stats(stats: tuple) -> tuple:
    """Format DB stats row."""
    total, max_c, active, idle, cache = stats
    pct = (total / max_c * 100) if max_c > 0 else 0
    return (
        pad(colorize(f"{total}/{max_c}", pick_color(pct, 80, 90, True)) + f" ({pct:.0f}%)"),
        pad(colorize(str(active), pick_color(active, 5, 10, True))),
        pad(str(idle)),
        pad(colorize(fmt_percent(cache or 0), pick_color(cache or 0, 85, 95)))
    )


def format_kpi(kpi: tuple) -> tuple:
    """Format KPI row."""
    recharge, virtual, revenue, spend = kpi
    return tuple(pad(fmt_currency(float(v))) for v in kpi)


def format_daily_count(day_data: tuple) -> str:
    """Format single day recharge count."""
    _, _, count, _ = day_data
    return pad(colorize(str(count), pick_color(count, 5, 10)))


def format_daily_amount(day_data: tuple) -> str:
    """Format single day recharge amount."""
    _, _, _, amount = day_data
    return pad(fmt_currency(float(amount), 0))


def format_daily_rows(data: list) -> tuple:
    """Format daily recharge rows (counts and amounts)."""
    counts = ["# Recharges"] + [format_daily_count(d) for d in data]
    amounts = ["Rs. Amount"] + [format_daily_amount(d) for d in data]
    while len(counts) < 8:
        counts.append(pad("-"))
        amounts.append(pad("-"))
    return tuple(counts), tuple(amounts)


def get_daily_headers(data: list) -> list:
    """Get column headers from daily recharge data."""
    headers = ["Metric"]
    for d in data:
        _, label, _, _ = d
        headers.append(label)
    while len(headers) < 8:
        headers.append("-")
    return headers


def format_replication(repl: tuple) -> tuple:
    """Format replication status row."""
    is_rep, wal_bytes, secs = repl
    wal_color = pick_color(wal_bytes, 1024, 1024*1024, True)
    return (
        pad(colorize(fmt_bytes(wal_bytes) + (" (synced)" if wal_bytes == 0 else ""), wal_color)),
        pad(fmt_duration(secs))
    )


def format_txn_type(txn_type: str) -> str:
    """Format transaction type with color."""
    if txn_type == 'ADD':
        return colorize(txn_type, "green")
    elif txn_type == 'SPENT':
        return colorize(txn_type, "red")
    elif txn_type == 'PROMOTION_GRANT':
        return colorize("PROMO", "yellow")
    return txn_type


def format_transaction(row: tuple) -> tuple:
    """Format single transaction row."""
    txn_id, user_id, user_name, txn_type, amount, real_delta, virtual_delta, comment, created_at = row

    # Format deltas with color
    real_str = fmt_currency(float(real_delta)) if real_delta else "-"
    if real_delta and float(real_delta) > 0:
        real_str = colorize(real_str, "green")
    elif real_delta and float(real_delta) < 0:
        real_str = colorize(real_str, "red")

    virtual_str = fmt_currency(float(virtual_delta)) if virtual_delta else "-"
    if virtual_delta and float(virtual_delta) > 0:
        virtual_str = colorize(virtual_str, "yellow")
    elif virtual_delta and float(virtual_delta) < 0:
        virtual_str = colorize(virtual_str, "red")

    # Truncate comment
    comment_str = (comment[:30] + "...") if comment and len(comment) > 30 else (comment or "-")

    return (
        str(user_id),
        user_name or "-",
        format_txn_type(txn_type),
        fmt_currency(float(amount)),
        real_str,
        virtual_str,
        comment_str,
        fmt_datetime(created_at) or "-"
    )


# --- View Class ---

class WalletView(BaseView):
    """Wallet dashboard view."""

    name = "Wallet Dashboard"
    view_id = "wallet"
    icon = "W"

    def get_containers(self) -> List[ContainerConfig]:
        return [
            ContainerConfig("db-stats-container", "DATABASE CONNECTION STATS", [
                TableConfig("db-stats-table", ["Connections", "Active", "Idle", "Cache Hit %"])
            ]),
            ContainerConfig("kpi-container", "TODAY'S WALLET METRICS", [
                TableConfig("kpi-table", ["Recharge", "Promo Cash", "Revenue", "Spend"])
            ]),
            ContainerConfig("daily-container", "DAILY RECHARGE (Last 7 Days)", [
                TableConfig("daily-table", ["Day", "Today", "Yesterday", "2d", "3d", "4d", "5d", "6d"])
            ]),
            ContainerConfig("txn-container", "WALLET TRANSACTIONS", [
                TableConfig("txn-table", ["User ID", "Name", "Type", "Amount", "Real", "Virtual", "Comment", "Time"], cursor=True)
            ])
        ]

    def fetch_data(self, page: int = 1, per_page: int = 100) -> dict:
        offset = (page - 1) * per_page
        return {
            'db_stats': fetch_db_stats(),
            'kpis': fetch_kpis(),
            'daily': fetch_daily_recharges(),
            'replication': fetch_replication(),
            'total_txns': fetch_transaction_count(),
            'transactions': fetch_transactions(per_page, offset)
        }

    def format_rows(self, data: dict) -> dict:
        counts, amounts = format_daily_rows(data['daily'])
        return {
            'db-stats-table': [format_db_stats(data['db_stats'])],
            'kpi-table': [format_kpi(data['kpis'])],
            'daily-table': [counts, amounts],
            'txn-table': [format_transaction(t) for t in data['transactions']]
        }

    def get_dynamic_columns(self, data: dict) -> dict:
        """Return dynamic column headers based on data."""
        return {
            'daily-table': get_daily_headers(data.get('daily', []))
        }
