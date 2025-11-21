"""Integration tests for configuration from environment variables."""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest

from miraveja_log.application import LoggerConfig
from miraveja_log.domain import LogLevel, OutputTarget


class TestConfigurationFromEnv:
    """Test loading configuration from environment variables."""

    def setup_method(self) -> None:
        """Store original environment variables."""
        self.original_env: Dict[str, Any] = {}
        self.env_vars = [
            "LOGGER_NAME",
            "LOGGER_LEVEL",
            "LOGGER_TARGET",
            "LOGGER_FORMAT",
            "LOGGER_DATEFMT",
            "LOGGER_DIR",
            "LOGGER_FILENAME",
        ]
        for var in self.env_vars:
            self.original_env[var] = os.environ.get(var)

        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self) -> None:
        """Restore original environment variables."""
        for var in self.env_vars:
            if self.original_env[var] is None:
                os.environ.pop(var, None)
            else:
                os.environ[var] = self.original_env[var]

        # Clean up temp directory
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_from_env_loads_logger_name(self) -> None:
        """Test that from_env loads logger name from environment."""
        os.environ["LOGGER_NAME"] = "env_test_logger"
        config = LoggerConfig.from_env()
        assert config.name == "env_test_logger"

    def test_from_env_uses_default_name_when_not_set(self) -> None:
        """Test that from_env uses default name when env var not set."""
        os.environ.pop("LOGGER_NAME", None)
        config = LoggerConfig.from_env()
        assert config.name == "default_name"

    def test_from_env_loads_log_level(self) -> None:
        """Test that from_env loads log level from environment."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            os.environ["LOGGER_LEVEL"] = level
            config = LoggerConfig.from_env()
            assert config.level == LogLevel(level)

    def test_from_env_loads_output_target(self) -> None:
        """Test that from_env loads output target from environment."""
        # Test CONSOLE target
        os.environ["LOGGER_TARGET"] = "CONSOLE"
        os.environ.pop("LOGGER_DIR", None)
        os.environ.pop("LOGGER_FILENAME", None)
        config = LoggerConfig.from_env()
        assert config.output_target == OutputTarget.CONSOLE

        # Test FILE target with required fields
        os.environ["LOGGER_TARGET"] = "FILE"
        os.environ["LOGGER_DIR"] = str(self.temp_dir)
        os.environ["LOGGER_FILENAME"] = "test.log"
        config = LoggerConfig.from_env()
        assert config.output_target == OutputTarget.FILE

        # Test JSON target with required fields
        os.environ["LOGGER_TARGET"] = "JSON"
        os.environ["LOGGER_DIR"] = str(self.temp_dir)
        os.environ["LOGGER_FILENAME"] = "test.json"
        config = LoggerConfig.from_env()
        assert config.output_target == OutputTarget.JSON

    def test_from_env_loads_log_format(self) -> None:
        """Test that from_env loads log format from environment."""
        custom_format = "%(levelname)s - %(message)s"
        os.environ["LOGGER_FORMAT"] = custom_format
        config = LoggerConfig.from_env()
        assert config.log_format == custom_format

    def test_from_env_loads_date_format(self) -> None:
        """Test that from_env loads date format from environment."""
        custom_datefmt = "%Y/%m/%d %H:%M:%S"
        os.environ["LOGGER_DATEFMT"] = custom_datefmt
        config = LoggerConfig.from_env()
        assert config.date_format == custom_datefmt

    def test_from_env_loads_directory_and_filename_for_file_target(self) -> None:
        """Test that from_env loads directory and filename for FILE target."""
        os.environ["LOGGER_TARGET"] = "FILE"
        os.environ["LOGGER_DIR"] = str(self.temp_dir)
        os.environ["LOGGER_FILENAME"] = "app.log"

        config = LoggerConfig.from_env()

        assert config.output_target == OutputTarget.FILE
        assert config.directory == self.temp_dir
        assert config.filename == "app.log"

    def test_from_env_loads_directory_and_filename_for_json_target(self) -> None:
        """Test that from_env loads directory and filename for JSON target."""
        os.environ["LOGGER_TARGET"] = "JSON"
        os.environ["LOGGER_DIR"] = str(self.temp_dir)
        os.environ["LOGGER_FILENAME"] = "app.json"

        config = LoggerConfig.from_env()

        assert config.output_target == OutputTarget.JSON
        assert config.directory == self.temp_dir
        assert config.filename == "app.json"

    def test_from_env_with_complete_configuration(self) -> None:
        """Test from_env with all environment variables set."""
        os.environ["LOGGER_NAME"] = "complete_env_logger"
        os.environ["LOGGER_LEVEL"] = "WARNING"
        os.environ["LOGGER_TARGET"] = "FILE"
        os.environ["LOGGER_FORMAT"] = "%(asctime)s | %(levelname)s | %(message)s"
        os.environ["LOGGER_DATEFMT"] = "%Y-%m-%d %H:%M:%S"
        os.environ["LOGGER_DIR"] = str(self.temp_dir)
        os.environ["LOGGER_FILENAME"] = "complete.log"

        config = LoggerConfig.from_env()

        assert config.name == "complete_env_logger"
        assert config.level == LogLevel.WARNING
        assert config.output_target == OutputTarget.FILE
        assert config.log_format == "%(asctime)s | %(levelname)s | %(message)s"
        assert config.date_format == "%Y-%m-%d %H:%M:%S"
        assert config.directory == self.temp_dir
        assert config.filename == "complete.log"

    def test_from_env_validation_for_file_target_without_directory(self) -> None:
        """Test that from_env validates FILE target requires directory."""
        os.environ["LOGGER_TARGET"] = "FILE"
        os.environ.pop("LOGGER_DIR", None)
        os.environ["LOGGER_FILENAME"] = "app.log"

        with pytest.raises(ValueError, match="directory must be provided"):
            LoggerConfig.from_env()

    def test_from_env_validation_for_file_target_without_filename(self) -> None:
        """Test that from_env validates FILE target requires filename."""
        os.environ["LOGGER_TARGET"] = "FILE"
        os.environ["LOGGER_DIR"] = str(self.temp_dir)
        os.environ.pop("LOGGER_FILENAME", None)

        with pytest.raises(ValueError, match="filename must be provided"):
            LoggerConfig.from_env()

    def test_from_env_validation_for_json_target_without_directory(self) -> None:
        """Test that from_env validates JSON target requires directory."""
        os.environ["LOGGER_TARGET"] = "JSON"
        os.environ.pop("LOGGER_DIR", None)
        os.environ["LOGGER_FILENAME"] = "app.json"

        with pytest.raises(ValueError, match="directory must be provided"):
            LoggerConfig.from_env()

    def test_from_env_validation_for_json_target_without_filename(self) -> None:
        """Test that from_env validates JSON target requires filename."""
        os.environ["LOGGER_TARGET"] = "JSON"
        os.environ["LOGGER_DIR"] = str(self.temp_dir)
        os.environ.pop("LOGGER_FILENAME", None)

        with pytest.raises(ValueError, match="filename must be provided"):
            LoggerConfig.from_env()

    def test_from_env_console_target_without_directory_and_filename(self) -> None:
        """Test that CONSOLE target doesn't require directory and filename."""
        os.environ["LOGGER_TARGET"] = "CONSOLE"
        os.environ.pop("LOGGER_DIR", None)
        os.environ.pop("LOGGER_FILENAME", None)

        config = LoggerConfig.from_env()

        assert config.output_target == OutputTarget.CONSOLE
        assert config.directory is None
        assert config.filename is None

    def test_from_env_with_default_target(self) -> None:
        """Test from_env with default_target parameter."""
        os.environ.pop("LOGGER_TARGET", None)
        os.environ.pop("LOGGER_DIR", None)
        os.environ.pop("LOGGER_FILENAME", None)

        config = LoggerConfig.from_env()

        assert config.output_target == OutputTarget.CONSOLE

    def test_from_env_creates_directory_if_not_exists(self) -> None:
        """Test that from_env accepts non-existent directory path (adapter creates it)."""
        nested_dir = self.temp_dir / "nested" / "logs"
        os.environ["LOGGER_TARGET"] = "FILE"
        os.environ["LOGGER_DIR"] = str(nested_dir)
        os.environ["LOGGER_FILENAME"] = "app.log"

        config = LoggerConfig.from_env()

        # Configuration should be created successfully with non-existent directory
        # (adapter will create directory when creating handler)
        assert config.directory == nested_dir
        assert config.filename == "app.log"

    def test_from_env_with_relative_directory_path(self) -> None:
        """Test from_env converts relative directory path to absolute."""
        os.environ["LOGGER_TARGET"] = "FILE"
        os.environ["LOGGER_DIR"] = "./logs"
        os.environ["LOGGER_FILENAME"] = "app.log"

        config = LoggerConfig.from_env()

        # Directory should be converted to absolute path
        assert config.directory is not None
        assert config.directory.is_absolute()

    def test_from_env_empty_string_values_treated_as_not_set(self) -> None:
        """Test that empty string environment variables are treated as not set."""
        os.environ["LOGGER_NAME"] = ""
        os.environ["LOGGER_FORMAT"] = ""

        config = LoggerConfig.from_env()

        # Should use defaults when env vars are empty strings
        assert config.name == "default_name"
        # Format should use the default format from LoggerConfig

    def test_from_env_with_invalid_log_level_raises_error(self) -> None:
        """Test that invalid log level raises error."""
        os.environ["LOGGER_LEVEL"] = "INVALID_LEVEL"

        with pytest.raises((ValueError, KeyError)):
            LoggerConfig.from_env()

    def test_from_env_with_invalid_target_raises_error(self) -> None:
        """Test that invalid output target raises error."""
        os.environ["LOGGER_TARGET"] = "INVALID_TARGET"

        with pytest.raises((ValueError, KeyError)):
            LoggerConfig.from_env()

    def test_from_env_case_sensitivity(self) -> None:
        """Test that environment variables are case-sensitive."""
        os.environ["logger_name"] = "lowercase"  # Wrong case
        os.environ["LOGGER_NAME"] = "uppercase"  # Correct case

        config = LoggerConfig.from_env()

        # Should use the correctly-cased variable
        assert config.name == "uppercase"

    def test_from_env_preserves_whitespace_in_format(self) -> None:
        """Test that from_env preserves whitespace in format strings."""
        format_with_spaces = "  %(levelname)s  -  %(message)s  "
        os.environ["LOGGER_FORMAT"] = format_with_spaces

        config = LoggerConfig.from_env()

        assert config.log_format == format_with_spaces

    def test_from_env_multiple_calls_with_different_env_vars(self) -> None:
        """Test multiple from_env calls with different environment variables."""
        # First call
        os.environ["LOGGER_NAME"] = "first_logger"
        os.environ["LOGGER_LEVEL"] = "DEBUG"
        config1 = LoggerConfig.from_env()

        # Change environment
        os.environ["LOGGER_NAME"] = "second_logger"
        os.environ["LOGGER_LEVEL"] = "ERROR"
        config2 = LoggerConfig.from_env()

        assert config1.name == "first_logger"
        assert config1.level == LogLevel.DEBUG
        assert config2.name == "second_logger"
        assert config2.level == LogLevel.ERROR
