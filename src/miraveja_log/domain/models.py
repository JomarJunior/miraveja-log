from datetime import datetime, timezone
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field, model_serializer

from miraveja_log.domain.enums import LogLevel


class LogEntry(BaseModel):
    """Value object representing a single log entry."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="The timestamp of the log entry in UTC."
    )
    level: LogLevel = Field(..., description="The log level of the entry.")
    name: str = Field(..., description="The name of the logger that created the entry.")
    message: str = Field(..., description="The log message.")
    context: Dict[str, Any] = Field(
        default_factory=dict, description="Additional contextual information for the log entry."
    )

    @model_serializer
    def serialize(self) -> Dict[str, Any]:
        """Custom serializer to convert LogEntry to a dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": str(self.level),
            "name": self.name,
            "message": self.message,
            **self.context,  # Merge context into the main dictionary
        }
