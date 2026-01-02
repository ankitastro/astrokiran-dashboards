"""
Guides Dashboard View
Real-time monitoring of guides availability with skills breakdown.
"""

from typing import List
from views.base import BaseView, TableConfig, ContainerConfig
from db import execute_query, execute_single
from queries import (
    GUIDE_COUNTS_QUERY,
    GUIDE_CHANNEL_COUNTS_QUERY,
    GUIDE_SKILLS_BREAKDOWN_QUERY,
    ONLINE_GUIDES_QUERY,
    OFFLINE_GUIDES_QUERY,
    TEST_GUIDES_QUERY,
    PROMO_GRANT_SPENDING_QUERY,
    LATEST_FEEDBACK_QUERY
)
from fmt import colorize, fmt_currency, fmt_number, pad, GREEN, RED, YELLOW


# --- Data Fetching (stateless) ---

def fetch_guide_counts() -> tuple:
    """Fetch online/offline/total counts."""
    return execute_single(GUIDE_COUNTS_QUERY) or (0, 0, 0)


def fetch_channel_counts() -> tuple:
    """Fetch chat/voice/video counts."""
    return execute_single(GUIDE_CHANNEL_COUNTS_QUERY) or (0, 0, 0)


def fetch_skills_breakdown() -> list:
    """Fetch skill-wise guide counts."""
    return execute_query(GUIDE_SKILLS_BREAKDOWN_QUERY)


def fetch_online_guides() -> list:
    """Fetch online guides with details."""
    return execute_query(ONLINE_GUIDES_QUERY)


def fetch_offline_guides() -> list:
    """Fetch offline guides with details."""
    return execute_query(OFFLINE_GUIDES_QUERY)


def fetch_test_guides() -> list:
    """Fetch test guides."""
    return execute_query(TEST_GUIDES_QUERY)


def fetch_promo_grants() -> list:
    """Fetch promo grant spending."""
    return execute_query(PROMO_GRANT_SPENDING_QUERY)


def fetch_feedback() -> list:
    """Fetch latest feedback."""
    return execute_query(LATEST_FEEDBACK_QUERY)


# --- Row Formatting (stateless) ---

def format_counts_row(counts: tuple, channels: tuple) -> tuple:
    """Format guide counts as a summary row."""
    online, offline, total = counts
    chat, voice, video = channels
    return (
        pad(colorize(fmt_number(online), GREEN)),
        pad(colorize(fmt_number(offline), RED)),
        pad(fmt_number(total)),
        pad(fmt_number(chat)),
        pad(fmt_number(voice)),
        pad(fmt_number(video))
    )


def format_skill_row(row: tuple) -> tuple:
    """Format skill breakdown row."""
    skill_name, online, offline, total = row
    return (
        skill_name,
        pad(colorize(str(online), GREEN)),
        pad(colorize(str(offline), RED)),
        pad(str(total))
    )


def format_guide_row(row: tuple) -> tuple:
    """Format online/offline guide row."""
    (guide_id, name, phone, chat, voice, video, skills, price,
     rating, consultations, earnings, today_p, today_ip_count,
     today_ip_customers, today_c, today_earnings, today_r, today_x,
     session_status) = row
    session = _format_session(session_status)
    return (
        str(guide_id),
        name or "N/A",
        session,
        "Y" if chat else "-",
        "Y" if voice else "-",
        pad(fmt_currency(float(price) if price else 0, decimals=0)),
        pad(fmt_currency(float(earnings) if earnings else 0, decimals=0)),
        str(today_p),
        str(today_ip_count),
        _truncate(today_ip_customers, 15) if today_ip_customers != '-' else '-',
        str(today_c),
        pad(fmt_currency(float(today_earnings) if today_earnings else 0, decimals=0)),
        str(today_r),
        str(today_x)
    )


def format_test_guide_row(row: tuple) -> tuple:
    """Format test guide row (includes status)."""
    (guide_id, name, phone, status, chat, voice, video, skills, price,
     rating, consultations, earnings, today_p, today_ip_count,
     today_ip_customers, today_c, today_earnings, today_r, today_x,
     session_status) = row
    status_display = _format_status(status)
    session = _format_session(session_status)
    return (
        str(guide_id),
        name or "N/A",
        status_display,
        session,
        "Y" if chat else "-",
        "Y" if voice else "-",
        pad(fmt_currency(float(price) if price else 0, decimals=0)),
        pad(fmt_currency(float(earnings) if earnings else 0, decimals=0)),
        str(today_p),
        str(today_ip_count),
        _truncate(today_ip_customers, 15) if today_ip_customers != '-' else '-',
        str(today_c),
        pad(fmt_currency(float(today_earnings) if today_earnings else 0, decimals=0)),
        str(today_r),
        str(today_x)
    )


def format_promo_row(row: tuple) -> tuple:
    """Format promo grant row."""
    consultant_id, guide_name, count = row
    return (
        str(consultant_id) if consultant_id else "N/A",
        guide_name or "Unknown",
        str(count)
    )


def format_feedback_row(row: tuple) -> tuple:
    """Format feedback row."""
    guide_id, guide_name, customer_name, rating, feedback, date, order_id = row
    stars = "*" * int(rating) if rating else "-"
    feedback_short = _truncate(feedback, 40) if feedback else "-"
    date_str = date.strftime("%Y-%m-%d %H:%M") if date else "-"
    return (
        str(order_id) if order_id else "-",
        guide_name or "Unknown",
        customer_name or "Anonymous",
        stars,
        feedback_short,
        date_str
    )


def _format_session(status: str) -> str:
    """Format session status."""
    if status == 'Active':
        return colorize("OK", GREEN)
    elif status == 'Expired':
        return colorize("EXP", YELLOW)
    return colorize("NO", RED)


def _format_status(status: str) -> str:
    """Format availability status."""
    if status == 'ONLINE_AVAILABLE':
        return colorize("ON", GREEN)
    elif status == 'ONLINE_BUSY':
        return colorize("BUSY", YELLOW)
    return colorize("OFF", RED)


def _truncate(text: str, max_len: int) -> str:
    """Truncate text to max length."""
    if not text:
        return "-"
    return text[:max_len] + "..." if len(text) > max_len else text


# --- View Class ---

class GuidesView(BaseView):
    """Guides Dashboard View"""

    name = "Guides"
    view_id = "guides"
    icon = "G"

    def get_containers(self) -> List[ContainerConfig]:
        return [
            ContainerConfig("guide-summary-container", "GUIDE SUMMARY", [
                TableConfig("guide-summary-table", [
                    "Online", "Offline", "Total", "Chat", "Voice", "Video"
                ])
            ]),
            ContainerConfig("guide-skills-container", "SKILLS BREAKDOWN", [
                TableConfig("guide-skills-table", [
                    "Skill", "Online", "Offline", "Total"
                ], cursor=True)
            ]),
            ContainerConfig("guide-online-container", "ONLINE GUIDES", [
                TableConfig("guide-online-table", [
                    "ID", "Name", "Sess", "Chat", "Voice", "Rs/m",
                    "Earn", "PEND", "IP#", "IP Names", "COMP", "Today", "REF", "CAN"
                ], cursor=True)
            ]),
            ContainerConfig("guide-offline-container", "OFFLINE GUIDES", [
                TableConfig("guide-offline-table", [
                    "ID", "Name", "Sess", "Chat", "Voice", "Rs/m",
                    "Earn", "PEND", "IP#", "IP Names", "COMP", "Today", "REF", "CAN"
                ], cursor=True)
            ]),
            ContainerConfig("guide-test-container", "TEST GUIDES", [
                TableConfig("guide-test-table", [
                    "ID", "Name", "Status", "Sess", "Chat", "Voice", "Rs/m",
                    "Earn", "PEND", "IP#", "IP Names", "COMP", "Today", "REF", "CAN"
                ], cursor=True)
            ]),
            ContainerConfig("guide-promo-container", "PROMO GRANT SPENDING", [
                TableConfig("guide-promo-table", [
                    "Consultant ID", "Guide Name", "Grants Spent"
                ], cursor=True)
            ]),
            ContainerConfig("guide-feedback-container", "LATEST FEEDBACK", [
                TableConfig("guide-feedback-table", [
                    "Order", "Guide", "Customer", "Rating", "Feedback", "Date"
                ], cursor=True)
            ])
        ]

    def fetch_data(self, **kwargs) -> dict:
        return {
            'counts': fetch_guide_counts(),
            'channels': fetch_channel_counts(),
            'skills': fetch_skills_breakdown(),
            'online': fetch_online_guides(),
            'offline': fetch_offline_guides(),
            'test': fetch_test_guides(),
            'promo': fetch_promo_grants(),
            'feedback': fetch_feedback()
        }

    def format_rows(self, data: dict) -> dict:
        return {
            'guide-summary-table': [format_counts_row(data['counts'], data['channels'])],
            'guide-skills-table': [format_skill_row(r) for r in data['skills']],
            'guide-online-table': [format_guide_row(r) for r in data['online']],
            'guide-offline-table': [format_guide_row(r) for r in data['offline']],
            'guide-test-table': [format_test_guide_row(r) for r in data['test']],
            'guide-promo-table': [format_promo_row(r) for r in data['promo']],
            'guide-feedback-table': [format_feedback_row(r) for r in data['feedback']]
        }
