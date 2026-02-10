"""
Offer Add Modal - Add new offers.
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


class OfferAddScreen(ModalScreen):
    """Modal for adding new offers."""

    CSS = """
    OfferAddScreen { align: center middle; }
    #add-dialog { width: 80; height: auto; max-height: 90%; border: thick #32416a; background: #0f1525; padding: 1 2; overflow-y: auto; }
    #add-title { text-align: center; text-style: bold; color: #8fb0ee; margin-bottom: 1; }
    .field-row { height: 3; margin-bottom: 1; }
    .field-label { width: 20; }
    .field-input { width: 55; }
    .field-select { width: 55; }
    .section-title { text-style: bold; color: #f0e357; margin-top: 1; margin-bottom: 1; }
    .selection-list { height: 5; width: 55; }
    #button-row { height: 3; margin-top: 1; }
    #save-btn { margin-right: 2; }
    #add-hint { text-align: center; color: #788bc9; text-style: italic; margin-top: 1; }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, target_user_type: str = "FIRST_TIME"):
        super().__init__()
        self.target_user_type = target_user_type

    def compose(self) -> ComposeResult:
        target_options = [("FIRST_TIME", "FIRST_TIME"), ("REGULAR", "REGULAR")]
        with Container(id="add-dialog"):
            yield Static("Add New Offer", id="add-title")
            with Horizontal(classes="field-row"):
                yield Label("Name:", classes="field-label")
                yield Input(id="input-name", classes="field-input", placeholder="Offer name")
            with Horizontal(classes="field-row"):
                yield Label("Description:", classes="field-label")
                yield Input(id="input-desc", classes="field-input", placeholder="Offer description")
            with Horizontal(classes="field-row"):
                yield Label("Type:", classes="field-label")
                yield Select(options=OFFER_TYPES, value="COMBO_OFFER", id="select-type", classes="field-select")
            with Horizontal(classes="field-row"):
                yield Label("Subtype:", classes="field-label")
                yield Select(options=VOUCHER_SUBTYPES, value=Select.BLANK, allow_blank=True, id="select-subtype", classes="field-select")
            with Horizontal(classes="field-row"):
                yield Label("Category:", classes="field-label")
                yield Input(value="RECHARGE", id="input-category", classes="field-input", placeholder="RECHARGE/CONSULTATION/PROMOTION")
            with Horizontal(classes="field-row"):
                yield Label("Service Type:", classes="field-label")
                yield Select(options=SERVICE_TYPES, value="ALL", id="select-service", classes="field-select")
            with Horizontal(classes="field-row"):
                yield Label("Target Users:", classes="field-label")
                yield Select(options=target_options, value=self.target_user_type, id="select-target", classes="field-select")
            with Horizontal(classes="field-row"):
                yield Label("Trigger:", classes="field-label")
                yield Select(options=TRIGGER_TYPES, value="ON_RECHARGE", id="select-trigger", classes="field-select")
            with Horizontal(classes="field-row"):
                yield Label("Cashback %:", classes="field-label")
                yield Input(value="0", id="input-pct", classes="field-input")
            with Horizontal(classes="field-row"):
                yield Label("Free Minutes:", classes="field-label")
                yield Input(value="0", id="input-mins", classes="field-input")
            with Horizontal(classes="field-row"):
                yield Label("Min Recharge:", classes="field-label")
                yield Input(value="0", id="input-min", classes="field-input")
            with Horizontal(classes="field-row"):
                yield Label("Max Recharge:", classes="field-label")
                yield Input(value="0", id="input-max", classes="field-input")
            with Horizontal(classes="field-row"):
                yield Label("Usage Limit:", classes="field-label")
                yield Input(value="0", id="input-limit", classes="field-input", placeholder="0 = unlimited")
            with Horizontal(classes="field-row"):
                yield Label("CTA Text:", classes="field-label")
                yield Input(id="input-cta", classes="field-input", placeholder="e.g. Recharge Now")
            yield Static("Guide Tiers (select multiple)", classes="section-title")
            tier_items = [(label, value, True) for value, label in GUIDE_TIERS]  # Default: all selected
            yield SelectionList(*tier_items, id="select-tiers", classes="selection-list")
            with Horizontal(classes="field-row"):
                yield Label("Valid From:", classes="field-label")
                yield Input(id="input-valid-from", classes="field-input", placeholder="YYYY-MM-DD HH:MM:SS (IST)")
            with Horizontal(classes="field-row"):
                yield Label("Valid To:", classes="field-label")
                yield Input(id="input-valid-to", classes="field-input", placeholder="YYYY-MM-DD HH:MM:SS (IST)")
            with Horizontal(id="button-row"):
                yield Button("Create", id="save-btn", variant="success")
                yield Button("Cancel", id="cancel-btn", variant="default")
            yield Static("Tab to navigate fields", id="add-hint")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            self._save()
        else:
            self.dismiss(False)

    def action_cancel(self) -> None:
        self.dismiss(False)

    def _parse_ist_to_utc(self, val: str):
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
            category = self.query_one("#input-category", Input).value.strip()
            service_type = self.query_one("#select-service", Select).value
            target = self.query_one("#select-target", Select).value
            trigger_type = self.query_one("#select-trigger", Select).value
            pct = float(self.query_one("#input-pct", Input).value or 0)
            mins = int(self.query_one("#input-mins", Input).value or 0)
            min_amt = float(self.query_one("#input-min", Input).value or 0)
            max_amt = float(self.query_one("#input-max", Input).value or 0)
            usage_limit = int(self.query_one("#input-limit", Input).value or 0)
            cta_text = self.query_one("#input-cta", Input).value.strip()
            valid_from = self._parse_ist_to_utc(self.query_one("#input-valid-from", Input).value.strip())
            valid_to = self._parse_ist_to_utc(self.query_one("#input-valid-to", Input).value.strip())

            if not name or not valid_from or not valid_to:
                self.query_one("#add-hint", Static).update("Error: Name, Valid From, Valid To required")
                return

            # Get selected guide tiers
            tiers_list = self.query_one("#select-tiers", SelectionList)
            selected_tier_ids = list(tiers_list.selected)

            # Free minutes only valid for COMBO_OFFER and VOUCHER
            if offer_type not in ('COMBO_OFFER', 'VOUCHER'):
                mins = 0

            # Convert target to array format
            target_array = '{' + target + '}'

            # Convert tiers to PostgreSQL array format
            if selected_tier_ids:
                tiers_array = '{' + ','.join(selected_tier_ids) + '}'
            else:
                tiers_array = '{}'

            query = """
            INSERT INTO offers.offer_definitions (
                offer_name, description, offer_type, voucher_subtype, offer_category, service_type, target_user_types,
                trigger_type, bonus_percentage, free_minutes, min_recharge_amount, max_recharge_amount,
                usage_limit_per_user, cta_text, target_guide_tiers, valid_from, valid_to, is_active
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, true)
            """
            execute_update(query, (name, description, offer_type, voucher_subtype, category, service_type, target_array, trigger_type, pct, mins, min_amt, max_amt, usage_limit, cta_text, tiers_array, valid_from, valid_to))
            self.dismiss(True)
        except Exception as e:
            self.query_one("#add-hint", Static).update(f"Error: {str(e)[:40]}")
