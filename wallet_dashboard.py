#!/usr/bin/env python3
"""
AstroKiran Wallet Dashboard - ALL USERS VIEW
Real-time monitoring of ALL user wallet balances, recharges, and spending.
Auto-refreshes every 10 seconds to show latest data.
"""

import os
import psycopg2
import re
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Static, DataTable, ProgressBar
from textual.worker import Worker, WorkerState
from dotenv import load_dotenv

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

# --- SQL QUERIES ---

# KPI Metrics: Today's Recharge (from invoices), Virtual Cash, Today's Revenue, Today's Spends
KPI_QUERY = """
SELECT
    (SELECT COALESCE(SUM(total_amount), 0) FROM wallet.invoices WHERE created_at >= CURRENT_DATE) as today_recharge_invoices,
    (SELECT COALESCE(SUM(virtual_cash), 0) FROM wallet.user_wallets WHERE deleted_at IS NULL) as total_virtual_liability,
    (SELECT COALESCE(SUM(amount), 0) FROM wallet.payment_orders
     WHERE status = 'SUCCESSFUL' AND created_at >= CURRENT_DATE) as today_revenue,
    (SELECT COALESCE(SUM(final_amount), 0) FROM wallet.wallet_orders
     WHERE status = 'COMPLETED' AND created_at >= CURRENT_DATE) as today_spend
;
"""

# Count of REAL Users (created after Nov 13, 2025 OR recharged after Nov 13, 2025)
ALL_USERS_COUNT_QUERY = """
SELECT COUNT(DISTINCT uw.user_id)
FROM wallet.user_wallets uw
WHERE uw.deleted_at IS NULL
  AND (
    uw.created_at >= '2025-11-13 00:00:00'
    OR EXISTS (
      SELECT 1 FROM wallet.payment_orders po
      WHERE po.user_id = uw.user_id
        AND po.status = 'SUCCESSFUL'
        AND po.created_at >= '2025-11-13 00:00:00'
    )
  );
"""

# ALL Users with Complete Wallet Data (paginated) + Batch Detection
ALL_USERS_COMPLETE_QUERY = """
WITH user_recharges AS (
    SELECT
        user_id,
        COUNT(*) FILTER (WHERE status = 'SUCCESSFUL') as successful_recharge_count,
        COALESCE(SUM(amount) FILTER (WHERE status = 'SUCCESSFUL'), 0) as total_recharge_amount,
        MAX(created_at) FILTER (WHERE status = 'SUCCESSFUL') as last_recharge_date
    FROM wallet.payment_orders
    GROUP BY user_id
),
user_spending AS (
    SELECT
        user_id,
        COUNT(*) FILTER (WHERE status = 'COMPLETED') as completed_order_count,
        COALESCE(SUM(final_amount) FILTER (WHERE status = 'COMPLETED'), 0) as total_spent
    FROM wallet.wallet_orders
    GROUP BY user_id
),
daily_batch_counts AS (
    SELECT
        DATE(created_at) as creation_date,
        COUNT(*) as batch_size
    FROM wallet.user_wallets
    WHERE deleted_at IS NULL
    GROUP BY DATE(created_at)
)
SELECT
    uw.user_id,
    uw.name as user_name,
    CONCAT(c.country_code, c.phone_number) as phone_number,
    uw.real_cash as current_real_balance,
    uw.virtual_cash as current_virtual_balance,
    COALESCE(ur.successful_recharge_count, 0) as total_recharges,
    COALESCE(ur.total_recharge_amount, 0) as total_recharged,
    COALESCE(us.total_spent, 0) as total_spent,
    COALESCE(us.completed_order_count, 0) as completed_orders,
    GREATEST(ur.last_recharge_date, uw.updated_at) as last_activity,
    uw.created_at as account_created,
    COALESCE(dbc.batch_size, 1) as batch_size
FROM wallet.user_wallets uw
LEFT JOIN customers.customer c ON uw.user_id = c.customer_id AND c.deleted_at IS NULL
LEFT JOIN user_recharges ur ON uw.user_id = ur.user_id
LEFT JOIN user_spending us ON uw.user_id = us.user_id
LEFT JOIN daily_batch_counts dbc ON DATE(uw.created_at) = dbc.creation_date
WHERE uw.deleted_at IS NULL
  AND (
    uw.created_at >= '2025-11-13 00:00:00'
    OR EXISTS (
      SELECT 1 FROM wallet.payment_orders po
      WHERE po.user_id = uw.user_id
        AND po.status = 'SUCCESSFUL'
        AND po.created_at >= '2025-11-13 00:00:00'
    )
  )
ORDER BY GREATEST(ur.last_recharge_date, uw.updated_at) DESC NULLS LAST, total_spent DESC
LIMIT %s OFFSET %s;
"""


class MetricCard(Static):
    """A card displaying a single metric"""

    def __init__(self, title: str, value: str = "0", color: str = "#8fb0ee"):
        super().__init__()
        self.title = title
        self.value = value
        self.color = color

    def render(self) -> str:
        return f"[bold {self.color}]{self.title}[/]\n[bold #e9e9e9]{self.value}[/]"


class WalletDashboard(App):
    """A Textual app to monitor ALL user wallets."""

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

    /* --- Main Users Table --- */
    #users-container {
        height: 1fr;
        border: tall #32416a;
        margin: 1;
        padding: 1;
        background: #0f1525;
    }

    .section-header {
        text-align: center;
        text-style: bold;
        color: #8fb0ee;
        background: #131a2c;
        padding: 0 1;
        margin-bottom: 1;
    }

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

    #all-users-table {
        height: 1fr;
    }

    /* --- Pagination Info --- */
    #pagination-info {
        height: 1;
        text-align: center;
        background: #131a2c;
        color: #bbc8e8;
        text-style: bold;
        margin-top: 1;
    }

    /* --- Last Update Label --- */
    #last-update {
        height: 1;
        margin: 1;
        text-align: center;
        color: #788bc9;
        background: #0f1525;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh Now"),
        ("n", "next_page", "Next Page"),
        ("p", "prev_page", "Previous Page"),
        ("left", "prev_page", "Prev"),
        ("right", "next_page", "Next"),
        ("home", "first_page", "First Page"),
        ("end", "last_page", "Last Page"),
    ]

    # Configuration for the refresh timer - 10 seconds for faster updates
    REFRESH_SECONDS = 30
    TICK_RATE = 0.1

    def __init__(self):
        super().__init__()
        # Data storage
        self.kpi_data = (0, 0, 0, 0)
        self.all_users_data = []

        # Pagination state
        self.current_page = 1
        self.items_per_page = 25  # Show 25 users per page
        self.total_users = 0

        # Timer state
        self.timer_ticks = 0
        self.total_ticks = int(self.REFRESH_SECONDS / self.TICK_RATE)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)

        # 1. Refresh Progress Bar
        with Container(id="refresh-timer-container"):
            yield Static(f"⚡ Auto-refresh every {self.REFRESH_SECONDS}s | Next refresh in {self.REFRESH_SECONDS}s", id="refresh-label")
            yield ProgressBar(total=self.total_ticks, show_eta=False, id="refresh-bar")

        # 2. KPI Cards
        with Container(id="metrics"):
            with Horizontal():
                yield MetricCard("📥 Today's Recharge", "₹0", "#54efae")
                yield MetricCard("💎 Total Promo Cash", "₹0", "#91abec")
                yield MetricCard("💰 Today's Revenue", "₹0", "#f0e357")
                yield MetricCard("📤 Today's Spend", "₹0", "#5c81d7")

        # 3. Main ALL USERS Table (takes up most of the screen)
        with Container(id="users-container"):
            yield Static("👥 REAL USERS ONLY - Created or Recharged since Nov 13, 2025 (Real-time)", classes="section-header")
            yield DataTable(id="all-users-table")
            yield Static("Page 1 of 1 | Use ← → (Prev/Next) or Home/End | Press R to refresh | Press Q to quit", id="pagination-info")

        yield Static("Last updated: Never", id="last-update")
        yield Footer()

    def on_mount(self) -> None:
        """Set up tables and timer."""
        # Setup All Users Table with comprehensive columns
        table = self.query_one("#all-users-table", DataTable)
        table.add_columns(
            "ID",
            "Name",
            "Phone",
            "💰 Real ₹",
            "💎 Promo ₹",
            "📥 #",
            "📥 Total ₹",
            "📤 Spent ₹",
            "🛒 #",
            "📅 Created",
            "🕒 Last Activity"
        )
        table.cursor_type = "row"
        table.zebra_stripes = True

        # Initial data load
        self.fetch_data()

        # Start the tick timer for auto-refresh
        self.set_interval(self.TICK_RATE, self.tick_timer)

    def tick_timer(self) -> None:
        """Update progress bar and trigger fetch."""
        self.timer_ticks += 1

        bar = self.query_one("#refresh-bar", ProgressBar)
        bar.progress = self.timer_ticks

        if self.timer_ticks % 10 == 0:
            seconds_left = self.REFRESH_SECONDS - (self.timer_ticks * self.TICK_RATE)
            self.query_one("#refresh-label", Static).update(
                f"⚡ Auto-refresh every {self.REFRESH_SECONDS}s | Next refresh in {int(seconds_left)}s"
            )

        if self.timer_ticks >= self.total_ticks:
            self.timer_ticks = 0
            bar.progress = 0
            self.fetch_data()

    def fetch_data(self) -> None:
        self.run_worker(self._fetch_data_worker, thread=True, exclusive=True)

    def _fetch_data_worker(self) -> None:
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # 1. KPIs
            cursor.execute(KPI_QUERY)
            self.kpi_data = cursor.fetchone()

            # 2. Get total count of users for pagination
            cursor.execute(ALL_USERS_COUNT_QUERY)
            self.total_users = cursor.fetchone()[0]

            # 3. All Users with Complete Data (paginated)
            offset = (self.current_page - 1) * self.items_per_page
            cursor.execute(ALL_USERS_COMPLETE_QUERY, (self.items_per_page, offset))
            self.all_users_data = cursor.fetchall()

            cursor.close()
            conn.close()

        except Exception as e:
            self.call_from_thread(self.notify, f"DB Error: {str(e)}", severity="error")

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker state changes and update display on success."""
        if event.state == WorkerState.SUCCESS:
            self.update_display()
        elif event.state == WorkerState.ERROR:
            self.notify("Failed to fetch wallet data", severity="error")

    def update_display(self) -> None:
        # 1. Update KPIs
        metrics = self.query(MetricCard)
        today_recharge, virtual, rev_today, spend_today = self.kpi_data

        metrics[0].value = f"₹{float(today_recharge):,.2f}"
        metrics[1].value = f"₹{float(virtual):,.2f}"
        metrics[2].value = f"₹{float(rev_today):,.2f}"
        metrics[3].value = f"₹{float(spend_today):,.2f}"

        for m in metrics:
            m.refresh()

        # 2. Update All Users Table
        table = self.query_one("#all-users-table", DataTable)
        table.clear()

        for row in self.all_users_data:
            uid, name, phone, real, virtual, recharge_count, total_in, total_out, order_count, last_activity, account_created, batch_size = row

            # Format last activity
            if last_activity:
                if isinstance(last_activity, str):
                    last_activity_str = last_activity[:16]  # "YYYY-MM-DD HH:MM"
                else:
                    last_activity_str = last_activity.strftime("%Y-%m-%d %H:%M")
            else:
                last_activity_str = "Never"

            # Format account creation date
            if account_created:
                if isinstance(account_created, str):
                    created_str = account_created[:10]  # "YYYY-MM-DD"
                else:
                    created_str = account_created.strftime("%Y-%m-%d")
            else:
                created_str = "Unknown"

            # Add row with color coding for high-value users
            real_balance = float(real)
            if real_balance > 1000:
                real_str = f"[bold green]₹{real_balance:,.2f}[/]"
            elif real_balance > 0:
                real_str = f"[green]₹{real_balance:,.2f}[/]"
            else:
                real_str = f"₹{real_balance:,.2f}"

            table.add_row(
                str(uid),
                name or "-",
                phone or "-",
                real_str,
                f"₹{float(virtual):,.2f}",
                str(recharge_count),
                f"₹{float(total_in):,.2f}",
                f"₹{float(total_out):,.2f}",
                str(order_count),
                created_str,
                last_activity_str
            )

        # 3. Update pagination info
        total_pages = max(1, (self.total_users + self.items_per_page - 1) // self.items_per_page)
        start_item = (self.current_page - 1) * self.items_per_page + 1
        end_item = min(self.current_page * self.items_per_page, self.total_users)

        pagination_text = f"Page {self.current_page} of {total_pages} | "
        pagination_text += f"Showing {start_item}-{end_item} of {self.total_users} REAL users | "
        pagination_text += f"Filter: Nov 13+ or recharged | Use ← → or Home/End | R=refresh Q=quit"

        self.query_one("#pagination-info", Static).update(pagination_text)

        # 4. Update timestamp
        self.query_one("#last-update", Static).update(
            f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Auto-refresh: ON ({self.REFRESH_SECONDS}s)"
        )

    def action_refresh(self) -> None:
        """Manual refresh - resets timer and fetches immediately."""
        self.timer_ticks = 0
        self.query_one("#refresh-bar", ProgressBar).progress = 0
        self.notify("🔄 Refreshing wallet data...", severity="information")
        self.fetch_data()

    def action_next_page(self) -> None:
        """Navigate to the next page."""
        total_pages = max(1, (self.total_users + self.items_per_page - 1) // self.items_per_page)
        if self.current_page < total_pages:
            self.current_page += 1
            self.notify(f"→ Page {self.current_page}", severity="information")
            self.fetch_data()
        else:
            self.notify(f"Already on last page ({total_pages})", severity="warning")

    def action_prev_page(self) -> None:
        """Navigate to the previous page."""
        if self.current_page > 1:
            self.current_page -= 1
            self.notify(f"← Page {self.current_page}", severity="information")
            self.fetch_data()
        else:
            self.notify("Already on first page", severity="warning")

    def action_first_page(self) -> None:
        """Jump to the first page."""
        if self.current_page != 1:
            self.current_page = 1
            self.notify("⏮ First page", severity="information")
            self.fetch_data()
        else:
            self.notify("Already on first page", severity="warning")

    def action_last_page(self) -> None:
        """Jump to the last page."""
        total_pages = max(1, (self.total_users + self.items_per_page - 1) // self.items_per_page)
        if self.current_page != total_pages:
            self.current_page = total_pages
            self.notify(f"⏭ Last page ({total_pages})", severity="information")
            self.fetch_data()
        else:
            self.notify(f"Already on last page ({total_pages})", severity="warning")


if __name__ == "__main__":
    app = WalletDashboard()
    app.run()
