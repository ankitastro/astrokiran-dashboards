"""
Offer Edit Modal - Edit existing offers.
"""

from datetime import datetime, timezone, timedelta
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Static, Input, Button, Label, Select, SelectionList
from textual.screen import ModalScreen

from constants import OFFER_TYPES, TRIGGER_TYPES, SERVICE_TYPES, VOUCHER_SUBTYPES, GUIDE_TIERS
from db import execute_update


IST = timezone(timedelta(hours=5, minutes=30))
UTC = timezone.utc


class OfferEditScreen(ModalScreen):
    """Modal for editing offer values."""

    CSS = """
    OfferEditScreen { align: center middle; }
    #edit-dialog { width: 80; height: auto; max-height: 90%; border: thick #32416a; background: #0f1525; padding: 1 2; overflow-y: auto; }
    #edit-title { text-align: center; text-style: bold; color: #8fb0ee; margin-bottom: 1; }
    .field-row { height: 3; margin-bottom: 1; }
    .field-label { width: 20; }
    .field-input { width: 55; }
    .field-select { width: 55; }
    .section-title { text-style: bold; color: #f0e357; margin-top: 1; margin-bottom: 1; }
    .selection-list { height: 5; width: 55; }
    #button-row { height: 3; margin-top: 1; }
    #save-btn { margin-right: 2; }
    #edit-hint { text-align: center; color: #788bc9; text-style: italic; margin-top: 1; }
    .editing { border: solid #00ff00; }
    """

    BINDINGS = [
        ("ctrl+s", "submit", "Save"),
    ]

    def __init__(self, offer_data: dict):
        super().__init__()
        self.offer_data = offer_data
        self.edit_mode = False  # Track if we're editing a field
        # Get current guide tiers (stored as lowercase in DB)
        current_tiers = offer_data.get('target_guide_tiers') or []
        self.selected_tiers = set(current_tiers)

    def _format_ts(self, val) -> str:
        """Format timestamp for display in input field (IST)."""
        if not val:
            return ""
        if hasattr(val, 'astimezone'):
            val = val.astimezone(IST)
        if hasattr(val, 'strftime'):
            return val.strftime("%Y-%m-%d %H:%M:%S")
        return str(val)[:19]

    def compose(self) -> ComposeResult:
        current_type = self.offer_data.get('offer_type', 'COMBO_OFFER')
        current_trigger = self.offer_data.get('trigger_type') or 'ON_RECHARGE'
        current_service = self.offer_data.get('service_type') or 'ALL'
        current_subtype = self.offer_data.get('voucher_subtype') or ''
        with Container(id="edit-dialog"):
            yield Static("Edit Offer", id="edit-title")
            with Horizontal(classes="field-row"):
                yield Label("Name:", classes="field-label")
                yield Input(value=self.offer_data.get('name', ''), id="input-name", classes="field-input")
            with Horizontal(classes="field-row"):
                yield Label("Description:", classes="field-label")
                yield Input(value=self.offer_data.get('description', ''), id="input-desc", classes="field-input")
            with Horizontal(classes="field-row"):
                yield Label("Type:", classes="field-label")
                yield Select(options=OFFER_TYPES, value=current_type, id="select-type", classes="field-select")
            with Horizontal(classes="field-row"):
                yield Label("Subtype:", classes="field-label")
                yield Select(options=VOUCHER_SUBTYPES, value=current_subtype or Select.BLANK, allow_blank=True, id="select-subtype", classes="field-select")
            with Horizontal(classes="field-row"):
                yield Label("Service Type:", classes="field-label")
                yield Select(options=SERVICE_TYPES, value=current_service, id="select-service", classes="field-select")
            with Horizontal(classes="field-row"):
                yield Label("Trigger:", classes="field-label")
                yield Select(options=TRIGGER_TYPES, value=current_trigger, id="select-trigger", classes="field-select")
            with Horizontal(classes="field-row"):
                yield Label("Cashback %:", classes="field-label")
                yield Input(value=str(self.offer_data.get('bonus_pct', 0)), id="input-pct", classes="field-input")
            with Horizontal(classes="field-row"):
                yield Label("Free Minutes:", classes="field-label")
                yield Input(value=str(self.offer_data.get('free_mins', 0)), id="input-mins", classes="field-input")
            with Horizontal(classes="field-row"):
                yield Label("Min Recharge:", classes="field-label")
                yield Input(value=str(self.offer_data.get('min_amt', 0)), id="input-min", classes="field-input")
            with Horizontal(classes="field-row"):
                yield Label("Max Recharge:", classes="field-label")
                yield Input(value=str(self.offer_data.get('max_amt', 0)), id="input-max", classes="field-input")
            with Horizontal(classes="field-row"):
                yield Label("Usage Limit:", classes="field-label")
                yield Input(value=str(self.offer_data.get('usage_limit', 0)), id="input-limit", classes="field-input")
            with Horizontal(classes="field-row"):
                yield Label("CTA Text:", classes="field-label")
                yield Input(value=self.offer_data.get('cta_text', ''), id="input-cta", classes="field-input")
            yield Static("Guide Tiers (select multiple)", classes="section-title")
            tier_items = [(label, value, value in self.selected_tiers) for value, label in GUIDE_TIERS]
            yield SelectionList(*tier_items, id="select-tiers", classes="selection-list")
            with Horizontal(classes="field-row"):
                yield Label("Valid From:", classes="field-label")
                yield Input(value=self._format_ts(self.offer_data.get('valid_from')), id="input-valid-from", classes="field-input", placeholder="YYYY-MM-DD HH:MM:SS")
            with Horizontal(classes="field-row"):
                yield Label("Valid To:", classes="field-label")
                yield Input(value=self._format_ts(self.offer_data.get('valid_to')), id="input-valid-to", classes="field-input", placeholder="YYYY-MM-DD HH:MM:SS")
            with Horizontal(classes="field-row"):
                yield Label("Active (1/0):", classes="field-label")
                yield Input(value="1" if self.offer_data.get('is_active') else "0", id="input-active", classes="field-input")
            with Horizontal(id="button-row"):
                yield Button("Save", id="save-btn", variant="success")
                yield Button("Cancel", id="cancel-btn", variant="default")
            yield Static("↑↓←→ Navigate | Enter Edit/Select | Ctrl+S Save | Esc Cancel", id="edit-hint")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            self._save()
        else:
            self.dismiss(False)

    def action_cancel(self) -> None:
        self.dismiss(False)

    def action_submit(self) -> None:
        """Submit the form."""
        self._save()

    def _get_focusable_widgets(self):
        """Get all focusable widgets in order."""
        widgets = []
        for widget in self.query("Input, Select, SelectionList, Button"):
            widgets.append(widget)
        return widgets

    def _focus_by_offset(self, offset: int) -> None:
        """Move focus by offset in the widget list."""
        widgets = self._get_focusable_widgets()
        if not widgets:
            return
        focused = self.focused
        try:
            current_idx = widgets.index(focused) if focused in widgets else -1
        except ValueError:
            current_idx = -1
        new_idx = (current_idx + offset) % len(widgets)
        widgets[new_idx].focus()

    def on_key(self, event) -> None:
        """Handle navigation and edit mode."""
        focused = self.focused

        # EDIT MODE: let widget handle keys, Escape exits
        if self.edit_mode:
            if event.key == "escape":
                self.edit_mode = False
                if focused:
                    focused.remove_class("editing")
                self._update_hint()
                event.stop()
                event.prevent_default()
            # Let all other keys pass through to the widget
            return

        # NAVIGATION MODE
        if event.key == "down":
            self._focus_by_offset(1)
            event.stop()
            event.prevent_default()
        elif event.key == "up":
            self._focus_by_offset(-1)
            event.stop()
            event.prevent_default()
        elif event.key == "left":
            self._focus_by_offset(-1)
            event.stop()
            event.prevent_default()
        elif event.key == "right":
            self._focus_by_offset(1)
            event.stop()
            event.prevent_default()
        elif event.key == "enter":
            # Enter edit mode for inputs/selects, activate buttons
            if isinstance(focused, Button):
                focused.press()
            elif isinstance(focused, (Input, Select, SelectionList)):
                self.edit_mode = True
                focused.add_class("editing")
                self._update_hint()
            event.stop()
            event.prevent_default()
        elif event.key == "escape":
            self.dismiss(False)
            event.stop()
            event.prevent_default()
        else:
            # Block all other keys in navigation mode (no typing)
            event.stop()
            event.prevent_default()

    def _update_hint(self) -> None:
        """Update hint text based on mode."""
        hint = self.query_one("#edit-hint", Static)
        if self.edit_mode:
            hint.update("EDIT MODE | Esc to exit | Type to edit")
        else:
            hint.update("↑↓←→ Navigate | Enter Edit/Select | Ctrl+S Save | Esc Cancel")

    def on_click(self, event) -> None:
        """Prevent clicks outside dialog from closing modal."""
        event.stop()

    def _parse_ist_to_utc(self, val: str):
        """Parse IST datetime string and convert to UTC."""
        if not val:
            return None
        dt = datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
        dt_ist = dt.replace(tzinfo=IST)
        return dt_ist.astimezone(UTC)

    def _save(self) -> None:
        try:
            name = self.query_one("#input-name", Input).value.strip()
            description = self.query_one("#input-desc", Input).value.strip()
            offer_type = self.query_one("#select-type", Select).value
            subtype_val = self.query_one("#select-subtype", Select).value
            voucher_subtype = None if subtype_val == Select.BLANK else subtype_val
            service_type = self.query_one("#select-service", Select).value
            trigger_type = self.query_one("#select-trigger", Select).value
            pct = float(self.query_one("#input-pct", Input).value or 0)
            mins = int(self.query_one("#input-mins", Input).value or 0)
            min_amt = float(self.query_one("#input-min", Input).value or 0)
            max_amt = float(self.query_one("#input-max", Input).value or 0)
            usage_limit = int(self.query_one("#input-limit", Input).value or 0)
            cta_text = self.query_one("#input-cta", Input).value.strip()
            valid_from = self._parse_ist_to_utc(self.query_one("#input-valid-from", Input).value.strip())
            valid_to = self._parse_ist_to_utc(self.query_one("#input-valid-to", Input).value.strip())
            active = self.query_one("#input-active", Input).value == "1"

            # Get selected guide tiers
            tiers_list = self.query_one("#select-tiers", SelectionList)
            selected_tier_ids = list(tiers_list.selected)

            # Free minutes only valid for COMBO_OFFER and VOUCHER
            if offer_type not in ('COMBO_OFFER', 'VOUCHER'):
                mins = 0

            # Convert tiers to PostgreSQL array format
            if selected_tier_ids:
                tiers_array = '{' + ','.join(selected_tier_ids) + '}'
            else:
                tiers_array = '{}'

            query = """
            UPDATE offers.offer_definitions
            SET offer_name = %s,
                description = %s,
                offer_type = %s,
                voucher_subtype = %s,
                service_type = %s,
                trigger_type = %s,
                bonus_percentage = %s,
                free_minutes = %s,
                min_recharge_amount = %s,
                max_recharge_amount = %s,
                usage_limit_per_user = %s,
                cta_text = %s,
                target_guide_tiers = %s,
                valid_from = %s,
                valid_to = %s,
                is_active = %s,
                updated_at = NOW()
            WHERE offer_id = %s
            """
            execute_update(query, (name, description, offer_type, voucher_subtype, service_type, trigger_type, pct, mins, min_amt, max_amt, usage_limit, cta_text, tiers_array, valid_from, valid_to, active, self.offer_data['offer_id']))
            self.dismiss(True)
        except Exception as e:
            self.query_one("#edit-hint", Static).update(f"Error: {str(e)[:40]}")
