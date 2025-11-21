"""Integration tests for JSON logging output."""

import json
import logging
import shutil
import tempfile
from pathlib import Path

import pytest

from miraveja_log.application import LoggerConfig, LoggerFactory
from miraveja_log.domain import LogLevel, OutputTarget
from miraveja_log.infrastructure.adapters import AsyncPythonLoggerAdapter, PythonLoggerAdapter


class TestJSONLogging:
    """Test JSON logging functionality with actual file I/O operations."""

    def setup_method(self) -> None:
        """Create temporary directory for test log files."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self) -> None:
        """Clean up temporary directory and log files."""
        # Close all file handlers to release locks
        for logger_name in logging.Logger.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            for handler in logger.handlers[:]:
                if isinstance(handler, logging.FileHandler):
                    handler.close()
                    logger.removeHandler(handler)

        # Remove temporary directory
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_json_logger_creates_log_file(self) -> None:
        """Test that JSON logger creates the log file."""
        log_file = "test_json_create.json"
        config = LoggerConfig(
            name="test_json_create",
            output_target=OutputTarget.JSON,
            directory=self.temp_dir,
            filename=log_file,
        )
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        logger.info("Test JSON message")

        log_path = self.temp_dir / log_file
        assert log_path.exists()
        assert log_path.is_file()

    def test_json_logger_writes_valid_json(self) -> None:
        """Test that JSON logger writes valid JSON format."""
        log_file = "test_json_valid.json"
        config = LoggerConfig(
            name="test_json_valid",
            output_target=OutputTarget.JSON,
            directory=self.temp_dir,
            filename=log_file,
        )
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        logger.info("Valid JSON test")

        # Flush the handler
        underlying_logger = logging.getLogger(config.name)
        for handler in underlying_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()

        log_path = self.temp_dir / log_file
        content = log_path.read_text()

        # Each line should be valid JSON
        for line in content.strip().split("\n"):
            if line:
                log_entry = json.loads(line)
                assert isinstance(log_entry, dict)

    def test_json_logger_includes_required_fields(self) -> None:
        """Test that JSON logger includes timestamp, level, name, and message."""
        log_file = "test_json_fields.json"
        config = LoggerConfig(
            name="test_json_fields",
            output_target=OutputTarget.JSON,
            directory=self.temp_dir,
            filename=log_file,
        )
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        test_message = "JSON fields test"
        logger.info(test_message)

        # Flush the handler
        underlying_logger = logging.getLogger(config.name)
        for handler in underlying_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()

        log_path = self.temp_dir / log_file
        content = log_path.read_text()
        log_entry = json.loads(content.strip())

        assert "timestamp" in log_entry
        assert "level" in log_entry
        assert "name" in log_entry
        assert "message" in log_entry
        assert log_entry["message"] == test_message
        assert log_entry["level"] == "INFO"
        assert log_entry["name"] == "test_json_fields"

    def test_json_logger_writes_multiple_json_lines(self) -> None:
        """Test that JSON logger writes multiple log entries as separate JSON lines."""
        log_file = "test_json_multiple.json"
        config = LoggerConfig(
            name="test_json_multiple",
            output_target=OutputTarget.JSON,
            directory=self.temp_dir,
            filename=log_file,
        )
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        messages = ["First JSON message", "Second JSON message", "Third JSON message"]
        for msg in messages:
            logger.info(msg)

        # Flush the handler
        underlying_logger = logging.getLogger(config.name)
        for handler in underlying_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()

        log_path = self.temp_dir / log_file
        content = log_path.read_text()
        lines = [line for line in content.strip().split("\n") if line]

        assert len(lines) == 3

        for i, line in enumerate(lines):
            log_entry = json.loads(line)
            assert log_entry["message"] == messages[i]

    def test_json_logger_respects_log_level(self) -> None:
        """Test that JSON logger respects log level filtering."""
        log_file = "test_json_level.json"
        config = LoggerConfig(
            name="test_json_level",
            output_target=OutputTarget.JSON,
            directory=self.temp_dir,
            filename=log_file,
            level=LogLevel.ERROR,
        )
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

        # Flush the handler
        underlying_logger = logging.getLogger(config.name)
        for handler in underlying_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()

        log_path = self.temp_dir / log_file
        content = log_path.read_text()
        lines = [line for line in content.strip().split("\n") if line]

        # Only ERROR and CRITICAL should be logged
        assert len(lines) == 2

        log_entry1 = json.loads(lines[0])
        log_entry2 = json.loads(lines[1])

        assert log_entry1["level"] == "ERROR"
        assert log_entry1["message"] == "Error message"
        assert log_entry2["level"] == "CRITICAL"
        assert log_entry2["message"] == "Critical message"

    def test_json_logger_with_extra_fields(self) -> None:
        """Test JSON logger merges extra fields at top level."""
        log_file = "test_json_extra.json"
        config = LoggerConfig(
            name="test_json_extra",
            output_target=OutputTarget.JSON,
            directory=self.temp_dir,
            filename=log_file,
        )
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        logger.info(
            "User action",
            extra={"user_id": "user456", "action": "purchase", "amount": 99.99},
        )

        # Flush the handler
        underlying_logger = logging.getLogger(config.name)
        for handler in underlying_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()

        log_path = self.temp_dir / log_file
        content = log_path.read_text()
        log_entry = json.loads(content.strip())

        assert log_entry["message"] == "User action"
        assert log_entry["user_id"] == "user456"
        assert log_entry["action"] == "purchase"
        assert log_entry["amount"] == 99.99

    def test_json_logger_with_exception_info(self) -> None:
        """Test JSON logger includes exception information."""
        log_file = "test_json_exception.json"
        config = LoggerConfig(
            name="test_json_exception",
            output_target=OutputTarget.JSON,
            directory=self.temp_dir,
            filename=log_file,
        )
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        try:
            raise ValueError("JSON test exception")
        except ValueError:
            logger.error("Exception in JSON", exc_info=True)

        # Flush the handler
        underlying_logger = logging.getLogger(config.name)
        for handler in underlying_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()

        log_path = self.temp_dir / log_file
        content = log_path.read_text()
        log_entry = json.loads(content.strip())

        assert log_entry["message"] == "Exception in JSON"
        assert "exception" in log_entry
        assert "ValueError: JSON test exception" in log_entry["exception"]
        assert "Traceback" in log_entry["exception"]

    def test_json_logger_with_nested_directory(self) -> None:
        """Test JSON logger creates nested directory structure."""
        nested_dir = self.temp_dir / "json_logs" / "app"
        log_file = "nested.json"
        config = LoggerConfig(
            name="test_json_nested",
            output_target=OutputTarget.JSON,
            directory=nested_dir,
            filename=log_file,
        )
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        logger.info("Nested JSON test")

        # Flush the handler
        underlying_logger = logging.getLogger(config.name)
        for handler in underlying_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()

        log_path = nested_dir / log_file
        assert log_path.exists()
        assert log_path.parent.exists()

        content = log_path.read_text()
        log_entry = json.loads(content.strip())
        assert log_entry["message"] == "Nested JSON test"

    def test_json_logger_with_complex_data_types(self) -> None:
        """Test JSON logger handles complex data types in extra fields."""
        log_file = "test_json_complex.json"
        config = LoggerConfig(
            name="test_json_complex",
            output_target=OutputTarget.JSON,
            directory=self.temp_dir,
            filename=log_file,
        )
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        logger.info(
            "Complex data",
            extra={
                "list_data": [1, 2, 3],
                "dict_data": {"key": "value", "nested": {"inner": "data"}},
                "bool_data": True,
                "null_data": None,
            },
        )

        # Flush the handler
        underlying_logger = logging.getLogger(config.name)
        for handler in underlying_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()

        log_path = self.temp_dir / log_file
        content = log_path.read_text()
        log_entry = json.loads(content.strip())

        assert log_entry["list_data"] == [1, 2, 3]
        assert log_entry["dict_data"]["key"] == "value"
        assert log_entry["dict_data"]["nested"]["inner"] == "data"
        assert log_entry["bool_data"] is True
        assert log_entry["null_data"] is None

    def test_json_logger_timestamp_is_iso_format(self) -> None:
        """Test that JSON logger timestamp is in ISO 8601 format."""
        log_file = "test_json_timestamp.json"
        config = LoggerConfig(
            name="test_json_timestamp",
            output_target=OutputTarget.JSON,
            directory=self.temp_dir,
            filename=log_file,
        )
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        logger.info("Timestamp test")

        # Flush the handler
        underlying_logger = logging.getLogger(config.name)
        for handler in underlying_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()

        log_path = self.temp_dir / log_file
        content = log_path.read_text()
        log_entry = json.loads(content.strip())

        # Timestamp should be parseable as ISO format
        from datetime import datetime

        timestamp = log_entry["timestamp"]
        parsed = datetime.fromisoformat(timestamp)
        assert parsed is not None

    def test_json_logger_with_unicode_characters(self) -> None:
        """Test JSON logger handles unicode characters correctly."""
        log_file = "test_json_unicode.json"
        config = LoggerConfig(
            name="test_json_unicode",
            output_target=OutputTarget.JSON,
            directory=self.temp_dir,
            filename=log_file,
        )
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        unicode_msg = "Hello 世界 🌍 Ω ñ"
        logger.info(unicode_msg)

        # Flush the handler
        underlying_logger = logging.getLogger(config.name)
        for handler in underlying_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()

        log_path = self.temp_dir / log_file
        content = log_path.read_text(encoding="utf-8")
        log_entry = json.loads(content.strip())

        assert log_entry["message"] == unicode_msg

    def test_multiple_json_loggers_different_files(self) -> None:
        """Test multiple JSON loggers write to different files."""
        log_file1 = "test_json_multi_1.json"
        log_file2 = "test_json_multi_2.json"

        config1 = LoggerConfig(
            name="test_json_multi_1",
            output_target=OutputTarget.JSON,
            directory=self.temp_dir,
            filename=log_file1,
        )
        config2 = LoggerConfig(
            name="test_json_multi_2",
            output_target=OutputTarget.JSON,
            directory=self.temp_dir,
            filename=log_file2,
        )
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)

        logger1 = factory.get_or_create_logger(config1)
        logger2 = factory.get_or_create_logger(config2)

        logger1.info("JSON logger 1 message")
        logger2.info("JSON logger 2 message")

        # Flush handlers
        for config in [config1, config2]:
            underlying_logger = logging.getLogger(config.name)
            for handler in underlying_logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    handler.flush()

        log_path1 = self.temp_dir / log_file1
        log_path2 = self.temp_dir / log_file2

        content1 = log_path1.read_text()
        content2 = log_path2.read_text()

        log_entry1 = json.loads(content1.strip())
        log_entry2 = json.loads(content2.strip())

        assert log_entry1["message"] == "JSON logger 1 message"
        assert log_entry2["message"] == "JSON logger 2 message"

    @pytest.mark.asyncio
    async def test_json_logger_async_variant(self) -> None:
        """Test async JSON logger functionality."""
        log_file = "test_json_async.json"
        config = LoggerConfig(
            name="test_json_async",
            output_target=OutputTarget.JSON,
            directory=self.temp_dir,
            filename=log_file,
        )
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_async_logger(config)

        await logger.info("Async JSON message")

        # Flush the handler
        underlying_logger = logging.getLogger(config.name)
        for handler in underlying_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()

        log_path = self.temp_dir / log_file
        content = log_path.read_text()
        log_entry = json.loads(content.strip())

        assert log_entry["message"] == "Async JSON message"
