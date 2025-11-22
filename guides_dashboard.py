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
    get_test_guides_query,
    get_promo_grant_spending_query,
    get_latest_feedback_query
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

    def __init__(self, title: str, value: str = "0", color: str = "#8fb0ee"):
        super().__init__()
        self.title = title
        self.value = value
        self.color = color

    def render(self) -> str:
        return f"[bold {self.color}]{self.title}[/]\n[bold #e9e9e9]{self.value}[/]"


class GuidesDashboard(App):
    """A Textual app to monitor guides online."""

    CSS = """
    /* Dolphie-inspired Dark Blue Theme */
    Screen {
        background: #0a0e1b;
    }

    /* --- Refresh Timer Bar --- */
    #refresh-timer-container {
        height: auto;
        margin: 0 1;
        background: #0f1525;
    }

    #refresh-bar {
        width: 100%;
        margin-bottom: 1;
        color: #91abec;
        background: #131a2c;
    }

    #refresh-bar > .bar--bar {
        color: #91abec;
    }

    #refresh-bar > .bar--complete {
        color: #54efae;
    }

    #refresh-label {
        text-align: right;
        color: #bbc8e8;
        text-style: italic;
        padding: 0 1;
    }

    /* --- Metrics --- */
    #metrics {
        height: 5;
        margin: 1 1 0 1;
    }

    .metric-card {
        width: 1fr;
        height: 5;
        border: tall #1c2440;
        padding: 1;
        margin: 0 1;
        text-align: center;
        background: #0f1525;
    }

    /* --- Section Headers --- */
    .section-header {
        text-align: center;
        text-style: bold;
        color: #8fb0ee;
        background: #131a2c;
        padding: 0 1;
        margin: 1 1 0 1;
    }

    /* --- Tables --- */
    DataTable {
        height: auto;
        background: #0f1525;
        color: #e9e9e9;
    }

    DataTable > .datatable--header {
        background: #131a2c;
        color: #c5c7d2;
        text-style: bold;
    }

    DataTable > .datatable--odd-row {
        background: #131a2c;
    }

    DataTable > .datatable--even-row {
        background: #0f1525;
    }

    DataTable > .datatable--cursor {
        background: #1c2440;
    }

    DataTable > .datatable--hover {
        background: #171e2f;
    }

    #skills-table {
        max-height: 15;
        margin: 0 1 1 1;
        border: tall #32416a;
    }

    #online-guides-table {
        margin: 0 1 1 1;
        border: tall #54efae;
    }

    #offline-guides-table {
        margin: 0 1 1 1;
        border: tall #f05757;
    }

    #test-guides-table {
        margin: 0 1 1 1;
        border: tall #f0e357;
    }

    #promo-grant-table {
        max-height: 15;
        margin: 0 1 1 1;
        border: tall #91abec;
    }

    #feedback-table {
        max-height: 15;
        margin: 0 1 1 1;
        border: tall #5bd088;
    }

    #last-update {
        height: 1;
        margin: 0 1 1 1;
        text-align: center;
        color: #788bc9;
        background: #0f1525;
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
        self.promo_grant_data = []
        self.latest_feedback_data = []

        # Timer state
        self.timer_ticks = 0
        self.total_ticks = int(self.REFRESH_SECONDS / self.TICK_RATE)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)

        # Refresh Timer Bar
        with Container(id="refresh-timer-container"):
            yield Static(f"Next refresh in {self.REFRESH_SECONDS}s", id="refresh-label")
            yield ProgressBar(total=self.total_ticks, show_eta=False, id="refresh-bar")

        with Container(id="metrics"):
            with Horizontal():
                yield MetricCard("🟢 Online", "0", "#54efae")
                yield MetricCard("🔴 Offline", "0", "#f05757")
                yield MetricCard("💬 Chat", "0", "#91abec")
                yield MetricCard("🎤 Voice", "0", "#8fb0ee")
                yield MetricCard("📹 Video", "0", "#5c81d7")

        yield Static("🎯 Skills Breakdown", classes="section-header")
        yield DataTable(id="skills-table")

        yield Static("🟢 Online Guides", classes="section-header")
        yield DataTable(id="online-guides-table")

        yield Static("🔴 Offline Guides", classes="section-header")
        yield DataTable(id="offline-guides-table")

        yield Static("🧪 Test Guides", classes="section-header")
        yield DataTable(id="test-guides-table")

        yield Static("💎 Promo Grant Spending by Guide (since Nov 13)", classes="section-header")
        yield DataTable(id="promo-grant-table")

        yield Static("⭐ Latest Customer Feedback by Guide", classes="section-header")
        yield DataTable(id="feedback-table")

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

        # Setup promo grant spending table
        promo_grant_table = self.query_one("#promo-grant-table", DataTable)
        promo_grant_table.cursor_type = "row"
        promo_grant_table.add_columns("Consultant ID", "Guide Name", "💎 Grants Spent")

        # Setup feedback table
        feedback_table = self.query_one("#feedback-table", DataTable)
        feedback_table.cursor_type = "row"
        feedback_table.add_columns("Order ID", "Guide", "Customer", "⭐ Rating", "Feedback", "Date")

        # Initial data load
        self.fetch_data()

        # Set up tick timer (runs fast to animate bar)
        self.set_interval(self.TICK_RATE, self.tick_timer)

    def tick_timer(self) -> None:
        """Update progress bar and trigger fetch."""
        self.timer_ticks += 1

        bar = self.query_one("#refresh-bar", ProgressBar)
        bar.progress = self.timer_ticks

        if self.timer_ticks % 10 == 0:
            seconds_left = self.REFRESH_SECONDS - (self.timer_ticks * self.TICK_RATE)
            self.query_one("#refresh-label", Static).update(f"Next refresh in {int(seconds_left)}s")

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

            # Query 7: Get promo grant spending by guide
            cursor.execute(get_promo_grant_spending_query())
            self.promo_grant_data = cursor.fetchall()

            # Query 8: Get latest feedback by guide
            cursor.execute(get_latest_feedback_query())
            self.latest_feedback_data = cursor.fetchall()

            cursor.close()
            conn.close()

        except Exception as e:
            self.call_from_thread(self.notify, f"Error fetching data: {str(e)}", severity="error")

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker state changes and update display on success."""
        if event.state == WorkerState.SUCCESS:
            self.update_display()
        elif event.state == WorkerState.ERROR:
            self.notify("Failed to fetch guides data", severity="error")

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

        # Update promo grant spending table
        promo_grant_table = self.query_one("#promo-grant-table", DataTable)
        promo_grant_table.clear()

        for grant_row in self.promo_grant_data:
            consultant_id, guide_name, grants_count = grant_row
            promo_grant_table.add_row(
                str(consultant_id) if consultant_id else "N/A",
                guide_name or "Unknown Guide",
                str(grants_count)
            )

        # Update feedback table
        feedback_table = self.query_one("#feedback-table", DataTable)
        feedback_table.clear()

        for fb_row in self.latest_feedback_data:
            guide_id, guide_name, customer_name, rating, feedback_text, feedback_date, order_id = fb_row
            # Format rating with stars
            rating_str = "⭐" * int(rating) if rating else "-"
            # Truncate feedback to 50 chars for display
            feedback_short = (feedback_text[:50] + "...") if feedback_text and len(feedback_text) > 50 else (feedback_text or "-")
            # Format date
            date_str = feedback_date.strftime("%Y-%m-%d %H:%M") if feedback_date else "-"
            feedback_table.add_row(
                str(order_id) if order_id else "-",
                guide_name or "Unknown",
                customer_name or "Anonymous",
                rating_str,
                feedback_short,
                date_str
            )

        # Update timestamp
        timestamp = self.query_one("#last-update", Static)
        timestamp.update(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def action_refresh(self) -> None:
        """Manually refresh the data and reset timer."""
        self.timer_ticks = 0
        self.query_one("#refresh-bar", ProgressBar).progress = 0
        self.notify("Refreshing guides data...", severity="information")
        self.fetch_data()


if __name__ == "__main__":
    app = GuidesDashboard()
    app.run()
