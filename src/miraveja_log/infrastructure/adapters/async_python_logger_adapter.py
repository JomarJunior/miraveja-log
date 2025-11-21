import asyncio
import sys
from typing import Any

from miraveja_log.application import LoggerConfig
from miraveja_log.domain import IAsyncLogger
from miraveja_log.infrastructure.adapters.python_logger_adapter import PythonLoggerAdapter


class AsyncPythonLoggerAdapter(IAsyncLogger):
    """Adapter wrapping Python's logging.Logger for asynchronous operations."""

    def __init__(self, config: LoggerConfig) -> None:
        """
        Initialize adapter with configuration.

        Args:
            config: Logger configuration settings.
        """

        self._sync_adapter = PythonLoggerAdapter(config)

    def _capture_exc_info(self, kwargs: dict) -> dict:
        """Capture exc_info before passing to thread to preserve exception context."""
        if kwargs.get("exc_info") is True:
            # Capture the actual exception info in the current context
            kwargs = kwargs.copy()
            kwargs["exc_info"] = sys.exc_info()
        return kwargs

    async def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log a debug message."""
        kwargs = self._capture_exc_info(kwargs)
        await asyncio.to_thread(self._sync_adapter.debug, message, *args, **kwargs)

    async def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log an info message."""
        kwargs = self._capture_exc_info(kwargs)
        await asyncio.to_thread(self._sync_adapter.info, message, *args, **kwargs)

    async def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log a warning message."""
        kwargs = self._capture_exc_info(kwargs)
        await asyncio.to_thread(self._sync_adapter.warning, message, *args, **kwargs)

    async def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log an error message."""
        kwargs = self._capture_exc_info(kwargs)
        await asyncio.to_thread(self._sync_adapter.error, message, *args, **kwargs)

    async def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log a critical message."""
        kwargs = self._capture_exc_info(kwargs)
        await asyncio.to_thread(self._sync_adapter.critical, message, *args, **kwargs)
