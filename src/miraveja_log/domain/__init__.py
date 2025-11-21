"""
Domain layer - Core business logic and models.

This layer contains the fundamental business rules and models for logging.
It has no dependencies on other layers.
"""

from .enums import LogLevel, OutputTarget
from .exceptions import ConfigurationException, HandlerException, LogException
from .interfaces import IAsyncLogger, ILogger
from .models import LogEntry

# Rebuild Pydantic models to resolve forward references
LogEntry.model_rebuild()

__all__: list[str] = [
    # Enums
    "LogLevel",
    "OutputTarget",
    # Interfaces
    "ILogger",
    "IAsyncLogger",
    # Models
    "LogEntry",
    # Exceptions
    "LogException",
    "ConfigurationException",
    "HandlerException",
]
