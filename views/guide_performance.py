"""
Guide Performance View
Shows repeat ADD rates and leakage/retention metrics per guide.
Flow: SPENT (Guide) → ADD → ADD again
"""

from typing import List
from views.base import BaseView, TableConfig, ContainerConfig
from db import execute_query
from queries import GUIDE_PERFORMANCE_QUERY, GUIDE_LEAKAGE_QUERY
from fmt import colorize, fmt_number, fmt_percent, pad, GREEN, RED, YELLOW


# --- Data Fetching (stateless) ---

def fetch_guide_performance() -> list:
    """Fetch guide repeat ADD performance."""
    return execute_query(GUIDE_PERFORMANCE_QUERY)


def fetch_guide_leakage() -> list:
    """Fetch guide leakage/retention metrics."""
    return execute_query(GUIDE_LEAKAGE_QUERY)


# --- Row Formatting (stateless) ---

def format_performance_row(row: tuple) -> tuple:
    """Format guide performance row."""
    guide_id, name, spoke, first_add, repeat_add, repeat_rate, retention_rate = row

    # Color code repeat_rate (1st ADD / Spoke)
    repeat_rate_str = f"{repeat_rate}%" if repeat_rate else "-"
    if repeat_rate and repeat_rate >= 25:
        repeat_rate_str = colorize(repeat_rate_str, GREEN)
    elif repeat_rate and repeat_rate >= 15:
        repeat_rate_str = colorize(repeat_rate_str, YELLOW)
    elif repeat_rate:
        repeat_rate_str = colorize(repeat_rate_str, RED)

    # Color code retention_rate (2nd ADD / 1st ADD)
    retention_rate_str = f"{retention_rate}%" if retention_rate else "-"
    if retention_rate and retention_rate >= 40:
        retention_rate_str = colorize(retention_rate_str, GREEN)
    elif retention_rate and retention_rate >= 25:
        retention_rate_str = colorize(retention_rate_str, YELLOW)
    elif retention_rate:
        retention_rate_str = colorize(retention_rate_str, RED)

    return (
        str(guide_id),
        name or "N/A",
        pad(str(spoke or 0)),
        pad(str(first_add or 0)),
        pad(str(repeat_add or 0)),
        pad(repeat_rate_str),
        pad(retention_rate_str)
    )


def format_leakage_row(row: tuple) -> tuple:
    """Format guide leakage row."""
    (guide_id, name, spoke, recharged, came_back, leaked,
     recharge_rate, retention_rate, leakage_rate) = row

    # Color code retention_rate (higher is better)
    ret_str = f"{retention_rate}%" if retention_rate else "-"
    if retention_rate and retention_rate >= 60:
        ret_str = colorize(ret_str, GREEN)
    elif retention_rate and retention_rate >= 40:
        ret_str = colorize(ret_str, YELLOW)
    elif retention_rate:
        ret_str = colorize(ret_str, RED)

    # Color code leakage_rate (lower is better)
    leak_str = f"{leakage_rate}%" if leakage_rate else "-"
    if leakage_rate and leakage_rate <= 30:
        leak_str = colorize(leak_str, GREEN)
    elif leakage_rate and leakage_rate <= 50:
        leak_str = colorize(leak_str, YELLOW)
    elif leakage_rate:
        leak_str = colorize(leak_str, RED)

    return (
        str(guide_id),
        name or "N/A",
        pad(str(spoke or 0)),
        pad(str(recharged or 0)),
        pad(str(came_back or 0)),
        pad(str(leaked or 0)),
        pad(ret_str),
        pad(leak_str)
    )


# --- View Class ---

class GuidePerformanceView(BaseView):
    """Guide Performance Dashboard View"""

    name = "Guide Performance"
    view_id = "guide_performance"
    icon = "P"

    def get_containers(self) -> List[ContainerConfig]:
        return [
            ContainerConfig("gp-repeat-container", "GUIDE REPEAT & RETENTION (SPENT → ADD → ADD)", [
                TableConfig("gp-repeat-table", [
                    "ID", "Guide", "Spoke", "1st ADD", "2nd ADD", "Repeat%", "Retain%"
                ], cursor=True)
            ]),
            ContainerConfig("gp-leakage-container", "RETENTION vs LEAKAGE (Recharged → Came Back vs Leaked)", [
                TableConfig("gp-leakage-table", [
                    "ID", "Guide", "Spoke", "Recharged", "Back", "Leaked", "Retain%", "Leak%"
                ], cursor=True)
            ])
        ]

    def fetch_data(self, **kwargs) -> dict:
        return {
            'performance': fetch_guide_performance(),
            'leakage': fetch_guide_leakage()
        }

    def format_rows(self, data: dict) -> dict:
        return {
            'gp-repeat-table': [format_performance_row(r) for r in data['performance']],
            'gp-leakage-table': [format_leakage_row(r) for r in data['leakage']]
        }
