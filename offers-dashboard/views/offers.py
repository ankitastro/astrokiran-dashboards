"""
Offers View - Active offers, consumptions, and usage stats.
"""

from typing import List
from views.base import BaseView, TableConfig, ContainerConfig
from db import execute_query
from fmt import colorize, pick_color, fmt_currency, fmt_number, fmt_date, fmt_datetime, pad
from queries import (
    ACTIVE_OFFERS_QUERY,
    OFFER_STATS_QUERY,
    RECENT_CONSUMPTIONS_QUERY,
    DAILY_CONSUMPTION_QUERY,
    FIRST_TIME_VS_REGULAR_QUERY,
    USER_SEGMENTS_QUERY,
)


# --- Data Fetching ---

def fetch_active_offers() -> list:
    return execute_query(ACTIVE_OFFERS_QUERY) or []

def fetch_offer_stats() -> list:
    return execute_query(OFFER_STATS_QUERY) or []

def fetch_recent_consumptions() -> list:
    return execute_query(RECENT_CONSUMPTIONS_QUERY) or []

def fetch_user_segments() -> list:
    return execute_query(USER_SEGMENTS_QUERY) or []

def fetch_daily_consumptions() -> list:
    return execute_query(DAILY_CONSUMPTION_QUERY) or []

def fetch_user_type_stats() -> list:
    return execute_query(FIRST_TIME_VS_REGULAR_QUERY) or []


# --- Row Formatting ---

def format_offer_type(offer_type: str) -> str:
    colors = {
        'COMBO_OFFER': 'magenta',
        'WALLET_RECHARGE': 'green',
        'VOUCHER': 'yellow',
        'CONSULTANT_PRICING': 'cyan'
    }
    return colorize(offer_type, colors.get(offer_type, 'white'))


def format_user_types(types: list) -> str:
    if not types:
        return "-"
    if 'FIRST_TIME' in types and 'REGULAR' in types:
        return colorize("ALL", "cyan")
    if 'FIRST_TIME' in types:
        return colorize("1ST", "green")
    if 'REGULAR' in types:
        return colorize("REG", "yellow")
    return str(types)


def format_active_offer(row: tuple) -> tuple:
    name, otype, category, pct, mins, min_amt, max_amt, user_types, trigger_type, valid_to = row
    name_str = (name[:25] + "..") if len(name) > 27 else name

    bonus_str = ""
    if pct and float(pct) > 0:
        bonus_str = colorize(f"{float(pct):.0f}%", "green")
    if mins and int(mins) > 0:
        mins_str = colorize(f"{int(mins)}m", "yellow")
        bonus_str = f"{bonus_str}+{mins_str}" if bonus_str else mins_str

    range_str = f"{fmt_currency(float(min_amt), 0)}-{fmt_currency(float(max_amt), 0)}"

    trigger_str = colorize(trigger_type, "cyan") if trigger_type else "-"

    return (
        name_str,
        format_offer_type(otype),
        bonus_str or "-",
        range_str,
        format_user_types(user_types),
        trigger_str,
        fmt_date(valid_to)
    )


def format_offer_stat(row: tuple) -> tuple:
    otype, count, consumptions, total_bonus = row
    return (
        format_offer_type(otype),
        pad(str(count)),
        pad(colorize(fmt_number(consumptions), pick_color(consumptions, 10, 50))),
        pad(colorize(fmt_currency(float(total_bonus)), "green"))
    )


def format_consumption(row: tuple) -> tuple:
    user_id, offer_name, otype, orig_amt, bonus_amt, status, consumed_at = row
    name_str = (offer_name[:20] + "..") if len(offer_name) > 22 else offer_name

    status_colors = {
        'COMPLETED': 'green',
        'PENDING': 'yellow',
        'FAILED': 'red',
        'REFUNDED': 'magenta'
    }
    status_str = colorize(status, status_colors.get(status, 'white'))

    return (
        str(user_id),
        name_str,
        format_offer_type(otype),
        fmt_currency(float(orig_amt)),
        colorize(fmt_currency(float(bonus_amt)), "green"),
        status_str,
        fmt_datetime(consumed_at) or "-"
    )


def format_daily_consumption(row: tuple) -> tuple:
    date, day_label, count, total_bonus = row
    return (
        pad(day_label),
        pad(colorize(fmt_number(count), pick_color(count, 5, 20))),
        pad(colorize(fmt_currency(float(total_bonus)), "green"))
    )


def format_user_type_stat(row: tuple) -> tuple:
    user_type, consumptions, total_bonus = row
    type_colors = {'FIRST_TIME': 'green', 'REGULAR': 'yellow', 'BOTH': 'cyan'}
    type_str = colorize(user_type, type_colors.get(user_type, 'white'))

    return (
        type_str,
        pad(colorize(fmt_number(consumptions), pick_color(consumptions, 10, 50))),
        pad(colorize(fmt_currency(float(total_bonus)), "green"))
    )


# --- View Class ---

class OffersView(BaseView):
    name = "Offers Dashboard"
    view_id = "offers"
    icon = "O"

    def get_containers(self) -> List[ContainerConfig]:
        return [
            ContainerConfig("offer-stats-container", "OFFER STATISTICS BY TYPE", [
                TableConfig("offer-stats-table", ["Type", "Offers", "Consumptions", "Bonus Given"])
            ]),
            ContainerConfig("user-type-container", "FIRST-TIME vs REGULAR USERS", [
                TableConfig("user-type-table", ["User Type", "Consumptions", "Total Bonus"])
            ]),
            ContainerConfig("daily-container", "DAILY CONSUMPTIONS (Last 7 Days)", [
                TableConfig("daily-consumption-table", ["Day", "Count", "Bonus"])
            ]),
            ContainerConfig("active-offers-container", "ACTIVE OFFERS", [
                TableConfig("active-offers-table", ["Name", "Type", "Bonus", "Range", "Target", "Trigger", "Valid To"])
            ]),
            ContainerConfig("consumption-container", "RECENT CONSUMPTIONS", [
                TableConfig("consumption-table", ["User", "Offer", "Type", "Amount", "Bonus", "Status", "Time"], cursor=True)
            ])
        ]

    def fetch_data(self, **kwargs) -> dict:
        return {
            'active_offers': fetch_active_offers(),
            'offer_stats': fetch_offer_stats(),
            'consumptions': fetch_recent_consumptions(),
            'user_segments': fetch_user_segments(),
            'daily': fetch_daily_consumptions(),
            'user_type_stats': fetch_user_type_stats()
        }

    def format_rows(self, data: dict) -> dict:
        return {
            'offer-stats-table': [format_offer_stat(r) for r in data['offer_stats']],
            'user-type-table': [format_user_type_stat(r) for r in data['user_type_stats']],
            'daily-consumption-table': [format_daily_consumption(r) for r in data['daily']],
            'active-offers-table': [format_active_offer(r) for r in data['active_offers']],
            'consumption-table': [format_consumption(r) for r in data['consumptions']]
        }
