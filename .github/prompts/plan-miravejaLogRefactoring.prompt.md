# Complete Refactoring Plan: miraveja-log

## Project Goal

Rebuild miraveja-log from scratch as a lightweight logging abstraction for the Miraveja ecosystem with both synchronous and asynchronous support. Follow DDD/Hexagonal Architecture and TDD patterns from miraveja-di, targeting 96%+ test coverage with maximum simplicity.

**Primary Goal**: "An abstraction of the logging for the miraveja ecosystem. A lightweight and flexible logging library with structured logging support for Python"

## Architecture Principles

### Layered Architecture (DDD/Hexagonal)
- **Domain Layer** (`src/miraveja_log/domain/`): Core business logic, models, enums, interfaces, and exceptions. NO dependencies on other layers.
- **Application Layer** (`src/miraveja_log/application/`): Use cases and orchestration (factories, configuration). Depends ONLY on Domain layer.
- **Infrastructure Layer** (`src/miraveja_log/infrastructure/`): External integrations (Python logging, file system, formatters). Depends on Application and Domain layers.

**Dependency Rule**: Domain ← Application ← Infrastructure

### Design Patterns
- **Factory Pattern**: LoggerFactory for creating configured loggers
- **Strategy Pattern**: Different output targets (console, file, JSON) and formatters
- **Adapter Pattern**: Wrapping Python's logging module
- **Composition Over Inheritance**: Build through composition
- **Interface Segregation**: Clean ILogger and IAsyncLogger interfaces

## Implementation Steps

### Step 1: Define Domain Layer

#### 1.1 Domain Enums (`domain/enums.py`)
**Purpose**: Define core value types for the domain

```python
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
    """Defines where logs are output."""
    CONSOLE = "CONSOLE"
    FILE = "FILE"
    JSON = "JSON"

    def __str__(self) -> str:
        return self.value
```

**Tests to write** (`tests/unit/miraveja_log/domain/test_enums.py`):
- `test_log_level_values_are_uppercase_strings()`
- `test_log_level_str_returns_value()`
- `test_output_target_has_three_values()`
- `test_output_target_str_returns_value()`
- `test_log_level_can_be_compared()`

#### 1.2 Domain Interfaces (`domain/interfaces.py`)
**Purpose**: Define contracts for logging operations

```python
class ILogger(ABC):
    """Abstract interface for synchronous logging operations."""

    @abstractmethod
    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a debug message."""

    @abstractmethod
    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an info message."""

    @abstractmethod
    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a warning message."""

    @abstractmethod
    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an error message."""

    @abstractmethod
    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a critical message."""

class IAsyncLogger(ABC):
    """Abstract interface for asynchronous logging operations."""

    @abstractmethod
    async def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a debug message asynchronously."""

    @abstractmethod
    async def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an info message asynchronously."""

    @abstractmethod
    async def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a warning message asynchronously."""

    @abstractmethod
    async def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an error message asynchronously."""

    @abstractmethod
    async def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a critical message asynchronously."""
```

**Tests to write** (`tests/unit/miraveja_log/domain/test_interfaces.py`):
- `test_ilogger_is_abstract_base_class()`
- `test_ilogger_cannot_be_instantiated()`
- `test_iasync_logger_is_abstract_base_class()`
- `test_iasync_logger_has_async_methods()`
- `test_concrete_implementation_must_implement_all_methods()`

#### 1.3 Domain Models (`domain/models.py`)
**Purpose**: Define value objects and domain entities

```python
class LogEntry(BaseModel):
    """Value object representing a single log entry."""
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    timestamp: datetime = Field(..., description="When the log was created")
    level: LogLevel = Field(..., description="Log level")
    name: str = Field(..., description="Logger name")
    message: str = Field(..., description="Log message")
    extra: Dict[str, Any] = Field(default_factory=dict, description="Additional context")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": str(self.level),
            "name": self.name,
            "message": self.message,
            **self.extra  # Merge extra dict at top level (flat structure)
        }
```

**Tests to write** (`tests/unit/miraveja_log/domain/test_models.py`):
- `test_log_entry_is_frozen_when_created()`
- `test_log_entry_requires_timestamp_level_name_message()`
- `test_log_entry_extra_defaults_to_empty_dict()`
- `test_log_entry_to_dict_returns_flat_structure()`
- `test_log_entry_to_dict_merges_extra_at_top_level()`
- `test_log_entry_timestamp_serializes_to_isoformat()`

#### 1.4 Domain Exceptions (`domain/exceptions.py`)
**Purpose**: Define domain-specific exceptions with rich context

```python
class LogException(Exception):
    """Base exception for all logging-related errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

class ConfigurationException(LogException):
    """Raised when logger configuration is invalid."""

    def __init__(self, field: str, reason: str) -> None:
        self.field = field
        self.reason = reason
        message = f"Configuration error for '{field}': {reason}"
        super().__init__(message)

class HandlerException(LogException):
    """Raised when a log handler encounters an error."""

    def __init__(self, handler_type: str, reason: str) -> None:
        self.handler_type = handler_type
        self.reason = reason
        message = f"Handler '{handler_type}' error: {reason}"
        super().__init__(message)
```

**Tests to write** (`tests/unit/miraveja_log/domain/test_exceptions.py`):
- `test_log_exception_stores_message()`
- `test_configuration_exception_includes_field_and_reason()`
- `test_configuration_exception_formats_message_correctly()`
- `test_handler_exception_includes_handler_type_and_reason()`
- `test_all_exceptions_inherit_from_log_exception()`

#### 1.5 Domain Layer Export (`domain/__init__.py`)
```python
"""
Domain layer - Core business logic and models.

This layer contains the fundamental business rules and models for logging.
It has no dependencies on other layers.
"""

from .enums import LogLevel, OutputTarget
from .exceptions import ConfigurationException, HandlerException, LogException
from .interfaces import IAsyncLogger, ILogger
from .models import LogEntry

# Rebuild Pydantic models to resolve forward references
LogEntry.model_rebuild()

__all__ = [
    # Enums
    "LogLevel",
    "OutputTarget",
    # Interfaces
    "ILogger",
    "IAsyncLogger",
    # Models
    "LogEntry",
    # Exceptions
    "LogException",
    "ConfigurationException",
    "HandlerException",
]
```

---

### Step 2: Build Application Layer

#### 2.1 Application Configuration (`application/configuration.py`)
**Purpose**: Manage logger configuration with environment variable support

```python
class LoggerConfig(BaseModel):
    """Configuration model for logger creation."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = Field(..., description="Logger name")
    level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    target: OutputTarget = Field(default=OutputTarget.CONSOLE, description="Output target")
    format: Optional[str] = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )
    datefmt: Optional[str] = Field(
        default="%Y-%m-%d %H:%M:%S",
        description="Date format string"
    )
    directory: Optional[Path] = Field(default=None, description="Log directory for FILE/JSON targets")
    filename: Optional[str] = Field(default=None, description="Log filename for FILE/JSON targets")

    @field_validator("directory")
    @classmethod
    def validate_directory_for_file_targets(cls, v: Optional[Path], info: ValidationInfo) -> Optional[Path]:
        """Validate directory is provided for FILE/JSON targets."""
        target = info.data.get("target")
        if target in (OutputTarget.FILE, OutputTarget.JSON) and v is None:
            raise ConfigurationException("directory", "required for FILE and JSON targets")
        return v

    @field_validator("filename")
    @classmethod
    def validate_filename_for_file_targets(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        """Validate filename is provided for FILE/JSON targets."""
        target = info.data.get("target")
        if target in (OutputTarget.FILE, OutputTarget.JSON) and not v:
            raise ConfigurationException("filename", "required for FILE and JSON targets")
        return v

    @classmethod
    def from_env(
        cls,
        default_name: str = "miraveja",
        default_level: LogLevel = LogLevel.INFO,
        default_target: OutputTarget = OutputTarget.CONSOLE
    ) -> "LoggerConfig":
        """
        Create configuration from environment variables.

        Environment variables:
        - LOGGER_NAME: Logger name
        - LOGGER_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        - LOGGER_TARGET: Output target (CONSOLE, FILE, JSON)
        - LOGGER_FORMAT: Log format string
        - LOGGER_DATEFMT: Date format string
        - LOGGER_DIR: Log directory
        - LOGGER_FILENAME: Log filename
        """
        name = os.getenv("LOGGER_NAME", default_name)
        level_str = os.getenv("LOGGER_LEVEL", default_level.value)
        target_str = os.getenv("LOGGER_TARGET", default_target.value)

        level = LogLevel(level_str)
        target = OutputTarget(target_str)

        format_str = os.getenv("LOGGER_FORMAT")
        datefmt = os.getenv("LOGGER_DATEFMT")
        dir_str = os.getenv("LOGGER_DIR")
        filename = os.getenv("LOGGER_FILENAME")

        directory = Path(dir_str) if dir_str else None

        # Create directory if it doesn't exist and target requires it
        if directory and target in (OutputTarget.FILE, OutputTarget.JSON):
            directory.mkdir(parents=True, exist_ok=True)

        return cls(
            name=name,
            level=level,
            target=target,
            format=format_str,
            datefmt=datefmt,
            directory=directory,
            filename=filename
        )

    def get_full_path(self) -> Optional[Path]:
        """Get full path to log file."""
        if self.directory and self.filename:
            return self.directory / self.filename
        return None
```

**Tests to write** (`tests/unit/miraveja_log/application/test_configuration.py`):
- `test_logger_config_requires_name()`
- `test_logger_config_defaults_to_info_level()`
- `test_logger_config_defaults_to_console_target()`
- `test_logger_config_validates_directory_for_file_target()`
- `test_logger_config_validates_filename_for_file_target()`
- `test_from_env_loads_from_environment_variables()`
- `test_from_env_uses_defaults_when_env_not_set()`
- `test_from_env_creates_directory_when_target_is_file()`
- `test_get_full_path_returns_combined_path()`
- `test_get_full_path_returns_none_when_directory_or_filename_missing()`

#### 2.2 Application Factory (`application/logger_factory.py`)
**Purpose**: Orchestrate logger creation with proper configuration

```python
class LoggerFactory:
    """Factory for creating logger instances."""

    _logger_cache: Dict[str, Any] = {}  # Cache loggers by name
    _lock = threading.Lock()

    @classmethod
    def create_logger(
        cls,
        name: str,
        level: LogLevel = LogLevel.INFO,
        target: OutputTarget = OutputTarget.CONSOLE,
        format: Optional[str] = None,
        datefmt: Optional[str] = None,
        directory: Optional[Path] = None,
        filename: Optional[str] = None,
    ) -> ILogger:
        """
        Create and configure a synchronous logger instance.

        Args:
            name: Logger name
            level: Logging level
            target: Output target (CONSOLE, FILE, JSON)
            format: Log format string
            datefmt: Date format string
            directory: Log directory (required for FILE/JSON)
            filename: Log filename (required for FILE/JSON)

        Returns:
            Configured ILogger instance

        Raises:
            ConfigurationException: If configuration is invalid

        Example:
            >>> logger = LoggerFactory.create_logger(name="my_app")
            >>> logger.info("Hello, World!")
        """
        # Create config to validate
        config = LoggerConfig(
            name=name,
            level=level,
            target=target,
            format=format,
            datefmt=datefmt,
            directory=directory,
            filename=filename,
        )

        # Check cache
        with cls._lock:
            if name in cls._logger_cache:
                return cls._logger_cache[name]

            # Create logger adapter (infrastructure dependency injected here)
            from miraveja_log.infrastructure.adapters import PythonLoggerAdapter

            logger = PythonLoggerAdapter(config)
            cls._logger_cache[name] = logger
            return logger

    @classmethod
    def create_async_logger(
        cls,
        name: str,
        level: LogLevel = LogLevel.INFO,
        target: OutputTarget = OutputTarget.CONSOLE,
        format: Optional[str] = None,
        datefmt: Optional[str] = None,
        directory: Optional[Path] = None,
        filename: Optional[str] = None,
    ) -> IAsyncLogger:
        """
        Create and configure an asynchronous logger instance.

        Args:
            name: Logger name
            level: Logging level
            target: Output target (CONSOLE, FILE, JSON)
            format: Log format string
            datefmt: Date format string
            directory: Log directory (required for FILE/JSON)
            filename: Log filename (required for FILE/JSON)

        Returns:
            Configured IAsyncLogger instance

        Raises:
            ConfigurationException: If configuration is invalid

        Example:
            >>> logger = LoggerFactory.create_async_logger(name="my_app")
            >>> await logger.info("Hello, World!")
        """
        # Create config to validate
        config = LoggerConfig(
            name=name,
            level=level,
            target=target,
            format=format,
            datefmt=datefmt,
            directory=directory,
            filename=filename,
        )

        # Check cache with async prefix to avoid conflicts
        async_name = f"async_{name}"
        with cls._lock:
            if async_name in cls._logger_cache:
                return cls._logger_cache[async_name]

            # Create async logger adapter (infrastructure dependency injected here)
            from miraveja_log.infrastructure.adapters import AsyncPythonLoggerAdapter

            logger = AsyncPythonLoggerAdapter(config)
            cls._logger_cache[async_name] = logger
            return logger

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the logger cache. Useful for testing."""
        with cls._lock:
            cls._logger_cache.clear()
```

**Tests to write** (`tests/unit/miraveja_log/application/test_logger_factory.py`):
- `test_create_logger_returns_ilogger_instance()`
- `test_create_logger_caches_logger_by_name()`
- `test_create_logger_returns_same_instance_for_same_name()`
- `test_create_logger_validates_configuration()`
- `test_create_logger_raises_exception_for_invalid_config()`
- `test_create_async_logger_returns_iasync_logger_instance()`
- `test_create_async_logger_caches_with_async_prefix()`
- `test_create_async_logger_separate_from_sync_cache()`
- `test_clear_cache_removes_all_cached_loggers()`
- `test_factory_is_thread_safe()`

#### 2.3 Application Layer Export (`application/__init__.py`)
```python
"""
Application layer - Use cases and orchestration.

This layer contains the business logic for logger creation and configuration.
Depends only on the Domain layer.
"""

from .configuration import LoggerConfig
from .logger_factory import LoggerFactory

__all__ = [
    "LoggerFactory",
    "LoggerConfig",
]
```

---

### Step 3: Implement Infrastructure Adapters

#### 3.1 Python Logger Adapter (`infrastructure/adapters/python_logger_adapter.py`)
**Purpose**: Wrap Python's logging module for synchronous logging

```python
class PythonLoggerAdapter(ILogger):
    """Adapter wrapping Python's logging.Logger for synchronous operations."""

    def __init__(self, config: LoggerConfig) -> None:
        """
        Initialize adapter with configuration.

        Args:
            config: Logger configuration
        """
        self._config = config
        self._logger = self._configure_logger()

    def _configure_logger(self) -> logging.Logger:
        """Configure Python logger with handlers and formatters."""
        logger = logging.getLogger(self._config.name)
        logger.setLevel(self._config.level.value)
        logger.handlers.clear()  # Clear existing handlers

        # Select handler based on target
        if self._config.target == OutputTarget.CONSOLE:
            handler = logging.StreamHandler()
        elif self._config.target == OutputTarget.FILE:
            log_path = self._config.get_full_path()
            if not log_path:
                raise ConfigurationException("filename", "File path not configured")
            handler = logging.FileHandler(log_path)
        elif self._config.target == OutputTarget.JSON:
            log_path = self._config.get_full_path()
            if not log_path:
                raise ConfigurationException("filename", "File path not configured")
            handler = logging.FileHandler(log_path)
        else:
            raise ConfigurationException("target", f"Unsupported target: {self._config.target}")

        # Select formatter based on target
        if self._config.target == OutputTarget.JSON:
            from miraveja_log.infrastructure.formatters import JSONFormatter
            formatter = JSONFormatter()
        else:
            from miraveja_log.infrastructure.formatters import TextFormatter
            formatter = TextFormatter(self._config.format, self._config.datefmt)

        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a debug message."""
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an info message."""
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a warning message."""
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an error message."""
        self._logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a critical message."""
        self._logger.critical(msg, *args, **kwargs)
```

**Tests to write** (`tests/unit/miraveja_log/infrastructure/adapters/test_python_logger_adapter.py`):
- `test_adapter_implements_ilogger_interface()`
- `test_adapter_configures_console_handler_for_console_target()`
- `test_adapter_configures_file_handler_for_file_target()`
- `test_adapter_configures_json_formatter_for_json_target()`
- `test_adapter_sets_logger_level_correctly()`
- `test_adapter_raises_exception_for_invalid_target()`
- `test_debug_calls_underlying_logger()`
- `test_info_calls_underlying_logger()`
- `test_error_passes_exc_info_to_logger()`

#### 3.2 Async Python Logger Adapter (`infrastructure/adapters/async_python_logger_adapter.py`)
**Purpose**: Provide non-blocking asynchronous logging

```python
class AsyncPythonLoggerAdapter(IAsyncLogger):
    """Adapter providing asynchronous logging using asyncio.to_thread."""

    def __init__(self, config: LoggerConfig) -> None:
        """
        Initialize async adapter with configuration.

        Args:
            config: Logger configuration
        """
        self._sync_adapter = PythonLoggerAdapter(config)

    async def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a debug message asynchronously."""
        await asyncio.to_thread(self._sync_adapter.debug, msg, *args, **kwargs)

    async def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an info message asynchronously."""
        await asyncio.to_thread(self._sync_adapter.info, msg, *args, **kwargs)

    async def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a warning message asynchronously."""
        await asyncio.to_thread(self._sync_adapter.warning, msg, *args, **kwargs)

    async def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an error message asynchronously."""
        await asyncio.to_thread(self._sync_adapter.error, msg, *args, **kwargs)

    async def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a critical message asynchronously."""
        await asyncio.to_thread(self._sync_adapter.critical, msg, *args, **kwargs)
```

**Tests to write** (`tests/unit/miraveja_log/infrastructure/adapters/test_async_python_logger_adapter.py`):
- `test_async_adapter_implements_iasync_logger_interface()`
- `test_async_adapter_wraps_sync_adapter()`
- `test_async_debug_offloads_to_thread()`
- `test_async_info_offloads_to_thread()`
- `test_async_methods_are_truly_async()`
- `test_async_adapter_does_not_block_event_loop()`

#### 3.3 Adapters Export (`infrastructure/adapters/__init__.py`)
```python
"""Adapters for external logging implementations."""

from .async_python_logger_adapter import AsyncPythonLoggerAdapter
from .python_logger_adapter import PythonLoggerAdapter

__all__ = [
    "PythonLoggerAdapter",
    "AsyncPythonLoggerAdapter",
]
```

---

### Step 4: Implement Formatters

#### 4.1 Text Formatter (`infrastructure/formatters/text_formatter.py`)
**Purpose**: Format logs as human-readable text

```python
class TextFormatter(logging.Formatter):
    """Standard text formatter for console and file output."""

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None
    ) -> None:
        """
        Initialize text formatter.

        Args:
            fmt: Log format string
            datefmt: Date format string
        """
        super().__init__(fmt=fmt, datefmt=datefmt)
```

**Tests to write** (`tests/unit/miraveja_log/infrastructure/formatters/test_text_formatter.py`):
- `test_text_formatter_inherits_from_logging_formatter()`
- `test_text_formatter_uses_custom_format()`
- `test_text_formatter_uses_custom_datefmt()`
- `test_text_formatter_formats_log_record_correctly()`

#### 4.2 JSON Formatter (`infrastructure/formatters/json_formatter.py`)
**Purpose**: Format logs as structured JSON

```python
class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging output."""

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON-formatted log string
        """
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }

        # Merge extra fields at top level (flat structure)
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_data.update(record.extra)

        # Handle exception info
        if record.exc_info:
            log_data["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(log_data)
```

**Tests to write** (`tests/unit/miraveja_log/infrastructure/formatters/test_json_formatter.py`):
- `test_json_formatter_inherits_from_logging_formatter()`
- `test_json_formatter_outputs_valid_json()`
- `test_json_formatter_includes_timestamp_level_name_message()`
- `test_json_formatter_merges_extra_dict_at_top_level()`
- `test_json_formatter_formats_timestamp_as_isoformat()`
- `test_json_formatter_includes_exception_info_when_present()`

#### 4.3 Formatters Export (`infrastructure/formatters/__init__.py`)
```python
"""Formatters for log output."""

from .json_formatter import JSONFormatter
from .text_formatter import TextFormatter

__all__ = [
    "TextFormatter",
    "JSONFormatter",
]
```

---

### Step 5: Testing Utilities, Public API & Integration Tests

#### 5.1 Testing Utilities (`infrastructure/testing/test_utilities.py`)
**Purpose**: Provide utilities for testing logging behavior

```python
class MemoryHandler(logging.Handler):
    """Handler that captures log records in memory for testing."""

    def __init__(self) -> None:
        """Initialize memory handler."""
        super().__init__()
        self.records: List[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        """Capture log record."""
        self.records.append(record)

    def clear(self) -> None:
        """Clear captured records."""
        self.records.clear()

    def get_messages(self) -> List[str]:
        """Get formatted messages."""
        return [self.format(record) for record in self.records]

class MockLogger(ILogger):
    """Mock logger for testing without actual I/O."""

    def __init__(self) -> None:
        """Initialize mock logger."""
        self.calls: List[Tuple[str, str, tuple, dict]] = []

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Record debug call."""
        self.calls.append(("debug", msg, args, kwargs))

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Record info call."""
        self.calls.append(("info", msg, args, kwargs))

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Record warning call."""
        self.calls.append(("warning", msg, args, kwargs))

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Record error call."""
        self.calls.append(("error", msg, args, kwargs))

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Record critical call."""
        self.calls.append(("critical", msg, args, kwargs))

    def clear(self) -> None:
        """Clear recorded calls."""
        self.calls.clear()

    def get_messages(self, level: Optional[str] = None) -> List[str]:
        """Get messages, optionally filtered by level."""
        if level:
            return [msg for lvl, msg, _, _ in self.calls if lvl == level]
        return [msg for _, msg, _, _ in self.calls]
```

**Tests to write** (`tests/unit/miraveja_log/infrastructure/testing/test_utilities.py`):
- `test_memory_handler_captures_log_records()`
- `test_memory_handler_clear_removes_all_records()`
- `test_memory_handler_get_messages_returns_formatted_messages()`
- `test_mock_logger_implements_ilogger()`
- `test_mock_logger_records_all_calls()`
- `test_mock_logger_get_messages_filters_by_level()`

#### 5.2 Testing Utilities Export (`infrastructure/testing/__init__.py`)
```python
"""Testing utilities for miraveja-log."""

from .test_utilities import MemoryHandler, MockLogger

__all__ = [
    "MemoryHandler",
    "MockLogger",
]
```

#### 5.3 Infrastructure Layer Export (`infrastructure/__init__.py`)
```python
"""
Infrastructure layer - External integrations.

This layer contains adapters for external systems and frameworks.
Depends on Application and Domain layers.
"""

from .adapters import AsyncPythonLoggerAdapter, PythonLoggerAdapter
from .formatters import JSONFormatter, TextFormatter

__all__ = [
    # Adapters
    "PythonLoggerAdapter",
    "AsyncPythonLoggerAdapter",
    # Formatters
    "TextFormatter",
    "JSONFormatter",
]
```

#### 5.4 Root Package Export (`__init__.py`)
**Purpose**: Expose clean public API

```python
"""
miraveja-log: Lightweight and flexible logging library with structured logging support.

Public API exports for the miraveja-log package.
"""

# Application exports
from miraveja_log.application import LoggerConfig, LoggerFactory

# Domain exports
from miraveja_log.domain import (
    ConfigurationException,
    HandlerException,
    IAsyncLogger,
    ILogger,
    LogException,
    LogLevel,
    OutputTarget,
)

__version__ = "0.1.0"

__all__ = [
    # Factory
    "LoggerFactory",
    # Configuration
    "LoggerConfig",
    # Enums
    "LogLevel",
    "OutputTarget",
    # Interfaces
    "ILogger",
    "IAsyncLogger",
    # Exceptions
    "LogException",
    "ConfigurationException",
    "HandlerException",
]
```

#### 5.5 Testing Namespace Export (`testing/__init__.py` - NEW)
**Purpose**: Provide testing utilities under separate namespace

```python
"""Testing utilities for miraveja-log."""

from miraveja_log.infrastructure.testing import MemoryHandler, MockLogger

__all__ = [
    "MemoryHandler",
    "MockLogger",
]
```

#### 5.6 Integration Tests

**Test File Structure**:
- `tests/integration/miraveja_log/test_end_to_end_sync_logging.py`
- `tests/integration/miraveja_log/test_end_to_end_async_logging.py`
- `tests/integration/miraveja_log/test_console_logging.py`
- `tests/integration/miraveja_log/test_file_logging.py`
- `tests/integration/miraveja_log/test_json_logging.py`
- `tests/integration/miraveja_log/test_configuration_from_env.py`
- `tests/integration/miraveja_log/test_structured_logging.py`
- `tests/integration/miraveja_log/test_error_scenarios.py`

**Key Integration Test Scenarios**:

1. **End-to-End Sync Logging**:
   - Create logger via factory
   - Log at all levels
   - Verify output captured correctly
   - Verify extra dict handled

2. **End-to-End Async Logging**:
   - Create async logger via factory
   - Log asynchronously at all levels
   - Verify non-blocking behavior
   - Verify output matches sync behavior

3. **Console Logging**:
   - Logger outputs to console
   - Format applied correctly
   - All log levels work

4. **File Logging**:
   - Logger creates file
   - Directory created automatically
   - Multiple loggers to same file
   - File permissions correct

5. **JSON Logging**:
   - Valid JSON output
   - Flat structure with merged extra
   - Exception info serialized
   - Timestamp in ISO format

6. **Configuration from Environment**:
   - Load all config from env vars
   - Defaults applied correctly
   - Validation errors raised
   - Directory created automatically

7. **Structured Logging**:
   - Extra dict parameter works
   - Context merged correctly
   - Complex objects handled
   - Exception info captured

8. **Error Scenarios**:
   - Invalid configuration raises exception
   - Missing required fields caught
   - File permission errors handled
   - Thread safety verified

---

## Design Decisions Summary

### 1. Async Implementation: asyncio.to_thread()
**Decision**: Use `asyncio.to_thread()` to offload blocking I/O operations.
**Rationale**: Simple, no extra dependencies, provides non-blocking behavior without reimplementing logging infrastructure.

### 2. Logger Instance Caching: Cache by Name
**Decision**: Cache loggers by name like Python's `logging.getLogger()`.
**Rationale**: Prevents duplicate handlers, maintains compatibility with Python logging patterns, thread-safe with lock.

### 3. JSON Format: Flat Structure
**Decision**: Merge extra dict at top level in JSON output.
**Rationale**: Easier to parse and query, standard practice in log aggregation systems (ELK, Splunk).

### 4. Testing Utilities: Separate Namespace
**Decision**: Export testing utilities under `miraveja_log.testing` namespace.
**Rationale**: Keeps main API clean, follows pytest pattern, clear intent for testing usage.

### 5. File Rotation: Future Phase
**Decision**: Not included in initial implementation.
**Rationale**: Maintain simplicity, can use stdlib `RotatingFileHandler` in future via factory parameter.

### 6. Sensitive Data Filtering: Optional Future Feature
**Decision**: Not included in core refactoring.
**Rationale**: Keep core simple, can add as optional `IFilter` interface if needed for compliance.

---

## Testing Strategy

### Test Coverage Target: 96%+

### Test Organization:
- **Unit Tests**: Isolated component testing with mocks
  - Mirror source structure: `tests/unit/miraveja_log/{layer}/{module}`
  - Test each class/function independently
  - Mock external dependencies (file system, logging module)

- **Integration Tests**: Cross-layer scenarios with real components
  - End-to-end flows
  - Real file I/O
  - Environment variable loading
  - Error handling

### Test Naming Convention:
- Pattern: `test_{behavior}_when_{condition}`
- Example: `test_create_logger_returns_ilogger_when_valid_config()`
- Descriptive docstrings explaining test purpose

### Test Classes:
- Group related tests by functionality
- Clear class names: `TestLoggerFactoryCreation`, `TestConfigurationValidation`
- One assertion per logical concept

### TDD Approach:
1. Write test first (red)
2. Implement minimum code to pass (green)
3. Refactor for simplicity (refactor)
4. Repeat

---

## Code Quality Standards

### Type Hints:
- All function parameters and return types
- Use `typing` for complex types
- Full mypy compliance in strict mode

### Docstrings:
- Google-style docstrings
- Include Args, Returns, Raises, Example sections
- Public APIs must be documented

### Formatting:
- Black with 120 character line length
- isort with black profile
- No trailing whitespace

### Linting:
- pylint with project-specific rules
- Disable `missing-docstring` for tests only
- Maximum complexity: 10

### Pre-commit Hooks:
- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON validation
- Black formatting
- isort import sorting
- No debug statements

---

## Implementation Checklist

### Phase 1: Domain Layer
- [X] Create `domain/enums.py` with LogLevel and OutputTarget
- [X] Write unit tests for enums
- [X] Create `domain/interfaces.py` with ILogger and IAsyncLogger
- [X] Write unit tests for interfaces
- [X] Create `domain/models.py` with LogEntry
- [X] Write unit tests for models
- [X] Create `domain/exceptions.py` with exception hierarchy
- [X] Write unit tests for exceptions
- [X] Create `domain/__init__.py` with exports
- [X] Verify all domain tests pass (100% coverage)

### Phase 2: Application Layer
- [X] Create `application/configuration.py` with LoggerConfig
- [X] Write unit tests for configuration
- [X] Create `application/logger_factory.py` with LoggerFactory
- [X] Write unit tests for factory
- [X] Create `application/__init__.py` with exports
- [X] Verify all application tests pass (100% coverage)

### Phase 3: Infrastructure Adapters
- [X] Create `infrastructure/adapters/python_logger_adapter.py`
- [X] Write unit tests for sync adapter
- [X] Create `infrastructure/adapters/async_python_logger_adapter.py`
- [X] Write unit tests for async adapter
- [X] Create `infrastructure/adapters/__init__.py` with exports
- [X] Verify all adapter tests pass (100% coverage)

### Phase 4: Infrastructure Formatters
- [X] Create `infrastructure/formatters/text_formatter.py`
- [X] Write unit tests for text formatter
- [X] Create `infrastructure/formatters/json_formatter.py`
- [X] Write unit tests for JSON formatter
- [X] Create `infrastructure/formatters/__init__.py` with exports
- [X] Verify all formatter tests pass (100% coverage)

### Phase 5: Testing Utilities & Public API
- [X] Create `infrastructure/testing/test_utilities.py`
- [X] Write unit tests for testing utilities
- [X] Create `infrastructure/testing/__init__.py` with exports
- [X] Create `infrastructure/__init__.py` with exports
- [X] Create root `__init__.py` with public API
- [X] Create `testing/__init__.py` for testing namespace
- [X] Verify all tests pass (overall 96%+ coverage)

### Phase 6: Integration Tests
- [ ] Write `test_end_to_end_sync_logging.py`
- [ ] Write `test_end_to_end_async_logging.py`
- [ ] Write `test_console_logging.py`
- [ ] Write `test_file_logging.py`
- [ ] Write `test_json_logging.py`
- [ ] Write `test_configuration_from_env.py`
- [ ] Write `test_structured_logging.py`
- [ ] Write `test_error_scenarios.py`
- [ ] Verify all integration tests pass

### Phase 7: Documentation & Quality
- [ ] Update README.md with new API examples
- [ ] Update CONTRIBUTING.md with refactored structure
- [ ] Run black formatter on all code
- [ ] Run isort on all imports
- [ ] Run pylint and fix issues
- [ ] Run mypy and achieve 100% type coverage
- [ ] Install and run pre-commit hooks
- [ ] Verify final coverage report (96%+)
- [ ] Update CHANGELOG.md

---

## Success Criteria

1. ✅ **Architecture**: Strict DDD/Hexagonal separation (Domain ← Application ← Infrastructure)
2. ✅ **Test Coverage**: 96%+ overall, 100% for domain and application layers
3. ✅ **Simplicity**: No over-engineering, clear single responsibilities
4. ✅ **Type Safety**: Full type hints, mypy strict mode passing
5. ✅ **Documentation**: All public APIs documented with examples
6. ✅ **Code Quality**: Black, isort, pylint all passing
7. ✅ **Functionality**: Sync + async, console + file + JSON, structured logging
8. ✅ **Testing**: TDD approach, comprehensive unit + integration tests
9. ✅ **Compatibility**: Python 3.10+, follows miraveja-di patterns
10. ✅ **Usability**: Clean public API, easy to use, well-tested utilities
