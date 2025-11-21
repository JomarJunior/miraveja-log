"""Unit tests for JSON formatter."""

import json
import logging
from datetime import datetime

import pytest

from miraveja_log.infrastructure.formatters.json_formatter import JSONFormatter


class TestJSONFormatterBasics:
    """Test basic JSONFormatter functionality."""

    def test_json_formatter_can_be_instantiated(self) -> None:
        """Test that JSONFormatter can be created."""
        formatter = JSONFormatter()
        assert formatter is not None

    def test_json_formatter_inherits_from_logging_formatter(self) -> None:
        """Test that JSONFormatter inherits from logging.Formatter."""
        formatter = JSONFormatter()
        assert isinstance(formatter, logging.Formatter)

    def test_json_formatter_with_custom_format(self) -> None:
        """Test that JSONFormatter can be created with custom format."""
        formatter = JSONFormatter(fmt="%(levelname)s: %(message)s")
        assert formatter is not None

    def test_json_formatter_with_custom_datefmt(self) -> None:
        """Test that JSONFormatter can be created with custom date format."""
        formatter = JSONFormatter(datefmt="%Y-%m-%d")
        assert formatter is not None


class TestJSONFormatterFormat:
    """Test JSONFormatter.format() method."""

    def test_format_returns_valid_json_string(self) -> None:
        """Test that format returns a valid JSON string."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        # Should be valid JSON
        json_data = json.loads(result)
        assert isinstance(json_data, dict)

    def test_format_includes_timestamp(self) -> None:
        """Test that formatted output includes timestamp."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        json_data = json.loads(result)

        assert "timestamp" in json_data
        # Verify it's a valid ISO format timestamp
        datetime.fromisoformat(json_data["timestamp"])

    def test_format_includes_level(self) -> None:
        """Test that formatted output includes log level."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.WARNING,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        json_data = json.loads(result)

        assert "level" in json_data
        assert json_data["level"] == "WARNING"

    def test_format_includes_logger_name(self) -> None:
        """Test that formatted output includes logger name."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="my_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        json_data = json.loads(result)

        assert "name" in json_data
        assert json_data["name"] == "my_logger"

    def test_format_includes_message(self) -> None:
        """Test that formatted output includes log message."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Hello, World!",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        json_data = json.loads(result)

        assert "message" in json_data
        assert json_data["message"] == "Hello, World!"


class TestJSONFormatterExtraFields:
    """Test JSONFormatter handling of extra fields."""

    def test_format_merges_extra_fields_at_top_level(self) -> None:
        """Test that extra fields are merged at top level."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        # Add extra fields as record attributes (how logging.extra actually works)
        record.user_id = "123"  # type: ignore
        record.request_id = "abc"  # type: ignore

        result = formatter.format(record)
        json_data = json.loads(result)

        assert "user_id" in json_data
        assert json_data["user_id"] == "123"
        assert "request_id" in json_data
        assert json_data["request_id"] == "abc"

    def test_format_without_extra_fields(self) -> None:
        """Test that format works without extra fields."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        json_data = json.loads(result)

        # Should have basic fields only
        assert "timestamp" in json_data
        assert "level" in json_data
        assert "name" in json_data
        assert "message" in json_data


class TestJSONFormatterExceptionHandling:
    """Test JSONFormatter exception handling."""

    def test_format_includes_exception_info_when_present(self) -> None:
        """Test that format includes exception info when available."""
        formatter = JSONFormatter()

        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys

            exc_info = sys.exc_info()
            record = logging.LogRecord(
                name="test_logger",
                level=logging.ERROR,
                pathname="test.py",
                lineno=1,
                msg="An error occurred",
                args=(),
                exc_info=exc_info,
            )

            result = formatter.format(record)
            json_data = json.loads(result)

            assert "exception" in json_data
            assert "ValueError" in json_data["exception"]
            assert "Test exception" in json_data["exception"]

    def test_format_without_exception_info(self) -> None:
        """Test that format works without exception info."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        json_data = json.loads(result)

        assert "exc_info" not in json_data


class TestJSONFormatterDifferentLogLevels:
    """Test JSONFormatter with different log levels."""

    def test_format_debug_level(self) -> None:
        """Test format with DEBUG level."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.DEBUG,
            pathname="test.py",
            lineno=1,
            msg="Debug message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        json_data = json.loads(result)

        assert json_data["level"] == "DEBUG"
        assert json_data["message"] == "Debug message"

    def test_format_info_level(self) -> None:
        """Test format with INFO level."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Info message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        json_data = json.loads(result)

        assert json_data["level"] == "INFO"

    def test_format_warning_level(self) -> None:
        """Test format with WARNING level."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.WARNING,
            pathname="test.py",
            lineno=1,
            msg="Warning message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        json_data = json.loads(result)

        assert json_data["level"] == "WARNING"

    def test_format_error_level(self) -> None:
        """Test format with ERROR level."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Error message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        json_data = json.loads(result)

        assert json_data["level"] == "ERROR"

    def test_format_critical_level(self) -> None:
        """Test format with CRITICAL level."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.CRITICAL,
            pathname="test.py",
            lineno=1,
            msg="Critical message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        json_data = json.loads(result)

        assert json_data["level"] == "CRITICAL"


class TestJSONFormatterEdgeCases:
    """Test edge cases and special scenarios."""

    def test_format_with_empty_message(self) -> None:
        """Test format with empty message."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        json_data = json.loads(result)

        assert json_data["message"] == ""

    def test_format_with_multiline_message(self) -> None:
        """Test format with multiline message."""
        formatter = JSONFormatter()
        message = "Line 1\nLine 2\nLine 3"
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg=message,
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        json_data = json.loads(result)

        assert json_data["message"] == message

    def test_format_with_special_characters_in_message(self) -> None:
        """Test format with special characters."""
        formatter = JSONFormatter()
        message = "Special chars: \"quotes\", 'apostrophes', \\backslash"
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg=message,
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        json_data = json.loads(result)

        assert json_data["message"] == message

    def test_format_timestamp_is_iso_format(self) -> None:
        """Test that timestamp is in ISO format."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        json_data = json.loads(result)

        # Should be able to parse as ISO format
        timestamp = datetime.fromisoformat(json_data["timestamp"])
        assert isinstance(timestamp, datetime)
