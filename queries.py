"""
SQL Queries for AstroKiran Dashboard
"""

# Daily Recharge Counts (last 7 days) - shows count and amount per day
# Uses wallet_transactions (ADD) as source of truth
DAILY_RECHARGE_QUERY = """
WITH date_series AS (
    SELECT generate_series(
        (CURRENT_DATE - interval '6 days')::date,
        CURRENT_DATE::date,
        '1 day'::interval
    )::date as day
),
daily_stats AS (
    SELECT
        (wt.created_at + INTERVAL '5 hours 30 minutes')::date as recharge_date,
        COUNT(*) as recharge_count,
        COALESCE(SUM(wt.real_cash_delta), 0) as total_amount
    FROM wallet.wallet_transactions wt
    WHERE wt.type = 'ADD'
      AND (wt.created_at + INTERVAL '5 hours 30 minutes') >= CURRENT_DATE - interval '6 days'
    GROUP BY (wt.created_at + INTERVAL '5 hours 30 minutes')::date
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

# KPI Metrics: Comprehensive wallet stats (since Dec 5, 2025)
# Note: All timestamps are stored in UTC. Use + INTERVAL '5 hours 30 minutes' for IST conversion.
KPI_QUERY = """
WITH first_payments AS (
    SELECT user_id, MIN(created_at + INTERVAL '5 hours 30 minutes') as first_payment
    FROM wallet.payment_orders
    WHERE status = 'SUCCESSFUL'
    GROUP BY user_id
),
paid_since_dec5 AS (
    SELECT DISTINCT user_id
    FROM wallet.payment_orders
    WHERE status = 'SUCCESSFUL'
      AND (created_at + INTERVAL '5 hours 30 minutes')::date >= '2025-12-05'
),
first_consult AS (
    SELECT customer_id, MIN(completed_at + INTERVAL '5 hours 30 minutes') as first_consult
    FROM consultation.consultation c
    JOIN guide.guide_profile gp ON c.guide_id = gp.id AND gp.deleted_at IS NULL
    WHERE c.state = 'completed' AND c.deleted_at IS NULL
    GROUP BY customer_id
),
consults_since_dec5 AS (
    SELECT c.id, c.customer_id, c.order_id
    FROM consultation.consultation c
    JOIN guide.guide_profile gp ON c.guide_id = gp.id AND gp.deleted_at IS NULL
    WHERE c.state = 'completed'
      AND c.deleted_at IS NULL
      AND (c.completed_at + INTERVAL '5 hours 30 minutes')::date >= '2025-12-05'
),
txn_stats AS (
    SELECT
        COALESCE(SUM(real_cash_delta) FILTER (WHERE type = 'ADD'), 0) as real_added,
        COALESCE(SUM(virtual_cash_delta) FILTER (WHERE type = 'ADD'), 0) as virtual_added,
        COALESCE(-SUM(real_cash_delta) FILTER (WHERE type = 'SPENT'), 0) as real_spent,
        COALESCE(-SUM(virtual_cash_delta) FILTER (WHERE type = 'SPENT'), 0) as virtual_spent
    FROM wallet.wallet_transactions
    WHERE (created_at + INTERVAL '5 hours 30 minutes')::date >= '2025-12-05'
),
user_payments AS (
    SELECT user_id, COUNT(*) as payment_count
    FROM wallet.payment_orders
    WHERE status = 'SUCCESSFUL'
      AND (created_at + INTERVAL '5 hours 30 minutes')::date >= '2025-12-05'
    GROUP BY user_id
)
SELECT
    -- Users & Customers
    (SELECT COUNT(*) FROM wallet.user_wallets WHERE deleted_at IS NULL) as total_users,
    (SELECT COUNT(*) FROM paid_since_dec5) as total_customers,
    -- New/Old paying users
    (SELECT COUNT(*) FROM paid_since_dec5 p JOIN first_payments fp ON p.user_id = fp.user_id WHERE fp.first_payment::date >= '2025-12-05') as new_paying_users,
    (SELECT COUNT(*) FROM paid_since_dec5 p JOIN first_payments fp ON p.user_id = fp.user_id WHERE fp.first_payment::date < '2025-12-05') as old_paying_users,
    -- Payment amounts
    ts.real_added as total_payment_amount,
    -- Repeat
    (SELECT COUNT(*) FROM user_payments WHERE payment_count > 1) as repeat_users,
    (SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE payment_count > 1) / NULLIF(COUNT(*), 0), 1) FROM user_payments) as repeat_rate,
    -- Consultations count
    (SELECT COUNT(*) FROM consults_since_dec5) as total_consultations,
    (SELECT COUNT(*) FROM consults_since_dec5 cs JOIN first_consult fc ON cs.customer_id = fc.customer_id WHERE fc.first_consult::date >= '2025-12-05') as new_user_consultations,
    (SELECT COUNT(*) FROM consults_since_dec5 cs JOIN first_consult fc ON cs.customer_id = fc.customer_id WHERE fc.first_consult::date < '2025-12-05') as old_user_consultations,
    -- Consultation amounts
    (SELECT COALESCE(SUM(wo.final_amount), 0) FROM consults_since_dec5 cs JOIN wallet.wallet_orders wo ON cs.order_id = wo.order_id) as total_consult_amount,
    (SELECT COALESCE(SUM(wo.final_amount), 0) FROM consults_since_dec5 cs JOIN wallet.wallet_orders wo ON cs.order_id = wo.order_id JOIN first_consult fc ON cs.customer_id = fc.customer_id WHERE fc.first_consult::date >= '2025-12-05') as new_user_consult_amount,
    (SELECT COALESCE(SUM(wo.final_amount), 0) FROM consults_since_dec5 cs JOIN wallet.wallet_orders wo ON cs.order_id = wo.order_id JOIN first_consult fc ON cs.customer_id = fc.customer_id WHERE fc.first_consult::date < '2025-12-05') as old_user_consult_amount
FROM txn_stats ts;
"""

# Wallet Creation Stats - Daily breakdown (last 7 days)
# Includes: phone entries (auth_users), wallet created, wallet deleted, repeat recharges
WALLET_CREATION_QUERY = """
WITH date_series AS (
    SELECT generate_series(
        (CURRENT_DATE - interval '6 days')::date,
        CURRENT_DATE::date,
        '1 day'::interval
    )::date as day
),
phone_entries AS (
    SELECT
        (created_at + INTERVAL '5 hours 30 minutes')::date as dt,
        COUNT(*) as cnt
    FROM auth.auth_users
    WHERE (created_at + INTERVAL '5 hours 30 minutes') >= CURRENT_DATE - interval '6 days'
    GROUP BY (created_at + INTERVAL '5 hours 30 minutes')::date
),
wallet_created AS (
    SELECT
        (created_at + INTERVAL '5 hours 30 minutes')::date as dt,
        COUNT(*) as cnt
    FROM wallet.user_wallets
    WHERE (created_at + INTERVAL '5 hours 30 minutes') >= CURRENT_DATE - interval '6 days'
    GROUP BY (created_at + INTERVAL '5 hours 30 minutes')::date
),
wallet_deleted AS (
    SELECT
        (deleted_at + INTERVAL '5 hours 30 minutes')::date as dt,
        COUNT(*) as cnt
    FROM wallet.user_wallets
    WHERE deleted_at IS NOT NULL
      AND (deleted_at + INTERVAL '5 hours 30 minutes') >= CURRENT_DATE - interval '6 days'
    GROUP BY (deleted_at + INTERVAL '5 hours 30 minutes')::date
),
user_first_payment AS (
    SELECT user_id, MIN((created_at + INTERVAL '5 hours 30 minutes')::date) as first_pay_date
    FROM wallet.payment_orders
    WHERE status = 'SUCCESSFUL'
    GROUP BY user_id
),
repeat_recharges AS (
    SELECT
        (po.created_at + INTERVAL '5 hours 30 minutes')::date as dt,
        COUNT(*) as cnt
    FROM wallet.payment_orders po
    JOIN user_first_payment ufp ON po.user_id = ufp.user_id
    WHERE po.status = 'SUCCESSFUL'
      AND (po.created_at + INTERVAL '5 hours 30 minutes') >= CURRENT_DATE - interval '6 days'
      AND (po.created_at + INTERVAL '5 hours 30 minutes')::date > ufp.first_pay_date
    GROUP BY (po.created_at + INTERVAL '5 hours 30 minutes')::date
)
SELECT
    ds.day,
    TO_CHAR(ds.day, 'Mon DD') as day_label,
    COALESCE(pe.cnt, 0) as phone_count,
    COALESCE(wc.cnt, 0) as wallet_count,
    COALESCE(wd.cnt, 0) as deleted_count,
    COALESCE(rr.cnt, 0) as repeat_recharge_count
FROM date_series ds
LEFT JOIN phone_entries pe ON ds.day = pe.dt
LEFT JOIN wallet_created wc ON ds.day = wc.dt
LEFT JOIN wallet_deleted wd ON ds.day = wd.dt
LEFT JOIN repeat_recharges rr ON ds.day = rr.dt
ORDER BY ds.day DESC;
"""

# ADD Transactions Comparison (7 days with by-this-time comparison)
ADD_COMPARISON_QUERY = """
WITH current_time_ist AS (
    SELECT (NOW() + INTERVAL '5 hours 30 minutes')::time as t
),
date_series AS (
    SELECT generate_series(
        (CURRENT_DATE - interval '6 days')::date,
        CURRENT_DATE::date,
        '1 day'::interval
    )::date as day
),
daily_counts AS (
    SELECT
        (created_at + INTERVAL '5 hours 30 minutes')::date as add_date,
        (created_at + INTERVAL '5 hours 30 minutes')::time as add_time,
        COUNT(*) as cnt
    FROM wallet.wallet_transactions
    WHERE type = 'ADD'
      AND (created_at + INTERVAL '5 hours 30 minutes')::date >= CURRENT_DATE - interval '6 days'
    GROUP BY (created_at + INTERVAL '5 hours 30 minutes')::date,
             (created_at + INTERVAL '5 hours 30 minutes')::time
)
SELECT
    ds.day as date,
    TO_CHAR(ds.day, 'Dy Mon DD') as day_label,
    COALESCE((SELECT SUM(cnt) FROM daily_counts WHERE add_date = ds.day), 0) as total_count,
    COALESCE((SELECT SUM(cnt) FROM daily_counts, current_time_ist WHERE add_date = ds.day AND add_time <= current_time_ist.t), 0) as by_now_count
FROM date_series ds
ORDER BY ds.day DESC;
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
    COALESCE(c.phone_number, '-') as phone,
    wt.type,
    wt.amount,
    wt.real_cash_delta,
    wt.virtual_cash_delta,
    wt.comment,
    wt.created_at + INTERVAL '5 hours 30 minutes' as created_at_ist
FROM wallet.wallet_transactions wt
LEFT JOIN customers.customer c ON wt.user_id = c.customer_id
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
# Note: wallet.* tables use timestamp WITHOUT time zone, use +5:30
REVENUE_SUMMARY_QUERY = """
SELECT
    -- BD-1.1: Add Cash (successful payment orders)
    COALESCE((
        SELECT SUM(amount)
        FROM wallet.payment_orders
        WHERE status = 'SUCCESSFUL'
          AND (created_at + INTERVAL '5 hours 30 minutes')::date >= %s
          AND (created_at + INTERVAL '5 hours 30 minutes')::date <= %s
    ), 0) as add_cash_amount,
    COALESCE((
        SELECT COUNT(*)
        FROM wallet.payment_orders
        WHERE status = 'SUCCESSFUL'
          AND (created_at + INTERVAL '5 hours 30 minutes')::date >= %s
          AND (created_at + INTERVAL '5 hours 30 minutes')::date <= %s
    ), 0) as add_cash_count,

    -- BD-1.2: Promotions (virtual cash used in payments)
    COALESCE((
        SELECT SUM(virtual_cash_amount)
        FROM wallet.payment_orders
        WHERE status = 'SUCCESSFUL'
          AND virtual_cash_amount > 0
          AND (created_at + INTERVAL '5 hours 30 minutes')::date >= %s
          AND (created_at + INTERVAL '5 hours 30 minutes')::date <= %s
    ), 0) as promotions_amount,
    COALESCE((
        SELECT COUNT(*)
        FROM wallet.payment_orders
        WHERE status = 'SUCCESSFUL'
          AND virtual_cash_amount > 0
          AND (created_at + INTERVAL '5 hours 30 minutes')::date >= %s
          AND (created_at + INTERVAL '5 hours 30 minutes')::date <= %s
    ), 0) as promotions_count,

    -- BD-1.3: Consultations Amount
    COALESCE((
        SELECT SUM(final_amount)
        FROM wallet.wallet_orders
        WHERE status = 'COMPLETED'
          AND (created_at + INTERVAL '5 hours 30 minutes')::date >= %s
          AND (created_at + INTERVAL '5 hours 30 minutes')::date <= %s
    ), 0) as consultations_amount,
    COALESCE((
        SELECT COUNT(*)
        FROM wallet.wallet_orders
        WHERE status = 'COMPLETED'
          AND (created_at + INTERVAL '5 hours 30 minutes')::date >= %s
          AND (created_at + INTERVAL '5 hours 30 minutes')::date <= %s
    ), 0) as consultations_count,

    -- BD-1.4: Astrologer Share
    COALESCE((
        SELECT SUM(consultant_share)
        FROM wallet.wallet_orders
        WHERE status = 'COMPLETED'
          AND (created_at + INTERVAL '5 hours 30 minutes')::date >= %s
          AND (created_at + INTERVAL '5 hours 30 minutes')::date <= %s
    ), 0) as astrologer_share,

    -- BD-1.5: Company Share
    COALESCE((
        SELECT SUM(final_amount - COALESCE(consultant_share, 0))
        FROM wallet.wallet_orders
        WHERE status = 'COMPLETED'
          AND (created_at + INTERVAL '5 hours 30 minutes')::date >= %s
          AND (created_at + INTERVAL '5 hours 30 minutes')::date <= %s
    ), 0) as company_share;
"""

# User Metrics (BD-2.0) - with date range parameters (IST timezone)
# BD-2.1: ARPU (lifetime), BD-2.2: Registrations, BD-2.3: Conversions
# Note: wallet.* tables use timestamp WITHOUT time zone, use +5:30
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
          AND (created_at + INTERVAL '5 hours 30 minutes')::date >= %s
          AND (created_at + INTERVAL '5 hours 30 minutes')::date <= %s
    ), 0) as registrations,

    -- BD-2.3: Conversions (first payment) in date range
    COALESCE((
        SELECT COUNT(*)
        FROM (
            SELECT user_id, MIN(created_at + INTERVAL '5 hours 30 minutes') as first_payment_ist
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
# Excludes deleted guides (test/developer accounts)
# Note: All timestamps stored in UTC. Use + INTERVAL '5 hours 30 minutes' for IST conversion.
CONSULTATION_SUMMARY_QUERY = """
SELECT
    -- All consultations
    COALESCE((
        SELECT COUNT(*)
        FROM consultation.consultation c
        JOIN guide.guide_profile gp ON c.guide_id = gp.id AND gp.deleted_at IS NULL
        WHERE c.state = 'completed'
          AND (c.completed_at + INTERVAL '5 hours 30 minutes')::date >= %s
          AND (c.completed_at + INTERVAL '5 hours 30 minutes')::date <= %s
    ), 0) as all_count,
    COALESCE((
        SELECT SUM(wo.final_amount)
        FROM consultation.consultation c
        JOIN guide.guide_profile gp ON c.guide_id = gp.id AND gp.deleted_at IS NULL
        JOIN wallet.wallet_orders wo ON c.order_id = wo.order_id
        WHERE c.state = 'completed'
          AND (c.completed_at + INTERVAL '5 hours 30 minutes')::date >= %s
          AND (c.completed_at + INTERVAL '5 hours 30 minutes')::date <= %s
    ), 0) as all_amount,

    -- Chat consultations
    COALESCE((
        SELECT COUNT(*)
        FROM consultation.consultation c
        JOIN guide.guide_profile gp ON c.guide_id = gp.id AND gp.deleted_at IS NULL
        WHERE c.state = 'completed' AND c.mode = 'chat'
          AND (c.completed_at + INTERVAL '5 hours 30 minutes')::date >= %s
          AND (c.completed_at + INTERVAL '5 hours 30 minutes')::date <= %s
    ), 0) as chat_count,
    COALESCE((
        SELECT SUM(wo.final_amount)
        FROM consultation.consultation c
        JOIN guide.guide_profile gp ON c.guide_id = gp.id AND gp.deleted_at IS NULL
        JOIN wallet.wallet_orders wo ON c.order_id = wo.order_id
        WHERE c.state = 'completed' AND c.mode = 'chat'
          AND (c.completed_at + INTERVAL '5 hours 30 minutes')::date >= %s
          AND (c.completed_at + INTERVAL '5 hours 30 minutes')::date <= %s
    ), 0) as chat_amount,

    -- Call (voice) consultations
    COALESCE((
        SELECT COUNT(*)
        FROM consultation.consultation c
        JOIN guide.guide_profile gp ON c.guide_id = gp.id AND gp.deleted_at IS NULL
        WHERE c.state = 'completed' AND c.mode = 'voice'
          AND (c.completed_at + INTERVAL '5 hours 30 minutes')::date >= %s
          AND (c.completed_at + INTERVAL '5 hours 30 minutes')::date <= %s
    ), 0) as call_count,
    COALESCE((
        SELECT SUM(wo.final_amount)
        FROM consultation.consultation c
        JOIN guide.guide_profile gp ON c.guide_id = gp.id AND gp.deleted_at IS NULL
        JOIN wallet.wallet_orders wo ON c.order_id = wo.order_id
        WHERE c.state = 'completed' AND c.mode = 'voice'
          AND (c.completed_at + INTERVAL '5 hours 30 minutes')::date >= %s
          AND (c.completed_at + INTERVAL '5 hours 30 minutes')::date <= %s
    ), 0) as call_amount;
"""

# Consultation Request Acceptance by Astrologer (IST timezone)
# Shows requests sent to each astrologer and their acceptance stats
CONSULTATION_REQUESTS_QUERY = """
SELECT
    c.guide_id,
    gp.full_name as guide_name,
    COUNT(*) as total_requests,
    COUNT(*) FILTER (WHERE c.accepted_at IS NOT NULL) as accepted,
    COUNT(*) FILTER (WHERE c.state = 'guide_rejected') as rejected,
    COUNT(*) FILTER (WHERE c.state IN ('request_expired', 'request_join_timeout')) as timed_out,
    COUNT(*) FILTER (WHERE c.state = 'completed') as completed
FROM consultation.consultation c
JOIN guide.guide_profile gp ON c.guide_id = gp.id AND gp.deleted_at IS NULL
WHERE c.deleted_at IS NULL
  AND (c.created_at + INTERVAL '5 hours 30 minutes')::date >= %s
  AND (c.created_at + INTERVAL '5 hours 30 minutes')::date <= %s
GROUP BY c.guide_id, gp.full_name
ORDER BY total_requests DESC;
"""

# Consultation by Astrologer (BD-3.0) - Per astrologer breakdown (IST timezone)
# Excludes deleted guides (test/developer accounts)
# Pivoted: one row per astrologer with chat/call columns + duration stats per mode
CONSULTATION_BY_ASTROLOGER_QUERY = """
SELECT
    gp.id as guide_id,
    gp.full_name as astrologer,
    -- Chat stats
    COUNT(*) FILTER (WHERE c.mode = 'chat') as chat_count,
    COALESCE(SUM(wo.final_amount) FILTER (WHERE c.mode = 'chat'), 0) as chat_amount,
    COALESCE(AVG(wo.final_amount) FILTER (WHERE c.mode = 'chat'), 0) as chat_avg_earn,
    COALESCE(SUM(wo.minutes_ordered + wo.seconds_ordered / 60.0) FILTER (WHERE c.mode = 'chat'), 0) as chat_total_dur,
    COALESCE(AVG(wo.minutes_ordered + wo.seconds_ordered / 60.0) FILTER (WHERE c.mode = 'chat'), 0) as chat_mean_dur,
    -- Call stats
    COUNT(*) FILTER (WHERE c.mode = 'voice') as call_count,
    COALESCE(SUM(wo.final_amount) FILTER (WHERE c.mode = 'voice'), 0) as call_amount,
    COALESCE(AVG(wo.final_amount) FILTER (WHERE c.mode = 'voice'), 0) as call_avg_earn,
    COALESCE(SUM(wo.minutes_ordered + wo.seconds_ordered / 60.0) FILTER (WHERE c.mode = 'voice'), 0) as call_total_dur,
    COALESCE(AVG(wo.minutes_ordered + wo.seconds_ordered / 60.0) FILTER (WHERE c.mode = 'voice'), 0) as call_mean_dur
FROM consultation.consultation c
JOIN guide.guide_profile gp ON c.guide_id = gp.id AND gp.deleted_at IS NULL
LEFT JOIN wallet.wallet_orders wo ON c.order_id = wo.order_id
WHERE c.state = 'completed'
  AND (c.completed_at + INTERVAL '5 hours 30 minutes')::date >= %s
  AND (c.completed_at + INTERVAL '5 hours 30 minutes')::date <= %s
GROUP BY gp.id, gp.full_name
ORDER BY (COALESCE(SUM(wo.final_amount), 0)) DESC;
"""

# Payment Metrics (BD-4.0) - with date range parameters (IST timezone)
# BD-4.1: Number of Payments, BD-4.2: Amount, BD-4.3: Success Rate, BD-4.4: By Payment Mode
PAYMENT_SUMMARY_QUERY = """
SELECT
    -- BD-4.1: Total Payments (attempted)
    COALESCE((
        SELECT COUNT(*)
        FROM wallet.payment_orders
        WHERE (created_at + INTERVAL '5 hours 30 minutes')::date >= %s
          AND (created_at + INTERVAL '5 hours 30 minutes')::date <= %s
    ), 0) as total_count,

    -- BD-4.2: Total Amount (successful only)
    COALESCE((
        SELECT SUM(amount)
        FROM wallet.payment_orders
        WHERE status = 'SUCCESSFUL'
          AND (created_at + INTERVAL '5 hours 30 minutes')::date >= %s
          AND (created_at + INTERVAL '5 hours 30 minutes')::date <= %s
    ), 0) as successful_amount,

    -- Successful count
    COALESCE((
        SELECT COUNT(*)
        FROM wallet.payment_orders
        WHERE status = 'SUCCESSFUL'
          AND (created_at + INTERVAL '5 hours 30 minutes')::date >= %s
          AND (created_at + INTERVAL '5 hours 30 minutes')::date <= %s
    ), 0) as successful_count,

    -- Failed count
    COALESCE((
        SELECT COUNT(*)
        FROM wallet.payment_orders
        WHERE status = 'FAILED'
          AND (created_at + INTERVAL '5 hours 30 minutes')::date >= %s
          AND (created_at + INTERVAL '5 hours 30 minutes')::date <= %s
    ), 0) as failed_count,

    -- Pending count
    COALESCE((
        SELECT COUNT(*)
        FROM wallet.payment_orders
        WHERE status = 'PENDING'
          AND (created_at + INTERVAL '5 hours 30 minutes')::date >= %s
          AND (created_at + INTERVAL '5 hours 30 minutes')::date <= %s
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
WHERE (created_at + INTERVAL '5 hours 30 minutes')::date >= %s
  AND (created_at + INTERVAL '5 hours 30 minutes')::date <= %s
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

# Failed Payments - Details of users with failed payments (IST timezone)
FAILED_PAYMENTS_QUERY = """
SELECT
    po.payment_order_id,
    po.user_id,
    COALESCE(uw.name, 'Unknown') as user_name,
    COALESCE(c.phone_number, '-') as phone,
    po.amount,
    CASE
        WHEN po.payment_method::text IN ('UPI', 'UPI_QR') THEN 'UPI'
        WHEN po.payment_method::text = 'CREDIT_CARD' THEN 'Card'
        WHEN po.payment_method::text = 'DEBIT_CARD' THEN 'Card'
        ELSE COALESCE(po.payment_method::text, '-')
    END as method,
    po.created_at + INTERVAL '5 hours 30 minutes' as created_ist
FROM wallet.payment_orders po
LEFT JOIN wallet.user_wallets uw ON po.user_id = uw.user_id
LEFT JOIN customers.customer c ON po.user_id = c.customer_id
WHERE po.status = 'FAILED'
  AND (po.created_at + INTERVAL '5 hours 30 minutes')::date >= %s
  AND (po.created_at + INTERVAL '5 hours 30 minutes')::date <= %s
ORDER BY po.created_at DESC;
"""

# Pending Payments - Details of users with pending payments (IST timezone)
PENDING_PAYMENTS_QUERY = """
SELECT
    po.payment_order_id,
    po.user_id,
    COALESCE(uw.name, 'Unknown') as user_name,
    COALESCE(c.phone_number, '-') as phone,
    po.amount,
    CASE
        WHEN po.payment_method::text IN ('UPI', 'UPI_QR') THEN 'UPI'
        WHEN po.payment_method::text = 'CREDIT_CARD' THEN 'Card'
        WHEN po.payment_method::text = 'DEBIT_CARD' THEN 'Card'
        ELSE COALESCE(po.payment_method::text, '-')
    END as method,
    po.created_at + INTERVAL '5 hours 30 minutes' as created_ist
FROM wallet.payment_orders po
LEFT JOIN wallet.user_wallets uw ON po.user_id = uw.user_id
LEFT JOIN customers.customer c ON po.user_id = c.customer_id
WHERE po.status = 'PENDING'
  AND (po.created_at + INTERVAL '5 hours 30 minutes')::date >= %s
  AND (po.created_at + INTERVAL '5 hours 30 minutes')::date <= %s
ORDER BY po.created_at DESC;
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
  AND (c.completed_at + INTERVAL '5 hours 30 minutes')::date >= %s
  AND (c.completed_at + INTERVAL '5 hours 30 minutes')::date <= %s
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
        action_tstamp + INTERVAL '5 hours 30 minutes' as changed_at_ist
    FROM audit.logged_actions
    WHERE table_name = 'guide_profile'
      AND action = 'U'
      AND original_data->>'availability_state' IS DISTINCT FROM new_data->>'availability_state'
      AND (action_tstamp + INTERVAL '5 hours 30 minutes')::date >= %s
      AND (action_tstamp + INTERVAL '5 hours 30 minutes')::date <= %s
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
            COALESCE(session_end, NOW() + INTERVAL '5 hours 30 minutes') - session_start
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
        MIN(created_at + INTERVAL '5 hours 30 minutes') as first_recharge_date_ist
    FROM wallet.payment_orders
    WHERE status = 'SUCCESSFUL'
    GROUP BY user_id
)
SELECT
    COUNT(*) as new_paying_customers,
    COALESCE(SUM(po.amount), 0) as total_recharge_amount
FROM first_recharges fr
JOIN wallet.payment_orders po ON fr.user_id = po.user_id
    AND (po.created_at + INTERVAL '5 hours 30 minutes')::date = fr.first_recharge_date_ist::date
    AND po.status = 'SUCCESSFUL'
WHERE fr.first_recharge_date_ist::date >= %s
  AND fr.first_recharge_date_ist::date <= %s;
"""

# --- Guides Dashboard Queries ---

# Guide counts (online/offline/total)
GUIDE_COUNTS_QUERY = """
SELECT
    COUNT(*) FILTER (WHERE availability_state = 'ONLINE_AVAILABLE') as online_guides,
    COUNT(*) FILTER (WHERE availability_state = 'OFFLINE') as offline_guides,
    COUNT(*) as total_guides
FROM guide.guide_profile
WHERE deleted_at IS NULL;
"""

# Channel counts (chat/voice/video for online guides)
GUIDE_CHANNEL_COUNTS_QUERY = """
SELECT
    COUNT(*) FILTER (WHERE chat_enabled = true) as online_chat_guides,
    COUNT(*) FILTER (WHERE voice_enabled = true) as online_voice_guides,
    COUNT(*) FILTER (WHERE video_enabled = true) as online_video_guides
FROM guide.guide_profile
WHERE availability_state = 'ONLINE_AVAILABLE'
  AND deleted_at IS NULL;
"""

# Skills breakdown (online/offline per skill)
GUIDE_SKILLS_BREAKDOWN_QUERY = """
SELECT
    s.name as skill_name,
    COUNT(*) FILTER (WHERE gp.availability_state = 'ONLINE_AVAILABLE') as online_count,
    COUNT(*) FILTER (WHERE gp.availability_state != 'ONLINE_AVAILABLE') as offline_count,
    COUNT(*) as total_count
FROM guide.skills s
LEFT JOIN guide.guide_skills gs ON s.id = gs.skill_id AND gs.deleted_at IS NULL
LEFT JOIN guide.guide_profile gp ON gs.guide_id = gp.id AND gp.deleted_at IS NULL
WHERE s.deleted_at IS NULL
GROUP BY s.id, s.name
HAVING COUNT(gp.id) > 0
ORDER BY online_count DESC, s.name;
"""

# Online guides with details
ONLINE_GUIDES_QUERY = """
WITH guide_skills_agg AS (
    SELECT
        gs.guide_id,
        STRING_AGG(s.name, ', ' ORDER BY s.name) as skills
    FROM guide.guide_skills gs
    JOIN guide.skills s ON gs.skill_id = s.id
    WHERE gs.deleted_at IS NULL
    GROUP BY gs.guide_id
),
guide_earnings AS (
    SELECT
        gp.id as guide_id,
        COALESCE(SUM(wo.consultant_share), 0) as total_earnings
    FROM guide.guide_profile gp
    LEFT JOIN wallet.consultant_wallets cw
        ON REPLACE(REPLACE(gp.phone_number, '+91', ''), '+', '') = cw.phone_number
        AND cw.deleted_at IS NULL
    LEFT JOIN wallet.wallet_orders wo
        ON cw.consultant_id = wo.consultant_id
        AND wo.status = 'COMPLETED'
        AND wo.consultant_share IS NOT NULL
    WHERE gp.deleted_at IS NULL
    GROUP BY gp.id
),
guide_pricing AS (
    SELECT
        gp.id as guide_id,
        c.price_per_minute
    FROM guide.guide_profile gp
    LEFT JOIN wallet.consultants c
        ON REPLACE(REPLACE(gp.phone_number, '+91', ''), '+', '') = c.phone_number
    WHERE gp.deleted_at IS NULL
),
guide_orders_today AS (
    SELECT
        gp.id as guide_id,
        COUNT(*) FILTER (WHERE wo.status = 'PENDING') as pending_count,
        COUNT(*) FILTER (WHERE wo.status = 'INPROGRESS') as inprogress_count,
        STRING_AGG(DISTINCT u.name, ', ' ORDER BY u.name) FILTER (WHERE wo.status = 'INPROGRESS') as inprogress_customers,
        COUNT(*) FILTER (WHERE wo.status = 'COMPLETED') as completed_count,
        COALESCE(SUM(wo.consultant_share) FILTER (WHERE wo.status = 'COMPLETED'), 0) as today_earnings,
        COUNT(*) FILTER (WHERE wo.status = 'REFUNDED') as refunded_count,
        COUNT(*) FILTER (WHERE wo.status = 'CANCELLED') as cancelled_count
    FROM guide.guide_profile gp
    LEFT JOIN wallet.consultant_wallets cw
        ON REPLACE(REPLACE(gp.phone_number, '+91', ''), '+', '') = cw.phone_number
        AND cw.deleted_at IS NULL
    LEFT JOIN wallet.wallet_orders wo
        ON cw.consultant_id = wo.consultant_id
        AND DATE(wo.created_at + INTERVAL '5 hours 30 minutes') = CURRENT_DATE
    LEFT JOIN wallet.users u
        ON wo.user_id = u.user_id
    WHERE gp.deleted_at IS NULL
    GROUP BY gp.id
),
guide_sessions AS (
    SELECT
        gp.id as guide_id,
        MAX(us.refresh_token_exp) as token_exp
    FROM guide.guide_profile gp
    LEFT JOIN auth.auth_users au
        ON REPLACE(REPLACE(gp.phone_number, '+91', ''), '+', '') = au.phone_number
    LEFT JOIN auth.user_sessions us
        ON au.id = us.auth_user_id AND us.user_type = 'guide'
    WHERE gp.deleted_at IS NULL
    GROUP BY gp.id
)
SELECT
    gp.id,
    gp.full_name,
    gp.phone_number,
    gp.chat_enabled,
    gp.voice_enabled,
    gp.video_enabled,
    COALESCE(gsa.skills, 'No skills') as skills,
    COALESCE(gpr.price_per_minute, 0) as price_per_minute,
    gp.guide_stats->>'rating' as rating,
    gp.guide_stats->>'total_number_of_completed_consultations' as completed_consultations,
    COALESCE(ge.total_earnings, 0) as total_earnings,
    COALESCE(got.pending_count, 0) as today_pending,
    COALESCE(got.inprogress_count, 0) as today_inprogress_count,
    COALESCE(got.inprogress_customers, '-') as today_inprogress_customers,
    COALESCE(got.completed_count, 0) as today_completed,
    COALESCE(got.today_earnings, 0) as today_earnings,
    COALESCE(got.refunded_count, 0) as today_refunded,
    COALESCE(got.cancelled_count, 0) as today_cancelled,
    CASE
        WHEN gsess.token_exp IS NULL THEN 'No Session'
        WHEN gsess.token_exp < NOW() THEN 'Expired'
        ELSE 'Active'
    END as session_status
FROM guide.guide_profile gp
LEFT JOIN guide_skills_agg gsa ON gp.id = gsa.guide_id
LEFT JOIN guide_earnings ge ON gp.id = ge.guide_id
LEFT JOIN guide_pricing gpr ON gp.id = gpr.guide_id
LEFT JOIN guide_orders_today got ON gp.id = got.guide_id
LEFT JOIN guide_sessions gsess ON gp.id = gsess.guide_id
WHERE gp.availability_state IN ('ONLINE_AVAILABLE', 'ONLINE_BUSY')
  AND gp.deleted_at IS NULL
  AND gp.full_name NOT IN ('Aman Jain', 'Praveen')
ORDER BY COALESCE(got.today_earnings, 0) DESC;
"""

# Offline guides with details
OFFLINE_GUIDES_QUERY = """
WITH guide_skills_agg AS (
    SELECT
        gs.guide_id,
        STRING_AGG(s.name, ', ' ORDER BY s.name) as skills
    FROM guide.guide_skills gs
    JOIN guide.skills s ON gs.skill_id = s.id
    WHERE gs.deleted_at IS NULL
    GROUP BY gs.guide_id
),
guide_earnings AS (
    SELECT
        gp.id as guide_id,
        COALESCE(SUM(wo.consultant_share), 0) as total_earnings
    FROM guide.guide_profile gp
    LEFT JOIN wallet.consultant_wallets cw
        ON REPLACE(REPLACE(gp.phone_number, '+91', ''), '+', '') = cw.phone_number
        AND cw.deleted_at IS NULL
    LEFT JOIN wallet.wallet_orders wo
        ON cw.consultant_id = wo.consultant_id
        AND wo.status = 'COMPLETED'
        AND wo.consultant_share IS NOT NULL
    WHERE gp.deleted_at IS NULL
    GROUP BY gp.id
),
guide_pricing AS (
    SELECT
        gp.id as guide_id,
        c.price_per_minute
    FROM guide.guide_profile gp
    LEFT JOIN wallet.consultants c
        ON REPLACE(REPLACE(gp.phone_number, '+91', ''), '+', '') = c.phone_number
    WHERE gp.deleted_at IS NULL
),
guide_orders_today AS (
    SELECT
        gp.id as guide_id,
        COUNT(*) FILTER (WHERE wo.status = 'PENDING') as pending_count,
        COUNT(*) FILTER (WHERE wo.status = 'INPROGRESS') as inprogress_count,
        STRING_AGG(DISTINCT u.name, ', ' ORDER BY u.name) FILTER (WHERE wo.status = 'INPROGRESS') as inprogress_customers,
        COUNT(*) FILTER (WHERE wo.status = 'COMPLETED') as completed_count,
        COALESCE(SUM(wo.consultant_share) FILTER (WHERE wo.status = 'COMPLETED'), 0) as today_earnings,
        COUNT(*) FILTER (WHERE wo.status = 'REFUNDED') as refunded_count,
        COUNT(*) FILTER (WHERE wo.status = 'CANCELLED') as cancelled_count
    FROM guide.guide_profile gp
    LEFT JOIN wallet.consultant_wallets cw
        ON REPLACE(REPLACE(gp.phone_number, '+91', ''), '+', '') = cw.phone_number
        AND cw.deleted_at IS NULL
    LEFT JOIN wallet.wallet_orders wo
        ON cw.consultant_id = wo.consultant_id
        AND DATE(wo.created_at + INTERVAL '5 hours 30 minutes') = CURRENT_DATE
    LEFT JOIN wallet.users u
        ON wo.user_id = u.user_id
    WHERE gp.deleted_at IS NULL
    GROUP BY gp.id
),
guide_sessions AS (
    SELECT
        gp.id as guide_id,
        MAX(us.refresh_token_exp) as token_exp
    FROM guide.guide_profile gp
    LEFT JOIN auth.auth_users au
        ON REPLACE(REPLACE(gp.phone_number, '+91', ''), '+', '') = au.phone_number
    LEFT JOIN auth.user_sessions us
        ON au.id = us.auth_user_id AND us.user_type = 'guide'
    WHERE gp.deleted_at IS NULL
    GROUP BY gp.id
)
SELECT
    gp.id,
    gp.full_name,
    gp.phone_number,
    gp.chat_enabled,
    gp.voice_enabled,
    gp.video_enabled,
    COALESCE(gsa.skills, 'No skills') as skills,
    COALESCE(gpr.price_per_minute, 0) as price_per_minute,
    gp.guide_stats->>'rating' as rating,
    gp.guide_stats->>'total_number_of_completed_consultations' as completed_consultations,
    COALESCE(ge.total_earnings, 0) as total_earnings,
    COALESCE(got.pending_count, 0) as today_pending,
    COALESCE(got.inprogress_count, 0) as today_inprogress_count,
    COALESCE(got.inprogress_customers, '-') as today_inprogress_customers,
    COALESCE(got.completed_count, 0) as today_completed,
    COALESCE(got.today_earnings, 0) as today_earnings,
    COALESCE(got.refunded_count, 0) as today_refunded,
    COALESCE(got.cancelled_count, 0) as today_cancelled,
    CASE
        WHEN gsess.token_exp IS NULL THEN 'No Session'
        WHEN gsess.token_exp < NOW() THEN 'Expired'
        ELSE 'Active'
    END as session_status
FROM guide.guide_profile gp
LEFT JOIN guide_skills_agg gsa ON gp.id = gsa.guide_id
LEFT JOIN guide_earnings ge ON gp.id = ge.guide_id
LEFT JOIN guide_pricing gpr ON gp.id = gpr.guide_id
LEFT JOIN guide_orders_today got ON gp.id = got.guide_id
LEFT JOIN guide_sessions gsess ON gp.id = gsess.guide_id
WHERE gp.availability_state NOT IN ('ONLINE_AVAILABLE', 'ONLINE_BUSY')
  AND gp.deleted_at IS NULL
  AND gp.full_name NOT IN ('Aman Jain', 'Praveen')
ORDER BY COALESCE(got.today_earnings, 0) DESC;
"""

# Test guides (Aman Jain and Praveen)
TEST_GUIDES_QUERY = """
WITH guide_skills_agg AS (
    SELECT
        gs.guide_id,
        STRING_AGG(s.name, ', ' ORDER BY s.name) as skills
    FROM guide.guide_skills gs
    JOIN guide.skills s ON gs.skill_id = s.id
    WHERE gs.deleted_at IS NULL
    GROUP BY gs.guide_id
),
guide_earnings AS (
    SELECT
        gp.id as guide_id,
        COALESCE(SUM(wo.consultant_share), 0) as total_earnings
    FROM guide.guide_profile gp
    LEFT JOIN wallet.consultant_wallets cw
        ON REPLACE(REPLACE(gp.phone_number, '+91', ''), '+', '') = cw.phone_number
        AND cw.deleted_at IS NULL
    LEFT JOIN wallet.wallet_orders wo
        ON cw.consultant_id = wo.consultant_id
        AND wo.status = 'COMPLETED'
        AND wo.consultant_share IS NOT NULL
    WHERE gp.deleted_at IS NULL
    GROUP BY gp.id
),
guide_pricing AS (
    SELECT
        gp.id as guide_id,
        c.price_per_minute
    FROM guide.guide_profile gp
    LEFT JOIN wallet.consultants c
        ON REPLACE(REPLACE(gp.phone_number, '+91', ''), '+', '') = c.phone_number
    WHERE gp.deleted_at IS NULL
),
guide_orders_today AS (
    SELECT
        gp.id as guide_id,
        COUNT(*) FILTER (WHERE wo.status = 'PENDING') as pending_count,
        COUNT(*) FILTER (WHERE wo.status = 'INPROGRESS') as inprogress_count,
        STRING_AGG(DISTINCT u.name, ', ' ORDER BY u.name) FILTER (WHERE wo.status = 'INPROGRESS') as inprogress_customers,
        COUNT(*) FILTER (WHERE wo.status = 'COMPLETED') as completed_count,
        COALESCE(SUM(wo.consultant_share) FILTER (WHERE wo.status = 'COMPLETED'), 0) as today_earnings,
        COUNT(*) FILTER (WHERE wo.status = 'REFUNDED') as refunded_count,
        COUNT(*) FILTER (WHERE wo.status = 'CANCELLED') as cancelled_count
    FROM guide.guide_profile gp
    LEFT JOIN wallet.consultant_wallets cw
        ON REPLACE(REPLACE(gp.phone_number, '+91', ''), '+', '') = cw.phone_number
        AND cw.deleted_at IS NULL
    LEFT JOIN wallet.wallet_orders wo
        ON cw.consultant_id = wo.consultant_id
        AND DATE(wo.created_at + INTERVAL '5 hours 30 minutes') = CURRENT_DATE
    LEFT JOIN wallet.users u
        ON wo.user_id = u.user_id
    WHERE gp.deleted_at IS NULL
    GROUP BY gp.id
),
guide_sessions AS (
    SELECT
        gp.id as guide_id,
        MAX(us.refresh_token_exp) as token_exp
    FROM guide.guide_profile gp
    LEFT JOIN auth.auth_users au
        ON REPLACE(REPLACE(gp.phone_number, '+91', ''), '+', '') = au.phone_number
    LEFT JOIN auth.user_sessions us
        ON au.id = us.auth_user_id AND us.user_type = 'guide'
    WHERE gp.deleted_at IS NULL
    GROUP BY gp.id
)
SELECT
    gp.id,
    gp.full_name,
    gp.phone_number,
    gp.availability_state,
    gp.chat_enabled,
    gp.voice_enabled,
    gp.video_enabled,
    COALESCE(gsa.skills, 'No skills') as skills,
    COALESCE(gpr.price_per_minute, 0) as price_per_minute,
    gp.guide_stats->>'rating' as rating,
    gp.guide_stats->>'total_number_of_completed_consultations' as completed_consultations,
    COALESCE(ge.total_earnings, 0) as total_earnings,
    COALESCE(got.pending_count, 0) as today_pending,
    COALESCE(got.inprogress_count, 0) as today_inprogress_count,
    COALESCE(got.inprogress_customers, '-') as today_inprogress_customers,
    COALESCE(got.completed_count, 0) as today_completed,
    COALESCE(got.today_earnings, 0) as today_earnings,
    COALESCE(got.refunded_count, 0) as today_refunded,
    COALESCE(got.cancelled_count, 0) as today_cancelled,
    CASE
        WHEN gsess.token_exp IS NULL THEN 'No Session'
        WHEN gsess.token_exp < NOW() THEN 'Expired'
        ELSE 'Active'
    END as session_status
FROM guide.guide_profile gp
LEFT JOIN guide_skills_agg gsa ON gp.id = gsa.guide_id
LEFT JOIN guide_earnings ge ON gp.id = ge.guide_id
LEFT JOIN guide_pricing gpr ON gp.id = gpr.guide_id
LEFT JOIN guide_orders_today got ON gp.id = got.guide_id
LEFT JOIN guide_sessions gsess ON gp.id = gsess.guide_id
WHERE gp.deleted_at IS NULL
  AND gp.full_name IN ('Aman Jain', 'Praveen')
ORDER BY COALESCE(got.today_earnings, 0) DESC;
"""

# Promo grant spending by guide (simplified - counts promotional spent transactions per guide)
PROMO_GRANT_SPENDING_QUERY = """
SELECT
    wo.consultant_id,
    gp.full_name as guide_name,
    COUNT(*) as grants_spent_on_this_guide
FROM wallet.wallet_transactions wt
JOIN wallet.wallet_orders wo ON wt.order_id = wo.order_id
LEFT JOIN guide.guide_profile gp ON wo.consultant_id = gp.id
WHERE wt.type = 'SPENT'
  AND wt.is_promotional = true
  AND wt.created_at >= '2025-11-13 00:00:00'
GROUP BY wo.consultant_id, gp.full_name
ORDER BY grants_spent_on_this_guide DESC;
"""

# Latest feedback by guide
LATEST_FEEDBACK_QUERY = """
SELECT DISTINCT ON (c.guide_id)
    c.guide_id,
    c.guide_name,
    c.customer_name,
    f.rating,
    f.feedback,
    f.created_at as feedback_date,
    c.order_id
FROM consultation.feedback f
JOIN consultation.consultation c ON f.consultation_id = c.id
WHERE f.deleted_at IS NULL
  AND c.deleted_at IS NULL
ORDER BY c.guide_id, f.created_at DESC;
"""

# Consultation Connection Performance (since Dec 5, 2025)
# Analyzes how many attempts customers make before connecting to a guide
CONSULTATION_PERFORMANCE_QUERY = """
WITH customer_attempts AS (
    SELECT
        c.customer_id,
        c.created_at + INTERVAL '5 hours 30 minutes' as attempt_time,
        c.state,
        c.completed_at + INTERVAL '5 hours 30 minutes' as completed_time,
        CASE WHEN c.state = 'completed' THEN 1 ELSE 0 END as is_success
    FROM consultation.consultation c
    JOIN guide.guide_profile gp ON c.guide_id = gp.id AND gp.deleted_at IS NULL
    WHERE c.deleted_at IS NULL
      AND (c.created_at + INTERVAL '5 hours 30 minutes')::date >= %s
      AND (c.created_at + INTERVAL '5 hours 30 minutes')::date <= %s
),
-- Add lag for session detection (separate CTE to avoid nested window functions)
attempts_with_lag AS (
    SELECT
        *,
        LAG(attempt_time) OVER (PARTITION BY customer_id ORDER BY attempt_time) as prev_attempt
    FROM customer_attempts
),
-- Session-based grouping (30 min gap = new session)
sessions AS (
    SELECT
        *,
        SUM(CASE WHEN prev_attempt IS NULL OR attempt_time - prev_attempt > INTERVAL '30 minutes' THEN 1 ELSE 0 END)
            OVER (PARTITION BY customer_id ORDER BY attempt_time) as session_id
    FROM attempts_with_lag
),
session_stats AS (
    SELECT
        customer_id,
        session_id,
        COUNT(*) as attempts_in_session,
        MAX(is_success) as session_succeeded,
        MIN(attempt_time) as session_start,
        MAX(CASE WHEN is_success = 1 THEN completed_time END) as success_time
    FROM sessions
    GROUP BY customer_id, session_id
)
SELECT
    -- Overall stats
    (SELECT COUNT(*) FROM customer_attempts) as total_attempts,
    (SELECT SUM(is_success) FROM customer_attempts) as total_successes,
    (SELECT ROUND(100.0 * SUM(is_success) / NULLIF(COUNT(*), 0), 1) FROM customer_attempts) as success_rate,
    -- Session stats
    (SELECT COUNT(*) FROM session_stats WHERE session_succeeded = 1) as successful_sessions,
    (SELECT ROUND(AVG(attempts_in_session)::numeric, 1) FROM session_stats WHERE session_succeeded = 1) as avg_attempts_per_session,
    -- First try success
    (SELECT COUNT(*) FROM session_stats WHERE session_succeeded = 1 AND attempts_in_session = 1) as first_try_success,
    (SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE attempts_in_session = 1) / NULLIF(COUNT(*), 0), 1)
     FROM session_stats WHERE session_succeeded = 1) as first_try_rate,
    -- Time to connect (within session)
    (SELECT ROUND(AVG(EXTRACT(EPOCH FROM (success_time - session_start)) / 60)::numeric, 1)
     FROM session_stats WHERE session_succeeded = 1 AND success_time IS NOT NULL) as avg_minutes_to_connect;
"""
