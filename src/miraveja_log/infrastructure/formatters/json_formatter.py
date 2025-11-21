import json
import logging
from datetime import datetime
from typing import Dict


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured log output."""

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON-formatted log string
        """

        log_data: Dict[str, str] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }

        # Merge extra fields at top level (flat structure)
        if hasattr(record, "extra") and isinstance(record.extra, dict):  # type: ignore
            log_data.update(record.extra)  # type: ignore

        # Handle exception information
        if record.exc_info:
            log_data["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(log_data)
