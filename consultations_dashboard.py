#!/usr/bin/env python3
"""
AstroKiran Consultations Dashboard
Real-time monitoring of consultation metrics - today, yesterday, day before yesterday
Updates every 30 seconds
"""

import os
import psycopg2
from datetime import datetime, timedelta
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, DataTable
from textual.timer import Timer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
ASTROKIRAN_DB_CONFIG = {
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


class ConsultationsDashboard(App):
    """A Textual app to monitor consultation metrics."""

    CSS = """
    Screen {
        background: $surface;
    }

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

    #mode-breakdown-table {
        height: auto;
        max-height: 12;
        margin: 1;
        border: solid $accent;
    }

    #recent-consultations-table {
        height: auto;
        margin: 1;
        border: solid blue;
    }

    #hourly-breakdown-table {
        height: auto;
        margin: 1;
        border: solid green;
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

    def __init__(self):
        super().__init__()
        self.today_count = 0
        self.yesterday_count = 0
        self.day_before_yesterday_count = 0
        self.total_count = 0
        self.avg_duration = 0
        self.mode_breakdown_data = []
        self.recent_consultations_data = []
        self.hourly_breakdown_data = []

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()

        with Container(id="metrics"):
            with Horizontal():
                yield MetricCard("📅 Today", "0", "green")
                yield MetricCard("📆 Yesterday", "0", "blue")
                yield MetricCard("📋 Day Before", "0", "yellow")
                yield MetricCard("📊 Total (All Time)", "0", "magenta")
                yield MetricCard("⏱️ Avg Duration (min)", "0", "cyan")

        yield Static("📊 Consultations by Mode (Today, Yesterday, Day Before)", classes="section-header")
        yield DataTable(id="mode-breakdown-table")

        yield Static("⏰ Today's Hourly Breakdown", classes="section-header")
        yield DataTable(id="hourly-breakdown-table")

        yield Static("🕒 Recent 20 Consultations", classes="section-header")
        yield DataTable(id="recent-consultations-table")

        yield Static("Last updated: Never", id="last-update")
        yield Footer()

    def on_mount(self) -> None:
        """Set up the dashboard when mounted."""
        # Setup mode breakdown table
        mode_table = self.query_one("#mode-breakdown-table", DataTable)
        mode_table.add_columns("Mode", "Today", "Yesterday", "Day Before", "Total")

        # Setup hourly breakdown table
        hourly_table = self.query_one("#hourly-breakdown-table", DataTable)
        hourly_table.add_columns("Hour", "Call", "Chat", "Total")

        # Setup recent consultations table
        recent_table = self.query_one("#recent-consultations-table", DataTable)
        recent_table.add_columns("ID", "Customer", "Guide", "Mode", "Duration (min)", "Completed At", "Rating")

        # Initial data load
        self.fetch_data()

        # Set up timer to refresh every 30 seconds
        self.set_interval(30, self.fetch_data)

    def fetch_data(self) -> None:
        """Fetch data from the database."""
        try:
            # Connect to astrokiran database
            conn = psycopg2.connect(**ASTROKIRAN_DB_CONFIG)
            cursor = conn.cursor()

            # Get timezone-aware dates (assuming IST)
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            yesterday_start = today_start - timedelta(days=1)
            day_before_yesterday_start = today_start - timedelta(days=2)

            # Query 1: Get consultations count by day (using wallet_orders)
            cursor.execute("""
                SELECT
                    COUNT(*) FILTER (WHERE wo.completed_at >= %s) as today_count,
                    COUNT(*) FILTER (WHERE wo.completed_at >= %s AND wo.completed_at < %s) as yesterday_count,
                    COUNT(*) FILTER (WHERE wo.completed_at >= %s AND wo.completed_at < %s) as day_before_count,
                    COUNT(*) as total_count,
                    COALESCE(AVG(COALESCE(wo.minutes_ordered, 0) + COALESCE(wo.seconds_ordered, 0) / 60.0), 0) as avg_duration_minutes
                FROM wallet.wallet_orders wo
                WHERE wo.status = 'COMPLETED'
                  AND wo.service_type IN ('CHAT', 'CALL')
            """, (
                today_start,
                yesterday_start, today_start,
                day_before_yesterday_start, yesterday_start
            ))

            result = cursor.fetchone()
            self.today_count = result[0] or 0
            self.yesterday_count = result[1] or 0
            self.day_before_yesterday_count = result[2] or 0
            self.total_count = result[3] or 0
            self.avg_duration = result[4] or 0

            # Query 2: Get consultations by service type for each day
            cursor.execute("""
                SELECT
                    wo.service_type,
                    COUNT(*) FILTER (WHERE wo.completed_at >= %s) as today_count,
                    COUNT(*) FILTER (WHERE wo.completed_at >= %s AND wo.completed_at < %s) as yesterday_count,
                    COUNT(*) FILTER (WHERE wo.completed_at >= %s AND wo.completed_at < %s) as day_before_count,
                    COUNT(*) as total_count
                FROM wallet.wallet_orders wo
                WHERE wo.status = 'COMPLETED'
                  AND wo.service_type IN ('CHAT', 'CALL')
                GROUP BY wo.service_type
                ORDER BY wo.service_type
            """, (
                today_start,
                yesterday_start, today_start,
                day_before_yesterday_start, yesterday_start
            ))
            self.mode_breakdown_data = cursor.fetchall()

            # Query 3: Get hourly breakdown for today
            cursor.execute("""
                SELECT
                    EXTRACT(HOUR FROM wo.completed_at) as hour,
                    COUNT(*) FILTER (WHERE wo.service_type = 'CALL') as call_count,
                    COUNT(*) FILTER (WHERE wo.service_type = 'CHAT') as chat_count,
                    COUNT(*) as total_count
                FROM wallet.wallet_orders wo
                WHERE wo.status = 'COMPLETED'
                  AND wo.service_type IN ('CHAT', 'CALL')
                  AND wo.completed_at >= %s
                GROUP BY EXTRACT(HOUR FROM wo.completed_at)
                ORDER BY hour
            """, (today_start,))
            self.hourly_breakdown_data = cursor.fetchall()

            # Query 4: Get recent consultations (JOIN wallet_orders with consultation)
            cursor.execute("""
                SELECT
                    wo.order_id,
                    c.customer_name,
                    c.guide_name,
                    wo.service_type,
                    ROUND(COALESCE(wo.minutes_ordered, 0) + COALESCE(wo.seconds_ordered, 0) / 60.0, 1) as duration_minutes,
                    wo.completed_at,
                    c.rating
                FROM wallet.wallet_orders wo
                LEFT JOIN consultation.consultation c ON wo.order_id = c.order_id
                WHERE wo.status = 'COMPLETED'
                  AND wo.service_type IN ('CHAT', 'CALL')
                ORDER BY wo.completed_at DESC
                LIMIT 20
            """)
            self.recent_consultations_data = cursor.fetchall()

            cursor.close()
            conn.close()

            # Update UI
            self.update_display()

        except Exception as e:
            self.notify(f"Error fetching data: {str(e)}", severity="error")

    def update_display(self) -> None:
        """Update the display with latest data."""
        # Update metric cards
        metrics = self.query(MetricCard)
        if len(metrics) >= 5:
            metrics[0].value = f"{self.today_count:,}"
            metrics[0].refresh()

            metrics[1].value = f"{self.yesterday_count:,}"
            metrics[1].refresh()

            metrics[2].value = f"{self.day_before_yesterday_count:,}"
            metrics[2].refresh()

            metrics[3].value = f"{self.total_count:,}"
            metrics[3].refresh()

            metrics[4].value = f"{self.avg_duration:.1f}"
            metrics[4].refresh()

        # Update mode breakdown table
        mode_table = self.query_one("#mode-breakdown-table", DataTable)
        mode_table.clear()

        for mode_data in self.mode_breakdown_data:
            mode, today, yesterday, day_before, total = mode_data
            mode_table.add_row(
                mode.upper(),
                f"{today:,}",
                f"{yesterday:,}",
                f"{day_before:,}",
                f"{total:,}"
            )

        # Add totals row
        if self.mode_breakdown_data:
            mode_table.add_row(
                "[bold]TOTAL[/]",
                f"[bold]{self.today_count:,}[/]",
                f"[bold]{self.yesterday_count:,}[/]",
                f"[bold]{self.day_before_yesterday_count:,}[/]",
                f"[bold]{self.total_count:,}[/]"
            )

        # Update hourly breakdown table
        hourly_table = self.query_one("#hourly-breakdown-table", DataTable)
        hourly_table.clear()

        for hourly_data in self.hourly_breakdown_data:
            hour, call, chat, total = hourly_data
            hour_str = f"{int(hour):02d}:00-{int(hour):02d}:59"
            hourly_table.add_row(
                hour_str,
                f"{call:,}",
                f"{chat:,}",
                f"{total:,}"
            )

        # Update recent consultations table
        recent_table = self.query_one("#recent-consultations-table", DataTable)
        recent_table.clear()

        for consultation in self.recent_consultations_data:
            cons_id, customer, guide, mode, duration, completed_at, rating = consultation
            recent_table.add_row(
                str(cons_id),
                customer or "N/A",
                guide or "N/A",
                mode.upper(),
                f"{duration:.1f}",
                completed_at.strftime('%Y-%m-%d %H:%M:%S') if completed_at else "N/A",
                f"⭐{rating}" if rating else "N/A"
            )

        # Update timestamp
        timestamp = self.query_one("#last-update", Static)
        timestamp.update(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def action_refresh(self) -> None:
        """Manually refresh the data."""
        self.notify("Refreshing data...", severity="information")
        self.fetch_data()


if __name__ == "__main__":
    app = ConsultationsDashboard()
    app.run()
