import logging
from typing import Any, Dict, List, Optional, Tuple

from miraveja_log.domain import ILogger


class MemoryHandler(logging.Handler):
    """Handler that captures log records in memory for testing."""

    def __init__(self) -> None:
        """
        Initialize the memory handler.
        """
        super().__init__()
        self.records: List[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        """
        Store the log record in memory.

        Args:
            record: The log record to store.
        """
        self.records.append(record)

    def clear(self) -> None:
        """
        Clear all stored log records.
        """
        self.records.clear()

    def get_messages(self) -> List[str]:
        """
        Retrieve all stored log messages.

        Returns:
            A list of log messages.
        """
        return [self.format(record) for record in self.records]


class MockLogger(ILogger):
    """Mock logger for testing without actual I/O."""

    def __init__(self) -> None:
        """
        Initialize the mock logger.
        """
        self.calls: List[Tuple[str, str, Tuple, Dict]] = []  # (level, message, args, kwargs)

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log a debug message."""
        self.calls.append(("debug", message, args, kwargs))

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log an info message."""
        self.calls.append(("info", message, args, kwargs))

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log a warning message."""
        self.calls.append(("warning", message, args, kwargs))

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log an error message."""
        self.calls.append(("error", message, args, kwargs))

    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log a critical message."""
        self.calls.append(("critical", message, args, kwargs))

    def clear(self) -> None:
        """
        Clear all recorded log calls.
        """
        self.calls.clear()

    def get_messages(self, level: Optional[str] = None) -> List[str]:
        """
        Retrieve logged messages, optionally filtered by level.

        Args:
            level: The log level to filter by (e.g., "debug", "info").

        Returns:
            A list of log messages.
        """
        if level:
            return [msg for lvl, msg, _, _ in self.calls if lvl == level]
        return [msg for _, msg, _, _ in self.calls]
