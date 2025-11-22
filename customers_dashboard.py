#!/usr/bin/env python3
"""
AstroKiran Customers Dashboard
Real-time monitoring of customer analytics, segments, and revenue metrics
Updates every 30 seconds
"""

import os
import psycopg2
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, DataTable
from textual.timer import Timer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configurations
ASK_DESK_DB_CONFIG = {
    'host': os.getenv('DB_ENDPOINT'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': 'ask_desk_db_2',
    'user': os.getenv('DB_USERNAME'),
    'password': os.getenv('DB_PASSWORD')
}

ANALYTICS_DB_CONFIG = {
    'host': os.getenv('DB_ENDPOINT'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': 'analytics',
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


class CustomersDashboard(App):
    """A Textual app to monitor customer analytics."""

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

    #segments-table {
        height: auto;
        max-height: 12;
        margin: 1;
        border: solid $accent;
    }

    #top-customers-table {
        height: auto;
        margin: 1;
        border: solid green;
    }

    #recent-customers-table {
        height: auto;
        margin: 1;
        border: solid blue;
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
        self.total_customers = 0
        self.paid_customers = 0
        self.cart_abandoners = 0
        self.never_ordered = 0
        self.total_revenue = 0
        self.segments_data = []
        self.top_customers_data = []
        self.recent_customers_data = []

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()

        with Container(id="metrics"):
            with Horizontal():
                yield MetricCard("📊 Total Customers", "0", "blue")
                yield MetricCard("💰 Paid Customers", "0", "green")
                yield MetricCard("🛒 Cart Abandoners", "0", "yellow")
                yield MetricCard("👤 Never Ordered", "0", "red")
                yield MetricCard("💵 Total Revenue ₹", "0", "magenta")

        yield Static("🎯 Customer Segments by Problem Category", classes="section-header")
        yield DataTable(id="segments-table")

        yield Static("🌟 Top 20 Paying Customers", classes="section-header")
        yield DataTable(id="top-customers-table")

        yield Static("🕒 Recent 20 Customers", classes="section-header")
        yield DataTable(id="recent-customers-table")

        yield Static("Last updated: Never", id="last-update")
        yield Footer()

    def on_mount(self) -> None:
        """Set up the dashboard when mounted."""
        # Setup segments table
        segments_table = self.query_one("#segments-table", DataTable)
        segments_table.add_columns("Problem Category", "Customer Count", "% of Total")

        # Setup top customers table
        top_customers_table = self.query_one("#top-customers-table", DataTable)
        top_customers_table.add_columns("Phone", "Name", "Orders", "Total Spent ₹", "Last Order")

        # Setup recent customers table
        recent_customers_table = self.query_one("#recent-customers-table", DataTable)
        recent_customers_table.add_columns("Phone", "Name", "Status", "Created", "Last Activity")

        # Initial data load
        self.fetch_data()

        # Set up timer to refresh every 30 seconds
        self.set_interval(30, self.fetch_data)

    def fetch_data(self) -> None:
        """Fetch data from the databases."""
        try:
            # Connect to ask_desk_db_2
            conn_main = psycopg2.connect(**ASK_DESK_DB_CONFIG)
            cursor_main = conn_main.cursor()

            # Query 1: Get customer segment counts
            cursor_main.execute("""
                SELECT
                    COUNT(DISTINCT c.id) as total_customers,
                    COUNT(DISTINCT CASE
                        WHEN pt.status = 'CAPTURED' OR o.status IN ('DELIVERED', 'FEEDBACK_DELIVERED')
                        THEN c.id
                    END) as paid_customers,
                    COUNT(DISTINCT CASE
                        WHEN o.status = 'PENDING_PAYMENT' THEN c.id
                    END) as cart_abandoners,
                    COUNT(DISTINCT CASE
                        WHEN o.id IS NULL THEN c.id
                    END) as never_ordered
                FROM customers_customer c
                LEFT JOIN orders_order o ON c.id = o.customer_id
                LEFT JOIN payments_paymenttransaction pt ON o.id = pt.order_id
            """)
            total, paid, cart_abandon, never_ord = cursor_main.fetchone()
            self.total_customers = total
            self.paid_customers = paid
            self.cart_abandoners = cart_abandon
            self.never_ordered = never_ord

            # Query 2: Get total revenue
            cursor_main.execute("""
                SELECT COALESCE(SUM(amount), 0)
                FROM payments_paymenttransaction
                WHERE status = 'CAPTURED'
            """)
            self.total_revenue = cursor_main.fetchone()[0] or 0

            # Query 3: Get top paying customers
            cursor_main.execute("""
                SELECT
                    c.phone_number,
                    c.whatsapp_profile_name,
                    COUNT(DISTINCT o.id) as order_count,
                    COALESCE(SUM(pt.amount), 0) as total_spent,
                    MAX(o.created_at) as last_order_date
                FROM customers_customer c
                JOIN orders_order o ON c.id = o.customer_id
                JOIN payments_paymenttransaction pt ON o.id = pt.order_id
                WHERE pt.status = 'CAPTURED'
                GROUP BY c.id, c.phone_number, c.whatsapp_profile_name
                ORDER BY total_spent DESC
                LIMIT 20
            """)
            self.top_customers_data = cursor_main.fetchall()

            # Query 4: Get recent customers
            cursor_main.execute("""
                SELECT
                    c.phone_number,
                    c.whatsapp_profile_name,
                    CASE
                        WHEN EXISTS (
                            SELECT 1 FROM payments_paymenttransaction pt
                            JOIN orders_order o2 ON pt.order_id = o2.id
                            WHERE o2.customer_id = c.id AND pt.status = 'CAPTURED'
                        ) THEN 'Paid'
                        WHEN EXISTS (
                            SELECT 1 FROM orders_order o2
                            WHERE o2.customer_id = c.id AND o2.status = 'PENDING_PAYMENT'
                        ) THEN 'Cart Abandon'
                        ELSE 'New'
                    END as customer_status,
                    c.created_at,
                    c.updated_at
                FROM customers_customer c
                ORDER BY c.created_at DESC
                LIMIT 20
            """)
            self.recent_customers_data = cursor_main.fetchall()

            cursor_main.close()
            conn_main.close()

            # Connect to analytics database
            conn_analytics = psycopg2.connect(**ANALYTICS_DB_CONFIG)
            cursor_analytics = conn_analytics.cursor()

            # Query 5: Get customer segments by problem category
            cursor_analytics.execute("""
                WITH total_discussed AS (
                    SELECT COUNT(DISTINCT customer_phone_number) as total
                    FROM consultation_transcripts
                    WHERE info->>'was_problem_discussed' = 'true'
                )
                SELECT
                    'Financial Problems' as category,
                    COUNT(DISTINCT customer_phone_number) as count,
                    ROUND(100.0 * COUNT(DISTINCT customer_phone_number) / (SELECT total FROM total_discussed), 1) as percentage
                FROM consultation_transcripts
                WHERE info->>'was_problem_discussed' = 'true'
                  AND LOWER(info->>'client_problem') ~ '(financial|money|debt|loan|expense|loss)'
                UNION ALL
                SELECT 'Career/Job Issues', COUNT(DISTINCT customer_phone_number),
                       ROUND(100.0 * COUNT(DISTINCT customer_phone_number) / (SELECT total FROM total_discussed), 1)
                FROM consultation_transcripts
                WHERE info->>'was_problem_discussed' = 'true'
                  AND LOWER(info->>'client_problem') ~ '(job|career|employment|government job)'
                UNION ALL
                SELECT 'Business Issues', COUNT(DISTINCT customer_phone_number),
                       ROUND(100.0 * COUNT(DISTINCT customer_phone_number) / (SELECT total FROM total_discussed), 1)
                FROM consultation_transcripts
                WHERE info->>'was_problem_discussed' = 'true'
                  AND LOWER(info->>'client_problem') ~ '(business|shop|trading|contractor|factory)'
                UNION ALL
                SELECT 'Marriage Related', COUNT(DISTINCT customer_phone_number),
                       ROUND(100.0 * COUNT(DISTINCT customer_phone_number) / (SELECT total FROM total_discussed), 1)
                FROM consultation_transcripts
                WHERE info->>'was_problem_discussed' = 'true'
                  AND LOWER(info->>'client_problem') ~ '(marriage|husband|wife|spouse|manglik)'
                ORDER BY count DESC
            """)
            self.segments_data = cursor_analytics.fetchall()

            cursor_analytics.close()
            conn_analytics.close()

            # Update UI
            self.update_display()

        except Exception as e:
            self.notify(f"Error fetching data: {str(e)}", severity="error")

    def update_display(self) -> None:
        """Update the display with latest data."""
        # Update metric cards
        metrics = self.query(MetricCard)
        if len(metrics) >= 5:
            metrics[0].value = f"{self.total_customers:,}"
            metrics[0].refresh()

            metrics[1].value = f"{self.paid_customers:,}"
            metrics[1].refresh()

            metrics[2].value = f"{self.cart_abandoners:,}"
            metrics[2].refresh()

            metrics[3].value = f"{self.never_ordered:,}"
            metrics[3].refresh()

            metrics[4].value = f"{float(self.total_revenue):,.2f}"
            metrics[4].refresh()

        # Update segments table
        segments_table = self.query_one("#segments-table", DataTable)
        segments_table.clear()

        for segment in self.segments_data:
            category, count, percentage = segment
            segments_table.add_row(
                category,
                f"{count:,}",
                f"{percentage}%"
            )

        # Update top customers table
        top_customers_table = self.query_one("#top-customers-table", DataTable)
        top_customers_table.clear()

        for customer in self.top_customers_data:
            phone, name, orders, total_spent, last_order = customer
            top_customers_table.add_row(
                phone or "N/A",
                name or "N/A",
                str(orders),
                f"{float(total_spent):,.2f}",
                last_order.strftime('%Y-%m-%d %H:%M') if last_order else "N/A"
            )

        # Update recent customers table
        recent_customers_table = self.query_one("#recent-customers-table", DataTable)
        recent_customers_table.clear()

        for customer in self.recent_customers_data:
            phone, name, status, created, updated = customer
            recent_customers_table.add_row(
                phone or "N/A",
                name or "N/A",
                status,
                created.strftime('%Y-%m-%d %H:%M') if created else "N/A",
                updated.strftime('%Y-%m-%d %H:%M') if updated else "N/A"
            )

        # Update timestamp
        timestamp = self.query_one("#last-update", Static)
        timestamp.update(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def action_refresh(self) -> None:
        """Manually refresh the data."""
        self.notify("Refreshing data...", severity="information")
        self.fetch_data()


if __name__ == "__main__":
    app = CustomersDashboard()
    app.run()
