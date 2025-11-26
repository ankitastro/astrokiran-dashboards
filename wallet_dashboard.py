#!/usr/bin/env python3
"""
AstroKiran Wallet Dashboard - ALL USERS VIEW
Real-time monitoring of ALL user wallet balances, recharges, and spending.
Auto-refreshes every 10 seconds to show latest data.
"""

import os
import psycopg2
import re
import boto3
from datetime import datetime, timedelta
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

# AWS Configuration for RDS CloudWatch metrics
AWS_CONFIG = {
    'region': os.getenv('AWS_REGION', 'ap-south-1'),
    'rds_instance_id': os.getenv('RDS_INSTANCE_ID', ''),
}

# AWS credentials (optional - will use IAM role if not provided)
if os.getenv('AWS_ACCESS_KEY_ID'):
    AWS_CONFIG['aws_access_key_id'] = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_CONFIG['aws_secret_access_key'] = os.getenv('AWS_SECRET_ACCESS_KEY')

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

# Database Connection and Load Stats
DB_CONNECTIONS_QUERY = """
SELECT
    (SELECT COUNT(*) FROM pg_stat_activity WHERE datname = 'astrokiran') as total_connections,
    (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') as max_connections,
    (SELECT COUNT(*) FROM pg_stat_activity WHERE datname = 'astrokiran' AND state = 'active' AND query NOT LIKE '%pg_stat_activity%') as active_queries,
    (SELECT COUNT(*) FROM pg_stat_activity WHERE datname = 'astrokiran' AND state = 'idle') as idle_connections,
    (SELECT ROUND(100.0 * sum(blks_hit) / NULLIF(sum(blks_hit) + sum(blks_read), 0), 2)
     FROM pg_stat_database WHERE datname = 'astrokiran') as cache_hit_ratio;
"""

# Replication Status (for read replicas)
REPLICATION_STATUS_QUERY = """
SELECT
    pg_is_in_recovery() as is_replica,
    CASE
        WHEN pg_is_in_recovery() THEN
            pg_wal_lsn_diff(pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn())
        ELSE 0
    END as wal_bytes_behind,
    CASE
        WHEN pg_is_in_recovery() THEN
            EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))
        ELSE 0
    END as seconds_since_last_transaction;
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


# --- AWS CloudWatch Helper Functions ---

def get_rds_cloudwatch_metrics():
    """
    Fetch RDS CloudWatch metrics for the last 10 minutes.
    Returns: dict with CPU, memory, IOPS, latency, replica lag, and replication metrics
    """
    if not AWS_CONFIG.get('rds_instance_id'):
        return None

    try:
        # Create CloudWatch client
        session_kwargs = {'region_name': AWS_CONFIG['region']}
        if AWS_CONFIG.get('aws_access_key_id'):
            session_kwargs['aws_access_key_id'] = AWS_CONFIG['aws_access_key_id']
            session_kwargs['aws_secret_access_key'] = AWS_CONFIG['aws_secret_access_key']

        cloudwatch = boto3.client('cloudwatch', **session_kwargs)

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=10)  # CloudWatch data may have 5-minute delay

        # Metrics to fetch
        metrics_to_fetch = [
            ('CPUUtilization', 'Percent'),
            ('FreeableMemory', 'Bytes'),
            ('ReadIOPS', 'Count/Second'),
            ('WriteIOPS', 'Count/Second'),
            ('ReadLatency', 'Seconds'),
            ('WriteLatency', 'Seconds'),
            ('ReplicaLag', 'Seconds'),  # Replication lag for read replicas
        ]

        results = {}

        for metric_name, unit in metrics_to_fetch:
            response = cloudwatch.get_metric_statistics(
                Namespace='AWS/RDS',
                MetricName=metric_name,
                Dimensions=[
                    {'Name': 'DBInstanceIdentifier', 'Value': AWS_CONFIG['rds_instance_id']}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,  # 5 minutes
                Statistics=['Average']
            )

            if response['Datapoints']:
                # Get the most recent datapoint
                datapoint = sorted(response['Datapoints'], key=lambda x: x['Timestamp'], reverse=True)[0]
                results[metric_name] = datapoint['Average']
            else:
                results[metric_name] = 0

        return results

    except Exception as e:
        return None


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

    #top-info-bar {
        height: auto;
        width: 100%;
    }

    #refresh-label {
        width: 100%;
        text-align: center;
        color: #bbc8e8;
        text-style: italic;
        padding: 0 1;
    }

    /* --- DB Stats Table --- */
    #db-stats-container {
        height: auto;
        margin: 1 1 0 1;
    }

    #db-stats-table {
        height: auto;
        border: solid #1c2440;
        background: #0f1525;
        text-align: center;
    }

    /* --- KPI Table --- */
    #kpi-container {
        height: auto;
        margin: 1 1 0 1;
    }

    #kpi-table {
        height: auto;
        border: solid #1c2440;
        background: #0f1525;
        text-align: center;
    }

    /* --- RDS Tables --- */
    #rds-container-1 {
        height: auto;
        margin: 1 1 0 1;
    }

    #rds-table-1 {
        height: auto;
        border: solid #1c2440;
        background: #0f1525;
        text-align: center;
    }

    #rds-container-2 {
        height: auto;
        margin: 1 1 0 1;
    }

    #rds-table-2 {
        height: auto;
        border: solid #1c2440;
        background: #0f1525;
        text-align: center;
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
        self.db_stats = (0, 0, 0, 0, 0.0)  # (total_conn, max_conn, active_queries, idle_conn, cache_hit_ratio)
        self.rds_metrics = None  # RDS CloudWatch metrics
        self.replication_status = (False, 0, 0)  # (is_replica, wal_bytes_behind, seconds_since_last_tx)

        # Pagination state
        self.current_page = 1
        self.items_per_page = 100  # Show 100 users per page
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

        # 2. DB Stats Table
        with Container(id="db-stats-container"):
            yield Static("🔌 DATABASE CONNECTION STATS", classes="section-header")
            yield DataTable(id="db-stats-table")

        # 3. KPI Metrics Table
        with Container(id="kpi-container"):
            yield Static("💰 TODAY'S WALLET METRICS", classes="section-header")
            yield DataTable(id="kpi-table")

        # 4. RDS CloudWatch Metrics Tables (if configured)
        with Container(id="rds-container-1"):
            yield Static("📊 AWS RDS CLOUDWATCH METRICS - Performance", classes="section-header")
            yield DataTable(id="rds-table-1")

        with Container(id="rds-container-2"):
            yield Static("📊 AWS RDS METRICS - Latency & Replication Status", classes="section-header")
            yield DataTable(id="rds-table-2")

        # 4. Main ALL USERS Table (takes up most of the screen)
        with Container(id="users-container"):
            yield Static("👥 REAL USERS ONLY - Created or Recharged since Nov 13, 2025 (Real-time)", classes="section-header")
            yield DataTable(id="all-users-table")
            yield Static("Page 1 of 1 | Use ← → (Prev/Next) or Home/End | Press R to refresh | Press Q to quit", id="pagination-info")

        yield Static("Last updated: Never", id="last-update")
        yield Footer()

    def on_mount(self) -> None:
        """Set up tables and timer."""
        # Setup DB Stats Table
        db_stats_table = self.query_one("#db-stats-table", DataTable)
        db_stats_table.add_columns(
            "🔌 Connections (Active/Max)",
            "⚡ Active Queries",
            "💤 Idle Connections",
            "📊 Cache Hit Ratio %"
        )
        db_stats_table.zebra_stripes = True

        # Setup KPI Table
        kpi_table = self.query_one("#kpi-table", DataTable)
        kpi_table.add_columns(
            "📥 Today's Recharge ₹",
            "💎 Total Promo Cash ₹",
            "💰 Today's Revenue ₹",
            "📤 Today's Spend ₹"
        )
        kpi_table.zebra_stripes = True

        # Setup RDS CloudWatch Metrics Tables
        rds_table_1 = self.query_one("#rds-table-1", DataTable)
        rds_table_1.add_columns(
            "🖥️ CPU %",
            "💾 Memory Free (GB)",
            "📀 Read IOPS",
            "📀 Write IOPS"
        )
        rds_table_1.zebra_stripes = True

        rds_table_2 = self.query_one("#rds-table-2", DataTable)
        rds_table_2.add_columns(
            "⏱️ Read Latency (ms)",
            "⏱️ Write Latency (ms)",
            "🔄 WAL Bytes Behind",
            "⏳ Time Since Last TX"
        )
        rds_table_2.zebra_stripes = True

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

            # 1. DB Connection and Load Stats
            cursor.execute(DB_CONNECTIONS_QUERY)
            self.db_stats = cursor.fetchone()

            # 2. KPIs
            cursor.execute(KPI_QUERY)
            self.kpi_data = cursor.fetchone()

            # 3. Get total count of users for pagination
            cursor.execute(ALL_USERS_COUNT_QUERY)
            self.total_users = cursor.fetchone()[0]

            # 4. All Users with Complete Data (paginated)
            offset = (self.current_page - 1) * self.items_per_page
            cursor.execute(ALL_USERS_COMPLETE_QUERY, (self.items_per_page, offset))
            self.all_users_data = cursor.fetchall()

            # 5. Replication Status
            cursor.execute(REPLICATION_STATUS_QUERY)
            self.replication_status = cursor.fetchone()

            cursor.close()
            conn.close()

            # 6. Fetch RDS CloudWatch Metrics (if configured)
            self.rds_metrics = get_rds_cloudwatch_metrics()

        except Exception as e:
            self.call_from_thread(self.notify, f"DB Error: {str(e)}", severity="error")

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker state changes and update display on success."""
        if event.state == WorkerState.SUCCESS:
            self.update_display()
        elif event.state == WorkerState.ERROR:
            self.notify("Failed to fetch wallet data", severity="error")

    def update_display(self) -> None:
        # 1. Update DB Stats Table
        total_conn, max_conn, active_queries, idle_conn, cache_hit = self.db_stats
        db_stats_table = self.query_one("#db-stats-table", DataTable)
        db_stats_table.clear()

        # Color code connections: green if under 80%, yellow if 80-90%, red if over 90%
        usage_pct = (total_conn / max_conn * 100) if max_conn > 0 else 0
        if usage_pct < 80:
            conn_color = "#54efae"  # green
        elif usage_pct < 90:
            conn_color = "#f0e357"  # yellow
        else:
            conn_color = "#f05757"  # red

        # Color code cache hit ratio: green if >95%, yellow if 85-95%, red if <85%
        cache_val = cache_hit or 0
        if cache_val >= 95:
            cache_color = "#54efae"  # green
        elif cache_val >= 85:
            cache_color = "#f0e357"  # yellow
        else:
            cache_color = "#f05757"  # red

        # Color code active queries: green if <=5, yellow if 6-10, red if >10
        if active_queries <= 5:
            active_color = "#54efae"
        elif active_queries <= 10:
            active_color = "#f0e357"
        else:
            active_color = "#f05757"

        db_stats_table.add_row(
            f"  [{conn_color}]{total_conn}/{max_conn}[/] ({usage_pct:.0f}%)  ",
            f"  [{active_color}]{active_queries}[/]  ",
            f"  {idle_conn}  ",
            f"  [{cache_color}]{cache_val:.1f}%[/]  "
        )

        # 2. Update KPI Table
        kpi_table = self.query_one("#kpi-table", DataTable)
        kpi_table.clear()

        today_recharge, virtual, rev_today, spend_today = self.kpi_data
        kpi_table.add_row(
            f"  ₹{float(today_recharge):,.2f}  ",
            f"  ₹{float(virtual):,.2f}  ",
            f"  ₹{float(rev_today):,.2f}  ",
            f"  ₹{float(spend_today):,.2f}  "
        )

        # 3. Update RDS Metrics Tables (if available)
        if self.rds_metrics:
            # Table 1: Performance metrics (CPU, Memory, IOPS)
            rds_table_1 = self.query_one("#rds-table-1", DataTable)
            rds_table_1.clear()

            # CPU Utilization
            cpu = self.rds_metrics.get('CPUUtilization', 0)

            # Free Memory (convert bytes to GB)
            mem_bytes = self.rds_metrics.get('FreeableMemory', 0)
            mem_gb = mem_bytes / (1024**3)

            # Read IOPS
            read_iops = self.rds_metrics.get('ReadIOPS', 0)

            # Write IOPS
            write_iops = self.rds_metrics.get('WriteIOPS', 0)

            rds_table_1.add_row(
                f"  {cpu:.1f}%  ",
                f"  {mem_gb:.2f}  ",
                f"  {read_iops:.0f}  ",
                f"  {write_iops:.0f}  "
            )

            # Table 2: Latency and Replication metrics
            rds_table_2 = self.query_one("#rds-table-2", DataTable)
            rds_table_2.clear()

            # Read Latency (convert seconds to ms)
            read_lat = self.rds_metrics.get('ReadLatency', 0) * 1000

            # Write Latency (convert seconds to ms)
            write_lat = self.rds_metrics.get('WriteLatency', 0) * 1000

            # Replication Status from PostgreSQL (actual WAL lag, not timestamp)
            is_replica, wal_bytes_behind, seconds_since_last_tx = self.replication_status

            # Format WAL bytes behind
            if wal_bytes_behind == 0:
                wal_display = "[#54efae]0 bytes (synced)[/]"
                lag_color = "#54efae"  # green
            elif wal_bytes_behind < 1024:
                wal_display = f"[#54efae]{wal_bytes_behind:.0f} bytes[/]"
                lag_color = "#54efae"  # green
            elif wal_bytes_behind < 1024 * 1024:
                kb = wal_bytes_behind / 1024
                wal_display = f"[#f0e357]{kb:.2f} KB[/]"
                lag_color = "#f0e357"  # yellow
            else:
                mb = wal_bytes_behind / (1024 * 1024)
                wal_display = f"[#f05757]{mb:.2f} MB[/]"
                lag_color = "#f05757"  # red

            # Format time since last transaction
            if seconds_since_last_tx < 60:
                time_display = f"{seconds_since_last_tx:.0f}s ago"
            elif seconds_since_last_tx < 3600:
                mins = seconds_since_last_tx / 60
                time_display = f"{mins:.1f}m ago"
            else:
                hours = seconds_since_last_tx / 3600
                time_display = f"{hours:.1f}h ago"

            rds_table_2.add_row(
                f"  {read_lat:.2f}  ",
                f"  {write_lat:.2f}  ",
                f"  {wal_display}  ",
                f"  {time_display}  "
            )

        # 4. Update All Users Table
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

        # 5. Update pagination info
        total_pages = max(1, (self.total_users + self.items_per_page - 1) // self.items_per_page)
        start_item = (self.current_page - 1) * self.items_per_page + 1
        end_item = min(self.current_page * self.items_per_page, self.total_users)

        pagination_text = f"Page {self.current_page} of {total_pages} | "
        pagination_text += f"Showing {start_item}-{end_item} of {self.total_users} REAL users | "
        pagination_text += f"Filter: Nov 13+ or recharged | Use ← → or Home/End | R=refresh Q=quit"

        self.query_one("#pagination-info", Static).update(pagination_text)

        # 6. Update timestamp
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
