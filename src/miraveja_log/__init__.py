"""
miraveja-log: Lightweight and flexible logging library with structured logging support.

Public API exports for the miraveja-log package.
"""

# Application exports
from miraveja_log.application import LoggerConfig, LoggerFactory

# Domain exports
from miraveja_log.domain import (
    ILogger,
    Logger,
    LoggerAlreadyExistsException,
    LoggerException,
    LoggerLevel,
    LoggerTarget,
)

__version__ = "0.1.0"

__all__ = [
    # Factory
    "LoggerFactory",
    # Configuration
    "LoggerConfig",
    # Enums
    "LoggerLevel",
    "LoggerTarget",
    # Interfaces
    "ILogger",
    # Models
    "Logger",
    # Exceptions
    "LoggerException",
    "LoggerAlreadyExistsException",
]
