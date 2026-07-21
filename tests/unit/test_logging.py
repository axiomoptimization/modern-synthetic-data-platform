import json
import logging
from pathlib import Path

from synthetic_data_platform.constants import LOG_FILE_NAME
from synthetic_data_platform.utils.logging import configure_logging, get_logger


def test_configure_logging_creates_json_log_file(tmp_path: Path) -> None:
    logger = configure_logging(tmp_path)

    logger.info("pipeline started", extra={"run_id": "run-123"})

    log_file = tmp_path / LOG_FILE_NAME
    assert log_file.exists()

    entry = json.loads(log_file.read_text().strip().splitlines()[-1])
    assert entry["message"] == "pipeline started"
    assert entry["run_id"] == "run-123"
    assert entry["level"] == "INFO"
    assert "timestamp" in entry


def test_configure_logging_adds_console_and_file_handlers(tmp_path: Path) -> None:
    logger = configure_logging(tmp_path)

    assert len(logger.handlers) == 2
    assert any(isinstance(h, logging.FileHandler) for h in logger.handlers)


def test_get_logger_returns_configured_logger(tmp_path: Path) -> None:
    configure_logging(tmp_path)

    assert get_logger() is logging.getLogger("synthetic_data_platform")
