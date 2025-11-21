"""Unit tests for AsyncPythonLoggerAdapter."""

import pytest

from miraveja_log.application.configuration import LoggerConfig
from miraveja_log.domain import IAsyncLogger, LogLevel
from miraveja_log.infrastructure.adapters.async_python_logger_adapter import AsyncPythonLoggerAdapter
from miraveja_log.infrastructure.adapters.python_logger_adapter import PythonLoggerAdapter


class TestAsyncPythonLoggerAdapterBasics:
    """Test basic AsyncPythonLoggerAdapter functionality."""

    def test_async_python_logger_adapter_can_be_instantiated(self) -> None:
        """Test that AsyncPythonLoggerAdapter can be created."""
        config = LoggerConfig(name="test_async_logger")
        adapter = AsyncPythonLoggerAdapter(config)

        assert adapter is not None

    def test_async_python_logger_adapter_implements_iasync_logger(self) -> None:
        """Test that AsyncPythonLoggerAdapter implements IAsyncLogger interface."""
        config = LoggerConfig(name="test_async_logger")
        adapter = AsyncPythonLoggerAdapter(config)

        assert isinstance(adapter, IAsyncLogger)

    def test_async_python_logger_adapter_creates_sync_adapter(self) -> None:
        """Test that AsyncPythonLoggerAdapter creates underlying sync adapter."""
        config = LoggerConfig(name="test_async_logger")
        adapter = AsyncPythonLoggerAdapter(config)

        assert adapter._sync_adapter is not None
        assert isinstance(adapter._sync_adapter, PythonLoggerAdapter)


class TestAsyncPythonLoggerAdapterLoggingMethods:
    """Test AsyncPythonLoggerAdapter logging methods."""

    @pytest.mark.asyncio
    async def test_debug_method_is_async(self) -> None:
        """Test that debug method is async."""
        config = LoggerConfig(name="test_async_logger", level=LogLevel.DEBUG)
        adapter = AsyncPythonLoggerAdapter(config)

        # Should be able to await the method
        await adapter.debug("Debug message")

    @pytest.mark.asyncio
    async def test_info_method_is_async(self) -> None:
        """Test that info method is async."""
        config = LoggerConfig(name="test_async_logger")
        adapter = AsyncPythonLoggerAdapter(config)

        # Should be able to await the method
        await adapter.info("Info message")

    @pytest.mark.asyncio
    async def test_warning_method_is_async(self) -> None:
        """Test that warning method is async."""
        config = LoggerConfig(name="test_async_logger")
        adapter = AsyncPythonLoggerAdapter(config)

        # Should be able to await the method
        await adapter.warning("Warning message")

    @pytest.mark.asyncio
    async def test_error_method_is_async(self) -> None:
        """Test that error method is async."""
        config = LoggerConfig(name="test_async_logger")
        adapter = AsyncPythonLoggerAdapter(config)

        # Should be able to await the method
        await adapter.error("Error message")

    @pytest.mark.asyncio
    async def test_critical_method_is_async(self) -> None:
        """Test that critical method is async."""
        config = LoggerConfig(name="test_async_logger")
        adapter = AsyncPythonLoggerAdapter(config)

        # Should be able to await the method
        await adapter.critical("Critical message")


class TestAsyncPythonLoggerAdapterLoggingWithArgs:
    """Test AsyncPythonLoggerAdapter logging methods with args and kwargs."""

    @pytest.mark.asyncio
    async def test_debug_method_accepts_args(self) -> None:
        """Test that debug method accepts positional args."""
        config = LoggerConfig(name="test_async_logger", level=LogLevel.DEBUG)
        adapter = AsyncPythonLoggerAdapter(config)

        # Should accept args without error
        await adapter.debug("Message: %s", "value")

    @pytest.mark.asyncio
    async def test_info_method_accepts_kwargs(self) -> None:
        """Test that info method accepts keyword arguments."""
        config = LoggerConfig(name="test_async_logger")
        adapter = AsyncPythonLoggerAdapter(config)

        # Should accept kwargs without error
        await adapter.info("Info message", extra={"user_id": "123"})

    @pytest.mark.asyncio
    async def test_error_method_accepts_exc_info(self) -> None:
        """Test that error method accepts exc_info."""
        config = LoggerConfig(name="test_async_logger")
        adapter = AsyncPythonLoggerAdapter(config)

        # Should accept exc_info without error
        await adapter.error("Error occurred", exc_info=True)


class TestAsyncPythonLoggerAdapterConfiguration:
    """Test AsyncPythonLoggerAdapter with different configurations."""

    @pytest.mark.asyncio
    async def test_adapter_with_different_log_levels(self) -> None:
        """Test adapter with all different log levels."""
        for level in LogLevel:
            config = LoggerConfig(name=f"test_async_logger_{level.value}", level=level)
            adapter = AsyncPythonLoggerAdapter(config)

            assert adapter._sync_adapter._config.level == level

            # Test that logging works
            await adapter.info(f"Test message for {level.value}")

    @pytest.mark.asyncio
    async def test_adapter_with_custom_log_format(self) -> None:
        """Test adapter with custom log format."""
        config = LoggerConfig(name="test_async_logger", log_format="%(levelname)s: %(message)s")
        adapter = AsyncPythonLoggerAdapter(config)

        assert adapter._sync_adapter._config.log_format == "%(levelname)s: %(message)s"
        await adapter.info("Test message")

    @pytest.mark.asyncio
    async def test_adapter_with_custom_date_format(self) -> None:
        """Test adapter with custom date format."""
        config = LoggerConfig(name="test_async_logger", date_format="%Y-%m-%d")
        adapter = AsyncPythonLoggerAdapter(config)

        assert adapter._sync_adapter._config.date_format == "%Y-%m-%d"
        await adapter.info("Test message")


class TestAsyncPythonLoggerAdapterDelegation:
    """Test that AsyncPythonLoggerAdapter properly delegates to sync adapter."""

    @pytest.mark.asyncio
    async def test_debug_delegates_to_sync_adapter(self) -> None:
        """Test that debug method delegates to sync adapter."""
        config = LoggerConfig(name="test_async_logger", level=LogLevel.DEBUG)
        adapter = AsyncPythonLoggerAdapter(config)

        # Mock the sync adapter's debug method to track calls
        call_count = [0]
        original_debug = adapter._sync_adapter.debug

        def mock_debug(*args, **kwargs):
            call_count[0] += 1
            original_debug(*args, **kwargs)

        adapter._sync_adapter.debug = mock_debug

        await adapter.debug("Test message")
        assert call_count[0] == 1

    @pytest.mark.asyncio
    async def test_info_delegates_to_sync_adapter(self) -> None:
        """Test that info method delegates to sync adapter."""
        config = LoggerConfig(name="test_async_logger")
        adapter = AsyncPythonLoggerAdapter(config)

        # Mock the sync adapter's info method to track calls
        call_count = [0]
        original_info = adapter._sync_adapter.info

        def mock_info(*args, **kwargs):
            call_count[0] += 1
            original_info(*args, **kwargs)

        adapter._sync_adapter.info = mock_info

        await adapter.info("Test message")
        assert call_count[0] == 1

    @pytest.mark.asyncio
    async def test_warning_delegates_to_sync_adapter(self) -> None:
        """Test that warning method delegates to sync adapter."""
        config = LoggerConfig(name="test_async_logger")
        adapter = AsyncPythonLoggerAdapter(config)

        # Mock the sync adapter's warning method to track calls
        call_count = [0]
        original_warning = adapter._sync_adapter.warning

        def mock_warning(*args, **kwargs):
            call_count[0] += 1
            original_warning(*args, **kwargs)

        adapter._sync_adapter.warning = mock_warning

        await adapter.warning("Test message")
        assert call_count[0] == 1

    @pytest.mark.asyncio
    async def test_error_delegates_to_sync_adapter(self) -> None:
        """Test that error method delegates to sync adapter."""
        config = LoggerConfig(name="test_async_logger")
        adapter = AsyncPythonLoggerAdapter(config)

        # Mock the sync adapter's error method to track calls
        call_count = [0]
        original_error = adapter._sync_adapter.error

        def mock_error(*args, **kwargs):
            call_count[0] += 1
            original_error(*args, **kwargs)

        adapter._sync_adapter.error = mock_error

        await adapter.error("Test message")
        assert call_count[0] == 1

    @pytest.mark.asyncio
    async def test_critical_delegates_to_sync_adapter(self) -> None:
        """Test that critical method delegates to sync adapter."""
        config = LoggerConfig(name="test_async_logger")
        adapter = AsyncPythonLoggerAdapter(config)

        # Mock the sync adapter's critical method to track calls
        call_count = [0]
        original_critical = adapter._sync_adapter.critical

        def mock_critical(*args, **kwargs):
            call_count[0] += 1
            original_critical(*args, **kwargs)

        adapter._sync_adapter.critical = mock_critical

        await adapter.critical("Test message")
        assert call_count[0] == 1
