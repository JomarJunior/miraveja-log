"""Basic usage examples for miraveja-log."""

from pathlib import Path

from miraveja_log import LoggerConfig, LoggerFactory, LogLevel, OutputTarget
from miraveja_log.infrastructure.adapters import AsyncPythonLoggerAdapter, PythonLoggerAdapter


def example_basic_console_logging():
    """Example: Basic console logging."""
    print("\n=== Basic Console Logging ===")
    factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
    config = LoggerConfig(name="my_app")
    logger = factory.get_or_create_logger(config)

    logger.info("Application started")
    logger.debug("Debug information")
    logger.warning("Warning message")
    logger.error("Error occurred")


def example_file_logging():
    """Example: File logging with custom format."""
    print("\n=== File Logging ===")
    factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
    config = LoggerConfig(
        name="file_logger",
        level=LogLevel.DEBUG,
        output_target=OutputTarget.FILE,
        directory=Path("./logs"),
        filename="example.log",
        log_format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        date_format="%Y-%m-%d %H:%M:%S",
    )
    logger = factory.get_or_create_logger(config)

    logger.info("This will be written to ./logs/example.log")
    logger.debug("Debug information in file")
    print("Check ./logs/example.log for output")


def example_json_logging():
    """Example: JSON logging with structured data."""
    print("\n=== JSON Logging ===")
    factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
    config = LoggerConfig(
        name="json_logger",
        output_target=OutputTarget.JSON,
        directory=Path("./logs"),
        filename="example.json",
    )
    logger = factory.get_or_create_logger(config)

    logger.info(
        "User action",
        extra={
            "user_id": 12345,
            "username": "john_doe",
            "action": "login",
            "ip_address": "192.168.1.1",
        },
    )
    print("Check ./logs/example.json for structured JSON output")


def example_exception_logging():
    """Example: Exception logging with traceback."""
    print("\n=== Exception Logging ===")
    factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
    logger = factory.get_or_create_logger(LoggerConfig(name="error_logger"))

    try:
        result = 10 / 0
        return result
    except ZeroDivisionError:
        logger.error("Division by zero error", exc_info=True)


def example_logger_caching():
    """Example: Logger caching."""
    print("\n=== Logger Caching ===")
    factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
    config = LoggerConfig(name="cached_logger")

    # First call creates the logger
    logger1 = factory.get_or_create_logger(config)
    logger1.info("Message from logger1")

    # Second call returns the same cached instance
    logger2 = factory.get_or_create_logger(config)
    logger2.info("Message from logger2")

    print(f"Same instance: {logger1 is logger2}")


if __name__ == "__main__":
    print("miraveja-log Examples\n")

    example_basic_console_logging()
    example_file_logging()
    example_json_logging()
    example_exception_logging()
    example_logger_caching()

    print("\n✅ All examples completed!")
