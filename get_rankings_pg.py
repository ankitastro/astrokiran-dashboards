#!/usr/bin/env python3
"""
Get guide rankings from PostgreSQL (real-time).
9-factor algorithm: Repeat=35%, AOV=15%, Volume=15%, Activity=15%, Rating=5%, Response=5%, Consistency=5%, Reliability=3%, Experience=2%
Activity multiplier penalty: <5d=0.5x, 5-10d=0.75x, 10-15d=0.9x, 15+d=1.0x
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

PG_CONFIG = {
    'host': os.getenv('DB_ENDPOINT'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': 'astrokiran',
    'user': os.getenv('DB_USERNAME'),
    'password': os.getenv('DB_PASSWORD')
}

PG_PRIMARY_CONFIG = {
    'host': os.getenv('DB_PRIMARY_ENDPOINT'),
    'port': int(os.getenv('DB_PRIMARY_PORT', 5432)),
    'database': os.getenv('DB_PRIMARY_NAME', 'astrokiran'),
    'user': os.getenv('DB_PRIMARY_USERNAME'),
    'password': os.getenv('DB_PRIMARY_PASSWORD')
}

TEST_GUIDES = ('Aman Jain', 'Praveen')

RANKING_QUERY = '''
WITH guide_activity AS (
    SELECT
        (original_data->>'id')::int as guide_id,
        COUNT(DISTINCT DATE(action_tstamp)) as days_active
    FROM audit.logged_actions
    WHERE table_name = 'guide_profile'
      AND original_data->>'availability_state' IS DISTINCT FROM new_data->>'availability_state'
      AND action_tstamp >= NOW() - INTERVAL '30 days'
    GROUP BY original_data->>'id'
),
consultation_stats AS (
    SELECT
        c.guide_id,
        COUNT(*) FILTER (WHERE c.state = 'completed') as completed,
        COUNT(DISTINCT c.customer_id) FILTER (WHERE c.state = 'completed') as unique_customers,
        COUNT(*) FILTER (WHERE c.state IN ('completed', 'cancelled', 'guide_rejected')) as total_cons,
        COUNT(*) FILTER (WHERE c.state IN ('cancelled', 'guide_rejected')) as cancelled,
        AVG(EXTRACT(EPOCH FROM (c.accepted_at - c.requested_at)))
            FILTER (WHERE c.state = 'completed' AND c.requested_at IS NOT NULL AND c.accepted_at IS NOT NULL) as avg_response_seconds
    FROM consultation.consultation c
    WHERE c.deleted_at IS NULL
    GROUP BY c.guide_id
),
feedback_stats AS (
    SELECT
        c.guide_id,
        COUNT(f.id) as review_count,
        AVG(f.rating) as avg_rating
    FROM consultation.consultation c
    JOIN consultation.feedback f ON f.consultation_id = c.id AND f.deleted_at IS NULL
    WHERE c.state = 'completed' AND c.deleted_at IS NULL
    GROUP BY c.guide_id
),
order_stats AS (
    -- AOV from SPENT transactions (real cash only)
    SELECT
        wo.consultant_id as guide_id,
        AVG(ABS(t.real_cash_delta)) as avg_order_value,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ABS(t.real_cash_delta)) as median_order_value
    FROM wallet.wallet_transactions t
    JOIN wallet.wallet_orders wo ON wo.order_id = t.order_id
    WHERE t.type = 'SPENT' AND t.real_cash_delta < 0
    GROUP BY wo.consultant_id
),
guide_spends AS (
    -- All SPENT transactions per guide with row number
    SELECT t.user_id, wo.consultant_id as guide_id, t.created_at as spent_at,
           ROW_NUMBER() OVER (PARTITION BY t.user_id, wo.consultant_id ORDER BY t.created_at) as spend_num
    FROM wallet.wallet_transactions t
    JOIN wallet.wallet_orders wo ON wo.order_id = t.order_id
    WHERE t.type = 'SPENT'
),
user_first_spend AS (
    -- First spend per user per guide
    SELECT user_id, guide_id, spent_at as first_spent_at
    FROM guide_spends WHERE spend_num = 1
),
user_adds_after_spend AS (
    -- Users who added after first spend on a guide
    SELECT DISTINCT ufs.user_id, ufs.guide_id
    FROM user_first_spend ufs
    JOIN wallet.wallet_transactions t ON t.user_id = ufs.user_id
        AND t.type = 'ADD' AND t.created_at > ufs.first_spent_at
),
user_repeat_spend AS (
    -- Users who spent again after adding
    SELECT DISTINCT uaas.user_id, uaas.guide_id
    FROM user_adds_after_spend uaas
    JOIN guide_spends gs ON gs.user_id = uaas.user_id
        AND gs.guide_id = uaas.guide_id AND gs.spend_num > 1
),
repeat_stats AS (
    SELECT
        ufs.guide_id,
        COUNT(DISTINCT ufs.user_id) as total_customers,
        COUNT(DISTINCT urs.user_id) as repeat_customers
    FROM user_first_spend ufs
    LEFT JOIN user_repeat_spend urs ON urs.user_id = ufs.user_id AND urs.guide_id = ufs.guide_id
    GROUP BY ufs.guide_id
),
guide_scores AS (
    SELECT
        g.id,
        g.full_name,
        COALESCE(ga.days_active, 0) as days_active,
        COALESCE(cs.completed, 0) as total_consultations,
        COALESCE(cs.unique_customers, 0) as unique_customers,
        COALESCE(rs.total_customers, 0) as total_customers,
        COALESCE(rs.repeat_customers, 0) as repeat_customers,
        COALESCE(os.avg_order_value, 0) as avg_order_value,
        -- Raw values for history
        COALESCE(fs.avg_rating, 0) as avg_rating,
        COALESCE(cs.avg_response_seconds, 0)::int as response_seconds,
        COALESCE(fs.review_count, 0) as review_count,
        COALESCE(cs.cancelled, 0) as cancelled_count,
        EXTRACT(MONTH FROM AGE(NOW(), g.created_at))::int +
            EXTRACT(YEAR FROM AGE(NOW(), g.created_at))::int * 12 as months_on_platform,

        CASE WHEN rs.total_customers > 0
             THEN rs.repeat_customers::float / rs.total_customers ELSE 0
        END as repeat_score,

        CASE WHEN os.avg_order_value >= 50 THEN 1.0
             WHEN os.avg_order_value > 0 THEN os.avg_order_value / 50.0 ELSE 0
        END as aov_score,

        CASE WHEN cs.completed > 0
             THEN LEAST(LOG(cs.completed::float) / LOG(200.0), 1.0) ELSE 0
        END as volume_score,

        CASE WHEN ga.days_active >= 20 THEN 1.0
             WHEN ga.days_active > 0 THEN ga.days_active / 20.0 ELSE 0
        END as activity_score,

        CASE WHEN fs.review_count > 0
             THEN ((fs.review_count * COALESCE(fs.avg_rating, 0) + 5 * 4.0) / (fs.review_count + 5) - 1.0) / 4.0
             ELSE (4.0 - 1.0) / 4.0
        END as rating_score,

        CASE WHEN cs.avg_response_seconds IS NULL THEN 0.5
             WHEN cs.avg_response_seconds <= 30 THEN 1.0
             WHEN cs.avg_response_seconds <= 300 THEN 1.0 - ((cs.avg_response_seconds - 30) / 270.0)
             ELSE 0.5
        END as response_score,

        CASE WHEN cs.completed > 0
             THEN COALESCE(fs.review_count, 0)::float / cs.completed ELSE 0
        END as consistency_score,

        CASE WHEN cs.total_cons > 0
             THEN 1.0 - (cs.cancelled::float / cs.total_cons) ELSE 1.0
        END as reliability_score,

        CASE WHEN g.created_at IS NOT NULL
             THEN LEAST(EXTRACT(EPOCH FROM (NOW() - g.created_at)) / (24.0 * 30 * 24 * 3600), 1.0)
             ELSE 0.5
        END as experience_score,

        CASE WHEN COALESCE(ga.days_active, 0) < 5 THEN 0.5
             WHEN COALESCE(ga.days_active, 0) < 10 THEN 0.75
             WHEN COALESCE(ga.days_active, 0) < 15 THEN 0.9
             ELSE 1.0
        END as activity_multiplier

    FROM guide.guide_profile g
    LEFT JOIN guide_activity ga ON ga.guide_id = g.id
    LEFT JOIN consultation_stats cs ON cs.guide_id = g.id
    LEFT JOIN feedback_stats fs ON fs.guide_id = g.id
    LEFT JOIN order_stats os ON os.guide_id = g.id
    LEFT JOIN repeat_stats rs ON rs.guide_id = g.id
    WHERE g.deleted_at IS NULL
      AND g.full_name NOT IN %s
)
SELECT
    id, full_name as name,
    (
        (repeat_score * 0.35) + (aov_score * 0.15) + (volume_score * 0.15) +
        (activity_score * 0.15) + (rating_score * 0.05) + (response_score * 0.05) +
        (consistency_score * 0.05) + (reliability_score * 0.03) + (experience_score * 0.02)
    ) * activity_multiplier * 10 as ranking,
    activity_multiplier, repeat_score, aov_score, volume_score, activity_score,
    rating_score, response_score, consistency_score, reliability_score, experience_score,
    total_consultations, unique_customers, total_customers, repeat_customers, avg_order_value, days_active,
    avg_rating, response_seconds, review_count, cancelled_count, months_on_platform
FROM guide_scores
ORDER BY ranking DESC
'''


def get_rankings():
    """Fetch rankings from PostgreSQL."""
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(RANKING_QUERY, (TEST_GUIDES,))
    rankings = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rankings


def save_ranking_history(cur, rankings):
    """Insert ranking history records."""
    if not rankings:
        return 0

    values = []
    for r in rankings:
        values.append(f"""(
            {r['id']}, {r['ranking']:.2f}, {r['activity_multiplier']:.2f},
            {r['repeat_score']:.3f}, {r['aov_score']:.3f}, {r['volume_score']:.3f},
            {r['activity_score']:.3f}, {r['rating_score']:.3f}, {r['response_score']:.3f},
            {r['consistency_score']:.3f}, {r['reliability_score']:.3f}, {r['experience_score']:.3f},
            {r['total_consultations']}, {r['unique_customers']}, {r['total_customers']},
            {r['avg_order_value']:.2f}, {r['days_active']},
            {r['avg_rating']:.2f}, {r['response_seconds']}, {r['review_count']},
            {r['cancelled_count']}, {r['months_on_platform']}, {r['repeat_customers']}
        )""")

    sql = f"""
    INSERT INTO guide.ranking_history (
        guide_id, ranking_score, activity_multiplier,
        repeat_score, aov_score, volume_score, activity_score,
        rating_score, response_score, consistency_score,
        reliability_score, experience_score,
        total_consultations, unique_customers, total_bookings,
        avg_order_value, days_active,
        avg_rating, response_seconds, review_count,
        cancelled_count, months_on_platform, repeat_customers
    ) VALUES {', '.join(values)}
    """
    cur.execute(sql)
    return cur.rowcount


def update_rankings_in_db(rankings):
    """Update ranking_score in PostgreSQL and save history."""
    if not rankings:
        print("No rankings to update")
        return

    conn = psycopg2.connect(**PG_PRIMARY_CONFIG)
    cur = conn.cursor()

    # Save history
    history_count = save_ranking_history(cur, rankings)
    print(f"Saved {history_count} ranking history records")

    # Update guide_profile
    case_parts = [f"WHEN {r['id']} THEN {r['ranking']:.2f}" for r in rankings]
    ids = [str(r['id']) for r in rankings]

    sql = f"""
    UPDATE guide.guide_profile
    SET ranking_score = CASE id {' '.join(case_parts)} END,
        updated_at = NOW()
    WHERE id IN ({', '.join(ids)})
    """

    cur.execute(sql)
    updated = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()

    print(f"Updated ranking_score for {updated} guides in PostgreSQL")


def print_table(rankings):
    """Print rankings as a table."""
    print("=" * 85)
    print(f"{'Rank':<5} {'Guide':<20} {'Score':>6} {'Consults':>9} {'Repeat%':>8} {'Avg OV':>8} {'Active':>8}")
    print("=" * 85)
    for i, r in enumerate(rankings, 1):
        repeat_pct = (r['repeat_score'] or 0) * 100
        aov = f"₹{r['avg_order_value']:.0f}" if r['avg_order_value'] else "₹0"
        activity = f"{r['days_active']}d" if r['days_active'] else "0d"
        print(f"{i:<5} {r['name']:<20} {r['ranking']:>6.2f} {r['total_consultations']:>9} {repeat_pct:>7.0f}% {aov:>8} {activity:>8}")
    print("=" * 85)


if __name__ == '__main__':
    import sys
    from datetime import datetime

    rankings = get_rankings()

    if '--update' in sys.argv:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating rankings in PostgreSQL...")
        update_rankings_in_db(rankings)
        print_table(rankings)
        print(f"\nTotal: {len(rankings)} guides")
    else:
        print_table(rankings)
        print(f"\nTotal: {len(rankings)} guides")
        print("\nRun with --update flag to update rankings in PostgreSQL")
