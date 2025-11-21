import logging
from typing import Any, Callable, Dict, Optional

from miraveja_log.application import LoggerConfig
from miraveja_log.domain import ConfigurationException, ILogger, OutputTarget
from miraveja_log.infrastructure.formatters.json_formatter import JSONFormatter
from miraveja_log.infrastructure.formatters.text_formatter import TextFormatter


class PythonLoggerAdapter(ILogger):
    """Adapter wrapping Python's logging.Logger for synchronous operations."""

    @staticmethod
    def _create_file_handler(config: LoggerConfig, default_name: str) -> logging.FileHandler:
        """Create a FileHandler and ensure directory exists."""
        file_path = config.get_full_path()
        if file_path:
            # Create directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            return logging.FileHandler(str(file_path))
        return logging.FileHandler(default_name)

    HANDLER_TARGET_MAPPER: Dict[OutputTarget, Callable[[LoggerConfig], logging.Handler]] = {
        OutputTarget.CONSOLE: lambda config: logging.StreamHandler(),
        OutputTarget.FILE: lambda config: PythonLoggerAdapter._create_file_handler(config, "app.log"),
        OutputTarget.JSON: lambda config: PythonLoggerAdapter._create_file_handler(config, "app.json"),
    }

    FORMATTER_TARGET_MAPPER: Dict[OutputTarget, Callable[[LoggerConfig], logging.Formatter]] = {
        OutputTarget.CONSOLE: lambda config: TextFormatter(config.log_format, config.date_format),
        OutputTarget.FILE: lambda config: TextFormatter(config.log_format, config.date_format),
        OutputTarget.JSON: lambda config: JSONFormatter(config.log_format, config.date_format),
    }

    def __init__(self, config: LoggerConfig) -> None:
        """
        Initialize adapter with configuration.

        Args:
            config: Logger configuration settings.
        """

        self._config: LoggerConfig = config
        self._logger: logging.Logger = self._configure_logger()

    def _select_handler_based_on_target(self) -> logging.Handler:
        """Select the appropriate logging handler based on the output target."""
        handler_factory: Optional[Callable[[LoggerConfig], logging.Handler]] = self.HANDLER_TARGET_MAPPER.get(
            self._config.output_target
        )
        if not handler_factory:
            raise ConfigurationException(
                field="output_target",
                reason=f"Unsupported output target: {self._config.output_target}",
            )
        return handler_factory(self._config)

    def _select_formatter_based_on_target(self) -> logging.Formatter:
        """Select the appropriate logging formatter based on the output target."""
        formatter_factory: Optional[Callable[[LoggerConfig], logging.Formatter]] = self.FORMATTER_TARGET_MAPPER.get(
            self._config.output_target
        )
        if not formatter_factory:
            raise ConfigurationException(
                field="output_target",
                reason=f"Unsupported output target: {self._config.output_target}",
            )
        return formatter_factory(self._config)

    def _configure_logger(self) -> logging.Logger:
        """Configure the underlying Python logger based on the provided configuration."""
        logger: logging.Logger = logging.getLogger(self._config.name)
        logger.setLevel(self._config.level.value)
        logger.handlers.clear()  # Clear existing handlers
        logger.propagate = False  # Prevent propagation to root logger

        handler: logging.Handler = self._select_handler_based_on_target()
        formatter: logging.Formatter = self._select_formatter_based_on_target()

        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log a debug message."""
        self._logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log an info message."""
        self._logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log a warning message."""
        self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log an error message."""
        self._logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log a critical message."""
        self._logger.critical(message, *args, **kwargs)
