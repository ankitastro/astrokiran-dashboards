# AstroKiran Dashboards

This directory contains TUI (Terminal User Interface) dashboards for monitoring different aspects of the AstroKiran platform.

## Quick Start - Master Dashboard

**Recommended**: Start with the Master Dashboard which embeds all dashboards in one interface.

```bash
python3 dashboards/master_dashboard.py
```

The Master Dashboard provides:
- 🏠 **Home Screen**: System overview with key metrics from all databases
- 👥 **Guides Tab**: Embedded live Guides Dashboard with auto-refresh
- 📊 **Customers Tab**: Embedded live Customers Dashboard with auto-refresh

All dashboards update automatically every 30 seconds.

**Keyboard Shortcuts**:
- `h` - Return to Home
- `1` - Switch to Guides Dashboard tab
- `2` - Switch to Customers Dashboard tab
- `q` - Quit

---

## Available Dashboards

### 1. Guides Dashboard (`guides_dashboard.py`)

Real-time monitoring of astrologer guides with:
- **Metrics**: Online/Offline counts, channel availability (Chat/Voice/Video)
- **Skills Breakdown**: Guide counts per astrological skill
- **Online Guides**: Green-bordered table with all online guides
- **Offline Guides**: Red-bordered table with all offline guides

**Columns**: ID, Name, Phone, Chat, Voice, Video, Skills, ₹/min, Rating, Consults, Earnings ₹

**Usage**:
```bash
python3 dashboards/guides_dashboard.py
```

**Keyboard Shortcuts**:
- `r` - Manual refresh
- `q` - Quit

**Auto-refresh**: Every 30 seconds

---

### 2. Customers Dashboard (`customers_dashboard.py`)

Real-time monitoring of customer analytics and revenue with:
- **Metrics**: Total customers, Paid customers, Cart abandoners, Never ordered, Total revenue
- **Problem Category Segments**: Customer distribution across problem categories (Financial, Career, Business, Marriage)
- **Top 20 Paying Customers**: Highest revenue customers with order counts
- **Recent 20 Customers**: Latest customer signups with status

**Columns**:
- Top Customers: Phone, Name, Orders, Total Spent ₹, Last Order
- Recent Customers: Phone, Name, Status, Created, Last Activity

**Usage**:
```bash
python3 dashboards/customers_dashboard.py
```

**Keyboard Shortcuts**:
- `r` - Manual refresh
- `q` - Quit

**Auto-refresh**: Every 30 seconds

**Databases Used**: Both `ask_desk_db_2` (main app) and `analytics` (problem categories)

---

## Technical Details

All dashboards:
- Built with [Textual](https://github.com/Textualize/textual) framework
- Connect to AWS RDS PostgreSQL (`astrokiran` database)
- Load credentials from `.env` file in project root
- Use phone number mapping via `wallet.consultant_wallets` for financial data

## Navigation

### Option 1: Master Dashboard (Recommended)
Use the master dashboard as a central hub:
```bash
python3 dashboards/master_dashboard.py
```

### Option 2: Individual Dashboards
Run each dashboard separately for full-screen, real-time monitoring:
```bash
# Guides Dashboard
python3 dashboards/guides_dashboard.py

# Customers Dashboard
python3 dashboards/customers_dashboard.py
```

## Dashboard Architecture

The dashboard system uses an embeddable widget pattern:

### Widget Components (Embeddable)
- **`guides_widget.py`**: GuidesWidget - embeddable guides monitoring component
- **`customers_widget.py`**: CustomersWidget - embeddable customers analytics component

These widgets extend `ScrollableContainer` and can be used standalone or embedded in other dashboards.

### Standalone Dashboards
- **`guides_dashboard.py`**: Full-screen guides monitoring app
- **`customers_dashboard.py`**: Full-screen customers analytics app

### Master Dashboard
- **`master_dashboard.py`**: Imports and embeds both widget components with tabbed navigation

## Development

To add a new dashboard:
1. Create `{name}_widget.py` extending ScrollableContainer with embeddable component
2. Create `{name}_dashboard.py` as standalone App using the widget
3. Import widget in `master_dashboard.py` and add a new TabPane
4. Query widget in on_mount and setup auto-refresh timer: `self.set_interval(30, widget.refresh_data)`
5. Update this README
6. Update main project CLAUDE.md
