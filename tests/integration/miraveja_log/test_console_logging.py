"""Integration tests for console logging output."""

import logging
import sys
from io import StringIO

import pytest

from miraveja_log.application import LoggerConfig, LoggerFactory
from miraveja_log.domain import LogLevel, OutputTarget
from miraveja_log.infrastructure.adapters import AsyncPythonLoggerAdapter, PythonLoggerAdapter
from miraveja_log.infrastructure.testing import MemoryHandler


class TestConsoleLogging:
    """Test console logging functionality with various configurations."""

    def test_console_logger_logs_to_console_target(self) -> None:
        """Test that console logger is configured with console target."""
        config = LoggerConfig(name="test_console_basic", output_target=OutputTarget.CONSOLE)
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        # Verify logger was created
        assert logger is not None

        # Verify underlying logger has a StreamHandler
        underlying_logger = logging.getLogger(config.name)
        handlers = underlying_logger.handlers
        assert any(isinstance(h, logging.StreamHandler) for h in handlers)

    def test_console_logger_uses_default_text_format(self) -> None:
        """Test that console logger uses text formatter by default."""
        config = LoggerConfig(name="test_console_format", output_target=OutputTarget.CONSOLE)
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        # Add memory handler to verify format
        memory_handler = MemoryHandler()
        # Copy formatter from the console handler to memory handler
        underlying_logger = logging.getLogger(config.name)
        if underlying_logger.handlers:
            memory_handler.setFormatter(underlying_logger.handlers[0].formatter)
        underlying_logger.addHandler(memory_handler)

        logger.info("Test console message")

        messages = memory_handler.get_messages()
        assert len(messages) == 1
        # Default format includes timestamp, name, level, and message
        # Format: %(asctime)s - %(name)s - %(levelname)s - %(message)s
        message = messages[0]
        assert "INFO" in message
        assert "Test console message" in message
        # Verify format structure (timestamp - name - level - message)
        assert " - " in message

        # Clean up
        underlying_logger.removeHandler(memory_handler)

    def test_console_logger_with_custom_format(self) -> None:
        """Test console logger with custom log format."""
        custom_format = "%(levelname)s - %(message)s"
        config = LoggerConfig(
            name="test_console_custom_format",
            output_target=OutputTarget.CONSOLE,
            log_format=custom_format,
        )
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        # Add memory handler with custom format
        memory_handler = MemoryHandler()
        memory_handler.setFormatter(logging.Formatter(custom_format))
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        logger.info("Custom format message")

        messages = memory_handler.get_messages()
        assert len(messages) == 1
        assert messages[0] == "INFO - Custom format message"

        # Clean up
        underlying_logger.removeHandler(memory_handler)

    def test_console_logger_with_different_log_levels(self) -> None:
        """Test console logger respects different log levels."""
        for level in [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]:
            config = LoggerConfig(
                name=f"test_console_{level.lower()}",
                output_target=OutputTarget.CONSOLE,
                level=level,
            )
            factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
            logger = factory.get_or_create_logger(config)

            # Add memory handler
            memory_handler = MemoryHandler()
            underlying_logger = logging.getLogger(config.name)
            underlying_logger.addHandler(memory_handler)

            # Log at all levels
            logger.debug("Debug")
            logger.info("Info")
            logger.warning("Warning")
            logger.error("Error")
            logger.critical("Critical")

            messages = memory_handler.get_messages()

            # Verify correct filtering based on level
            if level == LogLevel.DEBUG:
                assert len(messages) == 5
            elif level == LogLevel.INFO:
                assert len(messages) == 4
            elif level == LogLevel.WARNING:
                assert len(messages) == 3
            elif level == LogLevel.ERROR:
                assert len(messages) == 2
            elif level == LogLevel.CRITICAL:
                assert len(messages) == 1

            # Clean up
            underlying_logger.removeHandler(memory_handler)
            factory.clear_cache()

    def test_console_logger_with_structured_logging(self) -> None:
        """Test console logger with extra fields."""
        config = LoggerConfig(name="test_console_structured", output_target=OutputTarget.CONSOLE)
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        # Add memory handler
        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        logger.info("User action", extra={"user_id": "789", "ip": "192.168.1.1"})

        records = memory_handler.records
        assert len(records) == 1
        assert hasattr(records[0], "user_id")
        assert records[0].user_id == "789"
        assert records[0].ip == "192.168.1.1"

        # Clean up
        underlying_logger.removeHandler(memory_handler)

    def test_console_logger_with_exception_logging(self) -> None:
        """Test console logger captures exception tracebacks."""
        config = LoggerConfig(name="test_console_exception", output_target=OutputTarget.CONSOLE)
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        # Add memory handler
        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        try:
            raise RuntimeError("Console test error")
        except RuntimeError:
            logger.error("Exception caught", exc_info=True)

        messages = memory_handler.get_messages()
        assert len(messages) == 1
        assert "Exception caught" in messages[0]
        assert "RuntimeError: Console test error" in messages[0]
        assert "Traceback" in messages[0]

        # Clean up
        underlying_logger.removeHandler(memory_handler)

    def test_console_logger_with_multiline_message(self) -> None:
        """Test console logger with multiline log messages."""
        config = LoggerConfig(name="test_console_multiline", output_target=OutputTarget.CONSOLE)
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        # Add memory handler
        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        multiline_msg = "Line 1\nLine 2\nLine 3"
        logger.info(multiline_msg)

        messages = memory_handler.get_messages()
        assert len(messages) == 1
        assert "Line 1" in messages[0]
        assert "Line 2" in messages[0]
        assert "Line 3" in messages[0]

        # Clean up
        underlying_logger.removeHandler(memory_handler)

    def test_console_logger_with_unicode_characters(self) -> None:
        """Test console logger handles unicode characters correctly."""
        config = LoggerConfig(name="test_console_unicode", output_target=OutputTarget.CONSOLE)
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        # Add memory handler
        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        unicode_msg = "Hello 世界 🌍 Ω"
        logger.info(unicode_msg)

        messages = memory_handler.get_messages()
        assert len(messages) == 1
        assert unicode_msg in messages[0]

        # Clean up
        underlying_logger.removeHandler(memory_handler)

    def test_console_logger_with_formatted_string(self) -> None:
        """Test console logger with string formatting."""
        config = LoggerConfig(name="test_console_formatted", output_target=OutputTarget.CONSOLE)
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        # Add memory handler
        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        logger.info("User %s performed %d actions", "alice", 42)

        messages = memory_handler.get_messages()
        assert len(messages) == 1
        assert "User alice performed 42 actions" in messages[0]

        # Clean up
        underlying_logger.removeHandler(memory_handler)

    def test_multiple_console_loggers_independent(self) -> None:
        """Test that multiple console loggers work independently."""
        config1 = LoggerConfig(name="test_console_multi_1", output_target=OutputTarget.CONSOLE)
        config2 = LoggerConfig(name="test_console_multi_2", output_target=OutputTarget.CONSOLE)
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)

        logger1 = factory.get_or_create_logger(config1)
        logger2 = factory.get_or_create_logger(config2)

        # Add separate memory handlers
        handler1 = MemoryHandler()
        handler2 = MemoryHandler()
        logging.getLogger(config1.name).addHandler(handler1)
        logging.getLogger(config2.name).addHandler(handler2)

        logger1.info("Message from logger 1")
        logger2.info("Message from logger 2")

        messages1 = handler1.get_messages()
        messages2 = handler2.get_messages()

        assert len(messages1) == 1
        assert len(messages2) == 1
        assert "Message from logger 1" in messages1[0]
        assert "Message from logger 2" in messages2[0]

        # Clean up
        logging.getLogger(config1.name).removeHandler(handler1)
        logging.getLogger(config2.name).removeHandler(handler2)

    @pytest.mark.asyncio
    async def test_console_logger_async_variant(self) -> None:
        """Test async console logger functionality."""
        config = LoggerConfig(name="test_console_async", output_target=OutputTarget.CONSOLE)
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_async_logger(config)

        # Add memory handler
        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        await logger.info("Async console message")

        messages = memory_handler.get_messages()
        assert len(messages) == 1
        assert "Async console message" in messages[0]

        # Clean up
        underlying_logger.removeHandler(memory_handler)
