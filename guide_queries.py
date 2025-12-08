"""
SQL queries for the Guides Dashboard
All queries for fetching guide data from the astrokiran database
"""


def get_guide_counts_query():
    """Get online/offline/total guide counts"""
    return """
        SELECT
            COUNT(*) FILTER (WHERE availability_state = 'ONLINE_AVAILABLE') as online_guides,
            COUNT(*) FILTER (WHERE availability_state = 'OFFLINE') as offline_guides,
            COUNT(*) as total_guides
        FROM guide.guide_profile
        WHERE deleted_at IS NULL
    """


def get_channel_counts_query():
    """Get counts of guides available on each channel (chat/voice/video)"""
    return """
        SELECT
            COUNT(*) FILTER (WHERE chat_enabled = true) as online_chat_guides,
            COUNT(*) FILTER (WHERE voice_enabled = true) as online_voice_guides,
            COUNT(*) FILTER (WHERE video_enabled = true) as online_video_guides
        FROM guide.guide_profile
        WHERE availability_state = 'ONLINE_AVAILABLE'
          AND deleted_at IS NULL
    """


def get_skills_breakdown_query():
    """Get skill-wise online/offline guide counts"""
    return """
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
        ORDER BY online_count DESC, s.name
    """


def get_online_guides_query():
    """Get online guides with skills, earnings, pricing, today's orders (IST), and session status"""
    return """
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
                cw.price_per_minute
            FROM guide.guide_profile gp
            LEFT JOIN wallet.consultant_wallets cw
                ON REPLACE(REPLACE(gp.phone_number, '+91', ''), '+', '') = cw.phone_number
                AND cw.deleted_at IS NULL
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
                AND DATE(wo.created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') = CURRENT_DATE
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
        ORDER BY COALESCE(got.today_earnings, 0) DESC
    """


def get_offline_guides_query():
    """Get offline guides with skills, earnings, pricing, today's orders (IST), and session status"""
    return """
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
                cw.price_per_minute
            FROM guide.guide_profile gp
            LEFT JOIN wallet.consultant_wallets cw
                ON REPLACE(REPLACE(gp.phone_number, '+91', ''), '+', '') = cw.phone_number
                AND cw.deleted_at IS NULL
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
                AND DATE(wo.created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') = CURRENT_DATE
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
        ORDER BY COALESCE(got.today_earnings, 0) DESC
    """


def get_latest_feedback_query():
    """Get the latest feedback given by customers to each guide"""
    return """
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
        ORDER BY c.guide_id, f.created_at DESC
    """


def get_promo_grant_spending_query():
    """Get promotional grant spending by guide since Nov 13, 2025"""
    return """
        SELECT
            wo.consultant_id,
            gp.full_name as guide_name,
            COUNT(*) as grants_spent_on_this_guide
        FROM wallet.wallet_transactions wt_grant
        JOIN wallet.wallet_transactions wt_spent
            ON wt_grant.transaction_id = wt_spent.source_grant_txn_id
        JOIN wallet.wallet_orders wo
            ON wt_spent.order_id = wo.order_id
        LEFT JOIN guide.guide_profile gp
            ON wo.consultant_id = gp.id
        WHERE wt_grant.type = 'PROMOTION_GRANT'
          AND wt_grant.created_at >= '2025-11-13 00:00:00'
          AND wt_spent.type = 'SPENT'
        GROUP BY wo.consultant_id, gp.full_name
        ORDER BY grants_spent_on_this_guide DESC
    """


def get_test_guides_query():
    """Get test guides (Aman Jain and Praveen) with skills, earnings, pricing, today's orders (IST), and session status"""
    return """
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
                cw.price_per_minute
            FROM guide.guide_profile gp
            LEFT JOIN wallet.consultant_wallets cw
                ON REPLACE(REPLACE(gp.phone_number, '+91', ''), '+', '') = cw.phone_number
                AND cw.deleted_at IS NULL
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
                AND DATE(wo.created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') = CURRENT_DATE
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
        ORDER BY COALESCE(got.today_earnings, 0) DESC
    """
