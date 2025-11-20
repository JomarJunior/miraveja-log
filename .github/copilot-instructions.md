# GitHub Copilot Instructions for miraveja-log

## Project Overview

miraveja-log is a lightweight and flexible logging library with structured logging support for Python. It follows DDD/Hexagonal Architecture principles with clear separation between Domain, Application, and Infrastructure layers. Part of the Miraveja ecosystem.

## Architecture Principles

### Layered Architecture
- **Domain Layer** (`src/miraveja_log/domain/`): Core business logic, models, enums, interfaces, and exceptions. NO dependencies on other layers.
- **Application Layer** (`src/miraveja_log/application/`): Use cases and orchestration. Depends ONLY on Domain layer.
- **Infrastructure Layer** (`src/miraveja_log/infrastructure/`): External integrations (FastAPI, Django, etc.). Depends on Application and Domain layers.

**Dependency Rule**: Domain ← Application ← Infrastructure

### Key Design Patterns
- **Factory Pattern**: LoggerFactory for creating configured loggers
- **Strategy Pattern**: Different output targets (console, file, JSON)
- **Configuration Pattern**: Environment-based configuration with sensible defaults
- **Interface Segregation**: Clean ILogger interface for domain contracts

## Code Style Guidelines

### Python Standards
- **Python Version**: 3.10+ (use modern type hints)
- **Line Length**: 120 characters maximum
- **Formatter**: black
- **Import Sorter**: isort (black profile)
- **Linter**: pylint
- **Type Checker**: mypy with strict mode

### Naming Conventions
- **Modules**: `snake_case` (e.g., `logger_factory.py`, `configuration.py`)
- **Classes**: `PascalCase` (e.g., `LoggerConfig`, `LoggerFactory`)
- **Functions/Methods**: `snake_case` (e.g., `create_logger`, `from_env`)
- **Constants**: `UPPER_CASE` (e.g., `DEFAULT_FORMAT`, `DEFAULT_HANDLER`)
- **Private members**: Prefix with `_` (e.g., `_logger`, `_configure_logging`)

### Type Hints
- **Always use type hints** for function parameters and return types
- Use `from typing import` for complex types (Dict, List, Optional, Callable, etc.)
- Use `typing-extensions` for compatibility features
- Generic types: Use `TypeVar` for generic operations if needed

Example:
```python
from typing import Any, Dict, Optional, Tuple

def create_logger(
    name: str = "miraveja",
    level: LoggerLevel = LoggerLevel.INFO,
    target: LoggerTarget = LoggerTarget.CONSOLE,
    format: Optional[str] = None,
) -> ILogger:
    """Create and configure a logger instance."""
    pass
```

## Domain Layer Components

### Enums
- `LoggerLevel`: DEBUG, INFO, WARNING, ERROR, CRITICAL
- `LoggerTarget`: CONSOLE, FILE, JSON

### Interfaces
- `ILogger`: Abstract interface for logging operations
  - Methods: `debug()`, `info()`, `warning()`, `error()`, `critical()`

### Models
- `Logger`: Concrete implementation of ILogger using Python's logging module

### Exceptions
- `LoggerException`: Base exception for logging-related errors
- `LoggerAlreadyExistsException`: Raised when attempting to create duplicate logger

## Application Layer Components

### Configuration
- `LoggerConfig`: Pydantic model for logger configuration
  - Environment-based configuration via `from_env()` class method
  - Automatic directory creation for file-based logging
  - Validation for required fields based on target

### Factory
- `LoggerFactory`: Creates and configures logger instances
  - `create_logger()`: Factory method with fluent configuration
  - Target-specific handler mapping
  - Default format and date format configuration

## Configuration Pattern

### Environment Variables
```python
LOGGER_NAME=my_service
LOGGER_LEVEL=INFO
LOGGER_TARGET=CONSOLE
LOGGER_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
LOGGER_DATEFMT=%Y-%m-%d %H:%M:%S
LOGGER_DIR=./logs
LOGGER_FILENAME=app.log
```

### Usage Pattern
```python
from miraveja_log import LoggerFactory, LoggerConfig

# From environment variables
config = LoggerConfig.from_env(default_name="my_service")
logger = LoggerFactory.create_logger(**config.model_dump())

# Direct configuration
logger = LoggerFactory.create_logger(
    name="my_service",
    level=LoggerLevel.INFO,
    target=LoggerTarget.CONSOLE
)

logger.info("Application started")
```

## Testing Standards

### Test Organization
- **Unit Tests**: `tests/unit/miraveja_log/{layer}/` - Isolated component testing
- **Integration Tests**: `tests/integration/miraveja_log/` - Cross-layer scenarios
- Mirror source structure in test directories

### Test Naming
- Test files: `test_{module_name}.py`
- Test classes: `Test{ClassName}`
- Test functions: `test_{behavior}_when_{condition}`

Example:
```python
def test_create_logger_returns_logger_when_valid_config():
    """Test that create_logger returns a valid logger instance."""
    pass

def test_from_env_raises_error_when_file_target_without_filename():
    """Test that from_env validates filename for file targets."""
    pass
```

### Test Coverage
- Maintain minimum 80% code coverage
- Focus on business logic and edge cases
- Mock external dependencies (file system, environment variables)

## Code Quality Standards

### Linting Rules
- Follow PEP 8 with 120 character line length
- No missing docstrings for public APIs (disable only for tests)
- Maximum function complexity: 10
- Use type hints consistently

### Pre-commit Hooks
- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON validation
- Black formatting
- isort import sorting
- No debug statements in committed code

## Common Patterns

### Creating a Logger
```python
# Simple console logger
logger = LoggerFactory.create_logger(name="my_app")

# File logger with custom format
logger = LoggerFactory.create_logger(
    name="my_app",
    level=LoggerLevel.DEBUG,
    target=LoggerTarget.FILE,
    filename="./logs/app.log",
    format="%(asctime)s [%(levelname)s] %(message)s"
)
```

### Using Configuration
```python
# Environment-based configuration
config = LoggerConfig.from_env(
    default_name="my_service",
    default_target=LoggerTarget.FILE
)
logger = LoggerFactory.create_logger(**config.model_dump())
```

### Logging Messages
```python
logger.debug("Detailed debug information")
logger.info("General information", extra={"user_id": 123})
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)
logger.critical("Critical system failure")
```

## Development Workflow

### Setting Up Environment
```bash
# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src/miraveja_log --cov-report=html
```

### Before Committing
```bash
# Format code
poetry run black src tests

# Sort imports
poetry run isort src tests

# Run linter
poetry run pylint src/miraveja_log

# Run type checker
poetry run mypy src/miraveja_log

# Run all tests
poetry run pytest --cov=src/miraveja_log
```

## Integration Guidelines

### FastAPI Integration (Future)
- Create dependency injection helper for logger instances
- Provide request-scoped loggers with correlation IDs
- Automatic exception logging middleware

### Django Integration (Future)
- Django settings integration
- Custom logging configuration
- Template filters for log formatting

## Documentation Standards

### Docstrings
- Use Google-style docstrings
- Include Args, Returns, Raises sections
- Provide usage examples for complex functions

Example:
```python
def create_logger(
    name: str = "miraveja",
    level: LoggerLevel = LoggerLevel.INFO,
    target: LoggerTarget = LoggerTarget.CONSOLE,
) -> ILogger:
    """
    Create and configure a logger instance.

    Args:
        name: Name of the logger (default: "miraveja")
        level: Logging level (default: LoggerLevel.INFO)
        target: Output target (default: LoggerTarget.CONSOLE)

    Returns:
        Configured ILogger instance

    Raises:
        LoggerAlreadyExistsException: If logger with given name exists

    Example:
        >>> logger = create_logger(name="my_app", level=LoggerLevel.DEBUG)
        >>> logger.info("Hello, World!")
    """
    pass
```

## Version Control

### Branching Strategy
- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `hotfix/*`: Emergency production fixes

### Commit Messages
- Use conventional commits format
- Examples:
  - `feat: add JSON logging target`
  - `fix: handle missing filename for file targets`
  - `docs: update README with configuration examples`
  - `test: add unit tests for LoggerFactory`
  - `refactor: simplify configuration validation`

## Performance Considerations

- Lazy initialization of loggers
- Efficient handler reuse
- Minimal overhead for disabled log levels
- Proper resource cleanup for file handlers

## Security Considerations

- Never log sensitive information (passwords, tokens, PII)
- Sanitize user input in log messages
- Proper file permissions for log files
- Rotate logs to prevent disk space exhaustion
