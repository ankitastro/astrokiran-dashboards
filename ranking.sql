-- Guide Ranking Algorithm - Pure PostgreSQL
-- 9-factor algorithm: Repeat=35%, AOV=15%, Volume=15%, Activity=15%, Rating=5%, Response=5%, Consistency=5%, Reliability=3%, Experience=2%
-- Activity multiplier penalty: <5d=0.5x, 5-10d=0.75x, 10-15d=0.9x, 15+d=1.0x

WITH guide_activity AS (
    -- Days active in last 30 days (from audit log)
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
    -- Consultation metrics per guide
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
    -- Rating metrics per guide
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
    -- Order value metrics per guide
    SELECT
        wo.consultant_id as guide_id,
        AVG(wo.final_amount) as avg_order_value,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY wo.final_amount) as median_order_value,
        COUNT(*) as total_orders
    FROM wallet.wallet_orders wo
    JOIN consultation.consultation c ON c.order_id = wo.order_id AND c.state = 'completed'
    WHERE wo.final_amount > 0
    GROUP BY wo.consultant_id
),
repeat_stats AS (
    -- Repeat customer rate
    SELECT
        c.guide_id,
        COUNT(*) as total_bookings,
        COUNT(*) - COUNT(DISTINCT c.customer_id) as repeat_bookings
    FROM consultation.consultation c
    WHERE c.state = 'completed' AND c.deleted_at IS NULL
    GROUP BY c.guide_id
),
guide_scores AS (
    SELECT
        g.id,
        g.full_name,
        g.created_at,
        COALESCE(ga.days_active, 0) as days_active,
        COALESCE(cs.completed, 0) as total_consultations,
        COALESCE(cs.unique_customers, 0) as unique_customers,
        COALESCE(rs.total_bookings, 0) as total_bookings,
        COALESCE(os.avg_order_value, 0) as avg_order_value,

        -- Repeat score (35%)
        CASE WHEN rs.total_bookings > 0 AND rs.total_bookings > cs.unique_customers
             THEN rs.repeat_bookings::float / rs.total_bookings
             ELSE 0
        END as repeat_score,

        -- AOV score (15%) - maxes at Rs.50
        CASE WHEN os.avg_order_value >= 50 THEN 1.0
             WHEN os.avg_order_value > 0 THEN os.avg_order_value / 50.0
             ELSE 0
        END as aov_score,

        -- Volume score (15%) - log scale, max at 200 consultations
        CASE WHEN cs.completed > 0
             THEN LEAST(LOG(cs.completed::float) / LOG(200.0), 1.0)
             ELSE 0
        END as volume_score,

        -- Activity score (15%) - max at 20 days
        CASE WHEN ga.days_active >= 20 THEN 1.0
             WHEN ga.days_active > 0 THEN ga.days_active / 20.0
             ELSE 0
        END as activity_score,

        -- Rating score (5%) - Bayesian with prior of 4.0 and 5 pseudo-reviews
        CASE WHEN fs.review_count > 0
             THEN ((fs.review_count * COALESCE(fs.avg_rating, 0) + 5 * 4.0) / (fs.review_count + 5) - 1.0) / 4.0
             ELSE (4.0 - 1.0) / 4.0  -- default 4.0 rating normalized
        END as rating_score,

        -- Response score (5%) - max at 30 seconds, 0.5 for > 300s or null
        CASE WHEN cs.avg_response_seconds IS NULL THEN 0.5
             WHEN cs.avg_response_seconds <= 30 THEN 1.0
             WHEN cs.avg_response_seconds <= 300 THEN 1.0 - ((cs.avg_response_seconds - 30) / 270.0)
             ELSE 0.5
        END as response_score,

        -- Consistency score (5%) - review rate
        CASE WHEN cs.completed > 0
             THEN COALESCE(fs.review_count, 0)::float / cs.completed
             ELSE 0
        END as consistency_score,

        -- Reliability score (3%) - 1 - cancellation rate
        CASE WHEN cs.total_cons > 0
             THEN 1.0 - (cs.cancelled::float / cs.total_cons)
             ELSE 1.0
        END as reliability_score,

        -- Experience score (2%) - tenure, max at 24 months
        CASE WHEN g.created_at IS NOT NULL
             THEN LEAST(EXTRACT(EPOCH FROM (NOW() - g.created_at)) / (24 * 30 * 24 * 3600), 1.0)
             ELSE 0.5
        END as experience_score,

        -- Activity multiplier penalty
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
      AND g.full_name NOT IN ('Aman Jain', 'Praveen')  -- test guides
)
SELECT
    id,
    full_name as name,
    ROUND(((
        (repeat_score * 0.35) +
        (aov_score * 0.15) +
        (volume_score * 0.15) +
        (activity_score * 0.15) +
        (rating_score * 0.05) +
        (response_score * 0.05) +
        (consistency_score * 0.05) +
        (reliability_score * 0.03) +
        (experience_score * 0.02)
    ) * activity_multiplier * 10)::numeric, 2) as ranking_score,
    activity_multiplier,
    ROUND(repeat_score::numeric, 3) as repeat_score,
    ROUND(aov_score::numeric, 3) as aov_score,
    ROUND(volume_score::numeric, 3) as volume_score,
    ROUND(activity_score::numeric, 3) as activity_score,
    ROUND(rating_score::numeric, 3) as rating_score,
    ROUND(response_score::numeric, 3) as response_score,
    ROUND(consistency_score::numeric, 3) as consistency_score,
    ROUND(reliability_score::numeric, 3) as reliability_score,
    ROUND(experience_score::numeric, 3) as experience_score,
    total_consultations,
    unique_customers,
    total_bookings,
    ROUND(avg_order_value::numeric, 2) as avg_order_value,
    days_active
FROM guide_scores
ORDER BY ranking_score DESC;
