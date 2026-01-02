# Superset API Guide

This document describes how to create dashboards, datasets, and charts in Apache Superset via the REST API.

## Authentication

Superset uses JWT tokens with CSRF protection.

### Step 1: Login to get access token

```bash
curl -s -c /tmp/superset_cookies.txt -X POST "https://asksuset.astrokiran.com/api/v1/security/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "askadmin", "password": "AskAdmin123", "provider": "db"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Step 2: Get CSRF token (required for POST/PUT/DELETE)

```bash
TOKEN="<access_token_from_step_1>"
curl -s -c /tmp/superset_cookies.txt -b /tmp/superset_cookies.txt \
  "https://asksuset.astrokiran.com/api/v1/security/csrf_token/" \
  -H "Authorization: Bearer $TOKEN"
```

Response:
```json
{
  "result": "ImJmYWVjYmU4MzljOTJkY2Y..."
}
```

**Important:** You must include both:
- The session cookie (`-b /tmp/superset_cookies.txt`)
- The X-CSRFToken header

### Token Expiry

Access tokens expire after ~15 minutes. Re-authenticate if you get:
```json
{"msg": "Bad Authorization header. Expected 'Authorization: Bearer <JWT>'"}
```

## API Endpoints

| Resource | List | Get | Create | Update | Delete |
|----------|------|-----|--------|--------|--------|
| Dashboard | GET /api/v1/dashboard/ | GET /api/v1/dashboard/{id} | POST /api/v1/dashboard/ | PUT /api/v1/dashboard/{id} | DELETE /api/v1/dashboard/{id} |
| Chart | GET /api/v1/chart/ | GET /api/v1/chart/{id} | POST /api/v1/chart/ | PUT /api/v1/chart/{id} | DELETE /api/v1/chart/{id} |
| Dataset | GET /api/v1/dataset/ | GET /api/v1/dataset/{id} | POST /api/v1/dataset/ | PUT /api/v1/dataset/{id} | DELETE /api/v1/dataset/{id} |
| Database | GET /api/v1/database/ | GET /api/v1/database/{id} | POST /api/v1/database/ | PUT /api/v1/database/{id} | DELETE /api/v1/database/{id} |

## Creating a Dataset (Virtual/SQL)

Datasets can be physical tables or virtual (SQL queries).

```bash
curl -s -b /tmp/superset_cookies.txt -X POST "https://asksuset.astrokiran.com/api/v1/dataset/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF" \
  -H "Referer: https://asksuset.astrokiran.com/" \
  -d @- << 'ENDJSON'
{
  "database": 2,
  "schema": "",
  "table_name": "my_dataset_name",
  "sql": "SELECT column1, column2 FROM schema.table WHERE condition",
  "owners": [3]
}
ENDJSON
```

**Parameters:**
- `database`: Database ID (use GET /api/v1/database/ to find)
- `schema`: Schema name (empty string for default)
- `table_name`: Name for the virtual dataset
- `sql`: SQL query (for virtual datasets)
- `owners`: Array of user IDs

**Response includes:**
- `id`: Dataset ID (use in charts)
- `columns`: Auto-detected columns with types

### Example: Daily Stats Dataset

```sql
WITH date_series AS (
    SELECT generate_series(
        (CURRENT_DATE - interval '6 days')::date,
        CURRENT_DATE::date,
        '1 day'::interval
    )::date as day
),
daily_counts AS (
    SELECT
        (created_at + INTERVAL '5 hours 30 minutes')::date as dt,
        COUNT(*) as cnt
    FROM wallet.user_wallets
    WHERE (created_at + INTERVAL '5 hours 30 minutes') >= CURRENT_DATE - interval '6 days'
    GROUP BY (created_at + INTERVAL '5 hours 30 minutes')::date
)
SELECT
    ds.day as date,
    TO_CHAR(ds.day, 'Mon DD') as day_label,
    COALESCE(dc.cnt, 0) as count
FROM date_series ds
LEFT JOIN daily_counts dc ON ds.day = dc.dt
ORDER BY ds.day DESC
```

## Creating a Chart

### Big Number Chart (KPI)

```bash
curl -s -b /tmp/superset_cookies.txt -X POST "https://asksuset.astrokiran.com/api/v1/chart/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF" \
  -H "Referer: https://asksuset.astrokiran.com/" \
  -d '{
    "slice_name": "👥 Total Users",
    "viz_type": "big_number_total",
    "datasource_id": 44,
    "datasource_type": "table",
    "params": "{\"metric\": {\"expressionType\": \"SIMPLE\", \"column\": {\"column_name\": \"total_users\"}, \"aggregate\": \"MAX\"}, \"adhoc_filters\": [], \"header_font_size\": 0.4, \"subheader_font_size\": 0.15, \"y_axis_format\": \"SMART_NUMBER\"}",
    "owners": [3]
  }'
```

**Parameters:**
- `slice_name`: Chart title (supports emojis)
- `viz_type`: Chart type (see below)
- `datasource_id`: Dataset ID
- `datasource_type`: Usually "table"
- `params`: JSON string with chart configuration
- `owners`: Array of user IDs

### Common viz_types

| viz_type | Description |
|----------|-------------|
| `big_number_total` | Single KPI number |
| `big_number` | KPI with trend line |
| `table` | Data table |
| `echarts_timeseries_line` | Line chart |
| `echarts_timeseries_bar` | Bar chart |
| `pie` | Pie chart |
| `dist_bar` | Distribution bar chart |

### Table Chart

```bash
curl -s -b /tmp/superset_cookies.txt -X POST "https://asksuset.astrokiran.com/api/v1/chart/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF" \
  -H "Referer: https://asksuset.astrokiran.com/" \
  -d '{
    "slice_name": "📊 Daily Stats",
    "viz_type": "table",
    "datasource_id": 42,
    "datasource_type": "table",
    "params": "{\"groupby\": [\"day_label\"], \"metrics\": [{\"expressionType\": \"SIMPLE\", \"column\": {\"column_name\": \"count\"}, \"aggregate\": \"MAX\", \"label\": \"Count\"}], \"adhoc_filters\": [], \"row_limit\": 7, \"order_desc\": true}",
    "owners": [3]
  }'
```

## Creating a Dashboard

### Step 1: Create empty dashboard

```bash
curl -s -b /tmp/superset_cookies.txt -X POST "https://asksuset.astrokiran.com/api/v1/dashboard/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF" \
  -H "Referer: https://asksuset.astrokiran.com/" \
  -d '{
    "dashboard_title": "My Dashboard",
    "slug": "my-dashboard",
    "published": true,
    "owners": [3],
    "json_metadata": "{\"refresh_frequency\": 30, \"cross_filters_enabled\": true}"
  }'
```

**Parameters:**
- `dashboard_title`: Display name
- `slug`: URL-friendly name (dashboard accessible at /superset/dashboard/{slug}/)
- `published`: true to make visible
- `json_metadata`: Configuration including refresh frequency (in seconds)

### Step 2: Add charts to dashboard

Update each chart to include the dashboard ID:

```bash
curl -s -b /tmp/superset_cookies.txt -X PUT "https://asksuset.astrokiran.com/api/v1/chart/{chart_id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF" \
  -H "Referer: https://asksuset.astrokiran.com/" \
  -d '{"dashboards": [15]}'
```

Charts will be auto-arranged. Use the Superset UI to manually arrange them.

## Listing Resources

### List all dashboards

```bash
curl -s "https://asksuset.astrokiran.com/api/v1/dashboard/?q=(page:0,page_size:100)" \
  -H "Authorization: Bearer $TOKEN"
```

### List all charts

```bash
curl -s "https://asksuset.astrokiran.com/api/v1/chart/?q=(page:0,page_size:100)" \
  -H "Authorization: Bearer $TOKEN"
```

### List all datasets

```bash
curl -s "https://asksuset.astrokiran.com/api/v1/dataset/?q=(page:0,page_size:100)" \
  -H "Authorization: Bearer $TOKEN"
```

## Deleting Resources

```bash
# Delete a dashboard
curl -s -b /tmp/superset_cookies.txt -X DELETE "https://asksuset.astrokiran.com/api/v1/dashboard/{id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-CSRFToken: $CSRF" \
  -H "Referer: https://asksuset.astrokiran.com/"

# Delete a chart
curl -s -b /tmp/superset_cookies.txt -X DELETE "https://asksuset.astrokiran.com/api/v1/chart/{id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-CSRFToken: $CSRF" \
  -H "Referer: https://asksuset.astrokiran.com/"

# Delete a dataset
curl -s -b /tmp/superset_cookies.txt -X DELETE "https://asksuset.astrokiran.com/api/v1/dataset/{id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-CSRFToken: $CSRF" \
  -H "Referer: https://asksuset.astrokiran.com/"
```

## Complete Example: Create Wallet Dashboard

```bash
#!/bin/bash

BASE_URL="https://asksuset.astrokiran.com"

# 1. Login
echo "Logging in..."
curl -s -c /tmp/superset_cookies.txt -X POST "$BASE_URL/api/v1/security/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "askadmin", "password": "AskAdmin123", "provider": "db"}' > /tmp/login.json

TOKEN=$(python3 -c "import json; print(json.load(open('/tmp/login.json'))['access_token'])")

# 2. Get CSRF token
curl -s -c /tmp/superset_cookies.txt -b /tmp/superset_cookies.txt \
  "$BASE_URL/api/v1/security/csrf_token/" \
  -H "Authorization: Bearer $TOKEN" > /tmp/csrf.json

CSRF=$(python3 -c "import json; print(json.load(open('/tmp/csrf.json'))['result'])")

# 3. Create dataset
echo "Creating dataset..."
DATASET_RESPONSE=$(curl -s -b /tmp/superset_cookies.txt -X POST "$BASE_URL/api/v1/dataset/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF" \
  -H "Referer: $BASE_URL/" \
  -d '{
    "database": 2,
    "schema": "",
    "table_name": "wallet_kpis",
    "sql": "SELECT COUNT(*) as total_users FROM wallet.user_wallets",
    "owners": [3]
  }')

DATASET_ID=$(echo $DATASET_RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Dataset ID: $DATASET_ID"

# 4. Create chart
echo "Creating chart..."
CHART_RESPONSE=$(curl -s -b /tmp/superset_cookies.txt -X POST "$BASE_URL/api/v1/chart/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF" \
  -H "Referer: $BASE_URL/" \
  -d "{
    \"slice_name\": \"Total Users\",
    \"viz_type\": \"big_number_total\",
    \"datasource_id\": $DATASET_ID,
    \"datasource_type\": \"table\",
    \"params\": \"{\\\"metric\\\": {\\\"expressionType\\\": \\\"SIMPLE\\\", \\\"column\\\": {\\\"column_name\\\": \\\"total_users\\\"}, \\\"aggregate\\\": \\\"MAX\\\"}, \\\"y_axis_format\\\": \\\"SMART_NUMBER\\\"}\",
    \"owners\": [3]
  }")

CHART_ID=$(echo $CHART_RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Chart ID: $CHART_ID"

# 5. Create dashboard
echo "Creating dashboard..."
DASHBOARD_RESPONSE=$(curl -s -b /tmp/superset_cookies.txt -X POST "$BASE_URL/api/v1/dashboard/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF" \
  -H "Referer: $BASE_URL/" \
  -d '{
    "dashboard_title": "Wallet Dashboard",
    "slug": "wallet-dashboard",
    "published": true,
    "owners": [3],
    "json_metadata": "{\"refresh_frequency\": 30}"
  }')

DASHBOARD_ID=$(echo $DASHBOARD_RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Dashboard ID: $DASHBOARD_ID"

# 6. Add chart to dashboard
echo "Adding chart to dashboard..."
curl -s -b /tmp/superset_cookies.txt -X PUT "$BASE_URL/api/v1/chart/$CHART_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF" \
  -H "Referer: $BASE_URL/" \
  -d "{\"dashboards\": [$DASHBOARD_ID]}"

echo "Done! Dashboard URL: $BASE_URL/superset/dashboard/wallet-dashboard/"
```

## Troubleshooting

### CSRF Token Missing
```json
{"errors": [{"message": "400 Bad Request: The CSRF token is missing."}]}
```
**Solution:** Include `-H "X-CSRFToken: $CSRF"` header

### CSRF Session Token Missing
```json
{"errors": [{"message": "400 Bad Request: The CSRF session token is missing."}]}
```
**Solution:** Include `-b /tmp/superset_cookies.txt` to send session cookie

### Charts showing "component deleted" in dashboard
**Solution:** Don't use complex `position_json`. Create dashboard first, then add charts via PUT /api/v1/chart/{id} with `{"dashboards": [dashboard_id]}`

### Token Expired
**Solution:** Re-authenticate (tokens expire in ~15 minutes)

## AstroKiran Superset Details

- **URL:** https://asksuset.astrokiran.com
- **Username:** askadmin
- **Password:** AskAdmin123
- **Database ID:** 2 (ProdReadReplica - PostgreSQL)
- **Owner ID:** 3 (Ask Admin)

### Existing Dashboards
- Guides Dashboard: /superset/dashboard/guides-dashboard/
- Wallet Dashboard: /superset/dashboard/wallet-dashboard/

### Timezone Handling
All timestamps in the database are in UTC. Use `+ INTERVAL '5 hours 30 minutes'` for IST conversion:
```sql
(created_at + INTERVAL '5 hours 30 minutes')::date >= '2025-12-05'
```
