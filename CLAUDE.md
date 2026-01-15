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
├── SUPERSET_API.md     # Superset REST API documentation
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
    └── meta.py         # Meta Ads view
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
