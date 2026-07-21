from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from synthetic_data_platform.constants import (
    BRONZE_DIR_NAME,
    DEFAULT_LOG_DIR,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_RANDOM_SEED,
    GOLD_DIR_NAME,
    SILVER_DIR_NAME,
)


class Settings(BaseModel):
    """Centralized, single-source-of-truth runtime configuration."""

    output_dir: Path = Field(default=DEFAULT_OUTPUT_DIR)
    log_dir: Path = Field(default=DEFAULT_LOG_DIR)
    random_seed: int = Field(default=DEFAULT_RANDOM_SEED)

    @property
    def bronze_dir(self) -> Path:
        return self.output_dir / BRONZE_DIR_NAME

    @property
    def silver_dir(self) -> Path:
        return self.output_dir / SILVER_DIR_NAME

    @property
    def gold_dir(self) -> Path:
        return self.output_dir / GOLD_DIR_NAME

    @classmethod
    def load(cls) -> Settings:
        """Load settings from defaults.

        Environment variable and configuration file overrides may be added
        in a future release.
        """
        return cls()
