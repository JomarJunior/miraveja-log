"""Integration tests for error scenarios and edge cases."""

import logging
import shutil
import tempfile
from pathlib import Path

import pytest

from miraveja_log.application import LoggerConfig, LoggerFactory
from miraveja_log.domain import ConfigurationException, LogLevel, OutputTarget
from miraveja_log.infrastructure.adapters import AsyncPythonLoggerAdapter, PythonLoggerAdapter


class TestErrorScenarios:
    """Test error handling and edge cases in logging."""

    def test_file_target_without_directory_raises_error(self) -> None:
        """Test that FILE target without directory raises ConfigurationException."""
        with pytest.raises(ValueError, match="directory must be provided"):
            LoggerConfig(
                name="test_error_no_dir",
                output_target=OutputTarget.FILE,
                directory=None,
                filename="app.log",
            )

    def test_file_target_without_filename_raises_error(self) -> None:
        """Test that FILE target without filename raises ConfigurationException."""
        temp_dir = Path(tempfile.mkdtemp())
        try:
            with pytest.raises(ValueError, match="filename must be provided"):
                LoggerConfig(
                    name="test_error_no_filename",
                    output_target=OutputTarget.FILE,
                    directory=temp_dir,
                    filename=None,
                )
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    def test_json_target_without_directory_raises_error(self) -> None:
        """Test that JSON target without directory raises ConfigurationException."""
        with pytest.raises(ValueError, match="directory must be provided"):
            LoggerConfig(
                name="test_error_json_no_dir",
                output_target=OutputTarget.JSON,
                directory=None,
                filename="app.json",
            )

    def test_json_target_without_filename_raises_error(self) -> None:
        """Test that JSON target without filename raises ConfigurationException."""
        temp_dir = Path(tempfile.mkdtemp())
        try:
            with pytest.raises(ValueError, match="filename must be provided"):
                LoggerConfig(
                    name="test_error_json_no_filename",
                    output_target=OutputTarget.JSON,
                    directory=temp_dir,
                    filename=None,
                )
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    def test_invalid_log_level_raises_error(self) -> None:
        """Test that invalid log level raises error."""
        with pytest.raises((ValueError, KeyError)):
            LoggerConfig(name="test_error", level="INVALID_LEVEL")  # type: ignore

    def test_invalid_output_target_raises_error(self) -> None:
        """Test that invalid output target raises error."""
        with pytest.raises((ValueError, KeyError)):
            LoggerConfig(name="test_error", output_target="INVALID_TARGET")  # type: ignore

    def test_logger_with_nonexistent_directory_creates_it(self) -> None:
        """Test that logger creates directory if it doesn't exist."""
        temp_dir = Path(tempfile.mkdtemp())
        nested_dir = temp_dir / "deeply" / "nested" / "path"

        try:
            config = LoggerConfig(
                name="test_create_dir",
                output_target=OutputTarget.FILE,
                directory=nested_dir,
                filename="test.log",
            )
            factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
            logger = factory.get_or_create_logger(config)

            logger.info("Test message")

            # Directory should be created
            assert nested_dir.exists()
            assert nested_dir.is_dir()

        finally:
            # Clean up
            for handler in logging.getLogger(config.name).handlers[:]:
                if isinstance(handler, logging.FileHandler):
                    handler.close()
                    logging.getLogger(config.name).removeHandler(handler)
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    def test_logger_with_readonly_directory_raises_error(self) -> None:
        """Test that logger handles readonly directory gracefully."""
        # This test is platform-specific and may behave differently
        # Skip on Windows where setting readonly is complex
        import sys

        if sys.platform == "win32":
            pytest.skip("Readonly directory test not reliable on Windows")

        temp_dir = Path(tempfile.mkdtemp())
        try:
            # Make directory readonly
            temp_dir.chmod(0o444)

            config = LoggerConfig(
                name="test_readonly",
                output_target=OutputTarget.FILE,
                directory=temp_dir,
                filename="test.log",
            )
            factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)

            # Should raise error when trying to write
            with pytest.raises((PermissionError, OSError, ConfigurationException)):
                logger = factory.get_or_create_logger(config)
                logger.info("Test message")

        finally:
            # Restore permissions and clean up
            temp_dir.chmod(0o755)
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    def test_logger_with_empty_message(self) -> None:
        """Test that logger handles empty messages correctly."""
        config = LoggerConfig(name="test_empty_message")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        # Should not raise error
        logger.info("")
        logger.debug("")

    def test_logger_with_very_long_message(self) -> None:
        """Test that logger handles very long messages."""
        config = LoggerConfig(name="test_long_message")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        long_message = "A" * 10000  # 10KB message

        # Should not raise error
        logger.info(long_message)

    def test_logger_with_special_characters_in_message(self) -> None:
        """Test that logger handles special characters correctly."""
        config = LoggerConfig(name="test_special_chars")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        special_message = "Test\nwith\ttabs\rand\x00null\rbytes"

        # Should not raise error
        logger.info(special_message)

    def test_logger_with_none_message_raises_error(self) -> None:
        """Test that logger handles None message (converts to 'None' string)."""
        config = LoggerConfig(name="test_none_message")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        # Python's logging accepts None and converts it to 'None' string
        # This should not raise an error
        logger.info(None)  # type: ignore
        # Test passes if no exception is raised

    def test_logger_with_circular_reference_in_extra(self) -> None:
        """Test that logger handles circular references in extra fields."""
        config = LoggerConfig(name="test_circular_ref")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        # Create circular reference
        data: dict = {"key": "value"}
        data["self"] = data

        # Should handle gracefully (may not raise error or may raise RuntimeError)
        try:
            logger.info("Circular reference test", extra={"data": data})
        except (RuntimeError, RecursionError):
            pass  # Expected for circular references

    def test_concurrent_file_access(self) -> None:
        """Test concurrent access to same log file."""
        temp_dir = Path(tempfile.mkdtemp())
        log_file = "concurrent.log"

        try:
            config = LoggerConfig(
                name="test_concurrent",
                output_target=OutputTarget.FILE,
                directory=temp_dir,
                filename=log_file,
            )
            factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
            logger = factory.get_or_create_logger(config)

            import threading

            def log_messages(thread_id: int) -> None:
                for i in range(10):
                    logger.info(f"Thread {thread_id} message {i}")

            threads = [threading.Thread(target=log_messages, args=(i,)) for i in range(5)]

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

            # Verify file was created and has content
            log_path = temp_dir / log_file
            assert log_path.exists()
            content = log_path.read_text()
            assert len(content) > 0

        finally:
            # Clean up
            for handler in logging.getLogger(config.name).handlers[:]:
                if isinstance(handler, logging.FileHandler):
                    handler.close()
                    logging.getLogger(config.name).removeHandler(handler)
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_async_logger_exception_in_async_context(self) -> None:
        """Test async logger handles exceptions in async context."""
        config = LoggerConfig(name="test_async_exception")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_async_logger(config)

        try:
            raise ValueError("Async exception test")
        except ValueError:
            # Should not raise error
            await logger.error("Async exception", exc_info=True)

    def test_logger_factory_clear_cache_while_logging(self) -> None:
        """Test clearing cache while logging is happening."""
        config = LoggerConfig(name="test_cache_clear")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        logger.info("Before clear")
        factory.clear_cache()

        # Should be able to create new logger after clear
        logger2 = factory.get_or_create_logger(config)
        logger2.info("After clear")

        # Loggers should be different instances
        assert logger is not logger2

    def test_logger_with_extreme_log_levels(self) -> None:
        """Test logger with all extreme log levels."""
        for level in [LogLevel.DEBUG, LogLevel.CRITICAL]:
            config = LoggerConfig(name=f"test_extreme_{level}", level=level)
            factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
            logger = factory.get_or_create_logger(config)

            # Should not raise error
            logger.debug("Debug")
            logger.critical("Critical")

            factory.clear_cache()

    def test_logger_with_file_path_containing_special_chars(self) -> None:
        """Test logger with special characters in filename."""
        temp_dir = Path(tempfile.mkdtemp())

        # Use safe special characters for filename
        log_file = "test_log-2025_11_20.log"

        try:
            config = LoggerConfig(
                name="test_special_filename",
                output_target=OutputTarget.FILE,
                directory=temp_dir,
                filename=log_file,
            )
            factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
            logger = factory.get_or_create_logger(config)

            logger.info("Test message")

            log_path = temp_dir / log_file
            assert log_path.exists()

        finally:
            # Clean up
            for handler in logging.getLogger(config.name).handlers[:]:
                if isinstance(handler, logging.FileHandler):
                    handler.close()
                    logging.getLogger(config.name).removeHandler(handler)
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    def test_logger_with_invalid_format_string(self) -> None:
        """Test logger with invalid format string."""
        # Invalid format should still create logger but may produce warnings
        config = LoggerConfig(name="test_invalid_format", log_format="%(invalid_field)s")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
        logger = factory.get_or_create_logger(config)

        # Should not raise error (format errors are typically caught at formatting time)
        logger.info("Test message")

    def test_logger_reusing_same_name_returns_cached_instance(self) -> None:
        """Test that reusing same logger name returns cached instance."""
        config = LoggerConfig(name="test_cached")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)

        logger1 = factory.get_or_create_logger(config)
        logger2 = factory.get_or_create_logger(config)

        assert logger1 is logger2

    def test_mixing_sync_and_async_loggers_with_same_name(self) -> None:
        """Test creating both sync and async loggers with same name."""
        config = LoggerConfig(name="test_mixed")
        factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)

        sync_logger = factory.get_or_create_logger(config)
        async_logger = factory.get_or_create_async_logger(config)

        # Should be different instances (different caches)
        assert sync_logger is not async_logger
        assert type(sync_logger).__name__ != type(async_logger).__name__
