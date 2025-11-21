"""Unit tests for PythonLoggerAdapter."""

import logging
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from miraveja_log.application.configuration import LoggerConfig
from miraveja_log.domain import ConfigurationException, ILogger, LogLevel, OutputTarget
from miraveja_log.infrastructure.adapters.python_logger_adapter import PythonLoggerAdapter


class TestPythonLoggerAdapterBasics:
    """Test basic PythonLoggerAdapter functionality."""

    def test_python_logger_adapter_can_be_instantiated(self) -> None:
        """Test that PythonLoggerAdapter can be created."""
        config = LoggerConfig(name="test_logger")
        adapter = PythonLoggerAdapter(config)

        assert adapter is not None

    def test_python_logger_adapter_implements_ilogger(self) -> None:
        """Test that PythonLoggerAdapter implements ILogger interface."""
        config = LoggerConfig(name="test_logger")
        adapter = PythonLoggerAdapter(config)

        assert isinstance(adapter, ILogger)

    def test_python_logger_adapter_stores_config(self) -> None:
        """Test that PythonLoggerAdapter stores the configuration."""
        config = LoggerConfig(name="test_logger", level=LogLevel.DEBUG)
        adapter = PythonLoggerAdapter(config)

        assert adapter._config == config

    def test_python_logger_adapter_creates_underlying_logger(self) -> None:
        """Test that PythonLoggerAdapter creates underlying Python logger."""
        config = LoggerConfig(name="test_logger")
        adapter = PythonLoggerAdapter(config)

        assert adapter._logger is not None
        assert isinstance(adapter._logger, logging.Logger)
        assert adapter._logger.name == "test_logger"


class TestPythonLoggerAdapterConfiguration:
    """Test PythonLoggerAdapter configuration."""

    def test_adapter_sets_correct_log_level(self) -> None:
        """Test that adapter sets the correct log level."""
        config = LoggerConfig(name="test_logger", level=LogLevel.WARNING)
        adapter = PythonLoggerAdapter(config)

        assert adapter._logger.level == logging.WARNING

    def test_adapter_clears_existing_handlers(self) -> None:
        """Test that adapter clears existing handlers during initialization."""
        # Pre-configure a logger with handlers
        logger = logging.getLogger("test_clear_handlers")
        logger.addHandler(logging.StreamHandler())
        assert len(logger.handlers) > 0

        # Create adapter with same logger name
        config = LoggerConfig(name="test_clear_handlers")
        adapter = PythonLoggerAdapter(config)

        # After adapter creation, should have exactly 1 handler (the new one)
        assert len(adapter._logger.handlers) == 1

    def test_adapter_adds_handler(self) -> None:
        """Test that adapter adds a handler to the logger."""
        config = LoggerConfig(name="test_logger")
        adapter = PythonLoggerAdapter(config)

        assert len(adapter._logger.handlers) == 1

    def test_adapter_sets_formatter_on_handler(self) -> None:
        """Test that adapter sets formatter on the handler."""
        config = LoggerConfig(name="test_logger")
        adapter = PythonLoggerAdapter(config)

        handler = adapter._logger.handlers[0]
        assert handler.formatter is not None


class TestPythonLoggerAdapterConsoleOutput:
    """Test PythonLoggerAdapter with console output."""

    def test_console_output_creates_stream_handler(self) -> None:
        """Test that console output creates a StreamHandler."""
        config = LoggerConfig(name="test_logger", output_target=OutputTarget.CONSOLE)
        adapter = PythonLoggerAdapter(config)

        handler = adapter._logger.handlers[0]
        assert isinstance(handler, logging.StreamHandler)

    def test_console_output_uses_text_formatter(self) -> None:
        """Test that console output uses TextFormatter."""
        config = LoggerConfig(name="test_logger", output_target=OutputTarget.CONSOLE)
        adapter = PythonLoggerAdapter(config)

        handler = adapter._logger.handlers[0]
        # TextFormatter is a subclass of logging.Formatter
        assert isinstance(handler.formatter, logging.Formatter)


class TestPythonLoggerAdapterFileOutput:
    """Test PythonLoggerAdapter with file output."""

    def test_file_output_creates_file_handler(self) -> None:
        """Test that file output creates a FileHandler."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = LoggerConfig(
                name="test_logger",
                output_target=OutputTarget.FILE,
                directory=Path(tmpdir),
                filename="test.log",
            )
            adapter = PythonLoggerAdapter(config)

            handler = adapter._logger.handlers[0]
            assert isinstance(handler, logging.FileHandler)

            # Close handler to release file on Windows
            handler.close()
            adapter._logger.handlers.clear()

    def test_file_output_uses_correct_file_path(self) -> None:
        """Test that file output uses the correct file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = LoggerConfig(
                name="test_logger",
                output_target=OutputTarget.FILE,
                directory=Path(tmpdir),
                filename="test.log",
            )
            adapter = PythonLoggerAdapter(config)

            handler = adapter._logger.handlers[0]
            assert isinstance(handler, logging.FileHandler)
            # FileHandler stores the filename in baseFilename
            expected_path = str(Path(tmpdir) / "test.log")
            assert handler.baseFilename == expected_path

            # Close handler to release file on Windows
            handler.close()
            adapter._logger.handlers.clear()


class TestPythonLoggerAdapterJSONOutput:
    """Test PythonLoggerAdapter with JSON output."""

    def test_json_output_creates_file_handler(self) -> None:
        """Test that JSON output creates a FileHandler."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = LoggerConfig(
                name="test_logger",
                output_target=OutputTarget.JSON,
                directory=Path(tmpdir),
                filename="test.json",
            )
            adapter = PythonLoggerAdapter(config)

            handler = adapter._logger.handlers[0]
            assert isinstance(handler, logging.FileHandler)

            # Close handler to release file on Windows
            handler.close()
            adapter._logger.handlers.clear()

    def test_json_output_uses_json_formatter(self) -> None:
        """Test that JSON output uses JSONFormatter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = LoggerConfig(
                name="test_logger",
                output_target=OutputTarget.JSON,
                directory=Path(tmpdir),
                filename="test.json",
            )
            adapter = PythonLoggerAdapter(config)

            handler = adapter._logger.handlers[0]
            formatter = handler.formatter
            # JSONFormatter is a subclass of logging.Formatter
            assert isinstance(formatter, logging.Formatter)
            # Check it's specifically JSONFormatter by class name
            assert formatter.__class__.__name__ == "JSONFormatter"

            # Close handler to release file on Windows
            handler.close()
            adapter._logger.handlers.clear()


class TestPythonLoggerAdapterLoggingMethods:
    """Test PythonLoggerAdapter logging methods."""

    def test_debug_method_logs_message(self) -> None:
        """Test that debug method logs a message."""
        config = LoggerConfig(name="test_logger", level=LogLevel.DEBUG)
        adapter = PythonLoggerAdapter(config)

        with patch.object(adapter._logger, "debug") as mock_debug:
            adapter.debug("Debug message")
            mock_debug.assert_called_once_with("Debug message")

    def test_info_method_logs_message(self) -> None:
        """Test that info method logs a message."""
        config = LoggerConfig(name="test_logger")
        adapter = PythonLoggerAdapter(config)

        with patch.object(adapter._logger, "info") as mock_info:
            adapter.info("Info message")
            mock_info.assert_called_once_with("Info message")

    def test_warning_method_logs_message(self) -> None:
        """Test that warning method logs a message."""
        config = LoggerConfig(name="test_logger")
        adapter = PythonLoggerAdapter(config)

        with patch.object(adapter._logger, "warning") as mock_warning:
            adapter.warning("Warning message")
            mock_warning.assert_called_once_with("Warning message")

    def test_error_method_logs_message(self) -> None:
        """Test that error method logs a message."""
        config = LoggerConfig(name="test_logger")
        adapter = PythonLoggerAdapter(config)

        with patch.object(adapter._logger, "error") as mock_error:
            adapter.error("Error message")
            mock_error.assert_called_once_with("Error message")

    def test_critical_method_logs_message(self) -> None:
        """Test that critical method logs a message."""
        config = LoggerConfig(name="test_logger")
        adapter = PythonLoggerAdapter(config)

        with patch.object(adapter._logger, "critical") as mock_critical:
            adapter.critical("Critical message")
            mock_critical.assert_called_once_with("Critical message")


class TestPythonLoggerAdapterLoggingWithArgs:
    """Test PythonLoggerAdapter logging methods with args and kwargs."""

    def test_debug_method_accepts_args(self) -> None:
        """Test that debug method accepts positional args."""
        config = LoggerConfig(name="test_logger", level=LogLevel.DEBUG)
        adapter = PythonLoggerAdapter(config)

        with patch.object(adapter._logger, "debug") as mock_debug:
            adapter.debug("Message: %s", "value")
            mock_debug.assert_called_once_with("Message: %s", "value")

    def test_info_method_accepts_kwargs(self) -> None:
        """Test that info method accepts keyword arguments."""
        config = LoggerConfig(name="test_logger")
        adapter = PythonLoggerAdapter(config)

        with patch.object(adapter._logger, "info") as mock_info:
            adapter.info("Info message", extra={"user_id": "123"})
            mock_info.assert_called_once_with("Info message", extra={"user_id": "123"})

    def test_error_method_accepts_exc_info(self) -> None:
        """Test that error method accepts exc_info."""
        config = LoggerConfig(name="test_logger")
        adapter = PythonLoggerAdapter(config)

        with patch.object(adapter._logger, "error") as mock_error:
            adapter.error("Error occurred", exc_info=True)
            mock_error.assert_called_once_with("Error occurred", exc_info=True)


class TestPythonLoggerAdapterHandlerMapping:
    """Test handler and formatter mapping."""

    def test_handler_mapper_has_all_output_targets(self) -> None:
        """Test that handler mapper includes all output targets."""
        assert OutputTarget.CONSOLE in PythonLoggerAdapter.HANDLER_TARGET_MAPPER
        assert OutputTarget.FILE in PythonLoggerAdapter.HANDLER_TARGET_MAPPER
        assert OutputTarget.JSON in PythonLoggerAdapter.HANDLER_TARGET_MAPPER

    def test_formatter_mapper_has_all_output_targets(self) -> None:
        """Test that formatter mapper includes all output targets."""
        assert OutputTarget.CONSOLE in PythonLoggerAdapter.FORMATTER_TARGET_MAPPER
        assert OutputTarget.FILE in PythonLoggerAdapter.FORMATTER_TARGET_MAPPER
        assert OutputTarget.JSON in PythonLoggerAdapter.FORMATTER_TARGET_MAPPER


class TestPythonLoggerAdapterExceptionHandling:
    """Test exception handling in PythonLoggerAdapter."""

    def test_adapter_raises_exception_for_unsupported_handler_target(self) -> None:
        """Test that adapter raises ConfigurationException for unsupported handler target."""
        config = LoggerConfig(name="test_logger")

        # Create adapter but modify the config to have an invalid target
        # We need to mock or patch to simulate an unsupported target
        with patch.object(PythonLoggerAdapter, "HANDLER_TARGET_MAPPER", {}):
            with pytest.raises(ConfigurationException) as exc_info:
                PythonLoggerAdapter(config)

            assert "output_target" in str(exc_info.value)
            assert "Unsupported output target" in str(exc_info.value)

    def test_adapter_raises_exception_for_unsupported_formatter_target(self) -> None:
        """Test that adapter raises ConfigurationException for unsupported formatter target."""
        config = LoggerConfig(name="test_logger")

        # Mock FORMATTER_TARGET_MAPPER to be empty while keeping HANDLER_TARGET_MAPPER valid
        with patch.object(PythonLoggerAdapter, "FORMATTER_TARGET_MAPPER", {}):
            with pytest.raises(ConfigurationException) as exc_info:
                PythonLoggerAdapter(config)

            assert "output_target" in str(exc_info.value)
            assert "Unsupported output target" in str(exc_info.value)


class TestPythonLoggerAdapterEdgeCases:
    """Test edge cases and special scenarios."""

    def test_adapter_with_custom_log_format(self) -> None:
        """Test adapter with custom log format."""
        config = LoggerConfig(name="test_logger", log_format="%(levelname)s: %(message)s")
        adapter = PythonLoggerAdapter(config)

        assert adapter._logger is not None
        handler = adapter._logger.handlers[0]
        assert handler.formatter is not None

    def test_adapter_with_custom_date_format(self) -> None:
        """Test adapter with custom date format."""
        config = LoggerConfig(name="test_logger", date_format="%Y-%m-%d")
        adapter = PythonLoggerAdapter(config)

        assert adapter._logger is not None
        handler = adapter._logger.handlers[0]
        assert handler.formatter is not None

    def test_adapter_with_different_log_levels(self) -> None:
        """Test adapter with all different log levels."""
        for level in LogLevel:
            config = LoggerConfig(name=f"test_logger_{level.value}", level=level)
            adapter = PythonLoggerAdapter(config)

            assert adapter._logger.level == getattr(logging, level.value)

    def test_multiple_adapters_with_same_name_share_logger(self) -> None:
        """Test that multiple adapters with the same name share the underlying logger."""
        config1 = LoggerConfig(name="shared_logger")
        adapter1 = PythonLoggerAdapter(config1)

        config2 = LoggerConfig(name="shared_logger")
        adapter2 = PythonLoggerAdapter(config2)

        # They should reference the same logger instance (Python logging module caches loggers)
        assert adapter1._logger.name == adapter2._logger.name == "shared_logger"
