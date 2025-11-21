import threading
from typing import Dict, Type, TypeVar

from miraveja_log.application.configuration import LoggerConfig
from miraveja_log.domain import ConfigurationException, IAsyncLogger, ILogger

T = TypeVar("T", bound=ILogger)
AT = TypeVar("AT", bound=IAsyncLogger)


class LoggerFactory:
    """Factory class to create and manage logger instances."""

    def __init__(
        self,
        logger_implementation: Type[T],
        async_logger_implementation: Type[AT],
    ) -> None:
        """
        Initializes the LoggerFactory.

        Args:
            logger_implementation: The class to use for creating synchronous loggers.
            async_logger_implementation: The class to use for creating asynchronous loggers.
        """
        self._logger_implementation = logger_implementation
        self._async_logger_implementation = async_logger_implementation
        self._sync_logger_cache: Dict[str, ILogger] = {}
        self._async_logger_cache: Dict[str, IAsyncLogger] = {}
        self._lock: threading.Lock = threading.Lock()

    def get_or_create_logger(self, config: LoggerConfig) -> ILogger:
        """
        Retrieves a cached or creates a new synchronous logger instance.

        Args:
            config: The configuration for the logger.

        Returns:
            An instance of a class implementing ILogger.

        Raises:
            ConfigurationException: If there is an error in the configuration or creation.
        """
        with self._lock:
            if config.name in self._sync_logger_cache:
                return self._sync_logger_cache[config.name]

            try:
                logger = self._logger_implementation(config)
                self._sync_logger_cache[config.name] = logger
                return logger
            except Exception as e:
                raise ConfigurationException(f"Failed to create logger '{config.name}'", str(e)) from e

    def get_or_create_async_logger(self, config: LoggerConfig) -> IAsyncLogger:
        """
        Retrieves a cached or creates a new asynchronous logger instance.

        Args:
            config: The configuration for the asynchronous logger.

        Returns:
            An instance of a class implementing IAsyncLogger.

        Raises:
            ConfigurationException: If there is an error in the configuration or creation.
        """
        with self._lock:
            if config.name in self._async_logger_cache:
                return self._async_logger_cache[config.name]

            try:
                async_logger = self._async_logger_implementation(config)
                self._async_logger_cache[config.name] = async_logger
                return async_logger
            except Exception as e:
                raise ConfigurationException(f"Failed to create async logger '{config.name}'", str(e)) from e

    def clear_cache(self) -> None:
        """Clear all logger caches. Useful for testing or reconfiguration."""
        with self._lock:
            self._sync_logger_cache.clear()
            self._async_logger_cache.clear()
