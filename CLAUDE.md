# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains Terminal User Interface (TUI) dashboards for monitoring the AstroKiran platform - an astrology consultation service connecting customers with astrologer guides. Built with [Textual](https://github.com/Textualize/textual), these dashboards provide real-time analytics by querying PostgreSQL databases on AWS RDS.

## Running Dashboards

All dashboards are standalone Python scripts. Activate the virtual environment and run directly:

```bash
source .venv/bin/activate

# Individual Dashboards
python3 guides_dashboard.py        # Guides availability, skills, earnings, today's orders
python3 customers_dashboard.py     # Customer analytics, segments, top payers
python3 consultations_dashboard.py # Consultation metrics (today/yesterday/day-before)
python3 wallet_dashboard.py        # User wallet monitoring (paginated, 25/page)
```

**Keyboard Shortcuts (Common Across All):**
- `r` - Manual refresh
- `q` - Quit
- Wallet dashboard also supports: `n`/`p` (next/prev page), `←`/`→`, `Home`/`End`

**Auto-Refresh:** 30 seconds (guides, customers, consultations), 10 seconds (wallet)

## Environment Configuration

All dashboards load credentials from `.env` in the project root:

```
DB_ENDPOINT=<RDS endpoint>
DB_PORT=5432
DB_USERNAME=<username>
DB_PASSWORD=<password>
```

**Database Structure:**
- `astrokiran` - Main app database (guides, consultations, wallet)
- `ask_desk_db_2` - Customer and order data
- `analytics` - Problem category analytics

## Architecture

### Dashboard Pattern

Each dashboard follows this architecture:

1. **Data Layer:** SQL queries fetch data via psycopg2
2. **Worker Pattern:** `run_worker()` executes queries in background threads to avoid blocking UI
3. **State Management:** Data stored in instance variables, updated by workers
4. **Display Layer:** Textual widgets (DataTable, MetricCard, ProgressBar) render data
5. **Timer System:** `set_interval()` triggers auto-refresh, tick timers animate progress bars

### Key Components

**MetricCard Widget:** Reusable card displaying title/value with color coding
```python
MetricCard("🟢 Online", "0", "#54efae")
```

**Worker Lifecycle:**
```python
def fetch_data(self):
    self.run_worker(self._fetch_data_worker, thread=True, exclusive=True)

def _fetch_data_worker(self):
    # Execute queries, update instance variables

def on_worker_state_changed(self, event):
    if event.state == WorkerState.SUCCESS:
        self.update_display()  # Refresh UI
```

**Timer Pattern:**
```python
# Progress bar animation
self.set_interval(self.TICK_RATE, self.tick_timer)  # Fast ticks (0.1s)

# On completion:
if self.timer_ticks >= self.total_ticks:
    self.timer_ticks = 0
    self.fetch_data()
```

### SQL Query Organization

**guides_dashboard.py** imports query functions from `guide_queries.py`:
- `get_guide_counts_query()` - Online/offline/total counts
- `get_channel_counts_query()` - Chat/voice/video availability
- `get_skills_breakdown_query()` - Skill-wise guide distribution
- `get_online_guides_query()` - Online guides with earnings, today's orders
- `get_offline_guides_query()` - Offline guides with same metrics
- `get_test_guides_query()` - Test guides (Aman Jain, Praveen)
- `get_promo_grant_spending_query()` - Promotional grant usage since Nov 13
- `get_latest_feedback_query()` - Latest customer feedback per guide

**Today's Orders Columns (IST timezone):**
- `PEND` - Pending orders
- `IP#` - In-progress count
- `IP Names` - Customer names for in-progress orders
- `COMP` - Completed orders
- `Today ₹` - Today's earnings
- `REFU` - Refunded orders
- `CANC` - Cancelled orders

### Database Join Patterns

**Guide-to-Wallet Mapping:**
```sql
-- Phone number normalization to link guides with wallet data
LEFT JOIN wallet.consultant_wallets cw
    ON REPLACE(REPLACE(gp.phone_number, '+91', ''), '+', '') = cw.phone_number
```

**Timezone Handling (IST):**
```sql
-- Today's orders filter
WHERE wo.created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata' >= CURRENT_DATE AT TIME ZONE 'Asia/Kolkata'
```

### CSS Theming

**guides_dashboard.py** uses Dolphie-inspired dark blue theme with specific hex colors:
- Background: `#0a0e1b`
- Containers: `#0f1525`
- Borders: `#1c2440`, `#32416a`
- Green (online): `#54efae`
- Red (offline): `#f05757`
- Blue accents: `#91abec`, `#8fb0ee`

Other dashboards use Textual's default theme variables (`$surface`, `$primary`, `$accent`).

## Adding New Dashboards

When creating a new dashboard:

1. **Query Design:** Use CTEs for complex aggregations, apply timezone conversions for IST
2. **Worker Pattern:** Always use `run_worker()` with `thread=True, exclusive=True`
3. **Error Handling:** Wrap database operations in try/except, use `self.notify()` for user feedback
4. **Column Formatting:** Use `f"{float(value):,.2f}"` for currency, handle None values
5. **Progress Bars:** Implement tick timer for smooth animations (TICK_RATE = 0.1)
6. **Table Setup:** Add columns in `on_mount()`, set `cursor_type = "row"` for navigation
7. **Update Pattern:** Clear tables before repopulating: `table.clear()` then `table.add_row()`

## Testing Database Queries

Test queries directly via psql:

```bash
psql -h $DB_ENDPOINT -U $DB_USERNAME -d astrokiran -c "SELECT ..."
psql -h $DB_ENDPOINT -U $DB_USERNAME -d ask_desk_db_2 -c "SELECT ..."
psql -h $DB_ENDPOINT -U $DB_USERNAME -d analytics -c "SELECT ..."
```

## Important Notes

- **Test Guides Filtering:** Aman Jain and Praveen are filtered out of main online/offline tables, shown separately in test guides table
- **Virtual Cash vs Real Cash:** Wallet dashboard distinguishes promotional (virtual) from paid (real) balances
- **Batch Detection:** Wallet dashboard tracks `batch_size` to identify bulk account creation
- **Real Users Filter:** Wallet dashboard only shows users created or recharged after Nov 13, 2025
- **Phone Number Consistency:** Guide phone numbers use `+91` prefix, wallet uses normalized format without country code
- **JSONB Columns:** `guide_stats` uses JSONB: access via `gp.guide_stats->>'rating'`
- **Pagination State:** Wallet dashboard maintains `current_page` state across refreshes
