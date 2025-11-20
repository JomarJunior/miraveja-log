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
from miraveja_log import LoggerFactory, LoggerLevel, LoggerTarget

# Create a simple console logger
logger = LoggerFactory.create_logger(name="my_app")

# Log messages at different levels
logger.info("Application started")
logger.debug("Debug information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical system failure")
```

### File Logging

```python
from miraveja_log import LoggerFactory, LoggerLevel, LoggerTarget

# Create a file logger with custom configuration
logger = LoggerFactory.create_logger(
    name="my_app",
    level=LoggerLevel.DEBUG,
    target=LoggerTarget.FILE,
    filename="./logs/app.log",
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger.info("This will be written to the log file")
```

### Environment-Based Configuration

```python
import os
from miraveja_log import LoggerFactory, LoggerConfig

# Set environment variables
os.environ["LOGGER_NAME"] = "my_service"
os.environ["LOGGER_LEVEL"] = "INFO"
os.environ["LOGGER_TARGET"] = "FILE"
os.environ["LOGGER_DIR"] = "./logs"
os.environ["LOGGER_FILENAME"] = "service.log"

# Load configuration from environment
config = LoggerConfig.from_env()
logger = LoggerFactory.create_logger(**config.model_dump())

logger.info("Configured from environment variables")
```

### Structured Logging

```python
from miraveja_log import LoggerFactory

logger = LoggerFactory.create_logger(name="my_app")

# Add extra context to log messages
logger.info(
    "User logged in",
    extra={
        "user_id": 12345,
        "username": "john_doe",
        "ip_address": "192.168.1.1"
    }
)

# Log exceptions with traceback
try:
    result = 10 / 0
except ZeroDivisionError:
    logger.error("Division by zero error", exc_info=True)
```

## 🔧 Configuration

### Logger Levels

miraveja-log supports standard Python logging levels:

- `LoggerLevel.DEBUG` - Detailed information for diagnosing problems
- `LoggerLevel.INFO` - Confirmation that things are working as expected
- `LoggerLevel.WARNING` - Indication of potential problems
- `LoggerLevel.ERROR` - Error that caused functionality to fail
- `LoggerLevel.CRITICAL` - Serious error that may cause the program to abort

### Logger Targets

- `LoggerTarget.CONSOLE` - Output to console/stdout
- `LoggerTarget.FILE` - Output to a file
- `LoggerTarget.JSON` - Output to a file in JSON format (structured logging)

### Environment Variables

Configure your logger using environment variables:

```bash
# Required
LOGGER_NAME=my_service          # Logger name
LOGGER_LEVEL=INFO               # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOGGER_TARGET=CONSOLE           # Output target (CONSOLE, FILE, JSON)

# Optional (required for FILE/JSON targets)
LOGGER_DIR=./logs               # Directory for log files
LOGGER_FILENAME=app.log         # Log file name

# Optional formatting
LOGGER_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
LOGGER_DATEFMT=%Y-%m-%d %H:%M:%S
```

### Configuration Model

```python
from miraveja_log import LoggerConfig, LoggerLevel, LoggerTarget

config = LoggerConfig(
    name="my_service",
    level=LoggerLevel.INFO,
    target=LoggerTarget.CONSOLE,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=None  # Required for FILE/JSON targets
)

logger = LoggerFactory.create_logger(**config.model_dump())
```

## 📚 API Reference

### LoggerFactory

Factory class for creating logger instances.

**Methods:**

- `create_logger(name, level, target, format, datefmt, **kwargs) -> ILogger`
  - Creates and configures a new logger instance
  - Returns: Configured ILogger instance
  - Raises: `LoggerAlreadyExistsException` if logger already exists

### ILogger Interface

Abstract interface for logging operations.

**Methods:**

- `debug(msg, *args, **kwargs)` - Log debug message
- `info(msg, *args, **kwargs)` - Log info message
- `warning(msg, *args, **kwargs)` - Log warning message
- `error(msg, *args, **kwargs)` - Log error message
- `critical(msg, *args, **kwargs)` - Log critical message

### LoggerConfig

Pydantic model for logger configuration.

**Class Methods:**

- `from_env(default_name="miraveja", default_target=LoggerTarget.CONSOLE) -> LoggerConfig`
  - Creates configuration from environment variables
  - Automatically creates log directories if needed

## 🧪 Testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src/miraveja_log --cov-report=html

# Run specific test file
poetry run pytest tests/unit/test_logger_factory.py

# Run with verbose output
poetry run pytest -v
```

### Test Structure

```
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
- ✅ Structured logging support
- 🚧 FastAPI integration
- 🚧 Django integration
- 🚧 Async logging support
- 🚧 Log rotation and archiving
- 🚧 Cloud logging integration (AWS CloudWatch, Google Cloud Logging)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built as part of the Miraveja ecosystem
- Inspired by Python's standard logging module
- Follows DDD/Hexagonal Architecture principles

## 📞 Contact

- **Author**: Jomar Júnior de Souza Pereira
- **Email**: jomarjunior@poli.ufrj.br
- **Repository**: https://github.com/JomarJunior/miraveja-log

## 🔗 Related Projects

- [miraveja-di](https://github.com/JomarJunior/miraveja-di) - Dependency Injection container
- [miraveja](https://github.com/JomarJunior/miraveja) - Main Miraveja project

---

Made with ❤️ for the Miraveja ecosystem
