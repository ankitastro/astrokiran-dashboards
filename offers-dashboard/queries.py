"""
SQL Queries for Offers Dashboard.
All queries organized by view/domain.
"""

# =============================================================================
# OFFERS VIEW QUERIES
# =============================================================================

ACTIVE_OFFERS_QUERY = """
SELECT
    offer_name,
    offer_type,
    offer_category,
    bonus_percentage,
    free_minutes,
    min_recharge_amount,
    max_recharge_amount,
    target_user_types,
    trigger_type,
    valid_to
FROM offers.offer_definitions
WHERE deleted_at IS NULL
  AND is_active = true
  AND valid_to > NOW()
ORDER BY offer_type, offer_name
"""

OFFER_STATS_QUERY = """
SELECT
    od.offer_type,
    COUNT(DISTINCT od.offer_id) as offer_count,
    COUNT(oc.consumption_id) as total_consumptions,
    COALESCE(SUM(oc.bonus_amount), 0) as total_bonus_given
FROM offers.offer_definitions od
LEFT JOIN offers.offer_consumptions oc ON od.offer_id = oc.offer_id
    AND oc.deleted_at IS NULL
    AND oc.consumption_status = 'COMPLETED'
WHERE od.deleted_at IS NULL AND od.is_active = true
GROUP BY od.offer_type
ORDER BY total_consumptions DESC
"""

RECENT_CONSUMPTIONS_QUERY = """
SELECT
    oc.user_id,
    od.offer_name,
    od.offer_type,
    oc.original_amount,
    oc.bonus_amount,
    oc.consumption_status,
    oc.consumed_at
FROM offers.offer_consumptions oc
JOIN offers.offer_definitions od ON oc.offer_id = od.offer_id
WHERE oc.deleted_at IS NULL
ORDER BY oc.consumed_at DESC
LIMIT 50
"""

DAILY_CONSUMPTION_QUERY = """
SELECT
    DATE(consumed_at) as date,
    TO_CHAR(consumed_at, 'Dy') as day_label,
    COUNT(*) as consumption_count,
    COALESCE(SUM(bonus_amount), 0) as total_bonus
FROM offers.offer_consumptions
WHERE deleted_at IS NULL
  AND consumption_status = 'COMPLETED'
  AND consumed_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(consumed_at), TO_CHAR(consumed_at, 'Dy')
ORDER BY date DESC
"""

FIRST_TIME_VS_REGULAR_QUERY = """
SELECT
    CASE
        WHEN 'FIRST_TIME' = ANY(od.target_user_types) AND NOT 'REGULAR' = ANY(od.target_user_types) THEN 'FIRST_TIME'
        WHEN 'REGULAR' = ANY(od.target_user_types) AND NOT 'FIRST_TIME' = ANY(od.target_user_types) THEN 'REGULAR'
        ELSE 'BOTH'
    END as user_type,
    COUNT(DISTINCT oc.consumption_id) as consumptions,
    COALESCE(SUM(oc.bonus_amount), 0) as total_bonus
FROM offers.offer_definitions od
LEFT JOIN offers.offer_consumptions oc ON od.offer_id = oc.offer_id
    AND oc.deleted_at IS NULL
    AND oc.consumption_status = 'COMPLETED'
WHERE od.deleted_at IS NULL
GROUP BY 1
ORDER BY consumptions DESC
"""


# =============================================================================
# RESERVATIONS VIEW QUERIES
# =============================================================================

ACTIVE_RESERVATIONS_QUERY = """
SELECT
    r.user_id,
    od.offer_name,
    od.offer_type,
    r.reservation_status,
    r.original_amount,
    r.bonus_amount,
    r.voucher_minutes,
    r.voucher_free_cash,
    r.expires_at,
    r.created_at
FROM offers.offer_reservations r
JOIN offers.offer_definitions od ON r.offer_id = od.offer_id
WHERE r.deleted_at IS NULL
  AND r.reservation_status = 'ACTIVE'
ORDER BY r.expires_at ASC
LIMIT 100
"""

RESERVATION_STATS_QUERY = """
SELECT
    reservation_status,
    COUNT(*) as count,
    COALESCE(SUM(bonus_amount), 0) as total_bonus,
    COALESCE(SUM(voucher_minutes), 0) as total_minutes
FROM offers.offer_reservations
WHERE deleted_at IS NULL
GROUP BY reservation_status
ORDER BY count DESC
"""

EXPIRING_SOON_QUERY = """
SELECT
    r.user_id,
    od.offer_name,
    r.voucher_minutes,
    r.voucher_free_cash,
    r.expires_at,
    EXTRACT(EPOCH FROM (r.expires_at - NOW())) / 3600 as hours_left
FROM offers.offer_reservations r
JOIN offers.offer_definitions od ON r.offer_id = od.offer_id
WHERE r.deleted_at IS NULL
  AND r.reservation_status = 'ACTIVE'
  AND r.expires_at BETWEEN NOW() AND NOW() + INTERVAL '24 hours'
ORDER BY r.expires_at ASC
LIMIT 50
"""

RECENT_REDEMPTIONS_QUERY = """
SELECT
    r.user_id,
    od.offer_name,
    r.voucher_minutes,
    r.bonus_amount,
    r.consumed_at
FROM offers.offer_reservations r
JOIN offers.offer_definitions od ON r.offer_id = od.offer_id
WHERE r.deleted_at IS NULL
  AND r.reservation_status = 'REDEEMED'
ORDER BY r.consumed_at DESC
LIMIT 50
"""


# =============================================================================
# RATES VIEW QUERIES
# =============================================================================

CONSULTANT_RATES_QUERY = """
SELECT
    cr.consultant_id,
    cr.service_type,
    cr.base_rate,
    cr.is_active,
    cr.valid_from,
    cr.valid_to,
    gp.tier
FROM offers.consultant_rates cr
JOIN guide.guide_profile gp ON cr.consultant_id = gp.id
WHERE cr.deleted_at IS NULL
ORDER BY cr.consultant_id, cr.service_type
LIMIT 100
"""

ALL_CONSULTANT_RATES_QUERY = """
SELECT
    cr.rate_id,
    cr.consultant_id,
    cr.service_type,
    cr.base_rate,
    cr.is_active,
    cr.valid_from,
    cr.valid_to
FROM offers.consultant_rates cr
WHERE cr.deleted_at IS NULL
ORDER BY cr.consultant_id, cr.service_type
"""

CONSULTANT_RATES_PIVOT_QUERY = """
SELECT
    gp.id as consultant_id,
    gp.full_name,
    MAX(CASE WHEN cr.service_type = 'CHAT' THEN cr.rate_id::text END) as chat_rate_id,
    MAX(CASE WHEN cr.service_type = 'CHAT' THEN cr.base_rate END) as chat_rate,
    MAX(CASE WHEN cr.service_type = 'VOICE' THEN cr.rate_id::text END) as voice_rate_id,
    MAX(CASE WHEN cr.service_type = 'VOICE' THEN cr.base_rate END) as voice_rate,
    MAX(CASE WHEN cr.service_type = 'VIDEO' THEN cr.rate_id::text END) as video_rate_id,
    MAX(CASE WHEN cr.service_type = 'VIDEO' THEN cr.base_rate END) as video_rate,
    BOOL_AND(cr.is_active) as is_active,
    gp.tier
FROM guide.guide_profile gp
JOIN offers.consultant_rates cr ON gp.id = cr.consultant_id AND cr.deleted_at IS NULL
WHERE gp.deleted_at IS NULL
GROUP BY gp.id, gp.full_name, gp.tier
ORDER BY gp.id
"""

RATES_BY_SERVICE_QUERY = """
SELECT
    service_type,
    COUNT(*) as consultant_count,
    MIN(base_rate) as min_rate,
    MAX(base_rate) as max_rate,
    AVG(base_rate) as avg_rate
FROM offers.consultant_rates
WHERE deleted_at IS NULL AND is_active = true
GROUP BY service_type
ORDER BY service_type
"""

DISCOUNT_OFFERS_QUERY = """
SELECT
    offer_name,
    bonus_percentage,
    target_user_types,
    valid_from,
    valid_to,
    is_active
FROM offers.offer_definitions
WHERE deleted_at IS NULL
  AND offer_type = 'CONSULTANT_PRICING'
ORDER BY is_active DESC, bonus_percentage DESC
"""

TOP_RATED_CONSULTANTS_QUERY = """
SELECT
    consultant_id,
    COUNT(*) as rate_count,
    MAX(base_rate) as highest_rate,
    MIN(base_rate) as lowest_rate
FROM offers.consultant_rates
WHERE deleted_at IS NULL AND is_active = true
GROUP BY consultant_id
ORDER BY highest_rate DESC
LIMIT 20
"""


# =============================================================================
# USERS VIEW QUERIES
# =============================================================================

USER_SEGMENTS_QUERY = """
SELECT
    user_segment,
    COUNT(*) as user_count,
    COALESCE(SUM(total_spent), 0) as total_spent,
    COALESCE(SUM(total_offers_used), 0) as total_offers,
    COALESCE(AVG(total_consultations), 0) as avg_consults
FROM offers.user_behavior_metrics
WHERE deleted_at IS NULL
GROUP BY user_segment
ORDER BY user_count DESC
"""

FIRST_TIME_USERS_QUERY = """
SELECT
    user_id,
    registration_source,
    is_first_time_user,
    total_spent,
    total_offers_used,
    created_at
FROM offers.user_behavior_metrics
WHERE deleted_at IS NULL
  AND is_first_time_user = true
ORDER BY created_at DESC
LIMIT 50
"""

TOP_SPENDERS_QUERY = """
SELECT
    user_id,
    user_segment,
    total_spent,
    total_consultations,
    total_offers_used,
    last_activity_at
FROM offers.user_behavior_metrics
WHERE deleted_at IS NULL
ORDER BY total_spent DESC
LIMIT 30
"""

RECENT_ACTIVITY_QUERY = """
SELECT
    user_id,
    user_segment,
    preferred_service_type,
    total_consultations,
    last_consultation_at,
    last_offer_used_at
FROM offers.user_behavior_metrics
WHERE deleted_at IS NULL
  AND last_activity_at >= NOW() - INTERVAL '7 days'
ORDER BY last_activity_at DESC
LIMIT 50
"""

REGISTRATION_SOURCES_QUERY = """
SELECT
    registration_source,
    COUNT(*) as user_count,
    SUM(CASE WHEN is_first_time_user THEN 1 ELSE 0 END) as first_time,
    COALESCE(SUM(total_spent), 0) as total_spent
FROM offers.user_behavior_metrics
WHERE deleted_at IS NULL
GROUP BY registration_source
ORDER BY user_count DESC
"""


# =============================================================================
# FIRST-TIME USERS VIEW QUERIES
# =============================================================================

FIRST_TIME_OFFERS_QUERY = """
SELECT
    offer_id,
    offer_name,
    offer_type,
    offer_category,
    bonus_percentage,
    bonus_fixed_amount,
    free_minutes,
    min_recharge_amount,
    max_recharge_amount,
    max_cashback_amount,
    voucher_subtype,
    trigger_type,
    valid_from,
    valid_to,
    is_active,
    description,
    service_type,
    usage_limit_per_user,
    cta_text,
    target_guide_tiers
FROM offers.offer_definitions
WHERE deleted_at IS NULL
  AND 'FIRST_TIME' = ANY(target_user_types)
ORDER BY
    is_active DESC,
    min_recharge_amount ASC
"""

REGULAR_OFFERS_QUERY = """
SELECT
    offer_id,
    offer_name,
    offer_type,
    offer_category,
    bonus_percentage,
    bonus_fixed_amount,
    free_minutes,
    min_recharge_amount,
    max_recharge_amount,
    max_cashback_amount,
    voucher_subtype,
    trigger_type,
    valid_from,
    valid_to,
    is_active,
    description,
    service_type,
    usage_limit_per_user,
    cta_text,
    target_guide_tiers
FROM offers.offer_definitions
WHERE deleted_at IS NULL
  AND 'REGULAR' = ANY(target_user_types)
ORDER BY
    is_active DESC,
    min_recharge_amount ASC
"""

FIRST_TIME_OFFER_PERFORMANCE_QUERY = """
SELECT
    od.offer_name,
    od.offer_type,
    COUNT(DISTINCT oc.user_id) as unique_users,
    COUNT(oc.consumption_id) as total_consumptions,
    COALESCE(SUM(oc.bonus_amount), 0) as total_bonus_given,
    COALESCE(SUM(oc.original_amount), 0) as total_recharge_amount
FROM offers.offer_definitions od
LEFT JOIN offers.offer_consumptions oc ON od.offer_id = oc.offer_id
    AND oc.deleted_at IS NULL
    AND oc.consumption_status = 'COMPLETED'
WHERE od.deleted_at IS NULL
  AND 'FIRST_TIME' = ANY(od.target_user_types)
GROUP BY od.offer_id, od.offer_name, od.offer_type
ORDER BY total_consumptions DESC
"""

FIRST_TIME_USERS_COUNT_QUERY = """
SELECT
    COUNT(*) FILTER (WHERE is_first_time_user = true) as first_time_count,
    COUNT(*) FILTER (WHERE is_first_time_user = false) as converted_count,
    COUNT(*) as total_users
FROM offers.user_behavior_metrics
WHERE deleted_at IS NULL
"""

FIRST_TIME_RECENT_CONVERSIONS_QUERY = """
SELECT
    oc.user_id,
    od.offer_name,
    od.offer_type,
    oc.original_amount,
    oc.bonus_amount,
    oc.voucher_minutes,
    oc.consumed_at
FROM offers.offer_consumptions oc
JOIN offers.offer_definitions od ON oc.offer_id = od.offer_id
WHERE oc.deleted_at IS NULL
  AND oc.consumption_status = 'COMPLETED'
  AND 'FIRST_TIME' = ANY(od.target_user_types)
ORDER BY oc.consumed_at DESC
LIMIT 50
"""

FIRST_TIME_DAILY_CONVERSIONS_QUERY = """
SELECT
    DATE(oc.consumed_at) as date,
    TO_CHAR(oc.consumed_at, 'Dy') as day_label,
    COUNT(DISTINCT oc.user_id) as unique_users,
    COUNT(*) as conversions,
    COALESCE(SUM(oc.original_amount), 0) as total_recharge,
    COALESCE(SUM(oc.bonus_amount), 0) as total_bonus
FROM offers.offer_consumptions oc
JOIN offers.offer_definitions od ON oc.offer_id = od.offer_id
WHERE oc.deleted_at IS NULL
  AND oc.consumption_status = 'COMPLETED'
  AND 'FIRST_TIME' = ANY(od.target_user_types)
  AND oc.consumed_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(oc.consumed_at), TO_CHAR(oc.consumed_at, 'Dy')
ORDER BY date DESC
"""

FIRST_TIME_OFFER_BY_RANGE_QUERY = """
SELECT
    offer_name,
    min_recharge_amount,
    max_recharge_amount,
    bonus_percentage,
    free_minutes
FROM offers.offer_definitions
WHERE deleted_at IS NULL
  AND is_active = true
  AND valid_to > NOW()
  AND 'FIRST_TIME' = ANY(target_user_types)
ORDER BY min_recharge_amount ASC
"""
