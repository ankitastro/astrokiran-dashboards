#!/bin/bash
cd /home/ubuntu/astrokiran-dashboards
source .venv/bin/activate

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting sync..."
python neo4j_sync.py

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Updating rankings..."
python get_rankings.py --update

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Done!"
