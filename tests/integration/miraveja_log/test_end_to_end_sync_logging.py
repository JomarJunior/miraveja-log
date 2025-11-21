"""End-to-end integration tests for synchronous logging."""

import logging
from pathlib import Path
from typing import List

import pytest

from miraveja_log.application import LoggerConfig, LoggerFactory
from miraveja_log.domain import ILogger, LogLevel, OutputTarget
from miraveja_log.infrastructure.adapters import AsyncPythonLoggerAdapter, PythonLoggerAdapter
from miraveja_log.infrastructure.testing import MemoryHandler


class TestEndToEndSyncLogging:
    """Test complete synchronous logging workflow from factory to output."""

    def test_create_sync_logger_with_factory(self) -> None:
        """Test creating a sync logger using factory with default config."""
        config = LoggerConfig(name="test_sync_logger")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)

        logger = factory.get_or_create_logger(config)

        assert logger is not None
        assert isinstance(logger, ILogger)

    def test_sync_logger_logs_all_levels(self) -> None:
        """Test that sync logger can log at all severity levels."""
        config = LoggerConfig(name="test_all_levels")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        # Add memory handler to capture logs
        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        # Log at all levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

        messages = memory_handler.get_messages()
        assert len(messages) == 5

        # Clean up
        underlying_logger.removeHandler(memory_handler)

    def test_sync_logger_respects_log_level_filtering(self) -> None:
        """Test that log level filtering works correctly."""
        config = LoggerConfig(name="test_level_filter", level=LogLevel.WARNING)
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        # Add memory handler
        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        # Log at all levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        messages = memory_handler.get_messages()
        # Only WARNING and ERROR should be logged
        assert len(messages) == 2
        assert "Warning message" in messages[0]
        assert "Error message" in messages[1]

        # Clean up
        underlying_logger.removeHandler(memory_handler)

    def test_sync_logger_with_custom_format(self) -> None:
        """Test sync logger with custom log format."""
        custom_format = "%(levelname)s | %(message)s"
        config = LoggerConfig(name="test_custom_format", format=custom_format)
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        # Add memory handler
        memory_handler = MemoryHandler()
        memory_handler.setFormatter(logging.Formatter(custom_format))
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        logger.info("Test message")

        messages = memory_handler.get_messages()
        assert len(messages) == 1
        assert "INFO | Test message" in messages[0]

        # Clean up
        underlying_logger.removeHandler(memory_handler)

    def test_sync_logger_with_extra_fields(self) -> None:
        """Test sync logger with structured logging (extra fields)."""
        config = LoggerConfig(name="test_extra_fields")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        # Add memory handler
        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        # Log with extra fields
        logger.info("User action", extra={"user_id": "123", "action": "login"})

        records = memory_handler.records
        assert len(records) == 1
        assert hasattr(records[0], "user_id")
        assert records[0].user_id == "123"
        assert records[0].action == "login"

        # Clean up
        underlying_logger.removeHandler(memory_handler)

    def test_sync_logger_caching_returns_same_instance(self) -> None:
        """Test that factory returns cached logger for same name."""
        config = LoggerConfig(name="test_cached_logger")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)

        logger1 = factory.get_or_create_logger(config)
        logger2 = factory.get_or_create_logger(config)

        assert logger1 is logger2

    def test_sync_logger_different_names_create_different_instances(self) -> None:
        """Test that different logger names create different instances."""
        config1 = LoggerConfig(name="test_logger_1")
        config2 = LoggerConfig(name="test_logger_2")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)

        logger1 = factory.get_or_create_logger(config1)
        logger2 = factory.get_or_create_logger(config2)

        assert logger1 is not logger2

    def test_sync_logger_clear_cache_removes_instances(self) -> None:
        """Test that clear_cache removes cached logger instances."""
        config = LoggerConfig(name="test_clear_cache")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)

        logger1 = factory.get_or_create_logger(config)
        factory.clear_cache()
        logger2 = factory.get_or_create_logger(config)

        assert logger1 is not logger2

    def test_sync_logger_with_positional_args(self) -> None:
        """Test sync logger with positional arguments for string formatting."""
        config = LoggerConfig(name="test_positional_args")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        # Add memory handler
        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        logger.info("User %s logged in at %s", "john_doe", "2025-11-20")

        messages = memory_handler.get_messages()
        assert len(messages) == 1
        assert "john_doe" in messages[0]
        assert "2025-11-20" in messages[0]

        # Clean up
        underlying_logger.removeHandler(memory_handler)

    def test_sync_logger_with_exception_info(self) -> None:
        """Test sync logger with exception information."""
        config = LoggerConfig(name="test_exception_info")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        # Add memory handler
        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.error("An error occurred", exc_info=True)

        messages = memory_handler.get_messages()
        assert len(messages) == 1
        assert "An error occurred" in messages[0]
        assert "ValueError: Test exception" in messages[0]
        assert "Traceback" in messages[0]

        # Clean up
        underlying_logger.removeHandler(memory_handler)

    def test_multiple_sync_loggers_operate_independently(self) -> None:
        """Test that multiple sync loggers operate independently."""
        config1 = LoggerConfig(name="test_independent_1")
        config2 = LoggerConfig(name="test_independent_2")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)

        logger1 = factory.get_or_create_logger(config1)
        logger2 = factory.get_or_create_logger(config2)

        # Add memory handlers
        handler1 = MemoryHandler()
        handler2 = MemoryHandler()
        logging.getLogger(config1.name).addHandler(handler1)
        logging.getLogger(config2.name).addHandler(handler2)

        logger1.info("Logger 1 message")
        logger2.info("Logger 2 message")

        messages1 = handler1.get_messages()
        messages2 = handler2.get_messages()

        assert len(messages1) == 1
        assert len(messages2) == 1
        assert "Logger 1 message" in messages1[0]
        assert "Logger 2 message" in messages2[0]

        # Clean up
        logging.getLogger(config1.name).removeHandler(handler1)
        logging.getLogger(config2.name).removeHandler(handler2)

    def test_sync_logger_with_all_output_targets(self) -> None:
        """Test that sync logger can be created with all output targets."""
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)

        # Console target
        config_console = LoggerConfig(name="test_console", output_target=OutputTarget.CONSOLE)
        logger_console = factory.get_or_create_logger(config_console)
        assert logger_console is not None

        # File target (with temp directory)
        temp_dir = Path("./temp_logs_sync")
        temp_dir.mkdir(exist_ok=True)
        config_file = LoggerConfig(
            name="test_file",
            output_target=OutputTarget.FILE,
            directory=temp_dir,
            filename="test.log",
        )
        logger_file = factory.get_or_create_logger(config_file)
        assert logger_file is not None

        # JSON target
        config_json = LoggerConfig(
            name="test_json",
            output_target=OutputTarget.JSON,
            directory=temp_dir,
            filename="test.json",
        )
        logger_json = factory.get_or_create_logger(config_json)
        assert logger_json is not None

        # Clean up - close all handlers first to release file locks
        import logging
        import shutil

        for logger_name in ["test_file", "test_json"]:
            logger = logging.getLogger(logger_name)
            for handler in logger.handlers[:]:
                if isinstance(handler, logging.FileHandler):
                    handler.close()
                    logger.removeHandler(handler)

        if temp_dir.exists():
            shutil.rmtree(temp_dir)
