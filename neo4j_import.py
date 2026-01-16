#!/usr/bin/env python3
"""
Neo4j Import Script - AstroKiran Domain Model
Pure functions, max 20 lines each.
"""

import os
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


# === POSTGRES FUNCTIONS ===

def pg_connect():
    """Create PostgreSQL connection."""
    import psycopg2
    from psycopg2.extras import RealDictCursor
    conn = psycopg2.connect(**PG_CONFIG)
    return conn, conn.cursor(cursor_factory=RealDictCursor)


def pg_fetch(cursor, query: str) -> list:
    """Execute query and return list of dicts."""
    cursor.execute(query)
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


# === CLEANUP ===

def clear_database(driver):
    """Delete all nodes and relationships."""
    neo4j_run(driver, "MATCH (n) DETACH DELETE n")


def create_constraints(driver):
    """Create uniqueness constraints for key nodes."""
    constraints = [
        "CREATE CONSTRAINT IF NOT EXISTS FOR (n:AuthUser) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Customer) REQUIRE n.customer_id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Guide) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Skill) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Language) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Consultation) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Payment) REQUIRE n.payment_order_id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (n:WalletOrder) REQUIRE n.order_id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Offer) REQUIRE n.offer_id IS UNIQUE",
    ]
    for c in constraints:
        neo4j_run(driver, c)


# === DATA QUERIES ===

Q_AUTH_USERS = "SELECT id, phone_number, is_active, is_test_user, created_at FROM auth.auth_users WHERE deleted_at IS NULL"

Q_CUSTOMERS = "SELECT customer_id, phone_number, country_code, x_auth_id, wallet_user_id, created_at, deleted_at FROM customers.customer"

Q_CUSTOMER_PROFILES = "SELECT profile_id, customer_id, name, dob, birth_city, zodiac_sign, gender, created_at FROM customers.customer_profile WHERE deleted_at IS NULL"

Q_GUIDES = """
SELECT id, full_name, phone_number, email, x_auth_id, availability_state,
       chat_enabled, voice_enabled, video_enabled, ranking_score, tier,
       referral_code, referrer_code, years_of_experience, created_at, deleted_at
FROM guide.guide_profile
"""

Q_SKILLS = "SELECT id, name, description FROM guide.skills WHERE deleted_at IS NULL"

Q_LANGUAGES = "SELECT id, name FROM guide.languages WHERE deleted_at IS NULL"

Q_GUIDE_SKILLS = "SELECT guide_id, skill_id FROM guide.guide_skills WHERE deleted_at IS NULL"

Q_GUIDE_LANGUAGES = "SELECT guide_id, language_id FROM guide.guide_languages WHERE deleted_at IS NULL"

Q_CONSULTATIONS = """
SELECT id, customer_id, guide_id, mode, state, order_id,
       base_rate_per_minute, call_duration_seconds, is_quick_connect_request,
       promotional, free, created_at, completed_at, requested_at, accepted_at
FROM consultation.consultation WHERE deleted_at IS NULL
"""

Q_FEEDBACK = """
SELECT id, consultation_id, customer_id, rating, feedback, status, created_at
FROM consultation.feedback WHERE deleted_at IS NULL
"""

Q_USER_WALLETS = """
SELECT user_id, name, phone_number, real_cash, virtual_cash, recharge_count, created_at
FROM wallet.user_wallets WHERE deleted_at IS NULL
"""

Q_CONSULTANT_WALLETS = """
SELECT consultant_id, name, phone_number, revenue_share, accepts_promotional_offers
FROM wallet.consultant_wallets WHERE deleted_at IS NULL
"""

Q_PAYMENTS = """
SELECT payment_order_id, user_id, amount, status, payment_method, gateway_id, created_at
FROM wallet.payment_orders
"""

Q_WALLET_ORDERS = """
SELECT order_id, user_id, consultant_id, service_type, minutes_ordered,
       price_per_minute, final_amount, consultant_share, status, created_at
FROM wallet.wallet_orders
"""

Q_TRANSACTIONS = """
SELECT id, transaction_id, user_id, order_id, type, amount,
       real_cash_delta, virtual_cash_delta, is_promotional, created_at
FROM wallet.wallet_transactions
"""

Q_OFFERS = """
SELECT offer_id, offer_name, offer_type, bonus_percentage, bonus_fixed_amount,
       min_recharge_amount, max_recharge_amount, free_minutes, is_active
FROM offers.offer_definitions WHERE deleted_at IS NULL
"""

Q_OFFER_RESERVATIONS = """
SELECT reservation_id, offer_id, user_id, reservation_status,
       original_amount, bonus_amount, consultation_id, created_at
FROM offers.offer_reservations WHERE deleted_at IS NULL
"""

Q_LEADS = """
SELECT id, phone, name, source, utm_source, utm_medium, utm_campaign, status, created_at
FROM marketing.leads
"""

Q_GUIDE_ACTIVITY = """
SELECT
    (original_data->>'id')::int as guide_id,
    COUNT(DISTINCT DATE(action_tstamp)) as days_active,
    COUNT(*) as state_changes_30d,
    MAX(action_tstamp) as last_activity
FROM audit.logged_actions
WHERE table_name = 'guide_profile'
  AND original_data->>'availability_state' IS DISTINCT FROM new_data->>'availability_state'
  AND action_tstamp >= NOW() - INTERVAL '30 days'
GROUP BY original_data->>'id'
"""


# === NODE IMPORT FUNCTIONS ===

def import_auth_users(driver, data: list):
    """Import AuthUser nodes."""
    query = """
    UNWIND $batch AS row
    MERGE (n:AuthUser {id: row.id})
    SET n.phone_number = row.phone_number,
        n.is_active = row.is_active,
        n.is_test_user = row.is_test_user,
        n.created_at = row.created_at
    """
    neo4j_batch(driver, query, data)


def import_customers(driver, data: list):
    """Import Customer nodes (including deleted)."""
    query = """
    UNWIND $batch AS row
    MERGE (n:Customer {customer_id: row.customer_id})
    SET n.phone_number = row.phone_number,
        n.country_code = row.country_code,
        n.x_auth_id = row.x_auth_id,
        n.created_at = row.created_at,
        n.deleted_at = row.deleted_at,
        n.is_deleted = CASE WHEN row.deleted_at IS NOT NULL THEN true ELSE false END
    """
    neo4j_batch(driver, query, data)


def import_customer_profiles(driver, data: list):
    """Import CustomerProfile nodes."""
    query = """
    UNWIND $batch AS row
    MERGE (n:CustomerProfile {profile_id: row.profile_id})
    SET n.customer_id = row.customer_id, n.name = row.name,
        n.dob = row.dob, n.birth_city = row.birth_city,
        n.zodiac_sign = row.zodiac_sign, n.gender = row.gender
    """
    neo4j_batch(driver, query, data)


def import_guides(driver, data: list):
    """Import Guide nodes (including deleted)."""
    query = """
    UNWIND $batch AS row
    MERGE (n:Guide {id: row.id})
    SET n.full_name = row.full_name, n.phone_number = row.phone_number,
        n.x_auth_id = row.x_auth_id, n.availability_state = row.availability_state,
        n.chat_enabled = row.chat_enabled, n.voice_enabled = row.voice_enabled,
        n.video_enabled = row.video_enabled, n.ranking_score = row.ranking_score,
        n.tier = row.tier, n.referral_code = row.referral_code,
        n.referrer_code = row.referrer_code, n.created_at = row.created_at,
        n.deleted_at = row.deleted_at,
        n.is_deleted = CASE WHEN row.deleted_at IS NOT NULL THEN true ELSE false END
    """
    neo4j_batch(driver, query, data)


def import_skills(driver, data: list):
    """Import Skill nodes."""
    query = """
    UNWIND $batch AS row
    MERGE (n:Skill {id: row.id})
    SET n.name = row.name, n.description = row.description
    """
    neo4j_batch(driver, query, data)


def import_languages(driver, data: list):
    """Import Language nodes."""
    query = """
    UNWIND $batch AS row
    MERGE (n:Language {id: row.id})
    SET n.name = row.name
    """
    neo4j_batch(driver, query, data)


def import_consultations(driver, data: list):
    """Import Consultation nodes."""
    query = """
    UNWIND $batch AS row
    MERGE (n:Consultation {id: row.id})
    SET n.customer_id = row.customer_id, n.guide_id = row.guide_id,
        n.mode = row.mode, n.state = row.state, n.order_id = row.order_id,
        n.duration_seconds = row.call_duration_seconds,
        n.is_quick_connect = row.is_quick_connect_request,
        n.promotional = row.promotional, n.created_at = row.created_at,
        n.requested_at = row.requested_at, n.accepted_at = row.accepted_at
    """
    neo4j_batch(driver, query, data)


def import_feedback(driver, data: list):
    """Import Feedback nodes."""
    query = """
    UNWIND $batch AS row
    MERGE (n:Feedback {id: row.id})
    SET n.consultation_id = row.consultation_id, n.customer_id = row.customer_id,
        n.rating = row.rating, n.feedback = row.feedback, n.status = row.status
    """
    neo4j_batch(driver, query, data)


def import_user_wallets(driver, data: list):
    """Import CustomerWallet nodes."""
    query = """
    UNWIND $batch AS row
    MERGE (n:CustomerWallet {user_id: row.user_id})
    SET n.name = row.name, n.phone_number = row.phone_number,
        n.real_cash = row.real_cash, n.virtual_cash = row.virtual_cash,
        n.recharge_count = row.recharge_count
    """
    neo4j_batch(driver, query, data)


def import_consultant_wallets(driver, data: list):
    """Import GuideWallet nodes."""
    query = """
    UNWIND $batch AS row
    MERGE (n:GuideWallet {consultant_id: row.consultant_id})
    SET n.name = row.name, n.phone_number = row.phone_number,
        n.revenue_share = row.revenue_share
    """
    neo4j_batch(driver, query, data)


def import_payments(driver, data: list):
    """Import Payment nodes."""
    query = """
    UNWIND $batch AS row
    MERGE (n:Payment {payment_order_id: row.payment_order_id})
    SET n.user_id = row.user_id, n.amount = row.amount,
        n.status = row.status, n.payment_method = row.payment_method,
        n.created_at = row.created_at
    """
    neo4j_batch(driver, query, data)


def import_wallet_orders(driver, data: list):
    """Import WalletOrder nodes."""
    query = """
    UNWIND $batch AS row
    MERGE (n:WalletOrder {order_id: row.order_id})
    SET n.user_id = row.user_id, n.consultant_id = row.consultant_id,
        n.service_type = row.service_type, n.minutes_ordered = row.minutes_ordered,
        n.final_amount = row.final_amount, n.consultant_share = row.consultant_share,
        n.status = row.status, n.created_at = row.created_at
    """
    neo4j_batch(driver, query, data)


def import_transactions(driver, data: list):
    """Import Transaction nodes."""
    query = """
    UNWIND $batch AS row
    MERGE (n:Transaction {transaction_id: row.transaction_id})
    SET n.user_id = row.user_id, n.order_id = row.order_id,
        n.type = row.type, n.amount = row.amount,
        n.real_cash_delta = row.real_cash_delta, n.virtual_cash_delta = row.virtual_cash_delta,
        n.is_promotional = row.is_promotional
    """
    neo4j_batch(driver, query, data)


def import_offers(driver, data: list):
    """Import Offer nodes."""
    query = """
    UNWIND $batch AS row
    MERGE (n:Offer {offer_id: row.offer_id})
    SET n.offer_name = row.offer_name, n.offer_type = row.offer_type,
        n.bonus_percentage = row.bonus_percentage, n.free_minutes = row.free_minutes,
        n.is_active = row.is_active
    """
    neo4j_batch(driver, query, data)


def import_offer_reservations(driver, data: list):
    """Import OfferReservation nodes."""
    query = """
    UNWIND $batch AS row
    MERGE (n:OfferReservation {reservation_id: row.reservation_id})
    SET n.offer_id = row.offer_id, n.user_id = row.user_id,
        n.reservation_status = row.reservation_status,
        n.bonus_amount = row.bonus_amount, n.consultation_id = row.consultation_id
    """
    neo4j_batch(driver, query, data)


def import_leads(driver, data: list):
    """Import Lead nodes."""
    query = """
    UNWIND $batch AS row
    MERGE (n:Lead {id: row.id})
    SET n.phone = row.phone, n.name = row.name, n.source = row.source,
        n.utm_source = row.utm_source, n.utm_medium = row.utm_medium,
        n.utm_campaign = row.utm_campaign, n.status = row.status
    """
    neo4j_batch(driver, query, data)


def update_guide_activity(driver, data: list):
    """Update Guide nodes with activity metrics from audit log."""
    query = """
    UNWIND $batch AS row
    MATCH (g:Guide {id: row.guide_id})
    SET g.days_active_30d = row.days_active,
        g.state_changes_30d = row.state_changes_30d,
        g.last_activity = row.last_activity
    """
    neo4j_batch(driver, query, data)


# === RELATIONSHIP IMPORT FUNCTIONS ===

def link_customer_auth(driver):
    """Create Customer -> AuthUser relationships."""
    query = """
    MATCH (c:Customer) WHERE c.x_auth_id IS NOT NULL
    MATCH (a:AuthUser {id: c.x_auth_id})
    MERGE (c)-[:HAS_AUTH]->(a)
    """
    neo4j_run(driver, query)


def link_customer_wallet(driver):
    """Create Customer -> CustomerWallet relationships."""
    query = """
    MATCH (c:Customer)
    MATCH (w:CustomerWallet {user_id: c.customer_id})
    MERGE (c)-[:HAS_WALLET]->(w)
    """
    neo4j_run(driver, query)


def link_customer_profile(driver):
    """Create Customer -> CustomerProfile relationships."""
    query = """
    MATCH (c:Customer)
    MATCH (p:CustomerProfile {customer_id: c.customer_id})
    MERGE (c)-[:HAS_PROFILE]->(p)
    """
    neo4j_run(driver, query)


def link_guide_auth(driver):
    """Create Guide -> AuthUser relationships."""
    query = """
    MATCH (g:Guide) WHERE g.x_auth_id IS NOT NULL
    MATCH (a:AuthUser {id: g.x_auth_id})
    MERGE (g)-[:HAS_AUTH]->(a)
    """
    neo4j_run(driver, query)


def link_guide_wallet(driver):
    """Create Guide -> GuideWallet relationships."""
    query = """
    MATCH (g:Guide)
    MATCH (w:GuideWallet {consultant_id: g.id})
    MERGE (g)-[:HAS_WALLET]->(w)
    """
    neo4j_run(driver, query)


def link_guide_skills(driver, data: list):
    """Create Guide -> Skill relationships."""
    query = """
    UNWIND $batch AS row
    MATCH (g:Guide {id: row.guide_id})
    MATCH (s:Skill {id: row.skill_id})
    MERGE (g)-[:HAS_SKILL]->(s)
    """
    neo4j_batch(driver, query, data)


def link_guide_languages(driver, data: list):
    """Create Guide -> Language relationships."""
    query = """
    UNWIND $batch AS row
    MATCH (g:Guide {id: row.guide_id})
    MATCH (l:Language {id: row.language_id})
    MERGE (g)-[:SPEAKS]->(l)
    """
    neo4j_batch(driver, query, data)


def link_guide_referrals(driver):
    """Create Guide -> Guide (referral) relationships."""
    query = """
    MATCH (g:Guide) WHERE g.referrer_code IS NOT NULL
    MATCH (referrer:Guide {referral_code: g.referrer_code})
    MERGE (g)-[:REFERRED_BY]->(referrer)
    """
    neo4j_run(driver, query)


def link_consultation_customer(driver):
    """Create Customer -> Consultation relationships."""
    query = """
    MATCH (c:Consultation) WHERE c.customer_id IS NOT NULL
    MATCH (cust:Customer {customer_id: c.customer_id})
    MERGE (cust)-[:BOOKED]->(c)
    """
    neo4j_run(driver, query)


def link_consultation_guide(driver):
    """Create Consultation -> Guide relationships."""
    query = """
    MATCH (c:Consultation) WHERE c.guide_id IS NOT NULL
    MATCH (g:Guide {id: c.guide_id})
    MERGE (c)-[:WITH_GUIDE]->(g)
    """
    neo4j_run(driver, query)


def link_consultation_order(driver):
    """Create Consultation -> WalletOrder relationships."""
    query = """
    MATCH (c:Consultation) WHERE c.order_id IS NOT NULL AND c.order_id > 0
    MATCH (wo:WalletOrder {order_id: c.order_id})
    MERGE (c)-[:PAID_VIA]->(wo)
    """
    neo4j_run(driver, query)


def link_consultation_feedback(driver):
    """Create Consultation -> Feedback relationships."""
    query = """
    MATCH (f:Feedback)
    MATCH (c:Consultation {id: f.consultation_id})
    MERGE (c)-[:HAS_FEEDBACK]->(f)
    """
    neo4j_run(driver, query)


def link_payment_wallet(driver):
    """Create Payment -> CustomerWallet relationships."""
    query = """
    MATCH (p:Payment) WHERE p.user_id IS NOT NULL
    MATCH (w:CustomerWallet {user_id: p.user_id})
    MERGE (p)-[:CREDITED_TO]->(w)
    """
    neo4j_run(driver, query)


def link_payment_customer(driver):
    """Create Customer -> Payment relationships."""
    query = """
    MATCH (p:Payment) WHERE p.user_id IS NOT NULL
    MATCH (c:Customer {customer_id: p.user_id})
    MERGE (c)-[:MADE_PAYMENT]->(p)
    """
    neo4j_run(driver, query)


def link_wallet_order_customer(driver):
    """Create WalletOrder -> CustomerWallet relationships."""
    query = """
    MATCH (wo:WalletOrder) WHERE wo.user_id IS NOT NULL
    MATCH (w:CustomerWallet {user_id: wo.user_id})
    MERGE (wo)-[:DEBITED_FROM]->(w)
    """
    neo4j_run(driver, query)


def link_wallet_order_guide(driver):
    """Create WalletOrder -> GuideWallet relationships."""
    query = """
    MATCH (wo:WalletOrder) WHERE wo.consultant_id IS NOT NULL
    MATCH (gw:GuideWallet {consultant_id: wo.consultant_id})
    MERGE (wo)-[:CREDITED_TO]->(gw)
    """
    neo4j_run(driver, query)


def link_transaction_wallet(driver):
    """Create CustomerWallet -> Transaction relationships."""
    query = """
    MATCH (t:Transaction) WHERE t.user_id IS NOT NULL
    MATCH (w:CustomerWallet {user_id: toInteger(t.user_id)})
    MERGE (w)-[:HAS_TRANSACTION]->(t)
    """
    neo4j_run(driver, query)


def link_transaction_order(driver):
    """Create Transaction -> WalletOrder relationships."""
    query = """
    MATCH (t:Transaction) WHERE t.order_id IS NOT NULL AND t.order_id > 0
    MATCH (wo:WalletOrder {order_id: t.order_id})
    MERGE (t)-[:FOR_ORDER]->(wo)
    """
    neo4j_run(driver, query)


def link_offer_reservation(driver):
    """Create OfferReservation -> Offer relationships."""
    query = """
    MATCH (r:OfferReservation) WHERE r.offer_id IS NOT NULL
    MATCH (o:Offer {offer_id: r.offer_id})
    MERGE (r)-[:FOR_OFFER]->(o)
    """
    neo4j_run(driver, query)


def link_reservation_customer(driver):
    """Create Customer -> OfferReservation relationships."""
    query = """
    MATCH (r:OfferReservation) WHERE r.user_id IS NOT NULL
    MATCH (c:Customer {customer_id: r.user_id})
    MERGE (c)-[:RESERVED]->(r)
    """
    neo4j_run(driver, query)


# === SERIALIZATION ===

def serialize_row(row: dict) -> dict:
    """Convert row values to Neo4j-compatible types."""
    from datetime import datetime
    from decimal import Decimal
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
    from datetime import datetime
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def run_import():
    """Main import orchestration."""
    log("Connecting to PostgreSQL...")
    pg_conn, pg_cursor = pg_connect()

    log("Connecting to Neo4j...")
    neo4j_driver = neo4j_connect()

    log("Clearing Neo4j database...")
    clear_database(neo4j_driver)

    log("Creating constraints...")
    create_constraints(neo4j_driver)

    # Import nodes
    import_nodes(pg_cursor, neo4j_driver)

    # Import relationships
    import_relationships(pg_cursor, neo4j_driver)

    log("Closing connections...")
    pg_close(pg_conn, pg_cursor)
    neo4j_close(neo4j_driver)

    log("Done!")


def import_nodes(cursor, driver):
    """Import all nodes."""
    node_imports = [
        ("AuthUsers", Q_AUTH_USERS, import_auth_users),
        ("Customers", Q_CUSTOMERS, import_customers),
        ("CustomerProfiles", Q_CUSTOMER_PROFILES, import_customer_profiles),
        ("Guides", Q_GUIDES, import_guides),
        ("Skills", Q_SKILLS, import_skills),
        ("Languages", Q_LANGUAGES, import_languages),
        ("Consultations", Q_CONSULTATIONS, import_consultations),
        ("Feedback", Q_FEEDBACK, import_feedback),
        ("CustomerWallets", Q_USER_WALLETS, import_user_wallets),
        ("GuideWallets", Q_CONSULTANT_WALLETS, import_consultant_wallets),
        ("Payments", Q_PAYMENTS, import_payments),
        ("WalletOrders", Q_WALLET_ORDERS, import_wallet_orders),
        ("Transactions", Q_TRANSACTIONS, import_transactions),
        ("Offers", Q_OFFERS, import_offers),
        ("OfferReservations", Q_OFFER_RESERVATIONS, import_offer_reservations),
        ("Leads", Q_LEADS, import_leads),
    ]
    for name, query, import_fn in node_imports:
        log(f"Importing {name}...")
        data = serialize_data(pg_fetch(cursor, query))
        import_fn(driver, data)
        log(f"  -> {len(data)} nodes")


def import_relationships(cursor, driver):
    """Import all relationships."""
    log("Creating relationships...")

    # Identity links
    log("  -> Customer-Auth links")
    link_customer_auth(driver)
    log("  -> Customer-Wallet links")
    link_customer_wallet(driver)
    log("  -> Customer-Profile links")
    link_customer_profile(driver)
    log("  -> Guide-Auth links")
    link_guide_auth(driver)
    log("  -> Guide-Wallet links")
    link_guide_wallet(driver)

    # Guide profile
    log("  -> Guide-Skills links")
    skills_data = serialize_data(pg_fetch(cursor, Q_GUIDE_SKILLS))
    link_guide_skills(driver, skills_data)
    log("  -> Guide-Languages links")
    langs_data = serialize_data(pg_fetch(cursor, Q_GUIDE_LANGUAGES))
    link_guide_languages(driver, langs_data)
    log("  -> Guide referrals")
    link_guide_referrals(driver)

    # Consultations
    log("  -> Consultation-Customer links")
    link_consultation_customer(driver)
    log("  -> Consultation-Guide links")
    link_consultation_guide(driver)
    log("  -> Consultation-Order links")
    link_consultation_order(driver)
    log("  -> Consultation-Feedback links")
    link_consultation_feedback(driver)

    # Financial
    log("  -> Payment links")
    link_payment_wallet(driver)
    link_payment_customer(driver)
    log("  -> WalletOrder links")
    link_wallet_order_customer(driver)
    link_wallet_order_guide(driver)
    log("  -> Transaction links")
    link_transaction_wallet(driver)
    link_transaction_order(driver)

    # Offers
    log("  -> Offer reservation links")
    link_offer_reservation(driver)
    link_reservation_customer(driver)

    # Guide activity metrics (from audit log - availability state changes)
    log("  -> Guide activity (from audit log)")
    activity_data = serialize_data(pg_fetch(cursor, Q_GUIDE_ACTIVITY))
    update_guide_activity(driver, activity_data)
    log(f"     Updated {len(activity_data)} guides with activity data")


if __name__ == '__main__':
    run_import()
