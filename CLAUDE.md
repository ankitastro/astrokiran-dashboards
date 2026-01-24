# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Terminal User Interface (TUI) dashboards for monitoring the AstroKiran platform. Built with [Textual](https://github.com/Textualize/textual), using a pluggable view framework.

## Running Dashboards

```bash
source ../.venv/bin/activate

# Main app (view framework)
python app.py

# Legacy dashboards
python guides_dashboard.py
python wallet_dashboard.py
```

**Keyboard Shortcuts:**
- `d` - Switch views
- `l` - Load CSV (Meta Ads)
- `r` - Refresh
- `n`/`p` - Next/prev page
- `q` - Quit

## Project Structure

```
dashboards/
├── app.py              # Main app using view framework
├── db.py               # Stateless DB functions
├── fmt.py              # Stateless formatting functions
├── queries.py          # SQL queries (IST timezone adjusted)
├── styles.py           # CSS styles
├── get_rankings.py     # Neo4j guide ranking system
├── neo4j_sync.py       # PostgreSQL → Neo4j incremental sync
├── components/
│   └── date_range.py   # Date range picker component
└── views/
    ├── base.py         # BaseView protocol
    ├── registry.py     # ViewRegistry
    ├── wallet.py       # Wallet dashboard view
    ├── payments.py     # Payments view
    ├── revenue.py      # Revenue view
    ├── users.py        # Users view
    ├── consultations.py # Consultations view
    ├── guides.py       # Guides view
    ├── astrologer_availability.py
    ├── astrologer_performance.py
    ├── meta.py         # Meta Ads view
    ├── meta_campaigns.py
    └── meta_totals.py
```

## View Framework

### Adding a New View

1. Create `views/myview.py`:

```python
from views.base import BaseView, TableConfig, ContainerConfig

class MyView(BaseView):
    name = "My View"
    view_id = "myview"
    icon = "M"

    def get_containers(self):
        return [
            ContainerConfig("my-container", "MY DATA", [
                TableConfig("my-table", ["Col1", "Col2"])
            ])
        ]

    def fetch_data(self, **kwargs):
        # Stateless data fetching
        return {'items': fetch_items()}

    def format_rows(self, data):
        # Stateless formatting
        return {'my-table': [format_item(i) for i in data['items']]}
```

2. Register in `app.py`:

```python
from views.myview import MyView
ViewRegistry.register(MyView())
```

### Design Principles

1. **Stateless Functions:** All functions under 20 lines, no side effects
2. **Separation:** Data fetching, formatting, and display are separate
3. **Pluggable:** Views register themselves, app discovers them

## Module Reference

### db.py - Database Functions

```python
execute_query(query, params)  # Returns list of tuples
execute_single(query, params) # Returns single row
execute_scalar(query, params) # Returns single value
```

### fmt.py - Formatting Functions

```python
colorize(value, color)        # Wrap with color markup
pick_color(val, lo, hi)       # Choose color by threshold
fmt_currency(val, decimals)   # "Rs.1,234.56"
fmt_percent(val, decimals)    # "12.3%"
fmt_number(val, decimals)     # "1,234"
fmt_bytes(val)                # "1.5 KB"
fmt_duration(seconds)         # "5m ago"
fmt_date(val, fmt)            # "2024-01-15"
pad(val)                      # "  value  "
truncate(val, max_len)        # "long text..."
```

### views/base.py - Base Classes

```python
@dataclass
class TableConfig:
    id: str
    columns: List[str]
    cursor: bool = False

@dataclass
class ContainerConfig:
    id: str
    header: str
    tables: List[TableConfig]

class BaseView(ABC):
    name: str
    view_id: str
    icon: str

    def get_containers(self) -> List[ContainerConfig]: ...
    def fetch_data(self, **kwargs) -> dict: ...
    def format_rows(self, data: dict) -> dict: ...
```

## Environment Configuration

`.env` file in project root:

```
DB_ENDPOINT=<RDS endpoint>
DB_PORT=5432
DB_USERNAME=<username>
DB_PASSWORD=<password>
```

## CSS Theming

Colors (Dolphie-inspired dark blue):
- Background: `#0a0e1b`
- Containers: `#0f1525`
- Green: `#54efae`
- Yellow: `#f0e357`
- Red: `#f05757`

## Database Structure

- `astrokiran` - Main app database
- `ask_desk_db_2` - Customer data
- `analytics` - Problem analytics

## Legacy Dashboards

`guides_dashboard.py` and `wallet_dashboard.py` still work but don't use the view framework. They import queries from `guide_queries.py` and `queries.py`.

## Neo4j Guide Ranking System

Graph-based ranking algorithm for astrologers. Deployed on AWS server `65.2.176.137` (prod-worker-wapp).

### Running Rankings

```bash
# View current rankings
python get_rankings.py

# Generate SQL update statement
python get_rankings.py --sql

# Update rankings in PostgreSQL (production)
python get_rankings.py --update
```

### 9-Factor Algorithm

| Factor | Weight | Description |
|--------|--------|-------------|
| Repeat Rate | 35% | (total_bookings - unique_customers) / total_bookings |
| AOV | 15% | Average order value (capped at ₹50) |
| Volume | 15% | Log scale of completed consultations (200 = 100%) |
| Activity | 15% | Days active in last 30 days (20+ = 100%) |
| Rating | 5% | Bayesian rating (prior: 5 reviews at 4.0) |
| Response | 5% | Response time score (≤30s = 100%) |
| Consistency | 5% | Review rate (reviews / completed) |
| Reliability | 3% | 1 - (cancelled / total) |
| Experience | 2% | Months since joined (24+ = 100%) |

**Activity Multiplier Penalty:**
- <5 days active: 0.5x
- 5-10 days: 0.75x
- 10-15 days: 0.9x
- 15+ days: 1.0x

### Neo4j Sync

```bash
# Run incremental sync (hourly via cron)
python neo4j_sync.py
```

Sync state stored in `.neo4j_sync_state.json`. Requires Neo4j environment variables:
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<password>
```

For production updates, also requires:
```
DB_PRIMARY_ENDPOINT=<primary-rds-endpoint>
DB_PRIMARY_USERNAME=<username>
DB_PRIMARY_PASSWORD=<password>
DB_PRIMARY_NAME=astrokiran
```

## Timezone Handling

**Critical:** All timestamps in the database are UTC. Convert to IST (+5:30) for display:

```sql
-- Use this pattern in all date queries
(created_at + INTERVAL '5 hours 30 minutes')::date as date_ist

-- For "today" comparisons
WHERE (created_at + INTERVAL '5 hours 30 minutes')::date = (NOW() + INTERVAL '5 hours 30 minutes')::date
```

## Superset Integration

See `SUPERSET_API.md` for REST API documentation. Key endpoints:
- Login: `POST /api/v1/security/login`
- CSRF: `GET /api/v1/security/csrf_token/`
- Datasets: `POST /api/v1/dataset/`
- Charts: `POST /api/v1/chart/`

Superset credentials are in `.env` (SUPERSET_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD).
