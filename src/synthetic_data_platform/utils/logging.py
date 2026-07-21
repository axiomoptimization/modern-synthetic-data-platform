from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from rich.logging import RichHandler

from synthetic_data_platform.constants import LOG_FILE_NAME, LOGGER_NAME


class JsonFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "run_id": getattr(record, "run_id", None),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def configure_logging(log_dir: Path, level: int = logging.INFO) -> logging.Logger:
    """Configure the application logger with a Rich console handler and a
    JSON file handler, then return it for reuse throughout the application.
    """
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    logger.handlers.clear()
    logger.propagate = False

    console_handler = RichHandler(rich_tracebacks=True, show_path=False)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(log_dir / LOG_FILE_NAME)
    file_handler.setLevel(level)
    file_handler.setFormatter(JsonFormatter())
    logger.addHandler(file_handler)

    return logger


def get_logger() -> logging.Logger:
    """Return the application logger, assuming it has already been configured."""
    return logging.getLogger(LOGGER_NAME)
