#!/usr/bin/env python3
"""
Neo4j Incremental Sync Script
Updates Neo4j with latest data from PostgreSQL.
Pure functions, max 20 lines each.
"""

import os
import json
from datetime import datetime, timedelta
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()

# === CONFIG ===

PG_CONFIG = {
    'host': os.getenv('DB_ENDPOINT'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': 'astrokiran',
    'user': os.getenv('DB_USERNAME'),
    'password': os.getenv('DB_PASSWORD')
}

NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')

SYNC_STATE_FILE = '/Users/ankitgupta/astrokiran-analytics/dashboards/.neo4j_sync_state.json'


# === STATE MANAGEMENT ===

def load_sync_state() -> dict:
    """Load last sync timestamp from file."""
    if os.path.exists(SYNC_STATE_FILE):
        with open(SYNC_STATE_FILE, 'r') as f:
            return json.load(f)
    return {'last_sync': None}


def save_sync_state(state: dict):
    """Save sync state to file."""
    with open(SYNC_STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def get_last_sync() -> datetime:
    """Get last sync time or default to 1 hour ago."""
    state = load_sync_state()
    if state.get('last_sync'):
        return datetime.fromisoformat(state['last_sync'])
    return datetime.now() - timedelta(hours=1)


def update_sync_time(sync_time: datetime):
    """Update last sync timestamp."""
    save_sync_state({'last_sync': sync_time.isoformat()})


# === POSTGRES FUNCTIONS ===

def pg_connect():
    """Create PostgreSQL connection."""
    import psycopg2
    from psycopg2.extras import RealDictCursor
    conn = psycopg2.connect(**PG_CONFIG)
    return conn, conn.cursor(cursor_factory=RealDictCursor)


def pg_fetch(cursor, query: str, params: tuple = None) -> list:
    """Execute query and return list of dicts."""
    cursor.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]


def pg_close(conn, cursor):
    """Close PostgreSQL connection."""
    cursor.close()
    conn.close()


# === NEO4J FUNCTIONS ===

def neo4j_connect():
    """Create Neo4j driver."""
    from neo4j import GraphDatabase
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def neo4j_run(driver, query: str, params: dict = None):
    """Run a single Cypher query."""
    with driver.session() as session:
        session.run(query, params or {})


def neo4j_batch(driver, query: str, data: list, batch_size: int = 500):
    """Run batched Cypher query with UNWIND."""
    with driver.session() as session:
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            session.run(query, {'batch': batch})


def neo4j_close(driver):
    """Close Neo4j driver."""
    driver.close()


# === INCREMENTAL QUERIES ===

def q_auth_users(since: datetime) -> str:
    """Query for new/updated auth users."""
    return f"""
    SELECT id, phone_number, is_active, is_test_user, created_at, updated_at
    FROM auth.auth_users
    WHERE deleted_at IS NULL AND (created_at >= %s OR updated_at >= %s)
    """


def q_customers(since: datetime) -> str:
    """Query for new/updated customers."""
    return f"""
    SELECT customer_id, phone_number, country_code, x_auth_id, created_at, updated_at
    FROM customers.customer
    WHERE deleted_at IS NULL AND (created_at >= %s OR updated_at >= %s)
    """


def q_customer_profiles(since: datetime) -> str:
    """Query for new/updated customer profiles."""
    return f"""
    SELECT profile_id, customer_id, name, dob, birth_city, zodiac_sign, gender, created_at, updated_at
    FROM customers.customer_profile
    WHERE deleted_at IS NULL AND (created_at >= %s OR updated_at >= %s)
    """


def q_guides() -> str:
    """Query all guides (small table, always full sync)."""
    return """
    SELECT id, full_name, phone_number, email, x_auth_id, availability_state,
           chat_enabled, voice_enabled, video_enabled, ranking_score, tier,
           referral_code, referrer_code, years_of_experience, created_at
    FROM guide.guide_profile WHERE deleted_at IS NULL
    """


def q_consultations(since: datetime) -> str:
    """Query for new/updated consultations."""
    return f"""
    SELECT id, customer_id, guide_id, mode, state, order_id,
           base_rate_per_minute, call_duration_seconds, is_quick_connect_request,
           promotional, free, created_at, completed_at, updated_at
    FROM consultation.consultation
    WHERE deleted_at IS NULL AND (created_at >= %s OR updated_at >= %s)
    """


def q_feedback(since: datetime) -> str:
    """Query for new/updated feedback."""
    return f"""
    SELECT id, consultation_id, customer_id, rating, feedback, status, created_at, updated_at
    FROM consultation.feedback
    WHERE deleted_at IS NULL AND (created_at >= %s OR updated_at >= %s)
    """


def q_user_wallets(since: datetime) -> str:
    """Query for new/updated user wallets."""
    return f"""
    SELECT user_id, name, phone_number, real_cash, virtual_cash, recharge_count, created_at, updated_at
    FROM wallet.user_wallets
    WHERE deleted_at IS NULL AND (created_at >= %s OR updated_at >= %s)
    """


def q_payments(since: datetime) -> str:
    """Query for new/updated payments."""
    return f"""
    SELECT payment_order_id, user_id, amount, status, payment_method, gateway_id, created_at, updated_at
    FROM wallet.payment_orders
    WHERE created_at >= %s OR updated_at >= %s
    """


def q_wallet_orders(since: datetime) -> str:
    """Query for new/updated wallet orders."""
    return f"""
    SELECT order_id, user_id, consultant_id, service_type, minutes_ordered,
           price_per_minute, final_amount, consultant_share, status, created_at
    FROM wallet.wallet_orders
    WHERE created_at >= %s
    """


def q_transactions(since: datetime) -> str:
    """Query for new transactions."""
    return f"""
    SELECT id, transaction_id, user_id, order_id, type, amount,
           real_cash_delta, virtual_cash_delta, is_promotional, created_at
    FROM wallet.wallet_transactions
    WHERE created_at >= %s
    """


def q_offer_reservations(since: datetime) -> str:
    """Query for new/updated offer reservations."""
    return f"""
    SELECT reservation_id, offer_id, user_id, reservation_status,
           original_amount, bonus_amount, consultation_id, created_at, updated_at
    FROM offers.offer_reservations
    WHERE deleted_at IS NULL AND (created_at >= %s OR updated_at >= %s)
    """


# === SYNC FUNCTIONS ===

def sync_auth_users(cursor, driver, since: datetime) -> int:
    """Sync auth users."""
    data = serialize_data(pg_fetch(cursor, q_auth_users(since), (since, since)))
    if not data:
        return 0
    query = """
    UNWIND $batch AS row
    MERGE (n:AuthUser {id: row.id})
    SET n.phone_number = row.phone_number, n.is_active = row.is_active,
        n.is_test_user = row.is_test_user, n.created_at = row.created_at
    """
    neo4j_batch(driver, query, data)
    return len(data)


def sync_customers(cursor, driver, since: datetime) -> int:
    """Sync customers."""
    data = serialize_data(pg_fetch(cursor, q_customers(since), (since, since)))
    if not data:
        return 0
    query = """
    UNWIND $batch AS row
    MERGE (n:Customer {customer_id: row.customer_id})
    SET n.phone_number = row.phone_number, n.country_code = row.country_code,
        n.x_auth_id = row.x_auth_id, n.created_at = row.created_at
    """
    neo4j_batch(driver, query, data)
    return len(data)


def sync_customer_profiles(cursor, driver, since: datetime) -> int:
    """Sync customer profiles."""
    data = serialize_data(pg_fetch(cursor, q_customer_profiles(since), (since, since)))
    if not data:
        return 0
    query = """
    UNWIND $batch AS row
    MERGE (n:CustomerProfile {profile_id: row.profile_id})
    SET n.customer_id = row.customer_id, n.name = row.name, n.dob = row.dob,
        n.birth_city = row.birth_city, n.zodiac_sign = row.zodiac_sign, n.gender = row.gender
    """
    neo4j_batch(driver, query, data)
    return len(data)


def sync_guides(cursor, driver) -> int:
    """Sync all guides (always full)."""
    data = serialize_data(pg_fetch(cursor, q_guides()))
    query = """
    UNWIND $batch AS row
    MERGE (n:Guide {id: row.id})
    SET n.full_name = row.full_name, n.phone_number = row.phone_number,
        n.x_auth_id = row.x_auth_id, n.availability_state = row.availability_state,
        n.chat_enabled = row.chat_enabled, n.voice_enabled = row.voice_enabled,
        n.video_enabled = row.video_enabled, n.ranking_score = row.ranking_score,
        n.tier = row.tier, n.referral_code = row.referral_code
    """
    neo4j_batch(driver, query, data)
    return len(data)


def sync_consultations(cursor, driver, since: datetime) -> int:
    """Sync consultations."""
    data = serialize_data(pg_fetch(cursor, q_consultations(since), (since, since)))
    if not data:
        return 0
    query = """
    UNWIND $batch AS row
    MERGE (n:Consultation {id: row.id})
    SET n.customer_id = row.customer_id, n.guide_id = row.guide_id,
        n.mode = row.mode, n.state = row.state, n.order_id = row.order_id,
        n.duration_seconds = row.call_duration_seconds,
        n.is_quick_connect = row.is_quick_connect_request,
        n.promotional = row.promotional, n.created_at = row.created_at
    """
    neo4j_batch(driver, query, data)
    return len(data)


def sync_feedback(cursor, driver, since: datetime) -> int:
    """Sync feedback."""
    data = serialize_data(pg_fetch(cursor, q_feedback(since), (since, since)))
    if not data:
        return 0
    query = """
    UNWIND $batch AS row
    MERGE (n:Feedback {id: row.id})
    SET n.consultation_id = row.consultation_id, n.customer_id = row.customer_id,
        n.rating = row.rating, n.feedback = row.feedback, n.status = row.status
    """
    neo4j_batch(driver, query, data)
    return len(data)


def sync_user_wallets(cursor, driver, since: datetime) -> int:
    """Sync user wallets."""
    data = serialize_data(pg_fetch(cursor, q_user_wallets(since), (since, since)))
    if not data:
        return 0
    query = """
    UNWIND $batch AS row
    MERGE (n:CustomerWallet {user_id: row.user_id})
    SET n.name = row.name, n.phone_number = row.phone_number,
        n.real_cash = row.real_cash, n.virtual_cash = row.virtual_cash,
        n.recharge_count = row.recharge_count
    """
    neo4j_batch(driver, query, data)
    return len(data)


def sync_payments(cursor, driver, since: datetime) -> int:
    """Sync payments."""
    data = serialize_data(pg_fetch(cursor, q_payments(since), (since, since)))
    if not data:
        return 0
    query = """
    UNWIND $batch AS row
    MERGE (n:Payment {payment_order_id: row.payment_order_id})
    SET n.user_id = row.user_id, n.amount = row.amount,
        n.status = row.status, n.payment_method = row.payment_method,
        n.created_at = row.created_at
    """
    neo4j_batch(driver, query, data)
    return len(data)


def sync_wallet_orders(cursor, driver, since: datetime) -> int:
    """Sync wallet orders."""
    data = serialize_data(pg_fetch(cursor, q_wallet_orders(since), (since,)))
    if not data:
        return 0
    query = """
    UNWIND $batch AS row
    MERGE (n:WalletOrder {order_id: row.order_id})
    SET n.user_id = row.user_id, n.consultant_id = row.consultant_id,
        n.service_type = row.service_type, n.minutes_ordered = row.minutes_ordered,
        n.final_amount = row.final_amount, n.consultant_share = row.consultant_share,
        n.status = row.status, n.created_at = row.created_at
    """
    neo4j_batch(driver, query, data)
    return len(data)


def sync_transactions(cursor, driver, since: datetime) -> int:
    """Sync transactions."""
    data = serialize_data(pg_fetch(cursor, q_transactions(since), (since,)))
    if not data:
        return 0
    query = """
    UNWIND $batch AS row
    MERGE (n:Transaction {transaction_id: row.transaction_id})
    SET n.user_id = row.user_id, n.order_id = row.order_id,
        n.type = row.type, n.amount = row.amount,
        n.real_cash_delta = row.real_cash_delta, n.virtual_cash_delta = row.virtual_cash_delta,
        n.is_promotional = row.is_promotional
    """
    neo4j_batch(driver, query, data)
    return len(data)


def sync_offer_reservations(cursor, driver, since: datetime) -> int:
    """Sync offer reservations."""
    data = serialize_data(pg_fetch(cursor, q_offer_reservations(since), (since, since)))
    if not data:
        return 0
    query = """
    UNWIND $batch AS row
    MERGE (n:OfferReservation {reservation_id: row.reservation_id})
    SET n.offer_id = row.offer_id, n.user_id = row.user_id,
        n.reservation_status = row.reservation_status,
        n.bonus_amount = row.bonus_amount, n.consultation_id = row.consultation_id
    """
    neo4j_batch(driver, query, data)
    return len(data)


# === RELATIONSHIP SYNC ===

def sync_new_relationships(driver, since: datetime):
    """Create relationships for newly added nodes."""
    queries = [
        # Customer -> Auth
        """
        MATCH (c:Customer) WHERE c.x_auth_id IS NOT NULL
        AND NOT (c)-[:HAS_AUTH]->()
        MATCH (a:AuthUser {id: c.x_auth_id})
        MERGE (c)-[:HAS_AUTH]->(a)
        """,
        # Customer -> Wallet
        """
        MATCH (c:Customer)
        WHERE NOT (c)-[:HAS_WALLET]->()
        MATCH (w:CustomerWallet {user_id: c.customer_id})
        MERGE (c)-[:HAS_WALLET]->(w)
        """,
        # Customer -> Profile
        """
        MATCH (p:CustomerProfile)
        WHERE NOT ()-[:HAS_PROFILE]->(p)
        MATCH (c:Customer {customer_id: p.customer_id})
        MERGE (c)-[:HAS_PROFILE]->(p)
        """,
        # Consultation -> Customer
        """
        MATCH (con:Consultation) WHERE con.customer_id IS NOT NULL
        AND NOT ()-[:BOOKED]->(con)
        MATCH (c:Customer {customer_id: con.customer_id})
        MERGE (c)-[:BOOKED]->(con)
        """,
        # Consultation -> Guide
        """
        MATCH (con:Consultation) WHERE con.guide_id IS NOT NULL
        AND NOT (con)-[:WITH_GUIDE]->()
        MATCH (g:Guide {id: con.guide_id})
        MERGE (con)-[:WITH_GUIDE]->(g)
        """,
        # Consultation -> WalletOrder
        """
        MATCH (con:Consultation) WHERE con.order_id IS NOT NULL AND con.order_id > 0
        AND NOT (con)-[:PAID_VIA]->()
        MATCH (wo:WalletOrder {order_id: con.order_id})
        MERGE (con)-[:PAID_VIA]->(wo)
        """,
        # Feedback -> Consultation
        """
        MATCH (f:Feedback)
        WHERE NOT ()-[:HAS_FEEDBACK]->(f)
        MATCH (c:Consultation {id: f.consultation_id})
        MERGE (c)-[:HAS_FEEDBACK]->(f)
        """,
        # Payment -> Customer
        """
        MATCH (p:Payment) WHERE p.user_id IS NOT NULL
        AND NOT ()-[:MADE_PAYMENT]->(p)
        MATCH (c:Customer {customer_id: p.user_id})
        MERGE (c)-[:MADE_PAYMENT]->(p)
        """,
        # Payment -> Wallet
        """
        MATCH (p:Payment) WHERE p.user_id IS NOT NULL
        AND NOT (p)-[:CREDITED_TO]->()
        MATCH (w:CustomerWallet {user_id: p.user_id})
        MERGE (p)-[:CREDITED_TO]->(w)
        """,
        # WalletOrder -> CustomerWallet
        """
        MATCH (wo:WalletOrder) WHERE wo.user_id IS NOT NULL
        AND NOT (wo)-[:DEBITED_FROM]->()
        MATCH (w:CustomerWallet {user_id: wo.user_id})
        MERGE (wo)-[:DEBITED_FROM]->(w)
        """,
        # WalletOrder -> GuideWallet
        """
        MATCH (wo:WalletOrder) WHERE wo.consultant_id IS NOT NULL
        AND NOT (wo)-[:CREDITED_TO]->()
        MATCH (gw:GuideWallet {consultant_id: wo.consultant_id})
        MERGE (wo)-[:CREDITED_TO]->(gw)
        """,
        # Transaction -> Wallet
        """
        MATCH (t:Transaction) WHERE t.user_id IS NOT NULL
        AND NOT ()-[:HAS_TRANSACTION]->(t)
        MATCH (w:CustomerWallet {user_id: toInteger(t.user_id)})
        MERGE (w)-[:HAS_TRANSACTION]->(t)
        """,
        # Transaction -> WalletOrder
        """
        MATCH (t:Transaction) WHERE t.order_id IS NOT NULL AND t.order_id > 0
        AND NOT (t)-[:FOR_ORDER]->()
        MATCH (wo:WalletOrder {order_id: t.order_id})
        MERGE (t)-[:FOR_ORDER]->(wo)
        """,
        # OfferReservation -> Customer
        """
        MATCH (r:OfferReservation) WHERE r.user_id IS NOT NULL
        AND NOT ()-[:RESERVED]->(r)
        MATCH (c:Customer {customer_id: r.user_id})
        MERGE (c)-[:RESERVED]->(r)
        """,
        # OfferReservation -> Offer
        """
        MATCH (r:OfferReservation) WHERE r.offer_id IS NOT NULL
        AND NOT (r)-[:FOR_OFFER]->()
        MATCH (o:Offer {offer_id: r.offer_id})
        MERGE (r)-[:FOR_OFFER]->(o)
        """
    ]
    for q in queries:
        neo4j_run(driver, q)


# === SERIALIZATION ===

def serialize_row(row: dict) -> dict:
    """Convert row values to Neo4j-compatible types."""
    result = {}
    for k, v in row.items():
        if isinstance(v, datetime):
            result[k] = v.isoformat()
        elif isinstance(v, Decimal):
            result[k] = float(v)
        elif isinstance(v, (bytes, memoryview)):
            result[k] = None
        else:
            result[k] = v
    return result


def serialize_data(data: list) -> list:
    """Serialize all rows in a list."""
    return [serialize_row(row) for row in data]


# === MAIN ===

def log(msg: str):
    """Print log message with timestamp."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def run_sync():
    """Main sync orchestration."""
    since = get_last_sync()
    sync_start = datetime.now()

    log(f"Syncing changes since: {since}")

    log("Connecting to PostgreSQL...")
    pg_conn, pg_cursor = pg_connect()

    log("Connecting to Neo4j...")
    neo4j_driver = neo4j_connect()

    # Sync nodes
    stats = sync_all_nodes(pg_cursor, neo4j_driver, since)

    # Sync relationships
    log("Syncing relationships...")
    sync_new_relationships(neo4j_driver, since)

    # Update sync time
    update_sync_time(sync_start)

    log("Closing connections...")
    pg_close(pg_conn, pg_cursor)
    neo4j_close(neo4j_driver)

    log("=== SYNC COMPLETE ===")
    for name, count in stats.items():
        if count > 0:
            log(f"  {name}: {count} updated")


def sync_all_nodes(cursor, driver, since: datetime) -> dict:
    """Sync all node types and return stats."""
    stats = {}

    log("Syncing AuthUsers...")
    stats['AuthUsers'] = sync_auth_users(cursor, driver, since)

    log("Syncing Customers...")
    stats['Customers'] = sync_customers(cursor, driver, since)

    log("Syncing CustomerProfiles...")
    stats['CustomerProfiles'] = sync_customer_profiles(cursor, driver, since)

    log("Syncing Guides...")
    stats['Guides'] = sync_guides(cursor, driver)

    log("Syncing Consultations...")
    stats['Consultations'] = sync_consultations(cursor, driver, since)

    log("Syncing Feedback...")
    stats['Feedback'] = sync_feedback(cursor, driver, since)

    log("Syncing UserWallets...")
    stats['UserWallets'] = sync_user_wallets(cursor, driver, since)

    log("Syncing Payments...")
    stats['Payments'] = sync_payments(cursor, driver, since)

    log("Syncing WalletOrders...")
    stats['WalletOrders'] = sync_wallet_orders(cursor, driver, since)

    log("Syncing Transactions...")
    stats['Transactions'] = sync_transactions(cursor, driver, since)

    log("Syncing OfferReservations...")
    stats['OfferReservations'] = sync_offer_reservations(cursor, driver, since)

    return stats


if __name__ == '__main__':
    run_sync()
