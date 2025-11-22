"""
Guide Hover Handler
Handles displaying guide skills when hovering/selecting rows in the dashboard
"""

from textual.widgets import Static


class GuideHoverInfo(Static):
    """Widget to display guide information on hover/selection"""

    def __init__(self):
        super().__init__("")
        self.guide_skills_map = {}

    def update_skills_map(self, skills_map: dict):
        """Update the mapping of guide IDs to their skills"""
        self.guide_skills_map = skills_map

    def show_guide_skills(self, guide_id: int, guide_name: str):
        """Display skills for a guide"""
        skills = self.guide_skills_map.get(guide_id, "No skills")
        self.update(f"💡 [bold cyan]{guide_name}[/] → Skills: [yellow]{skills}[/]")

    def clear_info(self):
        """Clear the hover information"""
        self.update("")


def build_skills_map(online_data, offline_data, test_data):
    """
    Build a mapping of guide IDs to their skills from guide data

    Args:
        online_data: List of online guides data
        offline_data: List of offline guides data
        test_data: List of test guides data

    Returns:
        dict: Mapping of guide_id -> skills string
    """
    skills_map = {}

    # Build skills map from all guide data
    # Online/Offline data format: guide_id, name, phone, chat, voice, video, skills, ...
    for guide in online_data:
        guide_id = guide[0]
        skills = guide[6]  # skills is at index 6
        skills_map[guide_id] = skills if skills else "No skills"

    for guide in offline_data:
        guide_id = guide[0]
        skills = guide[6]  # skills is at index 6
        skills_map[guide_id] = skills if skills else "No skills"

    # Test data format: guide_id, name, phone, status, chat, voice, video, skills, ...
    for guide in test_data:
        guide_id = guide[0]
        skills = guide[7]  # skills is at index 7 (because of status column)
        skills_map[guide_id] = skills if skills else "No skills"

    return skills_map


def get_guide_info_from_row_index(row_index: int, data_list):
    """
    Get guide ID and name from a row index in a data list

    Args:
        row_index: The row index
        data_list: List of guide data

    Returns:
        tuple: (guide_id, guide_name) or (None, None) if not found
    """
    try:
        if 0 <= row_index < len(data_list):
            guide = data_list[row_index]
            return guide[0], guide[1]  # guide_id, name
    except (ValueError, IndexError):
        pass

    return None, None
