"""
Wallet View - Database stats, KPIs, and user data.
All functions are stateless and under 20 lines.
"""

from typing import List
from views.base import BaseView, TableConfig, ContainerConfig
from db import execute_query, execute_single, execute_scalar
from queries import (
    DAILY_RECHARGE_QUERY, KPI_QUERY, DB_CONNECTIONS_QUERY,
    REPLICATION_STATUS_QUERY, ALL_USERS_COUNT_QUERY, ALL_USERS_COMPLETE_QUERY
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


def fetch_user_count() -> int:
    """Fetch total user count."""
    return execute_scalar(ALL_USERS_COUNT_QUERY) or 0


def fetch_users(limit: int, offset: int) -> list:
    """Fetch paginated user data."""
    return execute_query(ALL_USERS_COMPLETE_QUERY, (limit, offset))


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


def format_replication(repl: tuple) -> tuple:
    """Format replication status row."""
    is_rep, wal_bytes, secs = repl
    wal_color = pick_color(wal_bytes, 1024, 1024*1024, True)
    return (
        pad(colorize(fmt_bytes(wal_bytes) + (" (synced)" if wal_bytes == 0 else ""), wal_color)),
        pad(fmt_duration(secs))
    )


def format_user(row: tuple) -> tuple:
    """Format single user row."""
    uid, name, phone, real, virt, rech_c, total, spent, orders, last, created, _ = row
    real_f = float(real)
    real_str = colorize(fmt_currency(real_f), "bold green" if real_f > 1000 else "green") if real_f > 0 else fmt_currency(real_f)
    return (
        str(uid), name or "-", phone or "-", real_str,
        fmt_currency(float(virt)), str(rech_c), fmt_currency(float(total)),
        fmt_currency(float(spent)), str(orders), fmt_date(created), fmt_datetime(last) or "Never"
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
            ContainerConfig("users-container", "REAL USERS", [
                TableConfig("users-table", ["ID", "Name", "Phone", "Real", "Promo", "#", "Total", "Spent", "#", "Created", "Last"], cursor=True)
            ])
        ]

    def fetch_data(self, page: int = 1, per_page: int = 100) -> dict:
        offset = (page - 1) * per_page
        return {
            'db_stats': fetch_db_stats(),
            'kpis': fetch_kpis(),
            'daily': fetch_daily_recharges(),
            'replication': fetch_replication(),
            'total_users': fetch_user_count(),
            'users': fetch_users(per_page, offset)
        }

    def format_rows(self, data: dict) -> dict:
        counts, amounts = format_daily_rows(data['daily'])
        return {
            'db-stats-table': [format_db_stats(data['db_stats'])],
            'kpi-table': [format_kpi(data['kpis'])],
            'daily-table': [counts, amounts],
            'users-table': [format_user(u) for u in data['users']]
        }
