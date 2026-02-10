"""
Rate Edit Modal - Edit consultation rates.
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Static, Input, Button, Label
from textual.screen import ModalScreen

from db import execute_update


class RateEditScreen(ModalScreen):
    """Modal for editing consultation rates."""

    CSS = """
    RateEditScreen { align: center middle; }
    #edit-dialog { width: 70; height: auto; border: thick #32416a; background: #0f1525; padding: 1 2; }
    #edit-title { text-align: center; text-style: bold; color: #8fb0ee; margin-bottom: 1; }
    .field-row { height: 3; margin-bottom: 1; }
    .field-label { width: 20; }
    .field-input { width: 45; }
    #button-row { height: 3; margin-top: 1; }
    #save-btn { margin-right: 2; }
    #edit-hint { text-align: center; color: #788bc9; text-style: italic; margin-top: 1; }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, rate_data: dict):
        super().__init__()
        self.rate_data = rate_data

    def compose(self) -> ComposeResult:
        with Container(id="edit-dialog"):
            yield Static(f"Edit Rates: {self.rate_data['name']} (ID: {self.rate_data['consultant_id']})", id="edit-title")
            with Horizontal(classes="field-row"):
                yield Label("Chat Rate (Rs/min):", classes="field-label")
                yield Input(value=str(self.rate_data.get('chat_rate') or 0), id="input-chat", classes="field-input")
            with Horizontal(classes="field-row"):
                yield Label("Voice Rate (Rs/min):", classes="field-label")
                yield Input(value=str(self.rate_data.get('voice_rate') or 0), id="input-voice", classes="field-input")
            with Horizontal(classes="field-row"):
                yield Label("Video Rate (Rs/min):", classes="field-label")
                yield Input(value=str(self.rate_data.get('video_rate') or 0), id="input-video", classes="field-input")
            with Horizontal(classes="field-row"):
                yield Label("Active (1/0):", classes="field-label")
                yield Input(value="1" if self.rate_data.get('is_active') else "0", id="input-active", classes="field-input")
            with Horizontal(id="button-row"):
                yield Button("Save", id="save-btn", variant="success")
                yield Button("Cancel", id="cancel-btn", variant="default")
            yield Static("Tab to navigate, Enter to save", id="edit-hint")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            self._save()
        else:
            self.dismiss(False)

    def action_cancel(self) -> None:
        self.dismiss(False)

    def _save(self) -> None:
        try:
            chat_rate = float(self.query_one("#input-chat", Input).value or 0)
            voice_rate = float(self.query_one("#input-voice", Input).value or 0)
            video_rate = float(self.query_one("#input-video", Input).value or 0)
            active = self.query_one("#input-active", Input).value == "1"

            # Update each rate
            query = """
            UPDATE offers.consultant_rates
            SET base_rate = %s, is_active = %s, updated_at = NOW()
            WHERE rate_id = %s
            """
            if self.rate_data.get('chat_rate_id'):
                execute_update(query, (chat_rate, active, self.rate_data['chat_rate_id']))
            if self.rate_data.get('voice_rate_id'):
                execute_update(query, (voice_rate, active, self.rate_data['voice_rate_id']))
            if self.rate_data.get('video_rate_id'):
                execute_update(query, (video_rate, active, self.rate_data['video_rate_id']))

            self.dismiss(True)
        except Exception as e:
            self.query_one("#edit-hint", Static).update(f"Error: {str(e)[:40]}")
