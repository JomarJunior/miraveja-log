import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from miraveja_log.domain import LogLevel, OutputTarget


class LoggerConfig(BaseModel):
    """Configuration settings for the logger."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = Field(..., description="The name of the logger.")
    level: LogLevel = Field(default=LogLevel.INFO, description="The logging level.")
    output_target: OutputTarget = Field(default=OutputTarget.CONSOLE, description="The output target for the logger.")
    log_format: Optional[str] = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="The format string for log messages.",
    )
    date_format: Optional[str] = Field(
        default="%Y-%m-%d %H:%M:%S", description="The format string for timestamps in log messages."
    )
    directory: Optional[Path] = Field(
        default=None, description="The directory where log files will be stored if output_target is FILE or JSON."
    )
    filename: Optional[str] = Field(
        default=None, description="The filename for the log file if output_target is FILE or JSON."
    )

    @field_validator("directory", mode="before")
    def validate_directory(cls, v: Optional[str]) -> Optional[Path]:
        """Convert directory string to Path if provided."""
        return Path(v) if v is not None else None

    @model_validator(mode="after")
    def validate_file_target_requirements(self) -> "LoggerConfig":
        """Validate that directory and filename are provided when output_target is FILE or JSON."""
        if self.output_target in {OutputTarget.FILE, OutputTarget.JSON}:
            if self.directory is None:
                raise ValueError(f"directory must be provided when output_target is {self.output_target}.")
            if self.filename is None:
                raise ValueError(f"filename must be provided when output_target is {self.output_target}.")
        return self

    @classmethod
    def from_env(cls) -> "LoggerConfig":
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
        name = os.getenv("LOGGER_NAME", "default_logger")
        config = cls(
            name=name,
        )

        level_str = os.getenv("LOGGER_LEVEL")
        if level_str:
            config.level = LogLevel(level_str)

        target_str = os.getenv("LOGGER_TARGET")
        if target_str:
            config.output_target = OutputTarget(target_str)

        format_str = os.getenv("LOGGER_FORMAT")
        if format_str:
            config.log_format = format_str

        datefmt_str = os.getenv("LOGGER_DATEFMT")
        if datefmt_str:
            config.date_format = datefmt_str

        dir_str = os.getenv("LOGGER_DIR")
        if dir_str:
            config.directory = Path(dir_str)

        filename_str = os.getenv("LOGGER_FILENAME")
        if filename_str:
            config.filename = filename_str

        return config

    def get_full_path(self) -> Optional[Path]:
        """Get the full path to the log file if applicable."""
        if self.output_target in {OutputTarget.FILE, OutputTarget.JSON} and self.directory and self.filename:
            return self.directory / self.filename
        return None
