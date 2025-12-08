"""
SQL Queries for AstroKiran Dashboard
"""

# Daily Recharge Counts (last 7 days) - shows count and amount per day
DAILY_RECHARGE_QUERY = """
WITH date_series AS (
    SELECT generate_series(
        (CURRENT_DATE AT TIME ZONE 'Asia/Kolkata' - interval '6 days')::date,
        (CURRENT_DATE AT TIME ZONE 'Asia/Kolkata')::date,
        '1 day'::interval
    )::date as day
),
daily_stats AS (
    SELECT
        (po.created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date as recharge_date,
        COUNT(*) as recharge_count,
        COALESCE(SUM(amount), 0) as total_amount
    FROM wallet.payment_orders po
    WHERE po.status = 'SUCCESSFUL'
      AND po.created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata' >= CURRENT_DATE AT TIME ZONE 'Asia/Kolkata' - interval '6 days'
    GROUP BY (po.created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date
)
SELECT
    ds.day,
    CASE
        WHEN ds.day = CURRENT_DATE AT TIME ZONE 'Asia/Kolkata' THEN 'Today'
        WHEN ds.day = (CURRENT_DATE AT TIME ZONE 'Asia/Kolkata' - interval '1 day')::date THEN 'Yesterday'
        WHEN ds.day = (CURRENT_DATE AT TIME ZONE 'Asia/Kolkata' - interval '2 days')::date THEN '2 days ago'
        ELSE TO_CHAR(ds.day, 'Mon DD')
    END as day_label,
    COALESCE(d.recharge_count, 0) as recharge_count,
    COALESCE(d.total_amount, 0) as total_amount
FROM date_series ds
LEFT JOIN daily_stats d ON ds.day = d.recharge_date
ORDER BY ds.day DESC;
"""

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

# Query to get paying customers (first recharge) in a date range (IST corrected)
CAC_QUERY = """
WITH first_recharges AS (
    SELECT
        user_id,
        MIN(created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') as first_recharge_date_ist
    FROM wallet.payment_orders
    WHERE status = 'SUCCESSFUL'
    GROUP BY user_id
)
SELECT
    COUNT(*) as new_paying_customers,
    COALESCE(SUM(po.amount), 0) as total_recharge_amount
FROM first_recharges fr
JOIN wallet.payment_orders po ON fr.user_id = po.user_id
    AND (po.created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date = fr.first_recharge_date_ist::date
    AND po.status = 'SUCCESSFUL'
WHERE fr.first_recharge_date_ist::date >= %s
  AND fr.first_recharge_date_ist::date <= %s;
"""
