"""
Base View Protocol for Dashboard Views
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Callable, Any
from textual.app import ComposeResult


@dataclass
class TableConfig:
    """Configuration for a DataTable."""
    id: str
    columns: List[str]
    cursor: bool = False


@dataclass
class ContainerConfig:
    """Configuration for a container with tables."""
    id: str
    header: str
    tables: List[TableConfig]


class BaseView(ABC):
    """Abstract base class for dashboard views."""

    name: str = ""
    view_id: str = ""
    icon: str = ""

    @abstractmethod
    def get_containers(self) -> List[ContainerConfig]:
        """Return list of container configurations."""
        pass

    @abstractmethod
    def fetch_data(self, **kwargs) -> dict:
        """Fetch data for this view. Must be stateless."""
        pass

    @abstractmethod
    def format_rows(self, data: dict) -> dict:
        """Format data into table rows. Must be stateless."""
        pass

    def get_css(self) -> str:
        """Return view-specific CSS. Override if needed."""
        return ""
