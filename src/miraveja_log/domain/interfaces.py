from abc import ABC, abstractmethod
from typing import Any


class ILogger(ABC):
    """Abstract interface for synchronous logging operations."""

    @abstractmethod
    def __init__(self, config: Any) -> None:
        """Initializes the logger."""

    @abstractmethod
    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Logs a debug message."""

    @abstractmethod
    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Logs an info message."""

    @abstractmethod
    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Logs a warning message."""

    @abstractmethod
    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Logs an error message."""

    @abstractmethod
    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Logs a critical message."""


class IAsyncLogger(ABC):
    """Abstract interface for asynchronous logging operations."""

    @abstractmethod
    def __init__(self, config: Any) -> None:
        """Initializes the asynchronous logger."""

    @abstractmethod
    async def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Asynchronously logs a debug message."""

    @abstractmethod
    async def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Asynchronously logs an info message."""

    @abstractmethod
    async def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Asynchronously logs a warning message."""

    @abstractmethod
    async def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Asynchronously logs an error message."""

    @abstractmethod
    async def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Asynchronously logs a critical message."""
