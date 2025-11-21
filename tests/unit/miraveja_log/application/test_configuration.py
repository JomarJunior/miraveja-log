"""Unit tests for application configuration."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from miraveja_log.application.configuration import LoggerConfig
from miraveja_log.domain.enums import LogLevel, OutputTarget


class TestLoggerConfigBasics:
    """Test basic LoggerConfig functionality."""

    def test_logger_config_requires_name(self) -> None:
        """Test that LoggerConfig requires a name field."""
        with pytest.raises(ValidationError):
            LoggerConfig()  # type: ignore

    def test_logger_config_defaults_to_info_level(self) -> None:
        """Test that LoggerConfig defaults to INFO level."""
        config = LoggerConfig(name="test")
        assert config.level == LogLevel.INFO

    def test_logger_config_defaults_to_console_target(self) -> None:
        """Test that LoggerConfig defaults to CONSOLE output target."""
        config = LoggerConfig(name="test")
        assert config.output_target == OutputTarget.CONSOLE

    def test_logger_config_has_default_log_format(self) -> None:
        """Test that LoggerConfig has a default log format."""
        config = LoggerConfig(name="test")
        assert config.log_format == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    def test_logger_config_has_default_date_format(self) -> None:
        """Test that LoggerConfig has a default date format."""
        config = LoggerConfig(name="test")
        assert config.date_format == "%Y-%m-%d %H:%M:%S"

    def test_logger_config_directory_defaults_to_none(self) -> None:
        """Test that directory defaults to None."""
        config = LoggerConfig(name="test")
        assert config.directory is None

    def test_logger_config_filename_defaults_to_none(self) -> None:
        """Test that filename defaults to None."""
        config = LoggerConfig(name="test")
        assert config.filename is None

    def test_logger_config_can_be_created_with_all_fields(self) -> None:
        """Test that LoggerConfig can be created with all fields specified."""
        config = LoggerConfig(
            name="test_logger",
            level=LogLevel.DEBUG,
            output_target=OutputTarget.FILE,
            log_format="%(message)s",
            date_format="%Y-%m-%d",
            directory="./logs",
            filename="test.log",
        )

        assert config.name == "test_logger"
        assert config.level == LogLevel.DEBUG
        assert config.output_target == OutputTarget.FILE
        assert config.log_format == "%(message)s"
        assert config.date_format == "%Y-%m-%d"
        assert config.directory == Path("./logs")
        assert config.filename == "test.log"


class TestLoggerConfigValidation:
    """Test LoggerConfig validation rules."""

    def test_logger_config_validates_directory_for_file_target(self) -> None:
        """Test that directory is required for FILE target."""
        with pytest.raises(ValidationError, match="directory must be provided"):
            LoggerConfig(name="test", output_target=OutputTarget.FILE, directory=None, filename="test.log")

    def test_logger_config_validates_filename_for_file_target(self) -> None:
        """Test that filename is required for FILE target."""
        with pytest.raises(ValidationError, match="filename must be provided"):
            LoggerConfig(name="test", output_target=OutputTarget.FILE, directory=Path("./logs"))

    def test_logger_config_validates_directory_for_json_target(self) -> None:
        """Test that directory is required for JSON target."""
        with pytest.raises(ValidationError, match="directory must be provided"):
            LoggerConfig(name="test", output_target=OutputTarget.JSON, filename="test.json")

    def test_logger_config_validates_filename_for_json_target(self) -> None:
        """Test that filename is required for JSON target."""
        with pytest.raises(ValidationError, match="filename must be provided"):
            LoggerConfig(name="test", output_target=OutputTarget.JSON, directory=Path("./logs"))

    def test_logger_config_allows_none_directory_for_console_target(self) -> None:
        """Test that directory can be None for CONSOLE target."""
        config = LoggerConfig(name="test", output_target=OutputTarget.CONSOLE)
        assert config.directory is None
        assert config.filename is None

    def test_logger_config_requires_both_directory_and_filename_for_file_targets(self) -> None:
        """Test that both directory and filename are required for FILE/JSON targets."""
        # Valid configuration with both - directory can be passed as string and will be converted to Path
        config = LoggerConfig(name="test", output_target=OutputTarget.FILE, directory="./logs", filename="test.log")
        assert config.directory == Path("./logs")
        assert config.filename == "test.log"


class TestLoggerConfigFromEnv:
    """Test LoggerConfig.from_env() class method."""

    def test_from_env_uses_default_name_when_env_not_set(self) -> None:
        """Test that from_env uses default name when LOGGER_NAME is not set."""
        with patch.dict(os.environ, {}, clear=True):
            config = LoggerConfig.from_env()
            assert config.name == "default_logger"

    def test_from_env_loads_name_from_environment(self) -> None:
        """Test that from_env loads logger name from LOGGER_NAME."""
        with patch.dict(os.environ, {"LOGGER_NAME": "my_service"}, clear=True):
            config = LoggerConfig.from_env()
            assert config.name == "my_service"

    def test_from_env_loads_level_from_environment(self) -> None:
        """Test that from_env loads log level from LOGGER_LEVEL."""
        with patch.dict(os.environ, {"LOGGER_NAME": "test", "LOGGER_LEVEL": "DEBUG"}, clear=True):
            config = LoggerConfig.from_env()
            assert config.level == LogLevel.DEBUG

    def test_from_env_loads_target_from_environment(self) -> None:
        """Test that from_env loads output target from LOGGER_TARGET."""
        with patch.dict(os.environ, {"LOGGER_NAME": "test", "LOGGER_TARGET": "CONSOLE"}, clear=True):
            config = LoggerConfig.from_env()
            assert config.output_target == OutputTarget.CONSOLE

    def test_from_env_loads_format_from_environment(self) -> None:
        """Test that from_env loads log format from LOGGER_FORMAT."""
        custom_format = "%(levelname)s: %(message)s"
        with patch.dict(os.environ, {"LOGGER_NAME": "test", "LOGGER_FORMAT": custom_format}, clear=True):
            config = LoggerConfig.from_env()
            assert config.log_format == custom_format

    def test_from_env_loads_datefmt_from_environment(self) -> None:
        """Test that from_env loads date format from LOGGER_DATEFMT."""
        custom_datefmt = "%Y/%m/%d"
        with patch.dict(os.environ, {"LOGGER_NAME": "test", "LOGGER_DATEFMT": custom_datefmt}, clear=True):
            config = LoggerConfig.from_env()
            assert config.date_format == custom_datefmt

    def test_from_env_loads_directory_from_environment(self) -> None:
        """Test that from_env loads directory from LOGGER_DIR."""
        with patch.dict(os.environ, {"LOGGER_NAME": "test", "LOGGER_DIR": "./logs"}, clear=True):
            config = LoggerConfig.from_env()
            assert config.directory == Path("./logs")

    def test_from_env_loads_filename_from_environment(self) -> None:
        """Test that from_env loads filename from LOGGER_FILENAME."""
        with patch.dict(os.environ, {"LOGGER_NAME": "test", "LOGGER_FILENAME": "app.log"}, clear=True):
            config = LoggerConfig.from_env()
            assert config.filename == "app.log"

    def test_from_env_uses_defaults_when_env_vars_not_set(self) -> None:
        """Test that from_env uses defaults when environment variables are not set."""
        with patch.dict(os.environ, {"LOGGER_NAME": "test"}, clear=True):
            config = LoggerConfig.from_env()
            assert config.name == "test"
            assert config.level == LogLevel.INFO
            assert config.output_target == OutputTarget.CONSOLE
            assert config.log_format == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            assert config.date_format == "%Y-%m-%d %H:%M:%S"

    def test_from_env_with_complete_configuration(self) -> None:
        """Test from_env with all environment variables set."""
        env_vars = {
            "LOGGER_NAME": "complete_logger",
            "LOGGER_LEVEL": "WARNING",
            "LOGGER_TARGET": "FILE",
            "LOGGER_FORMAT": "%(message)s",
            "LOGGER_DATEFMT": "%Y-%m-%d",
            "LOGGER_DIR": "./test_logs",
            "LOGGER_FILENAME": "test.log",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = LoggerConfig.from_env()
            assert config.name == "complete_logger"
            assert config.level == LogLevel.WARNING
            assert config.output_target == OutputTarget.FILE
            assert config.log_format == "%(message)s"
            assert config.date_format == "%Y-%m-%d"
            assert config.directory == Path("./test_logs")
            assert config.filename == "test.log"


class TestLoggerConfigGetFullPath:
    """Test LoggerConfig.get_full_path() method."""

    def test_get_full_path_returns_combined_path_for_file_target(self) -> None:
        """Test that get_full_path returns combined path for FILE target."""
        config = LoggerConfig(
            name="test", output_target=OutputTarget.FILE, directory=Path("./logs"), filename="app.log"
        )
        assert config.get_full_path() == Path("./logs/app.log")

    def test_get_full_path_returns_combined_path_for_json_target(self) -> None:
        """Test that get_full_path returns combined path for JSON target."""
        config = LoggerConfig(
            name="test", output_target=OutputTarget.JSON, directory=Path("./logs"), filename="app.json"
        )
        assert config.get_full_path() == Path("./logs/app.json")

    def test_get_full_path_returns_none_for_console_target(self) -> None:
        """Test that get_full_path returns None for CONSOLE target."""
        config = LoggerConfig(name="test", output_target=OutputTarget.CONSOLE)
        assert config.get_full_path() is None

    def test_get_full_path_returns_none_when_directory_missing(self) -> None:
        """Test that get_full_path returns None when directory is None."""
        config = LoggerConfig(name="test", output_target=OutputTarget.CONSOLE, filename="app.log")
        assert config.get_full_path() is None

    def test_get_full_path_returns_none_when_filename_missing(self) -> None:
        """Test that get_full_path returns None when filename is None."""
        config = LoggerConfig(name="test", output_target=OutputTarget.CONSOLE, directory=Path("./logs"))
        assert config.get_full_path() is None

    def test_get_full_path_with_nested_directory(self) -> None:
        """Test get_full_path with nested directory structure."""
        config = LoggerConfig(
            name="test", output_target=OutputTarget.FILE, directory=Path("./logs/app/debug"), filename="debug.log"
        )
        assert config.get_full_path() == Path("./logs/app/debug/debug.log")


class TestLoggerConfigEdgeCases:
    """Test edge cases and special scenarios."""

    def test_logger_config_with_different_log_levels(self) -> None:
        """Test LoggerConfig with all different log levels."""
        for level in LogLevel:
            config = LoggerConfig(name="test", level=level)
            assert config.level == level

    def test_logger_config_with_different_output_targets(self) -> None:
        """Test LoggerConfig with all different output targets (only CONSOLE works without dir/file)."""
        config = LoggerConfig(name="test", output_target=OutputTarget.CONSOLE)
        assert config.output_target == OutputTarget.CONSOLE

    def test_logger_config_with_empty_log_format(self) -> None:
        """Test LoggerConfig with empty log format string."""
        config = LoggerConfig(name="test", log_format="")
        assert config.log_format == ""

    def test_logger_config_with_none_log_format(self) -> None:
        """Test LoggerConfig with None log format."""
        config = LoggerConfig(name="test", log_format=None)
        assert config.log_format is None

    def test_logger_config_directory_is_path_object(self) -> None:
        """Test that directory is converted to Path object."""
        config = LoggerConfig(name="test", output_target=OutputTarget.FILE, directory="./logs", filename="test.log")
        assert isinstance(config.directory, Path)
        assert config.directory == Path("./logs")

    def test_logger_config_with_windows_path(self) -> None:
        """Test LoggerConfig with Windows-style path."""
        config = LoggerConfig(name="test", output_target=OutputTarget.FILE, directory="C:\\logs", filename="app.log")
        assert config.directory == Path("C:\\logs")
        assert config.get_full_path() == Path("C:\\logs\\app.log")

    def test_logger_config_model_dump(self) -> None:
        """Test that LoggerConfig can be dumped to dictionary."""
        config = LoggerConfig(
            name="test",
            level=LogLevel.DEBUG,
            output_target=OutputTarget.FILE,
            directory=Path("./logs"),
            filename="app.log",
        )
        dumped = config.model_dump()

        assert dumped["name"] == "test"
        assert dumped["level"] == LogLevel.DEBUG
        assert dumped["output_target"] == OutputTarget.FILE
