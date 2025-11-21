"""Unit tests for testing utilities."""

import logging

import pytest

from miraveja_log.domain import ILogger
from miraveja_log.infrastructure.testing.test_utilities import MemoryHandler, MockLogger


class TestMemoryHandler:
    """Test MemoryHandler functionality."""

    def test_memory_handler_can_be_instantiated(self) -> None:
        """Test that MemoryHandler can be created."""
        handler = MemoryHandler()
        assert handler is not None

    def test_memory_handler_inherits_from_logging_handler(self) -> None:
        """Test that MemoryHandler inherits from logging.Handler."""
        handler = MemoryHandler()
        assert isinstance(handler, logging.Handler)

    def test_memory_handler_initializes_with_empty_records(self) -> None:
        """Test that MemoryHandler starts with no records."""
        handler = MemoryHandler()
        assert len(handler.records) == 0

    def test_memory_handler_emit_stores_record(self) -> None:
        """Test that emit stores log records."""
        handler = MemoryHandler()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        assert len(handler.records) == 1
        assert handler.records[0] is record

    def test_memory_handler_stores_multiple_records(self) -> None:
        """Test that multiple records are stored."""
        handler = MemoryHandler()

        for i in range(3):
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="test.py",
                lineno=1,
                msg=f"Message {i}",
                args=(),
                exc_info=None,
            )
            handler.emit(record)

        assert len(handler.records) == 3

    def test_memory_handler_clear_removes_all_records(self) -> None:
        """Test that clear removes all stored records."""
        handler = MemoryHandler()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        handler.emit(record)

        handler.clear()

        assert len(handler.records) == 0

    def test_memory_handler_get_messages_returns_formatted_messages(self) -> None:
        """Test that get_messages returns formatted log messages."""
        handler = MemoryHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        handler.emit(record)

        messages = handler.get_messages()

        assert len(messages) == 1
        assert "INFO: Test message" in messages[0]

    def test_memory_handler_get_messages_with_multiple_records(self) -> None:
        """Test get_messages with multiple records."""
        handler = MemoryHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))

        for i in range(3):
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="test.py",
                lineno=1,
                msg=f"Message {i}",
                args=(),
                exc_info=None,
            )
            handler.emit(record)

        messages = handler.get_messages()

        assert len(messages) == 3
        assert messages[0] == "Message 0"
        assert messages[1] == "Message 1"
        assert messages[2] == "Message 2"


class TestMockLogger:
    """Test MockLogger functionality."""

    def test_mock_logger_can_be_instantiated(self) -> None:
        """Test that MockLogger can be created."""
        logger = MockLogger()
        assert logger is not None

    def test_mock_logger_implements_ilogger(self) -> None:
        """Test that MockLogger implements ILogger interface."""
        logger = MockLogger()
        assert isinstance(logger, ILogger)

    def test_mock_logger_initializes_with_empty_calls(self) -> None:
        """Test that MockLogger starts with no calls."""
        logger = MockLogger()
        assert len(logger.calls) == 0

    def test_mock_logger_debug_records_call(self) -> None:
        """Test that debug method records the call."""
        logger = MockLogger()
        logger.debug("Debug message")

        assert len(logger.calls) == 1
        level, message, args, kwargs = logger.calls[0]
        assert level == "debug"
        assert message == "Debug message"

    def test_mock_logger_info_records_call(self) -> None:
        """Test that info method records the call."""
        logger = MockLogger()
        logger.info("Info message")

        assert len(logger.calls) == 1
        level, message, args, kwargs = logger.calls[0]
        assert level == "info"
        assert message == "Info message"

    def test_mock_logger_warning_records_call(self) -> None:
        """Test that warning method records the call."""
        logger = MockLogger()
        logger.warning("Warning message")

        assert len(logger.calls) == 1
        level, message, args, kwargs = logger.calls[0]
        assert level == "warning"
        assert message == "Warning message"

    def test_mock_logger_error_records_call(self) -> None:
        """Test that error method records the call."""
        logger = MockLogger()
        logger.error("Error message")

        assert len(logger.calls) == 1
        level, message, args, kwargs = logger.calls[0]
        assert level == "error"
        assert message == "Error message"

    def test_mock_logger_critical_records_call(self) -> None:
        """Test that critical method records the call."""
        logger = MockLogger()
        logger.critical("Critical message")

        assert len(logger.calls) == 1
        level, message, args, kwargs = logger.calls[0]
        assert level == "critical"
        assert message == "Critical message"

    def test_mock_logger_records_args(self) -> None:
        """Test that MockLogger records positional arguments."""
        logger = MockLogger()
        logger.info("Message: %s", "value")

        level, message, args, kwargs = logger.calls[0]
        assert args == ("value",)

    def test_mock_logger_records_kwargs(self) -> None:
        """Test that MockLogger records keyword arguments."""
        logger = MockLogger()
        logger.info("Message", extra={"user_id": "123"})

        level, message, args, kwargs = logger.calls[0]
        assert "extra" in kwargs
        assert kwargs["extra"] == {"user_id": "123"}

    def test_mock_logger_clear_removes_all_calls(self) -> None:
        """Test that clear removes all recorded calls."""
        logger = MockLogger()
        logger.info("Message 1")
        logger.debug("Message 2")

        logger.clear()

        assert len(logger.calls) == 0

    def test_mock_logger_get_messages_returns_all_messages(self) -> None:
        """Test that get_messages returns all messages."""
        logger = MockLogger()
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")

        messages = logger.get_messages()

        assert len(messages) == 3
        assert "Debug message" in messages
        assert "Info message" in messages
        assert "Warning message" in messages

    def test_mock_logger_get_messages_filters_by_level(self) -> None:
        """Test that get_messages can filter by level."""
        logger = MockLogger()
        logger.debug("Debug message")
        logger.info("Info message 1")
        logger.info("Info message 2")
        logger.warning("Warning message")

        info_messages = logger.get_messages(level="info")

        assert len(info_messages) == 2
        assert "Info message 1" in info_messages
        assert "Info message 2" in info_messages

    def test_mock_logger_get_messages_with_nonexistent_level(self) -> None:
        """Test get_messages with a level that has no messages."""
        logger = MockLogger()
        logger.info("Info message")

        critical_messages = logger.get_messages(level="critical")

        assert len(critical_messages) == 0

    def test_mock_logger_records_multiple_calls(self) -> None:
        """Test that MockLogger records multiple calls in order."""
        logger = MockLogger()
        logger.debug("First")
        logger.info("Second")
        logger.error("Third")

        assert len(logger.calls) == 3
        assert logger.calls[0][1] == "First"
        assert logger.calls[1][1] == "Second"
        assert logger.calls[2][1] == "Third"
