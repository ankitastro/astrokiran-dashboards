#!/usr/bin/env python3
"""
Daily offer scheduler.
- Runs at 6 AM IST daily
- Updates validity period for all offers
- Sets valid_from to now, valid_to to 4 AM next day
- Does NOT change is_active status
"""

import os
import psycopg2
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

PG_PRIMARY_CONFIG = {
    'host': os.getenv('DB_PRIMARY_ENDPOINT'),
    'port': int(os.getenv('DB_PRIMARY_PORT', 5432)),
    'database': os.getenv('DB_PRIMARY_NAME', 'astrokiran'),
    'user': os.getenv('DB_PRIMARY_USERNAME'),
    'password': os.getenv('DB_PRIMARY_PASSWORD')
}

IST = ZoneInfo('Asia/Kolkata')


def update_offer_validity():
    """Update validity period for all offers (valid_from to now, valid_to to 4 AM tomorrow)."""
    now = datetime.now(IST)
    tomorrow_4am = (now + timedelta(days=1)).replace(hour=4, minute=0, second=0, microsecond=0)

    conn = psycopg2.connect(**PG_PRIMARY_CONFIG)
    cur = conn.cursor()

    # Update validity period for all non-deleted offers (don't change is_active)
    cur.execute("""
        UPDATE offers.offer_definitions
        SET valid_from = %s,
            valid_to = %s,
            updated_at = NOW()
        WHERE deleted_at IS NULL
    """, (now, tomorrow_4am))

    updated = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()

    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')} IST] Updated validity for {updated} offers")
    print(f"  Valid from: {now.strftime('%Y-%m-%d %H:%M:%S')} IST")
    print(f"  Valid to:   {tomorrow_4am.strftime('%Y-%m-%d %H:%M:%S')} IST")

    return updated


if __name__ == '__main__':
    update_offer_validity()
