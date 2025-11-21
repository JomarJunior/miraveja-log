import logging
from typing import Optional


class TextFormatter(logging.Formatter):
    """Standard text formatter for console and file output."""

    def __init__(self, log_format: Optional[str] = None, date_format: Optional[str] = None) -> None:
        """
        Initialize the text formatter.

        Args:
            log_format: The log message format.
            date_format: The date format for log messages.
        """
        super().__init__(fmt=log_format, datefmt=date_format)
