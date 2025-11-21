"""
Infrastructure layer - External integrations.

This layer contains adapters for external systems and frameworks.
Depends on Application and Domain layers.
"""

from .adapters import AsyncPythonLoggerAdapter, PythonLoggerAdapter
from .formatters import JSONFormatter, TextFormatter

__all__: list[str] = [
    # Adapters
    "PythonLoggerAdapter",
    "AsyncPythonLoggerAdapter",
    # Formatters
    "TextFormatter",
    "JSONFormatter",
]
