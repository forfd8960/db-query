"""Base exporter abstract class."""

from abc import ABC, abstractmethod
from typing import Any


class BaseExporter(ABC):
    """Abstract base class for all export format implementations."""

    @abstractmethod
    def export(self, columns: list[str], rows: list[dict[str, Any]]) -> bytes:
        """
        Export query results to the specific format.

        Args:
            columns: List of column names
            rows: List of row dictionaries with column names as keys

        Returns:
            Exported data as bytes

        Raises:
            ValueError: If data is invalid or cannot be exported
        """
        pass
