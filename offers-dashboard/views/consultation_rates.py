"""
Consultation Rates View - View and edit consultant rates.
"""

from typing import List
from views.base import BaseView, TableConfig, ContainerConfig
from db import execute_query
from fmt import colorize, fmt_currency
from queries import CONSULTANT_RATES_PIVOT_QUERY


# --- Data Fetching ---

def fetch_all_rates() -> list:
    return execute_query(CONSULTANT_RATES_PIVOT_QUERY) or []


# --- Formatting ---

def format_rate_value(rate, color: str) -> str:
    if rate is None:
        return colorize("-", "gray")
    return colorize(fmt_currency(float(rate), 0), color)


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
    (consultant_id, full_name, chat_rate_id, chat_rate,
     voice_rate_id, voice_rate, video_rate_id, video_rate, is_active, tier) = row

    status = colorize("ACTIVE", "green") if is_active else colorize("INACTIVE", "red")

    return (
        str(consultant_id),
        full_name or "-",
        format_tier(tier),
        format_rate_value(chat_rate, "cyan"),
        format_rate_value(voice_rate, "green"),
        format_rate_value(video_rate, "magenta"),
        status
    )


# --- View Class ---

class ConsultationRatesView(BaseView):
    name = "Consultation Rates"
    view_id = "consultation_rates"
    icon = "₹"

    def get_containers(self) -> List[ContainerConfig]:
        return [
            ContainerConfig("rates-container", "ALL CONSULTATION RATES", [
                TableConfig("rates-table", ["ID", "Consultant", "Tier", "Chat", "Voice", "Video", "Status"], cursor=True)
            ])
        ]

    def fetch_data(self, **kwargs) -> dict:
        return {
            'rates': fetch_all_rates()
        }

    def format_rows(self, data: dict) -> dict:
        return {
            'rates-table': [format_rate(r) for r in data['rates']]
        }
