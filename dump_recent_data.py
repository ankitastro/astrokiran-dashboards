#!/usr/bin/env python3
"""
Dump last 7 days of data from all relevant tables.
Outputs JSON files for analysis.
"""

import os
import json
from datetime import datetime, timedelta
from decimal import Decimal
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_ENDPOINT'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': 'astrokiran',
    'user': os.getenv('DB_USERNAME'),
    'password': os.getenv('DB_PASSWORD')
}

OUTPUT_DIR = '/Users/ankitgupta/astrokiran-analytics/dashboards/data_dump'

# Tables to dump with their date column (if any)
TABLES = {
    # Auth schema
    'auth.auth_users': 'created_at',
    'auth.auth_user_roles': 'created_at',
    'auth.user_sessions': 'created_at',
    'auth.user_devices': 'created_at',
    'auth.login_activities': 'timestamp',
    'auth.otp_attempts': 'created_at',
    'auth.casbin_rules': None,  # No date column, dump all

    # Customers schema
    'customers.customer': 'created_at',
    'customers.customer_profile': 'created_at',
    'customers.address': 'created_at',
    'customers.customer_address': 'created_at',

    # Guide schema
    'guide.guide_profile': None,  # Dump all guides
    'guide.skills': None,  # Reference data
    'guide.languages': None,  # Reference data
    'guide.guide_skills': 'created_at',
    'guide.guide_languages': 'created_at',
    'guide.bank_account': 'created_at',
    'guide.kyc_document': 'created_at',
    'guide.agreement': 'created_at',
    'guide.verification': 'created_at',
    'guide.addresses': 'created_at',
    'guide.media': 'created_at',
    'guide.saved_messages': 'created_at',

    # Consultation schema
    'consultation.consultation': 'created_at',
    'consultation.feedback': 'created_at',
    'consultation.feedback_comments_by_guide': 'created_at',
    'consultation.agora_consultation_session': 'created_at',
    'consultation.agora_webhook_events': 'created_at',
    'consultation.consultation_quality_metrics': 'created_at',

    # Wallet schema
    'wallet.user_wallets': 'created_at',
    'wallet.consultant_wallets': 'created_at',
    'wallet.consultants': 'created_at',
    'wallet.users': 'created_at',
    'wallet.payment_orders': 'created_at',
    'wallet.payment_transactions': 'created_at',
    'wallet.payment_gateways': None,  # Reference data
    'wallet.wallet_orders': 'created_at',
    'wallet.wallet_transactions': 'created_at',
    'wallet.consultant_payouts': 'created_at',
    'wallet.invoices': 'created_at',
    'wallet.invoice_line_items': None,  # Join with invoices
    'wallet.coupons': 'created_at',
    'wallet.promotion_rules': None,  # Reference data
    'wallet.quick_connect_rates': 'created_at',
    'wallet.refund_audit': 'created_at',
    'wallet.tenants': None,  # Reference data
    'wallet.wallet_settings': 'created_at',
    'wallet.wallets': 'created_at',

    # Offers schema
    'offers.offer_definitions': 'created_at',
    'offers.offer_reservations': 'created_at',
    'offers.offer_consumptions': 'created_at',
    'offers.offer_campaigns': 'created_at',
    'offers.consultant_rates': 'created_at',
    'offers.user_behavior_metrics': 'created_at',
    'offers.user_segments': 'created_at',
    'offers.user_milestone_progress': 'created_at',
    'offers.volume_bonus_tracking': 'created_at',

    # Marketing schema
    'marketing.leads': 'created_at',
    'marketing.messages': 'created_at',

    # Notifications schema
    'notifications.notifications': 'created_at',
    'notifications.client_events': 'created_at',
    'notifications.delivery_attempts': 'created_at',
    'notifications.escalation_rules': 'created_at',
}


def json_serializer(obj):
    """Handle non-serializable types."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, bytes):
        return '<binary>'
    if isinstance(obj, memoryview):
        return '<binary>'
    return str(obj)


def dump_table(cursor, table, date_col, since_date):
    """Dump a single table."""
    if date_col:
        query = f"""
            SELECT * FROM {table}
            WHERE {date_col} >= %s
            ORDER BY {date_col} DESC
        """
        cursor.execute(query, (since_date,))
    else:
        query = f"SELECT * FROM {table}"
        cursor.execute(query)

    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def main():
    since_date = datetime.now() - timedelta(days=7)
    print(f"Dumping data since: {since_date}")

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    summary = {}

    for table, date_col in TABLES.items():
        try:
            print(f"Dumping {table}...", end=" ")
            data = dump_table(cursor, table, date_col, since_date)

            # Save to JSON
            filename = table.replace('.', '_') + '.json'
            filepath = os.path.join(OUTPUT_DIR, filename)

            with open(filepath, 'w') as f:
                json.dump(data, f, default=json_serializer, indent=2)

            summary[table] = len(data)
            print(f"{len(data)} rows")

        except Exception as e:
            print(f"ERROR: {e}")
            summary[table] = f"ERROR: {e}"

    cursor.close()
    conn.close()

    # Save summary
    summary_path = os.path.join(OUTPUT_DIR, '_summary.json')
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print("\n=== SUMMARY ===")
    for table, count in summary.items():
        print(f"{table}: {count}")


if __name__ == '__main__':
    main()
