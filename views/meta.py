"""
Meta Ads View - Campaign performance analytics.
All functions are stateless and under 20 lines.
"""

import csv
import re
from datetime import datetime
from typing import List
from views.base import BaseView, TableConfig, ContainerConfig
from db import execute_single
from queries import CAC_QUERY
from fmt import (
    colorize, pick_color, fmt_currency, fmt_percent,
    fmt_number, pad, truncate, GREEN, YELLOW, RED, GRAY
)


# --- CSV Parsing (stateless) ---

def clean_number(val) -> float:
    """Clean and convert to float."""
    if not val:
        return 0
    return float(re.sub(r'[^0-9.-]+', '', str(val))) or 0


def parse_date(val) -> datetime.date:
    """Parse date string."""
    if not val:
        return None
    try:
        return datetime.strptime(val.strip(), '%Y-%m-%d').date()
    except:
        return None


def find_column(headers: list, *patterns) -> str:
    """Find column matching patterns."""
    for h in headers:
        for p in patterns:
            if p.lower() in h.lower():
                return h
    return None


def parse_csv_row(row: dict, keys: dict) -> dict:
    """Parse single CSV row into ad data."""
    name = row.get(keys['name'], '')
    if not name or name == 'nan':
        return None
    spend = clean_number(row.get(keys['spend'], 0))
    if spend <= 0:
        return None
    installs = clean_number(row.get(keys['results'], 0))
    impressions = clean_number(row.get(keys['impressions'], 0))
    clicks = clean_number(row.get(keys['clicks'], 0))
    return {
        'name': name,
        'spend': spend,
        'installs': int(installs),
        'impressions': int(impressions),
        'clicks': int(clicks),
        'reach': int(clean_number(row.get(keys.get('reach'), 0))),
        'cpi': spend / installs if installs > 0 else 0,
        'ctr': (clicks / impressions * 100) if impressions > 0 else 0
    }


def parse_csv(path: str) -> tuple:
    """Parse Meta Ads CSV file. Returns (ads_list, summary_dict)."""
    data, date_start, date_end = [], None, None
    with open(path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        keys = {
            'name': find_column(headers, 'ad set name'),
            'spend': find_column(headers, 'amount spent'),
            'results': find_column(headers, 'Results', 'mobile app install'),
            'impressions': find_column(headers, 'impressions'),
            'clicks': find_column(headers, 'link clicks'),
            'reach': find_column(headers, 'reach'),
            'start': find_column(headers, 'reporting starts'),
            'end': find_column(headers, 'reporting ends')
        }
        for row in reader:
            if not date_start and keys['start']:
                date_start = parse_date(row.get(keys['start']))
            if not date_end and keys['end']:
                date_end = parse_date(row.get(keys['end']))
            ad = parse_csv_row(row, keys)
            if ad:
                data.append(ad)
    data.sort(key=lambda x: x['spend'], reverse=True)
    return data, compute_summary(data, date_start, date_end)


def compute_summary(data: list, date_start, date_end) -> dict:
    """Compute summary metrics from ad data."""
    spend = sum(d['spend'] for d in data)
    installs = sum(d['installs'] for d in data)
    impressions = sum(d['impressions'] for d in data)
    clicks = sum(d['clicks'] for d in data)
    reach = sum(d['reach'] for d in data)
    return {
        'total_spend': spend,
        'total_installs': installs,
        'total_reach': reach,
        'avg_frequency': impressions / reach if reach > 0 else 0,
        'avg_cpi': spend / installs if installs > 0 else 0,
        'avg_ctr': (clicks / impressions * 100) if impressions > 0 else 0,
        'date_start': date_start,
        'date_end': date_end,
        'ad_count': len(data)
    }


# --- CAC Fetching (stateless) ---

def fetch_cac(date_start, date_end) -> dict:
    """Fetch CAC data from database."""
    if not date_start or not date_end:
        return None
    result = execute_single(CAC_QUERY, (date_start, date_end))
    if not result:
        return None
    return {'customers': result[0] or 0, 'revenue': float(result[1] or 0)}


# --- Row Formatting (stateless) ---

def format_period(summary: dict) -> str:
    """Format date period."""
    s, e = summary.get('date_start'), summary.get('date_end')
    if s and e:
        return f"{s.strftime('%b %d')} - {e.strftime('%b %d')}"
    return "Unknown"


def format_kpi(summary: dict, cac: dict) -> tuple:
    """Format Meta KPI row."""
    s = summary
    cust = cac['customers'] if cac else 0
    rev = cac['revenue'] if cac else 0
    cac_val = s['total_spend'] / cust if cust > 0 else 0
    rev_str = colorize(fmt_currency(rev), GREEN if rev > s['total_spend'] else RED) if cac else "-"
    cac_str = colorize(fmt_currency(cac_val), pick_color(cac_val, 50, 100, True)) if cust > 0 else "-"
    return (
        pad(format_period(s)), pad(fmt_currency(s['total_spend'], 0)),
        pad(fmt_number(s['total_reach'])), pad(f"{s['avg_frequency']:.2f}"),
        pad(fmt_number(s['total_installs'])), pad(fmt_currency(s['avg_cpi'])),
        pad(fmt_number(cust)), pad(rev_str), pad(cac_str)
    )


def get_ad_status(ad: dict) -> str:
    """Get status label for ad."""
    if ad['installs'] > 0:
        if ad['cpi'] < 15:
            return colorize("Winner", GREEN)
        if ad['cpi'] > 40:
            return colorize("Expensive", RED)
        return colorize("Average", YELLOW)
    if ad['spend'] > 50:
        return colorize("Wasted", RED)
    return colorize("No Data", GRAY)


def format_ad(ad: dict) -> tuple:
    """Format single ad row."""
    cpi_str = colorize(fmt_currency(ad['cpi']), pick_color(ad['cpi'], 15, 40, True)) if ad['installs'] > 0 else "-"
    return (
        truncate(ad['name']), fmt_currency(ad['spend']),
        str(ad['installs']), cpi_str,
        fmt_number(ad['impressions']), fmt_number(ad['clicks']),
        fmt_percent(ad['ctr']), get_ad_status(ad)
    )


# --- View Class ---

class MetaView(BaseView):
    """Meta Ads analytics view."""

    name = "Meta Ads Analytics"
    view_id = "meta"
    icon = "M"

    def get_containers(self) -> List[ContainerConfig]:
        return [
            ContainerConfig("meta-kpi-container", "META ADS CAMPAIGN METRICS", [
                TableConfig("meta-kpi-table", ["Period", "Spend", "Reach", "Freq", "Installs", "CPI", "Customers", "Revenue", "CAC"])
            ]),
            ContainerConfig("meta-ads-container", "AD SET PERFORMANCE", [
                TableConfig("meta-ads-table", ["Ad Set", "Spend", "Installs", "CPI", "Impressions", "Clicks", "CTR", "Status"], cursor=True)
            ])
        ]

    def fetch_data(self, csv_path: str = None) -> dict:
        if not csv_path:
            return {'ads': [], 'summary': {}, 'cac': None}
        ads, summary = parse_csv(csv_path)
        cac = fetch_cac(summary.get('date_start'), summary.get('date_end'))
        return {'ads': ads, 'summary': summary, 'cac': cac}

    def format_rows(self, data: dict) -> dict:
        if not data.get('summary'):
            return {'meta-kpi-table': [], 'meta-ads-table': []}
        return {
            'meta-kpi-table': [format_kpi(data['summary'], data['cac'])],
            'meta-ads-table': [format_ad(ad) for ad in data['ads']]
        }
