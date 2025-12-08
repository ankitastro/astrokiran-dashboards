"""
View Registry - Central registration for all views.
"""

from typing import Dict, List, Type
from views.base import BaseView


class ViewRegistry:
    """Registry for dashboard views."""

    _views: Dict[str, BaseView] = {}

    @classmethod
    def register(cls, view: BaseView) -> None:
        """Register a view instance."""
        cls._views[view.view_id] = view

    @classmethod
    def get(cls, view_id: str) -> BaseView:
        """Get a view by ID."""
        return cls._views.get(view_id)

    @classmethod
    def all(cls) -> List[BaseView]:
        """Get all registered views."""
        return list(cls._views.values())

    @classmethod
    def ids(cls) -> List[str]:
        """Get all view IDs."""
        return list(cls._views.keys())

    @classmethod
    def clear(cls) -> None:
        """Clear all registered views."""
        cls._views.clear()
