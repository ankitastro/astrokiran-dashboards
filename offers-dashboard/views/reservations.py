"""
Reservations View - Active reservations and voucher tracking.
"""

from typing import List
from views.base import BaseView, TableConfig, ContainerConfig
from db import execute_query
from fmt import colorize, pick_color, fmt_currency, fmt_number, fmt_datetime, pad
from queries import (
    ACTIVE_RESERVATIONS_QUERY,
    RESERVATION_STATS_QUERY,
    EXPIRING_SOON_QUERY,
    RECENT_REDEMPTIONS_QUERY,
)


# --- Data Fetching ---

def fetch_active_reservations() -> list:
    return execute_query(ACTIVE_RESERVATIONS_QUERY) or []

def fetch_reservation_stats() -> list:
    return execute_query(RESERVATION_STATS_QUERY) or []

def fetch_expiring_soon() -> list:
    return execute_query(EXPIRING_SOON_QUERY) or []

def fetch_recent_redemptions() -> list:
    return execute_query(RECENT_REDEMPTIONS_QUERY) or []


# --- Formatting ---

def format_status(status: str) -> str:
    colors = {
        'ACTIVE': 'green',
        'REDEEMED': 'cyan',
        'EXPIRED': 'red',
        'CANCELLED': 'yellow'
    }
    return colorize(status, colors.get(status, 'white'))


def format_reservation(row: tuple) -> tuple:
    user_id, name, otype, status, orig, bonus, mins, cash, expires, created = row
    name_str = (name[:22] + "..") if len(name) > 24 else name

    benefit = ""
    if mins and int(mins) > 0:
        benefit = colorize(f"{int(mins)}m", "yellow")
    if cash and float(cash) > 0:
        cash_str = colorize(fmt_currency(float(cash)), "green")
        benefit = f"{benefit}+{cash_str}" if benefit else cash_str

    return (
        str(user_id),
        name_str,
        format_status(status),
        fmt_currency(float(orig)),
        benefit or "-",
        fmt_datetime(expires) or "-"
    )


def format_stat(row: tuple) -> tuple:
    status, count, bonus, mins = row
    return (
        format_status(status),
        pad(fmt_number(count)),
        pad(fmt_currency(float(bonus))),
        pad(f"{int(mins)}m") if mins else "-"
    )


def format_expiring(row: tuple) -> tuple:
    user_id, name, mins, cash, expires, hours = row
    name_str = (name[:20] + "..") if len(name) > 22 else name

    hours_str = f"{float(hours):.1f}h"
    if float(hours) < 2:
        hours_str = colorize(hours_str, "red")
    elif float(hours) < 6:
        hours_str = colorize(hours_str, "yellow")

    benefit = ""
    if mins: benefit = f"{int(mins)}m"
    if cash and float(cash) > 0: benefit += f" +{fmt_currency(float(cash))}"

    return (
        str(user_id),
        name_str,
        benefit or "-",
        hours_str
    )


def format_redemption(row: tuple) -> tuple:
    user_id, name, mins, bonus, consumed = row
    name_str = (name[:22] + "..") if len(name) > 24 else name
    return (
        str(user_id),
        name_str,
        f"{int(mins)}m" if mins else "-",
        colorize(fmt_currency(float(bonus)), "green") if bonus else "-",
        fmt_datetime(consumed) or "-"
    )


# --- View Class ---

class ReservationsView(BaseView):
    name = "Reservations"
    view_id = "reservations"
    icon = "R"

    def get_containers(self) -> List[ContainerConfig]:
        return [
            ContainerConfig("res-stats-container", "RESERVATION STATUS SUMMARY", [
                TableConfig("res-stats-table", ["Status", "Count", "Bonus", "Minutes"])
            ]),
            ContainerConfig("expiring-container", "EXPIRING SOON (24h)", [
                TableConfig("expiring-table", ["User", "Offer", "Benefit", "Time Left"])
            ]),
            ContainerConfig("active-res-container", "ACTIVE RESERVATIONS", [
                TableConfig("active-res-table", ["User", "Offer", "Status", "Amount", "Benefit", "Expires"], cursor=True)
            ]),
            ContainerConfig("redemptions-container", "RECENT REDEMPTIONS", [
                TableConfig("redemptions-table", ["User", "Offer", "Minutes", "Bonus", "Redeemed"])
            ])
        ]

    def fetch_data(self, **kwargs) -> dict:
        return {
            'stats': fetch_reservation_stats(),
            'expiring': fetch_expiring_soon(),
            'active': fetch_active_reservations(),
            'redemptions': fetch_recent_redemptions()
        }

    def format_rows(self, data: dict) -> dict:
        return {
            'res-stats-table': [format_stat(r) for r in data['stats']],
            'expiring-table': [format_expiring(r) for r in data['expiring']],
            'active-res-table': [format_reservation(r) for r in data['active']],
            'redemptions-table': [format_redemption(r) for r in data['redemptions']]
        }
