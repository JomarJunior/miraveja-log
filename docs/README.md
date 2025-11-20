# miraveja-log Documentation

## Overview

miraveja-log is a lightweight and flexible logging library designed following Domain-Driven Design (DDD) and Hexagonal Architecture principles.

## Architecture

### Layers

1. **Domain Layer** - Core business logic
   - Enums: `LoggerLevel`, `LoggerTarget`
   - Interfaces: `ILogger`
   - Models: `Logger`
   - Exceptions: `LoggerException`, `LoggerAlreadyExistsException`

2. **Application Layer** - Use cases and orchestration
   - Configuration: `LoggerConfig`
   - Factory: `LoggerFactory`

3. **Infrastructure Layer** - External integrations (future)
   - FastAPI integration (planned)
   - Django integration (planned)

## Design Patterns

### Factory Pattern

The `LoggerFactory` provides a clean way to create and configure logger instances:

```python
logger = LoggerFactory.create_logger(
    name="my_app",
    level=LoggerLevel.INFO,
    target=LoggerTarget.CONSOLE
)
```

### Strategy Pattern

Different logging targets (console, file, JSON) are handled through the strategy pattern, making it easy to add new targets.

### Configuration Pattern

Environment-based configuration allows for flexible deployment:

```python
config = LoggerConfig.from_env(default_name="my_service")
logger = LoggerFactory.create_logger(**config.model_dump())
```

## Usage Examples

### Basic Console Logging

```python
from miraveja_log import LoggerFactory, LoggerLevel

logger = LoggerFactory.create_logger(
    name="my_app",
    level=LoggerLevel.DEBUG
)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

### File Logging

```python
from miraveja_log import LoggerFactory, LoggerLevel, LoggerTarget

logger = LoggerFactory.create_logger(
    name="my_app",
    level=LoggerLevel.INFO,
    target=LoggerTarget.FILE,
    filename="./logs/app.log"
)

logger.info("This goes to file")
```

### Environment Configuration

```bash
export LOGGER_NAME=my_service
export LOGGER_LEVEL=INFO
export LOGGER_TARGET=FILE
export LOGGER_DIR=./logs
export LOGGER_FILENAME=service.log
```

```python
from miraveja_log import LoggerConfig, LoggerFactory

config = LoggerConfig.from_env()
logger = LoggerFactory.create_logger(**config.model_dump())
```

### Structured Logging

```python
logger.info(
    "User action",
    extra={
        "user_id": 123,
        "action": "login",
        "ip": "192.168.1.1"
    }
)
```

## Testing

The package includes comprehensive unit and integration tests:

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src/miraveja_log --cov-report=html

# Run specific layer tests
poetry run pytest tests/unit/miraveja_log/domain/
poetry run pytest tests/unit/miraveja_log/application/
```

## Future Enhancements

- FastAPI dependency injection integration
- Django logging configuration
- Async logging support
- Custom JSON formatter for structured logging
- Log rotation and archiving
- Cloud logging integration (AWS CloudWatch, Google Cloud Logging)
- Correlation ID support for distributed tracing
