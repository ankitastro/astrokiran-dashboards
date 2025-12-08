"""
Data Fetching Functions for AstroKiran Dashboard
"""

import psycopg2
from utils import DB_CONFIG, get_rds_cloudwatch_metrics
from queries import (
    DAILY_RECHARGE_QUERY,
    KPI_QUERY,
    DB_CONNECTIONS_QUERY,
    REPLICATION_STATUS_QUERY,
    ALL_USERS_COUNT_QUERY,
    ALL_USERS_COMPLETE_QUERY,
)


def fetch_all_dashboard_data(current_page: int, items_per_page: int) -> dict:
    """
    Fetch all dashboard data from database in a single call.
    Returns a dict with all the data needed to update the display.
    """
    result = {
        'db_stats': (0, 0, 0, 0, 0.0),
        'kpi_data': (0, 0, 0, 0),
        'daily_recharge_data': [],
        'total_users': 0,
        'all_users_data': [],
        'replication_status': (False, 0, 0),
        'rds_metrics': None,
        'error': None,
    }

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 1. DB Connection and Load Stats
        cursor.execute(DB_CONNECTIONS_QUERY)
        result['db_stats'] = cursor.fetchone()

        # 2. KPIs
        cursor.execute(KPI_QUERY)
        result['kpi_data'] = cursor.fetchone()

        # 3. Daily Recharge Counts (last 7 days)
        cursor.execute(DAILY_RECHARGE_QUERY)
        result['daily_recharge_data'] = cursor.fetchall()

        # 4. Get total count of users for pagination
        cursor.execute(ALL_USERS_COUNT_QUERY)
        result['total_users'] = cursor.fetchone()[0]

        # 5. All Users with Complete Data (paginated)
        offset = (current_page - 1) * items_per_page
        cursor.execute(ALL_USERS_COMPLETE_QUERY, (items_per_page, offset))
        result['all_users_data'] = cursor.fetchall()

        # 6. Replication Status
        cursor.execute(REPLICATION_STATUS_QUERY)
        result['replication_status'] = cursor.fetchone()

        cursor.close()
        conn.close()

        # 7. Fetch RDS CloudWatch Metrics (if configured)
        result['rds_metrics'] = get_rds_cloudwatch_metrics()

    except Exception as e:
        result['error'] = str(e)

    return result
