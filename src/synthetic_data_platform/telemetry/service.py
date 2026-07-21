from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from uuid import uuid4

from synthetic_data_platform.telemetry.models import PipelineRun


class TelemetryService:
    """Captures Run IDs, timing, and metadata for pipeline executions."""

    @contextmanager
    def start_run(self, pipeline_name: str) -> Iterator[PipelineRun]:
        run = PipelineRun(run_id=str(uuid4()), pipeline_name=pipeline_name)
        try:
            yield run
        except Exception as exc:
            run.status = "failed"
            run.add_error(str(exc))
            raise
        else:
            run.status = "success"
        finally:
            run.end_time = datetime.now(UTC)
