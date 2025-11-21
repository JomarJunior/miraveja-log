# 📝 miraveja-log

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)](#-development-status)
[![Coverage](https://codecov.io/gh/JomarJunior/miraveja-log/branch/main/graph/badge.svg)](https://codecov.io/gh/JomarJunior/miraveja-log)
[![CI](https://github.com/JomarJunior/miraveja-log/actions/workflows/ci.yml/badge.svg)](https://github.com/JomarJunior/miraveja-log/actions)

> A lightweight and flexible logging library with structured logging support for Python

**Etymology**: Combining "logging" with the Miraveja ecosystem naming convention

## 🚀 Overview

miraveja-log is a modern logging library that provides a clean, configurable interface for application logging. Built with DDD/Hexagonal Architecture principles, it offers flexible output targets, environment-based configuration, and structured logging capabilities.

Part of the **Miraveja** ecosystem, miraveja-log provides logging infrastructure for all ecosystem services.

## ✨ Key Features

- 🎯 **Clean Interface** - Simple, intuitive ILogger interface for all logging needs
- 📊 **Multiple Targets** - Console, file, and JSON output support
- ⚙️ **Environment Config** - Load configuration from environment variables
- 🏗️ **Factory Pattern** - Easy logger creation with sensible defaults
- 🔄 **Structured Logging** - Support for contextual log data
- 🧪 **Testing Utilities** - Built-in mocking and testing capabilities
- 🏛️ **Clean Architecture** - Organized following DDD/Hexagonal Architecture principles

## 🛠️ Technology Stack

### 🐍 Core Runtime

- **Python 3.10+** - Type hints and modern Python features
- **typing-extensions** - Compatibility for Python 3.8-3.9
- **pydantic** - Configuration validation and modeling

### 🧪 Development

- **pytest** - Testing framework with async support
- **pytest-asyncio** - Async testing utilities
- **pytest-cov** - Coverage reporting
- **black** - Code formatter
- **pylint** - Code quality checker
- **isort** - Import statement organizer
- **pre-commit** - Git hook framework for automated checks

## 🏛️ Architecture

miraveja-log follows Domain-Driven Design and Hexagonal Architecture principles:

```text
src/miraveja_log/
├── 🧠 domain/           # Core business logic (models, enums, interfaces, exceptions)
├── 🎬 application/      # Use cases (configuration, factory)
└── 🔌 infrastructure/   # External integrations (future: FastAPI, Django)
```

**Dependency Rule**: Domain ← Application ← Infrastructure

- **Domain** has no dependencies on other layers
- **Application** depends only on Domain
- **Infrastructure** depends on Application and Domain

## 🎯 Getting Started

### 📋 Prerequisites

- Python 3.10+
- Poetry 2.0+ (recommended) or pip

### 🚀 Installation

```bash
poetry add miraveja-log
```

Or with pip:

```bash
pip install miraveja-log
```

## 📖 Quick Start

### Basic Usage

```python
from miraveja_log import LoggerFactory, LoggerConfig, LogLevel, OutputTarget
from miraveja_log.infrastructure.adapters import PythonLoggerAdapter, AsyncPythonLoggerAdapter

# Create a simple console logger
factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
config = LoggerConfig(name="my_app")
logger = factory.get_or_create_logger(config)

# Log messages at different levels
logger.info("Application started")
logger.debug("Debug information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical system failure")
```

### File Logging

```python
from pathlib import Path
from miraveja_log import LoggerFactory, LoggerConfig, LogLevel, OutputTarget
from miraveja_log.infrastructure.adapters import PythonLoggerAdapter, AsyncPythonLoggerAdapter

# Create a file logger with custom configuration
factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
config = LoggerConfig(
    name="my_app",
    level=LogLevel.DEBUG,
    output_target=OutputTarget.FILE,
    directory=Path("./logs"),
    filename="app.log",
    log_format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    date_format="%Y-%m-%d %H:%M:%S"
)
logger = factory.get_or_create_logger(config)

logger.info("This will be written to the log file")
```

### JSON Logging with Structured Data

```python
from pathlib import Path
from miraveja_log import LoggerFactory, LoggerConfig, OutputTarget
from miraveja_log.infrastructure.adapters import PythonLoggerAdapter, AsyncPythonLoggerAdapter

# Create a JSON logger for structured logging
factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
config = LoggerConfig(
    name="my_app",
    output_target=OutputTarget.JSON,
    directory=Path("./logs"),
    filename="app.json"
)
logger = factory.get_or_create_logger(config)

# Log with structured data - extra fields are merged at top level
logger.info(
    "User logged in",
    extra={
        "user_id": 12345,
        "username": "john_doe",
        "ip_address": "192.168.1.1"
    }
)
# JSON output: {"timestamp": "2025-11-21T...", "level": "INFO", "name": "my_app",
#               "message": "User logged in", "user_id": 12345, "username": "john_doe", ...}
```

### Environment-Based Configuration

```python
import os
from miraveja_log import LoggerFactory, LoggerConfig
from miraveja_log.infrastructure.adapters import PythonLoggerAdapter, AsyncPythonLoggerAdapter

# Set environment variables
os.environ["LOGGER_NAME"] = "my_service"
os.environ["LOGGER_LEVEL"] = "INFO"
os.environ["LOGGER_TARGET"] = "FILE"
os.environ["LOGGER_DIR"] = "./logs"
os.environ["LOGGER_FILENAME"] = "service.log"

# Load configuration from environment
config = LoggerConfig.from_env()
factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
logger = factory.get_or_create_logger(config)

logger.info("Configured from environment variables")
```

### Async Logging

```python
import asyncio
from miraveja_log import LoggerFactory, LoggerConfig
from miraveja_log.infrastructure.adapters import PythonLoggerAdapter, AsyncPythonLoggerAdapter

async def main():
    # Create an async logger
    factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
    config = LoggerConfig(name="async_app")
    logger = factory.get_or_create_async_logger(config)

    # Use async logging methods
    await logger.info("Async operation started")
    await logger.debug("Processing data asynchronously")
    await logger.info("Async operation completed")

asyncio.run(main())
```

### Exception Logging

```python
from miraveja_log import LoggerFactory, LoggerConfig
from miraveja_log.infrastructure.adapters import PythonLoggerAdapter, AsyncPythonLoggerAdapter

factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
logger = factory.get_or_create_logger(LoggerConfig(name="my_app"))

# Log exceptions with traceback
try:
    result = 10 / 0
except ZeroDivisionError:
    logger.error("Division by zero error", exc_info=True)
```

## 🔧 Configuration

### Logger Levels

miraveja-log supports standard Python logging levels:

- `LogLevel.DEBUG` - Detailed information for diagnosing problems (default)
- `LogLevel.INFO` - Confirmation that things are working as expected
- `LogLevel.WARNING` - Indication of potential problems
- `LogLevel.ERROR` - Error that caused functionality to fail
- `LogLevel.CRITICAL` - Serious error that may cause the program to abort

### Output Targets

- `OutputTarget.CONSOLE` - Output to console/stdout (default)
- `OutputTarget.FILE` - Output to a file with text formatting
- `OutputTarget.JSON` - Output to a file in JSON format (structured logging)

### Environment Variables

Configure your logger using environment variables:

```bash
# Required
LOGGER_NAME=my_service          # Logger name (default: "default_name")
LOGGER_LEVEL=INFO               # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOGGER_TARGET=CONSOLE           # Output target (CONSOLE, FILE, JSON)

# Required for FILE/JSON targets
LOGGER_DIR=./logs               # Directory for log files (resolved to absolute path)
LOGGER_FILENAME=app.log         # Log file name

# Optional formatting
LOGGER_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
LOGGER_DATEFMT=%Y-%m-%d %H:%M:%S
```

### Configuration Model

```python
from pathlib import Path
from miraveja_log import LoggerConfig, LogLevel, OutputTarget

config = LoggerConfig(
    name="my_service",
    level=LogLevel.INFO,
    output_target=OutputTarget.CONSOLE,
    log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    date_format="%Y-%m-%d %H:%M:%S",
    directory=None,  # Required for FILE/JSON targets
    filename=None    # Required for FILE/JSON targets
)

# Use with factory
from miraveja_log import LoggerFactory
from miraveja_log.infrastructure.adapters import PythonLoggerAdapter, AsyncPythonLoggerAdapter

factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
logger = factory.get_or_create_logger(config)
```

## 📚 API Reference

### LoggerFactory

Factory class for creating and caching logger instances.

**Constructor:**

```python
LoggerFactory(sync_adapter_class, async_adapter_class)
```

- `sync_adapter_class`: Class for synchronous logger adapter (e.g., `PythonLoggerAdapter`)
- `async_adapter_class`: Class for asynchronous logger adapter (e.g., `AsyncPythonLoggerAdapter`)

**Methods:**

- `get_or_create_logger(config: LoggerConfig) -> ILogger`
  - Creates or retrieves cached synchronous logger instance
  - Returns: Configured ILogger instance
  - Thread-safe with internal locking

- `get_or_create_async_logger(config: LoggerConfig) -> IAsyncLogger`
  - Creates or retrieves cached asynchronous logger instance
  - Returns: Configured IAsyncLogger instance
  - Thread-safe with internal locking

- `clear_cache() -> None`
  - Clears all cached logger instances (both sync and async)

### ILogger Interface

Abstract interface for synchronous logging operations.

**Methods:**

- `debug(msg, *args, **kwargs)` - Log debug message
- `info(msg, *args, **kwargs)` - Log info message
- `warning(msg, *args, **kwargs)` - Log warning message
- `error(msg, *args, **kwargs)` - Log error message
- `critical(msg, *args, **kwargs)` - Log critical message

**Parameters:**

- `msg`: Log message (supports string formatting with args)
- `*args`: Positional arguments for message formatting
- `**kwargs`: Keyword arguments including:
  - `extra`: Dict of extra fields for structured logging
  - `exc_info`: Include exception traceback (True/False/tuple)
  - `stack_info`: Include stack trace information
  - `stacklevel`: Stack level for correct caller info

### IAsyncLogger Interface

Abstract interface for asynchronous logging operations.

**Methods:**

All methods are async and mirror ILogger interface:

- `async debug(msg, *args, **kwargs)` - Log debug message asynchronously
- `async info(msg, *args, **kwargs)` - Log info message asynchronously
- `async warning(msg, *args, **kwargs)` - Log warning message asynchronously
- `async error(msg, *args, **kwargs)` - Log error message asynchronously
- `async critical(msg, *args, **kwargs)` - Log critical message asynchronously

### LoggerConfig

Pydantic model for logger configuration with validation.

**Fields:**

- `name: str` - Logger name (required)
- `level: LogLevel` - Logging level (default: DEBUG)
- `output_target: OutputTarget` - Output target (default: CONSOLE)
- `log_format: Optional[str]` - Log format string (default: standard format)
- `date_format: Optional[str]` - Date format string (default: '%Y-%m-%d %H:%M:%S')
- `directory: Optional[Path]` - Directory for log files (required for FILE/JSON)
- `filename: Optional[str]` - Log filename (required for FILE/JSON)

**Class Methods:**

- `from_env() -> LoggerConfig`
  - Creates configuration from environment variables
  - Returns: LoggerConfig instance
  - Validates required fields based on output target
  - Resolves relative paths to absolute paths

## 🔥 Advanced Usage

### Logger Caching

The factory automatically caches logger instances by name for both sync and async loggers:

```python
from miraveja_log import LoggerFactory, LoggerConfig
from miraveja_log.infrastructure.adapters import PythonLoggerAdapter, AsyncPythonLoggerAdapter

factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
config = LoggerConfig(name="cached_logger")

# First call creates the logger
logger1 = factory.get_or_create_logger(config)

# Second call returns the same cached instance
logger2 = factory.get_or_create_logger(config)

assert logger1 is logger2  # Same instance

# Clear cache if needed
factory.clear_cache()
```

### Structured Logging with JSON Output

JSON output automatically merges extra fields at the top level for easy parsing:

```python
from pathlib import Path
from miraveja_log import LoggerFactory, LoggerConfig, OutputTarget
from miraveja_log.infrastructure.adapters import PythonLoggerAdapter, AsyncPythonLoggerAdapter

factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
config = LoggerConfig(
    name="api_logger",
    output_target=OutputTarget.JSON,
    directory=Path("./logs"),
    filename="api.json"
)
logger = factory.get_or_create_logger(config)

# Log API request with structured data
logger.info(
    "API request processed",
    extra={
        "method": "POST",
        "endpoint": "/api/users",
        "status_code": 201,
        "response_time_ms": 45,
        "user_agent": "Mozilla/5.0..."
    }
)

# Output (each line is valid JSON):
# {"timestamp": "2025-11-21T10:30:45.123456", "level": "INFO", "name": "api_logger",
#  "message": "API request processed", "method": "POST", "endpoint": "/api/users",
#  "status_code": 201, "response_time_ms": 45, "user_agent": "Mozilla/5.0..."}
```

### Multiple Loggers for Different Purposes

```python
from pathlib import Path
from miraveja_log import LoggerFactory, LoggerConfig, LogLevel, OutputTarget
from miraveja_log.infrastructure.adapters import PythonLoggerAdapter, AsyncPythonLoggerAdapter

factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)

# Application logger - console output
app_logger = factory.get_or_create_logger(
    LoggerConfig(name="app", level=LogLevel.INFO)
)

# Error logger - file output
error_logger = factory.get_or_create_logger(
    LoggerConfig(
        name="errors",
        level=LogLevel.ERROR,
        output_target=OutputTarget.FILE,
        directory=Path("./logs"),
        filename="errors.log"
    )
)

# Audit logger - JSON output
audit_logger = factory.get_or_create_logger(
    LoggerConfig(
        name="audit",
        output_target=OutputTarget.JSON,
        directory=Path("./logs"),
        filename="audit.json"
    )
)

app_logger.info("Application started")
error_logger.error("Critical error occurred")
audit_logger.info("User action", extra={"user_id": 123, "action": "login"})
```

### Exception Handling with Async Logging

```python
import asyncio
from miraveja_log import LoggerFactory, LoggerConfig
from miraveja_log.infrastructure.adapters import PythonLoggerAdapter, AsyncPythonLoggerAdapter

async def process_data():
    factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
    logger = factory.get_or_create_async_logger(LoggerConfig(name="async_app"))

    try:
        await logger.info("Starting data processing")
        # Simulate error
        result = 1 / 0
    except ZeroDivisionError:
        # Exception context is preserved even in async logging
        await logger.error("Processing failed", exc_info=True)
    finally:
        await logger.info("Cleanup completed")

asyncio.run(process_data())
```

### Custom Format Strings

```python
from pathlib import Path
from miraveja_log import LoggerFactory, LoggerConfig, OutputTarget
from miraveja_log.infrastructure.adapters import PythonLoggerAdapter, AsyncPythonLoggerAdapter

factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)

# Minimal format
minimal_logger = factory.get_or_create_logger(
    LoggerConfig(
        name="minimal",
        log_format="%(levelname)s: %(message)s"
    )
)

# Detailed format with module and function info
detailed_logger = factory.get_or_create_logger(
    LoggerConfig(
        name="detailed",
        log_format="%(asctime)s [%(levelname)-8s] %(name)s.%(funcName)s:%(lineno)d - %(message)s",
        date_format="%Y-%m-%d %H:%M:%S"
    )
)

minimal_logger.info("Simple message")
# Output: INFO: Simple message

detailed_logger.info("Detailed message")
# Output: 2025-11-21 10:30:45 [INFO    ] detailed.my_function:42 - Detailed message
```

## 📂 Examples

Complete working examples are available in the `examples/` directory:

- **`basic_usage.py`** - Console, file, and JSON logging examples
- **`async_usage.py`** - Async logging with concurrent tasks

Run examples:

```bash
# Basic examples
poetry run python examples/basic_usage.py

# Async examples
poetry run python examples/async_usage.py
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src/miraveja_log --cov-report=html

# Run specific test file
poetry run pytest tests/unit/miraveja_log/application/test_configuration.py

# Run with verbose output
poetry run pytest -v

# Run integration tests only
poetry run pytest tests/integration

# Run unit tests only
poetry run pytest tests/unit
```

### Test Structure

```bash
tests/
├── unit/                      # Unit tests
│   └── miraveja_log/
│       ├── domain/           # Domain layer tests
│       └── application/      # Application layer tests
└── integration/              # Integration tests
    └── miraveja_log/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/JomarJunior/miraveja-log.git
cd miraveja-log

# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Run tests
poetry run pytest --cov=src/miraveja_log
```

### Code Quality

```bash
# Format code
poetry run black src tests

# Sort imports
poetry run isort src tests

# Run linter
poetry run pylint src/miraveja_log

# Run type checker
poetry run mypy src/miraveja_log
```

## 📊 Development Status

miraveja-log is actively developed and maintained. Current status: **Beta**

### Roadmap

- ✅ Core logging functionality
- ✅ Multiple output targets (console, file, JSON)
- ✅ Environment-based configuration
- ✅ Structured logging support (extra fields merged at top level)
- ✅ Async logging support
- ✅ Logger caching and factory pattern
- ✅ Thread-safe operations
- ✅ Exception context preservation in async logging
- 🚧 FastAPI integration
- 🚧 Django integration
- 🚧 Log rotation and archiving
- 🚧 Cloud logging integration (AWS CloudWatch, Google Cloud Logging)
- 🚧 Sensitive data filtering

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built as part of the Miraveja ecosystem
- Inspired by Python's standard logging module
- Follows DDD/Hexagonal Architecture principles

## 📞 Contact

- **Author**: Jomar Júnior de Souza Pereira
- **Email**: <jomarjunior@poli.ufrj.br>
- **Repository**: <https://github.com/JomarJunior/miraveja-log>

## 🔗 Related Projects

- [miraveja-di](https://github.com/JomarJunior/miraveja-di) - Dependency Injection container
- [miraveja](https://github.com/JomarJunior/miraveja) - Main Miraveja project

---

Made with ❤️ for the Miraveja ecosystem
