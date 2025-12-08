"""
CSS Styles for AstroKiran Dashboard
Dolphie-inspired Dark Blue Theme
"""

# Main Dashboard CSS
DASHBOARD_CSS = """
/* Dolphie-inspired Dark Blue Theme */
Screen {
    background: #0a0e1b;
}

/* --- Refresh Timer Bar --- */
#refresh-timer-container {
    height: auto;
    margin: 0 1;
    background: #0f1525;
}

#refresh-bar {
    width: 100%;
    margin-bottom: 1;
    color: #91abec;
    background: #131a2c;
}

#refresh-bar > .bar--bar {
    color: #91abec;
}

#refresh-bar > .bar--complete {
    color: #54efae;
}

#top-info-bar {
    height: auto;
    width: 100%;
}

#refresh-label {
    width: 100%;
    text-align: center;
    color: #bbc8e8;
    text-style: italic;
    padding: 0 1;
}

/* --- DB Stats Table --- */
#db-stats-container {
    height: auto;
    margin: 1 1 0 1;
}

#db-stats-table {
    height: auto;
    border: solid #1c2440;
    background: #0f1525;
    text-align: center;
}

/* --- KPI Table --- */
#kpi-container {
    height: auto;
    margin: 1 1 0 1;
}

#kpi-table {
    height: auto;
    border: solid #1c2440;
    background: #0f1525;
    text-align: center;
}

/* --- Daily Recharge Table --- */
#daily-recharge-container {
    height: auto;
    margin: 1 1 0 1;
}

#daily-recharge-table {
    height: auto;
    border: solid #1c2440;
    background: #0f1525;
    text-align: center;
}

/* --- RDS Tables --- */
#rds-container-1 {
    height: auto;
    margin: 1 1 0 1;
}

#rds-table-1 {
    height: auto;
    border: solid #1c2440;
    background: #0f1525;
    text-align: center;
}

#rds-container-2 {
    height: auto;
    margin: 1 1 0 1;
}

#rds-table-2 {
    height: auto;
    border: solid #1c2440;
    background: #0f1525;
    text-align: center;
}

/* --- Main Users Table --- */
#users-container {
    height: 1fr;
    border: tall #32416a;
    margin: 1;
    padding: 1;
    background: #0f1525;
}

.section-header {
    text-align: center;
    text-style: bold;
    color: #8fb0ee;
    background: #131a2c;
    padding: 0 1;
    margin-bottom: 1;
}

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

DataTable > .datatable--hover {
    background: #171e2f;
}

#all-users-table {
    height: 1fr;
}

/* --- Pagination Info --- */
#pagination-info {
    height: 1;
    text-align: center;
    background: #131a2c;
    color: #bbc8e8;
    text-style: bold;
    margin-top: 1;
}

/* --- Last Update Label --- */
#last-update {
    height: 1;
    margin: 1;
    text-align: center;
    color: #788bc9;
    background: #0f1525;
}

/* Hidden class for view toggling */
.hidden {
    display: none;
}

/* --- Meta Ads View Styles --- */
#meta-ads-view {
    height: 1fr;
}

#meta-kpi-container {
    height: auto;
    margin: 1 1 0 1;
}

#meta-kpi-table {
    height: auto;
    border: solid #1c2440;
    background: #0f1525;
    text-align: center;
}

#meta-ads-container {
    height: 1fr;
    border: tall #32416a;
    margin: 1;
    padding: 1;
    background: #0f1525;
}

#meta-ads-table {
    height: 1fr;
}

#meta-pagination-info {
    height: 1;
    text-align: center;
    background: #131a2c;
    color: #bbc8e8;
    text-style: bold;
    margin-top: 1;
}

/* Wallet view container */
#wallet-view {
    height: 1fr;
}
"""

# View Selector Modal CSS
VIEW_SELECTOR_CSS = """
ViewSelectorScreen {
    align: center middle;
}

#view-dialog {
    width: 35;
    height: auto;
    border: thick #32416a;
    background: #0f1525;
    padding: 1 2;
}

#view-dialog-title {
    text-align: center;
    text-style: bold;
    color: #8fb0ee;
    margin-bottom: 1;
}

.view-option {
    width: 100%;
    margin: 0 0 1 0;
}
"""

# File Picker Modal CSS
FILE_PICKER_CSS = """
FilePickerScreen {
    align: center middle;
}

#file-dialog {
    width: 90;
    height: 24;
    border: thick #32416a;
    background: #0f1525;
    padding: 1 2;
}

#file-dialog-title {
    text-align: center;
    text-style: bold;
    color: #8fb0ee;
    margin-bottom: 1;
}

#file-list-container {
    height: 16;
    border: solid #1c2440;
    background: #131a2c;
}

#file-list {
    height: 100%;
}

#file-buttons {
    align: center middle;
    height: auto;
    margin-top: 1;
}

#file-buttons Button {
    margin: 0 1;
}

#file-hint {
    color: #788bc9;
    text-align: center;
    height: auto;
    margin-top: 1;
    text-style: italic;
}
"""
