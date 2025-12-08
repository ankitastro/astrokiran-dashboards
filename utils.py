"""
Utility Functions for AstroKiran Dashboard
"""

import os
import csv
import re
import psycopg2
import boto3
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

from queries import CAC_QUERY

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_ENDPOINT'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': 'astrokiran',
    'user': os.getenv('DB_USERNAME'),
    'password': os.getenv('DB_PASSWORD')
}

# AWS Configuration for RDS CloudWatch metrics
AWS_CONFIG = {
    'region': os.getenv('AWS_REGION', 'ap-south-1'),
    'rds_instance_id': os.getenv('RDS_INSTANCE_ID', ''),
}

# AWS credentials (optional - will use IAM role if not provided)
if os.getenv('AWS_ACCESS_KEY_ID'):
    AWS_CONFIG['aws_access_key_id'] = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_CONFIG['aws_secret_access_key'] = os.getenv('AWS_SECRET_ACCESS_KEY')


def parse_meta_ads_csv(file_path: str):
    """
    Parse a Meta Ads CSV export file.
    Returns: (list of ad set data, summary metrics dict)
    """
    data = []
    date_start = None
    date_end = None

    def clean_num(val):
        if not val:
            return 0
        return float(re.sub(r'[^0-9.-]+', '', str(val))) or 0

    def parse_date(val):
        if not val:
            return None
        try:
            return datetime.strptime(val.strip(), '%Y-%m-%d').date()
        except:
            return None

    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []

        # Find column names (Meta CSV headers vary)
        name_key = next((k for k in headers if 'ad set name' in k.lower()), None)
        spend_key = next((k for k in headers if 'amount spent' in k.lower()), None)
        results_key = next((k for k in headers if k == 'Results' or 'mobile app install' in k.lower()), None)
        impressions_key = next((k for k in headers if 'impressions' in k.lower()), None)
        clicks_key = next((k for k in headers if 'link clicks' in k.lower()), None)
        reach_key = next((k for k in headers if k.lower() == 'reach'), None)
        frequency_key = next((k for k in headers if k.lower() == 'frequency'), None)
        start_date_key = next((k for k in headers if 'reporting starts' in k.lower()), None)
        end_date_key = next((k for k in headers if 'reporting ends' in k.lower()), None)

        for row in reader:
            # Extract date range from first row with dates
            if date_start is None and start_date_key:
                date_start = parse_date(row.get(start_date_key, ''))
            if date_end is None and end_date_key:
                date_end = parse_date(row.get(end_date_key, ''))

            if not name_key or not row.get(name_key):
                continue

            name = row.get(name_key, '')
            if not name or name == 'nan':
                continue

            spend = clean_num(row.get(spend_key, 0))
            if spend <= 0:
                continue

            installs = clean_num(row.get(results_key, 0))
            impressions = clean_num(row.get(impressions_key, 0))
            clicks = clean_num(row.get(clicks_key, 0))
            reach = clean_num(row.get(reach_key, 0)) if reach_key else 0
            frequency = clean_num(row.get(frequency_key, 0)) if frequency_key else 0

            cpi = spend / installs if installs > 0 else 0
            ctr = (clicks / impressions * 100) if impressions > 0 else 0

            data.append({
                'name': name,
                'spend': spend,
                'installs': int(installs),
                'impressions': int(impressions),
                'clicks': int(clicks),
                'reach': int(reach),
                'frequency': frequency,
                'cpi': cpi,
                'ctr': ctr,
            })

    # Sort by spend descending
    data.sort(key=lambda x: x['spend'], reverse=True)

    # Calculate summary metrics
    total_spend = sum(d['spend'] for d in data)
    total_installs = sum(d['installs'] for d in data)
    total_impressions = sum(d['impressions'] for d in data)
    total_clicks = sum(d['clicks'] for d in data)
    total_reach = sum(d['reach'] for d in data)

    # Calculate weighted average frequency (impressions / reach)
    avg_frequency = total_impressions / total_reach if total_reach > 0 else 0

    summary = {
        'total_spend': total_spend,
        'total_installs': total_installs,
        'total_impressions': total_impressions,
        'total_clicks': total_clicks,
        'total_reach': total_reach,
        'avg_frequency': avg_frequency,
        'avg_cpi': total_spend / total_installs if total_installs > 0 else 0,
        'avg_ctr': (total_clicks / total_impressions * 100) if total_impressions > 0 else 0,
        'ad_sets': len(data),
        'date_start': date_start,
        'date_end': date_end,
    }

    return data, summary


def fetch_cac_data(date_start, date_end):
    """
    Fetch CAC data from database for the given date range.
    Returns: dict with new_customers, total_recharge, cac
    """
    if not date_start or not date_end:
        return None

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(CAC_QUERY, (date_start, date_end))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            new_customers, total_recharge = result
            return {
                'new_customers': new_customers or 0,
                'total_recharge': float(total_recharge or 0),
                'date_start': date_start,
                'date_end': date_end,
            }
    except Exception as e:
        print(f"CAC query error: {e}")

    return None


def scan_for_csv_files():
    """Scan common folders for CSV files."""
    folders_to_scan = [
        Path.home() / "Downloads",
        Path.home() / "Desktop",
        Path.home() / "Documents",
        Path.cwd(),
    ]

    csv_files = []
    for folder in folders_to_scan:
        if folder.exists():
            for csv_file in folder.glob("*.csv"):
                # Get file stats
                stat = csv_file.stat()
                csv_files.append({
                    'path': csv_file,
                    'name': csv_file.name,
                    'folder': folder.name,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime),
                })

    # Sort by modified date (newest first)
    csv_files.sort(key=lambda x: x['modified'], reverse=True)
    return csv_files[:20]  # Return top 20 most recent


def get_rds_cloudwatch_metrics():
    """
    Fetch RDS CloudWatch metrics for the last 10 minutes.
    Returns: dict with CPU, memory, IOPS, latency, replica lag, and replication metrics
    """
    if not AWS_CONFIG.get('rds_instance_id'):
        return None

    try:
        # Create CloudWatch client
        session_kwargs = {'region_name': AWS_CONFIG['region']}
        if AWS_CONFIG.get('aws_access_key_id'):
            session_kwargs['aws_access_key_id'] = AWS_CONFIG['aws_access_key_id']
            session_kwargs['aws_secret_access_key'] = AWS_CONFIG['aws_secret_access_key']

        cloudwatch = boto3.client('cloudwatch', **session_kwargs)

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=10)  # CloudWatch data may have 5-minute delay

        # Metrics to fetch
        metrics_to_fetch = [
            ('CPUUtilization', 'Percent'),
            ('FreeableMemory', 'Bytes'),
            ('ReadIOPS', 'Count/Second'),
            ('WriteIOPS', 'Count/Second'),
            ('ReadLatency', 'Seconds'),
            ('WriteLatency', 'Seconds'),
            ('ReplicaLag', 'Seconds'),  # Replication lag for read replicas
        ]

        results = {}

        for metric_name, unit in metrics_to_fetch:
            response = cloudwatch.get_metric_statistics(
                Namespace='AWS/RDS',
                MetricName=metric_name,
                Dimensions=[
                    {'Name': 'DBInstanceIdentifier', 'Value': AWS_CONFIG['rds_instance_id']}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,  # 5 minutes
                Statistics=['Average']
            )

            if response['Datapoints']:
                # Get the most recent datapoint
                datapoint = sorted(response['Datapoints'], key=lambda x: x['Timestamp'], reverse=True)[0]
                results[metric_name] = datapoint['Average']
            else:
                results[metric_name] = 0

        return results

    except Exception as e:
        return None
