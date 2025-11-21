"""Integration tests for file logging output."""

import logging
import shutil
import tempfile
from pathlib import Path

import pytest

from miraveja_log.application import LoggerConfig, LoggerFactory
from miraveja_log.domain import LogLevel, OutputTarget
from miraveja_log.infrastructure.adapters import AsyncPythonLoggerAdapter, PythonLoggerAdapter


class TestFileLogging:
    """Test file logging functionality with actual file I/O operations."""

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

    def test_file_logger_creates_log_file(self) -> None:
        """Test that file logger creates the log file."""
        log_file = "test_create.log"
        config = LoggerConfig(
            name="test_file_create",
            output_target=OutputTarget.FILE,
            directory=self.temp_dir,
            filename=log_file,
        )
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        logger.info("Test message")

        log_path = self.temp_dir / log_file
        assert log_path.exists()
        assert log_path.is_file()

    def test_file_logger_writes_log_messages(self) -> None:
        """Test that file logger writes messages to file."""
        log_file = "test_write.log"
        config = LoggerConfig(
            name="test_file_write",
            output_target=OutputTarget.FILE,
            directory=self.temp_dir,
            filename=log_file,
        )
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        test_message = "This is a test log message"
        logger.info(test_message)

        # Flush the handler
        underlying_logger = logging.getLogger(config.name)
        for handler in underlying_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()

        log_path = self.temp_dir / log_file
        content = log_path.read_text()
        assert test_message in content

    def test_file_logger_writes_multiple_messages(self) -> None:
        """Test that file logger writes multiple messages in sequence."""
        log_file = "test_multiple.log"
        config = LoggerConfig(
            name="test_file_multiple",
            output_target=OutputTarget.FILE,
            directory=self.temp_dir,
            filename=log_file,
        )
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        messages = ["First message", "Second message", "Third message"]
        for msg in messages:
            logger.info(msg)

        # Flush the handler
        underlying_logger = logging.getLogger(config.name)
        for handler in underlying_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()

        log_path = self.temp_dir / log_file
        content = log_path.read_text()
        for msg in messages:
            assert msg in content

    def test_file_logger_respects_log_level(self) -> None:
        """Test that file logger respects log level filtering."""
        log_file = "test_level_filter.log"
        config = LoggerConfig(
            name="test_file_level",
            output_target=OutputTarget.FILE,
            directory=self.temp_dir,
            filename=log_file,
            level=LogLevel.WARNING,
        )
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        # Flush the handler
        underlying_logger = logging.getLogger(config.name)
        for handler in underlying_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()

        log_path = self.temp_dir / log_file
        content = log_path.read_text()

        assert "Debug message" not in content
        assert "Info message" not in content
        assert "Warning message" in content
        assert "Error message" in content

    def test_file_logger_with_custom_format(self) -> None:
        """Test file logger with custom log format."""
        log_file = "test_custom_format.log"
        custom_format = "%(levelname)s | %(message)s"
        config = LoggerConfig(
            name="test_file_format",
            output_target=OutputTarget.FILE,
            directory=self.temp_dir,
            filename=log_file,
            log_format=custom_format,
        )
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        logger.info("Custom format test")

        # Flush the handler
        underlying_logger = logging.getLogger(config.name)
        for handler in underlying_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()

        log_path = self.temp_dir / log_file
        content = log_path.read_text()
        assert "INFO | Custom format test" in content

    def test_file_logger_with_exception_info(self) -> None:
        """Test file logger captures exception tracebacks."""
        log_file = "test_exception.log"
        config = LoggerConfig(
            name="test_file_exception",
            output_target=OutputTarget.FILE,
            directory=self.temp_dir,
            filename=log_file,
        )
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        try:
            raise ValueError("Test file exception")
        except ValueError:
            logger.error("Exception occurred", exc_info=True)

        # Flush the handler
        underlying_logger = logging.getLogger(config.name)
        for handler in underlying_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()

        log_path = self.temp_dir / log_file
        content = log_path.read_text()
        assert "Exception occurred" in content
        assert "ValueError: Test file exception" in content
        assert "Traceback" in content

    def test_file_logger_with_nested_directory(self) -> None:
        """Test file logger creates nested directory structure."""
        nested_dir = self.temp_dir / "logs" / "app" / "debug"
        log_file = "nested.log"
        config = LoggerConfig(
            name="test_file_nested",
            output_target=OutputTarget.FILE,
            directory=nested_dir,
            filename=log_file,
        )
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        logger.info("Nested directory test")

        # Flush the handler
        underlying_logger = logging.getLogger(config.name)
        for handler in underlying_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()

        log_path = nested_dir / log_file
        assert log_path.exists()
        assert log_path.parent.exists()
        content = log_path.read_text()
        assert "Nested directory test" in content

    def test_file_logger_with_structured_logging(self) -> None:
        """Test file logger with extra fields."""
        log_file = "test_structured.log"
        config = LoggerConfig(
            name="test_file_structured",
            output_target=OutputTarget.FILE,
            directory=self.temp_dir,
            filename=log_file,
        )
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        logger.info("User logged in", extra={"user_id": "user123", "ip": "10.0.0.1"})

        # Flush the handler
        underlying_logger = logging.getLogger(config.name)
        for handler in underlying_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()

        log_path = self.temp_dir / log_file
        content = log_path.read_text()
        assert "User logged in" in content

    def test_file_logger_appends_to_existing_file(self) -> None:
        """Test that file logger appends to existing file instead of overwriting."""
        log_file = "test_append.log"
        config = LoggerConfig(
            name="test_file_append",
            output_target=OutputTarget.FILE,
            directory=self.temp_dir,
            filename=log_file,
        )
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)

        # First logger instance
        logger1 = factory.get_or_create_logger(config)
        logger1.info("First message")

        # Flush and close
        underlying_logger = logging.getLogger(config.name)
        for handler in underlying_logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.flush()
                handler.close()
                underlying_logger.removeHandler(handler)

        # Clear cache and create new logger
        factory.clear_cache()
        logger2 = factory.get_or_create_logger(config)
        logger2.info("Second message")

        # Flush
        for handler in underlying_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()

        log_path = self.temp_dir / log_file
        content = log_path.read_text()
        assert "First message" in content
        assert "Second message" in content

    def test_multiple_file_loggers_different_files(self) -> None:
        """Test multiple file loggers write to different files."""
        log_file1 = "test_multi_1.log"
        log_file2 = "test_multi_2.log"

        config1 = LoggerConfig(
            name="test_file_multi_1",
            output_target=OutputTarget.FILE,
            directory=self.temp_dir,
            filename=log_file1,
        )
        config2 = LoggerConfig(
            name="test_file_multi_2",
            output_target=OutputTarget.FILE,
            directory=self.temp_dir,
            filename=log_file2,
        )
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)

        logger1 = factory.get_or_create_logger(config1)
        logger2 = factory.get_or_create_logger(config2)

        logger1.info("Logger 1 message")
        logger2.info("Logger 2 message")

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

        assert "Logger 1 message" in content1
        assert "Logger 2 message" not in content1
        assert "Logger 2 message" in content2
        assert "Logger 1 message" not in content2

    @pytest.mark.asyncio
    async def test_file_logger_async_variant(self) -> None:
        """Test async file logger functionality."""
        log_file = "test_async.log"
        config = LoggerConfig(
            name="test_file_async",
            output_target=OutputTarget.FILE,
            directory=self.temp_dir,
            filename=log_file,
        )
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_async_logger(config)

        await logger.info("Async file message")

        # Flush the handler
        underlying_logger = logging.getLogger(config.name)
        for handler in underlying_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()

        log_path = self.temp_dir / log_file
        content = log_path.read_text()
        assert "Async file message" in content
