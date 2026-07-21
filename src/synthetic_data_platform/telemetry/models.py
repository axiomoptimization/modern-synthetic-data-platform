from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field

RunStatus = Literal["running", "success", "failed"]


class PipelineRun(BaseModel):
    """Metadata captured for a single pipeline execution."""

    run_id: str
    pipeline_name: str
    status: RunStatus = "running"
    start_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    end_time: datetime | None = None
    row_counts: dict[str, int] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    output_locations: list[str] = Field(default_factory=list)

    @property
    def duration_seconds(self) -> float | None:
        if self.end_time is None:
            return None
        return (self.end_time - self.start_time).total_seconds()

    def record_row_count(self, entity: str, count: int) -> None:
        self.row_counts[entity] = count

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def add_output_location(self, location: str) -> None:
        self.output_locations.append(str(location))
