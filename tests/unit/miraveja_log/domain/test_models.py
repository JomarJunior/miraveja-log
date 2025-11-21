"""Unit tests for domain models."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from miraveja_log.domain.enums import LogLevel
from miraveja_log.domain.models import LogEntry


class TestLogEntry:
    """Test cases for LogEntry model."""

    def test_log_entry_is_frozen_when_created(self) -> None:
        """Test that LogEntry is immutable (frozen)."""
        entry = LogEntry(level=LogLevel.INFO, name="test", message="Test message")

        with pytest.raises(ValidationError, match="Instance is frozen"):
            entry.level = LogLevel.DEBUG  # type: ignore

        with pytest.raises(ValidationError, match="Instance is frozen"):
            entry.message = "New message"  # type: ignore

    def test_log_entry_requires_level_name_message(self) -> None:
        """Test that LogEntry requires level, name, and message fields."""
        # Missing level
        with pytest.raises(ValidationError):
            LogEntry(name="test", message="Test message")  # type: ignore

        # Missing name
        with pytest.raises(ValidationError):
            LogEntry(level=LogLevel.INFO, message="Test message")  # type: ignore

        # Missing message
        with pytest.raises(ValidationError):
            LogEntry(level=LogLevel.INFO, name="test")  # type: ignore

    def test_log_entry_timestamp_defaults_to_current_utc(self) -> None:
        """Test that timestamp defaults to current UTC time."""
        before = datetime.now(timezone.utc)
        entry = LogEntry(level=LogLevel.INFO, name="test", message="Test message")
        after = datetime.now(timezone.utc)

        assert before <= entry.timestamp <= after
        assert entry.timestamp.tzinfo == timezone.utc

    def test_log_entry_context_defaults_to_empty_dict(self) -> None:
        """Test that context field defaults to empty dictionary."""
        entry = LogEntry(level=LogLevel.INFO, name="test", message="Test message")
        assert entry.context == {}
        assert isinstance(entry.context, dict)

    def test_log_entry_can_be_created_with_custom_timestamp(self) -> None:
        """Test that LogEntry can be created with custom timestamp."""
        custom_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        entry = LogEntry(level=LogLevel.INFO, name="test", message="Test message", timestamp=custom_time)
        assert entry.timestamp == custom_time

    def test_log_entry_can_be_created_with_context(self) -> None:
        """Test that LogEntry can be created with custom context."""
        context = {"user_id": 123, "action": "login", "ip": "192.168.1.1"}
        entry = LogEntry(level=LogLevel.INFO, name="test", message="User logged in", context=context)
        assert entry.context == context
        assert entry.context["user_id"] == 123

    def test_log_entry_serialize_returns_flat_structure(self) -> None:
        """Test that serialize() returns a flat dictionary structure."""
        context = {"user_id": 123, "action": "login"}
        entry = LogEntry(level=LogLevel.INFO, name="test_logger", message="Test message", context=context)

        serialized = entry.serialize()

        assert isinstance(serialized, dict)
        assert "timestamp" in serialized
        assert "level" in serialized
        assert "name" in serialized
        assert "message" in serialized
        # Context should be merged at top level
        assert "user_id" in serialized
        assert "action" in serialized
        # Context dict itself should not be a key
        assert "context" not in serialized

    def test_log_entry_serialize_merges_context_at_top_level(self) -> None:
        """Test that serialize() merges context fields at top level."""
        context = {"request_id": "abc-123", "duration_ms": 150}
        entry = LogEntry(level=LogLevel.WARNING, name="api", message="Slow request", context=context)

        serialized = entry.serialize()

        assert serialized["request_id"] == "abc-123"
        assert serialized["duration_ms"] == 150
        assert serialized["level"] == "WARNING"
        assert serialized["name"] == "api"
        assert serialized["message"] == "Slow request"

    def test_log_entry_serialize_timestamp_is_isoformat(self) -> None:
        """Test that timestamp in serialized output is ISO format string."""
        custom_time = datetime(2024, 6, 15, 14, 30, 45, tzinfo=timezone.utc)
        entry = LogEntry(level=LogLevel.ERROR, name="test", message="Error occurred", timestamp=custom_time)

        serialized = entry.serialize()

        assert serialized["timestamp"] == "2024-06-15T14:30:45+00:00"
        assert isinstance(serialized["timestamp"], str)

    def test_log_entry_serialize_level_is_string(self) -> None:
        """Test that level in serialized output is a string."""
        entry = LogEntry(level=LogLevel.DEBUG, name="test", message="Debug message")

        serialized = entry.serialize()

        assert serialized["level"] == "DEBUG"
        assert isinstance(serialized["level"], str)

    def test_log_entry_serialize_with_empty_context(self) -> None:
        """Test that serialize() works correctly with empty context."""
        entry = LogEntry(level=LogLevel.INFO, name="test", message="Simple message")

        serialized = entry.serialize()

        assert "timestamp" in serialized
        assert "level" in serialized
        assert "name" in serialized
        assert "message" in serialized
        # Should have exactly 4 keys (no extra from empty context)
        assert len(serialized) == 4

    def test_log_entry_context_can_contain_nested_structures(self) -> None:
        """Test that context can contain nested dictionaries and lists."""
        context = {
            "user": {"id": 123, "name": "John"},
            "tags": ["important", "urgent"],
            "metadata": {"version": "1.0", "env": "prod"},
        }
        entry = LogEntry(level=LogLevel.CRITICAL, name="test", message="Critical issue", context=context)

        assert entry.context["user"]["id"] == 123
        assert entry.context["tags"][0] == "important"
        assert entry.context["metadata"]["env"] == "prod"

    def test_log_entry_different_log_levels(self) -> None:
        """Test LogEntry creation with different log levels."""
        levels = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]

        for level in levels:
            entry = LogEntry(level=level, name="test", message=f"{level} message")
            assert entry.level == level
            assert str(entry.level) == level.value

    def test_log_entry_serialize_uses_custom_serializer(self) -> None:
        """Test that serialize() uses custom model serializer."""
        context = {"key": "value"}
        entry = LogEntry(level=LogLevel.INFO, name="test", message="Test", context=context)

        # Both model_dump() and serialize() use the custom serializer
        dumped = entry.model_dump()
        serialized = entry.serialize()

        # Both should merge context at top level
        assert "context" not in dumped
        assert "key" in dumped
        assert dumped["key"] == "value"

        assert "context" not in serialized
        assert "key" in serialized
        assert serialized["key"] == "value"

        # They should be the same
        assert dumped == serialized

    def test_log_entry_equality(self) -> None:
        """Test LogEntry equality comparison."""
        time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        entry1 = LogEntry(level=LogLevel.INFO, name="test", message="Test", timestamp=time)
        entry2 = LogEntry(level=LogLevel.INFO, name="test", message="Test", timestamp=time)
        entry3 = LogEntry(level=LogLevel.DEBUG, name="test", message="Test", timestamp=time)

        assert entry1 == entry2
        assert entry1 != entry3

    def test_log_entry_with_none_values_in_context(self) -> None:
        """Test that context can contain None values."""
        context = {"optional_field": None, "required_field": "value"}
        entry = LogEntry(level=LogLevel.INFO, name="test", message="Test", context=context)

        assert entry.context["optional_field"] is None
        assert entry.context["required_field"] == "value"

        serialized = entry.serialize()
        assert serialized["optional_field"] is None
