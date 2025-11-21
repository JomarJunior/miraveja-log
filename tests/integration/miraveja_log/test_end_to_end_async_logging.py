"""End-to-end integration tests for asynchronous logging."""

import asyncio
import logging
from pathlib import Path

import pytest

from miraveja_log.application import LoggerConfig, LoggerFactory
from miraveja_log.domain import IAsyncLogger, LogLevel, OutputTarget
from miraveja_log.infrastructure.adapters import AsyncPythonLoggerAdapter, PythonLoggerAdapter
from miraveja_log.infrastructure.testing import MemoryHandler


class TestEndToEndAsyncLogging:
    """Test complete asynchronous logging workflow from factory to output."""

    @pytest.mark.asyncio
    async def test_create_async_logger_with_factory(self) -> None:
        """Test creating an async logger using factory with default config."""
        config = LoggerConfig(name="test_async_logger")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)

        logger = factory.get_or_create_async_logger(config)

        assert logger is not None
        assert isinstance(logger, IAsyncLogger)

    @pytest.mark.asyncio
    async def test_async_logger_logs_all_levels(self) -> None:
        """Test that async logger can log at all severity levels."""
        config = LoggerConfig(name="test_async_all_levels")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_async_logger(config)

        # Add memory handler to capture logs
        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        # Log at all levels asynchronously
        await logger.debug("Async debug message")
        await logger.info("Async info message")
        await logger.warning("Async warning message")
        await logger.error("Async error message")
        await logger.critical("Async critical message")

        messages = memory_handler.get_messages()
        assert len(messages) == 5

        # Clean up
        underlying_logger.removeHandler(memory_handler)

    @pytest.mark.asyncio
    async def test_async_logger_respects_log_level_filtering(self) -> None:
        """Test that async log level filtering works correctly."""
        config = LoggerConfig(name="test_async_level_filter", level=LogLevel.ERROR)
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_async_logger(config)

        # Add memory handler
        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        # Log at all levels
        await logger.debug("Async debug message")
        await logger.info("Async info message")
        await logger.warning("Async warning message")
        await logger.error("Async error message")
        await logger.critical("Async critical message")

        messages = memory_handler.get_messages()
        # Only ERROR and CRITICAL should be logged
        assert len(messages) == 2
        assert "Async error message" in messages[0]
        assert "Async critical message" in messages[1]

        # Clean up
        underlying_logger.removeHandler(memory_handler)

    @pytest.mark.asyncio
    async def test_async_logger_with_custom_format(self) -> None:
        """Test async logger with custom log format."""
        custom_format = "[%(levelname)s] %(message)s"
        config = LoggerConfig(name="test_async_custom_format", format=custom_format)
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_async_logger(config)

        # Add memory handler
        memory_handler = MemoryHandler()
        memory_handler.setFormatter(logging.Formatter(custom_format))
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        await logger.info("Async test message")

        messages = memory_handler.get_messages()
        assert len(messages) == 1
        assert "[INFO] Async test message" in messages[0]

        # Clean up
        underlying_logger.removeHandler(memory_handler)

    @pytest.mark.asyncio
    async def test_async_logger_with_extra_fields(self) -> None:
        """Test async logger with structured logging (extra fields)."""
        config = LoggerConfig(name="test_async_extra_fields")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_async_logger(config)

        # Add memory handler
        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        # Log with extra fields
        await logger.info("Async user action", extra={"user_id": "456", "action": "logout"})

        records = memory_handler.records
        assert len(records) == 1
        assert hasattr(records[0], "user_id")
        assert records[0].user_id == "456"
        assert records[0].action == "logout"

        # Clean up
        underlying_logger.removeHandler(memory_handler)

    @pytest.mark.asyncio
    async def test_async_logger_caching_returns_same_instance(self) -> None:
        """Test that factory returns cached async logger for same name."""
        config = LoggerConfig(name="test_async_cached_logger")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)

        logger1 = factory.get_or_create_async_logger(config)
        logger2 = factory.get_or_create_async_logger(config)

        assert logger1 is logger2

    @pytest.mark.asyncio
    async def test_async_logger_different_names_create_different_instances(self) -> None:
        """Test that different async logger names create different instances."""
        config1 = LoggerConfig(name="test_async_logger_1")
        config2 = LoggerConfig(name="test_async_logger_2")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)

        logger1 = factory.get_or_create_async_logger(config1)
        logger2 = factory.get_or_create_async_logger(config2)

        assert logger1 is not logger2

    @pytest.mark.asyncio
    async def test_async_logger_with_positional_args(self) -> None:
        """Test async logger with positional arguments for string formatting."""
        config = LoggerConfig(name="test_async_positional_args")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_async_logger(config)

        # Add memory handler
        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        await logger.info("Async user %s logged in at %s", "jane_doe", "2025-11-20")

        messages = memory_handler.get_messages()
        assert len(messages) == 1
        assert "jane_doe" in messages[0]
        assert "2025-11-20" in messages[0]

        # Clean up
        underlying_logger.removeHandler(memory_handler)

    @pytest.mark.asyncio
    async def test_async_logger_with_exception_info(self) -> None:
        """Test async logger with exception information."""
        config = LoggerConfig(name="test_async_exception_info")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_async_logger(config)

        # Add memory handler
        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        try:
            raise ValueError("Async test exception")
        except ValueError:
            await logger.error("An async error occurred", exc_info=True)

        messages = memory_handler.get_messages()
        assert len(messages) == 1
        assert "An async error occurred" in messages[0]
        assert "ValueError: Async test exception" in messages[0]
        assert "Traceback" in messages[0]

        # Clean up
        underlying_logger.removeHandler(memory_handler)

    @pytest.mark.asyncio
    async def test_concurrent_async_logging(self) -> None:
        """Test that concurrent async logging works correctly."""
        config = LoggerConfig(name="test_concurrent_async")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_async_logger(config)

        # Add memory handler
        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        # Log concurrently
        async def log_task(task_id: int) -> None:
            await logger.info(f"Task {task_id} executing")

        await asyncio.gather(*[log_task(i) for i in range(10)])

        messages = memory_handler.get_messages()
        assert len(messages) == 10

        # Clean up
        underlying_logger.removeHandler(memory_handler)

    @pytest.mark.asyncio
    async def test_multiple_async_loggers_operate_independently(self) -> None:
        """Test that multiple async loggers operate independently."""
        config1 = LoggerConfig(name="test_async_independent_1")
        config2 = LoggerConfig(name="test_async_independent_2")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)

        logger1 = factory.get_or_create_async_logger(config1)
        logger2 = factory.get_or_create_async_logger(config2)

        # Add memory handlers
        handler1 = MemoryHandler()
        handler2 = MemoryHandler()
        logging.getLogger(config1.name).addHandler(handler1)
        logging.getLogger(config2.name).addHandler(handler2)

        await logger1.info("Async logger 1 message")
        await logger2.info("Async logger 2 message")

        messages1 = handler1.get_messages()
        messages2 = handler2.get_messages()

        assert len(messages1) == 1
        assert len(messages2) == 1
        assert "Async logger 1 message" in messages1[0]
        assert "Async logger 2 message" in messages2[0]

        # Clean up
        logging.getLogger(config1.name).removeHandler(handler1)
        logging.getLogger(config2.name).removeHandler(handler2)

    @pytest.mark.asyncio
    async def test_async_logger_with_all_output_targets(self) -> None:
        """Test that async logger can be created with all output targets."""
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)

        # Console target
        config_console = LoggerConfig(name="test_async_console", output_target=OutputTarget.CONSOLE)
        logger_console = factory.get_or_create_async_logger(config_console)
        assert logger_console is not None

        # File target (with temp directory)
        temp_dir = Path("./temp_logs_async")
        temp_dir.mkdir(exist_ok=True)
        config_file = LoggerConfig(
            name="test_async_file",
            output_target=OutputTarget.FILE,
            directory=temp_dir,
            filename="test.log",
        )
        logger_file = factory.get_or_create_async_logger(config_file)
        assert logger_file is not None

        # JSON target
        config_json = LoggerConfig(
            name="test_async_json",
            output_target=OutputTarget.JSON,
            directory=temp_dir,
            filename="test.json",
        )
        logger_json = factory.get_or_create_async_logger(config_json)
        assert logger_json is not None

        # Clean up - close all handlers first to release file locks
        import logging
        import shutil

        for logger_name in ["test_async_file", "test_async_json"]:
            logger = logging.getLogger(logger_name)
            for handler in logger.handlers[:]:
                if isinstance(handler, logging.FileHandler):
                    handler.close()
                    logger.removeHandler(handler)

        if temp_dir.exists():
            shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_mixed_sync_async_loggers_separate_caches(self) -> None:
        """Test that sync and async loggers maintain separate caches."""
        config = LoggerConfig(name="test_mixed_logger")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)

        sync_logger = factory.get_or_create_logger(config)
        async_logger = factory.get_or_create_async_logger(config)

        # They should be different instances
        assert sync_logger is not async_logger
        assert type(sync_logger).__name__ != type(async_logger).__name__
