"""
Display Helper Functions for AstroKiran Dashboard
Formatting and color coding utilities.
"""

from pathlib import Path

# Color constants
GREEN = "#54efae"
YELLOW = "#f0e357"
RED = "#f05757"
GRAY = "#9ca3af"


def color_by_threshold(value, low_threshold, high_threshold, reverse=False):
    """Return color based on thresholds. If reverse=True, lower is better."""
    if reverse:
        if value < low_threshold:
            return GREEN
        elif value < high_threshold:
            return YELLOW
        else:
            return RED
    else:
        if value >= high_threshold:
            return GREEN
        elif value >= low_threshold:
            return YELLOW
        else:
            return RED


def format_db_stats_row(db_stats):
    """Format DB stats for display. Returns tuple of formatted strings."""
    total_conn, max_conn, active_queries, idle_conn, cache_hit = db_stats

    # Connection usage
    usage_pct = (total_conn / max_conn * 100) if max_conn > 0 else 0
    conn_color = color_by_threshold(usage_pct, 80, 90, reverse=True)

    # Cache hit ratio
    cache_val = cache_hit or 0
    cache_color = color_by_threshold(cache_val, 85, 95)

    # Active queries
    active_color = color_by_threshold(active_queries, 5, 10, reverse=True)

    return (
        f"  [{conn_color}]{total_conn}/{max_conn}[/] ({usage_pct:.0f}%)  ",
        f"  [{active_color}]{active_queries}[/]  ",
        f"  {idle_conn}  ",
        f"  [{cache_color}]{cache_val:.1f}%[/]  "
    )


def format_kpi_row(kpi_data):
    """Format KPI data for display."""
    today_recharge, virtual, rev_today, spend_today = kpi_data
    return (
        f"  Rs.{float(today_recharge):,.2f}  ",
        f"  Rs.{float(virtual):,.2f}  ",
        f"  Rs.{float(rev_today):,.2f}  ",
        f"  Rs.{float(spend_today):,.2f}  "
    )


def format_daily_recharge_rows(daily_recharge_data):
    """Format daily recharge data. Returns (counts_row, amounts_row)."""
    counts_row = ["# Recharges"]
    amounts_row = ["Rs. Amount"]

    for row in daily_recharge_data:
        day, day_label, count, amount = row
        count_color = color_by_threshold(count, 5, 10)
        counts_row.append(f"  [{count_color}]{count}[/]  ")
        amounts_row.append(f"  Rs.{float(amount):,.0f}  ")

    # Pad if fewer than 7 days
    while len(counts_row) < 8:
        counts_row.append("  -  ")
        amounts_row.append("  -  ")

    return counts_row, amounts_row


def format_rds_metrics_row1(rds_metrics):
    """Format RDS performance metrics (CPU, Memory, IOPS)."""
    cpu = rds_metrics.get('CPUUtilization', 0)
    mem_bytes = rds_metrics.get('FreeableMemory', 0)
    mem_gb = mem_bytes / (1024**3)
    read_iops = rds_metrics.get('ReadIOPS', 0)
    write_iops = rds_metrics.get('WriteIOPS', 0)

    return (
        f"  {cpu:.1f}%  ",
        f"  {mem_gb:.2f}  ",
        f"  {read_iops:.0f}  ",
        f"  {write_iops:.0f}  "
    )


def format_rds_metrics_row2(rds_metrics, replication_status):
    """Format RDS latency and replication metrics."""
    read_lat = rds_metrics.get('ReadLatency', 0) * 1000
    write_lat = rds_metrics.get('WriteLatency', 0) * 1000

    is_replica, wal_bytes_behind, seconds_since_last_tx = replication_status

    # Format WAL bytes behind
    if wal_bytes_behind == 0:
        wal_display = f"[{GREEN}]0 bytes (synced)[/]"
    elif wal_bytes_behind < 1024:
        wal_display = f"[{GREEN}]{wal_bytes_behind:.0f} bytes[/]"
    elif wal_bytes_behind < 1024 * 1024:
        kb = wal_bytes_behind / 1024
        wal_display = f"[{YELLOW}]{kb:.2f} KB[/]"
    else:
        mb = wal_bytes_behind / (1024 * 1024)
        wal_display = f"[{RED}]{mb:.2f} MB[/]"

    # Format time since last transaction
    if seconds_since_last_tx < 60:
        time_display = f"{seconds_since_last_tx:.0f}s ago"
    elif seconds_since_last_tx < 3600:
        mins = seconds_since_last_tx / 60
        time_display = f"{mins:.1f}m ago"
    else:
        hours = seconds_since_last_tx / 3600
        time_display = f"{hours:.1f}h ago"

    return (
        f"  {read_lat:.2f}  ",
        f"  {write_lat:.2f}  ",
        f"  {wal_display}  ",
        f"  {time_display}  "
    )


def format_user_row(row):
    """Format a single user row for display."""
    uid, name, phone, real, virtual, recharge_count, total_in, total_out, order_count, last_activity, account_created, batch_size = row

    # Format last activity
    if last_activity:
        if isinstance(last_activity, str):
            last_activity_str = last_activity[:16]
        else:
            last_activity_str = last_activity.strftime("%Y-%m-%d %H:%M")
    else:
        last_activity_str = "Never"

    # Format account creation date
    if account_created:
        if isinstance(account_created, str):
            created_str = account_created[:10]
        else:
            created_str = account_created.strftime("%Y-%m-%d")
    else:
        created_str = "Unknown"

    # Color code real balance
    real_balance = float(real)
    if real_balance > 1000:
        real_str = f"[bold green]Rs.{real_balance:,.2f}[/]"
    elif real_balance > 0:
        real_str = f"[green]Rs.{real_balance:,.2f}[/]"
    else:
        real_str = f"Rs.{real_balance:,.2f}"

    return (
        str(uid),
        name or "-",
        phone or "-",
        real_str,
        f"Rs.{float(virtual):,.2f}",
        str(recharge_count),
        f"Rs.{float(total_in):,.2f}",
        f"Rs.{float(total_out):,.2f}",
        str(order_count),
        created_str,
        last_activity_str
    )


def format_meta_kpi_row(summary, cac_data):
    """Format Meta Ads KPI row."""
    s = summary

    # Format date range
    if s.get('date_start') and s.get('date_end'):
        period_str = f"{s['date_start'].strftime('%b %d')} - {s['date_end'].strftime('%b %d')}"
    else:
        period_str = "Unknown"

    # Calculate CAC and Revenue
    if cac_data and cac_data['new_customers'] > 0:
        cac = s['total_spend'] / cac_data['new_customers']
        new_customers = cac_data['new_customers']
        revenue = cac_data['total_recharge']

        # Color code CAC
        if cac < 50:
            cac_str = f"[{GREEN}]Rs.{cac:,.2f}[/]"
        elif cac < 100:
            cac_str = f"[{YELLOW}]Rs.{cac:,.2f}[/]"
        else:
            cac_str = f"[{RED}]Rs.{cac:,.2f}[/]"

        # Color code revenue vs spend
        if revenue > s['total_spend']:
            revenue_str = f"[{GREEN}]Rs.{revenue:,.2f}[/]"
        else:
            revenue_str = f"[{RED}]Rs.{revenue:,.2f}[/]"
    else:
        cac_str = "-"
        revenue_str = "-"
        new_customers = 0

    return (
        f"  {period_str}  ",
        f"  Rs.{s['total_spend']:,.0f}  ",
        f"  {s['total_reach']:,}  ",
        f"  {s['avg_frequency']:.2f}  ",
        f"  {s['total_installs']:,}  ",
        f"  Rs.{s['avg_cpi']:,.2f}  ",
        f"  {new_customers:,}  ",
        f"  {revenue_str}  ",
        f"  {cac_str}  "
    )


def format_meta_ad_row(ad):
    """Format a single Meta ad row."""
    # Determine status based on CPI
    if ad['installs'] > 0:
        if ad['cpi'] < 15:
            status = f"[{GREEN}]Winner[/]"
        elif ad['cpi'] > 40:
            status = f"[{RED}]Expensive[/]"
        else:
            status = f"[{YELLOW}]Average[/]"
    elif ad['spend'] > 50:
        status = f"[{RED}]Wasted[/]"
    else:
        status = f"[{GRAY}]No Data[/]"

    # Color code CPI
    if ad['installs'] > 0:
        if ad['cpi'] < 15:
            cpi_str = f"[{GREEN}]Rs.{ad['cpi']:,.2f}[/]"
        elif ad['cpi'] > 40:
            cpi_str = f"[{RED}]Rs.{ad['cpi']:,.2f}[/]"
        else:
            cpi_str = f"[{YELLOW}]Rs.{ad['cpi']:,.2f}[/]"
    else:
        cpi_str = "-"

    # Truncate long names
    name = ad['name'][:30] + "..." if len(ad['name']) > 30 else ad['name']

    return (
        name,
        f"Rs.{ad['spend']:,.2f}",
        str(ad['installs']),
        cpi_str,
        f"{ad['impressions']:,}",
        f"{ad['clicks']:,}",
        f"{ad['ctr']:.2f}%",
        status
    )


def format_pagination_text(current_page, total_users, items_per_page):
    """Format pagination info text."""
    total_pages = max(1, (total_users + items_per_page - 1) // items_per_page)
    start_item = (current_page - 1) * items_per_page + 1
    end_item = min(current_page * items_per_page, total_users)

    return (
        f"Page {current_page} of {total_pages} | "
        f"Showing {start_item}-{end_item} of {total_users} REAL users | "
        f"Filter: Nov 13+ or recharged | Use <- -> or Home/End | R=refresh Q=quit"
    )


def format_meta_pagination_text(csv_path, ad_count):
    """Format Meta ads pagination info."""
    file_name = Path(csv_path).name if csv_path else "No file"
    return f"{file_name} | {ad_count} ad sets | Press L to load new CSV | Press W for Wallet view"
