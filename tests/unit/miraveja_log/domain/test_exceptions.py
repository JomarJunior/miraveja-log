"""Unit tests for domain exceptions."""

import pytest

from miraveja_log.domain.exceptions import ConfigurationException, HandlerException, LogException


class TestLogException:
    """Test cases for LogException base class."""

    def test_log_exception_stores_message(self) -> None:
        """Test that LogException stores the message correctly."""
        exception = LogException("Test error message")
        assert exception.message == "Test error message"
        assert str(exception) == "Test error message"

    def test_log_exception_can_be_raised(self) -> None:
        """Test that LogException can be raised and caught."""
        with pytest.raises(LogException) as exc_info:
            raise LogException("Error occurred")

        assert exc_info.value.message == "Error occurred"
        assert str(exc_info.value) == "Error occurred"

    def test_log_exception_inherits_from_exception(self) -> None:
        """Test that LogException inherits from Exception."""
        exception = LogException("Test")
        assert isinstance(exception, Exception)
        assert isinstance(exception, LogException)

    def test_log_exception_with_empty_message(self) -> None:
        """Test LogException with empty message."""
        exception = LogException("")
        assert exception.message == ""
        assert str(exception) == ""

    def test_log_exception_with_multiline_message(self) -> None:
        """Test LogException with multiline message."""
        message = "Line 1\nLine 2\nLine 3"
        exception = LogException(message)
        assert exception.message == message
        assert str(exception) == message


class TestConfigurationException:
    """Test cases for ConfigurationException."""

    def test_configuration_exception_includes_field_and_reason(self) -> None:
        """Test that ConfigurationException stores field and reason."""
        exception = ConfigurationException("filename", "required for FILE target")
        assert exception.field == "filename"
        assert exception.reason == "required for FILE target"

    def test_configuration_exception_formats_message_correctly(self) -> None:
        """Test that ConfigurationException formats error message correctly."""
        exception = ConfigurationException("directory", "must be a valid path")
        expected_message = "Configuration error in field 'directory': must be a valid path"
        assert exception.message == expected_message
        assert str(exception) == expected_message

    def test_configuration_exception_inherits_from_log_exception(self) -> None:
        """Test that ConfigurationException inherits from LogException."""
        exception = ConfigurationException("level", "invalid value")
        assert isinstance(exception, LogException)
        assert isinstance(exception, ConfigurationException)
        assert isinstance(exception, Exception)

    def test_configuration_exception_can_be_caught_as_log_exception(self) -> None:
        """Test that ConfigurationException can be caught as LogException."""
        with pytest.raises(LogException) as exc_info:
            raise ConfigurationException("target", "unsupported target type")

        assert isinstance(exc_info.value, ConfigurationException)
        assert exc_info.value.field == "target"

    def test_configuration_exception_with_empty_field(self) -> None:
        """Test ConfigurationException with empty field name."""
        exception = ConfigurationException("", "some reason")
        assert exception.field == ""
        assert "Configuration error in field '': some reason" == str(exception)

    def test_configuration_exception_with_empty_reason(self) -> None:
        """Test ConfigurationException with empty reason."""
        exception = ConfigurationException("field_name", "")
        assert exception.reason == ""
        assert "Configuration error in field 'field_name': " == str(exception)

    def test_configuration_exception_various_fields(self) -> None:
        """Test ConfigurationException with various field names."""
        test_cases = [
            ("filename", "is required"),
            ("directory", "does not exist"),
            ("level", "invalid log level"),
            ("target", "unsupported output target"),
            ("format", "invalid format string"),
        ]

        for field, reason in test_cases:
            exception = ConfigurationException(field, reason)
            assert exception.field == field
            assert exception.reason == reason
            assert field in str(exception)
            assert reason in str(exception)


class TestHandlerException:
    """Test cases for HandlerException."""

    def test_handler_exception_includes_handler_type_and_reason(self) -> None:
        """Test that HandlerException stores handler_type and reason."""
        exception = HandlerException("FileHandler", "permission denied")
        assert exception.handler_type == "FileHandler"
        assert exception.reason == "permission denied"

    def test_handler_exception_formats_message_correctly(self) -> None:
        """Test that HandlerException formats error message correctly."""
        exception = HandlerException("StreamHandler", "output stream closed")
        expected_message = "Handler error in 'StreamHandler': output stream closed"
        assert exception.message == expected_message
        assert str(exception) == expected_message

    def test_handler_exception_inherits_from_log_exception(self) -> None:
        """Test that HandlerException inherits from LogException."""
        exception = HandlerException("Handler", "error")
        assert isinstance(exception, LogException)
        assert isinstance(exception, HandlerException)
        assert isinstance(exception, Exception)

    def test_handler_exception_can_be_caught_as_log_exception(self) -> None:
        """Test that HandlerException can be caught as LogException."""
        with pytest.raises(LogException) as exc_info:
            raise HandlerException("JSONHandler", "invalid JSON")

        assert isinstance(exc_info.value, HandlerException)
        assert exc_info.value.handler_type == "JSONHandler"

    def test_handler_exception_with_empty_handler_type(self) -> None:
        """Test HandlerException with empty handler type."""
        exception = HandlerException("", "some reason")
        assert exception.handler_type == ""
        assert "Handler error in '': some reason" == str(exception)

    def test_handler_exception_with_empty_reason(self) -> None:
        """Test HandlerException with empty reason."""
        exception = HandlerException("CustomHandler", "")
        assert exception.reason == ""
        assert "Handler error in 'CustomHandler': " == str(exception)

    def test_handler_exception_various_handlers(self) -> None:
        """Test HandlerException with various handler types."""
        test_cases = [
            ("ConsoleHandler", "cannot write to console"),
            ("FileHandler", "file not found"),
            ("JSONFormatter", "serialization failed"),
            ("StreamHandler", "stream error"),
            ("RotatingFileHandler", "rotation failed"),
        ]

        for handler_type, reason in test_cases:
            exception = HandlerException(handler_type, reason)
            assert exception.handler_type == handler_type
            assert exception.reason == reason
            assert handler_type in str(exception)
            assert reason in str(exception)


class TestExceptionHierarchy:
    """Test cases for exception hierarchy and relationships."""

    def test_all_exceptions_inherit_from_log_exception(self) -> None:
        """Test that all custom exceptions inherit from LogException."""
        config_exc = ConfigurationException("field", "reason")
        handler_exc = HandlerException("handler", "reason")

        assert isinstance(config_exc, LogException)
        assert isinstance(handler_exc, LogException)

    def test_exceptions_can_be_caught_together(self) -> None:
        """Test that all exceptions can be caught with LogException."""
        exceptions = [
            LogException("base error"),
            ConfigurationException("field", "reason"),
            HandlerException("handler", "reason"),
        ]

        for exc in exceptions:
            with pytest.raises(LogException):
                raise exc

    def test_exceptions_can_be_distinguished(self) -> None:
        """Test that different exception types can be distinguished."""
        try:
            raise ConfigurationException("field", "reason")
        except HandlerException:
            pytest.fail("Should not catch as HandlerException")
        except ConfigurationException as e:
            assert e.field == "field"

        try:
            raise HandlerException("handler", "reason")
        except ConfigurationException:
            pytest.fail("Should not catch as ConfigurationException")
        except HandlerException as e:
            assert e.handler_type == "handler"

    def test_exception_message_attribute_consistency(self) -> None:
        """Test that all exceptions have consistent message attribute."""
        log_exc = LogException("test message")
        config_exc = ConfigurationException("field", "reason")
        handler_exc = HandlerException("handler", "reason")

        assert hasattr(log_exc, "message")
        assert hasattr(config_exc, "message")
        assert hasattr(handler_exc, "message")

        assert log_exc.message == "test message"
        assert "field" in config_exc.message
        assert "handler" in handler_exc.message
