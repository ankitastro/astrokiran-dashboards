"""
Meta Marketing Campaign Metrics View (BD-6.0)
Subtasks: BD-6.1 to BD-6.12
Per-campaign metrics:
- Campaign Name, Status, Start Date, End Date
- Total Budget, Budget Per Day, Total Spends
- CAC (Customer Acquisition Cost)
- Total Impressions, Total Clicks
- Total Registered Users, Total Converted Users
"""

from typing import List
from views.base import BaseView, TableConfig, ContainerConfig
from db import execute_query
from fmt import colorize, pick_color, fmt_currency, fmt_number, fmt_date, pad, GREEN, RED, YELLOW


# --- Placeholder Queries ---

META_CAMPAIGNS_QUERY = """SELECT NULL;"""  # All campaign data


# --- Data Fetching (stateless) ---

def fetch_campaigns() -> list:
    """Fetch all Meta campaign metrics."""
    # TODO: Implement - likely from Meta Marketing API or imported data
    # Returns: [(name, status, start, end, budget, daily_budget, spends, cac,
    #            impressions, clicks, registered, converted), ...]
    return []


# --- Row Formatting (stateless) ---

def format_status(status: str) -> str:
    """Format campaign status with color."""
    if status == 'Active':
        return colorize(status, GREEN)
    elif status == 'Paused':
        return colorize(status, YELLOW)
    return status


def format_campaign_row(row: tuple) -> tuple:
    """Format campaign row."""
    (name, status, start, end, budget, daily_budget, spends,
     cac, impressions, clicks, registered, converted) = row

    cac_color = pick_color(float(cac), 50, 100, True) if cac > 0 else None
    cac_str = colorize(fmt_currency(float(cac)), cac_color) if cac_color else fmt_currency(float(cac))

    return (
        name,                              # BD-6.1
        format_status(status),             # BD-6.2
        fmt_date(start),                   # BD-6.3
        fmt_date(end),                     # BD-6.4
        fmt_currency(float(budget)),       # BD-6.5
        fmt_currency(float(daily_budget)), # BD-6.6
        fmt_currency(float(spends)),       # BD-6.7
        cac_str,                           # BD-6.8
        fmt_number(int(impressions)),      # BD-6.9
        fmt_number(int(clicks)),           # BD-6.10
        fmt_number(int(registered)),       # BD-6.11
        colorize(fmt_number(int(converted)), GREEN)  # BD-6.12
    )


# --- View Class ---

class MetaCampaignsView(BaseView):
    """Meta Marketing Campaign Metrics Dashboard (BD-6.0)"""

    name = "Meta Campaigns"
    view_id = "meta-campaigns"
    icon = "M"

    def get_containers(self) -> List[ContainerConfig]:
        return [
            ContainerConfig("meta-campaigns-container", "META CAMPAIGN METRICS", [
                TableConfig("meta-campaigns-table", [
                    "Campaign",      # BD-6.1
                    "Status",        # BD-6.2
                    "Start",         # BD-6.3
                    "End",           # BD-6.4
                    "Budget",        # BD-6.5
                    "Daily",         # BD-6.6
                    "Spends",        # BD-6.7
                    "CAC",           # BD-6.8
                    "Impressions",   # BD-6.9
                    "Clicks",        # BD-6.10
                    "Registered",    # BD-6.11
                    "Converted"      # BD-6.12
                ], cursor=True)
            ])
        ]

    def fetch_data(self, **kwargs) -> dict:
        return {
            'campaigns': fetch_campaigns()
        }

    def format_rows(self, data: dict) -> dict:
        return {
            'meta-campaigns-table': [format_campaign_row(r) for r in data['campaigns']]
        }
