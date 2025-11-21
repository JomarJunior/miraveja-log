from enum import Enum


class LogLevel(str, Enum):
    """Defines the logging level."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    def __str__(self) -> str:
        return self.value


class OutputTarget(str, Enum):
    """Defines the output target for logs."""

    CONSOLE = "CONSOLE"
    FILE = "FILE"
    JSON = "JSON"

    def __str__(self) -> str:
        return self.value
