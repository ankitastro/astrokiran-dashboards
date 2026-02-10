"""
Guide Onboard Modal - Onboard new guides or edit existing ones.
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Static, Input, Button, Label, Select, SelectionList
from textual.screen import ModalScreen

from constants import ONBOARDING_STATES, TIER_OPTIONS
from db import execute_update, execute_insert_returning, execute_query


def get_skills():
    """Fetch available skills from DB."""
    rows = execute_query('SELECT id, name FROM guide.skills ORDER BY name')
    return [(str(r[0]), r[1]) for r in rows]


def get_languages():
    """Fetch available languages from DB."""
    rows = execute_query('SELECT id, name FROM guide.languages ORDER BY name')
    return [(str(r[0]), r[1]) for r in rows]


def get_guide_skills(guide_id):
    """Get skill IDs for a guide."""
    rows = execute_query('SELECT skill_id FROM guide.guide_skills WHERE guide_id = %s', (guide_id,))
    return [str(r[0]) for r in rows]


def get_guide_languages(guide_id):
    """Get language IDs for a guide."""
    rows = execute_query('SELECT language_id FROM guide.guide_languages WHERE guide_id = %s', (guide_id,))
    return [str(r[0]) for r in rows]


class GuideOnboardScreen(ModalScreen):
    """Modal for onboarding a new guide."""

    CSS = """
    GuideOnboardScreen { align: center middle; }
    #onboard-dialog { width: 95; height: auto; max-height: 90%; border: thick #32416a; background: #0f1525; padding: 1 2; overflow-y: auto; }
    #onboard-title { text-align: center; text-style: bold; color: #8fb0ee; margin-bottom: 1; }
    .field-row { height: 3; margin-bottom: 1; }
    .field-label { width: 22; }
    .field-input { width: 65; }
    .field-select { width: 65; }
    .section-title { text-style: bold; color: #f0e357; margin-top: 1; margin-bottom: 1; }
    #button-row { height: 3; margin-top: 1; }
    #save-btn { margin-right: 2; }
    #onboard-hint { text-align: center; color: #788bc9; text-style: italic; margin-top: 1; }
    .selection-list { height: 6; width: 65; }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, guide_data: dict = None):
        super().__init__()
        self.guide_data = guide_data or {}
        self.is_edit = bool(guide_data and guide_data.get('guide_id'))
        self.all_skills = get_skills()
        self.all_languages = get_languages()
        if self.is_edit:
            self.selected_skills = set(get_guide_skills(guide_data['guide_id']))
            self.selected_languages = set(get_guide_languages(guide_data['guide_id']))
        else:
            self.selected_skills = {'3'}  # Default: Astrology
            self.selected_languages = {'1', '2'}  # Default: English, Hindi

    def compose(self) -> ComposeResult:
        title = "Edit Guide" if self.is_edit else "Onboard New Guide"
        with Container(id="onboard-dialog"):
            yield Static(title, id="onboard-title")

            # Basic Info Section
            yield Static("Basic Information", classes="section-title")
            with Horizontal(classes="field-row"):
                yield Label("Full Name:", classes="field-label")
                yield Input(value=self.guide_data.get('name', ''), id="input-name", classes="field-input", placeholder="Full name of the guide")
            with Horizontal(classes="field-row"):
                yield Label("Phone Number:", classes="field-label")
                yield Input(value=self.guide_data.get('phone', ''), id="input-phone", classes="field-input", placeholder="10-digit phone number")
            with Horizontal(classes="field-row"):
                yield Label("Email:", classes="field-label")
                yield Input(value=self.guide_data.get('email', ''), id="input-email", classes="field-input", placeholder="email@example.com")
            with Horizontal(classes="field-row"):
                yield Label("Years of Experience:", classes="field-label")
                yield Input(value=str(self.guide_data.get('experience', 0)), id="input-experience", classes="field-input", placeholder="0")

            # Skills & Languages Section
            yield Static("Skills (select multiple)", classes="section-title")
            skill_items = [(sname, sid, sid in self.selected_skills) for sid, sname in self.all_skills]
            yield SelectionList(*skill_items, id="select-skills", classes="selection-list")

            yield Static("Languages (select multiple)", classes="section-title")
            lang_items = [(lname, lid, lid in self.selected_languages) for lid, lname in self.all_languages]
            yield SelectionList(*lang_items, id="select-languages", classes="selection-list")

            # Status Section
            yield Static("Status & Tier", classes="section-title")
            with Horizontal(classes="field-row"):
                yield Label("Onboarding State:", classes="field-label")
                yield Select(options=ONBOARDING_STATES, value=self.guide_data.get('state', 'ACTIVE'), id="select-state", classes="field-select")
            with Horizontal(classes="field-row"):
                yield Label("Tier:", classes="field-label")
                tier_value = (self.guide_data.get('tier') or 'basic').lower()
                yield Select(options=TIER_OPTIONS, value=tier_value, id="select-tier", classes="field-select")

            # Services Section
            yield Static("Services Enabled (1=Yes, 0=No)", classes="section-title")
            with Horizontal(classes="field-row"):
                yield Label("Chat Enabled:", classes="field-label")
                yield Input(value="1" if self.guide_data.get('chat_enabled') else "0", id="input-chat", classes="field-input")
            with Horizontal(classes="field-row"):
                yield Label("Voice Enabled:", classes="field-label")
                yield Input(value="1" if self.guide_data.get('voice_enabled') else "0", id="input-voice", classes="field-input")
            with Horizontal(classes="field-row"):
                yield Label("Video Enabled:", classes="field-label")
                yield Input(value="1" if self.guide_data.get('video_enabled') else "0", id="input-video", classes="field-input")

            # Rates Section (only for new guides)
            if not self.is_edit:
                yield Static("Initial Rates (Rs/min)", classes="section-title")
                with Horizontal(classes="field-row"):
                    yield Label("Chat Rate:", classes="field-label")
                    yield Input(value="10", id="input-chat-rate", classes="field-input", placeholder="Rate per minute")
                with Horizontal(classes="field-row"):
                    yield Label("Voice Rate:", classes="field-label")
                    yield Input(value="15", id="input-voice-rate", classes="field-input", placeholder="Rate per minute")
                with Horizontal(classes="field-row"):
                    yield Label("Video Rate:", classes="field-label")
                    yield Input(value="20", id="input-video-rate", classes="field-input", placeholder="Rate per minute")

            with Horizontal(id="button-row"):
                yield Button("Save" if self.is_edit else "Create", id="save-btn", variant="success")
                yield Button("Cancel", id="cancel-btn", variant="default")
            yield Static("Tab to navigate, Space to select", id="onboard-hint")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            self._save()
        else:
            self.dismiss(False)

    def action_cancel(self) -> None:
        self.dismiss(False)

    def _save(self) -> None:
        try:
            name = self.query_one("#input-name", Input).value.strip()
            phone = self.query_one("#input-phone", Input).value.strip()
            email = self.query_one("#input-email", Input).value.strip()
            experience = int(self.query_one("#input-experience", Input).value or 0)
            state = self.query_one("#select-state", Select).value
            tier = self.query_one("#select-tier", Select).value
            chat_enabled = self.query_one("#input-chat", Input).value == "1"
            voice_enabled = self.query_one("#input-voice", Input).value == "1"
            video_enabled = self.query_one("#input-video", Input).value == "1"

            # Get selected skills and languages
            skills_list = self.query_one("#select-skills", SelectionList)
            languages_list = self.query_one("#select-languages", SelectionList)
            selected_skill_ids = [int(s) for s in skills_list.selected]
            selected_lang_ids = [int(l) for l in languages_list.selected]

            if not name or not phone or not email:
                self.query_one("#onboard-hint", Static).update("Error: Name, Phone, Email required")
                return

            if not selected_skill_ids:
                self.query_one("#onboard-hint", Static).update("Error: Select at least one skill")
                return

            if not selected_lang_ids:
                self.query_one("#onboard-hint", Static).update("Error: Select at least one language")
                return

            if self.is_edit:
                guide_id = self.guide_data['guide_id']
                # Update existing guide
                query = """
                UPDATE guide.guide_profile
                SET full_name = %s,
                    phone_number = %s,
                    email = %s,
                    years_of_experience = %s,
                    onboarding_state = %s,
                    tier = %s,
                    chat_enabled = %s,
                    voice_enabled = %s,
                    video_enabled = %s,
                    updated_at = NOW()
                WHERE id = %s
                """
                execute_update(query, (name, phone, email, experience, state, tier,
                                       chat_enabled, voice_enabled, video_enabled, guide_id))

                # Update skills - delete old and insert new
                execute_update('DELETE FROM guide.guide_skills WHERE guide_id = %s', (guide_id,))
                for skill_id in selected_skill_ids:
                    execute_update(
                        'INSERT INTO guide.guide_skills (guide_id, skill_id, created_at) VALUES (%s, %s, NOW())',
                        (guide_id, skill_id)
                    )

                # Update languages - delete old and insert new
                execute_update('DELETE FROM guide.guide_languages WHERE guide_id = %s', (guide_id,))
                for lang_id in selected_lang_ids:
                    execute_update(
                        'INSERT INTO guide.guide_languages (guide_id, language_id, created_at) VALUES (%s, %s, NOW())',
                        (guide_id, lang_id)
                    )
            else:
                # Create new guide
                # First check if auth user already exists
                full_phone = '+91' + phone
                existing_auth = execute_query(
                    'SELECT id FROM auth.auth_users WHERE phone_number = %s OR full_phone = %s LIMIT 1',
                    (phone, full_phone)
                )

                if existing_auth:
                    # Use existing auth user
                    auth_id = existing_auth[0][0]
                    # Check if this auth user is already linked to a guide
                    existing_guide = execute_query(
                        'SELECT id, full_name FROM guide.guide_profile WHERE x_auth_id = %s',
                        (auth_id,)
                    )
                    if existing_guide:
                        self.query_one("#onboard-hint", Static).update(f"Error: Phone already used by {existing_guide[0][1]}")
                        return
                else:
                    # Create new auth user
                    auth_query = """
                    INSERT INTO auth.auth_users (area_code, phone_number, full_phone, is_active, is_test_user)
                    VALUES ('+91', %s, %s, true, false)
                    RETURNING id
                    """
                    result = execute_insert_returning(auth_query, (phone, full_phone))
                    if not result:
                        self.query_one("#onboard-hint", Static).update("Error: Failed to create auth user")
                        return
                    auth_id = result[0][0]

                # Generate email if not provided
                if not email:
                    email = f"{name.lower().replace(' ', '_')}_{phone}@example.com"

                # Create guide profile with channel names
                guide_query = """
                INSERT INTO guide.guide_profile (
                    x_auth_id, full_name, phone_number, email,
                    onboarding_state, chat_enabled, voice_enabled, video_enabled,
                    tier, years_of_experience, voice_channel_name, video_channel_name
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """
                # Channel names will be updated after we get the guide_id
                result = execute_insert_returning(guide_query, (auth_id, name, phone, email, state,
                                                                chat_enabled, voice_enabled, video_enabled,
                                                                tier, experience, '', ''))
                if not result:
                    self.query_one("#onboard-hint", Static).update("Error: Failed to create guide")
                    return
                guide_id = result[0][0]

                # Update channel names with guide_id
                voice_channel = f"voice_{guide_id}_{phone}"
                video_channel = f"video_{guide_id}_{phone}"
                execute_update('''
                    UPDATE guide.guide_profile
                    SET voice_channel_name = %s, video_channel_name = %s
                    WHERE id = %s
                ''', (voice_channel, video_channel, guide_id))

                # Create wallet.consultants entry
                execute_update('''
                    INSERT INTO wallet.consultants (
                        consultant_id, name, tenant_id, specialization, rating,
                        price_per_minute, revenue_share, accepts_promotional_offers,
                        created_at, tenant_consultant_id, updated_at, phone_number
                    ) VALUES (%s, %s, 1, 'Astrology', NULL, 10.00, 50.00, true, NOW(), %s, NOW(), %s)
                ''', (guide_id, name, str(guide_id), phone))

                # Create wallet.consultant_wallets entry
                execute_update('''
                    INSERT INTO wallet.consultant_wallets (
                        consultant_id, name, phone_number, specialization, rating,
                        revenue_share, accepts_promotional_offers, created_at, updated_at
                    ) VALUES (%s, %s, %s, 'Astrology', NULL, 50, true, NOW(), NOW())
                ''', (guide_id, name, phone))

                # Create initial rates
                chat_rate = float(self.query_one("#input-chat-rate", Input).value or 10)
                voice_rate = float(self.query_one("#input-voice-rate", Input).value or 15)
                video_rate = float(self.query_one("#input-video-rate", Input).value or 20)

                rates_query = """
                INSERT INTO offers.consultant_rates (consultant_id, service_type, base_rate, is_active)
                VALUES (%s, %s, %s, true)
                """
                execute_update(rates_query, (guide_id, 'CHAT', chat_rate))
                execute_update(rates_query, (guide_id, 'VOICE', voice_rate))
                execute_update(rates_query, (guide_id, 'VIDEO', video_rate))

                # Add selected skills
                for skill_id in selected_skill_ids:
                    execute_update(
                        'INSERT INTO guide.guide_skills (guide_id, skill_id, created_at) VALUES (%s, %s, NOW())',
                        (guide_id, skill_id)
                    )

                # Add selected languages
                for lang_id in selected_lang_ids:
                    execute_update(
                        'INSERT INTO guide.guide_languages (guide_id, language_id, created_at) VALUES (%s, %s, NOW())',
                        (guide_id, lang_id)
                    )

                # Fix properties.reports to be empty array instead of null
                execute_update('''
                    UPDATE guide.guide_profile
                    SET properties = jsonb_set(properties, '{reports}', '[]'::jsonb)
                    WHERE id = %s
                ''', (guide_id,))

            self.dismiss(True)
        except Exception as e:
            self.query_one("#onboard-hint", Static).update(f"Error: {str(e)[:50]}")
