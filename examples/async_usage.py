"""Async logging examples for miraveja-log."""

import asyncio
from pathlib import Path

from miraveja_log import LoggerConfig, LoggerFactory, OutputTarget
from miraveja_log.infrastructure.adapters import AsyncPythonLoggerAdapter, PythonLoggerAdapter


async def example_basic_async_logging():
    """Example: Basic async logging."""
    print("\n=== Basic Async Logging ===")
    factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
    config = LoggerConfig(name="async_app")
    logger = factory.get_or_create_async_logger(config)

    await logger.info("Async operation started")
    await logger.debug("Processing data asynchronously")
    await logger.warning("Async warning")
    await logger.info("Async operation completed")


async def example_async_exception_handling():
    """Example: Exception handling in async logging."""
    print("\n=== Async Exception Handling ===")
    factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
    logger = factory.get_or_create_async_logger(LoggerConfig(name="async_errors"))

    try:
        await logger.info("Starting async task")
        # Simulate error
        result = 1 / 0
        return result
    except ZeroDivisionError:
        # Exception context is preserved even in async logging
        await logger.error("Async task failed", exc_info=True)
    finally:
        await logger.info("Cleanup completed")


async def example_concurrent_async_logging():
    """Example: Concurrent async logging."""
    print("\n=== Concurrent Async Logging ===")
    factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
    logger = factory.get_or_create_async_logger(LoggerConfig(name="concurrent_app"))

    async def task(task_id: int):
        await logger.info(f"Task {task_id} started", extra={"task_id": task_id})
        await asyncio.sleep(0.1)
        await logger.info(f"Task {task_id} completed", extra={"task_id": task_id})

    # Run multiple tasks concurrently
    await asyncio.gather(task(1), task(2), task(3), task(4), task(5))


async def example_async_json_logging():
    """Example: Async JSON logging with structured data."""
    print("\n=== Async JSON Logging ===")
    factory = LoggerFactory(PythonLoggerAdapter, AsyncPythonLoggerAdapter)
    config = LoggerConfig(
        name="async_json",
        output_target=OutputTarget.JSON,
        directory=Path("./logs"),
        filename="async_example.json",
    )
    logger = factory.get_or_create_async_logger(config)

    await logger.info(
        "API request processed",
        extra={
            "method": "POST",
            "endpoint": "/api/users",
            "status_code": 201,
            "response_time_ms": 45,
        },
    )
    print("Check ./logs/async_example.json for output")


async def main():
    """Run all async examples."""
    print("miraveja-log Async Examples\n")

    await example_basic_async_logging()
    await example_async_exception_handling()
    await example_concurrent_async_logging()
    await example_async_json_logging()

    print("\n✅ All async examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
