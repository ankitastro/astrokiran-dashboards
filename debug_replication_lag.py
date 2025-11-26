#!/usr/bin/env python3
"""
Debug high PostgreSQL replication lag on AWS RDS
"""

import os
import psycopg2
import boto3
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Database configurations
DB_CONFIG = {
    'host': os.getenv('DB_ENDPOINT'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': 'astrokiran',
    'user': os.getenv('DB_USERNAME'),
    'password': os.getenv('DB_PASSWORD')
}

# AWS configurations
AWS_REGION = os.getenv('AWS_REGION', 'ap-south-1')
RDS_INSTANCE_ID = os.getenv('RDS_INSTANCE_ID')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

def check_rds_metrics():
    """Check RDS CloudWatch metrics for insights"""
    print("=" * 80)
    print("1. CHECKING RDS CLOUDWATCH METRICS")
    print("=" * 80)

    cloudwatch = boto3.client(
        'cloudwatch',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=1)

    metrics_to_check = [
        ('ReplicaLag', 'Seconds'),
        ('CPUUtilization', 'Percent'),
        ('ReadLatency', 'Seconds'),
        ('WriteLatency', 'Seconds'),
        ('NetworkReceiveThroughput', 'Bytes/Second'),
        ('NetworkTransmitThroughput', 'Bytes/Second'),
        ('ReadIOPS', 'Count/Second'),
        ('WriteIOPS', 'Count/Second'),
    ]

    for metric_name, unit in metrics_to_check:
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/RDS',
            MetricName=metric_name,
            Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': RDS_INSTANCE_ID}],
            StartTime=start_time,
            EndTime=end_time,
            Period=300,  # 5 minutes
            Statistics=['Average', 'Maximum', 'Minimum']
        )

        if response['Datapoints']:
            datapoints = sorted(response['Datapoints'], key=lambda x: x['Timestamp'])
            latest = datapoints[-1]
            avg = sum(dp['Average'] for dp in datapoints) / len(datapoints)
            max_val = max(dp['Maximum'] for dp in datapoints)

            print(f"\n{metric_name}:")
            print(f"  Latest: {latest['Average']:.2f} {unit}")
            print(f"  Avg (1h): {avg:.2f} {unit}")
            print(f"  Max (1h): {max_val:.2f} {unit}")

            # Highlight issues
            if metric_name == 'ReplicaLag' and latest['Average'] > 10:
                print(f"  ⚠️  HIGH REPLICATION LAG DETECTED!")
            if metric_name == 'CPUUtilization' and latest['Average'] > 80:
                print(f"  ⚠️  HIGH CPU USAGE!")
            if metric_name in ['ReadLatency', 'WriteLatency'] and latest['Average'] > 0.01:
                print(f"  ⚠️  HIGH DISK LATENCY!")
        else:
            print(f"\n{metric_name}: No data available")

def check_replication_status():
    """Check PostgreSQL replication status"""
    print("\n" + "=" * 80)
    print("2. CHECKING POSTGRESQL REPLICATION STATUS")
    print("=" * 80)

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Check if this is a replica
    cursor.execute("SELECT pg_is_in_recovery();")
    is_replica = cursor.fetchone()[0]
    print(f"\nIs Read Replica: {is_replica}")

    if is_replica:
        # Replication lag from replica's perspective
        cursor.execute("""
            SELECT
                CASE
                    WHEN pg_last_wal_receive_lsn() = pg_last_wal_replay_lsn()
                    THEN 0
                    ELSE EXTRACT(EPOCH FROM now() - pg_last_xact_replay_timestamp())
                END as lag_seconds,
                pg_last_wal_receive_lsn() as receive_lsn,
                pg_last_wal_replay_lsn() as replay_lsn,
                pg_last_xact_replay_timestamp() as last_replay_time,
                now() as current_time;
        """)
        result = cursor.fetchone()

        print(f"\nReplication Lag: {result[0]:.2f} seconds" if result[0] else "Replication Lag: Up to date")
        print(f"Receive LSN: {result[1]}")
        print(f"Replay LSN: {result[2]}")
        print(f"Last Replay Time: {result[3]}")
        print(f"Current Time: {result[4]}")

        if result[0] and result[0] > 60:
            print(f"\n⚠️  CRITICAL: Replication lag is {result[0]:.0f} seconds behind!")

    cursor.close()
    conn.close()

def check_database_load():
    """Check current database activity and load"""
    print("\n" + "=" * 80)
    print("3. CHECKING DATABASE LOAD AND ACTIVITY")
    print("=" * 80)

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Active connections and queries
    cursor.execute("""
        SELECT
            state,
            COUNT(*) as count
        FROM pg_stat_activity
        WHERE datname = 'astrokiran'
        GROUP BY state
        ORDER BY count DESC;
    """)

    print("\nConnection States:")
    for row in cursor.fetchall():
        print(f"  {row[0] or 'NULL'}: {row[1]} connections")

    # Long-running queries
    cursor.execute("""
        SELECT
            pid,
            usename,
            state,
            EXTRACT(EPOCH FROM (now() - query_start)) as duration_seconds,
            LEFT(query, 100) as query_preview
        FROM pg_stat_activity
        WHERE datname = 'astrokiran'
          AND state != 'idle'
          AND query_start IS NOT NULL
          AND EXTRACT(EPOCH FROM (now() - query_start)) > 10
        ORDER BY duration_seconds DESC
        LIMIT 10;
    """)

    long_queries = cursor.fetchall()
    if long_queries:
        print("\nLong-Running Queries (>10s):")
        for row in long_queries:
            print(f"\n  PID: {row[0]}")
            print(f"  User: {row[1]}")
            print(f"  State: {row[2]}")
            print(f"  Duration: {row[3]:.1f}s")
            print(f"  Query: {row[4]}...")
    else:
        print("\n✓ No long-running queries detected")

    # Table bloat and vacuum stats
    cursor.execute("""
        SELECT
            schemaname,
            relname as tablename,
            last_vacuum,
            last_autovacuum,
            last_analyze,
            last_autoanalyze,
            n_dead_tup,
            n_live_tup
        FROM pg_stat_user_tables
        WHERE n_dead_tup > 10000
        ORDER BY n_dead_tup DESC
        LIMIT 5;
    """)

    bloated_tables = cursor.fetchall()
    if bloated_tables:
        print("\nTables with High Dead Tuples (may need VACUUM):")
        for row in bloated_tables:
            print(f"\n  Table: {row[0]}.{row[1]}")
            print(f"  Last Vacuum: {row[2]}")
            print(f"  Last Autovacuum: {row[3]}")
            print(f"  Dead Tuples: {row[6]:,}")
            print(f"  Live Tuples: {row[7]:,}")
    else:
        print("\n✓ No tables with excessive dead tuples")

    cursor.close()
    conn.close()

def check_write_activity():
    """Check write activity that could cause lag"""
    print("\n" + "=" * 80)
    print("4. CHECKING WRITE ACTIVITY (Potential Lag Causes)")
    print("=" * 80)

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Tables with most writes
    cursor.execute("""
        SELECT
            schemaname,
            relname as tablename,
            n_tup_ins as inserts,
            n_tup_upd as updates,
            n_tup_del as deletes,
            n_tup_ins + n_tup_upd + n_tup_del as total_writes
        FROM pg_stat_user_tables
        ORDER BY total_writes DESC
        LIMIT 10;
    """)

    print("\nTop 10 Tables by Write Activity (since stats reset):")
    for row in cursor.fetchall():
        print(f"\n  {row[0]}.{row[1]}:")
        print(f"    Inserts: {row[2]:,}")
        print(f"    Updates: {row[3]:,}")
        print(f"    Deletes: {row[4]:,}")
        print(f"    Total: {row[5]:,}")

    # Check for locks that might be blocking replication
    cursor.execute("""
        SELECT
            locktype,
            mode,
            COUNT(*) as count
        FROM pg_locks
        WHERE granted = true
        GROUP BY locktype, mode
        ORDER BY count DESC;
    """)

    print("\nCurrent Locks:")
    for row in cursor.fetchall():
        print(f"  {row[0]} - {row[1]}: {row[2]} locks")

    cursor.close()
    conn.close()

def check_recommendations():
    """Provide recommendations based on findings"""
    print("\n" + "=" * 80)
    print("5. RECOMMENDATIONS TO REDUCE REPLICATION LAG")
    print("=" * 80)

    print("""
Common causes and solutions for high replication lag:

1. HIGH WRITE VOLUME on Primary
   - Solution: Scale up primary instance
   - Solution: Optimize write queries (batch inserts, reduce updates)
   - Solution: Add connection pooling (PgBouncer)

2. REPLICA UNDER-PROVISIONED
   - Solution: Scale up replica instance to match or exceed primary
   - Solution: Ensure replica has same storage type (GP3, IO1)

3. NETWORK LATENCY between Primary and Replica
   - Solution: Ensure both instances are in same region/AZ
   - Solution: Check for network throughput limits

4. LONG-RUNNING TRANSACTIONS on Primary
   - Solution: Identify and optimize long transactions
   - Solution: Set statement_timeout for queries

5. DISK I/O BOTTLENECK on Replica
   - Solution: Upgrade to faster storage (GP3 with higher IOPS)
   - Solution: Increase provisioned IOPS

6. VACUUM LAG on Primary
   - Solution: Tune autovacuum settings
   - Solution: Run manual VACUUM ANALYZE on busy tables

7. REPLICATION SLOT ISSUES
   - Solution: Check pg_replication_slots for lag
   - Solution: Ensure slots are being consumed

Next Steps:
- Review CloudWatch metrics above for bottlenecks
- Check RDS Performance Insights for query performance
- Consider upgrading replica instance class if CPU/Memory constrained
- Review pg_stat_replication on primary database
""")

def main():
    print("\n" + "=" * 80)
    print("AWS RDS POSTGRESQL REPLICATION LAG DEBUGGING")
    print("=" * 80)
    print(f"Instance: {RDS_INSTANCE_ID}")
    print(f"Database: {DB_CONFIG['database']}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        check_rds_metrics()
        check_replication_status()
        check_database_load()
        check_write_activity()
        check_recommendations()

        print("\n" + "=" * 80)
        print("DEBUGGING COMPLETE")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error during debugging: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
