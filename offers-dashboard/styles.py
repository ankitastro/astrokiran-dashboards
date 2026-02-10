"""
CSS Styles for AstroKiran Dashboard
"""

DASHBOARD_CSS = """
Screen {
    background: #0a0e1b;
}

/* Date filter bar */
#filter-container {
    height: auto;
    margin: 0 1;
    padding: 0 1;
    background: #131a2c;
}

#date-range-label {
    text-align: center;
    color: #54efae;
    text-style: bold;
}

/* Timer bar */
#timer-container {
    height: auto;
    margin: 0 1;
    background: #0f1525;
}

#timer-bar {
    width: 100%;
    color: #91abec;
    background: #131a2c;
}

#timer-label {
    width: 100%;
    text-align: center;
    color: #bbc8e8;
    text-style: italic;
}

/* View containers */
#view-wallet, #view-meta, #view-revenue, #view-users, #view-consultations,
#view-payments, #view-meta-campaigns, #view-meta-totals, #view-astro-perf, #view-astro-avail, #view-guides {
    height: 1fr;
}

/* Generic container styling */
Container {
    height: auto;
}

/* Section headers */
.section-header {
    text-align: center;
    text-style: bold;
    color: #8fb0ee;
    background: #131a2c;
    padding: 0 1;
    margin-bottom: 1;
}

/* All DataTables */
DataTable {
    height: auto;
    background: #0f1525;
    color: #e9e9e9;
}

DataTable > .datatable--header {
    background: #131a2c;
    color: #c5c7d2;
    text-style: bold;
}

DataTable > .datatable--odd-row {
    background: #131a2c;
}

DataTable > .datatable--even-row {
    background: #0f1525;
}

DataTable > .datatable--cursor {
    background: #1c2440;
}

/* Specific containers */
#db-stats-container, #kpi-container, #daily-container, #meta-kpi-container {
    height: auto;
    margin: 0 1;
}

/* Transactions and ads containers - take remaining space */
#txn-container, #meta-ads-container {
    height: 1fr;
    border: tall #32416a;
    margin: 1;
    padding: 1;
    background: #0f1525;
}

#txn-table, #meta-ads-table {
    height: 1fr;
}

/* Last update */
#last-update {
    height: 1;
    margin: 0 1;
    text-align: center;
    color: #788bc9;
}

/* Hidden */
.hidden {
    display: none;
}
"""

# Legacy CSS for screens.py (wallet_dashboard.py compatibility)
VIEW_SELECTOR_CSS = """
ViewSelectorScreen { align: center middle; }
#view-dialog { width: 35; height: auto; border: thick #32416a; background: #0f1525; padding: 1 2; }
#view-dialog-title { text-align: center; text-style: bold; color: #8fb0ee; margin-bottom: 1; }
.view-option { width: 100%; margin-bottom: 1; }
"""

FILE_PICKER_CSS = """
FilePickerScreen { align: center middle; }
#file-dialog { width: 80; height: 20; border: thick #32416a; background: #0f1525; padding: 1 2; }
#file-dialog-title { text-align: center; text-style: bold; color: #8fb0ee; margin-bottom: 1; }
#file-list-container { height: 12; }
#file-list { height: 100%; }
#file-buttons { align: center middle; height: auto; margin-top: 1; }
#file-buttons Button { margin: 0 1; }
#file-hint { text-align: center; color: #788bc9; text-style: italic; margin-top: 1; }
"""
