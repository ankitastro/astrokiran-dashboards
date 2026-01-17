#!/usr/bin/env python3
"""
Get guide rankings from Neo4j and generate SQL update statement.
9-factor algorithm: Repeat=35%, AOV=15%, Volume=15%, Activity=15%, Rating=5%, Response=5%, Consistency=5%, Reliability=3%, Experience=2%
Activity multiplier penalty: <5d=0.5x, 5-10d=0.75x, 10-15d=0.9x, 15+d=1.0x
"""

import os
import psycopg2
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

# PostgreSQL config for updating rankings
PG_PRIMARY_CONFIG = {
    'host': os.getenv('DB_PRIMARY_ENDPOINT'),
    'port': int(os.getenv('DB_PRIMARY_PORT', 5432)),
    'database': os.getenv('DB_PRIMARY_NAME', 'astrokiran'),
    'user': os.getenv('DB_PRIMARY_USERNAME'),
    'password': os.getenv('DB_PRIMARY_PASSWORD')
}

NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')

TEST_GUIDES = ["Aman Jain", "Praveen"]

RANKING_QUERY = '''
MATCH (g:Guide)
WHERE g.is_deleted = false AND NOT g.full_name IN $test_guides

OPTIONAL MATCH (c:Consultation)-[:WITH_GUIDE]->(g)
WHERE c.state = "completed"
OPTIONAL MATCH (c)-[:HAS_FEEDBACK]->(f:Feedback)
OPTIONAL MATCH (c)-[:PAID_VIA]->(wo:WalletOrder)

OPTIONAL MATCH (cust:Customer)-[:BOOKED]->(c2:Consultation)-[:WITH_GUIDE]->(g)
WHERE c2.state = "completed"

WITH g,
     COUNT(DISTINCT c) as completed,
     AVG(CASE WHEN f.rating IS NOT NULL THEN f.rating END) as avg_rating,
     COUNT(DISTINCT f) as review_count,
     COUNT(DISTINCT cust.customer_id) as unique_customers,
     COUNT(DISTINCT c2) as total_bookings,
     AVG(wo.final_amount) as avg_order_value,
     COLLECT(wo.final_amount) as order_values

OPTIONAL MATCH (resp_con:Consultation)-[:WITH_GUIDE]->(g)
WHERE resp_con.state = "completed"
  AND resp_con.requested_at IS NOT NULL
  AND resp_con.accepted_at IS NOT NULL

WITH g, completed, avg_rating, review_count, unique_customers, total_bookings, avg_order_value, order_values,
     AVG(
       CASE
         WHEN resp_con.requested_at IS NOT NULL AND resp_con.accepted_at IS NOT NULL
         THEN duration.inSeconds(datetime(resp_con.requested_at), datetime(resp_con.accepted_at)).seconds
         ELSE NULL
       END
     ) as avg_response_seconds

OPTIONAL MATCH (all_con:Consultation)-[:WITH_GUIDE]->(g)
WHERE all_con.state IN ["completed", "cancelled", "guide_rejected"]

WITH g, completed, avg_rating, review_count, unique_customers, total_bookings, avg_order_value, order_values, avg_response_seconds,
     COUNT(all_con) as total_cons,
     SUM(CASE WHEN all_con.state IN ["cancelled", "guide_rejected"] THEN 1 ELSE 0 END) as cancelled

// Calculate median from order_values using subquery
CALL {
    WITH order_values
    UNWIND [x IN order_values WHERE x IS NOT NULL AND x > 0] as ov
    WITH ov ORDER BY ov
    WITH collect(ov) as sorted_values
    RETURN CASE WHEN size(sorted_values) > 0
                THEN sorted_values[size(sorted_values)/2]
                ELSE 0
           END as median_ov
}
WITH g, completed, avg_rating, review_count, unique_customers, total_bookings, avg_order_value, avg_response_seconds, total_cons, cancelled, median_ov as median_order_value

WITH g, completed, median_order_value,
     CASE WHEN review_count > 0
          THEN ((review_count * COALESCE(avg_rating, 0) + 5 * 4.0) / (review_count + 5))
          ELSE 4.0
     END as bayesian_rating,

     CASE WHEN completed > 0
          THEN CASE WHEN log10(toFloat(completed)) / log10(200.0) > 1 THEN 1.0
                    ELSE log10(toFloat(completed)) / log10(200.0)
               END
          ELSE 0
     END as volume_score,

     CASE WHEN completed > 0
          THEN toFloat(review_count) / completed
          ELSE 0
     END as consistency_score,

     CASE WHEN unique_customers > 0 AND total_bookings > unique_customers
          THEN toFloat(total_bookings - unique_customers) / total_bookings
          ELSE 0
     END as repeat_rate,

     CASE WHEN avg_order_value IS NOT NULL AND avg_order_value > 0
          THEN CASE WHEN avg_order_value >= 50 THEN 1.0
                    ELSE avg_order_value / 50.0
               END
          ELSE 0
     END as aov_score,

     CASE WHEN avg_response_seconds IS NOT NULL AND avg_response_seconds <= 300
          THEN CASE WHEN avg_response_seconds <= 30 THEN 1.0
                    ELSE 1.0 - ((avg_response_seconds - 30) / 270.0)
               END
          ELSE 0.5
     END as response_score,

     CASE WHEN total_cons > 0
          THEN 1.0 - (toFloat(cancelled) / total_cons)
          ELSE 1.0
     END as reliability_score,

     g.created_at as created_at,
     COALESCE(g.days_active_30d, 0) as days_active,
     unique_customers,
     total_bookings,
     avg_order_value

WITH g, completed, median_order_value, bayesian_rating, volume_score, consistency_score, repeat_rate, aov_score,
     response_score, reliability_score, days_active, unique_customers, total_bookings, avg_order_value,

     CASE WHEN created_at IS NOT NULL
          THEN CASE WHEN duration.between(datetime(created_at), datetime()).months > 24
                    THEN 1.0
                    ELSE toFloat(duration.between(datetime(created_at), datetime()).months) / 24.0
               END
          ELSE 0.5
     END as experience_score,

     CASE WHEN days_active >= 20 THEN 1.0
          WHEN days_active = 0 THEN 0.0
          ELSE toFloat(days_active) / 20.0
     END as activity_score

WITH g, completed, median_order_value, days_active,
     bayesian_rating, volume_score, consistency_score, repeat_rate, aov_score,
     response_score, reliability_score, experience_score, activity_score,
     (bayesian_rating - 1.0) / 4.0 as rating_normalized,
     unique_customers, total_bookings, avg_order_value

WITH g, completed, median_order_value, days_active,
     rating_normalized, volume_score, consistency_score, repeat_rate, aov_score,
     response_score, reliability_score, experience_score, activity_score,
     unique_customers, total_bookings, avg_order_value,

     (repeat_rate * 0.35) +
     (aov_score * 0.15) +
     (volume_score * 0.15) +
     (activity_score * 0.15) +
     (rating_normalized * 0.05) +
     (response_score * 0.05) +
     (consistency_score * 0.05) +
     (reliability_score * 0.03) +
     (experience_score * 0.02) as weighted_score,

     // Activity multiplier penalty
     CASE WHEN days_active < 5 THEN 0.5
          WHEN days_active < 10 THEN 0.75
          WHEN days_active < 15 THEN 0.9
          ELSE 1.0
     END as activity_multiplier

WITH g, completed, median_order_value, weighted_score, activity_multiplier, repeat_rate, avg_order_value,
     round(weighted_score * activity_multiplier * 10 * 100) / 100 as ranking

RETURN g.id as id,
       g.full_name as name,
       ranking,
       completed as total_consultations,
       round(repeat_rate * 100) as repeat_pct,
       round(avg_order_value) as aov,
       round(median_order_value) as median_ov,
       g.days_active_30d as activity
ORDER BY ranking DESC
'''


def get_rankings():
    """Fetch rankings from Neo4j."""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    with driver.session() as session:
        result = session.run(RANKING_QUERY, test_guides=TEST_GUIDES)
        rankings = [dict(r) for r in result]

    driver.close()
    return rankings


def print_table(rankings):
    """Print rankings as a table."""
    print("=" * 115)
    print(f"{'Rank':<5} {'Guide':<20} {'Score':>6} {'Consults':>9} {'Repeat%':>8} {'Avg OV':>8} {'Med OV':>8} {'Active':>8}")
    print("=" * 115)
    for i, r in enumerate(rankings, 1):
        consults = r['total_consultations'] or 0
        aov = f"₹{r['aov']:.0f}" if r['aov'] else "₹0"
        median = f"₹{r['median_ov']:.0f}" if r['median_ov'] else "₹0"
        activity = f"{r['activity']}d" if r['activity'] else "0d"
        print(f"{i:<5} {r['name']:<20} {r['ranking']:>6.2f} {consults:>9} {r['repeat_pct'] or 0:>7}% {aov:>8} {median:>8} {activity:>8}")
    print("=" * 115)


def print_sql(rankings):
    """Print SQL update statement."""
    print("\n-- SQL Update Statement")
    print("-- 9-factor algorithm: Repeat=35%, AOV=15%, Volume=15%, Activity=15%, Rating=5%, Response=5%, Consistency=5%, Reliability=3%, Experience=2%")
    print("-- Activity multiplier penalty: <5d=0.5x, 5-10d=0.75x, 10-15d=0.9x, 15+d=1.0x")
    print("")
    print("UPDATE guide.guide_profile SET ranking_score = CASE id")

    for r in rankings:
        print(f"    WHEN {r['id']} THEN {r['ranking']:.2f}  -- {r['name']}")

    ids = [str(r['id']) for r in rankings]
    print("END")
    print(f"WHERE id IN ({', '.join(ids)});")


def update_rankings_in_db(rankings):
    """Update ranking_score in PostgreSQL database."""
    if not rankings:
        print("No rankings to update")
        return

    conn = psycopg2.connect(**PG_PRIMARY_CONFIG)
    cur = conn.cursor()

    # Build the CASE statement
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


if __name__ == '__main__':
    import sys
    from datetime import datetime

    rankings = get_rankings()

    if '--update' in sys.argv:
        # Update rankings in PostgreSQL
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating rankings in PostgreSQL...")
        update_rankings_in_db(rankings)
        print_table(rankings)
        print(f"\nTotal: {len(rankings)} guides")
    elif '--sql' in sys.argv:
        print_sql(rankings)
    else:
        print_table(rankings)
        print(f"\nTotal: {len(rankings)} guides")
        print("\nRun with --sql flag to generate SQL update statement")
        print("Run with --update flag to update rankings in PostgreSQL")
