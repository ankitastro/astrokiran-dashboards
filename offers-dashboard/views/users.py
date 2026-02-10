"""
Users View - User behavior metrics and segments.
"""

from typing import List
from views.base import BaseView, TableConfig, ContainerConfig
from db import execute_query
from fmt import colorize, pick_color, fmt_currency, fmt_number, fmt_datetime, pad
from queries import (
    USER_SEGMENTS_QUERY,
    FIRST_TIME_USERS_QUERY,
    TOP_SPENDERS_QUERY,
    RECENT_ACTIVITY_QUERY,
    REGISTRATION_SOURCES_QUERY,
)


# --- Data Fetching ---

def fetch_user_segments() -> list:
    return execute_query(USER_SEGMENTS_QUERY) or []

def fetch_first_time_users() -> list:
    return execute_query(FIRST_TIME_USERS_QUERY) or []

def fetch_top_spenders() -> list:
    return execute_query(TOP_SPENDERS_QUERY) or []

def fetch_recent_activity() -> list:
    return execute_query(RECENT_ACTIVITY_QUERY) or []

def fetch_registration_sources() -> list:
    return execute_query(REGISTRATION_SOURCES_QUERY) or []


# --- Formatting ---

def format_segment(seg: str) -> str:
    colors = {
        'NEW': 'green',
        'ENGAGED': 'cyan',
        'LOYAL': 'yellow',
        'AT_RISK': 'red',
        'VIP': 'magenta'
    }
    return colorize(seg or "NEW", colors.get(seg, 'white'))


def format_source(src: str) -> str:
    colors = {'ORGANIC': 'green', 'WHATSAPP': 'cyan', 'GOOGLE_ADS': 'yellow'}
    return colorize(src or "ORGANIC", colors.get(src, 'white'))


def format_segment_row(row: tuple) -> tuple:
    seg, count, spent, offers, consults = row
    return (
        format_segment(seg),
        pad(colorize(fmt_number(count), pick_color(count, 10, 50))),
        pad(fmt_currency(float(spent))),
        pad(fmt_number(int(offers))),
        pad(f"{float(consults):.1f}")
    )


def format_first_time(row: tuple) -> tuple:
    uid, source, is_ft, spent, offers, created = row
    return (
        str(uid),
        format_source(source),
        colorize(fmt_currency(float(spent)), "green") if spent else "-",
        str(offers or 0),
        fmt_datetime(created) or "-"
    )


def format_top_spender(row: tuple) -> tuple:
    uid, seg, spent, consults, offers, last = row
    return (
        str(uid),
        format_segment(seg),
        colorize(fmt_currency(float(spent)), "green"),
        str(consults or 0),
        str(offers or 0),
        fmt_datetime(last) or "-"
    )


def format_recent(row: tuple) -> tuple:
    uid, seg, svc, consults, last_c, last_o = row
    svc_colors = {'CHAT': 'cyan', 'VOICE': 'green', 'VIDEO': 'magenta'}
    svc_str = colorize(svc or "-", svc_colors.get(svc, 'white'))
    return (
        str(uid),
        format_segment(seg),
        svc_str,
        str(consults or 0),
        fmt_datetime(last_c) or "-"
    )


def format_source_row(row: tuple) -> tuple:
    source, count, ft, spent = row
    return (
        format_source(source),
        pad(fmt_number(count)),
        pad(colorize(fmt_number(ft), "green")),
        pad(fmt_currency(float(spent)))
    )


# --- View Class ---

class UsersView(BaseView):
    name = "User Behavior"
    view_id = "users"
    icon = "U"

    def get_containers(self) -> List[ContainerConfig]:
        return [
            ContainerConfig("segments-container", "USER SEGMENTS", [
                TableConfig("segments-table", ["Segment", "Users", "Total Spent", "Offers Used", "Avg Consults"])
            ]),
            ContainerConfig("sources-container", "REGISTRATION SOURCES", [
                TableConfig("sources-table", ["Source", "Users", "First-Time", "Total Spent"])
            ]),
            ContainerConfig("top-container", "TOP SPENDERS", [
                TableConfig("top-table", ["User", "Segment", "Spent", "Consults", "Offers", "Last Active"])
            ]),
            ContainerConfig("recent-container", "RECENT ACTIVITY (7 Days)", [
                TableConfig("recent-table", ["User", "Segment", "Service", "Consults", "Last Consult"], cursor=True)
            ])
        ]

    def fetch_data(self, **kwargs) -> dict:
        return {
            'segments': fetch_user_segments(),
            'sources': fetch_registration_sources(),
            'top': fetch_top_spenders(),
            'recent': fetch_recent_activity()
        }

    def format_rows(self, data: dict) -> dict:
        return {
            'segments-table': [format_segment_row(r) for r in data['segments']],
            'sources-table': [format_source_row(r) for r in data['sources']],
            'top-table': [format_top_spender(r) for r in data['top']],
            'recent-table': [format_recent(r) for r in data['recent']]
        }
