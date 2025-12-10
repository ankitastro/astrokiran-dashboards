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
    TO_CHAR(ds.day, 'Mon DD') as day_label,
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

# Wallet Transactions (recent, paginated)
WALLET_TRANSACTIONS_QUERY = """
SELECT
    wt.transaction_id,
    wt.user_id,
    uw.name as user_name,
    wt.type,
    wt.amount,
    wt.real_cash_delta,
    wt.virtual_cash_delta,
    wt.comment,
    wt.created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata' as created_at_ist
FROM wallet.wallet_transactions wt
LEFT JOIN wallet.user_wallets uw ON wt.user_id = uw.user_id
ORDER BY wt.created_at DESC
LIMIT %s OFFSET %s;
"""

# Wallet Transactions Count
WALLET_TRANSACTIONS_COUNT_QUERY = """
SELECT COUNT(*) FROM wallet.wallet_transactions;
"""

# Revenue Summary (BD-1.0) - with date range parameters (IST timezone)
# BD-1.1: Add Cash, BD-1.2: Promotions, BD-1.3: Consultations
# BD-1.4: Astrologer Share, BD-1.5: Company Share
# Returns: (add_cash_amt, add_cash_count, promotions_amt, promotions_count,
#           consultations_amt, consultations_count, astrologer_share, company_share)
REVENUE_SUMMARY_QUERY = """
SELECT
    -- BD-1.1: Add Cash (successful payment orders)
    COALESCE((
        SELECT SUM(amount)
        FROM wallet.payment_orders
        WHERE status = 'SUCCESSFUL'
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date >= %s
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date <= %s
    ), 0) as add_cash_amount,
    COALESCE((
        SELECT COUNT(*)
        FROM wallet.payment_orders
        WHERE status = 'SUCCESSFUL'
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date >= %s
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date <= %s
    ), 0) as add_cash_count,

    -- BD-1.2: Promotions (virtual cash used in payments)
    COALESCE((
        SELECT SUM(virtual_cash_amount)
        FROM wallet.payment_orders
        WHERE status = 'SUCCESSFUL'
          AND virtual_cash_amount > 0
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date >= %s
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date <= %s
    ), 0) as promotions_amount,
    COALESCE((
        SELECT COUNT(*)
        FROM wallet.payment_orders
        WHERE status = 'SUCCESSFUL'
          AND virtual_cash_amount > 0
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date >= %s
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date <= %s
    ), 0) as promotions_count,

    -- BD-1.3: Consultations Amount
    COALESCE((
        SELECT SUM(final_amount)
        FROM wallet.wallet_orders
        WHERE status = 'COMPLETED'
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date >= %s
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date <= %s
    ), 0) as consultations_amount,
    COALESCE((
        SELECT COUNT(*)
        FROM wallet.wallet_orders
        WHERE status = 'COMPLETED'
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date >= %s
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date <= %s
    ), 0) as consultations_count,

    -- BD-1.4: Astrologer Share
    COALESCE((
        SELECT SUM(consultant_share)
        FROM wallet.wallet_orders
        WHERE status = 'COMPLETED'
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date >= %s
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date <= %s
    ), 0) as astrologer_share,

    -- BD-1.5: Company Share
    COALESCE((
        SELECT SUM(final_amount - COALESCE(consultant_share, 0))
        FROM wallet.wallet_orders
        WHERE status = 'COMPLETED'
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date >= %s
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date <= %s
    ), 0) as company_share;
"""

# User Metrics (BD-2.0) - with date range parameters (IST timezone)
# BD-2.1: ARPU (lifetime), BD-2.2: Registrations, BD-2.3: Conversions
USER_METRICS_QUERY = """
SELECT
    -- BD-2.1: ARPU (Lifetime - total revenue / total paying users)
    COALESCE((
        SELECT SUM(amount) / NULLIF(COUNT(DISTINCT user_id), 0)
        FROM wallet.payment_orders
        WHERE status = 'SUCCESSFUL'
    ), 0) as arpu,

    -- BD-2.2: Registrations in date range
    COALESCE((
        SELECT COUNT(*)
        FROM wallet.user_wallets
        WHERE deleted_at IS NULL
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date >= %s
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date <= %s
    ), 0) as registrations,

    -- BD-2.3: Conversions (first payment) in date range
    COALESCE((
        SELECT COUNT(*)
        FROM (
            SELECT user_id, MIN(created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') as first_payment_ist
            FROM wallet.payment_orders
            WHERE status = 'SUCCESSFUL'
            GROUP BY user_id
        ) fp
        WHERE fp.first_payment_ist::date >= %s
          AND fp.first_payment_ist::date <= %s
    ), 0) as conversions;
"""

# Consultation Summary (BD-3.0) - Totals by mode (IST timezone)
# BD-3.1: All, BD-3.4: Chat, BD-3.5: Call
CONSULTATION_SUMMARY_QUERY = """
SELECT
    -- All consultations
    COALESCE((
        SELECT COUNT(*)
        FROM consultation.consultation c
        WHERE c.state = 'completed'
          AND (c.completed_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date >= %s
          AND (c.completed_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date <= %s
    ), 0) as all_count,
    COALESCE((
        SELECT SUM(wo.final_amount)
        FROM consultation.consultation c
        JOIN wallet.wallet_orders wo ON c.order_id = wo.order_id
        WHERE c.state = 'completed'
          AND (c.completed_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date >= %s
          AND (c.completed_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date <= %s
    ), 0) as all_amount,

    -- Chat consultations
    COALESCE((
        SELECT COUNT(*)
        FROM consultation.consultation c
        WHERE c.state = 'completed' AND c.mode = 'chat'
          AND (c.completed_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date >= %s
          AND (c.completed_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date <= %s
    ), 0) as chat_count,
    COALESCE((
        SELECT SUM(wo.final_amount)
        FROM consultation.consultation c
        JOIN wallet.wallet_orders wo ON c.order_id = wo.order_id
        WHERE c.state = 'completed' AND c.mode = 'chat'
          AND (c.completed_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date >= %s
          AND (c.completed_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date <= %s
    ), 0) as chat_amount,

    -- Call (voice) consultations
    COALESCE((
        SELECT COUNT(*)
        FROM consultation.consultation c
        WHERE c.state = 'completed' AND c.mode = 'voice'
          AND (c.completed_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date >= %s
          AND (c.completed_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date <= %s
    ), 0) as call_count,
    COALESCE((
        SELECT SUM(wo.final_amount)
        FROM consultation.consultation c
        JOIN wallet.wallet_orders wo ON c.order_id = wo.order_id
        WHERE c.state = 'completed' AND c.mode = 'voice'
          AND (c.completed_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date >= %s
          AND (c.completed_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date <= %s
    ), 0) as call_amount;
"""

# Consultation by Astrologer (BD-3.0) - Per astrologer breakdown (IST timezone)
CONSULTATION_BY_ASTROLOGER_QUERY = """
SELECT
    gp.full_name as astrologer,
    c.mode,
    COUNT(*) as count,
    COALESCE(SUM(wo.final_amount), 0) as amount
FROM consultation.consultation c
JOIN guide.guide_profile gp ON c.guide_id = gp.id
LEFT JOIN wallet.wallet_orders wo ON c.order_id = wo.order_id
WHERE c.state = 'completed'
  AND (c.completed_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date >= %s
  AND (c.completed_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date <= %s
GROUP BY gp.full_name, c.mode
ORDER BY amount DESC;
"""

# Payment Metrics (BD-4.0) - with date range parameters (IST timezone)
# BD-4.1: Number of Payments, BD-4.2: Amount, BD-4.3: Success Rate, BD-4.4: By Payment Mode
PAYMENT_SUMMARY_QUERY = """
SELECT
    -- BD-4.1: Total Payments (attempted)
    COALESCE((
        SELECT COUNT(*)
        FROM wallet.payment_orders
        WHERE (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date >= %s
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date <= %s
    ), 0) as total_count,

    -- BD-4.2: Total Amount (successful only)
    COALESCE((
        SELECT SUM(amount)
        FROM wallet.payment_orders
        WHERE status = 'SUCCESSFUL'
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date >= %s
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date <= %s
    ), 0) as successful_amount,

    -- Successful count
    COALESCE((
        SELECT COUNT(*)
        FROM wallet.payment_orders
        WHERE status = 'SUCCESSFUL'
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date >= %s
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date <= %s
    ), 0) as successful_count,

    -- Failed count
    COALESCE((
        SELECT COUNT(*)
        FROM wallet.payment_orders
        WHERE status = 'FAILED'
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date >= %s
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date <= %s
    ), 0) as failed_count,

    -- Pending count
    COALESCE((
        SELECT COUNT(*)
        FROM wallet.payment_orders
        WHERE status = 'PENDING'
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date >= %s
          AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date <= %s
    ), 0) as pending_count;
"""

# Payment by Method (BD-4.4) - Success rate per payment mode
PAYMENT_BY_METHOD_QUERY = """
SELECT
    CASE
        WHEN payment_method::text IN ('UPI', 'UPI_QR') THEN 'UPI'
        WHEN payment_method::text = 'CREDIT_CARD' THEN 'Credit Card'
        WHEN payment_method::text = 'DEBIT_CARD' THEN 'Debit Card'
        WHEN payment_method::text = 'NEFT' THEN 'Net Banking'
        ELSE COALESCE(payment_method::text, 'Unknown')
    END as method,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE status = 'SUCCESSFUL') as successful,
    COUNT(*) FILTER (WHERE status = 'FAILED') as failed,
    COALESCE(SUM(amount) FILTER (WHERE status = 'SUCCESSFUL'), 0) as amount
FROM wallet.payment_orders
WHERE (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date >= %s
  AND (created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date <= %s
GROUP BY
    CASE
        WHEN payment_method::text IN ('UPI', 'UPI_QR') THEN 'UPI'
        WHEN payment_method::text = 'CREDIT_CARD' THEN 'Credit Card'
        WHEN payment_method::text = 'DEBIT_CARD' THEN 'Debit Card'
        WHEN payment_method::text = 'NEFT' THEN 'Net Banking'
        ELSE COALESCE(payment_method::text, 'Unknown')
    END
ORDER BY amount DESC;
"""

# Astrologer Performance (BD-8.0) - Chat and Call breakdown per astrologer (IST timezone)
# BD-8.1: Chat count, BD-8.2: Chat amount, BD-8.3: Call count, BD-8.4: Call amount
ASTROLOGER_PERFORMANCE_QUERY = """
SELECT
    gp.full_name as astrologer,
    COUNT(*) FILTER (WHERE c.mode = 'chat') as chat_count,
    COALESCE(SUM(wo.final_amount) FILTER (WHERE c.mode = 'chat'), 0) as chat_amount,
    COUNT(*) FILTER (WHERE c.mode = 'voice') as call_count,
    COALESCE(SUM(wo.final_amount) FILTER (WHERE c.mode = 'voice'), 0) as call_amount
FROM consultation.consultation c
JOIN guide.guide_profile gp ON c.guide_id = gp.id
LEFT JOIN wallet.wallet_orders wo ON c.order_id = wo.order_id
WHERE c.state = 'completed'
  AND (c.completed_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date >= %s
  AND (c.completed_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date <= %s
GROUP BY gp.full_name
ORDER BY (COALESCE(SUM(wo.final_amount), 0)) DESC;
"""

# Astrologer Availability (BD-9.0) - Online time from audit logs (IST timezone)
# BD-9.1: Online time per astrologer, BD-9.2: Live astrologers count
ASTROLOGER_AVAILABILITY_QUERY = """
WITH state_changes AS (
    SELECT
        (original_data->>'id')::int as guide_id,
        original_data->>'full_name' as guide_name,
        original_data->>'availability_state' as from_state,
        new_data->>'availability_state' as to_state,
        action_tstamp AT TIME ZONE 'Asia/Kolkata' as changed_at_ist
    FROM audit.logged_actions
    WHERE table_name = 'guide_profile'
      AND action = 'U'
      AND original_data->>'availability_state' IS DISTINCT FROM new_data->>'availability_state'
      AND (action_tstamp AT TIME ZONE 'Asia/Kolkata')::date >= %s
      AND (action_tstamp AT TIME ZONE 'Asia/Kolkata')::date <= %s
),
-- Track when each guide goes online and offline
online_periods AS (
    SELECT
        guide_id,
        guide_name,
        changed_at_ist as event_time,
        CASE WHEN to_state = 'ONLINE_AVAILABLE' THEN 1 ELSE -1 END as direction,
        to_state,
        from_state
    FROM state_changes
    WHERE to_state = 'ONLINE_AVAILABLE'
       OR from_state = 'ONLINE_AVAILABLE'
),
-- Pair start/end events
paired_sessions AS (
    SELECT
        guide_id,
        guide_name,
        event_time as session_start,
        LEAD(event_time) OVER (PARTITION BY guide_id ORDER BY event_time) as session_end,
        direction
    FROM online_periods
)
SELECT
    guide_name,
    MIN(session_start)::date as first_online,
    MAX(COALESCE(session_end, session_start))::date as last_online,
    COALESCE(SUM(
        EXTRACT(EPOCH FROM (
            COALESCE(session_end, NOW() AT TIME ZONE 'Asia/Kolkata') - session_start
        )) / 60
    ), 0)::int as total_minutes_online
FROM paired_sessions
WHERE direction = 1  -- Only count sessions that START with going online
  AND session_end IS NOT NULL  -- Only count completed sessions
GROUP BY guide_id, guide_name
ORDER BY total_minutes_online DESC;
"""

# Live Astrologers count (current snapshot)
LIVE_ASTROLOGERS_QUERY = """
SELECT COUNT(*) as live_count
FROM guide.guide_profile
WHERE availability_state = 'ONLINE_AVAILABLE'
  AND deleted_at IS NULL;
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
