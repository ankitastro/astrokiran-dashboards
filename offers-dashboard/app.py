#!/usr/bin/env python3
"""
Offers Dashboard - Visualize offers, consumptions, and user segments.
Press 'D' to switch views, 'R' to refresh, 'Q' to quit.
"""

from datetime import datetime
from typing import Optional
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Static, DataTable, ProgressBar
from textual.worker import Worker, WorkerState

from styles import DASHBOARD_CSS
from helpers import setup_table, update_table
from views.registry import ViewRegistry
from views.offers import OffersView
from views.reservations import ReservationsView
from views.rates import RatesView
from views.users import UsersView
from views.first_time import FirstTimeView
from views.consultation_rates import ConsultationRatesView
from views.onboard_guide import OnboardGuideView
from modals import (
    ViewSelectorScreen,
    OfferEditScreen,
    OfferAddScreen,
    RateEditScreen,
    GuideOnboardScreen,
)


# --- Register Views ---
ViewRegistry.register(OffersView())
ViewRegistry.register(FirstTimeView())
ViewRegistry.register(ConsultationRatesView())
ViewRegistry.register(OnboardGuideView())
ViewRegistry.register(ReservationsView())
ViewRegistry.register(RatesView())
ViewRegistry.register(UsersView())


class OffersDashboard(App):
    """Offers dashboard app with multi-view support."""

    CSS = DASHBOARD_CSS
    REFRESH_SECONDS = 30

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("d", "switch_view", "Views"),
        ("e", "edit_offer", "Edit"),
        ("a", "add_offer", "Add"),
        ("n", "next_page", "Next"),
        ("p", "prev_page", "Prev"),
        ("t", "next_table", "Switch Table"),
    ]

    def __init__(self):
        super().__init__()
        self.current_view_id = "offers"
        self.view_data = {}
        self.page = 1
        self.per_page = 50
        self.timer_ticks = 0
        self.total_ticks = int(self.REFRESH_SECONDS / 0.1)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="timer-container"):
            yield Static(f"Auto-refresh: {self.REFRESH_SECONDS}s", id="timer-label")
            yield ProgressBar(total=self.total_ticks, show_eta=False, id="timer-bar")
        # Render all views (hidden by default except current)
        for view in ViewRegistry.all():
            hidden = "hidden" if view.view_id != self.current_view_id else ""
            with Container(id=f"view-{view.view_id}", classes=hidden):
                for cfg in view.get_containers():
                    with Container(id=cfg.id):
                        yield Static(cfg.header, classes="section-header")
                        for tbl in cfg.tables:
                            yield DataTable(id=tbl.id)
        yield Static("Last updated: Never", id="last-update")
        yield Footer()

    def on_mount(self) -> None:
        # Setup tables for all views
        for view in ViewRegistry.all():
            for cfg in view.get_containers():
                for tbl in cfg.tables:
                    table = self.query_one(f"#{tbl.id}", DataTable)
                    setup_table(table, tbl.columns, tbl.cursor)
        self.fetch_data()
        self.set_interval(0.1, self._tick)

    def _tick(self) -> None:
        self.timer_ticks += 1
        bar = self.query_one("#timer-bar", ProgressBar)
        bar.progress = self.timer_ticks
        if self.timer_ticks % 10 == 0:
            secs = self.REFRESH_SECONDS - int(self.timer_ticks * 0.1)
            self.query_one("#timer-label", Static).update(f"Auto-refresh: {secs}s")
        if self.timer_ticks >= self.total_ticks:
            self._reset_timer()
            self.fetch_data()

    def _reset_timer(self) -> None:
        self.timer_ticks = 0
        self.query_one("#timer-bar", ProgressBar).progress = 0
        self.query_one("#timer-label", Static).update(f"Auto-refresh: {self.REFRESH_SECONDS}s")

    def fetch_data(self) -> None:
        self.run_worker(self._fetch_worker, thread=True, exclusive=True)

    def _fetch_worker(self) -> dict:
        view = ViewRegistry.get(self.current_view_id)
        return view.fetch_data(page=self.page, per_page=self.per_page)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.state == WorkerState.SUCCESS:
            self.view_data = event.worker.result
            self._update_display()

    def _update_display(self) -> None:
        view = ViewRegistry.get(self.current_view_id)
        rows = view.format_rows(self.view_data)
        first_focused = False
        for table_id, table_rows in rows.items():
            table = self.query_one(f"#{table_id}", DataTable)
            update_table(table, table_rows)
            # Focus only the first table with cursor for arrow key navigation
            if not first_focused and hasattr(view, 'get_containers'):
                for cfg in view.get_containers():
                    for tbl in cfg.tables:
                        if tbl.id == table_id and tbl.cursor:
                            table.focus()
                            first_focused = True
                            break
                    if first_focused:
                        break
        self.query_one("#last-update", Static).update(
            f"Last updated: {datetime.now().strftime('%H:%M:%S')} | Page {self.page}"
        )

    def _switch_to_view(self, view_id: str) -> None:
        if view_id == self.current_view_id:
            return
        self.query_one(f"#view-{self.current_view_id}").add_class("hidden")
        self.query_one(f"#view-{view_id}").remove_class("hidden")
        self.current_view_id = view_id
        self.page = 1
        self.fetch_data()

    # --- Actions ---

    def action_refresh(self) -> None:
        self._reset_timer()
        self.fetch_data()

    def action_switch_view(self) -> None:
        def handle(view_id: Optional[str]) -> None:
            if view_id:
                self._switch_to_view(view_id)
        self.push_screen(ViewSelectorScreen(), handle)

    def action_edit_offer(self) -> None:
        if self.current_view_id == "consultation_rates":
            self._edit_rate()
        elif self.current_view_id == "onboard_guide":
            self._edit_guide()
        elif self.current_view_id == "first_time":
            self._edit_offer()

    def action_add_offer(self) -> None:
        if self.current_view_id == "onboard_guide":
            self._add_guide()
        elif self.current_view_id == "first_time":
            self._add_offer()

    def action_next_page(self) -> None:
        self.page += 1
        self.fetch_data()

    def action_prev_page(self) -> None:
        if self.page > 1:
            self.page -= 1
            self.fetch_data()

    def action_next_table(self) -> None:
        """Cycle focus between tables with cursor enabled."""
        view = ViewRegistry.get(self.current_view_id)
        cursor_tables = []
        for cfg in view.get_containers():
            for tbl in cfg.tables:
                if tbl.cursor:
                    cursor_tables.append(tbl.id)
        if len(cursor_tables) <= 1:
            return
        # Find current focused table and move to next
        current_idx = -1
        for i, table_id in enumerate(cursor_tables):
            table = self.query_one(f"#{table_id}", DataTable)
            if table.has_focus:
                current_idx = i
                break
        next_idx = (current_idx + 1) % len(cursor_tables)
        self.query_one(f"#{cursor_tables[next_idx]}", DataTable).focus()

    # --- Edit/Add Handlers ---

    def _edit_offer(self) -> None:
        """Edit an offer."""
        row = self._get_selected_offer_row()
        if not row:
            return

        offer_data = {
            'offer_id': row[0],
            'name': row[1],
            'offer_type': row[2],
            'voucher_subtype': row[10] or '',
            'trigger_type': row[11],
            'bonus_pct': float(row[4] or 0),
            'free_mins': int(row[6] or 0),
            'min_amt': float(row[7] or 0),
            'max_amt': float(row[8] or 0),
            'valid_from': row[12],
            'valid_to': row[13],
            'is_active': row[14],
            'description': row[15] or '',
            'service_type': row[16] or 'ALL',
            'usage_limit': int(row[17] or 0),
            'cta_text': row[18] or '',
            'target_guide_tiers': row[19] or [],
        }

        def handle_edit(saved: bool) -> None:
            if saved:
                self.fetch_data()

        self.push_screen(OfferEditScreen(offer_data), handle_edit)

    def _get_selected_offer_row(self):
        """Get the selected row from offers tables."""
        row = None
        for table_id, data_key in [("first-time-table", "first_time"), ("regular-table", "regular")]:
            try:
                table = self.query_one(f"#{table_id}", DataTable)
                if table.has_focus and data_key in self.view_data:
                    idx = table.cursor_row
                    if idx is not None and idx < len(self.view_data[data_key]):
                        return self.view_data[data_key][idx]
            except:
                pass

        # Default to first-time-table if no focus
        if 'first_time' in self.view_data and self.view_data['first_time']:
            table = self.query_one("#first-time-table", DataTable)
            idx = table.cursor_row
            if idx is not None and idx < len(self.view_data['first_time']):
                return self.view_data['first_time'][idx]
        return None

    def _add_offer(self) -> None:
        """Add a new offer."""
        target = "FIRST_TIME"
        try:
            table = self.query_one("#regular-table", DataTable)
            if table.has_focus:
                target = "REGULAR"
        except:
            pass

        def handle_add(saved: bool) -> None:
            if saved:
                self.fetch_data()

        self.push_screen(OfferAddScreen(target), handle_add)

    def _edit_rate(self) -> None:
        """Edit consultation rate."""
        if 'rates' not in self.view_data or not self.view_data['rates']:
            return

        table = self.query_one("#rates-table", DataTable)
        idx = table.cursor_row
        if idx is None or idx >= len(self.view_data['rates']):
            return

        row = self.view_data['rates'][idx]
        rate_data = {
            'consultant_id': row[0],
            'name': row[1],
            'chat_rate_id': row[2],
            'chat_rate': float(row[3] or 0) if row[3] else 0,
            'voice_rate_id': row[4],
            'voice_rate': float(row[5] or 0) if row[5] else 0,
            'video_rate_id': row[6],
            'video_rate': float(row[7] or 0) if row[7] else 0,
            'is_active': row[8],
            'tier': row[9] or 'basic',
        }

        def handle_edit(saved: bool) -> None:
            if saved:
                self.fetch_data()

        self.push_screen(RateEditScreen(rate_data), handle_edit)

    def _edit_guide(self) -> None:
        """Edit a guide."""
        if 'guides' not in self.view_data or not self.view_data['guides']:
            return

        table = self.query_one("#guides-table", DataTable)
        idx = table.cursor_row
        if idx is None or idx >= len(self.view_data['guides']):
            return

        row = self.view_data['guides'][idx]
        guide_data = {
            'guide_id': row[0],
            'name': row[1],
            'phone': row[2],
            'email': row[3],
            'state': row[4],
            'chat_enabled': row[5],
            'voice_enabled': row[6],
            'video_enabled': row[7],
            'tier': row[8].lower() if row[8] else 'basic',
            'experience': row[9] or 0,
        }

        def handle_edit(saved: bool) -> None:
            if saved:
                self.fetch_data()

        self.push_screen(GuideOnboardScreen(guide_data), handle_edit)

    def _add_guide(self) -> None:
        """Add a new guide."""
        def handle_add(saved: bool) -> None:
            if saved:
                self.fetch_data()

        self.push_screen(GuideOnboardScreen(), handle_add)


if __name__ == "__main__":
    OffersDashboard().run()
