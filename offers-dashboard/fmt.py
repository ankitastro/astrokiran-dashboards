"""
Formatting functions - all stateless, under 20 lines each.
"""

from datetime import timezone, timedelta

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# Colors
GREEN, YELLOW, RED, GRAY = "#54efae", "#f0e357", "#f05757", "#9ca3af"


def colorize(value: str, color: str) -> str:
    """Wrap value with color markup."""
    return f"[{color}]{value}[/]"


def pick_color(val: float, lo: float, hi: float, reverse: bool = False) -> str:
    """Pick color based on thresholds."""
    if reverse:
        return GREEN if val < lo else (YELLOW if val < hi else RED)
    return GREEN if val >= hi else (YELLOW if val >= lo else RED)


def fmt_currency(val: float, decimals: int = 2) -> str:
    """Format as Indian Rupees."""
    return f"Rs.{val:,.{decimals}f}"


def fmt_percent(val: float, decimals: int = 1) -> str:
    """Format as percentage."""
    return f"{val:.{decimals}f}%"


def fmt_number(val: float, decimals: int = 0) -> str:
    """Format number with commas."""
    return f"{val:,.{decimals}f}"


def fmt_bytes(val: float) -> str:
    """Format bytes in human readable form."""
    if val == 0:
        return "0 bytes"
    if val < 1024:
        return f"{val:.0f} bytes"
    if val < 1024 * 1024:
        return f"{val / 1024:.2f} KB"
    return f"{val / (1024 * 1024):.2f} MB"


def fmt_duration(seconds: float) -> str:
    """Format seconds as human readable duration."""
    if seconds < 60:
        return f"{seconds:.0f}s ago"
    if seconds < 3600:
        return f"{seconds / 60:.1f}m ago"
    return f"{seconds / 3600:.1f}h ago"


def fmt_date(val, fmt: str = "%Y-%m-%d") -> str:
    """Format date/datetime."""
    if not val:
        return "-"
    if isinstance(val, str):
        return val[:len(fmt.replace("%", ""))]
    return val.strftime(fmt)


def fmt_datetime(val) -> str:
    """Format datetime as YYYY-MM-DD HH:MM in IST."""
    if not val:
        return "-"
    if hasattr(val, 'astimezone'):
        val = val.astimezone(IST)
    return val.strftime("%Y-%m-%d %H:%M")


def pad(val: str) -> str:
    """Pad value with spaces for table cells."""
    return f"  {val}  "


def truncate(val: str, max_len: int = 30) -> str:
    """Truncate string with ellipsis."""
    return val[:max_len] + "..." if len(val) > max_len else val
