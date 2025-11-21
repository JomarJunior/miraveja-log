"""Unit tests for application logger factory."""

import threading
from typing import Dict
from unittest.mock import Mock

import pytest

from miraveja_log.application.configuration import LoggerConfig
from miraveja_log.application.logger_factory import LoggerFactory
from miraveja_log.domain import ConfigurationException, IAsyncLogger, ILogger, LogLevel, OutputTarget


class MockLogger(ILogger):
    """Mock logger implementation for testing."""

    def __init__(self, config: LoggerConfig) -> None:
        """Initialize mock logger with config."""
        self.config = config

    def debug(self, message: str, **kwargs) -> None:
        """Mock debug method."""
        pass

    def info(self, message: str, **kwargs) -> None:
        """Mock info method."""
        pass

    def warning(self, message: str, **kwargs) -> None:
        """Mock warning method."""
        pass

    def error(self, message: str, **kwargs) -> None:
        """Mock error method."""
        pass

    def critical(self, message: str, **kwargs) -> None:
        """Mock critical method."""
        pass


class MockAsyncLogger(IAsyncLogger):
    """Mock async logger implementation for testing."""

    def __init__(self, config: LoggerConfig) -> None:
        """Initialize mock async logger with config."""
        self.config = config

    async def debug(self, message: str, **kwargs) -> None:
        """Mock async debug method."""
        pass

    async def info(self, message: str, **kwargs) -> None:
        """Mock async info method."""
        pass

    async def warning(self, message: str, **kwargs) -> None:
        """Mock async warning method."""
        pass

    async def error(self, message: str, **kwargs) -> None:
        """Mock async error method."""
        pass

    async def critical(self, message: str, **kwargs) -> None:
        """Mock async critical method."""
        pass


class TestLoggerFactoryBasics:
    """Test basic LoggerFactory functionality."""

    def test_logger_factory_initialization(self) -> None:
        """Test that LoggerFactory can be initialized."""
        factory = LoggerFactory(
            logger_implementation=MockLogger,
            async_logger_implementation=MockAsyncLogger,
        )

        assert factory is not None
        assert factory._logger_implementation == MockLogger
        assert factory._async_logger_implementation == MockAsyncLogger

    def test_logger_factory_has_empty_caches_on_init(self) -> None:
        """Test that LoggerFactory initializes with empty caches."""
        factory = LoggerFactory(
            logger_implementation=MockLogger,
            async_logger_implementation=MockAsyncLogger,
        )

        assert len(factory._sync_logger_cache) == 0
        assert len(factory._async_logger_cache) == 0

    def test_logger_factory_has_lock_on_init(self) -> None:
        """Test that LoggerFactory initializes with a lock."""
        factory = LoggerFactory(
            logger_implementation=MockLogger,
            async_logger_implementation=MockAsyncLogger,
        )

        assert factory._lock is not None
        assert type(factory._lock).__name__ == "lock"


class TestLoggerFactoryGetOrCreateLogger:
    """Test LoggerFactory.get_or_create_logger() method."""

    def test_get_or_create_logger_creates_new_logger(self) -> None:
        """Test that get_or_create_logger creates a new logger instance."""
        factory = LoggerFactory(
            logger_implementation=MockLogger,
            async_logger_implementation=MockAsyncLogger,
        )
        config = LoggerConfig(name="test_logger", level=LogLevel.INFO)

        logger = factory.get_or_create_logger(config)

        assert logger is not None
        assert isinstance(logger, MockLogger)
        assert logger.config.name == "test_logger"

    def test_get_or_create_logger_caches_logger(self) -> None:
        """Test that get_or_create_logger caches the created logger."""
        factory = LoggerFactory(
            logger_implementation=MockLogger,
            async_logger_implementation=MockAsyncLogger,
        )
        config = LoggerConfig(name="test_logger", level=LogLevel.INFO)

        logger = factory.get_or_create_logger(config)

        assert "test_logger" in factory._sync_logger_cache
        assert factory._sync_logger_cache["test_logger"] is logger

    def test_get_or_create_logger_returns_cached_logger(self) -> None:
        """Test that get_or_create_logger returns the cached logger on subsequent calls."""
        factory = LoggerFactory(
            logger_implementation=MockLogger,
            async_logger_implementation=MockAsyncLogger,
        )
        config = LoggerConfig(name="test_logger", level=LogLevel.INFO)

        logger1 = factory.get_or_create_logger(config)
        logger2 = factory.get_or_create_logger(config)

        assert logger1 is logger2

    def test_get_or_create_logger_creates_different_loggers_for_different_names(self) -> None:
        """Test that get_or_create_logger creates different loggers for different names."""
        factory = LoggerFactory(
            logger_implementation=MockLogger,
            async_logger_implementation=MockAsyncLogger,
        )
        config1 = LoggerConfig(name="logger1", level=LogLevel.INFO)
        config2 = LoggerConfig(name="logger2", level=LogLevel.DEBUG)

        logger1 = factory.get_or_create_logger(config1)
        logger2 = factory.get_or_create_logger(config2)

        assert logger1 is not logger2
        assert logger1.config.name == "logger1"
        assert logger2.config.name == "logger2"

    def test_get_or_create_logger_raises_configuration_exception_on_error(self) -> None:
        """Test that get_or_create_logger raises ConfigurationException when logger creation fails."""

        class FailingLogger(ILogger):
            """Logger that fails on initialization."""

            def __init__(self, config: LoggerConfig) -> None:
                raise ValueError("Logger initialization failed")

            def debug(self, message: str, **kwargs) -> None:
                pass

            def info(self, message: str, **kwargs) -> None:
                pass

            def warning(self, message: str, **kwargs) -> None:
                pass

            def error(self, message: str, **kwargs) -> None:
                pass

            def critical(self, message: str, **kwargs) -> None:
                pass

        factory = LoggerFactory(
            logger_implementation=FailingLogger,
            async_logger_implementation=MockAsyncLogger,
        )
        config = LoggerConfig(name="test_logger", level=LogLevel.INFO)

        with pytest.raises(ConfigurationException) as exc_info:
            factory.get_or_create_logger(config)

        assert "Failed to create logger 'test_logger'" in str(exc_info.value)


class TestLoggerFactoryGetOrCreateAsyncLogger:
    """Test LoggerFactory.get_or_create_async_logger() method."""

    def test_get_or_create_async_logger_creates_new_logger(self) -> None:
        """Test that get_or_create_async_logger creates a new async logger instance."""
        factory = LoggerFactory(
            logger_implementation=MockLogger,
            async_logger_implementation=MockAsyncLogger,
        )
        config = LoggerConfig(name="test_logger", level=LogLevel.INFO)

        logger = factory.get_or_create_async_logger(config)

        assert logger is not None
        assert isinstance(logger, MockAsyncLogger)
        assert logger.config.name == "test_logger"

    def test_get_or_create_async_logger_caches_logger(self) -> None:
        """Test that get_or_create_async_logger caches the created logger."""
        factory = LoggerFactory(
            logger_implementation=MockLogger,
            async_logger_implementation=MockAsyncLogger,
        )
        config = LoggerConfig(name="test_logger", level=LogLevel.INFO)

        logger = factory.get_or_create_async_logger(config)

        assert "test_logger" in factory._async_logger_cache
        assert factory._async_logger_cache["test_logger"] is logger

    def test_get_or_create_async_logger_returns_cached_logger(self) -> None:
        """Test that get_or_create_async_logger returns the cached logger on subsequent calls."""
        factory = LoggerFactory(
            logger_implementation=MockLogger,
            async_logger_implementation=MockAsyncLogger,
        )
        config = LoggerConfig(name="test_logger", level=LogLevel.INFO)

        logger1 = factory.get_or_create_async_logger(config)
        logger2 = factory.get_or_create_async_logger(config)

        assert logger1 is logger2

    def test_get_or_create_async_logger_creates_different_loggers_for_different_names(self) -> None:
        """Test that get_or_create_async_logger creates different loggers for different names."""
        factory = LoggerFactory(
            logger_implementation=MockLogger,
            async_logger_implementation=MockAsyncLogger,
        )
        config1 = LoggerConfig(name="logger1", level=LogLevel.INFO)
        config2 = LoggerConfig(name="logger2", level=LogLevel.DEBUG)

        logger1 = factory.get_or_create_async_logger(config1)
        logger2 = factory.get_or_create_async_logger(config2)

        assert logger1 is not logger2
        assert logger1.config.name == "logger1"
        assert logger2.config.name == "logger2"

    def test_get_or_create_async_logger_raises_configuration_exception_on_error(self) -> None:
        """Test that get_or_create_async_logger raises ConfigurationException when logger creation fails."""

        class FailingAsyncLogger(IAsyncLogger):
            """Async logger that fails on initialization."""

            def __init__(self, config: LoggerConfig) -> None:
                raise ValueError("Async logger initialization failed")

            async def debug(self, message: str, **kwargs) -> None:
                pass

            async def info(self, message: str, **kwargs) -> None:
                pass

            async def warning(self, message: str, **kwargs) -> None:
                pass

            async def error(self, message: str, **kwargs) -> None:
                pass

            async def critical(self, message: str, **kwargs) -> None:
                pass

        factory = LoggerFactory(
            logger_implementation=MockLogger,
            async_logger_implementation=FailingAsyncLogger,
        )
        config = LoggerConfig(name="test_logger", level=LogLevel.INFO)

        with pytest.raises(ConfigurationException) as exc_info:
            factory.get_or_create_async_logger(config)

        assert "Failed to create async logger 'test_logger'" in str(exc_info.value)


class TestLoggerFactoryCacheSeparation:
    """Test that sync and async logger caches are separate."""

    def test_sync_and_async_caches_are_separate(self) -> None:
        """Test that sync and async logger caches are independent."""
        factory = LoggerFactory(
            logger_implementation=MockLogger,
            async_logger_implementation=MockAsyncLogger,
        )
        config = LoggerConfig(name="test_logger", level=LogLevel.INFO)

        sync_logger = factory.get_or_create_logger(config)
        async_logger = factory.get_or_create_async_logger(config)

        assert sync_logger is not async_logger
        assert isinstance(sync_logger, MockLogger)
        assert isinstance(async_logger, MockAsyncLogger)

    def test_same_name_different_caches(self) -> None:
        """Test that the same logger name can exist in both caches."""
        factory = LoggerFactory(
            logger_implementation=MockLogger,
            async_logger_implementation=MockAsyncLogger,
        )
        config = LoggerConfig(name="test_logger", level=LogLevel.INFO)

        factory.get_or_create_logger(config)
        factory.get_or_create_async_logger(config)

        assert "test_logger" in factory._sync_logger_cache
        assert "test_logger" in factory._async_logger_cache
        assert len(factory._sync_logger_cache) == 1
        assert len(factory._async_logger_cache) == 1


class TestLoggerFactoryClearCache:
    """Test LoggerFactory.clear_cache() method."""

    def test_clear_cache_removes_all_sync_loggers(self) -> None:
        """Test that clear_cache removes all cached sync loggers."""
        factory = LoggerFactory(
            logger_implementation=MockLogger,
            async_logger_implementation=MockAsyncLogger,
        )
        config1 = LoggerConfig(name="logger1", level=LogLevel.INFO)
        config2 = LoggerConfig(name="logger2", level=LogLevel.DEBUG)

        factory.get_or_create_logger(config1)
        factory.get_or_create_logger(config2)

        assert len(factory._sync_logger_cache) == 2

        factory.clear_cache()

        assert len(factory._sync_logger_cache) == 0

    def test_clear_cache_removes_all_async_loggers(self) -> None:
        """Test that clear_cache removes all cached async loggers."""
        factory = LoggerFactory(
            logger_implementation=MockLogger,
            async_logger_implementation=MockAsyncLogger,
        )
        config1 = LoggerConfig(name="logger1", level=LogLevel.INFO)
        config2 = LoggerConfig(name="logger2", level=LogLevel.DEBUG)

        factory.get_or_create_async_logger(config1)
        factory.get_or_create_async_logger(config2)

        assert len(factory._async_logger_cache) == 2

        factory.clear_cache()

        assert len(factory._async_logger_cache) == 0

    def test_clear_cache_removes_both_sync_and_async_loggers(self) -> None:
        """Test that clear_cache removes both sync and async cached loggers."""
        factory = LoggerFactory(
            logger_implementation=MockLogger,
            async_logger_implementation=MockAsyncLogger,
        )
        config = LoggerConfig(name="test_logger", level=LogLevel.INFO)

        factory.get_or_create_logger(config)
        factory.get_or_create_async_logger(config)

        assert len(factory._sync_logger_cache) == 1
        assert len(factory._async_logger_cache) == 1

        factory.clear_cache()

        assert len(factory._sync_logger_cache) == 0
        assert len(factory._async_logger_cache) == 0

    def test_can_create_logger_after_clear_cache(self) -> None:
        """Test that loggers can be created after calling clear_cache."""
        factory = LoggerFactory(
            logger_implementation=MockLogger,
            async_logger_implementation=MockAsyncLogger,
        )
        config = LoggerConfig(name="test_logger", level=LogLevel.INFO)

        logger1 = factory.get_or_create_logger(config)
        factory.clear_cache()
        logger2 = factory.get_or_create_logger(config)

        assert logger1 is not logger2
        assert isinstance(logger2, MockLogger)


class TestLoggerFactoryThreadSafety:
    """Test LoggerFactory thread safety."""

    def test_concurrent_logger_creation_is_thread_safe(self) -> None:
        """Test that concurrent logger creation is thread-safe."""
        factory = LoggerFactory(
            logger_implementation=MockLogger,
            async_logger_implementation=MockAsyncLogger,
        )
        config = LoggerConfig(name="test_logger", level=LogLevel.INFO)
        loggers = []

        def create_logger():
            logger = factory.get_or_create_logger(config)
            loggers.append(logger)

        threads = [threading.Thread(target=create_logger) for _ in range(10)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # All threads should get the same logger instance
        assert len(loggers) == 10
        assert all(logger is loggers[0] for logger in loggers)

    def test_concurrent_async_logger_creation_is_thread_safe(self) -> None:
        """Test that concurrent async logger creation is thread-safe."""
        factory = LoggerFactory(
            logger_implementation=MockLogger,
            async_logger_implementation=MockAsyncLogger,
        )
        config = LoggerConfig(name="test_logger", level=LogLevel.INFO)
        loggers = []

        def create_async_logger():
            logger = factory.get_or_create_async_logger(config)
            loggers.append(logger)

        threads = [threading.Thread(target=create_async_logger) for _ in range(10)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # All threads should get the same logger instance
        assert len(loggers) == 10
        assert all(logger is loggers[0] for logger in loggers)

    def test_concurrent_clear_cache_is_thread_safe(self) -> None:
        """Test that concurrent clear_cache calls are thread-safe."""
        factory = LoggerFactory(
            logger_implementation=MockLogger,
            async_logger_implementation=MockAsyncLogger,
        )
        config = LoggerConfig(name="test_logger", level=LogLevel.INFO)

        factory.get_or_create_logger(config)

        def clear_cache():
            factory.clear_cache()

        threads = [threading.Thread(target=clear_cache) for _ in range(10)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Cache should be empty after all clears
        assert len(factory._sync_logger_cache) == 0
        assert len(factory._async_logger_cache) == 0


class TestLoggerFactoryEdgeCases:
    """Test edge cases and special scenarios."""

    def test_logger_factory_with_different_output_targets(self) -> None:
        """Test that logger factory works with different output targets."""
        factory = LoggerFactory(
            logger_implementation=MockLogger,
            async_logger_implementation=MockAsyncLogger,
        )

        for target in OutputTarget:
            if target == OutputTarget.CONSOLE:
                config = LoggerConfig(name=f"logger_{target.value}", output_target=target)
            else:
                config = LoggerConfig(
                    name=f"logger_{target.value}",
                    output_target=target,
                    directory="./logs",
                    filename="test.log",
                )

            logger = factory.get_or_create_logger(config)
            assert logger is not None
            assert logger.config.output_target == target

    def test_logger_factory_with_different_log_levels(self) -> None:
        """Test that logger factory works with different log levels."""
        factory = LoggerFactory(
            logger_implementation=MockLogger,
            async_logger_implementation=MockAsyncLogger,
        )

        for level in LogLevel:
            config = LoggerConfig(name=f"logger_{level.value}", level=level)
            logger = factory.get_or_create_logger(config)
            assert logger is not None
            assert logger.config.level == level

    def test_logger_factory_preserves_config(self) -> None:
        """Test that logger factory preserves the configuration."""
        factory = LoggerFactory(
            logger_implementation=MockLogger,
            async_logger_implementation=MockAsyncLogger,
        )
        config = LoggerConfig(
            name="test_logger",
            level=LogLevel.DEBUG,
            output_target=OutputTarget.CONSOLE,
            log_format="%(message)s",
            date_format="%Y-%m-%d",
        )

        logger = factory.get_or_create_logger(config)

        assert logger.config.name == "test_logger"
        assert logger.config.level == LogLevel.DEBUG
        assert logger.config.output_target == OutputTarget.CONSOLE
        assert logger.config.log_format == "%(message)s"
        assert logger.config.date_format == "%Y-%m-%d"
