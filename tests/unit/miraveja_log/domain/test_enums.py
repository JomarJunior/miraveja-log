"""Unit tests for domain enums."""

import pytest

from miraveja_log.domain.enums import LogLevel, OutputTarget


class TestLogLevel:
    """Test cases for LogLevel enum."""

    def test_log_level_values_are_uppercase_strings(self) -> None:
        """Test that all LogLevel values are uppercase strings."""
        assert LogLevel.DEBUG.value == "DEBUG"
        assert LogLevel.INFO.value == "INFO"
        assert LogLevel.WARNING.value == "WARNING"
        assert LogLevel.ERROR.value == "ERROR"
        assert LogLevel.CRITICAL.value == "CRITICAL"

    def test_log_level_str_returns_value(self) -> None:
        """Test that __str__ returns the enum value."""
        assert str(LogLevel.DEBUG) == "DEBUG"
        assert str(LogLevel.INFO) == "INFO"
        assert str(LogLevel.WARNING) == "WARNING"
        assert str(LogLevel.ERROR) == "ERROR"
        assert str(LogLevel.CRITICAL) == "CRITICAL"

    def test_log_level_can_be_compared(self) -> None:
        """Test that LogLevel enums can be compared."""
        assert LogLevel.DEBUG == LogLevel.DEBUG
        assert LogLevel.INFO != LogLevel.DEBUG
        assert LogLevel.DEBUG is LogLevel.DEBUG

    def test_log_level_has_five_values(self) -> None:
        """Test that LogLevel enum has exactly five values."""
        assert len(LogLevel) == 5

    def test_log_level_can_be_created_from_string(self) -> None:
        """Test that LogLevel can be created from string value."""
        assert LogLevel("DEBUG") == LogLevel.DEBUG
        assert LogLevel("INFO") == LogLevel.INFO
        assert LogLevel("WARNING") == LogLevel.WARNING
        assert LogLevel("ERROR") == LogLevel.ERROR
        assert LogLevel("CRITICAL") == LogLevel.CRITICAL

    def test_log_level_invalid_string_raises_error(self) -> None:
        """Test that invalid string raises ValueError."""
        with pytest.raises(ValueError):
            LogLevel("INVALID")

    def test_log_level_is_instance_of_str(self) -> None:
        """Test that LogLevel inherits from str."""
        assert isinstance(LogLevel.INFO, str)
        assert isinstance(LogLevel.DEBUG.value, str)


class TestOutputTarget:
    """Test cases for OutputTarget enum."""

    def test_output_target_has_three_values(self) -> None:
        """Test that OutputTarget enum has exactly three values."""
        assert len(OutputTarget) == 3
        assert set(OutputTarget) == {OutputTarget.CONSOLE, OutputTarget.FILE, OutputTarget.JSON}

    def test_output_target_values_are_uppercase_strings(self) -> None:
        """Test that all OutputTarget values are uppercase strings."""
        assert OutputTarget.CONSOLE.value == "CONSOLE"
        assert OutputTarget.FILE.value == "FILE"
        assert OutputTarget.JSON.value == "JSON"

    def test_output_target_str_returns_value(self) -> None:
        """Test that __str__ returns the enum value."""
        assert str(OutputTarget.CONSOLE) == "CONSOLE"
        assert str(OutputTarget.FILE) == "FILE"
        assert str(OutputTarget.JSON) == "JSON"

    def test_output_target_can_be_compared(self) -> None:
        """Test that OutputTarget enums can be compared."""
        assert OutputTarget.CONSOLE == OutputTarget.CONSOLE
        assert OutputTarget.FILE != OutputTarget.CONSOLE
        assert OutputTarget.CONSOLE is OutputTarget.CONSOLE

    def test_output_target_can_be_created_from_string(self) -> None:
        """Test that OutputTarget can be created from string value."""
        assert OutputTarget("CONSOLE") == OutputTarget.CONSOLE
        assert OutputTarget("FILE") == OutputTarget.FILE
        assert OutputTarget("JSON") == OutputTarget.JSON

    def test_output_target_invalid_string_raises_error(self) -> None:
        """Test that invalid string raises ValueError."""
        with pytest.raises(ValueError):
            OutputTarget("INVALID")

    def test_output_target_is_instance_of_str(self) -> None:
        """Test that OutputTarget inherits from str."""
        assert isinstance(OutputTarget.CONSOLE, str)
        assert isinstance(OutputTarget.FILE.value, str)
