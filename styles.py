"""
CSS Styles for AstroKiran Dashboard
"""

DASHBOARD_CSS = """
Screen {
    background: #0a0e1b;
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
#view-wallet, #view-meta {
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

/* Users and ads containers - take remaining space */
#users-container, #meta-ads-container {
    height: 1fr;
    border: tall #32416a;
    margin: 1;
    padding: 1;
    background: #0f1525;
}

#users-table, #meta-ads-table {
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
