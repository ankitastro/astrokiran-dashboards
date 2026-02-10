"""
Onboard Guide View - View all guides and onboard new ones.
"""

from typing import List
from views.base import BaseView, TableConfig, ContainerConfig
from db import execute_query
from fmt import colorize, fmt_datetime


# --- Data Fetching ---

def fetch_all_guides() -> list:
    query = """
    SELECT
        gp.id,
        gp.full_name,
        gp.phone_number,
        gp.email,
        gp.onboarding_state,
        gp.chat_enabled,
        gp.voice_enabled,
        gp.video_enabled,
        gp.tier,
        gp.years_of_experience,
        gp.availability_state,
        gp.created_at
    FROM guide.guide_profile gp
    WHERE gp.deleted_at IS NULL
    ORDER BY gp.created_at DESC
    """
    return execute_query(query) or []


# --- Formatting ---

def format_bool(val: bool, true_text: str = "Yes", false_text: str = "No") -> str:
    if val:
        return colorize(true_text, "green")
    return colorize(false_text, "gray")


def format_state(state: str) -> str:
    colors = {
        'ACTIVE': 'green',
        'REGISTRATION_PENDING': 'yellow',
        'PROFILE_PENDING': 'yellow',
        'INACTIVE': 'red',
        'BLOCKED': 'red',
    }
    return colorize(state, colors.get(state, 'white'))


def format_availability(state: str) -> str:
    colors = {
        'ONLINE': 'green',
        'BUSY': 'yellow',
        'OFFLINE': 'gray',
    }
    return colorize(state, colors.get(state, 'white'))


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


def format_guide(row: tuple) -> tuple:
    (guide_id, name, phone, email, state, chat, voice, video,
     tier, experience, availability, created_at) = row

    # Services enabled
    services = []
    if chat:
        services.append(colorize("C", "cyan"))
    if voice:
        services.append(colorize("V", "green"))
    if video:
        services.append(colorize("D", "magenta"))
    services_str = " ".join(services) if services else colorize("-", "gray")

    exp_str = f"{experience}y" if experience else "-"

    return (
        str(guide_id),
        name or "-",
        phone or "-",
        email[:30] + "..." if email and len(email) > 30 else (email or "-"),
        format_state(state),
        services_str,
        format_tier(tier),
        exp_str,
        format_availability(availability),
        fmt_datetime(created_at)
    )


# --- View Class ---

class OnboardGuideView(BaseView):
    name = "Guides"
    view_id = "onboard_guide"
    icon = "G"

    def get_containers(self) -> List[ContainerConfig]:
        columns = ["ID", "Name", "Phone", "Email", "State", "Services", "Tier", "Exp", "Availability", "Created"]
        return [
            ContainerConfig("guides-container", "ALL GUIDES (Press 'A' to add new)", [
                TableConfig("guides-table", columns, cursor=True)
            ])
        ]

    def fetch_data(self, **kwargs) -> dict:
        return {
            'guides': fetch_all_guides()
        }

    def format_rows(self, data: dict) -> dict:
        return {
            'guides-table': [format_guide(r) for r in data['guides']]
        }
