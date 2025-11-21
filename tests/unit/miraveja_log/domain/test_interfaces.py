"""Unit tests for domain interfaces."""

import inspect

import pytest

from miraveja_log.domain.interfaces import IAsyncLogger, ILogger


class TestILogger:
    """Test cases for ILogger interface."""

    def test_ilogger_is_abstract_base_class(self) -> None:
        """Test that ILogger is an abstract base class."""
        assert inspect.isabstract(ILogger)

    def test_ilogger_cannot_be_instantiated(self) -> None:
        """Test that ILogger cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            ILogger()  # type: ignore

    def test_ilogger_has_required_abstract_methods(self) -> None:
        """Test that ILogger has all required abstract methods."""
        abstract_methods = ILogger.__abstractmethods__
        expected_methods = {"__init__", "debug", "info", "warning", "error", "critical"}
        assert abstract_methods == expected_methods

    def test_concrete_implementation_must_implement_all_methods(self) -> None:
        """Test that concrete implementation must implement all abstract methods."""

        class IncompleteLogger(ILogger):
            """Incomplete logger missing some methods."""

            def __init__(self, config) -> None:  # type: ignore
                pass

            def debug(self, message, *args, **kwargs) -> None:  # type: ignore
                pass

            # Missing info, warning, error, critical

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteLogger(None)  # type: ignore

    def test_concrete_implementation_with_all_methods_can_be_instantiated(self) -> None:
        """Test that concrete implementation with all methods can be instantiated."""

        class CompleteLogger(ILogger):
            """Complete logger with all required methods."""

            def __init__(self, config) -> None:  # type: ignore
                self.config = config

            def debug(self, message, *args, **kwargs) -> None:  # type: ignore
                pass

            def info(self, message, *args, **kwargs) -> None:  # type: ignore
                pass

            def warning(self, message, *args, **kwargs) -> None:  # type: ignore
                pass

            def error(self, message, *args, **kwargs) -> None:  # type: ignore
                pass

            def critical(self, message, *args, **kwargs) -> None:  # type: ignore
                pass

        logger = CompleteLogger("test_config")
        assert isinstance(logger, ILogger)
        assert logger.config == "test_config"

    def test_ilogger_methods_have_correct_signatures(self) -> None:
        """Test that ILogger methods have correct signatures."""
        assert hasattr(ILogger, "debug")
        assert hasattr(ILogger, "info")
        assert hasattr(ILogger, "warning")
        assert hasattr(ILogger, "error")
        assert hasattr(ILogger, "critical")


class TestIAsyncLogger:
    """Test cases for IAsyncLogger interface."""

    def test_iasync_logger_is_abstract_base_class(self) -> None:
        """Test that IAsyncLogger is an abstract base class."""
        assert inspect.isabstract(IAsyncLogger)

    def test_iasync_logger_cannot_be_instantiated(self) -> None:
        """Test that IAsyncLogger cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IAsyncLogger()  # type: ignore

    def test_iasync_logger_has_required_abstract_methods(self) -> None:
        """Test that IAsyncLogger has all required abstract methods."""
        abstract_methods = IAsyncLogger.__abstractmethods__
        expected_methods = {"__init__", "debug", "info", "warning", "error", "critical"}
        assert abstract_methods == expected_methods

    def test_iasync_logger_has_async_methods(self) -> None:
        """Test that IAsyncLogger methods are async (coroutines)."""

        class CompleteAsyncLogger(IAsyncLogger):
            """Complete async logger for testing."""

            def __init__(self, config) -> None:  # type: ignore
                self.config = config

            async def debug(self, message, *args, **kwargs) -> None:  # type: ignore
                pass

            async def info(self, message, *args, **kwargs) -> None:  # type: ignore
                pass

            async def warning(self, message, *args, **kwargs) -> None:  # type: ignore
                pass

            async def error(self, message, *args, **kwargs) -> None:  # type: ignore
                pass

            async def critical(self, message, *args, **kwargs) -> None:  # type: ignore
                pass

        logger = CompleteAsyncLogger("test_config")
        assert inspect.iscoroutinefunction(logger.debug)
        assert inspect.iscoroutinefunction(logger.info)
        assert inspect.iscoroutinefunction(logger.warning)
        assert inspect.iscoroutinefunction(logger.error)
        assert inspect.iscoroutinefunction(logger.critical)

    def test_concrete_async_implementation_must_implement_all_methods(self) -> None:
        """Test that concrete async implementation must implement all abstract methods."""

        class IncompleteAsyncLogger(IAsyncLogger):
            """Incomplete async logger missing some methods."""

            def __init__(self, config) -> None:  # type: ignore
                pass

            async def debug(self, message, *args, **kwargs) -> None:  # type: ignore
                pass

            # Missing info, warning, error, critical

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteAsyncLogger(None)  # type: ignore

    def test_concrete_async_implementation_with_all_methods_can_be_instantiated(self) -> None:
        """Test that concrete async implementation with all methods can be instantiated."""

        class CompleteAsyncLogger(IAsyncLogger):
            """Complete async logger with all required methods."""

            def __init__(self, config) -> None:  # type: ignore
                self.config = config

            async def debug(self, message, *args, **kwargs) -> None:  # type: ignore
                pass

            async def info(self, message, *args, **kwargs) -> None:  # type: ignore
                pass

            async def warning(self, message, *args, **kwargs) -> None:  # type: ignore
                pass

            async def error(self, message, *args, **kwargs) -> None:  # type: ignore
                pass

            async def critical(self, message, *args, **kwargs) -> None:  # type: ignore
                pass

        logger = CompleteAsyncLogger("test_config")
        assert isinstance(logger, IAsyncLogger)
        assert logger.config == "test_config"

    def test_iasync_logger_methods_have_correct_signatures(self) -> None:
        """Test that IAsyncLogger methods have correct signatures."""
        assert hasattr(IAsyncLogger, "debug")
        assert hasattr(IAsyncLogger, "info")
        assert hasattr(IAsyncLogger, "warning")
        assert hasattr(IAsyncLogger, "error")
        assert hasattr(IAsyncLogger, "critical")
