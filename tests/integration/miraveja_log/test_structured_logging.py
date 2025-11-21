"""Integration tests for structured logging with extra fields and context."""

import json
import logging
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest

from miraveja_log.application import LoggerConfig, LoggerFactory
from miraveja_log.domain import LogLevel, OutputTarget
from miraveja_log.infrastructure.adapters import AsyncPythonLoggerAdapter, PythonLoggerAdapter
from miraveja_log.infrastructure.testing import MemoryHandler


class TestStructuredLogging:
    """Test structured logging with extra fields, context, and metadata."""

    def test_structured_logging_with_simple_extra_fields(self) -> None:
        """Test logging with simple extra fields."""
        config = LoggerConfig(name="test_structured_simple")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        logger.info("User logged in", extra={"user_id": "12345", "ip": "192.168.1.1"})

        records = memory_handler.records
        assert len(records) == 1
        assert hasattr(records[0], "user_id")
        assert records[0].user_id == "12345"
        assert records[0].ip == "192.168.1.1"

        underlying_logger.removeHandler(memory_handler)

    def test_structured_logging_with_nested_dict(self) -> None:
        """Test logging with nested dictionary in extra fields."""
        config = LoggerConfig(name="test_structured_nested")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        logger.info(
            "Transaction processed",
            extra={
                "transaction": {"id": "TXN-123", "amount": 99.99, "currency": "USD"},
                "status": "success",
            },
        )

        records = memory_handler.records
        assert len(records) == 1
        assert hasattr(records[0], "transaction")
        assert records[0].transaction["id"] == "TXN-123"
        assert records[0].status == "success"

        underlying_logger.removeHandler(memory_handler)

    def test_structured_logging_with_list_data(self) -> None:
        """Test logging with list data in extra fields."""
        config = LoggerConfig(name="test_structured_list")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        logger.info("Items processed", extra={"items": ["item1", "item2", "item3"], "count": 3})

        records = memory_handler.records
        assert len(records) == 1
        assert records[0].items == ["item1", "item2", "item3"]
        assert records[0].count == 3

        underlying_logger.removeHandler(memory_handler)

    def test_structured_logging_with_boolean_and_null_values(self) -> None:
        """Test logging with boolean and null values in extra fields."""
        config = LoggerConfig(name="test_structured_types")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        logger.info(
            "State update",
            extra={"is_active": True, "is_verified": False, "optional_field": None},
        )

        records = memory_handler.records
        assert len(records) == 1
        assert records[0].is_active is True
        assert records[0].is_verified is False
        assert records[0].optional_field is None

        underlying_logger.removeHandler(memory_handler)

    def test_structured_logging_with_numeric_types(self) -> None:
        """Test logging with various numeric types in extra fields."""
        config = LoggerConfig(name="test_structured_numbers")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        logger.info(
            "Metrics captured",
            extra={
                "int_value": 42,
                "float_value": 3.14159,
                "negative": -100,
                "large_number": 1_000_000,
            },
        )

        records = memory_handler.records
        assert len(records) == 1
        assert records[0].int_value == 42
        assert records[0].float_value == 3.14159
        assert records[0].negative == -100
        assert records[0].large_number == 1_000_000

        underlying_logger.removeHandler(memory_handler)

    def test_structured_logging_json_output_merges_fields(self) -> None:
        """Test that JSON output merges extra fields at top level."""
        temp_dir = Path(tempfile.mkdtemp())
        log_file = "structured.json"

        try:
            config = LoggerConfig(
                name="test_structured_json",
                output_target=OutputTarget.JSON,
                directory=temp_dir,
                filename=log_file,
            )
            factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
            logger = factory.get_or_create_logger(config)

            logger.info(
                "API request",
                extra={
                    "method": "POST",
                    "endpoint": "/api/users",
                    "status_code": 201,
                    "response_time_ms": 145,
                },
            )

            # Flush handler
            underlying_logger = logging.getLogger(config.name)
            for handler in underlying_logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    handler.flush()

            log_path = temp_dir / log_file
            content = log_path.read_text()
            log_entry = json.loads(content.strip())

            # Extra fields should be at top level
            assert log_entry["message"] == "API request"
            assert log_entry["method"] == "POST"
            assert log_entry["endpoint"] == "/api/users"
            assert log_entry["status_code"] == 201
            assert log_entry["response_time_ms"] == 145

        finally:
            # Clean up
            for handler in logging.getLogger(config.name).handlers[:]:
                if isinstance(handler, logging.FileHandler):
                    handler.close()
                    logging.getLogger(config.name).removeHandler(handler)
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    def test_structured_logging_multiple_calls_with_different_context(self) -> None:
        """Test multiple log calls with different context data."""
        config = LoggerConfig(name="test_structured_multiple_context")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        logger.info("User action", extra={"action": "login", "user_id": "user1"})
        logger.info("User action", extra={"action": "logout", "user_id": "user2"})
        logger.info("User action", extra={"action": "purchase", "user_id": "user3", "amount": 50.0})

        records = memory_handler.records
        assert len(records) == 3
        assert records[0].action == "login"
        assert records[1].action == "logout"
        assert records[2].action == "purchase"
        assert records[2].amount == 50.0

        underlying_logger.removeHandler(memory_handler)

    def test_structured_logging_with_complex_nested_structure(self) -> None:
        """Test logging with deeply nested data structures."""
        config = LoggerConfig(name="test_structured_complex")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        complex_data = {
            "request": {
                "headers": {"content-type": "application/json", "authorization": "Bearer token"},
                "body": {"username": "john", "settings": {"theme": "dark", "notifications": True}},
            },
            "metadata": {"timestamp": "2025-11-20", "version": "1.0"},
        }

        logger.info("Complex request", extra=complex_data)

        records = memory_handler.records
        assert len(records) == 1
        assert records[0].request["headers"]["content-type"] == "application/json"
        assert records[0].request["body"]["settings"]["theme"] == "dark"
        assert records[0].metadata["version"] == "1.0"

        underlying_logger.removeHandler(memory_handler)

    def test_structured_logging_with_empty_extra_dict(self) -> None:
        """Test logging with empty extra dictionary."""
        config = LoggerConfig(name="test_structured_empty")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        logger.info("Message without extra", extra={})

        records = memory_handler.records
        assert len(records) == 1
        assert records[0].getMessage() == "Message without extra"

        underlying_logger.removeHandler(memory_handler)

    def test_structured_logging_without_extra_parameter(self) -> None:
        """Test logging without extra parameter (standard logging)."""
        config = LoggerConfig(name="test_structured_no_extra")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        logger.info("Standard log message")

        records = memory_handler.records
        assert len(records) == 1
        assert records[0].getMessage() == "Standard log message"

        underlying_logger.removeHandler(memory_handler)

    def test_structured_logging_with_string_formatting_and_extra(self) -> None:
        """Test logging with both string formatting and extra fields."""
        config = LoggerConfig(name="test_structured_formatting")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        logger.info("User %s performed %s", "alice", "login", extra={"timestamp": "2025-11-20"})

        records = memory_handler.records
        assert len(records) == 1
        assert "alice" in records[0].getMessage()
        assert "login" in records[0].getMessage()
        assert records[0].timestamp == "2025-11-20"

        underlying_logger.removeHandler(memory_handler)

    @pytest.mark.asyncio
    async def test_structured_logging_async_logger(self) -> None:
        """Test structured logging with async logger."""
        config = LoggerConfig(name="test_structured_async")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_async_logger(config)

        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        await logger.info(
            "Async operation completed",
            extra={"operation_id": "OP-456", "duration_ms": 250, "success": True},
        )

        records = memory_handler.records
        assert len(records) == 1
        assert records[0].operation_id == "OP-456"
        assert records[0].duration_ms == 250
        assert records[0].success is True

        underlying_logger.removeHandler(memory_handler)

    def test_structured_logging_preserves_field_names_with_special_chars(self) -> None:
        """Test that field names with special characters are preserved."""
        config = LoggerConfig(name="test_structured_special_chars")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        logger.info(
            "Special fields",
            extra={"user-id": "123", "request_id": "456", "trace.id": "789"},
        )

        records = memory_handler.records
        assert len(records) == 1
        # Access with dict-style access for special characters
        assert hasattr(records[0], "user-id") or "user-id" in records[0].__dict__
        assert hasattr(records[0], "request_id")

        underlying_logger.removeHandler(memory_handler)

    def test_structured_logging_with_unicode_in_extra_fields(self) -> None:
        """Test structured logging with unicode characters in extra fields."""
        config = LoggerConfig(name="test_structured_unicode")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        logger.info("International user", extra={"user_name": "José García", "city": "São Paulo 🇧🇷"})

        records = memory_handler.records
        assert len(records) == 1
        assert records[0].user_name == "José García"
        assert records[0].city == "São Paulo 🇧🇷"

        underlying_logger.removeHandler(memory_handler)

    def test_structured_logging_context_preserved_across_levels(self) -> None:
        """Test that different log levels can have different context."""
        config = LoggerConfig(name="test_structured_levels", level=LogLevel.DEBUG)
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        memory_handler = MemoryHandler()
        underlying_logger = logging.getLogger(config.name)
        underlying_logger.addHandler(memory_handler)

        logger.debug("Debug info", extra={"component": "auth", "line": 42})
        logger.info("Info message", extra={"component": "api", "endpoint": "/users"})
        logger.error("Error occurred", extra={"component": "database", "error_code": "DB001"})

        records = memory_handler.records
        assert len(records) == 3
        assert records[0].component == "auth"
        assert records[1].endpoint == "/users"
        assert records[2].error_code == "DB001"

        underlying_logger.removeHandler(memory_handler)
