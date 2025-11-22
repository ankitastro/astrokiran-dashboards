#!/usr/bin/env python3
"""
AstroKiran Guides Online Dashboard
Real-time monitoring of guides availability with skills breakdown
Updates every 30 seconds with visual progress bar
"""

import os
import psycopg2
import asyncio
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, DataTable, ProgressBar
from textual.timer import Timer
from textual.worker import Worker, WorkerState
from dotenv import load_dotenv
from guide_queries import (
    get_guide_counts_query,
    get_channel_counts_query,
    get_skills_breakdown_query,
    get_online_guides_query,
    get_offline_guides_query,
    get_test_guides_query
)

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_ENDPOINT'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': 'astrokiran',
    'user': os.getenv('DB_USERNAME'),
    'password': os.getenv('DB_PASSWORD')
}


class MetricCard(Static):
    """A card displaying a single metric"""

    def __init__(self, title: str, value: str = "0", color: str = "green"):
        super().__init__()
        self.title = title
        self.value = value
        self.color = color

    def render(self) -> str:
        return f"[bold {self.color}]{self.title}[/]\n[bold white on {self.color}] {self.value} [/]"


class GuidesDashboard(App):
    """A Textual app to monitor guides online."""

    CSS = """
    Screen {
        background: $surface;
    }

    /* --- Refresh Timer Bar --- */
    #refresh-timer-container {
        height: auto;
        margin: 0 1;
    }
    
    #refresh-bar {
        width: 100%;
        margin-bottom: 1;
        tint: $accent; 
    }
    
    #refresh-label {
        text-align: right;
        color: $text-muted;
        text-style: italic;
    }

    /* --- Metrics --- */
    #metrics {
        height: 5;
        margin: 1;
    }

    .metric-card {
        width: 1fr;
        height: 5;
        border: solid $primary;
        padding: 1;
        margin: 0 1;
        text-align: center;
    }

    /* --- Tables --- */
    #skills-table {
        height: auto;
        max-height: 15;
        margin: 1;
        border: solid $accent;
    }

    #online-guides-table {
        height: auto;
        margin: 1;
        border: solid green;
    }

    #offline-guides-table {
        height: auto;
        margin: 1;
        border: solid red;
    }

    #test-guides-table {
        height: auto;
        margin: 1;
        border: solid yellow;
    }

    /* --- Loading Overlay --- */
    #loading-container {
        height: 5;
        margin: 1;
        background: $panel;
        border: solid yellow;
        display: none;
    }

    #loading-container.visible {
        display: block;
    }

    #loading-text {
        text-align: center;
        text-style: bold;
        color: $warning;
        margin-bottom: 1;
    }

    #loading-progress {
        width: 100%;
    }

    #last-update {
        height: 1;
        margin: 1;
        text-align: center;
        color: $text-muted;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh Now"),
    ]

    # Configuration for the refresh timer
    REFRESH_SECONDS = 30
    TICK_RATE = 0.1  # Update bar every 0.1 seconds

    def __init__(self):
        super().__init__()
        self.online_count = 0
        self.offline_count = 0
        self.total_count = 0
        self.online_chat = 0
        self.online_voice = 0
        self.online_video = 0
        self.online_guides_data = []
        self.offline_guides_data = []
        self.test_guides_data = []
        self.skills_data = []
        
        # Timer state
        self.timer_ticks = 0
        self.total_ticks = int(self.REFRESH_SECONDS / self.TICK_RATE)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()

        # New: Refresh Timer Bar
        with Container(id="refresh-timer-container"):
            yield Static(f"Next refresh in {self.REFRESH_SECONDS}s", id="refresh-label")
            yield ProgressBar(total=self.total_ticks, show_eta=False, id="refresh-bar")

        with Container(id="loading-container"):
            yield Static("⏳ Loading data...", id="loading-text")
            yield ProgressBar(id="loading-progress", show_eta=False)

        with Container(id="metrics"):
            with Horizontal():
                yield MetricCard("🟢 Online", "0", "green")
                yield MetricCard("🔴 Offline", "0", "red")
                yield MetricCard("💬 Chat", "0", "blue")
                yield MetricCard("🎤 Voice", "0", "cyan")
                yield MetricCard("📹 Video", "0", "magenta")

        yield Static("🎯 Skills Breakdown", classes="section-header")
        yield DataTable(id="skills-table")

        yield Static("🟢 Online Guides", classes="section-header")
        yield DataTable(id="online-guides-table")

        yield Static("🔴 Offline Guides", classes="section-header")
        yield DataTable(id="offline-guides-table")

        yield Static("🧪 Test Guides", classes="section-header")
        yield DataTable(id="test-guides-table")

        yield Static("Last updated: Never", id="last-update")
        yield Footer()

    def on_mount(self) -> None:
        """Set up the dashboard when mounted."""
        # Setup skills table
        skills_table = self.query_one("#skills-table", DataTable)
        skills_table.add_columns("Skill Name", "🟢 Online", "🔴 Offline", "Total")

        # Setup online guides table
        online_guides_table = self.query_one("#online-guides-table", DataTable)
        online_guides_table.cursor_type = "row"
        online_guides_table.add_columns("ID", "Name", "Chat", "Voice", "₹/min", "Earnings ₹", "PEND", "IP#", "IP Names", "COMP", "Today ₹", "REFU", "CANC")

        # Setup offline guides table
        offline_guides_table = self.query_one("#offline-guides-table", DataTable)
        offline_guides_table.cursor_type = "row"
        offline_guides_table.add_columns("ID", "Name", "Chat", "Voice", "₹/min", "Earnings ₹", "PEND", "IP#", "IP Names", "COMP", "Today ₹", "REFU", "CANC")

        # Setup test guides table
        test_guides_table = self.query_one("#test-guides-table", DataTable)
        test_guides_table.cursor_type = "row"
        test_guides_table.add_columns("ID", "Name", "Status", "Chat", "Voice", "₹/min", "Earnings ₹", "PEND", "IP#", "IP Names", "COMP", "Today ₹", "REFU", "CANC")

        # Initial data load
        self.fetch_data()

        # Set up tick timer (runs fast to animate bar)
        self.set_interval(self.TICK_RATE, self.tick_timer)

    def tick_timer(self) -> None:
        """Update the progress bar and trigger fetch if time is up."""
        self.timer_ticks += 1
        
        # Update Visuals
        bar = self.query_one("#refresh-bar", ProgressBar)
        bar.progress = self.timer_ticks
        
        # Optional: Update text label every second (every 10 ticks)
        if self.timer_ticks % 10 == 0:
            seconds_left = self.REFRESH_SECONDS - (self.timer_ticks * self.TICK_RATE)
            self.query_one("#refresh-label", Static).update(f"Next refresh in {int(seconds_left)}s")

        # Check if time to refresh
        if self.timer_ticks >= self.total_ticks:
            self.timer_ticks = 0
            bar.progress = 0
            self.fetch_data()

    def fetch_data(self) -> None:
        """Trigger data fetch using a worker."""
        self.run_worker(self._fetch_data_worker, thread=True, exclusive=True)

    def _fetch_data_worker(self) -> None:
        """Worker method to fetch data from the database."""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Query 1: Get counts
            cursor.execute(get_guide_counts_query())
            online, offline, total = cursor.fetchone()
            self.online_count = online
            self.offline_count = offline
            self.total_count = total

            # Query 2: Get channel counts
            cursor.execute(get_channel_counts_query())
            chat, voice, video = cursor.fetchone()
            self.online_chat = chat
            self.online_voice = voice
            self.online_video = video

            # Query 3: Get skill-wise online/offline counts
            cursor.execute(get_skills_breakdown_query())
            self.skills_data = cursor.fetchall()

            # Query 4: Get ONLINE guides WITH SKILLS AND EARNINGS
            cursor.execute(get_online_guides_query())
            self.online_guides_data = cursor.fetchall()

            # Query 5: Get OFFLINE guides WITH SKILLS AND EARNINGS
            cursor.execute(get_offline_guides_query())
            self.offline_guides_data = cursor.fetchall()

            # Query 6: Get TEST guides (Aman Jain and Praveen)
            cursor.execute(get_test_guides_query())
            self.test_guides_data = cursor.fetchall()

            cursor.close()
            conn.close()

        except Exception as e:
            self.call_from_thread(self.notify, f"Error fetching data: {str(e)}", severity="error")

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker state changes to show/hide loading indicator."""
        loading = self.query_one("#loading-container")
        loading_bar = self.query_one("#loading-progress", ProgressBar)

        if event.state == WorkerState.RUNNING:
            # Show loading indicator
            loading.add_class("visible")
            loading_bar.update(total=None)  # Indeterminate mode for the specific loading bar
        elif event.state in (WorkerState.SUCCESS, WorkerState.ERROR, WorkerState.CANCELLED):
            # Hide loading indicator
            loading.remove_class("visible")

            if event.state == WorkerState.SUCCESS:
                self.update_display()

    def update_display(self) -> None:
        """Update the display with latest data."""
        # Update metric cards
        metrics = self.query(MetricCard)
        if len(metrics) >= 5:
            metrics[0].value = str(self.online_count)
            metrics[0].refresh()

            metrics[1].value = str(self.offline_count)
            metrics[1].refresh()

            metrics[2].value = str(self.online_chat)
            metrics[2].refresh()

            metrics[3].value = str(self.online_voice)
            metrics[3].refresh()

            metrics[4].value = str(self.online_video)
            metrics[4].refresh()

        # Update skills table
        skills_table = self.query_one("#skills-table", DataTable)
        skills_table.clear()

        for skill in self.skills_data:
            skill_name, online, offline, total = skill
            skills_table.add_row(
                skill_name,
                str(online),
                str(offline),
                str(total)
            )

        # Update online guides table
        online_guides_table = self.query_one("#online-guides-table", DataTable)
        online_guides_table.clear()

        for guide in self.online_guides_data:
            guide_id, name, phone, chat, voice, video, skills, price_per_min, rating, consultations, earnings, today_p, today_ip_count, today_ip_customers, today_c, today_earnings, today_r, today_x = guide
            online_guides_table.add_row(
                str(guide_id),
                name or "N/A",
                "✓" if chat else "✗",
                "✓" if voice else "✗",
                f"{float(price_per_min):,.2f}" if price_per_min else "0.00",
                f"{float(earnings):,.2f}" if earnings else "0.00",
                str(today_p),
                str(today_ip_count),
                today_ip_customers if today_ip_customers and today_ip_customers != '-' else '-',
                str(today_c),
                f"{float(today_earnings):,.2f}" if today_earnings else "0.00",
                str(today_r),
                str(today_x)
            )

        # Update offline guides table
        offline_guides_table = self.query_one("#offline-guides-table", DataTable)
        offline_guides_table.clear()

        for guide in self.offline_guides_data:
            guide_id, name, phone, chat, voice, video, skills, price_per_min, rating, consultations, earnings, today_p, today_ip_count, today_ip_customers, today_c, today_earnings, today_r, today_x = guide
            offline_guides_table.add_row(
                str(guide_id),
                name or "N/A",
                "✓" if chat else "✗",
                "✓" if voice else "✗",
                f"{float(price_per_min):,.2f}" if price_per_min else "0.00",
                f"{float(earnings):,.2f}" if earnings else "0.00",
                str(today_p),
                str(today_ip_count),
                today_ip_customers if today_ip_customers and today_ip_customers != '-' else '-',
                str(today_c),
                f"{float(today_earnings):,.2f}" if today_earnings else "0.00",
                str(today_r),
                str(today_x)
            )

        # Update test guides table
        test_guides_table = self.query_one("#test-guides-table", DataTable)
        test_guides_table.clear()

        for guide in self.test_guides_data:
            guide_id, name, phone, status, chat, voice, video, skills, price_per_min, rating, consultations, earnings, today_p, today_ip_count, today_ip_customers, today_c, today_earnings, today_r, today_x = guide
            test_guides_table.add_row(
                str(guide_id),
                name or "N/A",
                "🟢 Online" if status == 'ONLINE_AVAILABLE' else "🔴 Offline",
                "✓" if chat else "✗",
                "✓" if voice else "✗",
                f"{float(price_per_min):,.2f}" if price_per_min else "0.00",
                f"{float(earnings):,.2f}" if earnings else "0.00",
                str(today_p),
                str(today_ip_count),
                today_ip_customers if today_ip_customers and today_ip_customers != '-' else '-',
                str(today_c),
                f"{float(today_earnings):,.2f}" if today_earnings else "0.00",
                str(today_r),
                str(today_x)
            )

        # Update timestamp
        timestamp = self.query_one("#last-update", Static)
        timestamp.update(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def action_refresh(self) -> None:
        """Manually refresh the data and reset timer."""
        self.notify("Refreshing data...", severity="information")
        # Reset the timer ticks so we don't double fetch
        self.timer_ticks = 0
        self.query_one("#refresh-bar", ProgressBar).progress = 0
        self.query_one("#refresh-label", Static).update(f"Next refresh in {self.REFRESH_SECONDS}s")
        self.fetch_data()


if __name__ == "__main__":
    app = GuidesDashboard()
    app.run()
