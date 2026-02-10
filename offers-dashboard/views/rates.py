"""
Rates View - Consultant rates and pricing.
"""

from typing import List
from views.base import BaseView, TableConfig, ContainerConfig
from db import execute_query
from fmt import colorize, pick_color, fmt_currency, fmt_number, fmt_date, pad
from queries import (
    CONSULTANT_RATES_QUERY,
    RATES_BY_SERVICE_QUERY,
    DISCOUNT_OFFERS_QUERY,
    TOP_RATED_CONSULTANTS_QUERY,
)


# --- Data Fetching ---

def fetch_consultant_rates() -> list:
    return execute_query(CONSULTANT_RATES_QUERY) or []

def fetch_rates_by_service() -> list:
    return execute_query(RATES_BY_SERVICE_QUERY) or []

def fetch_discount_offers() -> list:
    return execute_query(DISCOUNT_OFFERS_QUERY) or []

def fetch_top_consultants() -> list:
    return execute_query(TOP_RATED_CONSULTANTS_QUERY) or []


# --- Formatting ---

def format_service_type(stype: str) -> str:
    colors = {'CHAT': 'cyan', 'VOICE': 'green', 'VIDEO': 'magenta', 'ALL': 'yellow'}
    return colorize(stype, colors.get(stype, 'white'))


def format_tier(tier: str) -> str:
    if not tier:
        return colorize("-", "gray")
    colors = {
        'basic': 'white',
        'standard': 'cyan',
        'premium': 'yellow',
        'elite': 'magenta',
    }
    return colorize(tier.capitalize(), colors.get(tier.lower(), 'white'))


def format_rate(row: tuple) -> tuple:
    cid, stype, rate, active, vfrom, vto, tier = row
    active_str = colorize("YES", "green") if active else colorize("NO", "red")
    return (
        str(cid),
        format_tier(tier),
        format_service_type(stype),
        colorize(fmt_currency(float(rate)), "green"),
        active_str,
        fmt_date(vfrom) or "-",
        fmt_date(vto) or "-"
    )


def format_service_stat(row: tuple) -> tuple:
    stype, count, min_r, max_r, avg_r = row
    return (
        format_service_type(stype),
        pad(fmt_number(count)),
        pad(fmt_currency(float(min_r))),
        pad(fmt_currency(float(max_r))),
        pad(fmt_currency(float(avg_r)))
    )


def format_discount(row: tuple) -> tuple:
    name, pct, targets, vfrom, vto, active = row
    name_str = (name[:20] + "..") if len(name) > 22 else name

    pct_str = colorize(f"{float(pct):.0f}%", "green") if pct else "-"
    active_str = colorize("ACTIVE", "green") if active else colorize("INACTIVE", "red")

    target_str = "ALL"
    if targets:
        if 'FIRST_TIME' in targets and 'REGULAR' not in targets:
            target_str = colorize("1ST", "cyan")
        elif 'REGULAR' in targets and 'FIRST_TIME' not in targets:
            target_str = colorize("REG", "yellow")

    return (
        name_str,
        pct_str,
        target_str,
        active_str,
        fmt_date(vto) or "-"
    )


def format_top_consultant(row: tuple) -> tuple:
    cid, count, high, low = row
    return (
        str(cid),
        pad(str(count)),
        colorize(fmt_currency(float(high)), "green"),
        fmt_currency(float(low))
    )


# --- View Class ---

class RatesView(BaseView):
    name = "Rates & Pricing"
    view_id = "rates"
    icon = "$"

    def get_containers(self) -> List[ContainerConfig]:
        return [
            ContainerConfig("service-stats-container", "RATES BY SERVICE TYPE", [
                TableConfig("service-stats-table", ["Service", "Consultants", "Min Rate", "Max Rate", "Avg Rate"])
            ]),
            ContainerConfig("discounts-container", "DISCOUNT OFFERS", [
                TableConfig("discounts-table", ["Offer", "Discount", "Target", "Status", "Valid To"])
            ]),
            ContainerConfig("top-container", "TOP CONSULTANTS BY RATE", [
                TableConfig("top-table", ["Consultant", "Services", "Highest", "Lowest"])
            ]),
            ContainerConfig("rates-container", "CONSULTANT RATES", [
                TableConfig("rates-table", ["Consultant", "Tier", "Service", "Rate/min", "Active", "From", "To"], cursor=True)
            ])
        ]

    def fetch_data(self, **kwargs) -> dict:
        return {
            'service_stats': fetch_rates_by_service(),
            'discounts': fetch_discount_offers(),
            'top': fetch_top_consultants(),
            'rates': fetch_consultant_rates()
        }

    def format_rows(self, data: dict) -> dict:
        return {
            'service-stats-table': [format_service_stat(r) for r in data['service_stats']],
            'discounts-table': [format_discount(r) for r in data['discounts']],
            'top-table': [format_top_consultant(r) for r in data['top']],
            'rates-table': [format_rate(r) for r in data['rates']]
        }
