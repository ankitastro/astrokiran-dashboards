"""
First-Time Users View - All offers available to first-time users.
"""

from typing import List
from views.base import BaseView, TableConfig, ContainerConfig
from db import execute_query
from fmt import colorize, fmt_currency, fmt_datetime
from queries import FIRST_TIME_OFFERS_QUERY, REGULAR_OFFERS_QUERY


# --- Data Fetching ---

def fetch_first_time_offers() -> list:
    return execute_query(FIRST_TIME_OFFERS_QUERY) or []

def fetch_regular_offers() -> list:
    return execute_query(REGULAR_OFFERS_QUERY) or []


# --- Formatting ---

def format_offer_type(otype: str) -> str:
    colors = {
        'COMBO_OFFER': 'magenta',
        'WALLET_RECHARGE': 'green',
        'VOUCHER': 'yellow',
        'CONSULTANT_PRICING': 'cyan'
    }
    return colorize(otype, colors.get(otype, 'white'))


def wrap_text(text: str, width: int = 40) -> str:
    """Wrap text to specified width."""
    if len(text) <= width:
        return text
    words = text.split()
    lines = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= width:
            current = f"{current} {word}" if current else word
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return "\n".join(lines)


def format_offer(row: tuple) -> tuple:
    (offer_id, name, otype, category, pct, fixed, mins, min_amt, max_amt,
     max_cb, voucher_sub, trigger, valid_from, valid_to, is_active,
     description, service_type, usage_limit, cta_text, target_guide_tiers) = row

    # Wrap long names
    name_str = wrap_text(name, 40)

    # Format benefit
    benefit = ""
    if pct and float(pct) > 0:
        benefit = colorize(f"{float(pct):.0f}%", "green")
    if mins and int(mins) > 0:
        mins_str = colorize(f"+{int(mins)}m", "yellow")
        benefit = f"{benefit} {mins_str}" if benefit else mins_str
    elif fixed and float(fixed) > 0:
        # Show fixed amount only if no free minutes (otherwise fixed represents minutes value)
        benefit = colorize(f"+{fmt_currency(float(fixed), 0)}", "cyan")

    # Recharge range
    min_val = float(min_amt) if min_amt else 0
    max_val = float(max_amt) if max_amt else 0
    if min_val == max_val or max_val == 0:
        range_str = fmt_currency(min_val, 0)
    else:
        range_str = f"{fmt_currency(min_val, 0)}-{fmt_currency(max_val, 0)}"

    # Final value after recharge (recharge + cashback) for both min and max
    def calc_final(amt):
        val = amt
        if pct and float(pct) > 0:
            cashback = amt * float(pct) / 100
            if max_cb and float(max_cb) > 0:
                cashback = min(cashback, float(max_cb))
            val += cashback
        # Only add fixed amount if no free minutes (otherwise fixed represents minutes value)
        if fixed and float(fixed) > 0 and not (mins and int(mins) > 0):
            val += float(fixed)
        return val

    final_min = calc_final(min_val)
    final_max = calc_final(max_val)

    # Format final value as range
    if final_min == final_max or max_val == 0:
        final_str = colorize(fmt_currency(final_min, 0), "cyan")
    else:
        final_str = colorize(f"{fmt_currency(final_min, 0)}-{fmt_currency(final_max, 0)}", "cyan")

    # Voucher (free minutes)
    voucher_str = colorize(f"{int(mins)}m", "yellow") if mins and int(mins) > 0 else "-"

    # Status
    status = colorize("ACTIVE", "green") if is_active else colorize("INACTIVE", "red")

    # Trigger
    trigger_str = colorize(trigger, "cyan") if trigger else colorize("-", "gray")

    # Service type
    svc_str = colorize(service_type or "ALL", "magenta") if service_type else "-"

    # Usage limit
    limit_str = str(usage_limit) if usage_limit and usage_limit > 0 else "-"

    # Voucher subtype
    subtype_str = colorize(voucher_sub, "yellow") if voucher_sub else "-"

    # Guide tiers (format as comma-separated, capitalize first letter)
    if target_guide_tiers and len(target_guide_tiers) > 0:
        tiers_list = [t.capitalize() for t in target_guide_tiers]
        tiers_str = colorize(", ".join(tiers_list), "cyan")
    else:
        tiers_str = colorize("All", "gray")

    return (
        str(offer_id)[-4:] if offer_id else "-",
        name_str,
        format_offer_type(otype),
        subtype_str,
        benefit or "-",
        range_str,
        final_str,
        voucher_str,
        svc_str,
        trigger_str,
        limit_str,
        tiers_str,
        status,
        fmt_datetime(valid_from),
        fmt_datetime(valid_to)
    )


# --- View Class ---

class FirstTimeView(BaseView):
    name = "All Offers"
    view_id = "first_time"
    icon = "O"

    def get_containers(self) -> List[ContainerConfig]:
        columns = ["ID", "Name", "Type", "Subtype", "Benefit", "Recharge", "Final Value", "Voucher", "Service", "Trigger", "Limit", "Tiers", "Status", "Valid From", "Valid To"]
        return [
            ContainerConfig("first-time-container", "ALL FIRST-TIME OFFERS", [
                TableConfig("first-time-table", columns, cursor=True)
            ]),
            ContainerConfig("regular-container", "ALL REGULAR OFFERS", [
                TableConfig("regular-table", columns, cursor=True)
            ])
        ]

    def fetch_data(self, **kwargs) -> dict:
        return {
            'first_time': fetch_first_time_offers(),
            'regular': fetch_regular_offers()
        }

    def format_rows(self, data: dict) -> dict:
        return {
            'first-time-table': [format_offer(r) for r in data['first_time']],
            'regular-table': [format_offer(r) for r in data['regular']]
        }
