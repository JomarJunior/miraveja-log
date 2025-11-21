"""
miraveja-log: Lightweight and flexible logging library with structured logging support.

Public API exports for the miraveja-log package.
"""

# Application exports
from miraveja_log.application import LoggerConfig, LoggerFactory

# Domain exports
from miraveja_log.domain import (
    ConfigurationException,
    HandlerException,
    IAsyncLogger,
    ILogger,
    LogException,
    LogLevel,
    OutputTarget,
)

__version__ = "0.1.0"

__all__: list[str] = [
    # Factory
    "LoggerFactory",
    # Configuration
    "LoggerConfig",
    # Enums
    "LogLevel",
    "OutputTarget",
    # Interfaces
    "ILogger",
    "IAsyncLogger",
    # Exceptions
    "LogException",
    "ConfigurationException",
    "HandlerException",
]
