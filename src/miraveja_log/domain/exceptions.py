class LogException(Exception):
    """Base exception for logging-related errors."""

    def __init__(self, message: str) -> None:
        self.message: str = message
        super().__init__(message)


class ConfigurationException(LogException):
    """Exception raised for configuration-related errors in logging."""

    def __init__(self, field: str, reason: str) -> None:
        self.field: str = field
        self.reason: str = reason
        message: str = f"Configuration error in field '{field}': {reason}"
        super().__init__(message)


class HandlerException(LogException):
    """Exception raised for errors related to log handlers."""

    def __init__(self, handler_type: str, reason: str) -> None:
        self.handler_type: str = handler_type
        self.reason: str = reason
        message: str = f"Handler error in '{handler_type}': {reason}"
        super().__init__(message)
